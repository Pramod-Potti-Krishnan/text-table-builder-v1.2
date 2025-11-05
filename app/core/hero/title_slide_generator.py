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

        # Build prompt
        prompt = f"""Generate HTML content for a title slide (L29 hero layout).

**Slide Purpose**: Opening slide for a presentation - create strong first impression

**Content Guidelines**:
- Main Title: Clear, memorable presentation title (the big idea)
- Subtitle: Compelling value proposition or tagline (why this matters)
- Attribution: Presenter name, company, and date

**Constraints** (STRICT):
- Main title: 40-80 characters (punchy and memorable)
- Subtitle: 80-120 characters (compelling value proposition)
- Attribution: 60-100 characters (presenter + company + date format)

**HTML Structure** (EXACTLY this format):
```html
<div class="title-slide">
  <h1 class="main-title">Main Presentation Title</h1>
  <p class="subtitle">Compelling subtitle or value proposition</p>
  <p class="attribution">Presenter Name | Company | Date</p>
</div>
```

**Content Inputs**:
Narrative: {narrative}
Key Topics: {', '.join(topics) if topics else 'N/A'}
{f"Presentation Title Hint: {presentation_title}" if presentation_title else ""}
Theme: {theme}
Audience: {audience}

**Tone Requirements**:
- Professional and confident
- Clear and impactful
- Aligned with {theme} theme
- Appropriate for {audience}
- Create anticipation and interest

**Important**:
- Return ONLY the HTML structure above
- NO explanations, markdown code blocks, or extra text
- Use the exact CSS class names shown
- Keep within character limits
- Make the title memorable and the subtitle compelling

Generate the title slide HTML now:"""

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

        # Check for required structure
        has_container = bool(re.search(r'<div[^>]*class=["\']title-slide["\']', content))
        has_title = bool(re.search(r'<h1[^>]*class=["\']main-title["\']', content))
        has_subtitle = bool(re.search(r'<p[^>]*class=["\']subtitle["\']', content))
        has_attribution = bool(re.search(r'<p[^>]*class=["\']attribution["\']', content))

        if not has_container:
            violations.append("Missing title-slide div container")
        if not has_title:
            violations.append("Missing main-title h1 element")
        if not has_subtitle:
            violations.append("Missing subtitle p element")
        if not has_attribution:
            warnings.append("Missing attribution p element (recommended)")

        # Extract and validate text lengths
        title_match = re.search(
            r'<h1[^>]*class=["\']main-title["\'][^>]*>(.*?)</h1>',
            content,
            re.DOTALL
        )
        subtitle_match = re.search(
            r'<p[^>]*class=["\']subtitle["\'][^>]*>(.*?)</p>',
            content,
            re.DOTALL
        )
        attribution_match = re.search(
            r'<p[^>]*class=["\']attribution["\'][^>]*>(.*?)</p>',
            content,
            re.DOTALL
        )

        # Validate main title
        if title_match:
            title_text = self._extract_text_from_html(
                content,
                r'<h1[^>]*class=["\']main-title["\'][^>]*>(.*?)</h1>'
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
                r'<p[^>]*class=["\']subtitle["\'][^>]*>(.*?)</p>'
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
                r'<p[^>]*class=["\']attribution["\'][^>]*>(.*?)</p>'
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
