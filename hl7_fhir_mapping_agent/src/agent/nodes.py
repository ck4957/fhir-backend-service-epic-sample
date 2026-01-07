"""Node implementations for the transformation agent graph."""

import json
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from src.agent.state import HL7TransformationState
from src.agent.prompts import (
    PARSING_PROMPT,
    MAPPING_PROMPT,
    TRANSFORMATION_PROMPT,
    VALIDATION_CORRECTION_PROMPT,
)


async def parse_input_node(state: HL7TransformationState) -> dict[str, Any]:
    """
    Parse the raw input (HL7v2 or C-CDA) into structured format.

    This node uses the appropriate parsing tool based on input_type.
    """
    from src.tools.parsing import parse_hl7, parse_ccda

    input_type = state["input_type"]
    raw_input = state["raw_input"]

    if input_type == "hl7v2":
        parsed = parse_hl7.invoke({"message": raw_input})
    elif input_type == "ccda":
        parsed = parse_ccda.invoke({"xml_content": raw_input})
    else:
        return {
            "parsed_input": None,
            "messages": state["messages"]
            + [AIMessage(content=f"Unknown input type: {input_type}")],
        }

    # Extract segments/sections
    if input_type == "hl7v2":
        segments = list(parsed.get("segments", {}).keys())
        # Add Z-segments
        segments.extend(parsed.get("z_segments", {}).keys())
    else:
        segments = list(parsed.get("sections", {}).keys())

    return {
        "parsed_input": parsed,
        "segments_identified": segments,
        "messages": state["messages"]
        + [
            AIMessage(
                content=f"Parsed {input_type} input. Found segments: {', '.join(segments)}"
            )
        ],
    }


async def retrieve_mappings_node(state: HL7TransformationState) -> dict[str, Any]:
    """
    Retrieve mapping rules from RAG for identified segments.

    Queries the vector store for each segment to get mapping guidance.
    """
    from src.rag.retriever import search_mapping_rules

    segments = state["segments_identified"]
    mapping_context = []

    for segment in segments:
        # Query RAG for mapping rules
        query = f"How to map {segment} to FHIR"
        results = await search_mapping_rules(query)
        mapping_context.extend(results)

    # Determine target FHIR resources based on segments
    segment_to_resource = {
        "MSH": ["MessageHeader"],
        "PID": ["Patient"],
        "PD1": ["Patient"],
        "NK1": ["RelatedPerson"],
        "PV1": ["Encounter"],
        "PV2": ["Encounter"],
        "DG1": ["Condition"],
        "OBX": ["Observation"],
        "OBR": ["DiagnosticReport", "ServiceRequest"],
        "AL1": ["AllergyIntolerance"],
        "IN1": ["Coverage"],
        "GT1": ["RelatedPerson"],
        "NTE": ["Annotation"],
        # C-CDA sections
        "Allergies": ["AllergyIntolerance"],
        "Medications": ["MedicationStatement", "MedicationRequest"],
        "Problems": ["Condition"],
        "Procedures": ["Procedure"],
        "Results": ["Observation", "DiagnosticReport"],
        "Encounters": ["Encounter"],
        "Immunizations": ["Immunization"],
        "Vital Signs": ["Observation"],
    }

    target_resources = set()
    for segment in segments:
        if segment in segment_to_resource:
            target_resources.update(segment_to_resource[segment])
        elif segment.startswith("Z"):
            # Z-segments need inference - add placeholder
            target_resources.add(f"[Infer:{segment}]")

    return {
        "mapping_context": mapping_context,
        "target_resources": list(target_resources),
        "messages": state["messages"]
        + [
            AIMessage(
                content=f"Retrieved mapping rules. Target FHIR resources: {', '.join(target_resources)}"
            )
        ],
    }


async def transform_to_fhir_node(state: HL7TransformationState) -> dict[str, Any]:
    """
    Transform the parsed input to FHIR Bundle.

    Uses mapping context and LLM to generate the FHIR output.
    """
    from langchain_openai import ChatOpenAI
    from src.tools.fhir_lookup import get_fhir_structure

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    parsed_input = state["parsed_input"]
    mapping_context = state["mapping_context"]
    target_resources = state["target_resources"]

    # Get FHIR structure for target resources
    resource_structures = {}
    for resource in target_resources:
        if not resource.startswith("[Infer:"):
            structure = get_fhir_structure.invoke({"resource_type": resource})
            resource_structures[resource] = structure

    # Build transformation prompt
    prompt = TRANSFORMATION_PROMPT.format(
        parsed_input=json.dumps(parsed_input, indent=2),
        mapping_context="\n".join(mapping_context[:10]),  # Limit context
    )

    # Add resource structure context
    prompt += f"\n\nFHIR Resource Structures:\n{json.dumps(resource_structures, indent=2)}"

    response = await llm.ainvoke(
        [
            {"role": "system", "content": "You are a FHIR transformation expert. Output only valid JSON."},
            {"role": "user", "content": prompt},
        ]
    )

    # Parse the response as JSON
    try:
        # Extract JSON from response (may be wrapped in markdown code blocks)
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        fhir_bundle = json.loads(content.strip())
    except json.JSONDecodeError as e:
        return {
            "fhir_bundle": None,
            "messages": state["messages"]
            + [AIMessage(content=f"Failed to parse FHIR output: {e}")],
        }

    return {
        "fhir_bundle": fhir_bundle,
        "messages": state["messages"]
        + [AIMessage(content="Generated FHIR Bundle. Proceeding to validation.")],
    }


async def validate_fhir_node(state: HL7TransformationState) -> dict[str, Any]:
    """
    Validate the generated FHIR Bundle.

    Uses the FHIR validator to check for errors.
    """
    from src.tools.validation import validate_fhir

    fhir_bundle = state["fhir_bundle"]

    if fhir_bundle is None:
        return {
            "validation_results": {"valid": False, "errors": ["No FHIR bundle to validate"]},
            "is_valid": False,
        }

    results = validate_fhir.invoke({"bundle": fhir_bundle})

    is_valid = results.get("valid", False)
    errors = results.get("errors", [])

    message = "FHIR validation passed!" if is_valid else f"Validation failed: {len(errors)} errors"

    return {
        "validation_results": results,
        "is_valid": is_valid,
        "messages": state["messages"] + [AIMessage(content=message)],
    }


async def self_correct_node(state: HL7TransformationState) -> dict[str, Any]:
    """
    Attempt to fix validation errors.

    Analyzes errors and regenerates the FHIR Bundle.
    """
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    error_count = state.get("error_count", 0) + 1
    max_retries = state.get("max_retries", 3)

    if error_count > max_retries:
        return {
            "error_count": error_count,
            "messages": state["messages"]
            + [AIMessage(content=f"Max retries ({max_retries}) exceeded. Returning best effort result.")],
        }

    errors = state["validation_results"].get("errors", [])
    fhir_bundle = state["fhir_bundle"]

    prompt = VALIDATION_CORRECTION_PROMPT.format(
        errors=json.dumps(errors, indent=2),
        fhir_bundle=json.dumps(fhir_bundle, indent=2),
    )

    response = await llm.ainvoke(
        [
            {"role": "system", "content": "Fix the FHIR Bundle errors. Output only valid JSON."},
            {"role": "user", "content": prompt},
        ]
    )

    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        fixed_bundle = json.loads(content.strip())
    except json.JSONDecodeError:
        fixed_bundle = fhir_bundle  # Keep original if parsing fails

    return {
        "fhir_bundle": fixed_bundle,
        "error_count": error_count,
        "messages": state["messages"]
        + [AIMessage(content=f"Self-correction attempt {error_count}. Re-validating...")],
    }


def should_retry(state: HL7TransformationState) -> str:
    """
    Determine if we should retry after validation failure.

    Returns:
        "retry" if we should attempt correction
        "end" if we should stop (either valid or max retries exceeded)
    """
    if state.get("is_valid", False):
        return "end"

    error_count = state.get("error_count", 0)
    max_retries = state.get("max_retries", 3)

    if error_count >= max_retries:
        return "end"

    return "retry"
