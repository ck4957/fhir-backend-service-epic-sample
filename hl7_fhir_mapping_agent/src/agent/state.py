"""State definitions for the HL7/FHIR transformation agent."""

from typing import Annotated, Any
from typing_extensions import TypedDict

from langgraph.graph import MessagesState


class ParsedHL7(TypedDict, total=False):
    """Structure for parsed HL7v2 message."""

    message_type: str
    version: str
    segments: dict[str, list[dict[str, Any]]]
    z_segments: dict[str, dict[str, Any]]
    raw_message: str


class ParsedCCDA(TypedDict, total=False):
    """Structure for parsed C-CDA document."""

    document_type: str
    patient: dict[str, Any]
    sections: dict[str, dict[str, Any]]


class ValidationResult(TypedDict, total=False):
    """FHIR validation result structure."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    info: list[str]


class HL7TransformationState(MessagesState):
    """
    Typed state for the HL7/CCDA to FHIR transformation agent.

    This state extends MessagesState to maintain conversation history
    while tracking the transformation pipeline state.
    """

    # Input parsing
    input_type: str  # "hl7v2" or "ccda"
    raw_input: str  # Original input message/document
    parsed_input: ParsedHL7 | ParsedCCDA | None

    # Segment/Section identification
    segments_identified: list[str]  # List of detected segments (PID, MSH, etc.)
    target_resources: list[str]  # FHIR resources to generate

    # RAG context
    mapping_context: list[str]  # Retrieved mapping rules from RAG

    # Template handling
    template_name: str | None  # Selected/generated template name
    liquid_template: str | None  # Template content

    # Output
    fhir_bundle: dict[str, Any] | None  # Generated FHIR Bundle

    # Validation
    validation_results: ValidationResult | None
    is_valid: bool

    # Error handling / self-correction
    error_count: int  # Number of correction attempts
    max_retries: int  # Maximum retries before giving up (default: 3)


def create_initial_state(
    raw_input: str,
    input_type: str = "hl7v2",
) -> HL7TransformationState:
    """
    Create the initial state for a transformation run.

    Args:
        raw_input: The raw HL7v2 message or C-CDA document
        input_type: Type of input ("hl7v2" or "ccda")

    Returns:
        Initialized HL7TransformationState
    """
    return HL7TransformationState(
        messages=[],
        input_type=input_type,
        raw_input=raw_input,
        parsed_input=None,
        segments_identified=[],
        target_resources=[],
        mapping_context=[],
        template_name=None,
        liquid_template=None,
        fhir_bundle=None,
        validation_results=None,
        is_valid=False,
        error_count=0,
        max_retries=3,
    )
