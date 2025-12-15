"""
Hero Slide API Routes for v1.2 Text Service

Provides specialized endpoints for generating L29 hero slides:

Standard (gradient backgrounds):
- POST /v1.2/hero/title - Title/opening slides
- POST /v1.2/hero/section - Section divider slides
- POST /v1.2/hero/closing - Closing/conclusion slides

Image-Enhanced (AI-generated backgrounds):
- POST /v1.2/hero/title-with-image - Title slides with 16:9 background images
- POST /v1.2/hero/section-with-image - Section dividers with background images
- POST /v1.2/hero/closing-with-image - Closing slides with background images

These endpoints complement the existing /v1.2/generate endpoint for content slides,
creating a unified Text Service with 16 total endpoints (6 hero + 10 content variants).

Architecture:
- Each endpoint uses a specialized generator (TitleSlideGenerator, etc.)
- Image-enhanced variants use Image Builder v2.0 API for background generation
- All generators use async LLM service for FastAPI compatibility
- Complete HTML generation (not field-by-field)
- Full validation of output structure and character counts
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Callable

from ..core.hero import (
    BaseHeroGenerator,
    HeroGenerationRequest,
    HeroGenerationResponse,
    TitleSlideGenerator,
    SectionDividerGenerator,
    ClosingSlideGenerator,
    # Image-enhanced variants
    TitleSlideWithImageGenerator,
    SectionDividerWithImageGenerator,
    ClosingSlideWithImageGenerator
)
from ..services import create_llm_callable_async

logger = logging.getLogger(__name__)

# Create router for hero endpoints
router = APIRouter(prefix="/v1.2/hero", tags=["hero", "v1.2"])


# ============================================================================
# Dependencies
# ============================================================================

def get_async_llm_service() -> Callable:
    """
    Get async LLM service for hero slide generation.

    This uses the same async LLM service as content slides for consistency.
    Uses Vertex AI with Application Default Credentials (ADC).

    Returns:
        Async callable that takes prompt string and returns content string
    """
    return create_llm_callable_async()


def get_title_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> TitleSlideGenerator:
    """
    Create TitleSlideGenerator instance.

    Args:
        llm_service: Async LLM callable (injected)

    Returns:
        TitleSlideGenerator instance
    """
    return TitleSlideGenerator(llm_service)


def get_section_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> SectionDividerGenerator:
    """
    Create SectionDividerGenerator instance.

    Args:
        llm_service: Async LLM callable (injected)

    Returns:
        SectionDividerGenerator instance
    """
    return SectionDividerGenerator(llm_service)


def get_closing_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> ClosingSlideGenerator:
    """
    Create ClosingSlideGenerator instance.

    Args:
        llm_service: Async LLM callable (injected)

    Returns:
        ClosingSlideGenerator instance
    """
    return ClosingSlideGenerator(llm_service)


# Image-Enhanced Generator Dependencies
def get_title_with_image_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> TitleSlideWithImageGenerator:
    """
    Create TitleSlideWithImageGenerator instance.

    Args:
        llm_service: Async LLM callable (injected)

    Returns:
        TitleSlideWithImageGenerator instance
    """
    return TitleSlideWithImageGenerator(llm_service)


def get_section_with_image_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> SectionDividerWithImageGenerator:
    """
    Create SectionDividerWithImageGenerator instance.

    Args:
        llm_service: Async LLM callable (injected)

    Returns:
        SectionDividerWithImageGenerator instance
    """
    return SectionDividerWithImageGenerator(llm_service)


def get_closing_with_image_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> ClosingSlideWithImageGenerator:
    """
    Create ClosingSlideWithImageGenerator instance.

    Args:
        llm_service: Async LLM callable (injected)

    Returns:
        ClosingSlideWithImageGenerator instance
    """
    return ClosingSlideWithImageGenerator(llm_service)


# ============================================================================
# Hero Slide Endpoints
# ============================================================================

@router.post("/title", response_model=HeroGenerationResponse)
async def generate_title_slide(
    request: HeroGenerationRequest,
    generator: TitleSlideGenerator = Depends(get_title_generator)
) -> HeroGenerationResponse:
    """
    Generate title/opening slide (L29 hero layout).

    Creates a title slide with:
    - Main presentation title (h1)
    - Compelling subtitle/value proposition (p)
    - Presenter attribution (p)

    **Request Body**:
    - slide_number: Slide number in presentation
    - slide_type: "title_slide"
    - narrative: Narrative or purpose for the slide
    - topics: List of key topics to cover
    - context: Additional context (theme, audience, presentation_title, etc.)

    **Response**:
    - content: Complete HTML structure for title slide
    - metadata: Validation results, character counts, slide info

    **HTML Structure**:
    ```html
    <div class="title-slide">
      <h1 class="main-title">Presentation Title</h1>
      <p class="subtitle">Compelling subtitle</p>
      <p class="attribution">Presenter | Company | Date</p>
    </div>
    ```

    **Character Constraints**:
    - Main title: 40-80 chars (max 100)
    - Subtitle: 80-120 chars (max 150)
    - Attribution: 60-100 chars (max 120)
    """
    import time
    start_time = time.time()

    # REQUEST ARRIVAL LOGGING
    print(f"[HERO-REQ] type=title, slide_num={request.slide_number}")

    try:
        result = await generator.generate(request)

        # SUCCESS LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        html_len = len(result.get('content', '')) if isinstance(result, dict) else len(getattr(result, 'content', ''))
        print(f"[HERO-OK] type=title, slide_num={request.slide_number}, time={elapsed_ms}ms, html={html_len} chars")

        return result

    except ValueError as e:
        # VALIDATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-400] type=title, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=400,
            detail=f"Title slide validation failed: {str(e)}"
        )

    except Exception as e:
        # GENERATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-ERROR] type=title, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=500,
            detail=f"Title slide generation failed: {str(e)}"
        )


@router.post("/section", response_model=HeroGenerationResponse)
async def generate_section_divider(
    request: HeroGenerationRequest,
    generator: SectionDividerGenerator = Depends(get_section_generator)
) -> HeroGenerationResponse:
    """
    Generate section divider/transition slide (L29 hero layout).

    Creates a section divider with:
    - Section title (h2)
    - Section description/preview (p)

    **Request Body**:
    - slide_number: Slide number in presentation
    - slide_type: "section_divider"
    - narrative: Purpose or focus of this section
    - topics: List of key topics for this section
    - context: Additional context (theme, audience, etc.)

    **Response**:
    - content: Complete HTML structure for section divider
    - metadata: Validation results, character counts, slide info

    **HTML Structure**:
    ```html
    <div class="section-divider">
      <h2 class="section-title">Section Name</h2>
      <p class="section-description">Brief description of upcoming content</p>
    </div>
    ```

    **Character Constraints**:
    - Section title: 40-60 chars (max 80)
    - Section description: 80-120 chars (max 150)
    """
    import time
    start_time = time.time()

    # REQUEST ARRIVAL LOGGING
    print(f"[HERO-REQ] type=section, slide_num={request.slide_number}")

    try:
        result = await generator.generate(request)

        # SUCCESS LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        html_len = len(result.get('content', '')) if isinstance(result, dict) else len(getattr(result, 'content', ''))
        print(f"[HERO-OK] type=section, slide_num={request.slide_number}, time={elapsed_ms}ms, html={html_len} chars")

        return result

    except ValueError as e:
        # VALIDATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-400] type=section, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=400,
            detail=f"Section divider validation failed: {str(e)}"
        )

    except Exception as e:
        # GENERATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-ERROR] type=section, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=500,
            detail=f"Section divider generation failed: {str(e)}"
        )


@router.post("/closing", response_model=HeroGenerationResponse)
async def generate_closing_slide(
    request: HeroGenerationRequest,
    generator: ClosingSlideGenerator = Depends(get_closing_generator)
) -> HeroGenerationResponse:
    """
    Generate closing/conclusion slide (L29 hero layout).

    Creates a closing slide with:
    - Closing message/thank you + takeaway (h2)
    - Call-to-action (p)
    - Contact information (p)

    **Request Body**:
    - slide_number: Slide number in presentation
    - slide_type: "closing_slide"
    - narrative: Closing message or key takeaway
    - topics: List of key topics covered in presentation
    - context: Additional context (theme, audience, contact_info, etc.)

    **Response**:
    - content: Complete HTML structure for closing slide
    - metadata: Validation results, character counts, slide info

    **HTML Structure**:
    ```html
    <div class="closing-slide">
      <h2 class="closing-message">Thank You + Key Takeaway</h2>
      <p class="call-to-action">What's next for the audience</p>
      <p class="contact-info">presenter@email.com | website.com</p>
    </div>
    ```

    **Character Constraints**:
    - Closing message: 50-80 chars (max 120)
    - Call-to-action: 80-120 chars (max 150)
    - Contact info: 60-100 chars (max 120)
    """
    import time
    start_time = time.time()

    # REQUEST ARRIVAL LOGGING
    print(f"[HERO-REQ] type=closing, slide_num={request.slide_number}")

    try:
        result = await generator.generate(request)

        # SUCCESS LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        html_len = len(result.get('content', '')) if isinstance(result, dict) else len(getattr(result, 'content', ''))
        print(f"[HERO-OK] type=closing, slide_num={request.slide_number}, time={elapsed_ms}ms, html={html_len} chars")

        return result

    except ValueError as e:
        # VALIDATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-400] type=closing, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=400,
            detail=f"Closing slide validation failed: {str(e)}"
        )

    except Exception as e:
        # GENERATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-ERROR] type=closing, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=500,
            detail=f"Closing slide generation failed: {str(e)}"
        )


# ============================================================================
# Image-Enhanced Hero Slide Endpoints
# ============================================================================

@router.post("/title-with-image", response_model=HeroGenerationResponse)
async def generate_title_slide_with_image(
    request: HeroGenerationRequest,
    generator: TitleSlideWithImageGenerator = Depends(get_title_with_image_generator)
) -> HeroGenerationResponse:
    """
    Generate title/opening slide with AI-generated background image (L29 hero layout).

    Creates a title slide with:
    - AI-generated 16:9 background image (contextual to presentation topic)
    - Main presentation title (h1) - LEFT-aligned
    - Compelling subtitle/value proposition (p) - LEFT-aligned
    - Presenter attribution (p) - LEFT-aligned
    - Dark gradient overlay (dark left → light right) for text readability

    **Visual Style Options** (request.visual_style):
    - `illustrated` (default): Studio Ghibli-style, anime illustration, hand-painted aesthetic
    - `professional`: Photorealistic, modern, clean corporate imagery
    - `kids`: Bright vibrant colors, playful, cartoon illustration, kid-friendly

    **Image Generation**:
    - Automatically generates contextual background based on narrative and topics
    - Uses Image Builder v2.0 API
    - 16:9 aspect ratio with style-aware archetype
    - Crop anchor: LEFT (text placement area)
    - Generation time: ~10-15 seconds (parallel with content)
    - Graceful fallback to gradient if image generation fails

    **Request Body**:
    - slide_number: Slide number in presentation
    - slide_type: "title_slide"
    - narrative: Narrative or purpose for the slide
    - topics: List of key topics (used for image context)
    - visual_style: "illustrated" | "professional" | "kids" (default: "illustrated")
    - context: Additional context (theme, audience, presentation_title, etc.)

    **Example Request**:
    ```json
    {
        "slide_number": 1,
        "slide_type": "title_slide",
        "narrative": "AI transforming healthcare diagnostics",
        "topics": ["Machine Learning", "Diagnostics"],
        "context": {"theme": "professional", "audience": "healthcare professionals"}
    }
    ```

    **Response** (extended with image metadata):
    - content: Complete HTML with embedded background image
    - metadata:
      - background_image: URL to generated 16:9 image (or null if fallback)
      - image_generation_time_ms: Time taken to generate image
      - fallback_to_gradient: Whether image generation failed
      - validation: Standard validation results
      - slide_type, slide_number, etc.

    **Character Constraints** (same as standard):
    - Main title: 40-80 chars (max 100)
    - Subtitle: 80-120 chars (max 150)
    - Attribution: 60-100 chars (max 120)
    """
    import time
    start_time = time.time()

    # REQUEST ARRIVAL LOGGING
    print(f"[HERO-REQ] type=title-with-image, slide_num={request.slide_number}")

    try:
        result = await generator.generate(request)

        # SUCCESS LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        html_len = len(result.get('content', '')) if isinstance(result, dict) else len(getattr(result, 'content', ''))
        fallback = result['metadata'].get('fallback_to_gradient', False) if isinstance(result, dict) else getattr(result, 'metadata', {}).get('fallback_to_gradient', False)
        print(f"[HERO-OK] type=title-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, html={html_len} chars, fallback={fallback}")

        return result

    except ValueError as e:
        # VALIDATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-400] type=title-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=400,
            detail=f"Title slide with image validation failed: {str(e)}"
        )

    except Exception as e:
        # GENERATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-ERROR] type=title-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=500,
            detail=f"Title slide with image generation failed: {str(e)}"
        )


@router.post("/section-with-image", response_model=HeroGenerationResponse)
async def generate_section_divider_with_image(
    request: HeroGenerationRequest,
    generator: SectionDividerWithImageGenerator = Depends(get_section_with_image_generator)
) -> HeroGenerationResponse:
    """
    Generate section divider/transition slide with AI-generated background image (L29 hero layout).

    Creates a section divider with:
    - AI-generated 16:9 background image (contextual to new section)
    - Section title (h2) - RIGHT-aligned
    - Section description/preview (p) - RIGHT-aligned
    - Dark gradient overlay (dark right → light left) for text readability
    - Colored left border accent on text block

    **Visual Style Options** (request.visual_style):
    - `illustrated` (default): Studio Ghibli-style, anime illustration, hand-painted aesthetic
    - `professional`: Photorealistic, modern, clean corporate imagery
    - `kids`: Bright vibrant colors, playful, cartoon illustration, kid-friendly

    **Image Generation**:
    - Automatically generates contextual background based on narrative and topics
    - Uses Image Builder v2.0 API
    - 16:9 aspect ratio with style-aware archetype
    - Crop anchor: RIGHT (text placement area)
    - Generation time: ~10-15 seconds (parallel with content)
    - Graceful fallback to dark solid background if image generation fails

    **Request Body**:
    - slide_number: Slide number in presentation
    - slide_type: "section_divider"
    - narrative: Purpose or focus of this section
    - topics: List of key topics for this section (used for image context)
    - visual_style: "illustrated" | "professional" | "kids" (default: "illustrated")
    - context: Additional context (theme, audience, etc.)

    **Example Request**:
    ```json
    {
        "slide_number": 5,
        "slide_type": "section_divider",
        "narrative": "Implementation roadmap and next steps",
        "topics": ["Deployment", "Timeline"],
        "context": {"theme": "tech"}
    }
    ```

    **Response** (extended with image metadata):
    - content: Complete HTML with embedded background image
    - metadata:
      - background_image: URL to generated 16:9 image (or null if fallback)
      - image_generation_time_ms: Time taken to generate image
      - fallback_to_gradient: Whether image generation failed
      - validation: Standard validation results
      - slide_type, slide_number, etc.

    **Character Constraints** (same as standard):
    - Section title: 40-60 chars (max 80)
    - Section description: 80-120 chars (max 150)
    """
    import time
    start_time = time.time()

    # REQUEST ARRIVAL LOGGING
    print(f"[HERO-REQ] type=section-with-image, slide_num={request.slide_number}")

    try:
        result = await generator.generate(request)

        # SUCCESS LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        html_len = len(result.get('content', '')) if isinstance(result, dict) else len(getattr(result, 'content', ''))
        fallback = result['metadata'].get('fallback_to_gradient', False) if isinstance(result, dict) else getattr(result, 'metadata', {}).get('fallback_to_gradient', False)
        print(f"[HERO-OK] type=section-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, html={html_len} chars, fallback={fallback}")

        return result

    except ValueError as e:
        # VALIDATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-400] type=section-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=400,
            detail=f"Section divider with image validation failed: {str(e)}"
        )

    except Exception as e:
        # GENERATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-ERROR] type=section-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=500,
            detail=f"Section divider with image generation failed: {str(e)}"
        )


@router.post("/closing-with-image", response_model=HeroGenerationResponse)
async def generate_closing_slide_with_image(
    request: HeroGenerationRequest,
    generator: ClosingSlideWithImageGenerator = Depends(get_closing_with_image_generator)
) -> HeroGenerationResponse:
    """
    Generate closing/conclusion slide with AI-generated background image (L29 hero layout).

    Creates a closing slide with:
    - AI-generated 16:9 background image (inspiring, forward-looking)
    - Split layout: LEFT text column + RIGHT image column
    - Closing message/thank you + takeaway (h1)
    - Supporting text / value proposition recap (p)
    - Contact information with icons

    **Visual Style Options** (request.visual_style):
    - `illustrated` (default): Studio Ghibli-style, anime illustration, hand-painted aesthetic
    - `professional`: Photorealistic, modern, clean corporate imagery
    - `kids`: Bright vibrant colors, playful, cartoon illustration, kid-friendly

    **Image Generation**:
    - Automatically generates inspiring background based on narrative and topics
    - Uses Image Builder v2.0 API
    - 16:9 aspect ratio with style-aware archetype
    - Crop anchor: CENTER (balanced composition)
    - Generation time: ~10-15 seconds (parallel with content)
    - Graceful fallback to gradient background if image generation fails

    **Request Body**:
    - slide_number: Slide number in presentation
    - slide_type: "closing_slide"
    - narrative: Closing message or key takeaway
    - topics: List of key topics covered (used for image context)
    - visual_style: "illustrated" | "professional" | "kids" (default: "illustrated")
    - context: Additional context (theme, audience, contact_info, etc.)

    **Example Request**:
    ```json
    {
        "slide_number": 15,
        "slide_type": "closing_slide",
        "narrative": "Ready to transform your healthcare operations",
        "topics": ["AI Diagnostics", "Patient Outcomes"],
        "context": {
            "theme": "professional",
            "contact_info": "jane@company.com | linkedin.com/in/janedoe"
        }
    }
    ```

    **Response** (extended with image metadata):
    - content: Complete HTML with embedded background image
    - metadata:
      - background_image: URL to generated 16:9 image (or null if fallback)
      - image_generation_time_ms: Time taken to generate image
      - fallback_to_gradient: Whether image generation failed
      - validation: Standard validation results
      - slide_type, slide_number, etc.

    **Character Constraints** (same as standard):
    - Closing message: 50-80 chars (max 120)
    - Supporting text: Variable (value proposition)
    - Contact info: 60-100 chars (max 120)
    """
    import time
    start_time = time.time()

    # REQUEST ARRIVAL LOGGING
    print(f"[HERO-REQ] type=closing-with-image, slide_num={request.slide_number}")

    try:
        result = await generator.generate(request)

        # SUCCESS LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        html_len = len(result.get('content', '')) if isinstance(result, dict) else len(getattr(result, 'content', ''))
        fallback = result['metadata'].get('fallback_to_gradient', False) if isinstance(result, dict) else getattr(result, 'metadata', {}).get('fallback_to_gradient', False)
        print(f"[HERO-OK] type=closing-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, html={html_len} chars, fallback={fallback}")

        return result

    except ValueError as e:
        # VALIDATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-400] type=closing-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=400,
            detail=f"Closing slide with image validation failed: {str(e)}"
        )

    except Exception as e:
        # GENERATION ERROR LOGGING
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"[HERO-ERROR] type=closing-with-image, slide_num={request.slide_number}, time={elapsed_ms}ms, error={str(e)[:100]}")
        raise HTTPException(
            status_code=500,
            detail=f"Closing slide with image generation failed: {str(e)}"
        )


# ============================================================================
# Health Check Endpoint (for testing)
# ============================================================================

@router.get("/health")
async def hero_health_check():
    """
    Health check endpoint for hero slide service.

    Returns:
        Status information about hero slide endpoints
    """
    return {
        "status": "healthy",
        "service": "Text Service v1.2 - Hero Slides",
        "endpoints": {
            "standard": {
                "title": "/v1.2/hero/title",
                "section": "/v1.2/hero/section",
                "closing": "/v1.2/hero/closing"
            },
            "image_enhanced": {
                "title": "/v1.2/hero/title-with-image",
                "section": "/v1.2/hero/section-with-image",
                "closing": "/v1.2/hero/closing-with-image"
            }
        },
        "generators": {
            "standard": {
                "title": "TitleSlideGenerator (L29)",
                "section": "SectionDividerGenerator (L29)",
                "closing": "ClosingSlideGenerator (L29)"
            },
            "image_enhanced": {
                "title": "TitleSlideWithImageGenerator (L29 + Image Builder)",
                "section": "SectionDividerWithImageGenerator (L29 + Image Builder)",
                "closing": "ClosingSlideWithImageGenerator (L29 + Image Builder)"
            }
        },
        "integration": {
            "llm": "Async LLM service (Vertex AI with ADC)",
            "images": "Image Builder v2.0 API"
        }
    }
