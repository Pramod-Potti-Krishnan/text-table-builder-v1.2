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

Version: 1.3.0 - Added theme_config and content_context support
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

    def _inject_background_image(self, html_content: str, background_image: str) -> str:
        """
        Wrap HTML content with a container that has the background image.

        The title slide has text on the LEFT, so the image is positioned
        to focus on the RIGHT side (background-position: right center).

        Args:
            html_content: Generated HTML content from LLM
            background_image: URL of the generated background image

        Returns:
            HTML wrapped in a container with background image CSS
        """
        if not background_image:
            return html_content

        return f'''<div style="position: relative; width: 100%; height: 100%; background-image: url('{background_image}'); background-size: cover; background-position: right center;">
{html_content}
</div>'''

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

        v1.2.3: If global_brand is provided, uses simplified prompting (~30 words).

        Args:
            request: Hero generation request with narrative, context, and visual_style

        Returns:
            Tuple of (image_prompt, archetype)
        """
        # v1.2.3: Check for global_brand for simplified prompting
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
        topic_focus = ', '.join(topics[:2]) if topics else 'professional environment'

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

        v1.2.3: Uses prompt_assembler pattern for concise, natural language prompts.

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
            topic=request.narrative[:80] if request.narrative else "presentation theme",
            anchor_subject=anchor_subject,
            action_composition="with elegant composition and text overlay space on left",
            semantic_link="title slide",
            aspect_ratio="16:9"  # Title slides use landscape
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
            return f"abstract geometric shapes representing {narrative[:50]}"

        return "abstract professional business environment"

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

        v1.3.0: Uses theme_config for dynamic typography and accent colors,
        and content_context for audience-adapted language.

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

        # v1.3.0: Extract theme_config for dynamic styling
        theme_config = request.context.get("theme_config")
        content_context = request.context.get("content_context")

        # Extract typography from theme_config with defaults
        if theme_config and "typography" in theme_config:
            typo = theme_config["typography"]
            hero_title = typo.get("hero_title", {})
            # Convert px to rem (base 16px)
            title_size_px = hero_title.get("size", 88)
            title_size = f"{title_size_px / 16:.2f}rem"
            title_weight = hero_title.get("weight", 800)
            hero_subtitle = typo.get("hero_subtitle", typo.get("slide_title", {}))
            subtitle_size_px = hero_subtitle.get("size", 34)
            subtitle_size = f"{subtitle_size_px / 16:.2f}rem"
        else:
            title_size, title_weight = "5.5rem", 800
            subtitle_size = "2.1rem"

        # Extract accent colors from theme_config
        if theme_config and "colors" in theme_config:
            colors = theme_config["colors"]
            accent = colors.get("accent", "#4facfe")
            accent_light = colors.get("accent_light", "#00f2fe")
            accent_gradient = f"linear-gradient(135deg, {accent} 0%, {accent_light} 100%)"
        else:
            accent_gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"

        # v1.3.0: Build audience context section
        context_section = ""
        if content_context:
            audience_info = content_context.get("audience", {})
            purpose_info = content_context.get("purpose", {})
            audience_type = audience_info.get("audience_type", "professional")
            complexity = audience_info.get("complexity_level", "moderate")
            purpose_type = purpose_info.get("purpose_type", "inform")

            context_section = f"""
## 📊 AUDIENCE & PURPOSE
- **Audience**: {audience_type} ({complexity} complexity)
- **Purpose**: {purpose_type}
- **Language**: Adapt vocabulary and tone for {audience_type} audience
- **Avoid jargon**: {"Yes - use simple language" if audience_info.get("avoid_jargon") else "Use professional terminology as appropriate"}
"""

        # Build prompt with IMPROVED professional design
        prompt = f"""Generate HTML content for a PROFESSIONAL TITLE SLIDE with AI background image.

## 🎯 Slide Purpose
**Function**: Opening slide with maximum visual impact
**Word Count**: 40-55 words total (brief and punchy)
{context_section}
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

### Typography (Inter font, fixed sizes for reveal.js scaling):
- Title: font-size: {title_size}; font-weight: {title_weight}; letter-spacing: -0.04em
- Subtitle: font-size: {subtitle_size}; font-weight: 300; line-height: 1.5
- Footer: font-size: 1.6rem; font-weight: 400; letter-spacing: 0.05em

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

    <h1 style="font-size: {title_size}; font-weight: {title_weight}; line-height: 1.05;
               letter-spacing: -0.04em; margin: 0 0 28px 0; color: #ffffff;
               text-shadow: 0 4px 12px rgba(0,0,0,0.4); max-width: 100%;">
      Your Title with <span style="background: {accent_gradient};
                                    -webkit-background-clip: text;
                                    -webkit-text-fill-color: transparent;
                                    background-clip: text;">Key Word</span> Here
    </h1>

    <p style="font-size: {subtitle_size}; font-weight: 300; line-height: 1.5;
              color: rgba(255,255,255,0.92); margin: 0; max-width: 90%;
              text-shadow: 0 2px 8px rgba(0,0,0,0.3);">
      Your focused subtitle benefit statement here.
    </p>
  </div>

  <!-- Footer -->
  <div style="position: absolute; bottom: 8%; left: 6%; z-index: 2; display: flex; align-items: center;
              font-size: 1.6rem; letter-spacing: 0.05em; text-transform: uppercase;
              color: rgba(255,255,255,0.75); text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
    <span>Presenter Name</span>
    <div style="margin: 0 15px; height: 24px; width: 1px; background-color: rgba(255,255,255,0.4);"></div>
    <span>Company Name</span>
    <div style="margin: 0 15px; height: 24px; width: 1px; background-color: rgba(255,255,255,0.4);"></div>
    <span>Nov 15, 2023</span>
  </div>

</div>
```

## 📤 OUTPUT INSTRUCTIONS
- Return ONLY the HTML (NO code blocks, NO explanations)
- Use EXACT structure above with the specified font sizes
- Keep subtitle BRIEF (8-12 words max, NOT a paragraph)
- Use Inter font (included in template)
- Footer must have separators and proper date format
- Title can be split across 2 lines if needed (use <br> if natural break point)

## ✨ ACCENT COLOR HIGHLIGHTING (MANDATORY)
- Wrap 1-2 KEY WORDS in title with accent color gradient span
- Choose the most important/impactful word(s) from narrative/topics
- Use the EXACT gradient style: {accent_gradient}
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

        v1.5.0: Director can override model via request.context["image_model"]
        for presentation-level quality tier control.

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
            "slide_type": "title_slide",
            "slide_number": request.slide_number,
            "narrative": request.narrative[:100],  # Truncate for storage
            "visual_style": request.visual_style,
            # Semantic cache fields
            "topics": request.topics[:5] if request.topics else [],  # Top 5 topics
            "domain": domain
        }

        # v1.5.0: Director can override model via context for quality tier selection
        context = request.context if hasattr(request, 'context') and request.context else {}
        model = context.get("image_model") or get_image_model(request.slide_type, request.visual_style)

        return await self.image_client.generate_background_image(
            prompt=prompt,
            slide_type=SlideType.TITLE,
            metadata=metadata,
            model=model,
            archetype=archetype
        )

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
            'meditation', 'worship', 'divine', 'god', 'goddess', 'religious',
            'buddha', 'christian', 'islam', 'church', 'mosque', 'dharma'
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

        # Science
        if any(word in text for word in [
            'research', 'experiment', 'laboratory', 'chemistry', 'physics',
            'biology', 'scientific', 'discovery', 'hypothesis', 'analysis'
        ]):
            return "science"

        # Creative
        if any(word in text for word in [
            'art', 'design', 'creative', 'music', 'artist', 'gallery',
            'paint', 'sculpture', 'photography', 'illustration', 'visual'
        ]):
            return "creative"

        return "default"

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
