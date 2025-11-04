"""
FastAPI Routes for v1.2 Element-Based Content Generation

This module defines the API endpoints for the v1.2 deterministic assembly architecture.

Endpoints:
    POST /v1.2/generate - Generate slide content using element-based approach
    GET /v1.2/variants - List all available variants
    GET /v1.2/variant/{variant_id} - Get details about a specific variant
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import json
import logging
from pathlib import Path

from ..models.v1_2_models import (
    V1_2_GenerationRequest,
    V1_2_GenerationResponse,
    AvailableVariantsResponse,
    VariantInfo,
    ElementContent,
    GenerationMetadata,
    ValidationResult,
    CharacterCountViolation
)
from ..core import ElementBasedContentGenerator
from ..services import create_llm_callable_async


logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/v1.2", tags=["v1.2"])


# Dependency to get or create generator instance with ASYNC LLM callable
def get_generator() -> ElementBasedContentGenerator:
    """
    Get ElementBasedContentGenerator instance with async LLM service.

    Uses the async LLM service wrapper configured for Vertex AI with ADC.
    This properly works within FastAPI's event loop without conflicts.

    Returns:
        ElementBasedContentGenerator instance with async LLM integration
    """
    # Create ASYNC LLM callable from service (production-quality)
    llm_callable = create_llm_callable_async()

    return ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates",
        enable_parallel=True,
        max_workers=5
    )


@router.post("/generate", response_model=V1_2_GenerationResponse)
async def generate_slide_content(
    request: V1_2_GenerationRequest,
    generator: ElementBasedContentGenerator = Depends(get_generator)
) -> V1_2_GenerationResponse:
    """
    Generate slide content using v1.2 element-based approach.

    This endpoint:
    1. Loads the variant specification
    2. Builds context from the request
    3. Generates prompts for each element
    4. Calls LLM to generate content for each element (parallel or sequential)
    5. Assembles content into the HTML template
    6. Optionally validates character counts
    7. Returns the assembled HTML and metadata

    Args:
        request: V1_2_GenerationRequest with variant_id and specifications
        generator: ElementBasedContentGenerator instance (injected)

    Returns:
        V1_2_GenerationResponse with generated HTML and metadata
    """
    try:
        # Generate slide content using ASYNC method (production-quality)
        result = await generator.generate_slide_content_async(
            variant_id=request.variant_id,
            slide_spec=request.slide_spec.model_dump(),
            presentation_spec=request.presentation_spec.model_dump() if request.presentation_spec else None,
            element_relationships=request.element_relationships
        )

        # Validate character counts if requested
        validation = None
        if request.validate_character_counts:
            validation_result = generator.validate_character_counts(
                element_contents=result["elements"],
                variant_id=request.variant_id
            )

            validation = ValidationResult(
                valid=validation_result["valid"],
                violations=[
                    CharacterCountViolation(**v)
                    for v in validation_result["violations"]
                ]
            )

        # Convert elements to Pydantic models
        elements = [
            ElementContent(**elem)
            for elem in result["elements"]
        ]

        # Build response
        return V1_2_GenerationResponse(
            success=True,
            html=result["html"],
            elements=elements,
            metadata=GenerationMetadata(**result["metadata"]),
            validation=validation,
            variant_id=result["variant_id"],
            template_path=result["template_path"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Variant or template not found: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/variants", response_model=AvailableVariantsResponse)
async def list_available_variants() -> AvailableVariantsResponse:
    """
    List all available variants organized by slide type.

    Returns:
        AvailableVariantsResponse with all variants grouped by type
    """
    try:
        # Load variant index
        index_path = Path("app/variant_specs/variant_index.json")
        with open(index_path, 'r') as f:
            variant_index = json.load(f)

        # Transform into response format
        slide_types = {}
        for slide_type, type_info in variant_index["slide_types"].items():
            variants = [
                VariantInfo(
                    variant_id=v["variant_id"],
                    slide_type=slide_type,
                    description=type_info["description"],
                    layout=v["layout"]
                )
                for v in type_info["variants"]
            ]
            slide_types[slide_type] = variants

        return AvailableVariantsResponse(
            total_variants=variant_index["total_variants"],
            slide_types=slide_types
        )

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Variant index not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load variants: {str(e)}")


@router.get("/variant/{variant_id}")
async def get_variant_details(variant_id: str):
    """
    Get detailed information about a specific variant.

    Args:
        variant_id: The variant identifier (e.g., "matrix_2x2")

    Returns:
        Dictionary with variant specification details
    """
    try:
        generator = get_generator()
        metadata = generator.prompt_builder.get_variant_metadata(variant_id)
        spec = generator.prompt_builder.load_variant_spec(variant_id)

        return {
            "variant_id": metadata["variant_id"],
            "slide_type": metadata["slide_type"],
            "description": metadata["description"],
            "template_path": metadata["template_path"],
            "layout": metadata["layout"],
            "element_count": metadata["element_count"],
            "elements": spec["elements"]
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load variant details: {str(e)}")
