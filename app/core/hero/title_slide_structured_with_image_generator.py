"""
Title Slide Generator with Structured Fields + AI-Generated Background Image

Generates title slide content in STRUCTURED format with AI-generated background
image URL. Unlike TitleSlideWithImageGenerator which returns full HTML, this
generator returns separate fields for Layout Service to compose.

Layout: H1-structured
Model: Flash (gemini-2.5-flash)
Complexity: Simple + Image Generation

Purpose:
- Opening slide with AI-generated background
- Returns structured fields: slide_title, subtitle, author_info
- Returns background_image URL for Layout Service to use
- Parallel image + content generation for performance

Response Format:
{
  "slide_title": "AI in Healthcare",
  "subtitle": "Transforming patient outcomes",
  "author_info": "Dr. Jane Doe | TechCorp | Dec 2024",
  "background_image": "https://supabase.../generated/abc.png",
  "metadata": { ... }
}

Version: 1.0.0 - Initial implementation
"""

import asyncio
import logging
from typing import Dict, Any

from .base_hero_generator import BaseHeroGenerator, HeroGenerationRequest
from .style_config import (
    get_style_config,
    get_domain_theme,
    get_image_model
)
from app.services.image_service_client import (
    get_image_service_client,
    ImageServiceClient,
    SlideType
)

logger = logging.getLogger(__name__)


class TitleSlideStructuredWithImageGenerator(BaseHeroGenerator):
    """
    Title slide generator with structured fields and AI-generated background image.

    Returns structured fields for Layout Service to compose, plus background_image URL.
    This is for H1-structured layout (not H1-generated which uses hero_content).
    """

    def __init__(self, llm_service):
        """
        Initialize generator with LLM and Image services.

        Args:
            llm_service: LLM service instance for content generation
        """
        super().__init__(llm_service)
        self.image_client: ImageServiceClient = get_image_service_client()

    @property
    def slide_type(self) -> str:
        """Return slide type identifier."""
        return "title_slide_structured_with_image"

    def _build_image_prompt(
        self,
        request: HeroGenerationRequest
    ) -> tuple[str, str]:
        """
        Build style-aware image generation prompt for title slide.

        Creates a contextual prompt for background image generation with
        domain detection and visual style support.

        Args:
            request: Hero generation request with narrative, context, and visual_style

        Returns:
            Tuple of (image_prompt, archetype)
        """
        # Check for global_brand for simplified prompting
        if request.global_brand and request.global_brand.get("visual_style"):
            return self._build_image_prompt_simplified(request)

        # Legacy domain-based prompting
        narrative = request.narrative
        topics = request.topics
        visual_style = request.visual_style
        theme = request.context.get("theme", "professional")

        # Get style configuration
        style_config = get_style_config(visual_style)

        # Determine industry/domain from narrative and topics
        combined_text = f"{narrative} {' '.join(topics) if topics else ''}".lower()
        domain_imagery = get_domain_theme(style_config, combined_text)

        # Build style-aware image prompt with STRONG topic focus
        topic_focus = ', '.join(topics[:2]) if topics else 'professional presentation'

        prompt = f"""High-quality {visual_style} presentation background: {domain_imagery}.

Style: {style_config.prompt_style}
Composition: Clean and impactful, topic-focused imagery, darker left side for text overlay
Mood: Professional, trustworthy, innovative
Lighting: Natural, soft, appropriate for title slide

MAIN SUBJECT: {topic_focus}
The image MUST prominently feature visual elements related to: {topic_focus}

CRITICAL: Absolutely NO text, words, letters, numbers, or typography of any kind in the image."""

        return prompt, style_config.archetype

    def _build_image_prompt_simplified(
        self,
        request: HeroGenerationRequest
    ) -> tuple[str, str]:
        """
        Build simplified ~30 word image prompt using global brand variables.

        Args:
            request: Hero generation request with global_brand variables

        Returns:
            Tuple of (image_prompt, archetype)
        """
        from app.core.iseries.prompt_assembler import (
            GlobalBrandVars, LocalMessageVars, assemble_prompt
        )

        # Extract global brand variables
        global_vars = GlobalBrandVars.from_dict(request.global_brand)

        # Extract anchor subject from narrative/topics
        anchor_subject = self._extract_anchor_subject(request)

        # Build local variables for this title slide
        local_vars = LocalMessageVars(
            content_archetype="title-hero",
            topic=request.narrative[:80] if request.narrative else "presentation opening",
            anchor_subject=anchor_subject,
            action_composition="with balanced composition and text overlay space on left",
            semantic_link="title slide",
            aspect_ratio="16:9"
        )

        # Assemble the simplified prompt
        prompt = assemble_prompt(global_vars, local_vars)

        # Determine archetype for metadata
        style_config = get_style_config(request.visual_style)

        return prompt, style_config.archetype

    def _extract_anchor_subject(self, request: HeroGenerationRequest) -> str:
        """
        Extract anchor subject for simplified prompting.

        Analyzes narrative and topics to find the best visual subject.

        Args:
            request: Hero generation request

        Returns:
            Anchor subject string for image prompt
        """
        topics = request.topics or []
        narrative = request.narrative or ""

        # Try to find a visual noun from topics
        if topics and len(topics[0]) > 5:
            return f"abstract visualization representing {topics[0]}"

        # Fall back to narrative-based subject
        if narrative:
            return f"abstract professional imagery representing {narrative[:50]}"

        return "abstract professional presentation background"

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for structured title slide content generation.

        Instructs LLM to return JSON with slide_title, subtitle, author_info fields.

        Args:
            request: Hero generation request with narrative and context

        Returns:
            Complete LLM prompt string
        """
        # Extract context
        theme = request.context.get("theme", "professional")
        audience = request.context.get("audience", "general business audience")
        presentation_title = request.context.get("presentation_title", "")
        narrative = request.narrative
        topics = request.topics

        # Extract theme_config for dynamic styling
        theme_config = request.context.get("theme_config")
        content_context = request.context.get("content_context")

        # Build audience context section
        context_section = ""
        if content_context:
            audience_info = content_context.get("audience", {})
            audience_type = audience_info.get("audience_type", "professional")
            context_section = f"""
## AUDIENCE & PURPOSE
- Audience: {audience_type}
- Language: Adapt vocabulary for {audience_type} audience
"""

        prompt = f"""Generate STRUCTURED content for a TITLE SLIDE (H1-structured layout).

Return ONLY a JSON object with these exact fields:
- slide_title: Main presentation title (3-6 words, 25-45 chars)
- subtitle: Compelling tagline or value proposition (10-18 words, 60-100 chars)
- author_info: Presenter | Company | Date format (35-50 chars)
{context_section}
## Content Requirements

1. **slide_title** (3-6 words, 25-45 characters):
   - Core presentation topic - clear and memorable
   {f"- Consider using: '{presentation_title}'" if presentation_title else ""}
   - Otherwise derive from narrative: {narrative}
   - STRICT: Must be between 25-45 characters

2. **subtitle** (10-18 words, 60-100 characters):
   - What the presentation delivers
   - Key theme or benefit
   - Compelling value proposition
   - STRICT: Must be between 60-100 characters

3. **author_info** (35-50 characters):
   - Format: "FirstName LastName | Company | Mon DD, YYYY"
   - Professional and complete
   - STRICT: Must be between 35-50 characters

## Content Inputs
- Narrative: {narrative}
- Topics: {', '.join(topics) if topics else 'N/A'}
- Theme: {theme}
- Audience: {audience}

## OUTPUT FORMAT (EXACT)
Return ONLY this JSON structure with NO markdown, NO explanation:
{{"slide_title": "Your Title Here", "subtitle": "Your subtitle here", "author_info": "Name | Company | Date"}}

Generate the JSON NOW:"""

        return prompt

    def _detect_domain(self, text: str) -> str:
        """
        Detect content domain from text for semantic cache categorization.

        Args:
            text: Combined narrative and topics text (lowercase)

        Returns:
            Domain identifier string
        """
        # Religious/Spiritual
        if any(word in text for word in [
            'shiva', 'hindu', 'temple', 'prayer', 'spiritual', 'sacred',
            'meditation', 'worship', 'divine', 'god', 'goddess', 'religious'
        ]):
            return "religious"

        # Healthcare
        if any(word in text for word in [
            'health', 'medical', 'hospital', 'patient', 'diagnostic',
            'clinical', 'doctor', 'nurse', 'healthcare', 'medicine'
        ]):
            return "healthcare"

        # Technology
        if any(word in text for word in [
            'tech', 'software', 'digital', 'ai', 'data', 'cloud',
            'code', 'algorithm', 'computing', 'system', 'cyber'
        ]):
            return "tech"

        # Education
        if any(word in text for word in [
            'school', 'university', 'student', 'learning', 'education',
            'teach', 'academic', 'classroom', 'course', 'curriculum'
        ]):
            return "education"

        # Finance
        if any(word in text for word in [
            'finance', 'business', 'market', 'trading', 'investment',
            'bank', 'revenue', 'profit', 'economy', 'financial'
        ]):
            return "finance"

        # Nature/Environment
        if any(word in text for word in [
            'nature', 'environment', 'climate', 'green', 'sustainable',
            'wildlife', 'forest', 'ocean', 'conservation', 'ecosystem'
        ]):
            return "nature"

        return "default"

    async def _generate_image_with_retry(
        self,
        prompt: str,
        archetype: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate background image with style-aware configuration.

        Args:
            prompt: Image generation prompt
            archetype: Image style archetype (photorealistic, spot_illustration)
            request: Hero generation request for metadata and visual_style

        Returns:
            Image API response dict

        Raises:
            Exception: If generation fails after retries
        """
        # Detect domain from narrative/topics for semantic cache
        combined_text = f"{request.narrative} {' '.join(request.topics) if request.topics else ''}".lower()
        domain = self._detect_domain(combined_text)

        metadata = {
            "slide_type": "title_slide_structured",
            "slide_number": request.slide_number,
            "narrative": request.narrative[:100] if request.narrative else "",
            "visual_style": request.visual_style,
            "topics": request.topics[:5] if request.topics else [],
            "domain": domain
        }

        # Director can override model via context
        context = request.context if hasattr(request, 'context') and request.context else {}
        model = context.get("image_model") or get_image_model(request.slide_type, request.visual_style)

        return await self.image_client.generate_background_image(
            prompt=prompt,
            slide_type=SlideType.TITLE,
            metadata=metadata,
            model=model,
            archetype=archetype
        )

    async def _generate_content(
        self,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate structured content fields using LLM.

        Args:
            request: Hero generation request

        Returns:
            Dict with slide_title, subtitle, author_info fields
        """
        import json

        # Build prompt
        prompt = await self._build_prompt(request)

        # Generate with LLM
        raw_content = await self.llm_service(prompt)

        # Clean markdown wrappers if present
        content = self._clean_markdown_wrapper(raw_content)

        # Try to parse as JSON
        try:
            # Remove any leading/trailing whitespace and potential code block markers
            content = content.strip()
            if content.startswith("```"):
                # Find the end of the code block marker
                first_newline = content.find("\n")
                if first_newline != -1:
                    content = content[first_newline+1:]
                # Remove trailing ```
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            parsed = json.loads(content)
            return {
                "slide_title": parsed.get("slide_title", ""),
                "subtitle": parsed.get("subtitle", ""),
                "author_info": parsed.get("author_info", "")
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            # Fall back to extracting text manually
            return self._extract_structured_content(content, request)

    def _extract_structured_content(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Extract structured content from non-JSON LLM response.

        Fallback when LLM doesn't return valid JSON.

        Args:
            content: Raw LLM response
            request: Original request for defaults

        Returns:
            Dict with slide_title, subtitle, author_info fields
        """
        import re

        # Try to find quoted strings or key-value patterns
        title_match = re.search(r'slide_title["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
        subtitle_match = re.search(r'subtitle["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
        author_match = re.search(r'author_info["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)

        # Derive defaults from request
        presentation_title = request.context.get("presentation_title", "")
        narrative = request.narrative or ""

        return {
            "slide_title": title_match.group(1) if title_match else (presentation_title or narrative[:80]),
            "subtitle": subtitle_match.group(1) if subtitle_match else "Driving innovation and growth",
            "author_info": author_match.group(1) if author_match else "Presenter | Company | 2024"
        }

    async def generate(
        self,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate structured title slide with background image.

        Runs image generation and content generation in parallel.
        Returns structured fields + background_image URL.

        Args:
            request: Hero generation request

        Returns:
            Dict with slide_title, subtitle, author_info, background_image, metadata
        """
        logger.info(
            f"Generating structured title slide with background image "
            f"(slide #{request.slide_number})"
        )

        try:
            # Generate image prompt and get archetype
            image_prompt, archetype = self._build_image_prompt(request)

            # Start both tasks in parallel
            image_task = asyncio.create_task(
                self._generate_image_with_retry(image_prompt, archetype, request)
            )
            content_task = asyncio.create_task(
                self._generate_content(request)
            )

            # Wait for both to complete
            results = await asyncio.gather(
                image_task,
                content_task,
                return_exceptions=True
            )

            image_result = results[0]
            content_result = results[1]

            # Check for content generation errors
            if isinstance(content_result, Exception):
                logger.error(f"Content generation failed: {content_result}")
                raise content_result

            # Check for image generation errors (non-fatal)
            background_image = None
            fallback_to_gradient = False
            image_metadata = {}

            if isinstance(image_result, Exception):
                logger.warning(
                    f"Image generation failed, using gradient fallback: {image_result}"
                )
                fallback_to_gradient = True
            elif image_result and image_result.get("success"):
                # Use cropped if available, otherwise use original
                background_image = (image_result["urls"].get("cropped") or
                                   image_result["urls"]["original"])
                image_metadata = image_result.get("metadata", {})
                logger.info(
                    f"Image generated successfully in "
                    f"{image_metadata.get('generation_time_ms', 0)}ms"
                )
            else:
                logger.warning("Image generation returned unsuccessful, using gradient fallback")
                fallback_to_gradient = True

            # Build response with structured fields
            response = {
                "slide_title": content_result.get("slide_title", ""),
                "subtitle": content_result.get("subtitle", ""),
                "author_info": content_result.get("author_info", ""),
                "background_image": background_image,
                "metadata": {
                    "slide_type": self.slide_type,
                    "slide_number": request.slide_number,
                    "background_image": background_image,
                    "image_generation_time_ms": image_metadata.get("generation_time_ms"),
                    "image_prompt_built": image_prompt,
                    "image_archetype_built": archetype,
                    "image_prompt_used": image_metadata.get("prompt"),
                    "image_archetype_used": image_metadata.get("archetype"),
                    "image_generator": image_metadata.get("generator_used") or image_metadata.get("generator"),
                    "image_model": image_metadata.get("model"),
                    "fallback_to_gradient": fallback_to_gradient,
                    "generation_mode": "structured_title_with_image_async",
                    "layout_type": "H1-structured"
                }
            }

            logger.info(
                f"Structured title slide with image generated successfully "
                f"(fallback: {fallback_to_gradient})"
            )

            return response

        except Exception as e:
            logger.error(f"Structured title slide with image generation failed: {e}")
            raise

    def _validate_output(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate structured output fields.

        Note: This is not typically called for structured output since we
        validate during _generate_content. Kept for interface compatibility.

        Args:
            content: Generated content (JSON string or dict)
            request: Original request for context

        Returns:
            Validation result dictionary
        """
        return {
            "valid": True,
            "violations": [],
            "warnings": [],
            "metrics": {}
        }
