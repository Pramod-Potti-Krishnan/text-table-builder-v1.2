"""
Title Slide Generator with AI-Generated Background Images

Generates title slides using L29 hero layout with AI-generated 16:9 background images
instead of gradient backgrounds. Text is positioned on the LEFT side with a dark gradient
overlay to ensure readability.

Differences from standard TitleSlideGenerator:
- Generates contextual background images via Image Builder v2.0 API
- Text LEFT-aligned (not centered)
- CSS gradient overlay (dark left → light right)
- Parallel image + content generation
- Graceful fallback to gradient-only if image fails

Layout: L29 Full-Bleed Hero with Background Image
Model: Flash (gemini-2.5-flash)
Complexity: Simple + Image Generation

Purpose:
- Opening slide with visual impact
- AI-generated background relevant to presentation topic
- Main title + subtitle on left side (white text on dark overlay)
"""

import asyncio
import logging
import re
from typing import Dict, Any, Optional

from .title_slide_generator import TitleSlideGenerator
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


class TitleSlideWithImageGenerator(TitleSlideGenerator):
    """
    Title slide generator with AI-generated background images.

    Extends TitleSlideGenerator to add:
    - Contextual background image generation
    - Left-aligned text layout (instead of centered)
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

    @property
    def slide_type(self) -> str:
        """Return slide type identifier."""
        return "title_slide_with_image"

    def _build_image_prompt(
        self,
        request: HeroGenerationRequest
    ) -> tuple[str, str]:
        """
        Build style-aware image generation prompt from presentation context.

        Creates a contextual prompt that generates an appropriate background
        image for the title slide based on the narrative, topics, and visual style.

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

        # Build style-aware image prompt with STRONG negative prompts
        prompt = f"""High-quality {visual_style} presentation background: {domain_imagery}.

Style: {style_config.prompt_style}
Composition: Abstract and sophisticated, darker left side, lighter right side for text overlay
Mood: Professional, trustworthy, innovative
Lighting: Natural, soft, appropriate for title slide

Focus on: {', '.join(topics[:2]) if topics else 'professional environment'}

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
            "professional": "corporate and modern",
            "bold": "dynamic and energetic",
            "warm": "friendly and approachable",
            "minimal": "clean and minimalist",
            "tech": "futuristic and innovative",
            "creative": "artistic and inspiring"
        }
        return styles.get(theme.lower(), "professional and polished")

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for title slide with image background.

        Modified from parent to use LEFT-aligned text and CSS gradient overlay
        instead of full gradient background.

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

        # Build prompt with IMPROVED professional design
        prompt = f"""Generate HTML content for a PROFESSIONAL TITLE SLIDE with AI background image.

## 🎯 Slide Purpose
**Function**: Opening slide with maximum visual impact
**Word Count**: 40-55 words total (brief and punchy)

## 📋 Content Requirements

1. **Main Title** (5-8 words maximum)
   - Clear, memorable, high-impact
   {f"- Suggested: '{presentation_title}'" if presentation_title else ""}
   - Based on: {narrative}

2. **Subtitle** (8-12 words maximum)
   - ONE compelling benefit or value statement
   - Brief and focused
   - What the audience will gain

3. **Footer Attribution**
   - Format EXACTLY: "Dr. FirstName LastName | Company Name | Mon DD, YYYY"
   - Clean, professional, separated by pipes

## 🎨 MANDATORY STYLING (Modern Professional Design)

### Typography (Inter font, responsive, sharp):
- Title: font-size: clamp(3rem, 5.5vw, 6rem); font-weight: 800; letter-spacing: -0.04em
- Subtitle: font-size: clamp(1rem, 1.6vw, 1.7rem); font-weight: 300; line-height: 1.5
- Footer: font-size: clamp(0.75rem, 1vw, 1rem); font-weight: 400; letter-spacing: 0.05em

### Layout (Professional, Balanced):
- Gradient: linear-gradient(90deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.7) 45%, rgba(0,0,0,0) 100%)
- Padding: 6% left, 50% right (text stays on left half)
- Footer: position absolute, bottom: 8%, left: 6%

## ✨ EXACT TEMPLATE (Use this structure):
```html
<div style="position: relative; width: 100%; height: 100%; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">

  <!-- Dark gradient overlay -->
  <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
              background: linear-gradient(90deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.7) 45%, rgba(0,0,0,0) 100%);
              z-index: 1;"></div>

  <!-- Content -->
  <div style="position: relative; z-index: 2; height: 100%; display: flex; flex-direction: column;
              justify-content: center; padding-left: 6%; padding-right: 50%; color: #ffffff;">

    <h1 style="font-size: clamp(3rem, 5.5vw, 6rem); font-weight: 800; line-height: 1.05;
               letter-spacing: -0.04em; margin: 0 0 28px 0; color: #ffffff;
               text-shadow: 0 4px 12px rgba(0,0,0,0.4); max-width: 100%;">
      Your Title with <span style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                                    -webkit-background-clip: text;
                                    -webkit-text-fill-color: transparent;
                                    background-clip: text;">Key Word</span> Here
    </h1>

    <p style="font-size: clamp(1rem, 1.6vw, 1.7rem); font-weight: 300; line-height: 1.5;
              color: rgba(255,255,255,0.92); margin: 0; max-width: 90%;
              text-shadow: 0 2px 8px rgba(0,0,0,0.3);">
      Your focused subtitle benefit statement here.
    </p>
  </div>

  <!-- Footer -->
  <div style="position: absolute; bottom: 8%; left: 6%; z-index: 2; display: flex; align-items: center;
              font-size: clamp(0.75rem, 1vw, 1rem); letter-spacing: 0.05em; text-transform: uppercase;
              color: rgba(255,255,255,0.75); text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
    <span>Presenter Name</span>
    <div style="margin: 0 15px; height: 15px; width: 1px; background-color: rgba(255,255,255,0.4);"></div>
    <span>Company Name</span>
    <div style="margin: 0 15px; height: 15px; width: 1px; background-color: rgba(255,255,255,0.4);"></div>
    <span>Nov 15, 2023</span>
  </div>

</div>
```

## 📤 OUTPUT INSTRUCTIONS
- Return ONLY the HTML (NO code blocks, NO explanations)
- Use EXACT structure above with responsive clamp() font sizes
- Keep subtitle BRIEF (8-12 words max, NOT a paragraph)
- Use Inter font (included in template)
- Footer must have separators and proper date format
- Title can be split across 2 lines if needed (use <br> if natural break point)

## ✨ ACCENT COLOR HIGHLIGHTING (MANDATORY)
- Wrap 1-2 KEY WORDS in title with accent color gradient span
- Choose the most important/impactful word(s) from narrative/topics
- Use the EXACT gradient style shown in template
- Gradient colors: #4facfe → #00f2fe (healthcare blue)
- Example: "AI in <span style='...gradient...'>Healthcare</span>"
- The highlighted word should be the CORE TOPIC or KEY CONCEPT

**Content Inputs**:
Narrative: {narrative}
Topics: {', '.join(topics) if topics else 'N/A'}
Theme: {theme}
Audience: {audience}

Generate the professional title slide HTML NOW:"""

        return prompt

    async def generate(
        self,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate title slide with background image.

        Runs image generation and content generation in parallel for performance.
        Falls back gracefully to gradient-only version if image generation fails.

        Args:
            request: Hero generation request

        Returns:
            Generation result with content, metadata, and background_image URL
        """
        logger.info(
            f"Generating title slide with background image "
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

            # Build response
            response = {
                "content": content_result["content"],
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
                f"Title slide with image generated successfully "
                f"(fallback: {fallback_to_gradient})"
            )

            return response

        except Exception as e:
            logger.error(f"Title slide with image generation failed: {e}")
            raise

    async def _generate_image_with_retry(
        self,
        prompt: str,
        archetype: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate background image with style-aware model selection.

        Uses smart model selection based on visual style:
        - Professional → imagen-3.0-generate-001 (standard quality)
        - Illustrated/Kids → imagen-3.0-fast-generate-001 (fast/cheap)

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
            "slide_type": "title_slide",
            "slide_number": request.slide_number,
            "narrative": request.narrative[:100],  # Truncate for storage
            "visual_style": request.visual_style
        }

        # Get appropriate model based on slide type and visual style
        model = get_image_model(request.slide_type, request.visual_style)

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
        Validate title slide with image content.

        Extends parent validation to check for LEFT-aligned layout
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

        # Check for LEFT alignment
        has_left_align = bool(
            re.search(r'align-items:\s*flex-start', content, re.IGNORECASE)
        )
        if not has_left_align:
            warnings.append(
                "Text should be LEFT-aligned (align-items: flex-start) for image background"
            )

        # Check for gradient overlay (not solid gradient)
        has_overlay = bool(
            re.search(r'rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.\d+\s*\)', content)
        )
        if not has_overlay:
            warnings.append(
                "Should use semi-transparent gradient overlay (rgba) for image background"
            )

        validation["warnings"] = warnings
        validation["violations"] = violations

        return validation
