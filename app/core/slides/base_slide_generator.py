"""
Base Slide Generator for Slides Module

Abstract base class for all slide generators in the /v1.2/slides/* router.
Provides common functionality for validation, cleaning, and response building.

Version: 1.2.1
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Union
import re
import logging
import time

from ...models.slides_models import (
    UnifiedSlideRequest,
    HeroSlideResponse,
    ContentSlideResponse,
    ISeriesSlideResponse,
    SlideLayoutType
)
from .field_extractor import extract_structured_fields

logger = logging.getLogger(__name__)


class BaseSlideGenerator(ABC):
    """
    Abstract base class for slide generators.

    All slide generators (H1, H2, H3, C1, I-series) inherit from this class.
    Provides:
    - Common validation logic
    - HTML cleaning utilities
    - Response building helpers
    - Timing and metadata tracking
    """

    def __init__(self, llm_service: Callable, image_service: Optional[Any] = None):
        """
        Initialize slide generator with required services.

        Args:
            llm_service: Async callable for LLM generation
                        Signature: async def llm_service(prompt: str) -> str
            image_service: Optional image service client for image generation
        """
        self.llm_service = llm_service
        self.image_service = image_service

    @property
    @abstractmethod
    def layout_type(self) -> SlideLayoutType:
        """
        Return the layout type this generator handles.

        Returns:
            SlideLayoutType enum value
        """
        pass

    @property
    @abstractmethod
    def response_model(self):
        """
        Return the Pydantic response model class for this generator.

        Returns:
            One of: HeroSlideResponse, ContentSlideResponse, ISeriesSlideResponse
        """
        pass

    @abstractmethod
    async def generate(
        self,
        request: UnifiedSlideRequest
    ) -> Union[HeroSlideResponse, ContentSlideResponse, ISeriesSlideResponse]:
        """
        Generate slide content from request.

        Args:
            request: UnifiedSlideRequest with all parameters

        Returns:
            Response model appropriate for this layout type
        """
        pass

    def _clean_markdown_wrapper(self, content: str) -> str:
        """
        Remove markdown code fence wrappers from LLM output.

        LLMs often wrap HTML/JSON in ```html or ```json blocks.

        Args:
            content: Raw LLM output

        Returns:
            Cleaned content without markdown wrappers
        """
        content = content.strip()

        # Remove ```html, ```json, or ``` prefix
        if content.startswith("```html"):
            content = content[7:]
        elif content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]

        # Remove ``` suffix
        if content.endswith("```"):
            content = content[:-3]

        return content.strip()

    def _validate_html_security(self, html: str) -> Dict[str, Any]:
        """
        Validate HTML for security issues.

        Args:
            html: HTML content to validate

        Returns:
            Dict with 'valid', 'violations', 'warnings'
        """
        violations = []
        warnings = []

        if not html or not html.strip():
            violations.append("Generated content is empty")
            return {"valid": False, "violations": violations, "warnings": warnings}

        # Dangerous patterns
        dangerous_patterns = [
            (r'<script', "Script tags detected"),
            (r'javascript:', "JavaScript protocol detected"),
            (r'on\w+\s*=', "Event handlers detected (onclick, onerror, etc.)"),
            (r'<iframe', "iframe tags detected"),
            (r'<object', "object tags detected"),
            (r'<embed', "embed tags detected"),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                violations.append(message)

        # Warnings (not blocking)
        if len(html) > 50000:
            warnings.append("HTML content exceeds 50KB")

        if not ("<div" in html or "<section" in html or "<ul" in html or "<p" in html):
            warnings.append("HTML may be missing container elements")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings
        }

    def _extract_text_from_html(self, html: str) -> str:
        """
        Extract plain text from HTML content.

        Args:
            html: HTML string

        Returns:
            Plain text with tags removed
        """
        if not html:
            return ""
        clean = re.sub(r'<[^>]+>', ' ', html)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def _count_characters(self, text: str) -> int:
        """
        Count characters in text (excluding HTML tags).

        Args:
            text: Text (may contain HTML)

        Returns:
            Character count
        """
        clean = self._extract_text_from_html(text)
        return len(clean)

    def _build_metadata(
        self,
        request: UnifiedSlideRequest,
        start_time: float,
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build standard metadata dictionary for responses.

        Args:
            request: Original request
            start_time: Generation start time (from time.time())
            extra: Additional metadata fields

        Returns:
            Metadata dictionary
        """
        metadata = {
            "slide_type": self.layout_type.value,
            "slide_number": request.slide_number,
            "generation_time_ms": int((time.time() - start_time) * 1000),
            "visual_style": request.visual_style.value if hasattr(request, 'visual_style') else None,
        }

        if extra:
            metadata.update(extra)

        return metadata

    def _enhance_with_structured_fields(
        self,
        response_dict: Dict[str, Any],
        html_content: str
    ) -> Dict[str, Any]:
        """
        Enhance response dictionary with extracted structured fields.

        Args:
            response_dict: Base response dictionary
            html_content: HTML content to extract fields from

        Returns:
            Enhanced response dictionary with structured fields
        """
        # Extract fields based on layout type
        extracted = extract_structured_fields(html_content, self.layout_type.value)

        # Merge extracted fields (don't override existing values)
        for key, value in extracted.items():
            if key not in response_dict or response_dict[key] is None:
                response_dict[key] = value

        return response_dict

    async def _call_llm_with_logging(self, prompt: str, context: str = "") -> str:
        """
        Call LLM service with timing and logging.

        Args:
            prompt: LLM prompt
            context: Context string for logging

        Returns:
            LLM response content
        """
        start = time.time()
        logger.info(f"[{self.layout_type.value}] Calling LLM ({context})")

        try:
            response = await self.llm_service(prompt)
            elapsed = int((time.time() - start) * 1000)
            logger.info(f"[{self.layout_type.value}] LLM returned {len(response)} chars in {elapsed}ms")
            return response

        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            logger.error(f"[{self.layout_type.value}] LLM failed after {elapsed}ms: {e}")
            raise
