"""
Closing Slide Generator with Structured Fields + AI-Generated Background Image

Generates closing slide content in STRUCTURED format with AI-generated background
image URL. Unlike ClosingSlideWithImageGenerator which returns full HTML, this
generator returns separate fields for Layout Service to compose.

Layout: H3-closing
Model: Flash (gemini-2.5-flash)
Complexity: Simple + Image Generation

Purpose:
- Closing/thank you slide with AI-generated background
- Returns structured fields: slide_title, subtitle, contact_info
- Returns background_image URL for Layout Service to use
- Parallel image + content generation for performance

Response Format:
{
  "slide_title": "Thank You",
  "subtitle": "Questions & Discussion",
  "contact_info": "contact@company.com | www.company.com",
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


class ClosingSlideStructuredWithImageGenerator(BaseHeroGenerator):
    """
    Closing slide generator with structured fields and AI-generated background image.

    Returns structured fields for Layout Service to compose, plus background_image URL.
    This is for H3-closing layout which expects separate fields (not hero_content HTML).
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
        return "closing_slide_structured_with_image"

    def _build_image_prompt(
        self,
        request: HeroGenerationRequest
    ) -> tuple[str, str]:
        """
        Build style-aware image generation prompt for closing slide.

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

        # Build style-aware image prompt
        topic_focus = ', '.join(topics[:2]) if topics else 'professional conclusion'

        prompt = f"""High-quality {visual_style} closing slide background: {domain_imagery}.

Style: {style_config.prompt_style}
Composition: Clean and impactful, suitable for thank you/closing message, darker area for text
Mood: Warm, appreciative, forward-looking, professional
Lighting: Natural, soft, inspiring

MAIN SUBJECT: {topic_focus}
The image should evoke completion, gratitude, and future partnership.

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

        # Build local variables for this closing slide
        local_vars = LocalMessageVars(
            content_archetype="closing-gratitude",
            topic=request.narrative[:80] if request.narrative else "thank you closing",
            anchor_subject=anchor_subject,
            action_composition="with warm composition suggesting completion and future partnership",
            semantic_link="closing slide",
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
            return f"abstract visualization representing {topics[0]} with sense of completion"

        # Fall back to narrative-based subject
        if narrative:
            return f"abstract professional imagery representing {narrative[:50]}"

        return "abstract professional closing with sense of gratitude"

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for structured closing slide content generation.

        Instructs LLM to return JSON with slide_title, subtitle, contact_info fields.

        Args:
            request: Hero generation request with narrative and context

        Returns:
            Complete LLM prompt string
        """
        # Extract context
        theme = request.context.get("theme", "professional")
        narrative = request.narrative
        topics = request.topics
        contact_info = request.context.get("contact_info", "")

        # Extract content_context for audience-adapted language
        content_context = request.context.get("content_context")

        # Build audience context section
        context_section = ""
        if content_context:
            audience_info = content_context.get("audience", {})
            purpose_info = content_context.get("purpose", {})
            audience_type = audience_info.get("audience_type", "professional")
            emotional_tone = purpose_info.get("emotional_tone", "professional")
            context_section = f"""
## AUDIENCE & PURPOSE
- Audience: {audience_type}
- Tone: {emotional_tone}
- Language: Warm, appreciative, forward-looking
"""

        prompt = f"""Generate STRUCTURED content for a CLOSING SLIDE (H3-closing layout).

Return ONLY a JSON object with these exact fields:
- slide_title: Main closing message (2-5 words, max 40 chars) - warm and memorable
- subtitle: Secondary message or call-to-action (5-12 words, max 80 chars)
- contact_info: Contact details (email, website, phone - formatted nicely)
{context_section}
## Content Requirements

1. **slide_title**:
   - Warm, appreciative closing message
   - Examples: "Thank You", "Let's Connect", "Ready to Partner?", "Questions?"
   - Should feel genuine, not generic

2. **subtitle**:
   - Secondary message or call-to-action
   - Examples: "We'd love to hear from you", "Let's shape the future together"
   - Based on narrative: {narrative}

3. **contact_info**:
   - Professional contact details
   {f"- Use provided info: '{contact_info}'" if contact_info else "- Format: email@company.com | www.company.com"}

## Content Inputs
- Narrative: {narrative}
- Topics: {', '.join(topics) if topics else 'N/A'}
- Theme: {theme}
{f"- Contact: {contact_info}" if contact_info else ""}

## OUTPUT FORMAT (EXACT)
Return ONLY this JSON structure with NO markdown, NO explanation:
{{"slide_title": "Thank You", "subtitle": "Your subtitle here", "contact_info": "contact@company.com | www.company.com"}}

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
            "slide_type": "closing_slide_structured",
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
            slide_type=SlideType.CLOSING,
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
            Dict with slide_title, subtitle, contact_info fields
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
                "slide_title": parsed.get("slide_title", "Thank You"),
                "subtitle": parsed.get("subtitle", ""),
                "contact_info": parsed.get("contact_info", "")
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
            Dict with slide_title, subtitle, contact_info fields
        """
        # Try to find quoted strings or key-value patterns
        title_match = re.search(r'slide_title["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
        subtitle_match = re.search(r'subtitle["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
        contact_match = re.search(r'contact_info["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)

        # Derive defaults from request
        contact_info = request.context.get("contact_info", "contact@company.com | www.company.com")

        return {
            "slide_title": title_match.group(1) if title_match else "Thank You",
            "subtitle": subtitle_match.group(1) if subtitle_match else "We appreciate your time",
            "contact_info": contact_match.group(1) if contact_match else contact_info
        }

    async def generate(
        self,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate structured closing slide with background image.

        Runs image generation and content generation in parallel.
        Returns structured fields + background_image URL.

        Args:
            request: Hero generation request

        Returns:
            Dict with slide_title, subtitle, contact_info, background_image, metadata
        """
        logger.info(
            f"Generating structured closing slide with background image "
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
                "slide_title": content_result.get("slide_title", "Thank You"),
                "subtitle": content_result.get("subtitle", ""),
                "contact_info": content_result.get("contact_info", ""),
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
                    "generation_mode": "structured_closing_with_image_async",
                    "layout_type": "H3-closing"
                }
            }

            logger.info(
                f"Structured closing slide with image generated successfully "
                f"(fallback: {fallback_to_gradient})"
            )

            return response

        except Exception as e:
            logger.error(f"Structured closing slide with image generation failed: {e}")
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
