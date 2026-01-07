"""Pydantic models for API requests and responses."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class TransformRequest(BaseModel):
    """Request model for HL7/CCDA to FHIR transformation."""

    content: str = Field(
        description="Raw HL7v2 message or C-CDA XML document"
    )
    input_type: Literal["hl7v2", "ccda"] = Field(
        default="hl7v2",
        description="Type of input: 'hl7v2' or 'ccda'"
    )
    validate: bool = Field(
        default=True,
        description="Whether to validate the output FHIR bundle"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "MSH|^~\\&|HOSP|FAC|OTHER|FAC|20240101120000||ADT^A01|123456|P|2.5.1\rPID|1||12345^^^HOSP^MR||DOE^JOHN^A||19800515|M|||123 MAIN ST^^ANYTOWN^CA^12345||555-123-4567",
                    "input_type": "hl7v2",
                    "validate": True,
                }
            ]
        }
    }


class AgentMessage(BaseModel):
    """A message from the agent's reasoning process."""

    role: str = Field(description="Message role (assistant)")
    content: str = Field(description="Message content")


class TransformResponse(BaseModel):
    """Response model for transformation results."""

    success: bool = Field(description="Whether transformation succeeded")
    fhir_bundle: dict[str, Any] | None = Field(
        default=None,
        description="Generated FHIR Bundle (null if failed)"
    )
    is_valid: bool = Field(
        default=False,
        description="Whether the bundle passed FHIR validation"
    )
    validation_results: dict[str, Any] | None = Field(
        default=None,
        description="Detailed validation results"
    )
    segments_identified: list[str] = Field(
        default_factory=list,
        description="HL7 segments or C-CDA sections found in input"
    )
    target_resources: list[str] = Field(
        default_factory=list,
        description="FHIR resource types generated"
    )
    agent_messages: list[AgentMessage] = Field(
        default_factory=list,
        description="Agent's reasoning/thought process"
    )
    error: str | None = Field(
        default=None,
        description="Error message if transformation failed"
    )


class ParseRequest(BaseModel):
    """Request model for parsing HL7/CCDA without transformation."""

    content: str = Field(
        description="Raw HL7v2 message or C-CDA XML document"
    )
    input_type: Literal["hl7v2", "ccda"] = Field(
        default="hl7v2",
        description="Type of input: 'hl7v2' or 'ccda'"
    )


class ParseResponse(BaseModel):
    """Response model for parsing results."""

    success: bool = Field(description="Whether parsing succeeded")
    parsed: dict[str, Any] | None = Field(
        default=None,
        description="Parsed structure"
    )
    message_type: str | None = Field(
        default=None,
        description="Message/document type"
    )
    segments: list[str] = Field(
        default_factory=list,
        description="Segments/sections found"
    )
    error: str | None = Field(
        default=None,
        description="Error message if parsing failed"
    )


class ValidationRequest(BaseModel):
    """Request model for FHIR validation."""

    bundle: dict[str, Any] = Field(
        description="FHIR Bundle to validate"
    )
    profile: str | None = Field(
        default=None,
        description="Optional profile URL to validate against"
    )


class ValidationResponse(BaseModel):
    """Response model for validation results."""

    valid: bool = Field(description="Whether the bundle is valid")
    errors: list[str] = Field(
        default_factory=list,
        description="Validation errors"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Validation warnings"
    )
    info: list[str] = Field(
        default_factory=list,
        description="Informational messages"
    )


class MappingSearchRequest(BaseModel):
    """Request model for searching mapping rules."""

    query: str = Field(
        description="Search query (e.g., 'PID to Patient mapping')"
    )
    segment: str | None = Field(
        default=None,
        description="Optional segment filter"
    )
    k: int = Field(
        default=3,
        description="Number of results to return",
        ge=1,
        le=10,
    )


class MappingSearchResponse(BaseModel):
    """Response model for mapping search results."""

    results: list[str] = Field(
        description="Relevant mapping rule snippets"
    )
    count: int = Field(description="Number of results returned")


class FHIRStructureRequest(BaseModel):
    """Request model for FHIR structure lookup."""

    resource_type: str = Field(
        description="FHIR resource type (e.g., 'Patient', 'Observation')"
    )


class FHIRStructureResponse(BaseModel):
    """Response model for FHIR structure lookup."""

    resource_type: str = Field(description="Requested resource type")
    required: list[str] = Field(
        default_factory=list,
        description="Required fields"
    )
    recommended: list[str] = Field(
        default_factory=list,
        description="Recommended optional fields"
    )
    key_fields: dict[str, dict[str, str]] = Field(
        default_factory=dict,
        description="Field definitions"
    )
    error: str | None = Field(
        default=None,
        description="Error if resource type not found"
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    components: dict[str, str] = Field(
        description="Status of individual components"
    )
