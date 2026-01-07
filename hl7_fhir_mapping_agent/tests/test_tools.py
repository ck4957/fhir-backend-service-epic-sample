"""Tests for FHIR tools."""

import pytest

from src.tools.fhir_lookup import get_fhir_structure, get_all_resource_types
from src.tools.validation import validate_fhir


class TestFHIRLookup:
    """Test cases for FHIR structure lookup."""

    def test_get_patient_structure(self):
        """Test getting Patient resource structure."""
        result = get_fhir_structure.invoke({"resource_type": "Patient"})

        assert result.get("error") is None
        assert result["resource_type"] == "Patient"
        assert "name" in result["key_fields"]
        assert "gender" in result["key_fields"]
        assert "birthDate" in result["key_fields"]

    def test_get_observation_structure(self):
        """Test getting Observation resource structure."""
        result = get_fhir_structure.invoke({"resource_type": "Observation"})

        assert result.get("error") is None
        assert "status" in result["required"]
        assert "code" in result["required"]
        assert result["key_fields"]["status"]["cardinality"] == "1..1"

    def test_get_unknown_resource(self):
        """Test getting an unknown resource type."""
        result = get_fhir_structure.invoke({"resource_type": "UnknownResource"})

        assert result.get("error") is not None
        assert "Unknown resource type" in result["error"]

    def test_get_all_resource_types(self):
        """Test getting all available resource types."""
        resources = get_all_resource_types()

        assert "Patient" in resources
        assert "Observation" in resources
        assert "Encounter" in resources
        assert len(resources) > 5


class TestFHIRValidation:
    """Test cases for FHIR validation."""

    def test_validate_valid_bundle(self):
        """Test validating a valid FHIR bundle."""
        bundle = {
            "resourceType": "Bundle",
            "type": "batch",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "example",
                        "name": [{"family": "Doe", "given": ["John"]}],
                        "gender": "male",
                        "birthDate": "1980-05-15",
                    }
                }
            ],
        }

        result = validate_fhir.invoke({"bundle": bundle})

        # Should have no errors (may have warnings)
        assert len(result.get("errors", [])) == 0

    def test_validate_invalid_bundle_type(self):
        """Test validating a bundle with invalid type."""
        bundle = {
            "resourceType": "Bundle",
            "type": "invalid-type",
            "entry": [],
        }

        result = validate_fhir.invoke({"bundle": bundle})

        assert result["valid"] is False
        assert any("Invalid bundle type" in e for e in result["errors"])

    def test_validate_missing_required_fields(self):
        """Test validating with missing required fields."""
        bundle = {
            "resourceType": "Bundle",
            "type": "batch",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Observation",
                        # Missing required: status, code
                    }
                }
            ],
        }

        result = validate_fhir.invoke({"bundle": bundle})

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_non_dict_input(self):
        """Test validating non-dict input."""
        result = validate_fhir.invoke({"bundle": "not a dict"})

        assert result["valid"] is False
        assert "must be a JSON object" in result["errors"][0]
