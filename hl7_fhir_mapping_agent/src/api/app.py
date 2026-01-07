"""FastAPI application for HL7/FHIR transformation service."""

import os
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src import __version__
from src.api.models import (
    TransformRequest,
    TransformResponse,
    ParseRequest,
    ParseResponse,
    ValidationRequest,
    ValidationResponse,
    MappingSearchRequest,
    MappingSearchResponse,
    FHIRStructureRequest,
    FHIRStructureResponse,
    HealthCheckResponse,
    AgentMessage,
)

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    print("Starting HL7/FHIR Transformation Agent...")

    # Initialize RAG store with built-in mappings
    try:
        from src.rag.indexer import index_built_in_mappings

        count = index_built_in_mappings()
        print(f"Indexed {count} built-in mapping documents")
    except Exception as e:
        print(f"Warning: Could not initialize RAG store: {e}")

    yield

    # Shutdown
    print("Shutting down HL7/FHIR Transformation Agent...")


# Create FastAPI app
app = FastAPI(
    title="HL7/FHIR Transformation Agent",
    description="""
An AI-powered agent for transforming legacy healthcare data formats 
(HL7v2 and C-CDA) into FHIR R4.

## Features

- **HL7v2 Parsing**: Parse HL7v2 messages into structured JSON
- **C-CDA Parsing**: Parse C-CDA XML documents into structured JSON
- **FHIR Transformation**: Convert HL7v2/C-CDA to FHIR R4 Bundles
- **Validation**: Validate FHIR Bundles against R4 specification
- **RAG-Powered Mapping**: Uses HL7-to-FHIR Implementation Guide for accurate mappings
- **Z-Segment Handling**: Intelligently handles custom vendor-specific segments

## Usage

1. Send your HL7v2 message or C-CDA document to `/transform`
2. The agent will parse, map, and transform it to FHIR
3. The result includes the FHIR Bundle and validation status
""",
    version=__version__,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint."""
    components = {
        "api": "healthy",
        "rag_store": "unknown",
        "llm": "unknown",
    }

    # Check RAG store
    try:
        from src.rag.retriever import get_rag_store

        get_rag_store()
        components["rag_store"] = "healthy"
    except Exception:
        components["rag_store"] = "unavailable"

    # Check LLM availability
    if os.environ.get("OPENAI_API_KEY"):
        components["llm"] = "configured"
    else:
        components["llm"] = "not configured"

    return HealthCheckResponse(
        status="healthy",
        version=__version__,
        components=components,
    )


@app.post("/transform", response_model=TransformResponse)
async def transform_message(request: TransformRequest) -> TransformResponse:
    """
    Transform an HL7v2 message or C-CDA document to FHIR R4.

    This endpoint uses the AI agent to:
    1. Parse the input
    2. Identify segments/sections
    3. Retrieve mapping rules
    4. Generate FHIR Bundle
    5. Validate the output
    """
    try:
        from src.agent.graph import transform_message as agent_transform

        result = await agent_transform(
            raw_input=request.content,
            input_type=request.input_type,
        )

        return TransformResponse(
            success=result.get("fhir_bundle") is not None,
            fhir_bundle=result.get("fhir_bundle"),
            is_valid=result.get("is_valid", False),
            validation_results=result.get("validation_results"),
            segments_identified=result.get("segments_identified", []),
            target_resources=result.get("target_resources", []),
            agent_messages=[
                AgentMessage(**msg) for msg in result.get("messages", [])
            ],
            error=None,
        )

    except Exception as e:
        return TransformResponse(
            success=False,
            error=str(e),
        )


@app.post("/parse", response_model=ParseResponse)
async def parse_input(request: ParseRequest) -> ParseResponse:
    """
    Parse an HL7v2 message or C-CDA document without transformation.

    Useful for inspecting the structure of input data.
    """
    try:
        if request.input_type == "hl7v2":
            from src.tools.parsing import parse_hl7

            result = parse_hl7.invoke({"message": request.content})
        else:
            from src.tools.parsing import parse_ccda

            result = parse_ccda.invoke({"xml_content": request.content})

        if result.get("error"):
            return ParseResponse(
                success=False,
                error=result["error"],
            )

        # Extract segments/sections
        if request.input_type == "hl7v2":
            segments = list(result.get("segments", {}).keys())
            segments.extend(result.get("z_segments", {}).keys())
            message_type = result.get("message_type")
        else:
            segments = list(result.get("sections", {}).keys())
            message_type = result.get("document_type")

        return ParseResponse(
            success=True,
            parsed=result,
            message_type=message_type,
            segments=segments,
        )

    except Exception as e:
        return ParseResponse(
            success=False,
            error=str(e),
        )


@app.post("/validate", response_model=ValidationResponse)
async def validate_bundle(request: ValidationRequest) -> ValidationResponse:
    """
    Validate a FHIR Bundle against the R4 specification.
    """
    from src.tools.validation import validate_fhir

    result = validate_fhir.invoke({
        "bundle": request.bundle,
        "profile": request.profile,
    })

    return ValidationResponse(
        valid=result.get("valid", False),
        errors=result.get("errors", []),
        warnings=result.get("warnings", []),
        info=result.get("info", []),
    )


@app.post("/search-mappings", response_model=MappingSearchResponse)
async def search_mappings(request: MappingSearchRequest) -> MappingSearchResponse:
    """
    Search the mapping knowledge base for transformation rules.
    """
    from src.rag.retriever import search_mapping_rules

    results = await search_mapping_rules(
        query=request.query,
        k=request.k,
        source_segment=request.segment,
    )

    return MappingSearchResponse(
        results=results,
        count=len(results),
    )


@app.get("/fhir-structure/{resource_type}", response_model=FHIRStructureResponse)
async def get_fhir_structure(resource_type: str) -> FHIRStructureResponse:
    """
    Get the structure definition for a FHIR resource type.
    """
    from src.tools.fhir_lookup import get_fhir_structure as lookup

    result = lookup.invoke({"resource_type": resource_type})

    return FHIRStructureResponse(
        resource_type=result.get("resource_type", resource_type),
        required=result.get("required", []),
        recommended=result.get("recommended", []),
        key_fields=result.get("key_fields", {}),
        error=result.get("error"),
    )


@app.get("/fhir-resources")
async def list_fhir_resources() -> dict[str, list[str]]:
    """
    List all available FHIR resource types.
    """
    from src.tools.fhir_lookup import get_all_resource_types

    return {"resources": get_all_resource_types()}


@app.get("/segment-mappings")
async def get_segment_mappings() -> dict[str, dict[str, list[str]]]:
    """
    Get the standard HL7 segment to FHIR resource mappings.
    """
    from src.tools.fhir_lookup import get_segment_to_resource_mapping

    return {"mappings": get_segment_to_resource_mapping()}


def main():
    """Run the application with uvicorn."""
    import uvicorn

    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "8000"))

    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
