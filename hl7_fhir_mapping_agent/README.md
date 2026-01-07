# HL7/FHIR Mapping Agent

An AI-powered agent for transforming legacy healthcare data formats (HL7v2 and C-CDA) into FHIR R4.

## Overview

This project implements a "Template Engineer" approach where an AI agent uses RAG (Retrieval-Augmented Generation) to look up HL7-to-FHIR mapping specifications and generate accurate, reproducible FHIR transformations.

### Key Features

- **HL7v2 Parsing**: Parse HL7v2 messages into structured JSON using `hl7apy`
- **C-CDA Parsing**: Parse C-CDA XML documents with section extraction
- **RAG-Powered Mapping**: Uses HL7-to-FHIR Implementation Guide for accurate mappings
- **FHIR Validation**: Validate output against FHIR R4 specification
- **Z-Segment Handling**: Intelligently handles custom vendor-specific segments
- **Self-Correction**: Agent automatically fixes validation errors

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Input (HL7/CCDA)                │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│  1. Parse Input (hl7apy / lxml)                         │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│  2. RAG Lookup (ChromaDB + OpenAI Embeddings)           │
│     - HL7-to-FHIR Mapping Guide                         │
│     - FHIR Resource Definitions                         │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│  3. Transform to FHIR (LangGraph Agent + GPT-4)         │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│  4. Validate Output (fhir.resources)                    │
│     ↓ If errors, self-correct and retry                 │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│                 Validated FHIR Bundle                   │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

```bash
# Clone the repository
cd hl7_fhir_mapping_agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy environment file and add your API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the API

```bash
# Start the FastAPI server
uvicorn src.api.app:app --reload

# Or use the CLI command
hl7-fhir-agent
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

### Example Usage

#### Transform HL7v2 to FHIR

```bash
curl -X POST http://localhost:8000/transform \
  -H "Content-Type: application/json" \
  -d '{
    "content": "MSH|^~\\&|HOSP|FAC|OTHER|FAC|20240101120000||ADT^A01|123456|P|2.5.1\rPID|1||12345^^^HOSP^MR||DOE^JOHN^A||19800515|M|||123 MAIN ST^^ANYTOWN^CA^12345||555-123-4567",
    "input_type": "hl7v2",
    "validate": true
  }'
```

#### Parse HL7v2 Message

```bash
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{
    "content": "MSH|^~\\&|...",
    "input_type": "hl7v2"
  }'
```

#### Validate FHIR Bundle

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "bundle": {
      "resourceType": "Bundle",
      "type": "batch",
      "entry": [...]
    }
  }'
```

## Project Structure

```
hl7_fhir_mapping_agent/
├── src/
│   ├── agent/           # LangGraph agent implementation
│   │   ├── graph.py     # Workflow graph definition
│   │   ├── state.py     # State type definitions
│   │   ├── nodes.py     # Node implementations
│   │   └── prompts.py   # System prompts
│   │
│   ├── tools/           # Agent tools
│   │   ├── parsing.py   # HL7/CCDA parsing
│   │   ├── fhir_lookup.py  # FHIR structure lookup
│   │   └── validation.py   # FHIR validation
│   │
│   ├── rag/             # RAG components
│   │   ├── chunking.py  # Document chunking
│   │   ├── retriever.py # Vector store retrieval
│   │   └── indexer.py   # Document indexing
│   │
│   └── api/             # FastAPI application
│       ├── app.py       # Main application
│       └── models.py    # Request/response models
│
├── data/
│   ├── templates/       # Liquid templates
│   ├── specifications/  # HL7/FHIR specs
│   └── examples/        # Sample messages
│
└── tests/               # Test suite
```

## API Endpoints

| Endpoint                 | Method | Description                           |
| ------------------------ | ------ | ------------------------------------- |
| `/`                      | GET    | Health check                          |
| `/transform`             | POST   | Transform HL7/CCDA to FHIR            |
| `/parse`                 | POST   | Parse HL7/CCDA without transformation |
| `/validate`              | POST   | Validate FHIR Bundle                  |
| `/search-mappings`       | POST   | Search mapping knowledge base         |
| `/fhir-structure/{type}` | GET    | Get FHIR resource structure           |
| `/fhir-resources`        | GET    | List available FHIR resources         |
| `/segment-mappings`      | GET    | Get HL7 segment to FHIR mappings      |

## Supported HL7v2 Segments

| Segment | Maps To            | Description            |
| ------- | ------------------ | ---------------------- |
| MSH     | MessageHeader      | Message header         |
| PID     | Patient            | Patient identification |
| PV1     | Encounter          | Patient visit          |
| OBX     | Observation        | Observation/result     |
| DG1     | Condition          | Diagnosis              |
| NK1     | RelatedPerson      | Next of kin            |
| AL1     | AllergyIntolerance | Allergy                |
| IN1     | Coverage           | Insurance              |
| OBR     | DiagnosticReport   | Observation request    |
| Z\*     | (Inferred)         | Custom segments        |

## Supported C-CDA Sections

| Section       | Maps To                       |
| ------------- | ----------------------------- |
| Allergies     | AllergyIntolerance            |
| Medications   | MedicationStatement           |
| Problems      | Condition                     |
| Procedures    | Procedure                     |
| Results       | Observation, DiagnosticReport |
| Encounters    | Encounter                     |
| Immunizations | Immunization                  |
| Vital Signs   | Observation                   |

## Configuration

Environment variables (see `.env.example`):

| Variable             | Description        | Default                  |
| -------------------- | ------------------ | ------------------------ |
| `OPENAI_API_KEY`     | OpenAI API key     | Required                 |
| `LLM_MODEL`          | LLM model to use   | `gpt-4o`                 |
| `EMBEDDING_MODEL`    | Embedding model    | `text-embedding-3-large` |
| `API_HOST`           | API host           | `0.0.0.0`                |
| `API_PORT`           | API port           | `8000`                   |
| `CHROMA_PERSIST_DIR` | ChromaDB directory | `./data/chroma`          |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/

# Type checking
mypy src/
```

## License

MIT
