"""Healthcare-specific document chunking strategies."""

import re
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class HealthcareSpecificationSplitter:
    """
    Custom splitter for HL7/FHIR specification documents.

    This splitter uses semantic chunking based on healthcare-specific
    patterns rather than just character counts. It identifies segment-to-resource
    mapping sections and keeps them together for better retrieval.
    """

    def __init__(
        self,
        chunk_size: int = 1500,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the healthcare specification splitter.

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
        """
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " "],
        )

        # Pattern to identify HL7 segment to FHIR resource mappings
        self.segment_pattern = re.compile(
            r"(PID|MSH|OBX|PV1|PV2|NK1|DG1|OBR|AL1|IN1|IN2|GT1|RXA|RXE|ORC|NTE|EVN|MRG|ZIN|ZPD)"
            r"\s*[-–>to]+\s*"
            r"(Patient|Observation|Encounter|Condition|DiagnosticReport|AllergyIntolerance|"
            r"Coverage|RelatedPerson|Immunization|MedicationRequest|ServiceRequest|MessageHeader|Procedure)",
            re.IGNORECASE,
        )

        # Pattern for C-CDA section mappings
        self.ccda_pattern = re.compile(
            r"(Allergies?|Medications?|Problems?|Procedures?|Results?|Encounters?|"
            r"Immunizations?|Vital\s*Signs?|Social\s*History|Family\s*History)"
            r"\s*[-–>to]+\s*"
            r"(AllergyIntolerance|MedicationStatement|MedicationRequest|Condition|"
            r"Procedure|Observation|DiagnosticReport|Encounter|Immunization)",
            re.IGNORECASE,
        )

    def split_hl7_to_fhir_mapping_guide(
        self, content: str, source: str = "hl7_to_fhir_ig"
    ) -> list[Document]:
        """
        Split HL7-to-FHIR mapping guide by segment-to-resource pairs.

        Args:
            content: The full text content of the mapping guide
            source: Source identifier for metadata

        Returns:
            List of Document objects with appropriate metadata
        """
        chunks: list[Document] = []

        # Split by major sections first (headers)
        sections = re.split(r"\n(?=#{1,3}\s)", content)

        for section in sections:
            if not section.strip():
                continue

            # Check if this is a mapping section
            segment_match = self.segment_pattern.search(section)
            ccda_match = self.ccda_pattern.search(section)

            if segment_match:
                source_segment = segment_match.group(1).upper()
                target_resource = segment_match.group(2)

                chunks.append(
                    Document(
                        page_content=section.strip(),
                        metadata={
                            "source": source,
                            "source_segment": source_segment,
                            "target_resource": target_resource,
                            "doc_type": "mapping_rule",
                            "chunk_type": "segment_to_resource",
                        },
                    )
                )
            elif ccda_match:
                source_section = ccda_match.group(1)
                target_resource = ccda_match.group(2)

                chunks.append(
                    Document(
                        page_content=section.strip(),
                        metadata={
                            "source": source,
                            "source_section": source_section,
                            "target_resource": target_resource,
                            "doc_type": "mapping_rule",
                            "chunk_type": "ccda_section_to_resource",
                        },
                    )
                )
            else:
                # Use base splitter for non-mapping content
                sub_chunks = self.base_splitter.split_text(section)
                for i, chunk_text in enumerate(sub_chunks):
                    chunks.append(
                        Document(
                            page_content=chunk_text.strip(),
                            metadata={
                                "source": source,
                                "doc_type": "specification",
                                "chunk_index": i,
                            },
                        )
                    )

        return chunks

    def split_fhir_resource_definitions(
        self, content: str, source: str = "fhir_r4_spec"
    ) -> list[Document]:
        """
        Split FHIR resource definition documents.

        Args:
            content: FHIR resource definition content
            source: Source identifier

        Returns:
            List of Document objects
        """
        chunks: list[Document] = []

        # Pattern to identify resource definitions
        resource_pattern = re.compile(
            r"(?:^|\n)(#{1,3}\s*)?(Patient|Observation|Encounter|Condition|"
            r"DiagnosticReport|AllergyIntolerance|Coverage|RelatedPerson|"
            r"Immunization|MedicationRequest|MedicationStatement|ServiceRequest|"
            r"Procedure|Bundle|MessageHeader)\b",
            re.IGNORECASE,
        )

        # Split by resource sections
        parts = resource_pattern.split(content)

        current_resource = None
        current_content = []

        for i, part in enumerate(parts):
            resource_match = resource_pattern.match(part) if part else None

            if resource_match:
                # Save previous resource section
                if current_resource and current_content:
                    full_content = "".join(current_content)
                    if full_content.strip():
                        chunks.append(
                            Document(
                                page_content=full_content.strip(),
                                metadata={
                                    "source": source,
                                    "resource_type": current_resource,
                                    "doc_type": "fhir_structure",
                                },
                            )
                        )

                current_resource = part.strip()
                current_content = [part]
            else:
                current_content.append(part)

        # Don't forget the last section
        if current_resource and current_content:
            full_content = "".join(current_content)
            if full_content.strip():
                chunks.append(
                    Document(
                        page_content=full_content.strip(),
                        metadata={
                            "source": source,
                            "resource_type": current_resource,
                            "doc_type": "fhir_structure",
                        },
                    )
                )

        return chunks

    def split_liquid_templates(
        self, content: str, template_name: str, source: str = "fhir_converter"
    ) -> list[Document]:
        """
        Split Liquid template content for indexing.

        Keeps templates relatively intact for retrieval.

        Args:
            content: Liquid template content
            template_name: Name of the template (e.g., "ADT_A01")
            source: Source identifier

        Returns:
            List of Document objects
        """
        # For templates, we generally want to keep them whole
        # but can split very large ones

        if len(content) <= 3000:
            return [
                Document(
                    page_content=content,
                    metadata={
                        "source": source,
                        "template_name": template_name,
                        "doc_type": "liquid_template",
                    },
                )
            ]

        # For large templates, split by resource includes
        chunks: list[Document] = []
        include_pattern = re.compile(r"({%\s*include\s+['\"]Resource/(\w+)['\"].*?%})", re.DOTALL)

        matches = list(include_pattern.finditer(content))

        if not matches:
            # No includes found, use base splitter
            sub_chunks = self.base_splitter.split_text(content)
            for i, chunk_text in enumerate(sub_chunks):
                chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata={
                            "source": source,
                            "template_name": template_name,
                            "doc_type": "liquid_template",
                            "chunk_index": i,
                        },
                    )
                )
        else:
            # Split around resource includes
            last_end = 0
            for match in matches:
                resource_name = match.group(2)
                start = max(0, match.start() - 200)  # Include context
                end = min(len(content), match.end() + 200)

                chunk_content = content[start:end]
                chunks.append(
                    Document(
                        page_content=chunk_content,
                        metadata={
                            "source": source,
                            "template_name": template_name,
                            "doc_type": "liquid_template",
                            "resource_focus": resource_name,
                        },
                    )
                )
                last_end = end

        return chunks
