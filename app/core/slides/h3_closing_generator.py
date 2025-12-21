"""
H3-Closing Generator - Closing Slide with Contact Information

Wrapper that delegates to existing ClosingSlideGenerator,
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
from ..hero.closing_slide_generator import ClosingSlideGenerator
from ..hero.base_hero_generator import HeroGenerationRequest

logger = logging.getLogger(__name__)


class H3ClosingGenerator(BaseSlideGenerator):
    """
    H3-closing layout generator (closing slide with contact info).

    Wraps existing ClosingSlideGenerator and enhances response
    with structured fields for Layout Service integration.

    Features:
    - Contact information extraction (email, phone, website)
    - Closing message extraction (Thank You, Questions?)
    - Optional image background
    """

    def __init__(
        self,
        llm_service: Callable,
        image_service: Optional[Any] = None
    ):
        """
        Initialize H3 generator.

        Args:
            llm_service: Async LLM callable
            image_service: Optional image service for background
        """
        super().__init__(llm_service, image_service)

        # Create wrapped generator
        self._hero_generator = ClosingSlideGenerator(llm_service=llm_service)

    @property
    def layout_type(self) -> SlideLayoutType:
        return SlideLayoutType.H3_CLOSING

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
        # Build context with closing-specific fields
        context = dict(request.context) if request.context else {}

        # Add contact information
        contact_info = []
        if request.contact_email:
            context["contact_email"] = request.contact_email
            contact_info.append(request.contact_email)
        if request.contact_phone:
            context["contact_phone"] = request.contact_phone
            contact_info.append(request.contact_phone)
        if request.website_url:
            context["website_url"] = request.website_url
            contact_info.append(request.website_url)

        if contact_info:
            context["contact_info"] = " | ".join(contact_info)

        if request.closing_message:
            context["closing_message"] = request.closing_message

        # v1.3.0: Pass theme and content context through context dict
        if request.theme_config:
            context["theme_config"] = request.theme_config
        if request.content_context:
            context["content_context"] = request.content_context
        if request.styling_mode:
            context["styling_mode"] = request.styling_mode

        return HeroGenerationRequest(
            slide_number=request.slide_number,
            slide_type="closing_slide",
            narrative=request.narrative or request.closing_message or "Thank you for your attention",
            topics=request.topics,
            context=context,
            visual_style=request.visual_style.value
        )

    async def generate(self, request: UnifiedSlideRequest) -> HeroSlideResponse:
        """
        Generate closing slide with contact information.

        Args:
            request: UnifiedSlideRequest

        Returns:
            HeroSlideResponse with structured fields
        """
        start_time = time.time()
        logger.info(f"[H3-closing] Generating closing slide #{request.slide_number}")

        try:
            # Convert request format
            hero_request = self._convert_to_hero_request(request)

            # Call wrapped generator
            hero_response = await self._hero_generator.generate(hero_request)

            # Extract structured fields from HTML
            extracted = extract_structured_fields(hero_response.content, "H3-closing")

            # Build contact info from request or extraction
            contact_info = extracted.get("contact_info")
            if not contact_info:
                contact_parts = []
                if request.contact_email:
                    contact_parts.append(request.contact_email)
                if request.contact_phone:
                    contact_parts.append(request.contact_phone)
                if request.website_url:
                    contact_parts.append(request.website_url)
                if contact_parts:
                    contact_info = " | ".join(contact_parts)

            # Build enhanced response
            metadata = hero_response.metadata.copy()
            metadata.update({
                "layout_type": "H3-closing",
                "generation_time_ms": int((time.time() - start_time) * 1000),
            })

            # H3-closing uses individual fields + background_color
            # Per SLIDE_GENERATION_INPUT_SPEC.md: default background_color #1e3a5f
            response = HeroSlideResponse(
                content=hero_response.content,  # Full HTML (for backward compat)
                slide_title=extracted.get("slide_title"),
                subtitle=extracted.get("subtitle"),
                contact_info=contact_info,
                closing_message=extracted.get("closing_message") or request.closing_message,
                background_color="#1e3a5f",  # Default per SPEC
                image_fallback=False,
                metadata=metadata
            )

            logger.info(f"[H3-closing] Generated in {metadata['generation_time_ms']}ms")
            return response

        except Exception as e:
            elapsed = int((time.time() - start_time) * 1000)
            logger.error(f"[H3-closing] Failed after {elapsed}ms: {e}")
            raise
