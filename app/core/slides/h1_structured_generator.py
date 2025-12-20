"""
H1-Structured Generator - Title Slide without Image (Gradient Background)

Wrapper that delegates to existing TitleSlideGenerator,
adding structured field extraction for Layout Service compatibility.

Version: 1.2.1
"""

import logging
import time
from typing import Optional, Callable

from .base_slide_generator import BaseSlideGenerator
from .field_extractor import extract_structured_fields
from ...models.slides_models import (
    UnifiedSlideRequest,
    HeroSlideResponse,
    SlideLayoutType
)
from ..hero.title_slide_generator import TitleSlideGenerator
from ..hero.base_hero_generator import HeroGenerationRequest

logger = logging.getLogger(__name__)


class H1StructuredGenerator(BaseSlideGenerator):
    """
    H1-structured layout generator (title slide with gradient background).

    Wraps existing TitleSlideGenerator and enhances response
    with structured fields for Layout Service integration.

    Features:
    - Author name extraction
    - Date/event information
    - No image generation (gradient background)
    """

    def __init__(self, llm_service: Callable, image_service=None):
        """
        Initialize H1-structured generator.

        Args:
            llm_service: Async LLM callable
            image_service: Not used (no image generation)
        """
        super().__init__(llm_service, None)

        # Create wrapped generator
        self._hero_generator = TitleSlideGenerator(llm_service=llm_service)

    @property
    def layout_type(self) -> SlideLayoutType:
        return SlideLayoutType.H1_STRUCTURED

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
        # Build context with author/date fields
        context = dict(request.context) if request.context else {}

        if request.presentation_title:
            context["presentation_title"] = request.presentation_title
        if request.subtitle:
            context["subtitle"] = request.subtitle
        if request.author_name:
            context["author_name"] = request.author_name
        if request.date_info:
            context["date_info"] = request.date_info

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
        Generate title slide with gradient background.

        Args:
            request: UnifiedSlideRequest

        Returns:
            HeroSlideResponse with structured fields
        """
        start_time = time.time()
        logger.info(f"[H1-structured] Generating title slide #{request.slide_number}")

        try:
            # Convert request format
            hero_request = self._convert_to_hero_request(request)

            # Call wrapped generator
            hero_response = await self._hero_generator.generate(hero_request)

            # Extract structured fields from HTML
            extracted = extract_structured_fields(hero_response.content, "H1-structured")

            # Build enhanced response
            metadata = hero_response.metadata.copy()
            metadata.update({
                "layout_type": "H1-structured",
                "generation_time_ms": int((time.time() - start_time) * 1000),
            })

            # H1-structured uses individual fields + background_color
            # Per SLIDE_GENERATION_INPUT_SPEC.md: default background_color #1e3a5f
            response = HeroSlideResponse(
                content=hero_response.content,  # Full HTML (for backward compat)
                slide_title=extracted.get("slide_title"),
                subtitle=extracted.get("subtitle"),
                author_info=extracted.get("author_info") or request.author_name,
                date_info=extracted.get("date_info") or request.date_info,
                background_color="#1e3a5f",  # Default per SPEC
                image_fallback=False,  # No image, gradient background
                metadata=metadata
            )

            logger.info(f"[H1-structured] Generated in {metadata['generation_time_ms']}ms")
            return response

        except Exception as e:
            elapsed = int((time.time() - start_time) * 1000)
            logger.error(f"[H1-structured] Failed after {elapsed}ms: {e}")
            raise
