"""
Section Divider Generator with AI-Generated Background Images

Generates section divider slides using L29 hero layout with AI-generated 16:9
background images. Text is positioned on the RIGHT side with a dark gradient
overlay to ensure readability.

Differences from standard SectionDividerGenerator:
- Generates contextual background images via Image Builder v2.0 API
- Text RIGHT-aligned (not left-aligned)
- CSS gradient overlay (dark right → light left)
- Parallel image + content generation
- Graceful fallback to solid dark background if image fails

Layout: L29 Full-Bleed Hero with Background Image
Model: Flash (gemini-2.5-flash)
Complexity: Simple + Image Generation

Purpose:
- Section transition with visual context
- AI-generated background relevant to new section topic
- Clear topic shift with right-aligned text
"""

import asyncio
import logging
import re
from typing import Dict, Any

from .section_divider_generator import SectionDividerGenerator
from .base_hero_generator import HeroGenerationRequest
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


class SectionDividerWithImageGenerator(SectionDividerGenerator):
    """
    Section divider generator with AI-generated background images.

    Extends SectionDividerGenerator to add:
    - Contextual background image generation
    - Right-aligned text layout
    - Dark gradient overlay for text readability
    - Parallel execution for performance
    """

    def __init__(self, llm_service):
        """
        Initialize generator with LLM and Image services.

        Args:
            llm_service: LLM service instance for content generation
        """
        super().__init__(llm_service)
        self.image_client: ImageServiceClient = get_image_service_client()

    def _inject_background_image(self, html_content: str, background_image: str) -> str:
        """
        Wrap HTML content with a container that has the background image.

        The section divider has text on the RIGHT, so the image is positioned
        to focus on the LEFT side (background-position: left center).

        Args:
            html_content: Generated HTML content from LLM
            background_image: URL of the generated background image

        Returns:
            HTML wrapped in a container with background image CSS
        """
        if not background_image:
            return html_content

        return f'''<div style="position: relative; width: 100%; height: 100%; background-image: url('{background_image}'); background-size: cover; background-position: left center;">
{html_content}
</div>'''

    @property
    def slide_type(self) -> str:
        """Return slide type identifier."""
        return "section_divider_with_image"

    def _build_image_prompt(
        self,
        request: HeroGenerationRequest
    ) -> tuple[str, str]:
        """
        Build style-aware image generation prompt for section divider.

        Creates a contextual prompt that generates an appropriate transition background
        with smart domain detection and visual style support.

        Args:
            request: Hero generation request with narrative, context, and visual_style

        Returns:
            Tuple of (image_prompt, archetype)
        """
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
Composition: Clean and minimal, darker RIGHT side, lighter LEFT side for text overlay
Mood: Professional, transitional, forward-moving
Lighting: Natural, soft, appropriate for section break

MAIN SUBJECT: {topic_focus}
The image MUST prominently feature visual elements related to: {topic_focus}

CRITICAL: Absolutely NO text, words, letters, numbers, or typography of any kind in the image."""

        return prompt, style_config.archetype

    def _get_theme_style(self, theme: str) -> str:
        """
        Get visual style description based on theme.

        Args:
            theme: Presentation theme

        Returns:
            Style description string
        """
        styles = {
            "professional": "subtle and refined",
            "bold": "dynamic with energy",
            "warm": "soft and approachable",
            "minimal": "ultra-clean and simple",
            "tech": "modern and sleek",
            "creative": "artistic but restrained"
        }
        return styles.get(theme.lower(), "professional and understated")

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for section divider with image background.

        Modified from parent to use RIGHT-aligned text and CSS gradient overlay.

        Args:
            request: Hero generation request with narrative and context

        Returns:
            Complete LLM prompt string
        """
        # Extract context
        theme = request.context.get("theme", "professional")
        narrative = request.narrative
        topics = request.topics

        # Build prompt with modern design principles
        prompt = f"""Generate HTML content for a PROFESSIONAL SECTION DIVIDER SLIDE with AI background image.

## 🎯 Slide Purpose
**Function**: Signal major topic transition with visual context
**Word Count**: 20-35 words total (concise and impactful)

## 📋 Content Requirements

1. **Section Title** (3-6 words maximum)
   - Clear topic or phase name
   - Impactful and memorable
   - Based on: {narrative}
   - Topics: {', '.join(topics) if topics else 'N/A'}

2. **Context Text** (5-12 words, optional)
   - Brief preview of what's coming
   - Can be omitted for minimal look

## 🎨 MANDATORY STYLING (Modern Professional Design)

### Typography (Inter font, fixed sizes for reveal.js scaling):
- Section Title: font-size: 5.5rem; font-weight: 800; letter-spacing: -0.03em
- Context Text: font-size: 2.1rem; font-weight: 300; line-height: 1.4

### Layout (Professional, RIGHT-aligned):
- Gradient: linear-gradient(to left, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.05) 100%)
- Padding: 80px 120px 80px 200px (text stays on RIGHT half)
- Text block: border-left: 8px solid #00d9ff (cyan accent)

## ✨ EXACT TEMPLATE (Use this structure):
```html
<div style="position: relative; width: 100%; height: 100%; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">

  <!-- Dark gradient overlay (dark right → light left) -->
  <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
              background: linear-gradient(to left, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.05) 100%);
              z-index: 1;"></div>

  <!-- Content (RIGHT-aligned) -->
  <div style="position: relative; z-index: 2; height: 100%; display: flex;
              align-items: center; justify-content: flex-end;
              padding: 80px 120px 80px 200px;">

    <div style="border-left: 8px solid #00d9ff; padding-left: 48px; max-width: 50%;">

      <h2 style="font-size: 5.5rem; font-weight: 800; line-height: 1.05;
                 letter-spacing: -0.03em; margin: 0 0 24px 0; color: #ffffff;
                 text-shadow: 0 4px 12px rgba(0,0,0,0.4); text-align: left;">
        Implementation <span style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                                      -webkit-background-clip: text;
                                      -webkit-text-fill-color: transparent;
                                      background-clip: text;">Roadmap</span>
      </h2>

      <p style="font-size: 2.1rem; font-weight: 300; line-height: 1.4;
                color: rgba(255,255,255,0.92); margin: 0; text-align: left;
                text-shadow: 0 2px 8px rgba(0,0,0,0.3);">
        From Strategy to Full Deployment
      </p>

    </div>

  </div>

</div>
```

## 📤 OUTPUT INSTRUCTIONS
- Return ONLY the HTML (NO code blocks, NO explanations)
- Use EXACT structure above with fixed rem font sizes
- Keep context text BRIEF (5-12 words max, NOT a paragraph)
- Use Inter font (included in template)
- Text must be RIGHT-aligned (justify-content: flex-end)
- Cyan accent border: border-left: 8px solid #00d9ff

## ✨ ACCENT COLOR HIGHLIGHTING (MANDATORY)
- Wrap 1-2 KEY WORDS in section title with accent color gradient span
- Choose the most important/impactful word(s) from narrative/topics
- Use the EXACT gradient style shown in template
- Gradient colors: #4facfe → #00f2fe (cyan-blue)
- Example: "Implementation <span style='...gradient...'>Roadmap</span>"
- The highlighted word should be the CORE TOPIC or KEY CONCEPT

**Content Inputs**:
Narrative: {narrative}
Topics: {', '.join(topics) if topics else 'N/A'}
Theme: {theme}

Generate the professional section divider HTML NOW:"""

        return prompt

    async def generate(
        self,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate section divider with background image.

        Runs image generation and content generation in parallel for performance.
        Falls back gracefully to solid dark background if image generation fails.

        Args:
            request: Hero generation request

        Returns:
            Generation result with content, metadata, and background_image URL
        """
        logger.info(
            f"Generating section divider with background image "
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
                    f"Image generation failed, using dark background fallback: {image_result}"
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
                logger.warning("Image generation returned unsuccessful, using dark background fallback")
                fallback_to_gradient = True

            # Inject background image into HTML content
            final_content = content_result["content"]
            if background_image:
                final_content = self._inject_background_image(final_content, background_image)

            # Build response
            response = {
                "content": final_content,
                "metadata": {
                    "slide_type": self.slide_type,
                    "slide_number": request.slide_number,
                    "background_image": background_image,
                    "image_generation_time_ms": image_metadata.get("generation_time_ms"),
                    "fallback_to_gradient": fallback_to_gradient,
                    "validation": content_result.get("validation", {}),
                    "generation_mode": "hero_slide_with_image_async"
                }
            }

            logger.info(
                f"Section divider with image generated successfully "
                f"(fallback: {fallback_to_gradient})"
            )

            return response

        except Exception as e:
            logger.error(f"Section divider with image generation failed: {e}")
            raise

    async def _generate_image_with_retry(
        self,
        prompt: str,
        archetype: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate background image with style-aware configuration.

        Section dividers ALWAYS use fast model regardless of visual style
        to optimize cost for transition slides.

        Args:
            prompt: Image generation prompt
            archetype: Image style archetype (photorealistic, spot_illustration)
            request: Hero generation request for metadata and visual_style

        Returns:
            Image API response dict

        Raises:
            Exception: If generation fails after retries
        """
        metadata = {
            "slide_type": "section_divider",
            "slide_number": request.slide_number,
            "narrative": request.narrative[:100],  # Truncate for storage
            "visual_style": request.visual_style
        }

        # Section dividers always use fast model (all styles)
        model = get_image_model(request.slide_type, request.visual_style)

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
        Generate HTML content using LLM.

        Args:
            request: Hero generation request

        Returns:
            Dict with content and validation results
        """
        # Build prompt
        prompt = await self._build_prompt(request)

        # Generate with LLM
        raw_content = await self.llm_service(prompt)

        # Clean markdown wrappers
        content = self._clean_markdown_wrapper(raw_content)

        # Validate
        validation = self._validate_output(content, request)

        return {
            "content": content,
            "validation": validation
        }

    def _validate_output(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate section divider with image content.

        Extends parent validation to check for RIGHT-aligned layout
        and gradient overlay.

        Args:
            content: Generated HTML content
            request: Original request for context

        Returns:
            Validation result dictionary
        """
        # Run parent validation
        validation = super()._validate_output(content, request)

        # Additional checks for image variant
        warnings = validation.get("warnings", [])
        violations = validation.get("violations", [])

        # Check for RIGHT alignment
        has_right_align = bool(
            re.search(r'justify-content:\s*flex-end', content, re.IGNORECASE)
        )
        if not has_right_align:
            warnings.append(
                "Container should be RIGHT-aligned (justify-content: flex-end) for image background"
            )

        # Check for gradient overlay (not solid background)
        has_overlay = bool(
            re.search(r'rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.\d+\s*\)', content)
        )
        if not has_overlay:
            warnings.append(
                "Should use semi-transparent gradient overlay (rgba) for image background"
            )

        # Check for reverse gradient direction (dark right → light left)
        has_reverse_gradient = bool(
            re.search(r'linear-gradient\(\s*to\s+left', content, re.IGNORECASE)
        )
        if not has_reverse_gradient:
            warnings.append(
                "Gradient should be 'to left' (dark right → light left) for right-aligned text"
            )

        validation["warnings"] = warnings
        validation["violations"] = violations

        return validation
