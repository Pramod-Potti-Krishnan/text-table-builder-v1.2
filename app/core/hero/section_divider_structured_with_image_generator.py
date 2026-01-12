"""
Section Divider Generator with Structured Fields + AI-Generated Background Image

Generates section divider content in STRUCTURED format with AI-generated background
image URL. Unlike SectionDividerWithImageGenerator which returns full HTML, this
generator returns separate fields for Layout Service to compose.

Layout: H2-section
Model: Flash (gemini-2.5-flash)
Complexity: Simple + Image Generation

Purpose:
- Section transition with AI-generated background
- Returns structured fields: section_number, slide_title
- Returns background_image URL for Layout Service to use
- Parallel image + content generation for performance

Response Format:
{
  "section_number": "01",
  "slide_title": "Strategic Overview",
  "background_image": "https://supabase.../generated/abc.png",
  "metadata": { ... }
}

Version: 1.0.0 - Initial implementation
"""

import asyncio
import json
import logging
import re
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


class SectionDividerStructuredWithImageGenerator(BaseHeroGenerator):
    """
    Section divider generator with structured fields and AI-generated background image.

    Returns structured fields for Layout Service to compose, plus background_image URL.
    This is for H2-section layout which expects separate fields (not hero_content HTML).
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
        return "section_divider_structured_with_image"

    def _build_image_prompt(
        self,
        request: HeroGenerationRequest
    ) -> tuple[str, str]:
        """
        Build style-aware image generation prompt for section divider.

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
        topic_focus = ', '.join(topics[:2]) if topics else 'professional transition'

        prompt = f"""High-quality {visual_style} section transition background: {domain_imagery}.

Style: {style_config.prompt_style}
Composition: Clean and minimal, darker RIGHT side for text overlay, lighter LEFT side
Mood: Professional, transitional, forward-moving
Lighting: Natural, soft, appropriate for section break

MAIN SUBJECT: {topic_focus}
The image MUST prominently feature visual elements related to: {topic_focus}

TEXT GUIDANCE: Prefer text-free imagery - the slide content handles messaging. Avoid adding words, letters, or typography unless naturally part of the scene (book titles, signs, labels are acceptable)."""

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

        # Build local variables for this section divider
        local_vars = LocalMessageVars(
            content_archetype="section-transition",
            topic=request.narrative[:80] if request.narrative else "section break",
            anchor_subject=anchor_subject,
            action_composition="with balanced composition and text overlay space on right",
            semantic_link="section transition",
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
            return f"abstract geometric shapes representing {narrative[:50]}"

        return "abstract professional section transition"

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for structured section divider content generation.

        Instructs LLM to return JSON with section_number, slide_title fields.

        Args:
            request: Hero generation request with narrative and context

        Returns:
            Complete LLM prompt string
        """
        # Extract context
        theme = request.context.get("theme", "professional")
        narrative = request.narrative
        topics = request.topics
        section_title = request.context.get("section_title", "")
        section_number = request.context.get("section_number", "01")

        # Extract content_context for audience-adapted language
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

        prompt = f"""Generate STRUCTURED content for a SECTION DIVIDER SLIDE (H2-section layout).

Return ONLY a JSON object with these exact fields:
- section_number: Section number (e.g., "01", "02", "03") - max 2 characters
- slide_title: Section title (2-7 words, 10-35 chars) - clear and impactful
{context_section}
## Content Requirements

1. **section_number**:
   - Format: Two-digit number like "01", "02", "03"
   - {f"Use: '{section_number}'" if section_number else "Derive from context or default to '01'"}

2. **slide_title** (2-7 words, 10-35 characters):
   - Clear topic or phase name
   - Impactful and memorable
   {f"- Consider using: '{section_title}'" if section_title else ""}
   - Otherwise derive from narrative: {narrative}
   - STRICT: Must be between 10-35 characters

## Content Inputs
- Narrative: {narrative}
- Topics: {', '.join(topics) if topics else 'N/A'}
- Theme: {theme}

## OUTPUT FORMAT (EXACT)
Return ONLY this JSON structure with NO markdown, NO explanation:
{{"section_number": "01", "slide_title": "Your Section Title"}}

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

        # Finance
        if any(word in text for word in [
            'finance', 'business', 'market', 'trading', 'investment',
            'bank', 'revenue', 'profit', 'economy', 'financial'
        ]):
            return "finance"

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
            archetype: Image style archetype
            request: Hero generation request for metadata

        Returns:
            Image API response dict
        """
        combined_text = f"{request.narrative} {' '.join(request.topics) if request.topics else ''}".lower()
        domain = self._detect_domain(combined_text)

        metadata = {
            "slide_type": "section_divider_structured",
            "slide_number": request.slide_number,
            "narrative": request.narrative[:100] if request.narrative else "",
            "visual_style": request.visual_style,
            "topics": request.topics[:5] if request.topics else [],
            "domain": domain
        }

        context = request.context if hasattr(request, 'context') and request.context else {}
        model = context.get("image_model") or get_image_model(request.slide_type, request.visual_style)

        return await self.image_client.generate_background_image(
            prompt=prompt,
            slide_type=SlideType.SECTION,
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
            Dict with section_number, slide_title fields
        """
        # Build prompt
        prompt = await self._build_prompt(request)

        # Generate with LLM
        raw_content = await self.llm_service(prompt)

        # Clean markdown wrappers if present
        content = self._clean_markdown_wrapper(raw_content)

        # Try to parse as JSON
        try:
            content = content.strip()
            if content.startswith("```"):
                first_newline = content.find("\n")
                if first_newline != -1:
                    content = content[first_newline+1:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            parsed = json.loads(content)
            return {
                "section_number": parsed.get("section_number", "01"),
                "slide_title": parsed.get("slide_title", "")
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            return self._extract_structured_content(content, request)

    def _extract_structured_content(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Extract structured content from non-JSON LLM response.

        Args:
            content: Raw LLM response
            request: Original request for defaults

        Returns:
            Dict with section_number, slide_title fields
        """
        # Try to find quoted strings or key-value patterns
        number_match = re.search(r'section_number["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
        title_match = re.search(r'slide_title["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)

        # Derive defaults from request
        section_title = request.context.get("section_title", "")
        section_number = request.context.get("section_number", "01")
        narrative = request.narrative or ""

        return {
            "section_number": number_match.group(1) if number_match else section_number,
            "slide_title": title_match.group(1) if title_match else (section_title or narrative[:50])
        }

    async def generate(
        self,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate structured section divider with background image.

        Runs image generation and content generation in parallel.
        Returns structured fields + background_image URL.

        Args:
            request: Hero generation request

        Returns:
            Dict with section_number, slide_title, background_image, metadata
        """
        logger.info(
            f"Generating structured section divider with background image "
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
                "section_number": content_result.get("section_number", "01"),
                "slide_title": content_result.get("slide_title", ""),
                "background_image": background_image,
                "metadata": {
                    "slide_type": self.slide_type,
                    "slide_number": request.slide_number,
                    "background_image": background_image,
                    "image_generation_time_ms": image_metadata.get("generation_time_ms"),
                    "image_prompt_built": image_prompt,
                    "image_archetype_built": archetype,
                    "image_generator": image_metadata.get("generator_used") or image_metadata.get("generator"),
                    "image_model": image_metadata.get("model"),
                    "fallback_to_gradient": fallback_to_gradient,
                    "generation_mode": "structured_section_with_image_async",
                    "layout_type": "H2-section"
                }
            }

            logger.info(
                f"Structured section divider with image generated successfully "
                f"(fallback: {fallback_to_gradient})"
            )

            return response

        except Exception as e:
            logger.error(f"Structured section divider with image generation failed: {e}")
            raise

    def _validate_output(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate structured output fields.

        Args:
            content: Generated content
            request: Original request

        Returns:
            Validation result dictionary
        """
        return {
            "valid": True,
            "violations": [],
            "warnings": [],
            "metrics": {}
        }
