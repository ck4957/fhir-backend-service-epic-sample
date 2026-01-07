"""FHIR validation tools."""

from typing import Any

from langchain_core.tools import tool

from src.tools.schemas import FHIRValidationInput


@tool(args_schema=FHIRValidationInput)
def validate_fhir(bundle: dict[str, Any], profile: str | None = None) -> dict[str, Any]:
    """
    Validate a FHIR Bundle against the FHIR R4 specification.

    This tool checks a FHIR Bundle for structural validity, required fields,
    cardinality constraints, and reference integrity. It uses the fhir.resources
    library for Python-based validation.

    Args:
        bundle: FHIR Bundle JSON to validate
        profile: Optional profile URL to validate against (not yet supported)

    Returns:
        Dictionary containing:
        - valid: Whether the bundle passed validation
        - errors: List of validation errors
        - warnings: List of validation warnings
        - info: Informational messages
    """
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # Check basic bundle structure
    if not isinstance(bundle, dict):
        return {
            "valid": False,
            "errors": ["Bundle must be a JSON object"],
            "warnings": [],
            "info": [],
        }

    resource_type = bundle.get("resourceType")
    if resource_type != "Bundle":
        errors.append(f"Expected resourceType 'Bundle', got '{resource_type}'")

    bundle_type = bundle.get("type")
    if bundle_type not in ["batch", "transaction", "document", "message", "searchset", "collection", "history"]:
        errors.append(f"Invalid bundle type: {bundle_type}")

    # Validate entries
    entries = bundle.get("entry", [])
    if not entries:
        warnings.append("Bundle has no entries")

    # Try to validate using fhir.resources
    try:
        from fhir.resources.bundle import Bundle as FHIRBundle

        FHIRBundle.model_validate(bundle)
        info.append("Bundle passes fhir.resources structural validation")

    except ImportError:
        warnings.append("fhir.resources not installed - using basic validation only")
        # Fall back to basic validation
        for i, entry in enumerate(entries):
            entry_errors = _validate_entry(entry, i)
            errors.extend(entry_errors)

    except Exception as e:
        error_msg = str(e)
        # Parse Pydantic validation errors
        if "validation error" in error_msg.lower():
            errors.append(f"FHIR validation error: {error_msg}")
        else:
            errors.append(f"Validation failed: {error_msg}")

    # Additional semantic validations
    semantic_issues = _validate_bundle_semantics(bundle)
    errors.extend(semantic_issues.get("errors", []))
    warnings.extend(semantic_issues.get("warnings", []))

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }


def _validate_entry(entry: dict[str, Any], index: int) -> list[str]:
    """Validate a single bundle entry."""
    errors = []

    if not isinstance(entry, dict):
        errors.append(f"Entry {index}: must be a JSON object")
        return errors

    resource = entry.get("resource")
    if not resource:
        errors.append(f"Entry {index}: missing 'resource' property")
        return errors

    resource_type = resource.get("resourceType")
    if not resource_type:
        errors.append(f"Entry {index}: resource missing 'resourceType'")
        return errors

    # Check for required fields based on resource type
    required_fields = _get_required_fields(resource_type)
    for field in required_fields:
        if "|" in field:
            # OR condition (e.g., "name|identifier")
            alternatives = field.split("|")
            if not any(alt.strip() in resource for alt in alternatives):
                errors.append(
                    f"Entry {index} ({resource_type}): missing one of required fields: {field}"
                )
        elif field not in resource:
            errors.append(f"Entry {index} ({resource_type}): missing required field '{field}'")

    return errors


def _get_required_fields(resource_type: str) -> list[str]:
    """Get required fields for a FHIR resource type."""
    required_by_type = {
        "Patient": [],  # Patient has no required fields in base spec
        "Observation": ["status", "code"],
        "Encounter": ["status", "class"],
        "Condition": ["subject"],
        "AllergyIntolerance": ["patient"],
        "DiagnosticReport": ["status", "code"],
        "Procedure": ["status", "subject"],
        "MedicationStatement": ["status", "subject"],
        "Immunization": ["status", "vaccineCode", "patient"],
        "Coverage": ["status", "beneficiary", "payor"],
        "RelatedPerson": ["patient"],
        "MessageHeader": ["source"],
    }
    return required_by_type.get(resource_type, [])


def _validate_bundle_semantics(bundle: dict[str, Any]) -> dict[str, list[str]]:
    """Perform semantic validation on the bundle."""
    errors: list[str] = []
    warnings: list[str] = []

    entries = bundle.get("entry", [])

    # Track resource references for integrity check
    resource_ids: set[str] = set()
    references_used: list[tuple[int, str]] = []

    for i, entry in enumerate(entries):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType", "")

        # Collect resource IDs
        if "id" in resource:
            full_id = f"{resource_type}/{resource['id']}"
            resource_ids.add(full_id)

        # Collect references
        _collect_references(resource, references_used, i)

    # Check for unresolved references (within bundle)
    for entry_idx, ref in references_used:
        if ref.startswith("urn:uuid:"):
            # UUID references should be in fullUrl
            full_urls = {
                e.get("fullUrl", "") for e in entries
            }
            if ref not in full_urls:
                warnings.append(
                    f"Entry {entry_idx}: reference '{ref}' may not resolve within bundle"
                )
        elif "/" in ref and not ref.startswith("http"):
            # Relative reference
            if ref not in resource_ids:
                warnings.append(
                    f"Entry {entry_idx}: reference '{ref}' not found in bundle"
                )

    return {"errors": errors, "warnings": warnings}


def _collect_references(
    obj: Any, references: list[tuple[int, str]], entry_idx: int
) -> None:
    """Recursively collect all references in a resource."""
    if isinstance(obj, dict):
        if "reference" in obj and isinstance(obj["reference"], str):
            references.append((entry_idx, obj["reference"]))
        for value in obj.values():
            _collect_references(value, references, entry_idx)
    elif isinstance(obj, list):
        for item in obj:
            _collect_references(item, references, entry_idx)


class FHIRValidatorService:
    """
    Client for external FHIR Validator HTTP service.

    This class can be used to validate against the official HL7 FHIR
    Validator running as an HTTP service for more comprehensive validation.
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize the validator service client.

        Args:
            base_url: Base URL of the FHIR validator service
        """
        self.base_url = base_url.rstrip("/")

    async def validate(
        self,
        resource: dict[str, Any],
        profile: str | None = None,
    ) -> dict[str, Any]:
        """
        Validate a FHIR resource using the external validator service.

        Args:
            resource: FHIR resource or bundle to validate
            profile: Optional profile URL to validate against

        Returns:
            Validation results with errors, warnings, and info
        """
        import httpx

        params = {}
        if profile:
            params["profile"] = profile

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/validate",
                    json=resource,
                    params=params,
                    headers={"Content-Type": "application/fhir+json"},
                )

                if response.status_code == 200:
                    result = response.json()
                    return self._parse_operation_outcome(result)
                else:
                    return {
                        "valid": False,
                        "errors": [f"Validator service error: {response.status_code}"],
                        "warnings": [],
                        "info": [],
                    }

        except httpx.ConnectError:
            return {
                "valid": False,
                "errors": [f"Could not connect to validator service at {self.base_url}"],
                "warnings": [],
                "info": [],
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validator service error: {str(e)}"],
                "warnings": [],
                "info": [],
            }

    def _parse_operation_outcome(
        self, outcome: dict[str, Any]
    ) -> dict[str, Any]:
        """Parse OperationOutcome into structured result."""
        errors: list[str] = []
        warnings: list[str] = []
        info: list[str] = []

        issues = outcome.get("issue", [])
        for issue in issues:
            severity = issue.get("severity", "")
            message = issue.get("diagnostics", issue.get("details", {}).get("text", "Unknown issue"))
            location = issue.get("location", [])
            location_str = f" at {location[0]}" if location else ""

            full_message = f"{message}{location_str}"

            if severity == "error" or severity == "fatal":
                errors.append(full_message)
            elif severity == "warning":
                warnings.append(full_message)
            else:
                info.append(full_message)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "info": info,
        }
