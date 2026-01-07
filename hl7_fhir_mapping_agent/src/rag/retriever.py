"""RAG retriever for healthcare specification lookup."""

import os
from typing import Any

from langchain_core.documents import Document


class HealthcareRAGStore:
    """
    Vector store manager for healthcare specification retrieval.

    Maintains separate collections for different document types:
    - mapping_rules: HL7/CCDA to FHIR mapping rules
    - fhir_structures: FHIR resource definitions
    - hl7_segments: HL7 segment definitions
    - liquid_templates: Transformation template examples
    """

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        embedding_model: str = "text-embedding-3-large",
    ):
        """
        Initialize the healthcare RAG store.

        Args:
            persist_directory: Directory to persist vector store
            embedding_model: OpenAI embedding model to use
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self._stores: dict[str, Any] = {}
        self._embeddings = None

    def _get_embeddings(self):
        """Lazy load embeddings model."""
        if self._embeddings is None:
            try:
                from langchain_openai import OpenAIEmbeddings

                self._embeddings = OpenAIEmbeddings(
                    model=self.embedding_model,
                )
            except ImportError:
                raise ImportError(
                    "langchain-openai required. Install with: pip install langchain-openai"
                )
        return self._embeddings

    def _get_store(self, collection_name: str):
        """Get or create a vector store for a collection."""
        if collection_name not in self._stores:
            try:
                from langchain_chroma import Chroma
            except ImportError:
                # Fallback to in-memory store
                from langchain_core.vectorstores import InMemoryVectorStore

                self._stores[collection_name] = InMemoryVectorStore(
                    embedding=self._get_embeddings()
                )
                return self._stores[collection_name]

            collection_path = os.path.join(
                self.persist_directory, collection_name
            )

            self._stores[collection_name] = Chroma(
                collection_name=collection_name,
                embedding_function=self._get_embeddings(),
                persist_directory=collection_path,
            )

        return self._stores[collection_name]

    def add_mapping_rules(self, documents: list[Document]) -> None:
        """Add mapping rule documents to the store."""
        store = self._get_store("mapping_rules")
        store.add_documents(documents)

    def add_fhir_structures(self, documents: list[Document]) -> None:
        """Add FHIR structure documents to the store."""
        store = self._get_store("fhir_structures")
        store.add_documents(documents)

    def add_hl7_segments(self, documents: list[Document]) -> None:
        """Add HL7 segment definition documents to the store."""
        store = self._get_store("hl7_segments")
        store.add_documents(documents)

    def add_liquid_templates(self, documents: list[Document]) -> None:
        """Add Liquid template documents to the store."""
        store = self._get_store("liquid_templates")
        store.add_documents(documents)

    def search_mapping_rules(
        self,
        query: str,
        k: int = 3,
        source_segment: str | None = None,
    ) -> list[Document]:
        """
        Search for mapping rules.

        Args:
            query: Search query
            k: Number of results
            source_segment: Optional filter by source segment

        Returns:
            List of relevant documents
        """
        store = self._get_store("mapping_rules")

        filter_dict = None
        if source_segment:
            filter_dict = {"source_segment": source_segment.upper()}

        try:
            if filter_dict:
                results = store.similarity_search(query, k=k, filter=filter_dict)
            else:
                results = store.similarity_search(query, k=k)
        except Exception:
            # Fallback without filter if filter not supported
            results = store.similarity_search(query, k=k)

        return results

    def search_fhir_structure(
        self,
        resource_type: str,
        k: int = 3,
    ) -> list[Document]:
        """
        Search for FHIR resource structure information.

        Args:
            resource_type: FHIR resource type to search for
            k: Number of results

        Returns:
            List of relevant documents
        """
        store = self._get_store("fhir_structures")
        query = f"FHIR {resource_type} resource structure required fields"
        return store.similarity_search(query, k=k)

    def search_templates(
        self,
        message_type: str,
        k: int = 3,
    ) -> list[Document]:
        """
        Search for Liquid template examples.

        Args:
            message_type: HL7 message type (e.g., "ADT_A01")
            k: Number of results

        Returns:
            List of relevant documents
        """
        store = self._get_store("liquid_templates")
        query = f"Liquid template for {message_type} HL7 message FHIR conversion"
        return store.similarity_search(query, k=k)


# Global store instance (lazy initialized)
_global_store: HealthcareRAGStore | None = None


def get_rag_store() -> HealthcareRAGStore:
    """Get the global RAG store instance."""
    global _global_store
    if _global_store is None:
        persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "./data/chroma")
        _global_store = HealthcareRAGStore(persist_directory=persist_dir)
    return _global_store


async def search_mapping_rules(
    query: str,
    k: int = 3,
    source_segment: str | None = None,
) -> list[str]:
    """
    Search for mapping rules from the RAG store.

    This is the main entry point used by the agent for retrieving
    HL7-to-FHIR mapping guidance.

    Args:
        query: Natural language search query
        k: Number of results to return
        source_segment: Optional filter by HL7 segment

    Returns:
        List of relevant mapping rule text snippets
    """
    store = get_rag_store()

    try:
        documents = store.search_mapping_rules(
            query=query,
            k=k,
            source_segment=source_segment,
        )
        return [doc.page_content for doc in documents]
    except Exception as e:
        # Return empty if store not initialized or error occurs
        # This allows the agent to work even without RAG data
        return [f"RAG search unavailable: {e}. Using built-in mapping knowledge."]


# Built-in mapping knowledge (fallback when RAG is not available)
BUILT_IN_MAPPINGS = {
    "PID": """
## PID (Patient Identification) → Patient Resource

### Field Mappings:
- PID-3 (Patient ID) → Patient.identifier
- PID-5 (Patient Name) → Patient.name
  - PID-5.1 (Family Name) → Patient.name.family
  - PID-5.2 (Given Name) → Patient.name.given
- PID-7 (Date of Birth) → Patient.birthDate
- PID-8 (Sex) → Patient.gender
  - M → male, F → female, O → other, U → unknown
- PID-11 (Address) → Patient.address
- PID-13 (Phone) → Patient.telecom
- PID-19 (SSN) → Patient.identifier (system: http://hl7.org/fhir/sid/us-ssn)
""",
    "PV1": """
## PV1 (Patient Visit) → Encounter Resource

### Field Mappings:
- PV1-2 (Patient Class) → Encounter.class
  - I (Inpatient) → IMP
  - O (Outpatient) → AMB
  - E (Emergency) → EMER
- PV1-3 (Assigned Location) → Encounter.location
- PV1-7 (Attending Doctor) → Encounter.participant
- PV1-19 (Visit Number) → Encounter.identifier
- PV1-44 (Admit Date/Time) → Encounter.period.start
- PV1-45 (Discharge Date/Time) → Encounter.period.end
""",
    "OBX": """
## OBX (Observation) → Observation Resource

### Field Mappings:
- OBX-2 (Value Type) → Determines Observation.value[x] type
  - NM → valueQuantity
  - ST → valueString
  - CE/CWE → valueCodeableConcept
- OBX-3 (Observation ID) → Observation.code
- OBX-5 (Observation Value) → Observation.value[x]
- OBX-6 (Units) → Observation.valueQuantity.unit
- OBX-8 (Abnormal Flags) → Observation.interpretation
- OBX-11 (Status) → Observation.status
  - F (Final) → final
  - P (Preliminary) → preliminary
- OBX-14 (Date/Time) → Observation.effectiveDateTime
""",
    "DG1": """
## DG1 (Diagnosis) → Condition Resource

### Field Mappings:
- DG1-3 (Diagnosis Code) → Condition.code
- DG1-4 (Diagnosis Description) → Condition.code.text
- DG1-5 (Diagnosis Date/Time) → Condition.onsetDateTime
- DG1-6 (Diagnosis Type) → Condition.category
- DG1-15 (Diagnosis Priority) → Used for Condition ordering
""",
    "NK1": """
## NK1 (Next of Kin) → RelatedPerson Resource

### Field Mappings:
- NK1-2 (Name) → RelatedPerson.name
- NK1-3 (Relationship) → RelatedPerson.relationship
- NK1-4 (Address) → RelatedPerson.address
- NK1-5 (Phone) → RelatedPerson.telecom
- NK1-7 (Contact Role) → RelatedPerson.relationship
""",
    "AL1": """
## AL1 (Allergy) → AllergyIntolerance Resource

### Field Mappings:
- AL1-2 (Allergen Type) → AllergyIntolerance.category
  - DA (Drug) → medication
  - FA (Food) → food
  - EA (Environment) → environment
- AL1-3 (Allergen Code) → AllergyIntolerance.code
- AL1-4 (Allergy Severity) → AllergyIntolerance.criticality
- AL1-5 (Allergy Reaction) → AllergyIntolerance.reaction.manifestation
""",
}


def get_built_in_mapping(segment: str) -> str | None:
    """Get built-in mapping knowledge for a segment."""
    return BUILT_IN_MAPPINGS.get(segment.upper())
