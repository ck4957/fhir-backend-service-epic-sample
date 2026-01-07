"""Tests for HL7v2 and C-CDA parsing tools."""

import pytest

from src.tools.parsing import parse_hl7, parse_ccda


class TestHL7Parsing:
    """Test cases for HL7v2 message parsing."""

    def test_parse_simple_adt_a01(self):
        """Test parsing a simple ADT^A01 message."""
        message = (
            "MSH|^~\\&|SENDING|FAC|RECEIVING|FAC|20240101120000||ADT^A01|MSG001|P|2.5.1\r"
            "PID|1||12345^^^HOSP^MR||DOE^JOHN^A||19800515|M"
        )

        result = parse_hl7.invoke({"message": message})

        assert result.get("error") is None
        assert result["message_type"] == "ADT^A01"
        assert "PID" in result["segments"]
        assert "MSH" in result["segments"]

    def test_parse_message_with_z_segment(self):
        """Test parsing a message with custom Z-segments."""
        message = (
            "MSH|^~\\&|SENDING|FAC|RECEIVING|FAC|20240101120000||ADT^A01|MSG001|P|2.5.1\r"
            "PID|1||12345^^^HOSP^MR||DOE^JOHN||19800515|M\r"
            "ZIN|1|PREMIUM|250.00|MONTHLY"
        )

        result = parse_hl7.invoke({"message": message})

        assert result.get("error") is None
        assert "ZIN" in result["z_segments"]
        assert "inferred_purpose" in result["z_segments"]["ZIN"]

    def test_parse_invalid_message(self):
        """Test parsing an invalid HL7 message."""
        message = "This is not a valid HL7 message"

        result = parse_hl7.invoke({"message": message})

        assert result.get("error") is not None

    def test_parse_message_extracts_version(self):
        """Test that version is extracted from MSH-12."""
        message = "MSH|^~\\&|A|B|C|D|20240101||ADT^A01|1|P|2.5.1\rPID|1||123||DOE^JOHN"

        result = parse_hl7.invoke({"message": message})

        assert result.get("error") is None
        assert result["version"] == "2.5.1"


class TestCCDAParsing:
    """Test cases for C-CDA document parsing."""

    def test_parse_minimal_ccda(self):
        """Test parsing a minimal C-CDA document."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <ClinicalDocument xmlns="urn:hl7-org:v3">
            <code displayName="Continuity of Care Document"/>
            <recordTarget>
                <patientRole>
                    <id root="2.16.840.1.113883.19.5" extension="12345"/>
                    <patient>
                        <name>
                            <given>John</given>
                            <family>Doe</family>
                        </name>
                        <birthTime value="19800515"/>
                        <administrativeGenderCode code="M"/>
                    </patient>
                </patientRole>
            </recordTarget>
        </ClinicalDocument>
        """

        result = parse_ccda.invoke({"xml_content": xml_content})

        assert result.get("error") is None
        assert result["document_type"] == "Continuity of Care Document"
        assert result["patient"]["name"]["family"] == "Doe"
        assert result["patient"]["gender"] == "male"

    def test_parse_invalid_xml(self):
        """Test parsing invalid XML."""
        xml_content = "<not><valid>xml"

        result = parse_ccda.invoke({"xml_content": xml_content})

        assert result.get("error") is not None
        assert "XML parsing error" in result["error"]
