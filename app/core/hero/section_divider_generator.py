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

        # Build rich prompt based on v1.1 world-class template
        prompt = f"""Generate HTML content for a SECTION DIVIDER SLIDE (L29 Hero Layout).

## 🎯 Slide Purpose
**Cognitive Function**: Signal topic transition with minimal distraction
**When to Use**: Between major presentation sections
**Word Count Target**: 25-45 words total

## 📋 Content Requirements

1. **Section Title** (3-6 words)
   - New topic or phase name
   - Clear and bold
   - Derive from: {narrative}
   - Or use first topic if relevant: {topics[0] if topics else 'N/A'}

2. **Context Text** (5-10 words, optional)
   - Brief explanation of what's coming
   - Transition phrase
   - Can be omitted for ultra-minimal look

## 🎨 MANDATORY Styling (CRITICAL - DO NOT SKIP)

### Typography (EXACT sizes required):
- Section Title: font-size: 84px; font-weight: 700
- Context Text: font-size: 42px; font-weight: 400; color: #9ca3af (muted gray)

### Visual Requirements (ALL REQUIRED):
- ✅ Dark solid background (#1f2937) - creates contrast
- ✅ Colored left border accent (12px wide)
- ✅ White text color for title
- ✅ Muted gray (#9ca3af) for context text
- ✅ Left-aligned text block (NOT centered)
- ✅ Padding-left: 48px (text offset from border)

### Layout (EXACT structure):
- Full-screen: width: 100%; height: 100%
- Flexbox centered vertically: display: flex; align-items: center; justify-content: center
- Content block has left border accent

## 🎨 Border Color Options (Choose based on section theme):
Strategy/Planning: border-left: 12px solid #667eea (Purple)
Execution/Action: border-left: 12px solid #1a73e8 (Blue)
Results/Success: border-left: 12px solid #34a853 (Green)
Innovation: border-left: 12px solid #9333ea (Deep Purple)

## ✨ GOLDEN EXAMPLE (Follow this EXACTLY):
```html
<div style="width: 100%;
            height: 100%;
            background: #1f2937;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 80px;">

  <div style="border-left: 12px solid #667eea;
              padding-left: 48px;">

    <h2 style="font-size: 84px;
               color: white;
               font-weight: 700;
               margin: 0 0 24px 0;
               line-height: 1.1;">
      Implementation Roadmap
    </h2>

    <p style="font-size: 42px;
              color: #9ca3af;
              font-weight: 400;
              margin: 0;
              line-height: 1.3;">
      From Planning to Full Deployment
    </p>

  </div>

</div>
```

## 📤 OUTPUT INSTRUCTIONS
- Return ONLY complete inline-styled HTML (like example above)
- NO markdown code blocks (```html)
- NO explanations or comments
- MUST include ALL inline styles shown
- MUST use dark background (#1f2937)
- MUST use left border accent (12px solid color)
- MUST use large font size (84px for title)
- Context text MUST be muted gray (#9ca3af)

**Content Inputs**:
Narrative: {narrative}
Topics: {', '.join(topics) if topics else 'N/A'}
Theme: {theme}
Audience: {audience}

Generate the section divider HTML NOW with ALL styling inline:"""

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

        # Check for required inline-styled structure (v1.1-style)
        has_container = bool(re.search(r'<div[^>]*style=.*background:\s*#1f2937', content, re.DOTALL))
        has_title = bool(re.search(r'<h2[^>]*style=.*font-size:\s*84px', content, re.DOTALL))
        has_description = bool(re.search(r'<p[^>]*style=.*font-size:\s*42px', content, re.DOTALL))

        if not has_container:
            violations.append("Missing dark background (#1f2937) div container")
        if not has_title:
            violations.append("Missing 84px h2 section title element")
        if not has_description:
            violations.append("Missing 42px p context description element")

        # Extract and validate text lengths (match by tag and inline styles)
        title_text = self._extract_text_from_html(
            content,
            r'<h2[^>]*>(.*?)</h2>'
        )
        description_text = self._extract_text_from_html(
            content,
            r'<p[^>]*style=.*font-size:\s*42px[^>]*>(.*?)</p>'
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
