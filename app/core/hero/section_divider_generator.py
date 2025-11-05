"""
Section Divider Generator (L29 Hero Layout)

Generates content for section transition slides using L29 hero layout.
Adapted from v1.1's SectionDividerGenerator with async support for v1.2.

Layout: L29 Full-Bleed Hero
Model: Flash (gemini-2.0-flash-exp)
Complexity: Simple

Purpose:
- Transition between major presentation sections
- Clear topic shift marker
- Brief context for upcoming section

HTML Structure:
<div class="section-divider">
  <h2 class="section-title">Section Name</h2>
  <p class="section-description">Brief description of upcoming content</p>
</div>

Constraints:
- Section title: 40-60 characters (clear section name)
- Section description: 80-120 characters (what's coming next)
"""

from typing import Dict, Any
import re
import logging
from .base_hero_generator import BaseHeroGenerator, HeroGenerationRequest

logger = logging.getLogger(__name__)


class SectionDividerGenerator(BaseHeroGenerator):
    """
    Section divider generator for L29 hero layout.

    Generates complete HTML structure for section transitions with:
    - Section title (h2)
    - Section description/preview (p)
    """

    @property
    def slide_type(self) -> str:
        """Return slide type identifier."""
        return "section_divider"

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for section divider generation.

        Creates a comprehensive prompt that instructs the LLM to generate
        a section transition slide with proper HTML structure and constraints.

        Args:
            request: Hero generation request with narrative and context

        Returns:
            Complete LLM prompt string
        """
        # Extract context
        theme = request.context.get("theme", "professional")
        audience = request.context.get("audience", "general business audience")
        narrative = request.narrative
        topics = request.topics

        # Build prompt
        prompt = f"""Generate HTML content for a section divider slide (L29 hero layout).

**Slide Purpose**: Transition slide marking the start of a new major section

**Content Guidelines**:
- Section Title: Clear, concise name for the upcoming section
- Section Description: Brief preview of what's covered in this section

**Constraints** (STRICT):
- Section title: 40-60 characters (punchy and clear)
- Section description: 80-120 characters (preview without details)

**HTML Structure** (EXACTLY this format):
```html
<div class="section-divider">
  <h2 class="section-title">Section Name</h2>
  <p class="section-description">Brief description of upcoming content</p>
</div>
```

**Content Inputs**:
Narrative: {narrative}
Key Topics: {', '.join(topics) if topics else 'N/A'}
Theme: {theme}
Audience: {audience}

**Tone Requirements**:
- Clear and confident
- Builds anticipation for upcoming content
- Maintains momentum from previous section
- Aligned with {theme} theme
- Appropriate for {audience}

**Important**:
- Return ONLY the HTML structure above
- NO explanations, markdown code blocks, or extra text
- Use the exact CSS class names shown
- Keep within character limits
- Make the transition smooth and engaging

Generate the section divider HTML now:"""

        return prompt

    def _validate_output(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate section divider content structure and character counts.

        Checks for:
        - Required HTML structure (div.section-divider, h2.section-title, p.section-description)
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
        has_container = bool(re.search(r'<div[^>]*class=["\']section-divider["\']', content))
        has_title = bool(re.search(r'<h2[^>]*class=["\']section-title["\']', content))
        has_description = bool(re.search(r'<p[^>]*class=["\']section-description["\']', content))

        if not has_container:
            violations.append("Missing section-divider div container")
        if not has_title:
            violations.append("Missing section-title h2 element")
        if not has_description:
            violations.append("Missing section-description p element")

        # Extract and validate text lengths
        title_text = self._extract_text_from_html(
            content,
            r'<h2[^>]*class=["\']section-title["\'][^>]*>(.*?)</h2>'
        )
        description_text = self._extract_text_from_html(
            content,
            r'<p[^>]*class=["\']section-description["\'][^>]*>(.*?)</p>'
        )

        # Validate section title
        if title_text:
            title_len = self._count_characters(title_text)
            metrics["title_length"] = title_len

            if title_len < 15:
                warnings.append(
                    f"Section title is short: {title_len} chars (recommended: 40-60)"
                )
            elif title_len > 80:
                violations.append(
                    f"Section title too long: {title_len} chars (max: 80)"
                )
            elif title_len > 60:
                warnings.append(
                    f"Section title slightly long: {title_len} chars (recommended: 40-60)"
                )

        # Validate section description
        if description_text:
            description_len = self._count_characters(description_text)
            metrics["description_length"] = description_len

            if description_len < 40:
                warnings.append(
                    f"Section description is short: {description_len} chars (recommended: 80-120)"
                )
            elif description_len > 150:
                violations.append(
                    f"Section description too long: {description_len} chars (max: 150)"
                )
            elif description_len > 120:
                warnings.append(
                    f"Section description slightly long: {description_len} chars (recommended: 80-120)"
                )

        # Check for common quality issues
        if title_text:
            title_lower = title_text.lower()
            if "section" in title_lower and len(title_text) < 20:
                warnings.append("Section title appears generic (just 'Section X')")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "metrics": metrics
        }
