"""
H2-Section Generator - Section Divider Slide

Wrapper that delegates to existing SectionDividerGenerator (with or without image),
adding structured field extraction for Layout Service compatibility.

Version: 1.2.1
"""

import logging
import time
from typing import Any, Optional, Callable

from .base_slide_generator import BaseSlideGenerator
from .field_extractor import extract_structured_fields
from ...models.slides_models import (
    UnifiedSlideRequest,
    HeroSlideResponse,
    SlideLayoutType
)
from ..hero.section_divider_generator import SectionDividerGenerator
from ..hero.base_hero_generator import HeroGenerationRequest

logger = logging.getLogger(__name__)


class H2SectionGenerator(BaseSlideGenerator):
    """
    H2-section layout generator (section divider slide).

    Wraps existing SectionDividerGenerator and enhances response
    with structured fields for Layout Service integration.

    Features:
    - Section number extraction
    - Section title extraction
    - Optional image background
    """

    def __init__(
        self,
        llm_service: Callable,
        image_service: Optional[Any] = None
    ):
        """
        Initialize H2 generator.

        Args:
            llm_service: Async LLM callable
            image_service: Optional image service for background
        """
        super().__init__(llm_service, image_service)

        # Create wrapped generator
        self._hero_generator = SectionDividerGenerator(llm_service=llm_service)

    @property
    def layout_type(self) -> SlideLayoutType:
        return SlideLayoutType.H2_SECTION

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
        # Build context with section-specific fields
        context = dict(request.context) if request.context else {}

        if request.section_number:
            context["section_number"] = request.section_number
        if request.section_title:
            context["section_title"] = request.section_title

        return HeroGenerationRequest(
            slide_number=request.slide_number,
            slide_type="section_divider",
            narrative=request.narrative or request.section_title or f"Section {request.section_number}",
            topics=request.topics,
            context=context,
            visual_style=request.visual_style.value
        )

    async def generate(self, request: UnifiedSlideRequest) -> HeroSlideResponse:
        """
        Generate section divider slide.

        Args:
            request: UnifiedSlideRequest

        Returns:
            HeroSlideResponse with structured fields
        """
        start_time = time.time()
        logger.info(f"[H2-section] Generating section divider #{request.slide_number}")

        try:
            # Convert request format
            hero_request = self._convert_to_hero_request(request)

            # Call wrapped generator
            hero_response = await self._hero_generator.generate(hero_request)

            # Extract structured fields from HTML
            extracted = extract_structured_fields(hero_response.content, "H2-section")

            # Build enhanced response
            metadata = hero_response.metadata.copy()
            metadata.update({
                "layout_type": "H2-section",
                "generation_time_ms": int((time.time() - start_time) * 1000),
            })

            # H2-section uses individual fields + background_color
            # Per SLIDE_GENERATION_INPUT_SPEC.md: default background_color #374151
            response = HeroSlideResponse(
                content=hero_response.content,  # Full HTML (for backward compat)
                slide_title=extracted.get("slide_title") or request.section_title,
                subtitle=extracted.get("subtitle"),
                section_number=extracted.get("section_number") or request.section_number,
                background_color="#374151",  # Default per SPEC (darker gray)
                image_fallback=False,
                metadata=metadata
            )

            logger.info(f"[H2-section] Generated in {metadata['generation_time_ms']}ms")
            return response

        except Exception as e:
            elapsed = int((time.time() - start_time) * 1000)
            logger.error(f"[H2-section] Failed after {elapsed}ms: {e}")
            raise
