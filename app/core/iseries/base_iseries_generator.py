"""
Base I-Series Generator for Text Service v1.2

Abstract base class for I-series layout generators.
Implements the parallel image + content generation pattern
used by hero generators, adapted for portrait aspect ratio images.

Pattern follows:
- Parallel execution of image and content generation
- Graceful fallback if image fails
- Style-aware image prompts (professional, illustrated, kids)
- Content validation and HTML builders

Version: 1.3.0 - Added content_context support for audience-adapted text
"""

import asyncio
import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional

from app.services.image_service_client import get_image_service_client, ImageServiceClient
from app.models.iseries_models import (
    ISeriesGenerationRequest,
    ISeriesGenerationResponse,
    ISeriesVisualStyle,
    ISeriesContentStyle,
    get_layout_dimensions
)
from app.core.hero.style_config import (
    get_style_config,
    get_domain_theme
)

logger = logging.getLogger(__name__)


class BaseISeriesGenerator(ABC):
    """
    Abstract base class for I-series layout generators.

    Implements the parallel image + content generation pattern:
    1. Build image prompt based on narrative and visual style
    2. Build content prompt for text generation
    3. Execute both in parallel
    4. Handle image failure gracefully
    5. Assemble final response with HTML for each slot
    """

    def __init__(self, llm_service: Callable):
        """
        Initialize generator with LLM service.

        Args:
            llm_service: Async callable for LLM text generation
        """
        self.llm_service = llm_service
        self.image_client: ImageServiceClient = get_image_service_client()

    @property
    @abstractmethod
    def layout_type(self) -> str:
        """Return layout type: I1, I2, I3, I4"""
        pass

    @property
    @abstractmethod
    def image_position(self) -> str:
        """Return image position: left or right"""
        pass

    @property
    @abstractmethod
    def image_dimensions(self) -> Dict[str, int]:
        """Return image dimensions: {width: int, height: int}"""
        pass

    @property
    @abstractmethod
    def content_dimensions(self) -> Dict[str, int]:
        """Return content area dimensions: {width: int, height: int}"""
        pass

    async def generate(
        self,
        request: ISeriesGenerationRequest
    ) -> ISeriesGenerationResponse:
        """
        Main generation workflow - parallel image + content.

        Args:
            request: I-series generation request

        Returns:
            ISeriesGenerationResponse with HTML for each slot
        """
        import time
        start_time = time.time()

        logger.info(
            f"Generating {self.layout_type} layout "
            f"(slide #{request.slide_number}, style={request.visual_style.value})"
        )

        # Build prompts
        image_prompt, archetype = self._build_image_prompt(request)
        content_prompt = self._build_content_prompt(request)

        # Parallel generation
        image_task = asyncio.create_task(
            self._generate_image(image_prompt, archetype, request)
        )
        content_task = asyncio.create_task(
            self._generate_content(content_prompt, request)
        )

        results = await asyncio.gather(
            image_task,
            content_task,
            return_exceptions=True
        )

        image_result = results[0]
        content_result = results[1]

        # Handle content result (fatal if fails)
        if isinstance(content_result, Exception):
            logger.error(f"Content generation failed: {content_result}")
            raise content_result

        # Handle image result (non-fatal if fails)
        image_url = None
        image_fallback = False
        image_metadata = {}

        if isinstance(image_result, Exception):
            logger.warning(
                f"Image generation failed, using fallback: {image_result}"
            )
            image_fallback = True
        elif image_result and image_result.get("success"):
            image_url = (
                image_result["urls"].get("cropped") or
                image_result["urls"]["original"]
            )
            image_metadata = image_result.get("metadata", {})
            logger.info(
                f"Image generated in {image_metadata.get('generation_time_ms', 0)}ms"
            )
        else:
            logger.warning("Image generation returned unsuccessful, using fallback")
            image_fallback = True

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = self._build_response(
            image_url=image_url,
            image_fallback=image_fallback,
            content_result=content_result,
            request=request,
            generation_time_ms=generation_time_ms
        )

        logger.info(
            f"{self.layout_type} layout generated in {generation_time_ms}ms "
            f"(image_fallback={image_fallback})"
        )

        return response

    def _build_image_prompt(
        self,
        request: ISeriesGenerationRequest
    ) -> tuple[str, str]:
        """
        Build style-aware image generation prompt.

        Args:
            request: Generation request with narrative and visual_style

        Returns:
            Tuple of (image_prompt, archetype)
        """
        narrative = request.narrative
        topics = request.topics
        visual_style = request.visual_style.value

        # Get style configuration
        style_config = get_style_config(visual_style)

        # Determine domain from narrative and topics
        combined_text = f"{narrative} {' '.join(topics) if topics else ''}".lower()
        domain_imagery = get_domain_theme(style_config, combined_text)

        # Build topic focus
        topic_focus = ', '.join(topics[:2]) if topics else 'professional setting'

        # Use image_prompt_hint if provided
        if request.image_prompt_hint:
            topic_focus = request.image_prompt_hint

        prompt = f"""High-quality {visual_style} portrait image for presentation slide.

Style: {style_config.prompt_style}
Orientation: Tall portrait (9:16 aspect ratio)
Subject: {domain_imagery}
Focus: {topic_focus}
Composition: Subject centered, vertical composition, clean background

CRITICAL: Absolutely NO text, words, letters, numbers, or typography of any kind in the image."""

        return prompt, style_config.archetype

    def _build_content_prompt(
        self,
        request: ISeriesGenerationRequest
    ) -> str:
        """
        Build LLM prompt for text content generation.

        v1.3.0: Extracts content_context from request.context for
        audience-adapted language and vocabulary.

        Args:
            request: Generation request with narrative and content config

        Returns:
            LLM prompt string
        """
        content_style = request.content_style.value
        max_bullets = request.max_bullets
        content_dims = self.content_dimensions

        # v1.3.0: Extract content_context from request context
        context = request.context if hasattr(request, 'context') and request.context else {}
        content_context = context.get("content_context")
        theme_config = context.get("theme_config")

        # v1.3.0: Build audience section
        audience_section = ""
        if content_context:
            audience_info = content_context.get("audience", {})
            purpose_info = content_context.get("purpose", {})
            audience_type = audience_info.get("audience_type", "professional")
            complexity = audience_info.get("complexity_level", "moderate")
            avoid_jargon = audience_info.get("avoid_jargon", False)
            purpose_type = purpose_info.get("purpose_type", "inform")
            include_data = purpose_info.get("include_data", True)

            # Adjust max_bullets based on audience
            if audience_type in ["kids_tween", "kids_teen"]:
                max_bullets = min(max_bullets, 3)
            elif complexity == "low":
                max_bullets = min(max_bullets, 4)

            audience_section = f"""
## 📊 AUDIENCE & PURPOSE
- **Audience**: {audience_type} ({complexity} complexity)
- **Purpose**: {purpose_type}
- **Language**: {"Simple, clear language without jargon" if avoid_jargon else f"Professional language appropriate for {audience_type}"}
- **Data/Stats**: {"Include relevant numbers and data" if include_data else "Focus on concepts, minimize data"}
- **Tone**: {"Educational and encouraging" if audience_type.startswith("kids") else "Professional and authoritative" if purpose_type == "inform" else "Compelling and persuasive" if purpose_type == "persuade" else "Clear and instructive"}
"""

        # v1.3.0: Extract colors from theme_config with defaults
        if theme_config and "colors" in theme_config:
            colors = theme_config["colors"]
            text_color = colors.get("text_primary", "#374151")
        else:
            text_color = "#374151"

        # Determine format instructions based on content style
        if content_style == "bullets":
            format_instructions = f"""Format as a bullet list:
- Maximum {max_bullets} bullet points
- Each bullet: 60-100 characters
- Start with action verbs where appropriate
- Clear, professional language"""
        elif content_style == "paragraphs":
            format_instructions = """Format as paragraphs:
- 2-3 short paragraphs
- Each paragraph: 2-3 sentences
- Clear, professional language
- Logical flow between paragraphs"""
        else:  # mixed
            format_instructions = f"""Format as mixed content:
- Opening paragraph (1-2 sentences)
- {max_bullets - 1} bullet points
- Optional closing statement"""

        prompt = f"""Generate content for a presentation slide.

## Slide Information
Title: {request.title}
{f"Subtitle: {request.subtitle}" if request.subtitle else ""}
{audience_section}
## Narrative/Topic
{request.narrative}

## Key Topics to Cover
{', '.join(request.topics) if request.topics else 'General overview based on narrative'}

## Content Constraints
Content area size: {content_dims['width']}x{content_dims['height']} pixels
{format_instructions}

## Output Format
Return ONLY the HTML content (no code blocks, no explanations):
- For bullets: <ul class="content-list"><li>...</li></ul>
- For paragraphs: <div class="content-body"><p>...</p></div>
- For mixed: combine both formats

## Required Inline Styling
Include these inline CSS styles:
- Font family: 'Inter', -apple-system, sans-serif
- Font size: 1.5rem for body text
- Line height: 1.7
- Color: {text_color}
- Bullet/list spacing: margin-bottom: 0.75rem per item
- List style: disc for bullets

Generate the content HTML now:"""

        return prompt

    async def _generate_image(
        self,
        prompt: str,
        archetype: str,
        request: ISeriesGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate portrait image via Image Service.

        Args:
            prompt: Image generation prompt
            archetype: Image style archetype
            request: Original request for metadata

        Returns:
            Image API response dict
        """
        metadata = {
            "slide_number": request.slide_number,
            "layout_type": self.layout_type,
            "narrative": request.narrative[:100],
            "visual_style": request.visual_style.value
        }

        return await self.image_client.generate_iseries_image(
            prompt=prompt,
            layout_type=self.layout_type,
            visual_style=request.visual_style.value,
            metadata=metadata,
            archetype=archetype
        )

    async def _generate_content(
        self,
        prompt: str,
        request: ISeriesGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate text content via LLM.

        Args:
            prompt: LLM prompt
            request: Original request for validation

        Returns:
            Dict with content and validation results
        """
        # Generate with LLM
        raw_content = await self.llm_service(prompt)

        # Clean markdown wrappers
        content = self._clean_markdown_wrapper(raw_content)

        # Validate
        validation = self._validate_content(content, request)

        return {
            "content": content,
            "validation": validation
        }

    def _clean_markdown_wrapper(self, content: str) -> str:
        """
        Remove markdown code fences that LLMs often add.

        Args:
            content: Raw LLM output

        Returns:
            Cleaned HTML content
        """
        # Remove ```html ... ``` wrappers
        content = re.sub(r'^```html?\s*\n?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\n?```\s*$', '', content)

        # Remove leading/trailing whitespace
        content = content.strip()

        return content

    def _validate_content(
        self,
        content: str,
        request: ISeriesGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate generated content for security and structure.

        Args:
            content: Generated HTML content
            request: Original request for context

        Returns:
            Validation result dictionary
        """
        violations = []
        warnings = []

        # Security checks
        dangerous_patterns = [
            (r'<script', 'script tags not allowed'),
            (r'javascript:', 'javascript: protocol not allowed'),
            (r'onerror\s*=', 'onerror handlers not allowed'),
            (r'onclick\s*=', 'onclick handlers not allowed'),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(message)

        # Structure checks
        if not content.strip():
            violations.append("Content is empty")

        # Check for expected elements
        has_list = bool(re.search(r'<ul|<ol', content, re.IGNORECASE))
        has_paragraph = bool(re.search(r'<p|<div', content, re.IGNORECASE))

        if request.content_style == ISeriesContentStyle.BULLETS and not has_list:
            warnings.append("Bullets requested but no list found")
        if request.content_style == ISeriesContentStyle.PARAGRAPHS and not has_paragraph:
            warnings.append("Paragraphs requested but no paragraph found")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "has_list": has_list,
            "has_paragraph": has_paragraph
        }

    def _build_response(
        self,
        image_url: Optional[str],
        image_fallback: bool,
        content_result: Dict[str, Any],
        request: ISeriesGenerationRequest,
        generation_time_ms: int
    ) -> ISeriesGenerationResponse:
        """
        Build final response with all slot HTML.

        Args:
            image_url: Generated image URL or None
            image_fallback: Whether using fallback
            content_result: Content generation result
            request: Original request
            generation_time_ms: Total generation time

        Returns:
            ISeriesGenerationResponse
        """
        # Build image HTML
        image_html = self._build_image_html(image_url, request)

        # Build title HTML
        title_html = self._build_title_html(request.title)

        # Build subtitle HTML (if provided)
        subtitle_html = None
        if request.subtitle:
            subtitle_html = self._build_subtitle_html(request.subtitle)

        # Get content HTML
        content_html = content_result["content"]

        # Build metadata
        metadata = {
            "layout_type": self.layout_type,
            "slide_number": request.slide_number,
            "image_position": self.image_position,
            "image_dimensions": self.image_dimensions,
            "content_dimensions": self.content_dimensions,
            "visual_style": request.visual_style.value,
            "content_style": request.content_style.value,
            "generation_time_ms": generation_time_ms,
            "validation": content_result.get("validation", {})
        }

        # Per SLIDE_GENERATION_INPUT_SPEC.md: I-series uses background_color #ffffff
        return ISeriesGenerationResponse(
            image_html=image_html,
            title_html=title_html,
            subtitle_html=subtitle_html,
            content_html=content_html,
            image_url=image_url,
            image_fallback=image_fallback,
            background_color="#ffffff",  # Default per SPEC
            metadata=metadata
        )

    def _build_image_html(
        self,
        image_url: Optional[str],
        request: ISeriesGenerationRequest
    ) -> str:
        """
        Build HTML for image slot.

        Args:
            image_url: Generated image URL or None
            request: Original request for context

        Returns:
            HTML string for image slot
        """
        if image_url:
            return f'''<div style="width: 100%; height: 100%; overflow: hidden;">
    <img src="{image_url}"
         alt="Slide visual"
         style="width: 100%; height: 100%; object-fit: cover;"
    />
</div>'''
        else:
            # Placeholder gradient based on visual style
            gradient = self._get_fallback_gradient(request.visual_style)
            return f'''<div style="width: 100%; height: 100%;
    background: {gradient};
    display: flex; align-items: center; justify-content: center;">
    <span style="color: rgba(255,255,255,0.3); font-size: 48px; font-family: 'Inter', sans-serif;">IMAGE</span>
</div>'''

    def _get_fallback_gradient(self, visual_style: ISeriesVisualStyle) -> str:
        """
        Get fallback gradient based on visual style.

        Args:
            visual_style: Visual style enum

        Returns:
            CSS gradient string
        """
        gradients = {
            ISeriesVisualStyle.PROFESSIONAL: "linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%)",
            ISeriesVisualStyle.ILLUSTRATED: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            ISeriesVisualStyle.KIDS: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        }
        return gradients.get(visual_style, gradients[ISeriesVisualStyle.ILLUSTRATED])

    def _build_title_html(self, title: str) -> str:
        """
        Build HTML for title slot.

        Args:
            title: Slide title text

        Returns:
            HTML string for title
        """
        return f'''<h2 style="margin: 0 0 16px 0; font-size: 2.75rem; font-weight: 700;
    color: #1f2937; font-family: 'Inter', -apple-system, sans-serif;
    line-height: 1.2; letter-spacing: -0.02em;">{title}</h2>'''

    def _build_subtitle_html(self, subtitle: str) -> str:
        """
        Build HTML for subtitle slot.

        Args:
            subtitle: Subtitle text

        Returns:
            HTML string for subtitle
        """
        return f'''<p style="margin: 0 0 24px 0; font-size: 1.5rem; font-weight: 400;
    color: #6b7280; font-family: 'Inter', -apple-system, sans-serif;
    line-height: 1.5;">{subtitle}</p>'''
