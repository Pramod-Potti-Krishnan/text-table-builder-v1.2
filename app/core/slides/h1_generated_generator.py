"""
H1-Generated Generator - Title Slide with AI Background Image

Wrapper that delegates to existing TitleSlideWithImageGenerator,
adding structured field extraction for Layout Service compatibility.

Version: 1.2.2
"""

import logging
import time
from typing import Callable

from .base_slide_generator import BaseSlideGenerator
from .field_extractor import extract_structured_fields
from ...models.slides_models import (
    UnifiedSlideRequest,
    HeroSlideResponse,
    SlideLayoutType
)
from ..hero.title_slide_with_image_generator import TitleSlideWithImageGenerator
from ..hero.base_hero_generator import HeroGenerationRequest

logger = logging.getLogger(__name__)


class H1GeneratedGenerator(BaseSlideGenerator):
    """
    H1-generated layout generator (title slide with AI background image).

    Wraps existing TitleSlideWithImageGenerator and enhances response
    with structured fields for Layout Service integration.

    Layout Service Alias: L29
    """

    def __init__(self, llm_service: Callable):
        """
        Initialize H1 generator.

        Args:
            llm_service: Async LLM callable
        """
        super().__init__(llm_service)

        # Create wrapped generator (obtains image service internally)
        self._hero_generator = TitleSlideWithImageGenerator(llm_service)

    @property
    def layout_type(self) -> SlideLayoutType:
        return SlideLayoutType.H1_GENERATED

    @property
    def response_model(self):
        return HeroSlideResponse

    def _convert_to_hero_request(self, request: UnifiedSlideRequest) -> HeroGenerationRequest:
        """
        Convert UnifiedSlideRequest to HeroGenerationRequest.

        Args:
            request: Unified slide request

        Returns:
            HeroGenerationRequest for wrapped generator
        """
        # Build context with title-specific fields
        context = dict(request.context) if request.context else {}

        if request.presentation_title:
            context["presentation_title"] = request.presentation_title
        if request.subtitle:
            context["subtitle"] = request.subtitle

        return HeroGenerationRequest(
            slide_number=request.slide_number,
            slide_type="title_slide",
            narrative=request.narrative,
            topics=request.topics,
            context=context,
            visual_style=request.visual_style.value
        )

    async def generate(self, request: UnifiedSlideRequest) -> HeroSlideResponse:
        """
        Generate title slide with AI background image.

        Args:
            request: UnifiedSlideRequest

        Returns:
            HeroSlideResponse with structured fields
        """
        start_time = time.time()
        logger.info(f"[H1-generated] Generating title slide #{request.slide_number}")

        try:
            # Convert request format
            hero_request = self._convert_to_hero_request(request)

            # Call wrapped generator (returns dict, not object)
            hero_response = await self._hero_generator.generate(hero_request)

            # Extract structured fields from HTML
            content_html = hero_response["content"]
            extracted = extract_structured_fields(content_html, "H1-generated")

            # Build enhanced response
            metadata = hero_response["metadata"].copy()
            metadata.update({
                "layout_type": "H1-generated",
                "generation_time_ms": int((time.time() - start_time) * 1000),
                "visual_style": request.visual_style.value,
            })

            # H1-generated uses hero_content (full-slide HTML with embedded background)
            # Per SLIDE_GENERATION_INPUT_SPEC.md: no separate background_color needed
            response = HeroSlideResponse(
                hero_content=content_html,  # Full-slide HTML (1920x1080)
                content=content_html,  # Deprecated, kept for backward compat
                slide_title=extracted.get("slide_title"),
                subtitle=extracted.get("subtitle"),
                background_image=extracted.get("background_image"),
                # background_color NOT set - embedded in hero_content
                image_fallback=extracted.get("image_fallback", False),
                metadata=metadata
            )

            logger.info(f"[H1-generated] Generated in {metadata['generation_time_ms']}ms")
            return response

        except Exception as e:
            elapsed = int((time.time() - start_time) * 1000)
            logger.error(f"[H1-generated] Failed after {elapsed}ms: {e}")
            raise
