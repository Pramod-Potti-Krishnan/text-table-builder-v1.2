"""
v1.1 Legacy Routes for Hero Slides
===================================

Provides field-by-field generation using StructuredTextGenerator
for hero slides (title_slide, section_divider, closing_slide).

This maintains backward compatibility with the v1.1 format ownership architecture.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.models.requests import StructuredTextGenerationRequest
from app.core.generators import StructuredTextGenerator
from app.core.llm_client import get_llm_client
from app.core.session_manager import get_session_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/v1.1",
    tags=["v1.1-legacy"]
)


def get_structured_generator() -> StructuredTextGenerator:
    """
    Dependency to create StructuredTextGenerator instance.

    Returns:
        StructuredTextGenerator with LLM client and session manager
    """
    llm_client = get_llm_client()
    session_manager = get_session_manager()

    return StructuredTextGenerator(
        llm_client=llm_client,
        session_manager=session_manager
    )


@router.post("/generate")
async def generate_structured_content(
    request: StructuredTextGenerationRequest,
    generator: StructuredTextGenerator = Depends(get_structured_generator)
) -> Dict[str, Any]:
    """
    Generate structured content using v1.1 field-by-field approach.

    This endpoint is used for hero slides (title_slide, section_divider, closing_slide)
    where simple field-by-field generation works well.

    Args:
        request: StructuredTextGenerationRequest with field specifications
        generator: StructuredTextGenerator dependency

    Returns:
        Dictionary with generated content for each field

    Example Request:
        ```json
        {
          "presentation_id": "pres_123",
          "slide_id": "slide_001",
          "slide_number": 1,
          "layout_id": "L29",
          "layout_name": "Hero Title",
          "layout_subtype": "Title",
          "field_specifications": {
            "slide_title": {
              "format_type": "plain_text",
              "format_owner": "layout_builder",
              "max_chars": 60
            },
            "subtitle": {
              "format_type": "plain_text",
              "format_owner": "layout_builder",
              "max_chars": 100
            }
          },
          "layout_schema": {...},
          "content_guidance": {
            "title": "AI in Healthcare",
            "narrative": "Introduction to AI applications...",
            "key_points": [...]
          }
        }
        ```

    Example Response:
        ```json
        {
          "layout_id": "L29",
          "content": {
            "slide_title": "AI in Healthcare: Transforming Patient Outcomes",
            "subtitle": "Revolutionizing diagnostic accuracy through advanced machine learning"
          },
          "metadata": {
            "generation_time_ms": 1234.56,
            "fields_generated": 2,
            "field_metadata": {
              "slide_title": {
                "char_count": 47,
                "format_type": "plain_text",
                "validation_status": "passed"
              },
              "subtitle": {
                "char_count": 69,
                "format_type": "plain_text",
                "validation_status": "passed"
              }
            }
          }
        }
        ```
    """
    try:
        logger.info(
            f"v1.1 Legacy: Generating structured content for {request.slide_id} "
            f"({request.layout_id})"
        )

        # Generate content using StructuredTextGenerator
        result = await generator.generate(request)

        logger.info(
            f"v1.1 Legacy: Generated {len(result['content'])} fields for {request.slide_id} "
            f"in {result['metadata']['generation_time_ms']:.2f}ms"
        )

        return result

    except Exception as e:
        logger.error(f"v1.1 Legacy: Error generating content for {request.slide_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating structured content: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for v1.1 legacy endpoints.

    Returns:
        Status information
    """
    return {
        "status": "healthy",
        "version": "1.1.0",
        "endpoint": "v1.1-legacy",
        "purpose": "Hero slides (field-by-field generation)",
        "generator": "StructuredTextGenerator"
    }
