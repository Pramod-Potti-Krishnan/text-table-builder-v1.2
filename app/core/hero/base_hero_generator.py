"""
Base Hero Slide Generator for v1.2 Text Service

Adapted from v1.1's BaseSpecializedGenerator pattern for hero slides (L29).
This provides the abstract base class that all hero generators inherit from.

Architecture:
- Each hero slide type has its own generator class (Title, Section, Closing)
- All generate COMPLETE HTML structures (not field-by-field)
- Uses async LLM service for FastAPI compatibility
- Validates output for structure and character counts
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
import re
import logging

logger = logging.getLogger(__name__)


class HeroGenerationRequest(BaseModel):
    """
    Request model for hero slide generation.

    Designed to work with Director v3.4's slide data structure.
    """
    slide_number: int = Field(..., description="Slide number in presentation")
    slide_type: str = Field(..., description="Hero slide type: title_slide, section_divider, closing_slide")
    narrative: str = Field(..., description="Narrative or purpose of this slide")
    topics: list[str] = Field(default_factory=list, description="Key topics to cover")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context: theme, audience, presentation_title, contact_info, etc."
    )


class HeroGenerationResponse(BaseModel):
    """
    Response model for hero slide generation.

    Returns complete HTML content ready for deck-builder integration.
    """
    content: str = Field(..., description="Complete HTML structure for the hero slide")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata: slide_type, validation results, character counts, etc."
    )


class BaseHeroGenerator(ABC):
    """
    Abstract base class for hero slide generators (v1.1 pattern).

    All hero generators must implement:
    - slide_type property: Returns identifier ("title_slide", etc.)
    - _build_prompt(): Creates LLM prompt for this slide type
    - _validate_output(): Validates generated HTML structure

    The generate() method orchestrates the workflow:
    1. Build prompt
    2. Call async LLM service
    3. Validate output
    4. Return response
    """

    def __init__(self, llm_service: Callable):
        """
        Initialize hero generator with async LLM service.

        Args:
            llm_service: Async callable that takes prompt string and returns content string.
                        Signature: async def llm_service(prompt: str) -> str
        """
        self.llm_service = llm_service

    @property
    @abstractmethod
    def slide_type(self) -> str:
        """
        Return the slide type identifier for this generator.

        Returns:
            One of: "title_slide", "section_divider", "closing_slide"
        """
        pass

    @abstractmethod
    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build LLM prompt for generating this hero slide type.

        This method must be implemented by each generator to create
        a slide-type-specific prompt that instructs the LLM to generate
        the appropriate HTML structure with proper constraints.

        Args:
            request: Hero generation request with narrative, topics, context

        Returns:
            Complete LLM prompt string
        """
        pass

    def _validate_output(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate generated HTML structure and character counts.

        Base implementation provides common validation logic.
        Subclasses can override to add specific validation rules.

        Args:
            content: Generated HTML content
            request: Original request for context

        Returns:
            Dictionary with validation results:
            - valid (bool): Whether all validations passed
            - violations (list): List of validation errors
            - warnings (list): List of validation warnings
            - metrics (dict): Character counts and other metrics
        """
        violations = []
        warnings = []
        metrics = {}

        # Basic HTML structure validation
        if not content.strip():
            violations.append("Generated content is empty")

        if not ("<div" in content or "<section" in content):
            violations.append("Missing container element (div or section)")

        # Check for common HTML injection patterns
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onclick='
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Potentially dangerous pattern detected: {pattern}")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "metrics": metrics
        }

    def _extract_text_from_html(self, html: str, tag_pattern: str) -> str:
        """
        Extract text content from HTML tag.

        Args:
            html: HTML string
            tag_pattern: Regex pattern to match tag (e.g., r'<h1[^>]*>(.*?)</h1>')

        Returns:
            Extracted text content (empty string if not found)
        """
        match = re.search(tag_pattern, html, re.DOTALL | re.IGNORECASE)
        if match:
            text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            return text
        return ""

    def _count_characters(self, text: str) -> int:
        """
        Count characters in text (excluding HTML tags).

        Args:
            text: Text to count

        Returns:
            Character count
        """
        # Remove any remaining HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        return len(clean_text)

    async def generate(
        self,
        request: HeroGenerationRequest
    ) -> HeroGenerationResponse:
        """
        Main generation workflow for hero slides.

        Orchestrates the complete workflow:
        1. Build slide-type-specific prompt
        2. Call async LLM service to generate HTML
        3. Validate output structure and constraints
        4. Return response with content and metadata

        Args:
            request: Hero generation request

        Returns:
            HeroGenerationResponse with complete HTML and metadata

        Raises:
            ValueError: If validation fails with violations
            Exception: If LLM generation fails
        """
        logger.info(f"Generating {self.slide_type} (slide #{request.slide_number})")

        try:
            # Step 1: Build prompt
            prompt = await self._build_prompt(request)
            logger.debug(f"Built prompt for {self.slide_type} ({len(prompt)} chars)")

            # Step 2: Call async LLM service
            logger.info(f"Calling LLM for {self.slide_type} generation...")
            content = await self.llm_service(prompt)
            logger.info(f"LLM returned {len(content)} chars for {self.slide_type}")

            # Step 3: Validate output
            validation = self._validate_output(content, request)

            if not validation["valid"]:
                logger.error(f"Validation failed for {self.slide_type}: {validation['violations']}")
                raise ValueError(
                    f"Generated content validation failed: {validation['violations']}"
                )

            if validation["warnings"]:
                logger.warning(f"Validation warnings for {self.slide_type}: {validation['warnings']}")

            # Step 4: Return response
            logger.info(f"Successfully generated {self.slide_type}")
            return HeroGenerationResponse(
                content=content,
                metadata={
                    "slide_type": self.slide_type,
                    "slide_number": request.slide_number,
                    "validation": validation,
                    "generation_mode": "hero_slide_async"
                }
            )

        except Exception as e:
            logger.error(f"Hero slide generation failed for {self.slide_type}: {e}")
            raise
