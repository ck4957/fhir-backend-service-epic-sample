"""FHIR resource structure lookup tools."""

from typing import Any

from langchain_core.tools import tool

from src.tools.schemas import FHIRStructureLookupInput


# FHIR R4 resource structure definitions
FHIR_STRUCTURES: dict[str, dict[str, Any]] = {
    "Patient": {
        "required": ["identifier OR name"],
        "recommended": ["birthDate", "gender", "address", "telecom"],
        "key_fields": {
            "identifier": {
                "cardinality": "0..*",
                "type": "Identifier",
                "description": "Patient identifiers (MRN, SSN, etc.)",
            },
            "name": {
                "cardinality": "0..*",
                "type": "HumanName",
                "description": "Patient's names",
            },
            "gender": {
                "cardinality": "0..1",
                "type": "code",
                "valueset": "administrative-gender",
                "values": ["male", "female", "other", "unknown"],
            },
            "birthDate": {
                "cardinality": "0..1",
                "type": "date",
                "description": "Date of birth",
            },
            "address": {
                "cardinality": "0..*",
                "type": "Address",
                "description": "Patient addresses",
            },
            "telecom": {
                "cardinality": "0..*",
                "type": "ContactPoint",
                "description": "Contact details (phone, email)",
            },
            "maritalStatus": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "description": "Marital status",
            },
            "communication": {
                "cardinality": "0..*",
                "type": "BackboneElement",
                "description": "Language preferences",
            },
        },
    },
    "Observation": {
        "required": ["status", "code"],
        "recommended": ["subject", "effectiveDateTime", "value[x]"],
        "key_fields": {
            "status": {
                "cardinality": "1..1",
                "type": "code",
                "valueset": "observation-status",
                "values": [
                    "registered",
                    "preliminary",
                    "final",
                    "amended",
                    "corrected",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                ],
            },
            "code": {
                "cardinality": "1..1",
                "type": "CodeableConcept",
                "description": "Type of observation (LOINC code)",
            },
            "subject": {
                "cardinality": "0..1",
                "type": "Reference(Patient)",
                "description": "Who the observation is about",
            },
            "effectiveDateTime": {
                "cardinality": "0..1",
                "type": "dateTime",
                "description": "When the observation was made",
            },
            "value[x]": {
                "cardinality": "0..1",
                "type": "Quantity|string|CodeableConcept|boolean|integer|Range|Ratio|SampledData|time|dateTime|Period",
                "description": "Observation value",
            },
            "interpretation": {
                "cardinality": "0..*",
                "type": "CodeableConcept",
                "description": "High/Low/Normal interpretation",
            },
            "referenceRange": {
                "cardinality": "0..*",
                "type": "BackboneElement",
                "description": "Normal range for value",
            },
        },
    },
    "Encounter": {
        "required": ["status", "class"],
        "recommended": ["subject", "period", "type", "participant"],
        "key_fields": {
            "status": {
                "cardinality": "1..1",
                "type": "code",
                "valueset": "encounter-status",
                "values": [
                    "planned",
                    "arrived",
                    "triaged",
                    "in-progress",
                    "onleave",
                    "finished",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                ],
            },
            "class": {
                "cardinality": "1..1",
                "type": "Coding",
                "description": "Classification of encounter (ambulatory, emergency, inpatient)",
            },
            "subject": {
                "cardinality": "0..1",
                "type": "Reference(Patient)",
                "description": "The patient in the encounter",
            },
            "period": {
                "cardinality": "0..1",
                "type": "Period",
                "description": "Start and end time of encounter",
            },
            "type": {
                "cardinality": "0..*",
                "type": "CodeableConcept",
                "description": "Specific type of encounter",
            },
            "participant": {
                "cardinality": "0..*",
                "type": "BackboneElement",
                "description": "Practitioners involved in encounter",
            },
            "location": {
                "cardinality": "0..*",
                "type": "BackboneElement",
                "description": "Where the encounter took place",
            },
        },
    },
    "Condition": {
        "required": ["subject"],
        "recommended": ["code", "clinicalStatus", "verificationStatus"],
        "key_fields": {
            "clinicalStatus": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "valueset": "condition-clinical",
                "values": ["active", "recurrence", "relapse", "inactive", "remission", "resolved"],
            },
            "verificationStatus": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "valueset": "condition-ver-status",
                "values": ["unconfirmed", "provisional", "differential", "confirmed", "refuted", "entered-in-error"],
            },
            "code": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "description": "Diagnosis code (ICD-10, SNOMED)",
            },
            "subject": {
                "cardinality": "1..1",
                "type": "Reference(Patient)",
                "description": "Who has the condition",
            },
            "onsetDateTime": {
                "cardinality": "0..1",
                "type": "dateTime",
                "description": "When condition started",
            },
            "recordedDate": {
                "cardinality": "0..1",
                "type": "dateTime",
                "description": "When condition was recorded",
            },
        },
    },
    "AllergyIntolerance": {
        "required": ["patient"],
        "recommended": ["code", "clinicalStatus", "verificationStatus", "type", "criticality"],
        "key_fields": {
            "clinicalStatus": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "values": ["active", "inactive", "resolved"],
            },
            "verificationStatus": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "values": ["unconfirmed", "confirmed", "refuted", "entered-in-error"],
            },
            "type": {
                "cardinality": "0..1",
                "type": "code",
                "values": ["allergy", "intolerance"],
            },
            "criticality": {
                "cardinality": "0..1",
                "type": "code",
                "values": ["low", "high", "unable-to-assess"],
            },
            "code": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "description": "Substance or class of substances",
            },
            "patient": {
                "cardinality": "1..1",
                "type": "Reference(Patient)",
                "description": "Who has the allergy",
            },
            "reaction": {
                "cardinality": "0..*",
                "type": "BackboneElement",
                "description": "Adverse reaction details",
            },
        },
    },
    "DiagnosticReport": {
        "required": ["status", "code"],
        "recommended": ["subject", "effectiveDateTime", "result"],
        "key_fields": {
            "status": {
                "cardinality": "1..1",
                "type": "code",
                "values": ["registered", "partial", "preliminary", "final", "amended", "corrected", "appended", "cancelled", "entered-in-error", "unknown"],
            },
            "code": {
                "cardinality": "1..1",
                "type": "CodeableConcept",
                "description": "Report type (LOINC)",
            },
            "subject": {
                "cardinality": "0..1",
                "type": "Reference(Patient)",
                "description": "Subject of report",
            },
            "effectiveDateTime": {
                "cardinality": "0..1",
                "type": "dateTime",
                "description": "Clinically relevant time",
            },
            "result": {
                "cardinality": "0..*",
                "type": "Reference(Observation)",
                "description": "Observations that are part of report",
            },
            "conclusion": {
                "cardinality": "0..1",
                "type": "string",
                "description": "Clinical conclusion",
            },
        },
    },
    "RelatedPerson": {
        "required": ["patient"],
        "recommended": ["relationship", "name"],
        "key_fields": {
            "patient": {
                "cardinality": "1..1",
                "type": "Reference(Patient)",
                "description": "The patient this person is related to",
            },
            "relationship": {
                "cardinality": "0..*",
                "type": "CodeableConcept",
                "description": "Nature of relationship",
            },
            "name": {
                "cardinality": "0..*",
                "type": "HumanName",
                "description": "Name of related person",
            },
            "telecom": {
                "cardinality": "0..*",
                "type": "ContactPoint",
                "description": "Contact details",
            },
            "address": {
                "cardinality": "0..*",
                "type": "Address",
                "description": "Address",
            },
        },
    },
    "Coverage": {
        "required": ["status", "beneficiary", "payor"],
        "recommended": ["subscriber", "subscriberId", "type"],
        "key_fields": {
            "status": {
                "cardinality": "1..1",
                "type": "code",
                "values": ["active", "cancelled", "draft", "entered-in-error"],
            },
            "type": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "description": "Coverage type (medical, dental, etc.)",
            },
            "subscriber": {
                "cardinality": "0..1",
                "type": "Reference(Patient|RelatedPerson)",
                "description": "Subscriber to the policy",
            },
            "subscriberId": {
                "cardinality": "0..1",
                "type": "string",
                "description": "Subscriber ID",
            },
            "beneficiary": {
                "cardinality": "1..1",
                "type": "Reference(Patient)",
                "description": "Plan beneficiary",
            },
            "payor": {
                "cardinality": "1..*",
                "type": "Reference(Organization|Patient|RelatedPerson)",
                "description": "Issuer of the policy",
            },
            "class": {
                "cardinality": "0..*",
                "type": "BackboneElement",
                "description": "Coverage class (group, plan, etc.)",
            },
        },
    },
    "Immunization": {
        "required": ["status", "vaccineCode", "patient", "occurrenceDateTime"],
        "recommended": ["primarySource", "location", "performer"],
        "key_fields": {
            "status": {
                "cardinality": "1..1",
                "type": "code",
                "values": ["completed", "entered-in-error", "not-done"],
            },
            "vaccineCode": {
                "cardinality": "1..1",
                "type": "CodeableConcept",
                "description": "Vaccine product administered (CVX code)",
            },
            "patient": {
                "cardinality": "1..1",
                "type": "Reference(Patient)",
                "description": "Who was immunized",
            },
            "occurrenceDateTime": {
                "cardinality": "1..1",
                "type": "dateTime",
                "description": "When vaccine was administered",
            },
            "primarySource": {
                "cardinality": "0..1",
                "type": "boolean",
                "description": "Is this from the primary source",
            },
            "lotNumber": {
                "cardinality": "0..1",
                "type": "string",
                "description": "Vaccine lot number",
            },
        },
    },
    "Procedure": {
        "required": ["status", "subject"],
        "recommended": ["code", "performedDateTime", "performer"],
        "key_fields": {
            "status": {
                "cardinality": "1..1",
                "type": "code",
                "values": ["preparation", "in-progress", "not-done", "on-hold", "stopped", "completed", "entered-in-error", "unknown"],
            },
            "code": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "description": "Procedure code (CPT, SNOMED)",
            },
            "subject": {
                "cardinality": "1..1",
                "type": "Reference(Patient)",
                "description": "Who the procedure was performed on",
            },
            "performedDateTime": {
                "cardinality": "0..1",
                "type": "dateTime",
                "description": "When the procedure was performed",
            },
            "performer": {
                "cardinality": "0..*",
                "type": "BackboneElement",
                "description": "Who performed the procedure",
            },
        },
    },
    "MedicationStatement": {
        "required": ["status", "medicationCodeableConcept OR medicationReference", "subject"],
        "recommended": ["effectiveDateTime", "dosage"],
        "key_fields": {
            "status": {
                "cardinality": "1..1",
                "type": "code",
                "values": ["active", "completed", "entered-in-error", "intended", "stopped", "on-hold", "unknown", "not-taken"],
            },
            "medicationCodeableConcept": {
                "cardinality": "0..1",
                "type": "CodeableConcept",
                "description": "Medication code (RxNorm)",
            },
            "subject": {
                "cardinality": "1..1",
                "type": "Reference(Patient)",
                "description": "Who is taking the medication",
            },
            "effectiveDateTime": {
                "cardinality": "0..1",
                "type": "dateTime",
                "description": "When medication was taken",
            },
            "dosage": {
                "cardinality": "0..*",
                "type": "Dosage",
                "description": "How the medication is taken",
            },
        },
    },
    "MessageHeader": {
        "required": ["eventCoding OR eventUri", "source"],
        "recommended": ["destination", "sender", "focus"],
        "key_fields": {
            "eventCoding": {
                "cardinality": "0..1",
                "type": "Coding",
                "description": "Code for the event this message represents",
            },
            "source": {
                "cardinality": "1..1",
                "type": "BackboneElement",
                "description": "Message source application",
            },
            "destination": {
                "cardinality": "0..*",
                "type": "BackboneElement",
                "description": "Message destination application(s)",
            },
            "focus": {
                "cardinality": "0..*",
                "type": "Reference(Any)",
                "description": "The actual content of the message",
            },
        },
    },
}


@tool(args_schema=FHIRStructureLookupInput)
def get_fhir_structure(
    resource_type: str, include_extensions: bool = False
) -> dict[str, Any]:
    """
    Retrieve the FHIR resource structure definition.

    This tool returns required fields, cardinality, data types, and
    allowed values for a specified FHIR R4 resource type.

    Args:
        resource_type: FHIR resource type (e.g., "Patient", "Observation")
        include_extensions: Whether to include extension definitions (not yet implemented)

    Returns:
        Dictionary containing:
        - resource_type: The requested resource type
        - required: List of required fields
        - recommended: Commonly used optional fields
        - key_fields: Detailed field definitions
        - error: Error message if resource not found
    """
    if resource_type not in FHIR_STRUCTURES:
        available = ", ".join(sorted(FHIR_STRUCTURES.keys()))
        return {
            "resource_type": resource_type,
            "error": f"Unknown resource type: {resource_type}. Available: {available}",
            "required": [],
            "recommended": [],
            "key_fields": {},
        }

    structure = FHIR_STRUCTURES[resource_type].copy()
    structure["resource_type"] = resource_type
    structure["error"] = None

    return structure


def get_all_resource_types() -> list[str]:
    """Get a list of all available FHIR resource types."""
    return sorted(FHIR_STRUCTURES.keys())


def get_segment_to_resource_mapping() -> dict[str, list[str]]:
    """
    Get the standard HL7v2 segment to FHIR resource mapping.

    Returns a dictionary mapping HL7 segment names to their
    corresponding FHIR resource types.
    """
    return {
        # Patient Administration
        "MSH": ["MessageHeader"],
        "PID": ["Patient"],
        "PD1": ["Patient"],
        "NK1": ["RelatedPerson"],
        "PV1": ["Encounter"],
        "PV2": ["Encounter"],
        # Clinical
        "DG1": ["Condition"],
        "OBX": ["Observation"],
        "OBR": ["DiagnosticReport", "ServiceRequest"],
        "AL1": ["AllergyIntolerance"],
        "RXA": ["Immunization"],
        "RXE": ["MedicationRequest"],
        "RXO": ["MedicationRequest"],
        # Financial/Insurance
        "IN1": ["Coverage"],
        "IN2": ["Coverage"],
        "GT1": ["RelatedPerson"],
        # Orders
        "ORC": ["ServiceRequest"],
        # Common
        "NTE": ["Annotation"],  # Usually attached to another resource
    }
