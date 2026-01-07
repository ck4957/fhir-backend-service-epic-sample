"""HL7v2 and C-CDA parsing tools."""

from typing import Any

from langchain_core.tools import tool

from src.tools.schemas import HL7ParseInput, CCDAParseInput


def _extract_segment_fields(segment: Any) -> dict[str, Any]:
    """Extract fields from an HL7 segment into a dictionary."""
    seg_data = {}
    seg_name = segment.name

    for i, field in enumerate(segment.children, 1):
        field_key = f"{seg_name}.{i}"

        if hasattr(field, "value") and field.value:
            seg_data[field_key] = field.value
        elif hasattr(field, "children") and field.children:
            # Handle components
            components = []
            for comp in field.children:
                if hasattr(comp, "value") and comp.value:
                    components.append(comp.value)
                elif hasattr(comp, "children"):
                    # Handle sub-components
                    sub_comps = [
                        sc.value
                        for sc in comp.children
                        if hasattr(sc, "value") and sc.value
                    ]
                    if sub_comps:
                        components.append(sub_comps)
            if components:
                seg_data[field_key] = components

    return seg_data


@tool(args_schema=HL7ParseInput)
def parse_hl7(message: str, version: str = "2.5.1") -> dict[str, Any]:
    """
    Parse an HL7v2 message into a structured JSON format.

    This tool breaks down a raw HL7v2 message string into its component
    segments (MSH, PID, PV1, OBX, etc.) and fields. It also identifies
    any custom Z-segments for special handling.

    Args:
        message: Raw HL7v2 message string with segment delimiters (\\r or \\n)
        version: Expected HL7 version (default: 2.5.1)

    Returns:
        Dictionary containing:
        - message_type: The HL7 message type (e.g., "ADT^A01")
        - version: HL7 version from the message
        - segments: Dictionary of parsed segments grouped by type
        - z_segments: Any custom Z-segments found
        - error: Error message if parsing failed
    """
    try:
        from hl7apy.parser import parse_message
        from hl7apy.exceptions import HL7apyException
    except ImportError:
        return {
            "error": "hl7apy library not installed. Run: pip install hl7apy",
            "message_type": "",
            "version": version,
            "segments": {},
            "z_segments": {},
        }

    # Normalize line endings
    message = message.replace("\n", "\r").replace("\r\r", "\r")

    try:
        parsed = parse_message(message, find_groups=True)

        # Extract message type from MSH-9
        msg_type_field = parsed.msh.msh_9
        if hasattr(msg_type_field, "msh_9_1") and hasattr(msg_type_field, "msh_9_2"):
            message_type = f"{msg_type_field.msh_9_1.value}^{msg_type_field.msh_9_2.value}"
        else:
            message_type = str(msg_type_field.value) if hasattr(msg_type_field, "value") else "UNKNOWN"

        # Extract version from MSH-12
        msg_version = parsed.msh.msh_12.value if hasattr(parsed.msh.msh_12, "value") else version

        result = {
            "message_type": message_type,
            "version": msg_version,
            "segments": {},
            "z_segments": {},
            "error": None,
        }

        # Process each segment
        for segment in parsed.children:
            seg_name = segment.name
            seg_data = _extract_segment_fields(segment)

            # Check if it's a Z-segment (custom/vendor-specific)
            if seg_name.startswith("Z"):
                if seg_name not in result["z_segments"]:
                    result["z_segments"][seg_name] = {
                        "instances": [],
                        "inferred_purpose": _infer_z_segment_purpose(seg_name),
                    }
                result["z_segments"][seg_name]["instances"].append(seg_data)
            else:
                if seg_name not in result["segments"]:
                    result["segments"][seg_name] = []
                result["segments"][seg_name].append(seg_data)

        return result

    except HL7apyException as e:
        return {
            "error": f"HL7 parsing error: {str(e)}",
            "message_type": "",
            "version": version,
            "segments": {},
            "z_segments": {},
        }
    except Exception as e:
        return {
            "error": f"Unexpected parsing error: {str(e)}",
            "message_type": "",
            "version": version,
            "segments": {},
            "z_segments": {},
        }


def _infer_z_segment_purpose(segment_name: str) -> str:
    """Infer the purpose of a custom Z-segment based on naming patterns."""
    common_patterns = {
        "ZIN": "Insurance/Coverage information",
        "ZPD": "Extended patient demographics",
        "ZPV": "Extended visit information",
        "ZDG": "Extended diagnosis information",
        "ZPM": "Patient matching/identity",
        "ZEV": "Extended event information",
        "ZRX": "Extended pharmacy/prescription",
        "ZLB": "Extended laboratory information",
        "ZAL": "Extended allergy information",
        "ZCM": "Custom comments/notes",
    }

    # Check for exact match
    if segment_name in common_patterns:
        return common_patterns[segment_name]

    # Check for prefix patterns
    for prefix, purpose in common_patterns.items():
        if segment_name.startswith(prefix[:2]):
            return f"Possibly related to: {purpose}"

    return "Unknown custom segment - requires LLM inference for mapping"


@tool(args_schema=CCDAParseInput)
def parse_ccda(xml_content: str) -> dict[str, Any]:
    """
    Parse a C-CDA document into a structured JSON format.

    This tool extracts patient information and clinical sections
    (Allergies, Medications, Problems, etc.) from a C-CDA XML document.

    Args:
        xml_content: Raw C-CDA XML document content

    Returns:
        Dictionary containing:
        - document_type: The C-CDA document type
        - patient: Patient demographics
        - sections: Dictionary of parsed clinical sections
        - error: Error message if parsing failed
    """
    try:
        from lxml import etree
    except ImportError:
        return {
            "error": "lxml library not installed. Run: pip install lxml",
            "document_type": "",
            "patient": {},
            "sections": {},
        }

    CCDA_NAMESPACES = {
        "cda": "urn:hl7-org:v3",
        "sdtc": "urn:hl7-org:sdtc",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    # Template ID to section name mapping
    TEMPLATE_ID_MAP = {
        "2.16.840.1.113883.10.20.22.2.6.1": "Allergies",
        "2.16.840.1.113883.10.20.22.2.1.1": "Medications",
        "2.16.840.1.113883.10.20.22.2.5.1": "Problems",
        "2.16.840.1.113883.10.20.22.2.7.1": "Procedures",
        "2.16.840.1.113883.10.20.22.2.3.1": "Results",
        "2.16.840.1.113883.10.20.22.2.22.1": "Encounters",
        "2.16.840.1.113883.10.20.22.2.2.1": "Immunizations",
        "2.16.840.1.113883.10.20.22.2.4.1": "Vital Signs",
        "2.16.840.1.113883.10.20.22.2.17": "Social History",
        "2.16.840.1.113883.10.20.22.2.21.1": "Advance Directives",
        "2.16.840.1.113883.10.20.22.2.15": "Family History",
        "2.16.840.1.113883.10.20.22.2.8": "Assessment",
        "2.16.840.1.113883.10.20.22.2.10": "Plan of Treatment",
    }

    try:
        root = etree.fromstring(xml_content.encode())

        # Extract document type
        doc_type_elem = root.xpath("//cda:code", namespaces=CCDA_NAMESPACES)
        document_type = (
            doc_type_elem[0].get("displayName", "Unknown")
            if doc_type_elem
            else "Unknown"
        )

        # Extract patient information
        patient = _extract_ccda_patient(root, CCDA_NAMESPACES)

        # Extract sections
        sections = {}
        section_elems = root.xpath("//cda:section", namespaces=CCDA_NAMESPACES)

        for section in section_elems:
            template_ids = section.xpath(
                "cda:templateId/@root", namespaces=CCDA_NAMESPACES
            )

            for template_id in template_ids:
                if template_id in TEMPLATE_ID_MAP:
                    section_name = TEMPLATE_ID_MAP[template_id]
                    sections[section_name] = _extract_ccda_section(
                        section, section_name, CCDA_NAMESPACES
                    )
                    break

        return {
            "document_type": document_type,
            "patient": patient,
            "sections": sections,
            "error": None,
        }

    except etree.XMLSyntaxError as e:
        return {
            "error": f"XML parsing error: {str(e)}",
            "document_type": "",
            "patient": {},
            "sections": {},
        }
    except Exception as e:
        return {
            "error": f"Unexpected parsing error: {str(e)}",
            "document_type": "",
            "patient": {},
            "sections": {},
        }


def _extract_ccda_patient(root: Any, namespaces: dict) -> dict[str, Any]:
    """Extract patient demographics from C-CDA document."""
    patient = {}

    # Patient record target
    patient_elem = root.xpath(
        "//cda:recordTarget/cda:patientRole", namespaces=namespaces
    )

    if not patient_elem:
        return patient

    patient_elem = patient_elem[0]

    # Patient IDs
    ids = patient_elem.xpath("cda:id", namespaces=namespaces)
    patient["identifiers"] = [
        {"root": id_elem.get("root"), "extension": id_elem.get("extension")}
        for id_elem in ids
    ]

    # Patient name
    name_elem = patient_elem.xpath(
        "cda:patient/cda:name", namespaces=namespaces
    )
    if name_elem:
        name = name_elem[0]
        given = name.xpath("cda:given/text()", namespaces=namespaces)
        family = name.xpath("cda:family/text()", namespaces=namespaces)
        patient["name"] = {
            "given": list(given),
            "family": family[0] if family else None,
        }

    # Birth date
    birth = patient_elem.xpath(
        "cda:patient/cda:birthTime/@value", namespaces=namespaces
    )
    if birth:
        patient["birthDate"] = birth[0]

    # Gender
    gender = patient_elem.xpath(
        "cda:patient/cda:administrativeGenderCode/@code", namespaces=namespaces
    )
    if gender:
        gender_map = {"M": "male", "F": "female", "UN": "unknown"}
        patient["gender"] = gender_map.get(gender[0], gender[0])

    # Address
    addr = patient_elem.xpath("cda:addr", namespaces=namespaces)
    if addr:
        addr = addr[0]
        patient["address"] = {
            "street": addr.xpath("cda:streetAddressLine/text()", namespaces=namespaces),
            "city": (addr.xpath("cda:city/text()", namespaces=namespaces) or [None])[0],
            "state": (addr.xpath("cda:state/text()", namespaces=namespaces) or [None])[0],
            "postalCode": (addr.xpath("cda:postalCode/text()", namespaces=namespaces) or [None])[0],
        }

    return patient


def _extract_ccda_section(
    section: Any, section_name: str, namespaces: dict
) -> dict[str, Any]:
    """Extract entries from a C-CDA section."""
    result = {
        "title": None,
        "entries": [],
    }

    # Section title
    title = section.xpath("cda:title/text()", namespaces=namespaces)
    if title:
        result["title"] = title[0]

    # Extract entries based on section type
    entries = section.xpath("cda:entry", namespaces=namespaces)

    for entry in entries:
        entry_data = _extract_entry_data(entry, section_name, namespaces)
        if entry_data:
            result["entries"].append(entry_data)

    return result


def _extract_entry_data(
    entry: Any, section_name: str, namespaces: dict
) -> dict[str, Any] | None:
    """Extract data from a C-CDA entry element."""
    # This is a simplified extraction - full implementation would handle
    # each section type specifically

    entry_data = {}

    # Look for common clinical statement types
    for stmt_type in ["observation", "act", "substanceAdministration", "procedure", "encounter"]:
        stmt = entry.xpath(f"cda:{stmt_type}", namespaces=namespaces)
        if stmt:
            stmt = stmt[0]

            # Status
            status = stmt.xpath("cda:statusCode/@code", namespaces=namespaces)
            if status:
                entry_data["status"] = status[0]

            # Code
            code = stmt.xpath("cda:code", namespaces=namespaces)
            if code:
                entry_data["code"] = {
                    "code": code[0].get("code"),
                    "displayName": code[0].get("displayName"),
                    "codeSystem": code[0].get("codeSystem"),
                    "codeSystemName": code[0].get("codeSystemName"),
                }

            # Effective time
            eff_time = stmt.xpath("cda:effectiveTime", namespaces=namespaces)
            if eff_time:
                low = eff_time[0].xpath("cda:low/@value", namespaces=namespaces)
                high = eff_time[0].xpath("cda:high/@value", namespaces=namespaces)
                value = eff_time[0].get("value")

                if value:
                    entry_data["effectiveTime"] = value
                elif low or high:
                    entry_data["effectiveTime"] = {
                        "low": low[0] if low else None,
                        "high": high[0] if high else None,
                    }

            # Value (for observations)
            value = stmt.xpath("cda:value", namespaces=namespaces)
            if value:
                val_elem = value[0]
                val_type = val_elem.get("{http://www.w3.org/2001/XMLSchema-instance}type", "")

                if "PQ" in val_type:  # Physical quantity
                    entry_data["value"] = {
                        "value": val_elem.get("value"),
                        "unit": val_elem.get("unit"),
                    }
                elif "CD" in val_type or "CE" in val_type:  # Coded value
                    entry_data["value"] = {
                        "code": val_elem.get("code"),
                        "displayName": val_elem.get("displayName"),
                    }
                else:
                    entry_data["value"] = val_elem.get("value")

            entry_data["_type"] = stmt_type
            break

    return entry_data if entry_data else None
