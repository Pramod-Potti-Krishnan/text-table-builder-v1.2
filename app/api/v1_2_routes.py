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
import os
import asyncio
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
from ..services import create_llm_callable_async, create_llm_callable_pooled, get_pool_metrics
from ..services.llm_pool import QueueFullError


logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/v1.2", tags=["v1.2"])


# Dependency to get or create generator instance with ASYNC LLM callable
def get_generator() -> ElementBasedContentGenerator:
    """
    Get ElementBasedContentGenerator instance with async LLM service.

    Uses pooled or direct async LLM service based on USE_LLM_POOL env variable.
    Pooled version provides concurrency control and rate limiting.

    Environment variables:
        USE_LLM_POOL: Set to "true" to use pooled version (default: true)

    Returns:
        ElementBasedContentGenerator instance with async LLM integration
    """
    # Check if pooling is enabled (default: true for production)
    use_pool = os.getenv("USE_LLM_POOL", "true").lower() == "true"

    if use_pool:
        # Use pooled callable with concurrency control and rate limiting
        llm_callable = create_llm_callable_pooled()
        print("[GEN-INIT] Using pooled LLM callable with concurrency control")
    else:
        # Use direct async callable (no pooling)
        llm_callable = create_llm_callable_async()
        print("[GEN-INIT] Using direct async LLM callable")

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
    import time
    start_time = time.time()

    # Extract request info for logging
    base_variant_id = request.variant_id
    layout_id = request.layout_id or "L25"
    slide_title = ''
    if request.slide_spec and hasattr(request.slide_spec, 'slide_title'):
        slide_title = (request.slide_spec.slide_title or '')[:40]

    # Layout-aware variant resolution: if layout_id is not L25, try layout-specific variant
    effective_variant_id = base_variant_id
    if layout_id != "L25":
        layout_variant_id = f"{base_variant_id}_{layout_id.lower()}"
        # Check if layout-specific variant exists in the index
        variant_index = generator.prompt_builder.variant_index
        if layout_variant_id in variant_index.get("variant_lookup", {}):
            effective_variant_id = layout_variant_id
            print(f"[GEN-LAYOUT] Resolved {base_variant_id} + {layout_id} -> {effective_variant_id}")

    # REQUEST ARRIVAL LOGGING
    print(f"[GEN-REQ] variant={effective_variant_id}, layout={layout_id}, title='{slide_title}'")

    try:
        # Generate slide content using ASYNC method (production-quality)
        result = await generator.generate_slide_content_async(
            variant_id=effective_variant_id,
            slide_spec=request.slide_spec.model_dump(),
            presentation_spec=request.presentation_spec.model_dump() if request.presentation_spec else None,
            element_relationships=request.element_relationships
        )

        # Validate character counts if requested
        validation = None
        if request.validate_character_counts:
            validation_result = generator.validate_character_counts(
                element_contents=result["elements"],
                variant_id=effective_variant_id
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

        # SUCCESS LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        html_len = len(result.get("html", ""))
        print(f"[GEN-OK] variant={effective_variant_id}, time={elapsed_ms}ms, html={html_len} chars")

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
        # VALIDATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[GEN-400] variant={effective_variant_id}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(status_code=400, detail=str(e))

    except FileNotFoundError as e:
        # NOT FOUND ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[GEN-404] variant={effective_variant_id}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(status_code=404, detail=f"Variant or template not found: {str(e)}")

    except QueueFullError as e:
        # QUEUE FULL ERROR - Service at capacity
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[GEN-429] variant={effective_variant_id}, time={elapsed_ms}ms, error=Queue full")
        raise HTTPException(
            status_code=429,
            detail="Service at capacity. Please retry in 30 seconds.",
            headers={"Retry-After": "30"}
        )

    except asyncio.TimeoutError:
        # LLM TIMEOUT ERROR
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[GEN-504] variant={effective_variant_id}, time={elapsed_ms}ms, error=LLM timeout")
        raise HTTPException(
            status_code=504,
            detail="LLM request timed out. Please retry."
        )

    except Exception as e:
        # GENERATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[GEN-ERROR] variant={effective_variant_id}, time={elapsed_ms}ms, error={str(e)[:100]}")
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


@router.get("/health/pool")
async def get_pool_health():
    """
    Get LLM connection pool health and metrics.

    Returns pool status (healthy/degraded/overloaded) and metrics including:
    - Active and queued requests
    - Request counts and success/failure rates
    - Average latency
    - Pool configuration

    Use this endpoint to monitor service capacity and health.
    """
    metrics = get_pool_metrics()

    # Determine overall health
    status = metrics.get("status", "unknown")
    is_healthy = status == "healthy"

    return {
        "healthy": is_healthy,
        "status": status,
        "metrics": metrics
    }
