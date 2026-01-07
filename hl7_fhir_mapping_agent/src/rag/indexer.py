"""Document indexing for healthcare specifications."""

import os
from pathlib import Path

from langchain_core.documents import Document

from src.rag.chunking import HealthcareSpecificationSplitter
from src.rag.retriever import get_rag_store


def index_specifications(
    specs_directory: str = "./data/specifications",
    templates_directory: str = "./data/templates",
) -> dict[str, int]:
    """
    Index healthcare specification documents into the RAG store.

    This function reads specification files from the given directories
    and indexes them into appropriate vector store collections.

    Args:
        specs_directory: Directory containing specification documents
        templates_directory: Directory containing Liquid templates

    Returns:
        Dictionary with counts of indexed documents by type
    """
    store = get_rag_store()
    splitter = HealthcareSpecificationSplitter()
    counts = {
        "mapping_rules": 0,
        "fhir_structures": 0,
        "liquid_templates": 0,
    }

    specs_path = Path(specs_directory)
    templates_path = Path(templates_directory)

    # Index mapping guides
    mapping_dir = specs_path / "hl7_to_fhir_ig"
    if mapping_dir.exists():
        for file_path in mapping_dir.glob("*.md"):
            content = file_path.read_text(encoding="utf-8")
            documents = splitter.split_hl7_to_fhir_mapping_guide(
                content, source=file_path.name
            )
            if documents:
                store.add_mapping_rules(documents)
                counts["mapping_rules"] += len(documents)

    # Index FHIR resource definitions
    fhir_dir = specs_path / "fhir_r4"
    if fhir_dir.exists():
        for file_path in fhir_dir.glob("*.md"):
            content = file_path.read_text(encoding="utf-8")
            documents = splitter.split_fhir_resource_definitions(
                content, source=file_path.name
            )
            if documents:
                store.add_fhir_structures(documents)
                counts["fhir_structures"] += len(documents)

    # Index Liquid templates
    hl7v2_templates = templates_path / "hl7v2"
    if hl7v2_templates.exists():
        for file_path in hl7v2_templates.glob("*.liquid"):
            content = file_path.read_text(encoding="utf-8")
            template_name = file_path.stem  # e.g., "ADT_A01"
            documents = splitter.split_liquid_templates(
                content, template_name=template_name
            )
            if documents:
                store.add_liquid_templates(documents)
                counts["liquid_templates"] += len(documents)

    return counts


def index_built_in_mappings() -> int:
    """
    Index the built-in mapping knowledge into the RAG store.

    This provides baseline mapping knowledge even without external
    specification documents.

    Returns:
        Number of documents indexed
    """
    from src.rag.retriever import BUILT_IN_MAPPINGS

    store = get_rag_store()
    documents = []

    for segment, content in BUILT_IN_MAPPINGS.items():
        # Extract target resource from content
        import re

        resource_match = re.search(r"→\s*(\w+)\s*Resource", content)
        target_resource = resource_match.group(1) if resource_match else "Unknown"

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": "built_in",
                    "source_segment": segment,
                    "target_resource": target_resource,
                    "doc_type": "mapping_rule",
                    "chunk_type": "segment_to_resource",
                },
            )
        )

    if documents:
        store.add_mapping_rules(documents)

    return len(documents)


def create_sample_specifications() -> None:
    """
    Create sample specification files for development/testing.

    This creates basic mapping guides in the specifications directory.
    """
    specs_dir = Path("./data/specifications/hl7_to_fhir_ig")
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create sample PID mapping guide
    pid_content = """# PID Segment to Patient Resource Mapping

## Overview

The PID (Patient Identification) segment maps to the FHIR Patient resource.

## Field Mappings

### PID-3: Patient Identifier List → Patient.identifier

The patient identifier list contains MRN, SSN, and other identifiers.

```
PID-3.1 (ID) → identifier.value
PID-3.4 (Assigning Authority) → identifier.system
PID-3.5 (ID Type) → identifier.type
```

### PID-5: Patient Name → Patient.name

```
PID-5.1 (Family Name) → name.family
PID-5.2 (Given Name) → name.given[0]
PID-5.3 (Middle Name) → name.given[1]
PID-5.5 (Prefix) → name.prefix
PID-5.6 (Suffix) → name.suffix
```

### PID-7: Date of Birth → Patient.birthDate

Format: YYYYMMDD → YYYY-MM-DD

### PID-8: Administrative Sex → Patient.gender

| HL7 Code | FHIR Code |
|----------|-----------|
| M | male |
| F | female |
| O | other |
| U | unknown |

### PID-11: Patient Address → Patient.address

```
PID-11.1 → address.line[0]
PID-11.2 → address.line[1]  
PID-11.3 → address.city
PID-11.4 → address.state
PID-11.5 → address.postalCode
PID-11.6 → address.country
```

### PID-13: Phone Number → Patient.telecom

```
system: phone
value: PID-13.1
use: home (default)
```
"""

    (specs_dir / "pid_mapping.md").write_text(pid_content)

    # Create sample OBX mapping guide
    obx_content = """# OBX Segment to Observation Resource Mapping

## Overview

The OBX (Observation/Result) segment maps to the FHIR Observation resource.

## Field Mappings

### OBX-2: Value Type

Determines the type of Observation.value[x]:

| HL7 Type | FHIR Value Type |
|----------|-----------------|
| NM | valueQuantity |
| ST | valueString |
| TX | valueString |
| CE | valueCodeableConcept |
| CWE | valueCodeableConcept |
| DT | valueDateTime |

### OBX-3: Observation Identifier → Observation.code

```
OBX-3.1 (Code) → code.coding[0].code
OBX-3.2 (Text) → code.coding[0].display
OBX-3.3 (Code System) → code.coding[0].system
```

Common code systems:
- LN → http://loinc.org
- SCT → http://snomed.info/sct

### OBX-5: Observation Value → Observation.value[x]

Based on OBX-2 value type.

### OBX-6: Units → Observation.valueQuantity.unit

```
OBX-6.1 → valueQuantity.unit
OBX-6.2 → valueQuantity.code (UCUM)
```

### OBX-8: Abnormal Flags → Observation.interpretation

| HL7 Flag | FHIR Interpretation |
|----------|---------------------|
| H | high |
| L | low |
| N | normal |
| A | abnormal |
| HH | critical high |
| LL | critical low |

### OBX-11: Observation Result Status → Observation.status

| HL7 Status | FHIR Status |
|------------|-------------|
| F | final |
| P | preliminary |
| C | corrected |
| X | cancelled |
"""

    (specs_dir / "obx_mapping.md").write_text(obx_content)

    print(f"Created sample specifications in {specs_dir}")


if __name__ == "__main__":
    # When run directly, create sample specs and index them
    create_sample_specifications()
    counts = index_specifications()
    print(f"Indexed documents: {counts}")

    built_in_count = index_built_in_mappings()
    print(f"Indexed {built_in_count} built-in mapping documents")
