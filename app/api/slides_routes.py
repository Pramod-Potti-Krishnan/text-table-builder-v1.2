"""
Unified Slides Router for Text Service v1.2 - Layout Service Aligned

This module provides the /v1.2/slides/* endpoints with Layout Service naming
conventions (H1, H2, H3, C1, I1-I4) and L29/L25 aliases.

Key Features:
- Combined generation for C1-text (saves 2 LLM calls per slide)
- Enhanced responses with structured fields alongside HTML
- I-series integration for image+text layouts
- L29/L25 aliases for backward compatibility

Endpoints:
    POST /v1.2/slides/H1-generated  - Title slide with AI image
    POST /v1.2/slides/H1-structured - Title slide with gradient
    POST /v1.2/slides/H2-section    - Section divider slide
    POST /v1.2/slides/H3-closing    - Closing slide with contact
    POST /v1.2/slides/C1-text       - Content slide (combined gen)
    POST /v1.2/slides/I1-I4         - Image+text layouts
    POST /v1.2/slides/L29           - Alias for H1-generated
    POST /v1.2/slides/L25           - Alias for C1-text
    GET  /v1.2/slides/health        - Health check
    GET  /v1.2/slides/layouts       - List all layouts

Version: 1.2.2
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Dict, Any, Union, Optional
import logging
import os
import time
import json

from ..models.slides_models import (
    UnifiedSlideRequest,
    HeroSlideResponse,
    ContentSlideResponse,
    ISeriesSlideResponse,
    SlideLayoutType,
    resolve_layout_alias,
    get_response_model,
    C1_VARIANT_CATEGORIES,
    ALL_C1_VARIANTS
)
from ..models.iseries_models import (
    ISeriesLayoutType,
    ISeriesGenerationRequest,
    ISeriesGenerationResponse,
    ISERIES_DIMENSIONS
)
from ..core.slides import (
    C1TextGenerator,
    H1GeneratedGenerator,
    H1StructuredGenerator,
    H2SectionGenerator,
    H3ClosingGenerator
)
from ..core.iseries import (
    I1Generator,
    I2Generator,
    I3Generator,
    I4Generator
)
from ..services import create_llm_callable_async, create_llm_callable_pooled
from ..services.image_service_client import ImageServiceClient

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1.2/slides", tags=["slides"])


# ---------------------------------------------------------
# Dependencies
# ---------------------------------------------------------

def get_llm_service():
    """Get async LLM callable (pooled or direct based on config)."""
    use_pool = os.getenv("USE_LLM_POOL", "true").lower() == "true"
    if use_pool:
        return create_llm_callable_pooled()
    return create_llm_callable_async()


def get_image_service():
    """Get image service client."""
    return ImageServiceClient()


def get_h1_generated_generator(
    llm_service=Depends(get_llm_service)
) -> H1GeneratedGenerator:
    """Get H1-generated generator with LLM service."""
    return H1GeneratedGenerator(llm_service)


def get_h1_structured_generator(
    llm_service=Depends(get_llm_service)
) -> H1StructuredGenerator:
    """Get H1-structured generator (no image needed)."""
    return H1StructuredGenerator(llm_service)


def get_h2_section_generator(
    llm_service=Depends(get_llm_service),
    image_service=Depends(get_image_service)
) -> H2SectionGenerator:
    """Get H2-section generator with services."""
    return H2SectionGenerator(llm_service, image_service)


def get_h3_closing_generator(
    llm_service=Depends(get_llm_service),
    image_service=Depends(get_image_service)
) -> H3ClosingGenerator:
    """Get H3-closing generator with services."""
    return H3ClosingGenerator(llm_service, image_service)


def get_c1_text_generator(
    llm_service=Depends(get_llm_service)
) -> C1TextGenerator:
    """Get C1-text generator for combined generation."""
    return C1TextGenerator(llm_service)


def get_iseries_generator(layout_type: ISeriesLayoutType, llm_service):
    """Get I-series generator for specific layout type."""
    generators = {
        ISeriesLayoutType.I1: I1Generator,
        ISeriesLayoutType.I2: I2Generator,
        ISeriesLayoutType.I3: I3Generator,
        ISeriesLayoutType.I4: I4Generator,
    }
    generator_class = generators.get(layout_type)
    if not generator_class:
        raise ValueError(f"Unknown I-series layout type: {layout_type}")
    return generator_class(llm_service)


# ---------------------------------------------------------
# H-Series Endpoints
# ---------------------------------------------------------

@router.post("/H1-generated", response_model=HeroSlideResponse)
async def generate_h1_generated(
    request: UnifiedSlideRequest,
    generator: H1GeneratedGenerator = Depends(get_h1_generated_generator)
) -> HeroSlideResponse:
    """
    Generate title slide with AI-generated background image.

    Layout Service alias: L29

    Returns HeroSlideResponse with:
    - content: Full HTML structure
    - slide_title: Extracted title text
    - subtitle: Extracted subtitle text
    - background_image: Generated image URL
    - image_fallback: Whether using placeholder
    """
    start = time.time()
    print(f"[SLIDES] POST /H1-generated slide={request.slide_number}")

    try:
        response = await generator.generate(request)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] H1-generated completed in {elapsed}ms")
        return response

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] H1-generated failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/H1-structured", response_model=HeroSlideResponse)
async def generate_h1_structured(
    request: UnifiedSlideRequest,
    generator: H1StructuredGenerator = Depends(get_h1_structured_generator)
) -> HeroSlideResponse:
    """
    Generate title slide with gradient background (no image).

    Returns HeroSlideResponse with:
    - content: Full HTML structure
    - slide_title: Extracted title text
    - subtitle: Extracted subtitle text
    - author_info: Author/presenter name
    - date_info: Date or event information
    """
    start = time.time()
    print(f"[SLIDES] POST /H1-structured slide={request.slide_number}")

    try:
        response = await generator.generate(request)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] H1-structured completed in {elapsed}ms")
        return response

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] H1-structured failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/H2-section", response_model=HeroSlideResponse)
async def generate_h2_section(
    request: UnifiedSlideRequest,
    generator: H2SectionGenerator = Depends(get_h2_section_generator)
) -> HeroSlideResponse:
    """
    Generate section divider slide.

    Returns HeroSlideResponse with:
    - content: Full HTML structure
    - slide_title: Section title
    - section_number: Section number (e.g., "01", "02")
    """
    start = time.time()
    print(f"[SLIDES] POST /H2-section slide={request.slide_number}")

    try:
        response = await generator.generate(request)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] H2-section completed in {elapsed}ms")
        return response

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] H2-section failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/H3-closing", response_model=HeroSlideResponse)
async def generate_h3_closing(
    request: UnifiedSlideRequest,
    generator: H3ClosingGenerator = Depends(get_h3_closing_generator)
) -> HeroSlideResponse:
    """
    Generate closing slide with contact information.

    Returns HeroSlideResponse with:
    - content: Full HTML structure
    - slide_title: Closing title
    - contact_info: Formatted contact information
    - closing_message: Closing message (Thank You, Questions?, etc.)
    """
    start = time.time()
    print(f"[SLIDES] POST /H3-closing slide={request.slide_number}")

    try:
        response = await generator.generate(request)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] H3-closing completed in {elapsed}ms")
        return response

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] H3-closing failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# C-Series Endpoints
# ---------------------------------------------------------

@router.post("/C1-text", response_model=ContentSlideResponse)
async def generate_c1_text(
    request: UnifiedSlideRequest,
    generator: C1TextGenerator = Depends(get_c1_text_generator)
) -> ContentSlideResponse:
    """
    Generate content slide with combined title + subtitle + body.

    KEY INNOVATION: Single LLM call generates all three components,
    saving 2 LLM calls per slide (from 3 to 1).

    Supports 34 variants via variant_id parameter.

    Returns ContentSlideResponse with:
    - slide_title: Generated title (40-60 chars)
    - subtitle: Generated subtitle (60-100 chars)
    - body: Generated body HTML
    - rich_content: Alias for body (L25 compatibility)
    - metadata: Includes llm_calls=1, generation_mode=combined
    """
    start = time.time()
    variant_id = request.variant_id or "bullets"
    print(f"[SLIDES] POST /C1-text slide={request.slide_number} variant={variant_id}")

    try:
        response = await generator.generate(request)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] C1-text completed in {elapsed}ms (1 LLM call)")
        return response

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] C1-text failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# I-Series Endpoints
# ---------------------------------------------------------

@router.post("/I1", response_model=ISeriesSlideResponse)
async def generate_i1(
    request: UnifiedSlideRequest,
    llm_service=Depends(get_llm_service)
) -> ISeriesSlideResponse:
    """
    Generate I1 layout: Wide image left (660x1080), content right.
    """
    start = time.time()
    print(f"[SLIDES] POST /I1 slide={request.slide_number}")

    try:
        # Convert to I-series request
        iseries_request = _convert_to_iseries_request(request, ISeriesLayoutType.I1)
        generator = get_iseries_generator(ISeriesLayoutType.I1, llm_service)
        response = await generator.generate(iseries_request)

        # Enhance with Layout Service aliases
        enhanced = _enhance_iseries_response(response)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] I1 completed in {elapsed}ms")
        return enhanced

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] I1 failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/I2", response_model=ISeriesSlideResponse)
async def generate_i2(
    request: UnifiedSlideRequest,
    llm_service=Depends(get_llm_service)
) -> ISeriesSlideResponse:
    """
    Generate I2 layout: Wide image right (660x1080), content left.
    """
    start = time.time()
    print(f"[SLIDES] POST /I2 slide={request.slide_number}")

    try:
        iseries_request = _convert_to_iseries_request(request, ISeriesLayoutType.I2)
        generator = get_iseries_generator(ISeriesLayoutType.I2, llm_service)
        response = await generator.generate(iseries_request)
        enhanced = _enhance_iseries_response(response)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] I2 completed in {elapsed}ms")
        return enhanced

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] I2 failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/I3", response_model=ISeriesSlideResponse)
async def generate_i3(
    request: UnifiedSlideRequest,
    llm_service=Depends(get_llm_service)
) -> ISeriesSlideResponse:
    """
    Generate I3 layout: Narrow image left (360x1080), large content right.
    """
    start = time.time()
    print(f"[SLIDES] POST /I3 slide={request.slide_number}")

    try:
        iseries_request = _convert_to_iseries_request(request, ISeriesLayoutType.I3)
        generator = get_iseries_generator(ISeriesLayoutType.I3, llm_service)
        response = await generator.generate(iseries_request)
        enhanced = _enhance_iseries_response(response)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] I3 completed in {elapsed}ms")
        return enhanced

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] I3 failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/I4", response_model=ISeriesSlideResponse)
async def generate_i4(
    request: UnifiedSlideRequest,
    llm_service=Depends(get_llm_service)
) -> ISeriesSlideResponse:
    """
    Generate I4 layout: Narrow image right (360x1080), large content left.
    """
    start = time.time()
    print(f"[SLIDES] POST /I4 slide={request.slide_number}")

    try:
        iseries_request = _convert_to_iseries_request(request, ISeriesLayoutType.I4)
        generator = get_iseries_generator(ISeriesLayoutType.I4, llm_service)
        response = await generator.generate(iseries_request)
        enhanced = _enhance_iseries_response(response)
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] I4 completed in {elapsed}ms")
        return enhanced

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        print(f"[SLIDES] I4 failed after {elapsed}ms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# Alias Endpoints (L-series)
# ---------------------------------------------------------

@router.post("/L29", response_model=HeroSlideResponse)
async def generate_l29(
    request: UnifiedSlideRequest,
    generator: H1GeneratedGenerator = Depends(get_h1_generated_generator)
) -> HeroSlideResponse:
    """
    L29 layout alias for H1-generated (title with image).
    """
    print(f"[SLIDES] POST /L29 -> H1-generated slide={request.slide_number}")
    return await generate_h1_generated(request, generator)


@router.post("/L25", response_model=ContentSlideResponse)
async def generate_l25(
    request: UnifiedSlideRequest,
    generator: C1TextGenerator = Depends(get_c1_text_generator)
) -> ContentSlideResponse:
    """
    L25 layout alias for C1-text (content slide).
    """
    print(f"[SLIDES] POST /L25 -> C1-text slide={request.slide_number}")
    return await generate_c1_text(request, generator)


# ---------------------------------------------------------
# Info Endpoints
# ---------------------------------------------------------

@router.get("/health")
async def slides_health():
    """Health check for slides router."""
    return {
        "status": "healthy",
        "router": "/v1.2/slides",
        "version": "1.2.2",
        "features": {
            "combined_generation": True,
            "structured_fields": True,
            "layout_aliases": ["L29", "L25"]
        },
        "layouts": {
            "h_series": ["H1-generated", "H1-structured", "H2-section", "H3-closing"],
            "c_series": ["C1-text"],
            "i_series": ["I1", "I2", "I3", "I4"],
            "aliases": {"L29": "H1-generated", "L25": "C1-text"}
        }
    }


@router.get("/layouts")
async def list_layouts():
    """List all available slide layouts with details."""
    return {
        "h_series": {
            "H1-generated": {
                "description": "Title slide with AI-generated background image",
                "alias": "L29",
                "features": ["background_image", "slide_title", "subtitle"]
            },
            "H1-structured": {
                "description": "Title slide with gradient background",
                "features": ["slide_title", "subtitle", "author_info", "date_info"]
            },
            "H2-section": {
                "description": "Section divider slide",
                "features": ["section_number", "section_title"]
            },
            "H3-closing": {
                "description": "Closing slide with contact information",
                "features": ["closing_message", "contact_info"]
            }
        },
        "c_series": {
            "C1-text": {
                "description": "Content slide with combined generation",
                "alias": "L25",
                "features": ["slide_title", "subtitle", "body", "rich_content"],
                "innovation": "Single LLM call for title+subtitle+body (saves 2 calls)",
                "variants": len(ALL_C1_VARIANTS),
                "variant_categories": list(C1_VARIANT_CATEGORIES.keys())
            }
        },
        "i_series": {
            "I1": ISERIES_DIMENSIONS["I1"],
            "I2": ISERIES_DIMENSIONS["I2"],
            "I3": ISERIES_DIMENSIONS["I3"],
            "I4": ISERIES_DIMENSIONS["I4"]
        },
        "aliases": {
            "L29": "H1-generated",
            "L25": "C1-text"
        },
        "total_endpoints": 12,
        "total_variants": len(ALL_C1_VARIANTS) + 12  # C1 variants + 4 hero + 4 I-series + 2 aliases
    }


@router.get("/variants")
async def list_c1_variants():
    """List all C1-text variants organized by category."""
    from ..core.slides.c1_text_generator import C1TextGenerator

    return {
        "total": len(ALL_C1_VARIANTS),
        "categories": C1_VARIANT_CATEGORIES,
        "variants": C1TextGenerator.get_supported_variants()
    }


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def _get_iseries_variant_spec(
    layout_type: ISeriesLayoutType,
    topics: list,
    variant_id: Optional[str] = None
) -> Optional[dict]:
    """Auto-select variant spec based on layout type and topics count.

    Maps:
    - I1/I2 (wide image) → _i1 suffix (20% character reduction)
    - I3/I4 (narrow image) → _i3 suffix (15% character reduction)

    Default to single_column layout based on topics count.
    """
    import os

    topic_count = len(topics) if topics else 3

    # Determine base layout type from variant_id or default to single_column
    if variant_id:
        # Parse variant_id to extract base type
        if "comparison" in variant_id:
            if "2col" in variant_id or topic_count <= 2:
                variant_base = "comparison_2col"
            else:
                variant_base = "comparison_3col"
        elif "sequential" in variant_id:
            if topic_count <= 3:
                variant_base = "sequential_3col"
            else:
                # Cap at 4 columns for I-series (no space for 5 with image)
                variant_base = "sequential_4col"
        else:
            # Default to single_column
            if topic_count <= 3:
                variant_base = "single_column_3section"
            elif topic_count == 4:
                variant_base = "single_column_4section"
            else:
                variant_base = "single_column_5section"
    else:
        # Default mapping based on topic count
        if topic_count <= 3:
            variant_base = "single_column_3section"
        elif topic_count == 4:
            variant_base = "single_column_4section"
        else:
            variant_base = "single_column_5section"

    # Map layout type to suffix
    suffix = "_i1" if layout_type in [ISeriesLayoutType.I1, ISeriesLayoutType.I2] else "_i3"

    variant_id_full = f"{variant_base}{suffix}"

    # Get base path - resolve relative to this file's location
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec_path = os.path.join(base_dir, "variant_specs", "iseries", f"{variant_id_full}.json")

    # Load and return variant spec
    try:
        with open(spec_path) as f:
            spec = json.load(f)
            logger.info(f"[I-SERIES] Loaded variant spec: {variant_id_full}")
            return spec
    except FileNotFoundError:
        logger.warning(f"[I-SERIES] Variant spec not found: {spec_path}")
        return None
    except Exception as e:
        logger.warning(f"[I-SERIES] Failed to load variant spec {spec_path}: {e}")
        return None


def _convert_to_iseries_request(
    request: UnifiedSlideRequest,
    layout_type: ISeriesLayoutType
) -> ISeriesGenerationRequest:
    """Convert UnifiedSlideRequest to ISeriesGenerationRequest.

    v1.3.0: Merges theme_config, content_context, and styling_mode into context dict.
    v1.3.1: Auto-selects variant_spec based on layout type and topics count.
    """
    # Build context with v1.3.0 params
    context = dict(request.context) if request.context else {}

    # v1.3.0: Pass theme and content context through context dict
    if request.theme_config:
        context["theme_config"] = request.theme_config
    if request.content_context:
        context["content_context"] = request.content_context
    if request.styling_mode:
        context["styling_mode"] = request.styling_mode

    # v1.3.1: Auto-select variant spec based on layout type and topics
    variant_spec = _get_iseries_variant_spec(
        layout_type,
        request.topics,
        request.variant_id
    )
    if variant_spec:
        context["variant_spec"] = variant_spec
        logger.info(f"[I-SERIES] Using variant_spec: {variant_spec.get('variant_id')}")

    return ISeriesGenerationRequest(
        slide_number=request.slide_number,
        layout_type=layout_type,
        title=request.slide_title or request.presentation_title or "Content",
        narrative=request.narrative,
        topics=request.topics,
        subtitle=request.subtitle,
        visual_style=request.visual_style.value,
        content_style=request.content_style.value if hasattr(request, 'content_style') else "bullets",
        max_bullets=request.max_bullets,
        image_prompt_hint=request.image_prompt_hint,
        context=context
    )


def _enhance_iseries_response(response: ISeriesGenerationResponse) -> ISeriesSlideResponse:
    """Enhance I-series response with Layout Service aliases."""
    import re

    # Extract plain text title from title_html
    slide_title = ""
    if response.title_html:
        title_match = re.search(r'>([^<]+)<', response.title_html)
        if title_match:
            slide_title = title_match.group(1).strip()

    # Extract subtitle if present
    subtitle = None
    if response.subtitle_html:
        subtitle_match = re.search(r'>([^<]+)<', response.subtitle_html)
        if subtitle_match:
            subtitle = subtitle_match.group(1).strip()

    return ISeriesSlideResponse(
        image_html=response.image_html,
        title_html=response.title_html,
        subtitle_html=response.subtitle_html,
        content_html=response.content_html,
        image_url=response.image_url,
        image_fallback=response.image_fallback,
        slide_title=slide_title,
        subtitle=subtitle,
        body=response.content_html,  # Alias for content_html
        metadata=response.metadata
    )
