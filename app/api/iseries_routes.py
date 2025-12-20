"""
I-Series Layout API Routes for Text Service v1.2

Provides combined image + text generation endpoints for I-series layouts:
- POST /v1.2/iseries/generate - Generate any I-series layout (specify layout_type in request)
- POST /v1.2/iseries/I1 - Generate I1 (wide image left)
- POST /v1.2/iseries/I2 - Generate I2 (wide image right)
- POST /v1.2/iseries/I3 - Generate I3 (narrow image left)
- POST /v1.2/iseries/I4 - Generate I4 (narrow image right)
- GET /v1.2/iseries/health - Health check

Each endpoint generates both portrait image and text content in parallel,
following the proven hero slide generator pattern.
"""

import logging
import time
from typing import Callable

from fastapi import APIRouter, HTTPException, Depends

from app.models.iseries_models import (
    ISeriesGenerationRequest,
    ISeriesGenerationResponse,
    ISeriesLayoutType,
    ISERIES_DIMENSIONS
)
from app.core.iseries import (
    I1Generator,
    I2Generator,
    I3Generator,
    I4Generator
)
from app.services.llm_service import create_llm_callable_async

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1.2/iseries", tags=["iseries", "v1.2"])


# =============================================================================
# Dependencies
# =============================================================================

def get_async_llm_service() -> Callable:
    """Get async LLM service for content generation."""
    return create_llm_callable_async()


def get_generator(layout_type: ISeriesLayoutType, llm_service: Callable):
    """
    Get appropriate generator for the layout type.

    Args:
        layout_type: I-series layout type (I1, I2, I3, I4)
        llm_service: Async LLM callable

    Returns:
        Configured generator instance
    """
    generators = {
        ISeriesLayoutType.I1: I1Generator,
        ISeriesLayoutType.I2: I2Generator,
        ISeriesLayoutType.I3: I3Generator,
        ISeriesLayoutType.I4: I4Generator,
    }
    generator_class = generators.get(layout_type)
    if not generator_class:
        raise ValueError(f"Unknown layout type: {layout_type}")
    return generator_class(llm_service)


# =============================================================================
# Main Endpoint - Any I-Series Layout
# =============================================================================

@router.post("/generate", response_model=ISeriesGenerationResponse)
async def generate_iseries(
    request: ISeriesGenerationRequest,
    llm_service: Callable = Depends(get_async_llm_service)
) -> ISeriesGenerationResponse:
    """
    Generate I-series layout with image and text content.

    This endpoint generates:
    1. AI-generated portrait image for the image slot (9:16 aspect ratio)
    2. LLM-generated text content for the content area

    Both are generated in parallel for optimal performance (~12-15 seconds total).

    **Layout Types:**
    - I1: Wide image (660x1080) on LEFT, content on right
    - I2: Wide image (660x1080) on RIGHT, content on left
    - I3: Narrow image (360x1080) on LEFT, content on right
    - I4: Narrow image (360x1080) on RIGHT, content on left

    **Visual Styles:**
    - professional: Photorealistic, corporate imagery
    - illustrated: Ghibli-style, anime illustration
    - kids: Bright, playful, cartoon

    **Content Styles:**
    - bullets: Bullet point list (default)
    - paragraphs: Paragraph format
    - mixed: Combination of both
    """
    start_time = time.time()
    logger.info(
        f"[ISERIES-REQ] type={request.layout_type.value}, "
        f"slide={request.slide_number}, style={request.visual_style.value}"
    )

    try:
        generator = get_generator(request.layout_type, llm_service)
        result = await generator.generate(request)

        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"[ISERIES-OK] type={request.layout_type.value}, "
            f"time={elapsed_ms}ms, fallback={result.image_fallback}"
        )

        return result

    except ValueError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"[ISERIES-400] type={request.layout_type.value}, "
            f"time={elapsed_ms}ms, error={str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"[ISERIES-500] type={request.layout_type.value}, "
            f"time={elapsed_ms}ms, error={str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# =============================================================================
# Individual Layout Endpoints (Convenience)
# =============================================================================

@router.post("/I1", response_model=ISeriesGenerationResponse)
async def generate_i1(
    request: ISeriesGenerationRequest,
    llm_service: Callable = Depends(get_async_llm_service)
) -> ISeriesGenerationResponse:
    """
    Generate I1 layout: Wide image (660x1080) on LEFT, content on right.

    Use Case: Product showcases, team profiles, case studies with prominent imagery.
    Content Area: 1200x840 pixels
    """
    request.layout_type = ISeriesLayoutType.I1
    return await generate_iseries(request, llm_service)


@router.post("/I2", response_model=ISeriesGenerationResponse)
async def generate_i2(
    request: ISeriesGenerationRequest,
    llm_service: Callable = Depends(get_async_llm_service)
) -> ISeriesGenerationResponse:
    """
    Generate I2 layout: Wide image (660x1080) on RIGHT, content on left.

    Use Case: Balanced content with imagery on right, case studies, portfolio pieces.
    Content Area: 1140x840 pixels
    """
    request.layout_type = ISeriesLayoutType.I2
    return await generate_iseries(request, llm_service)


@router.post("/I3", response_model=ISeriesGenerationResponse)
async def generate_i3(
    request: ISeriesGenerationRequest,
    llm_service: Callable = Depends(get_async_llm_service)
) -> ISeriesGenerationResponse:
    """
    Generate I3 layout: Narrow image (360x1080) on LEFT, content on right.

    Use Case: Text-heavy slides with narrow image accent, detailed content.
    Content Area: 1500x840 pixels (LARGEST content area)
    """
    request.layout_type = ISeriesLayoutType.I3
    return await generate_iseries(request, llm_service)


@router.post("/I4", response_model=ISeriesGenerationResponse)
async def generate_i4(
    request: ISeriesGenerationRequest,
    llm_service: Callable = Depends(get_async_llm_service)
) -> ISeriesGenerationResponse:
    """
    Generate I4 layout: Narrow image (360x1080) on RIGHT, content on left.

    Use Case: Text-dominant layouts with narrow accent images, content-focused.
    Content Area: 1440x840 pixels
    """
    request.layout_type = ISeriesLayoutType.I4
    return await generate_iseries(request, llm_service)


# =============================================================================
# Health Check & Info
# =============================================================================

@router.get("/health")
async def iseries_health():
    """
    Health check for I-series endpoints.

    Returns service status and available layouts.
    """
    return {
        "status": "healthy",
        "service": "Text Service v1.2 - I-Series Layouts",
        "layouts": {
            layout_type: info
            for layout_type, info in ISERIES_DIMENSIONS.items()
        },
        "features": [
            "parallel_generation",
            "style_aware_images",
            "graceful_fallback",
            "portrait_aspect_ratio"
        ],
        "visual_styles": ["professional", "illustrated", "kids"],
        "content_styles": ["bullets", "paragraphs", "mixed"]
    }


@router.get("/layouts")
async def list_iseries_layouts():
    """
    List all I-series layouts with their specifications.

    Returns dimension details for each layout type.
    """
    return {
        "layouts": ISERIES_DIMENSIONS,
        "total_layouts": len(ISERIES_DIMENSIONS),
        "image_aspect_ratio": "9:16 (portrait)",
        "slide_size": "1920x1080 (16:9 HD)"
    }
