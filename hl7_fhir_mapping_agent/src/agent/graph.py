"""LangGraph workflow for HL7/CCDA to FHIR transformation."""

from langgraph.graph import StateGraph, START, END

from src.agent.state import HL7TransformationState
from src.agent.nodes import (
    parse_input_node,
    retrieve_mappings_node,
    transform_to_fhir_node,
    validate_fhir_node,
    self_correct_node,
    should_retry,
)


def create_transformation_graph() -> StateGraph:
    """
    Create the transformation agent workflow graph.

    The graph follows this flow:
    1. Parse input (HL7v2 or C-CDA)
    2. Retrieve mapping rules from RAG
    3. Transform to FHIR Bundle
    4. Validate output
    5. Self-correct if needed (loop back to step 4)

    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the graph with our state type
    graph = StateGraph(HL7TransformationState)

    # Add nodes
    graph.add_node("parse_input", parse_input_node)
    graph.add_node("retrieve_mappings", retrieve_mappings_node)
    graph.add_node("transform_to_fhir", transform_to_fhir_node)
    graph.add_node("validate_fhir", validate_fhir_node)
    graph.add_node("self_correct", self_correct_node)

    # Define edges (linear flow with conditional retry loop)
    graph.add_edge(START, "parse_input")
    graph.add_edge("parse_input", "retrieve_mappings")
    graph.add_edge("retrieve_mappings", "transform_to_fhir")
    graph.add_edge("transform_to_fhir", "validate_fhir")

    # Conditional edge after validation
    graph.add_conditional_edges(
        "validate_fhir",
        should_retry,
        {
            "retry": "self_correct",
            "end": END,
        },
    )

    # After self-correction, validate again
    graph.add_edge("self_correct", "validate_fhir")

    return graph


def create_transformation_agent():
    """
    Create and compile the transformation agent.

    Returns:
        Compiled runnable agent
    """
    graph = create_transformation_graph()
    return graph.compile()


# Convenience function for direct invocation
async def transform_message(
    raw_input: str,
    input_type: str = "hl7v2",
) -> dict:
    """
    Transform an HL7v2 message or C-CDA document to FHIR.

    Args:
        raw_input: The raw message or document
        input_type: "hl7v2" or "ccda"

    Returns:
        Dictionary containing:
        - fhir_bundle: The generated FHIR Bundle (or None if failed)
        - is_valid: Whether the bundle passed validation
        - validation_results: Detailed validation results
        - messages: Conversation history showing agent's reasoning
    """
    from src.agent.state import create_initial_state

    agent = create_transformation_agent()
    initial_state = create_initial_state(raw_input, input_type)

    final_state = await agent.ainvoke(initial_state)

    return {
        "fhir_bundle": final_state.get("fhir_bundle"),
        "is_valid": final_state.get("is_valid", False),
        "validation_results": final_state.get("validation_results"),
        "messages": [
            {"role": "assistant", "content": m.content}
            for m in final_state.get("messages", [])
        ],
        "segments_identified": final_state.get("segments_identified", []),
        "target_resources": final_state.get("target_resources", []),
    }
