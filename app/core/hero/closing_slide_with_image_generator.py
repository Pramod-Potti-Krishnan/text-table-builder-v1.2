"""
Closing Slide Generator with AI-Generated Background Images

Generates closing/conclusion slides using L29 hero layout with AI-generated 16:9
background images. Text is center-aligned with a radial gradient overlay
(darker edges, lighter center) to ensure readability.

Differences from standard ClosingSlideGenerator:
- Generates contextual background images via Image Builder v2.0 API
- Text CENTER-aligned (unchanged from base)
- Radial CSS gradient overlay (dark edges → light center)
- Parallel image + content generation
- Graceful fallback to gradient background if image fails

Layout: L29 Full-Bleed Hero with Background Image
Model: Flash (gemini-2.5-flash)
Complexity: Simple + Image Generation

Purpose:
- Closing slide with inspiring visual
- AI-generated background relevant to presentation outcome/impact
- Call-to-action with center-aligned layout

Version: 1.3.0 - Added theme_config and content_context support
"""

import asyncio
import logging
import re
from typing import Dict, Any

from .closing_slide_generator import ClosingSlideGenerator
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


class ClosingSlideWithImageGenerator(ClosingSlideGenerator):
    """
    Closing slide generator with AI-generated background images.

    Extends ClosingSlideGenerator to add:
    - Contextual background image generation
    - Center-aligned text layout (same as base)
    - Radial gradient overlay for text readability
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
        Inject background image into the RIGHT column placeholder div.

        The closing slide has a split layout:
        - LEFT column: text content
        - RIGHT column: image with gradient overlay

        The LLM generates a placeholder div that needs the background-image injected:
        <div style="position: absolute; inset: 0; background-size: cover; background-position: center;"></div>

        Args:
            html_content: Generated HTML content from LLM
            background_image: URL of the generated background image

        Returns:
            HTML with background image injected into the placeholder
        """
        if not background_image:
            return html_content

        # Find the placeholder div and add background-image style
        # Pattern matches: <div style="position: absolute; inset: 0; background-size: cover; background-position: center;">
        placeholder_pattern = r'(<div style="position: absolute; inset: 0; background-size: cover; background-position: center;)(">)'
        replacement = rf"\1 background-image: url('{background_image}');\2"

        result = re.sub(placeholder_pattern, replacement, html_content)

        # If the pattern wasn't found (LLM generated different HTML), wrap the whole thing
        if result == html_content:
            logger.warning("Placeholder div not found, wrapping entire content with background image")
            return f'''<div style="position: relative; width: 100%; height: 100%; background-image: url('{background_image}'); background-size: cover; background-position: center;">
{html_content}
</div>'''

        return result

    @property
    def slide_type(self) -> str:
        """Return slide type identifier."""
        return "closing_slide_with_image"

    def _build_image_prompt(
        self,
        request: HeroGenerationRequest
    ) -> tuple[str, str]:
        """
        Build style-aware image generation prompt for closing slide.

        Creates an inspiring, forward-looking background suitable for the RIGHT side
        of split-layout closing slide, with visual style support.

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

        # Use centralized domain detection from style_config
        combined_text = f"{narrative} {' '.join(topics) if topics else ''}".lower()
        domain_imagery = get_domain_theme(style_config, combined_text)

        # Add closing-specific hopeful/inspiring modifiers
        closing_imagery = f"inspiring {domain_imagery}, hopeful future, achievement and success"

        # Build style-aware image prompt with STRONG topic focus
        topic_focus = ', '.join(topics[:2]) if topics else 'future success and opportunity'

        prompt = f"""High-quality {visual_style} inspirational closing slide background: {closing_imagery}.

Style: {style_config.prompt_style}, uplifting
Composition: Professional and balanced, suitable for RIGHT side of split layout
Mood: Forward-looking, positive, successful, hopeful
Lighting: Natural, bright but not harsh, optimistic

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
            "professional": "polished and aspirational",
            "bold": "powerful and confident",
            "warm": "optimistic and inviting",
            "minimal": "clean and hopeful",
            "tech": "innovative and future-focused",
            "creative": "inspiring and transformative"
        }
        return styles.get(theme.lower(), "professional and motivating")

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for closing slide with split-layout design.

        LEFT column: text content (eyebrow, title, description, contact)
        RIGHT column: image with gradient overlay

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
        contact_info = request.context.get("contact_info", "")
        narrative = request.narrative
        topics = request.topics

        # v1.3.0: Extract theme_config for dynamic styling
        theme_config = request.context.get("theme_config")
        content_context = request.context.get("content_context")

        # v1.3.0: Extract typography from theme_config with defaults
        if theme_config and "typography" in theme_config:
            typo = theme_config["typography"]
            hero_title = typo.get("hero_title", {})
            title_size_px = hero_title.get("size", 88)
            title_size = f"{title_size_px / 16:.2f}rem"
            title_weight = hero_title.get("weight", 700)
            hero_subtitle = typo.get("hero_subtitle", typo.get("slide_title", {}))
            desc_size_px = hero_subtitle.get("size", 34)
            desc_size = f"{desc_size_px / 16:.2f}rem"
        else:
            title_size, title_weight = "5.5rem", 700
            desc_size = "2.1rem"

        # v1.3.0: Extract accent colors from theme_config
        if theme_config and "colors" in theme_config:
            colors = theme_config["colors"]
            accent = colors.get("accent", "#00d9ff")
            background_dark = colors.get("surface_dark", "#0b0f19")
        else:
            accent = "#00d9ff"
            background_dark = "#0b0f19"

        # v1.3.0: Build audience context section
        context_section = ""
        if content_context:
            audience_info = content_context.get("audience", {})
            purpose_info = content_context.get("purpose", {})
            audience_type = audience_info.get("audience_type", "professional")
            complexity = audience_info.get("complexity_level", "moderate")
            purpose_type = purpose_info.get("purpose_type", "inform")
            include_cta = purpose_info.get("include_cta", True)

            context_section = f"""
## 📊 AUDIENCE & PURPOSE
- **Audience**: {audience_type} ({complexity} complexity)
- **Purpose**: {purpose_type}
- **Language**: Adapt vocabulary and tone for {audience_type} audience
- **Include CTA**: {"Yes - emphasize call to action" if include_cta else "Focus on thank you and summary"}
"""

        # Build prompt with split-layout design
        prompt = f"""Generate HTML content for a MODERN CLOSING SLIDE with SPLIT LAYOUT.
{context_section}

## 🎯 Slide Purpose
**Function**: Final slide with strong visual impact and clear call-to-action
**Layout**: LEFT text column + RIGHT image column
**Word Count**: 60-80 words total

## 📋 Content Requirements

1. **Eyebrow Text** (2-4 words, uppercase)
   - Small text above main title
   - Category or section label
   - Examples: "NEXT STEPS", "GET STARTED", "READY TO BEGIN"
   - Derives from context and narrative

2. **Main Title** (6-10 words)
   - Compelling closing statement or question
   - Action-oriented and inspiring
   - Question format works well: "Ready to Transform Your Healthcare?"
   - Or statement: "Let's Build the Future Together"
   - Based on: {narrative}

3. **Description** (20-30 words)
   - Value proposition summary
   - Key benefits from topics: {', '.join(topics) if topics else 'N/A'}
   - What they gain by taking action
   - Brief and compelling

4. **Contact Information**
   - Email address (professional)
   - Website/LinkedIn URL
   {f"- Use provided: {contact_info}" if contact_info else ""}

## 🎨 MANDATORY STYLING (Professional Dark Theme)

### Layout Structure (EXACT):
- Container: display: flex; width: 100%; height: 100%; background: {background_dark}
- LEFT column (flex: 1): Text content, padding: 8% 6%
- RIGHT column (flex: 1.1): Image with gradient overlay

### Typography (Inter font, fixed sizes for reveal.js scaling):
- Eyebrow: font-size: 1.6rem; letter-spacing: 0.15em; color: {accent}
- Title: font-size: {title_size}; font-weight: {title_weight}; color: #ffffff
- Description: font-size: {desc_size}; font-weight: 300; color: rgba(255,255,255,0.8)
- Contact: font-size: 1.6rem; font-weight: 400; color: rgba(255,255,255,0.9)

### Visual Elements:
- Eyebrow has accent ::before line (width: 50px, height: 3px, background: {accent})
- Contact info in rounded boxes with icons (circular backgrounds)
- Icon circles: width: 44px; height: 44px; border-radius: 50%; background: rgba(0,217,255,0.1)
- Use Font Awesome icons (fa-envelope, fa-linkedin)

## ✨ EXACT TEMPLATE (Use this structure):
```html
<div style="display: flex; width: 100%; height: 100%; background: {background_dark}; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">

  <!-- LEFT COLUMN: Text Content -->
  <div style="flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 8% 6%; color: #ffffff;">

    <!-- Eyebrow with decorative line -->
    <div style="position: relative; display: inline-block; margin-bottom: 24px;">
      <div style="position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 50px; height: 3px; background: {accent}; margin-right: 15px;"></div>
      <span style="padding-left: 65px; font-size: 1.6rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; color: {accent};">
        NEXT STEPS
      </span>
    </div>

    <!-- Main Title -->
    <h1 style="font-size: {title_size}; font-weight: {title_weight}; line-height: 1.1; margin: 0 0 28px 0; color: #ffffff; max-width: 90%;">
      Ready to Transform Your Healthcare?
    </h1>

    <!-- Description -->
    <p style="font-size: {desc_size}; font-weight: 300; line-height: 1.6; color: rgba(255,255,255,0.8); margin: 0 0 48px 0; max-width: 85%;">
      Join leading organizations using AI-powered diagnostics to improve patient outcomes and reduce costs.
    </p>

    <!-- Contact Box -->
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <!-- Email -->
      <div style="display: flex; align-items: center; gap: 12px;">
        <div style="width: 52px; height: 52px; border-radius: 50%; background: rgba(0,217,255,0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
          <i class="fa-solid fa-envelope" style="color: {accent}; font-size: 26px;"></i>
        </div>
        <span style="font-size: 1.6rem; font-weight: 400; color: rgba(255,255,255,0.9);">
          contact@company.com
        </span>
      </div>

      <!-- LinkedIn -->
      <div style="display: flex; align-items: center; gap: 12px;">
        <div style="width: 52px; height: 52px; border-radius: 50%; background: rgba(0,217,255,0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
          <i class="fa-brands fa-linkedin" style="color: {accent}; font-size: 26px;"></i>
        </div>
        <span style="font-size: 1.6rem; font-weight: 400; color: rgba(255,255,255,0.9);">
          linkedin.com/company/yourcompany
        </span>
      </div>
    </div>

  </div>

  <!-- RIGHT COLUMN: Image with Gradient Overlay -->
  <div style="flex: 1.1; position: relative; overflow: hidden;">
    <!-- Placeholder for background image (will be injected) -->
    <div style="position: absolute; inset: 0; background-size: cover; background-position: center;"></div>

    <!-- Gradient overlay for smooth transition from left -->
    <div style="position: absolute; inset: 0; background: linear-gradient(90deg, {background_dark} 0%, rgba(11,15,25,0.3) 20%, transparent 40%);"></div>
  </div>

</div>

<!-- Font Awesome (required for icons) -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

## 📤 OUTPUT INSTRUCTIONS
- Return ONLY the HTML (NO code blocks, NO explanations)
- Use EXACT structure above with split layout
- LEFT column: eyebrow + title + description + contact
- RIGHT column: image placeholder with gradient overlay
- Must include Font Awesome link at bottom
- Accent color ({accent}) for eyebrow and icons
- Dark background ({background_dark})
- Contact info with icon circles (fa-envelope, fa-linkedin)
- Replace placeholder contact info with contextually appropriate details
- Use typography sizes: title {title_size}, description {desc_size}

**Content Inputs**:
Narrative: {narrative}
Topics: {', '.join(topics) if topics else 'N/A'}
Theme: {theme}
Audience: {audience}

Generate the professional split-layout closing slide HTML NOW:"""

        return prompt

    async def generate(
        self,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate closing slide with background image.

        Runs image generation and content generation in parallel for performance.
        Falls back gracefully to gradient background if image generation fails.

        Args:
            request: Hero generation request

        Returns:
            Generation result with content, metadata, and background_image URL
        """
        logger.info(
            f"Generating closing slide with background image "
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
                f"Closing slide with image generated successfully "
                f"(fallback: {fallback_to_gradient})"
            )

            return response

        except Exception as e:
            logger.error(f"Closing slide with image generation failed: {e}")
            raise

    async def _generate_image_with_retry(
        self,
        prompt: str,
        archetype: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate background image with style-aware configuration.

        Closing slides ALWAYS use fast model regardless of visual style
        to optimize cost for final slides.

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
            "slide_type": "closing_slide",
            "slide_number": request.slide_number,
            "narrative": request.narrative[:100],  # Truncate for storage
            "visual_style": request.visual_style,
            # Semantic cache fields
            "topics": request.topics[:5] if request.topics else [],  # Top 5 topics
            "domain": domain
        }

        # Closing slides always use fast model (all styles)
        model = get_image_model(request.slide_type, request.visual_style)

        return await self.image_client.generate_background_image(
            prompt=prompt,
            slide_type=SlideType.CLOSING,
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
        Validate closing slide with split-layout design.

        Extends parent validation to check for split-layout structure,
        Font Awesome icons, and dark theme.

        Args:
            content: Generated HTML content
            request: Original request for context

        Returns:
            Validation result dictionary
        """
        # Run parent validation
        validation = super()._validate_output(content, request)

        # Additional checks for split-layout variant
        warnings = validation.get("warnings", [])
        violations = validation.get("violations", [])

        # Check for split layout (flex container)
        has_flex_layout = bool(
            re.search(r'display:\s*flex', content, re.IGNORECASE)
        )
        if not has_flex_layout:
            warnings.append(
                "Should use display: flex for split-layout closing slide"
            )

        # Check for dark background (#0b0f19)
        has_dark_bg = bool(
            re.search(r'background:\s*#0b0f19', content, re.IGNORECASE)
        )
        if not has_dark_bg:
            warnings.append(
                "Should use dark background (#0b0f19) for modern closing slide"
            )

        # Check for Font Awesome link
        has_fontawesome = bool(
            re.search(r'font-awesome|fontawesome\.com', content, re.IGNORECASE)
        )
        if not has_fontawesome:
            warnings.append(
                "Should include Font Awesome for icon support"
            )

        # Check for LEFT and RIGHT columns (flex: 1 or flex: 1.1)
        has_columns = bool(
            re.search(r'flex:\s*1[\.;]', content, re.IGNORECASE)
        )
        if not has_columns:
            warnings.append(
                "Should have LEFT and RIGHT columns with flex sizing"
            )

        validation["warnings"] = warnings
        validation["violations"] = violations

        return validation
