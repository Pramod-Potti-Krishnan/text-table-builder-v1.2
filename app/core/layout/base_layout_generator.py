"""
Base Layout Generator for Layout Service Integration

Abstract base class for all Layout Service generators (text and table).
Follows the proven pattern from BaseHeroGenerator.

Architecture:
- Each content type has its own generator class
- All generate complete HTML structures with inline CSS
- Uses async LLM service for FastAPI compatibility
- Validates output and provides metadata
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, TypeVar, Generic, Optional
import re
import logging
import uuid
import json

logger = logging.getLogger(__name__)

# Generic types for request and response
RequestT = TypeVar('RequestT')
ResponseT = TypeVar('ResponseT')


class BaseLayoutGenerator(ABC, Generic[RequestT, ResponseT]):
    """
    Abstract base class for Layout Service generators.

    All layout generators must implement:
    - generator_type property: Returns identifier ("text_generate", etc.)
    - _build_prompt(): Creates LLM prompt for this operation
    - _build_response(): Constructs the response from LLM output

    The generate() method orchestrates the workflow:
    1. Build prompt with constraints
    2. Call async LLM service
    3. Clean and validate output
    4. Build response with metadata
    """

    def __init__(self, llm_service: Callable):
        """
        Initialize layout generator with async LLM service.

        Args:
            llm_service: Async callable that takes prompt string and returns content string.
                        Signature: async def llm_service(prompt: str) -> str
        """
        self.llm_service = llm_service

    @property
    @abstractmethod
    def generator_type(self) -> str:
        """
        Return the generator type identifier.

        Returns:
            One of: "text_generate", "text_transform", "text_autofit",
                   "table_generate", "table_transform", "table_analyze"
        """
        pass

    @abstractmethod
    async def _build_prompt(self, request: RequestT) -> str:
        """
        Build LLM prompt for this operation.

        This method must be implemented by each generator to create
        an operation-specific prompt with appropriate constraints.

        Args:
            request: The request object with all parameters

        Returns:
            Complete LLM prompt string
        """
        pass

    @abstractmethod
    async def _build_response(
        self,
        content: str,
        request: RequestT,
        generation_id: str
    ) -> ResponseT:
        """
        Build response object from generated content.

        Args:
            content: Clean HTML content from LLM
            request: Original request for context
            generation_id: UUID for this generation

        Returns:
            Typed response object
        """
        pass

    def _clean_html(self, content: str) -> str:
        """
        Remove markdown code fence wrappers if present.

        LLMs often wrap HTML in ```html...``` blocks. This removes them.
        Also strips excessive whitespace.

        Args:
            content: Raw content from LLM (may have markdown wrappers)

        Returns:
            Clean HTML content without markdown wrappers
        """
        # Strip leading/trailing whitespace
        content = content.strip()

        # Remove ```html prefix
        if content.startswith("```html"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]

        # Remove ``` suffix
        if content.endswith("```"):
            content = content[:-3]

        # Strip again after removing markers
        content = content.strip()

        # Normalize excessive whitespace (but preserve HTML structure)
        # Replace multiple spaces with single space (except in style attributes)
        content = re.sub(r'(?<!["\'])\s{2,}(?!["\'])', ' ', content)

        return content

    def _validate_html(self, content: str) -> Dict[str, Any]:
        """
        Validate generated HTML for basic structure and safety.

        Args:
            content: Generated HTML content

        Returns:
            Dictionary with validation results:
            - valid (bool): Whether all validations passed
            - violations (list): Critical errors
            - warnings (list): Non-critical issues
        """
        violations = []
        warnings = []

        # Check for empty content
        if not content or not content.strip():
            violations.append("Generated content is empty")
            return {"valid": False, "violations": violations, "warnings": warnings}

        # Check for basic HTML structure
        has_tag = bool(re.search(r'<[a-z]', content, re.IGNORECASE))
        if not has_tag:
            warnings.append("Content does not appear to be HTML")

        # Check for dangerous patterns (XSS prevention)
        dangerous_patterns = [
            (r'<script', "Script tags are not allowed"),
            (r'javascript:', "JavaScript URLs are not allowed"),
            (r'onerror\s*=', "Event handlers are not allowed"),
            (r'onclick\s*=', "Click handlers are not allowed"),
            (r'onload\s*=', "Load handlers are not allowed"),
            (r'onmouseover\s*=', "Mouse event handlers are not allowed"),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(message)

        # Check for unclosed tags (basic check)
        open_tags = re.findall(r'<([a-z][a-z0-9]*)\b[^>]*(?<!/)>', content, re.IGNORECASE)
        close_tags = re.findall(r'</([a-z][a-z0-9]*)>', content, re.IGNORECASE)

        # Self-closing tags that don't need closing
        self_closing = {'br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
        open_tags = [t.lower() for t in open_tags if t.lower() not in self_closing]
        close_tags = [t.lower() for t in close_tags]

        if len(open_tags) != len(close_tags):
            warnings.append(f"Potential unclosed tags: {len(open_tags)} open, {len(close_tags)} close")

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
            Plain text with HTML tags removed
        """
        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _count_characters(self, html: str) -> int:
        """
        Count characters in content (excluding HTML tags).

        Args:
            html: HTML content

        Returns:
            Character count of text content
        """
        text = self._extract_text_from_html(html)
        return len(text)

    def _count_words(self, html: str) -> int:
        """
        Count words in content (excluding HTML tags).

        Args:
            html: HTML content

        Returns:
            Word count of text content
        """
        text = self._extract_text_from_html(html)
        words = text.split()
        return len(words)

    def _estimate_read_time(self, word_count: int) -> float:
        """
        Estimate reading time in seconds.

        Uses average reading speed of 200 words per minute.

        Args:
            word_count: Number of words

        Returns:
            Estimated reading time in seconds
        """
        return (word_count / 200) * 60

    def _generate_id(self) -> str:
        """
        Generate a unique ID for this generation.

        Returns:
            UUID string
        """
        return str(uuid.uuid4())

    def _build_context_section(self, context: Any) -> str:
        """
        Build context section for LLM prompt.

        Args:
            context: SlideContext object

        Returns:
            Formatted context string for prompt
        """
        sections = []

        if hasattr(context, 'presentationTitle'):
            sections.append(f"Presentation: {context.presentationTitle}")

        if hasattr(context, 'slideTitle') and context.slideTitle:
            sections.append(f"Slide Title: {context.slideTitle}")

        if hasattr(context, 'slideIndex') and hasattr(context, 'slideCount'):
            sections.append(f"Position: Slide {context.slideIndex + 1} of {context.slideCount}")

        if hasattr(context, 'slideContext') and context.slideContext:
            sections.append(f"Slide Context: {context.slideContext}")

        if hasattr(context, 'previousSlideContent') and context.previousSlideContent:
            sections.append(f"Previous Slide: {context.previousSlideContent}")

        if hasattr(context, 'nextSlideContent') and context.nextSlideContent:
            sections.append(f"Next Slide: {context.nextSlideContent}")

        return "\n".join(sections)

    def _parse_json_from_response(self, response: str) -> Optional[Any]:
        """
        Try to parse JSON from LLM response.

        Handles responses wrapped in markdown code blocks.

        Args:
            response: Raw LLM response

        Returns:
            Parsed JSON or None if parsing fails
        """
        # Try direct parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to extract from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON
        json_match = re.search(r'(\{.*\}|\[.*\])', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return None

    async def generate(self, request: RequestT) -> ResponseT:
        """
        Main generation workflow.

        Orchestrates the complete workflow:
        1. Build operation-specific prompt
        2. Call async LLM service
        3. Clean HTML output
        4. Validate structure
        5. Build typed response

        Args:
            request: Typed request object

        Returns:
            Typed response object

        Raises:
            ValueError: If validation fails critically
            Exception: If LLM generation fails
        """
        generation_id = self._generate_id()
        logger.info(f"Starting {self.generator_type} generation (id: {generation_id})")

        try:
            # Step 1: Build prompt
            prompt = await self._build_prompt(request)
            logger.debug(f"Built prompt for {self.generator_type} ({len(prompt)} chars)")

            # Step 2: Call async LLM service
            logger.info(f"Calling LLM for {self.generator_type}...")
            raw_content = await self.llm_service(prompt)
            logger.info(f"LLM returned {len(raw_content)} chars")

            # Step 3: Clean HTML
            content = self._clean_html(raw_content)
            if len(content) != len(raw_content):
                logger.debug(f"Cleaned content: {len(raw_content)} -> {len(content)} chars")

            # Step 4: Validate
            validation = self._validate_html(content)
            if not validation["valid"]:
                logger.error(f"Validation failed: {validation['violations']}")
                raise ValueError(f"Generated content validation failed: {validation['violations']}")

            if validation["warnings"]:
                logger.warning(f"Validation warnings: {validation['warnings']}")

            # Step 5: Build response
            response = await self._build_response(content, request, generation_id)
            logger.info(f"Successfully completed {self.generator_type} (id: {generation_id})")

            return response

        except Exception as e:
            logger.error(f"{self.generator_type} failed (id: {generation_id}): {e}")
            raise
