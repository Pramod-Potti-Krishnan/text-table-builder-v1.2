"""
Title Slide Generator (L29 Hero Layout)

Generates content for opening/title slides using L29 hero layout.
Adapted from v1.1's TitleSlideGenerator with async support for v1.2.

Layout: L29 Full-Bleed Hero
Model: Flash (gemini-2.0-flash-exp)
Complexity: Simple

Purpose:
- Opening slide for presentations
- Main title + compelling subtitle
- Presenter attribution (name, company, date)

HTML Structure:
<div class="title-slide">
  <h1 class="main-title">Presentation Title</h1>
  <p class="subtitle">Compelling subtitle or value proposition</p>
  <p class="attribution">Presenter | Company | Date</p>
</div>

Constraints:
- Main title: 40-80 characters (punchy and memorable)
- Subtitle: 80-120 characters (compelling value proposition)
- Attribution: 60-100 characters (presenter + company + date)

Version: 1.3.0 - Added theme_config and content_context support
"""

from typing import Dict, Any
import re
import logging
from .base_hero_generator import BaseHeroGenerator, HeroGenerationRequest

logger = logging.getLogger(__name__)


class TitleSlideGenerator(BaseHeroGenerator):
    """
    Title slide generator for L29 hero layout.

    Generates complete HTML structure for opening slides with:
    - Main presentation title (h1)
    - Compelling subtitle (p)
    - Presenter attribution (p)
    """

    @property
    def slide_type(self) -> str:
        """Return slide type identifier."""
        return "title_slide"

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for title slide generation.

        Creates a comprehensive prompt that instructs the LLM to generate
        a title slide with proper HTML structure and character constraints.

        v1.3.0: Uses theme_config for dynamic typography and content_context
        for audience-adapted language when available.

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

        # v1.3.0: Extract theme_config for dynamic typography
        theme_config = request.context.get("theme_config")
        content_context = request.context.get("content_context")

        # Extract typography from theme_config with defaults
        if theme_config and "typography" in theme_config:
            typo = theme_config["typography"]
            hero_title = typo.get("hero_title", {})
            title_size = hero_title.get("size", 96)
            title_weight = hero_title.get("weight", 900)
            hero_subtitle = typo.get("hero_subtitle", typo.get("slide_title", {}))
            subtitle_size = hero_subtitle.get("size", 42)
            subtitle_weight = hero_subtitle.get("weight", 400)
        else:
            title_size, title_weight = 96, 900
            subtitle_size, subtitle_weight = 42, 400

        # Extract colors from theme_config
        if theme_config and "colors" in theme_config:
            colors = theme_config["colors"]
            primary = colors.get("primary", "#667eea")
            secondary = colors.get("secondary", "#764ba2")
            gradient = f"linear-gradient(135deg, {primary} 0%, {secondary} 100%)"
        else:
            gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

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
- **Avoid jargon**: {"Yes" if audience_info.get("avoid_jargon") else "Use professional terminology as appropriate"}
"""

        # Build rich prompt based on v1.1 world-class template
        prompt = f"""Generate HTML content for a TITLE SLIDE (L29 Hero Layout).

## 🎯 Slide Purpose
**Cognitive Function**: Set presentation tone with elegant simplicity
**When to Use**: Opening slide ONLY - first impression
**Word Count Target**: 40-60 words total
{context_section}
## 📋 Content Requirements

1. **Main Title** (5-10 words)
   - Core presentation topic - clear and memorable
   {f"- Use this title if appropriate: '{presentation_title}'" if presentation_title else ""}
   - Otherwise derive from narrative: {narrative}

2. **Subtitle** (10-15 words)
   - Compelling tagline or value proposition
   - What the presentation delivers
   - Key theme or benefit

3. **Attribution** (3-5 elements)
   - Format: "Presenter | Company | Date"
   - Professional and complete

## 🎨 MANDATORY Styling (CRITICAL - DO NOT SKIP)

### Typography (EXACT sizes required):
- Title: font-size: {title_size}px; font-weight: {title_weight}; letter-spacing: -2px
- Subtitle: font-size: {subtitle_size}px; font-weight: {subtitle_weight}
- Attribution: font-size: 32px; font-weight: 400

### Visual Requirements (ALL REQUIRED):
- ✅ Gradient background: {gradient}
- ✅ White text color on all elements
- ✅ Text shadows on ALL text (0 4px 12px rgba(0,0,0,0.3) for title)
- ✅ Center alignment (text-align: center)
- ✅ Generous vertical spacing (40-64px between elements)
- ✅ 80px padding around edges

### Layout (EXACT structure):
- Full-screen: width: 100%; height: 100%
- Flexbox centered: display: flex; justify-content: center; align-items: center
- Vertical stack: flex-direction: column

## ✨ GOLDEN EXAMPLE (Follow this EXACTLY):
```html
<div style="width: 100%;
            height: 100%;
            background: {gradient};
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 80px;">

  <h1 style="font-size: {title_size}px;
             color: white;
             font-weight: {title_weight};
             text-align: center;
             margin: 0 0 40px 0;
             text-shadow: 0 4px 12px rgba(0,0,0,0.3);
             line-height: 1.1;
             letter-spacing: -2px;">
    Your Catchy Title Here
  </h1>

  <p style="font-size: {subtitle_size}px;
            color: rgba(255,255,255,0.95);
            text-align: center;
            margin: 0 0 64px 0;
            line-height: 1.4;
            text-shadow: 0 2px 8px rgba(0,0,0,0.2);">
    Your Compelling Subtitle About Value
  </p>

  <div style="font-size: 32px;
              color: rgba(255,255,255,0.9);
              text-align: center;
              text-shadow: 0 2px 6px rgba(0,0,0,0.2);">
    Presenter Name | Company Name | Date
  </div>

</div>
```

## 📤 OUTPUT INSTRUCTIONS
- Return ONLY complete inline-styled HTML (like example above)
- NO markdown code blocks (```html)
- NO explanations or comments
- MUST include ALL inline styles shown
- MUST use gradient background
- MUST use the exact font sizes shown ({title_size}px/{subtitle_size}px/32px)

**Content Inputs**:
Narrative: {narrative}
Topics: {', '.join(topics) if topics else 'N/A'}
Theme: {theme}
Audience: {audience}

Generate the title slide HTML NOW with ALL styling inline:"""

        return prompt

    def _validate_output(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate title slide content structure and character counts.

        Checks for:
        - Required HTML structure (div.title-slide, h1.main-title, p.subtitle, p.attribution)
        - Character count constraints
        - Text content quality

        Args:
            content: Generated HTML content
            request: Original request for context

        Returns:
            Validation result dictionary
        """
        violations = []
        warnings = []
        metrics = {}

        # Check for required inline-styled structure (v1.1-style)
        has_container = bool(re.search(r'<div[^>]*style=.*linear-gradient', content, re.DOTALL))
        has_title = bool(re.search(r'<h1[^>]*style=.*font-size:\s*96px', content, re.DOTALL))
        has_subtitle = bool(re.search(r'<p[^>]*style=.*font-size:\s*42px', content, re.DOTALL))
        has_attribution = bool(re.search(r'<div[^>]*style=.*font-size:\s*32px', content, re.DOTALL))

        if not has_container:
            violations.append("Missing gradient background div container")
        if not has_title:
            violations.append("Missing 96px h1 title element")
        if not has_subtitle:
            violations.append("Missing 42px p subtitle element")
        if not has_attribution:
            warnings.append("Missing 32px attribution element (recommended)")

        # Extract and validate text lengths (match by tag and inline styles)
        title_match = re.search(
            r'<h1[^>]*>(.*?)</h1>',
            content,
            re.DOTALL
        )
        subtitle_match = re.search(
            r'<p[^>]*style=.*font-size:\s*42px[^>]*>(.*?)</p>',
            content,
            re.DOTALL
        )
        attribution_match = re.search(
            r'<div[^>]*style=.*font-size:\s*32px[^>]*>(.*?)</div>',
            content,
            re.DOTALL
        )

        # Validate main title
        if title_match:
            title_text = self._extract_text_from_html(
                content,
                r'<h1[^>]*>(.*?)</h1>'
            )
            title_len = self._count_characters(title_text)
            metrics["title_length"] = title_len

            if title_len < 20:
                warnings.append(
                    f"Main title is short: {title_len} chars (recommended: 40-80)"
                )
            elif title_len > 100:
                violations.append(
                    f"Main title too long: {title_len} chars (max: 100)"
                )
            elif title_len > 80:
                warnings.append(
                    f"Main title slightly long: {title_len} chars (recommended: 40-80)"
                )

        # Validate subtitle
        if subtitle_match:
            subtitle_text = self._extract_text_from_html(
                content,
                r'<p[^>]*style=.*font-size:\s*42px[^>]*>(.*?)</p>'
            )
            subtitle_len = self._count_characters(subtitle_text)
            metrics["subtitle_length"] = subtitle_len

            if subtitle_len < 40:
                warnings.append(
                    f"Subtitle is short: {subtitle_len} chars (recommended: 80-120)"
                )
            elif subtitle_len > 150:
                violations.append(
                    f"Subtitle too long: {subtitle_len} chars (max: 150)"
                )
            elif subtitle_len > 120:
                warnings.append(
                    f"Subtitle slightly long: {subtitle_len} chars (recommended: 80-120)"
                )

        # Validate attribution
        if attribution_match:
            attribution_text = self._extract_text_from_html(
                content,
                r'<div[^>]*style=.*font-size:\s*32px[^>]*>(.*?)</div>'
            )
            attribution_len = self._count_characters(attribution_text)
            metrics["attribution_length"] = attribution_len

            if attribution_len > 120:
                violations.append(
                    f"Attribution too long: {attribution_len} chars (max: 120)"
                )

        # Check for common quality issues
        if title_match:
            title_lower = title_text.lower()
            if "untitled" in title_lower or "placeholder" in title_lower:
                warnings.append("Title appears to be a placeholder")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "metrics": metrics
        }
