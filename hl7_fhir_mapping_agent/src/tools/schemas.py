"""Pydantic schemas for tool inputs and outputs."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class HL7ParseInput(BaseModel):
    """Input schema for HL7v2 message parsing."""

    message: str = Field(
        description="Raw HL7v2 message string with segment delimiters"
    )
    version: str = Field(
        default="2.5.1",
        description="HL7 version (e.g., '2.3', '2.5.1', '2.7')"
    )


class HL7ParseOutput(BaseModel):
    """Output schema for parsed HL7v2 message."""

    message_type: str = Field(description="Message type (e.g., 'ADT^A01')")
    version: str = Field(description="HL7 version from MSH segment")
    segments: dict[str, list[dict[str, Any]]] = Field(
        description="Parsed segments grouped by segment type"
    )
    z_segments: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom Z-segments found in message"
    )
    error: Optional[str] = Field(default=None, description="Error message if parsing failed")


class CCDAParseInput(BaseModel):
    """Input schema for C-CDA document parsing."""

    xml_content: str = Field(description="Raw C-CDA XML document content")


class CCDAParseOutput(BaseModel):
    """Output schema for parsed C-CDA document."""

    document_type: str = Field(description="C-CDA document type")
    patient: dict[str, Any] = Field(description="Patient demographics")
    sections: dict[str, dict[str, Any]] = Field(
        description="Parsed sections (Allergies, Medications, etc.)"
    )
    error: Optional[str] = Field(default=None, description="Error message if parsing failed")


class FHIRStructureLookupInput(BaseModel):
    """Input schema for FHIR structure lookup."""

    resource_type: str = Field(
        description="FHIR resource type (e.g., 'Patient', 'Observation')"
    )
    include_extensions: bool = Field(
        default=False,
        description="Include extension definitions"
    )


class FHIRStructureOutput(BaseModel):
    """Output schema for FHIR structure lookup."""

    resource_type: str = Field(description="FHIR resource type")
    required: list[str] = Field(description="Required fields")
    recommended: list[str] = Field(description="Commonly used optional fields")
    key_fields: dict[str, dict[str, str]] = Field(
        description="Field definitions with cardinality and types"
    )
    error: Optional[str] = Field(default=None, description="Error if resource not found")


class FHIRValidationInput(BaseModel):
    """Input schema for FHIR validation."""

    bundle: dict[str, Any] = Field(description="FHIR Bundle JSON to validate")
    profile: Optional[str] = Field(
        default=None,
        description="Optional profile URL to validate against"
    )


class FHIRValidationOutput(BaseModel):
    """Output schema for FHIR validation."""

    valid: bool = Field(description="Whether the bundle is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    info: list[str] = Field(default_factory=list, description="Informational messages")


class MappingSearchInput(BaseModel):
    """Input schema for mapping guide search."""

    query: str = Field(
        description="Search query for mapping rules (e.g., 'PID to Patient mapping')"
    )
    segment: Optional[str] = Field(
        default=None,
        description="Optional segment filter"
    )
    k: int = Field(default=3, description="Number of results to return")


class LiquidTemplateInput(BaseModel):
    """Input schema for Liquid template retrieval."""

    message_type: str = Field(
        description="HL7 message type (e.g., 'ADT_A01', 'ORU_R01')"
    )
    segment: Optional[str] = Field(
        default=None,
        description="Specific segment to focus on"
    )
