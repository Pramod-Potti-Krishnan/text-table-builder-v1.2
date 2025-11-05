"""
Closing Slide Generator (L29 Hero Layout)

Generates content for closing/conclusion slides using L29 hero layout.
Adapted from v1.1's ClosingSlideGenerator with async support for v1.2.

Layout: L29 Full-Bleed Hero
Model: Flash (gemini-2.0-flash-exp)
Complexity: Simple

Purpose:
- Conclusion and thank you
- Key takeaway or call-to-action
- Contact information

HTML Structure:
<div class="closing-slide">
  <h2 class="closing-message">Thank You + Key Takeaway</h2>
  <p class="call-to-action">What's next for the audience</p>
  <p class="contact-info">presenter@email.com | website.com</p>
</div>

Constraints:
- Closing message: 50-80 characters (thank you + takeaway)
- Call-to-action: 80-120 characters (next steps)
- Contact info: 60-100 characters (email, website, or social)
"""

from typing import Dict, Any
import re
import logging
from .base_hero_generator import BaseHeroGenerator, HeroGenerationRequest

logger = logging.getLogger(__name__)


class ClosingSlideGenerator(BaseHeroGenerator):
    """
    Closing slide generator for L29 hero layout.

    Generates complete HTML structure for closing slides with:
    - Closing message/thank you (h2)
    - Call-to-action (p)
    - Contact information (p)
    """

    @property
    def slide_type(self) -> str:
        """Return slide type identifier."""
        return "closing_slide"

    async def _build_prompt(
        self,
        request: HeroGenerationRequest
    ) -> str:
        """
        Build prompt for closing slide generation.

        Creates a comprehensive prompt that instructs the LLM to generate
        a closing slide with proper HTML structure and constraints.

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

        # Build prompt
        prompt = f"""Generate HTML content for a closing slide (L29 hero layout).

**Slide Purpose**: Conclusion slide - thank audience and provide takeaways/next steps

**Content Guidelines**:
- Closing Message: Thank you + key takeaway
- Call-to-Action: What should the audience do next? (optional but recommended)
- Contact Info: How to reach the presenter

**Constraints** (STRICT):
- Closing message: 50-80 characters (gracious and memorable)
- Call-to-action: 80-120 characters (clear next steps)
- Contact info: 60-100 characters (email, website, or social)

**HTML Structure** (EXACTLY this format):
```html
<div class="closing-slide">
  <h2 class="closing-message">Thank You + Key Takeaway</h2>
  <p class="call-to-action">What's next for the audience</p>
  <p class="contact-info">presenter@email.com | website.com</p>
</div>
```

**Content Inputs**:
Narrative: {narrative}
Key Topics: {', '.join(topics) if topics else 'N/A'}
Theme: {theme}
Audience: {audience}
{f"Contact Info Hint: {contact_info}" if contact_info else ""}

**Tone Requirements**:
- Grateful and positive
- Reinforces key takeaways
- Encourages action or engagement
- Leaves lasting impression
- Aligned with {theme} theme
- Appropriate for {audience}

**Important**:
- Return ONLY the HTML structure above
- NO explanations, markdown code blocks, or extra text
- Use the exact CSS class names shown
- Keep within character limits
- Make it memorable and actionable

Generate the closing slide HTML now:"""

        return prompt

    def _validate_output(
        self,
        content: str,
        request: HeroGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate closing slide content structure and character counts.

        Checks for:
        - Required HTML structure (div.closing-slide, h2.closing-message, p.call-to-action, p.contact-info)
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
        has_container = bool(re.search(r'<div[^>]*class=["\']closing-slide["\']', content))
        has_message = bool(re.search(r'<h2[^>]*class=["\']closing-message["\']', content))
        has_cta = bool(re.search(r'<p[^>]*class=["\']call-to-action["\']', content))
        has_contact = bool(re.search(r'<p[^>]*class=["\']contact-info["\']', content))

        if not has_container:
            violations.append("Missing closing-slide div container")
        if not has_message:
            violations.append("Missing closing-message h2 element")
        if not has_cta:
            warnings.append("Missing call-to-action p element (recommended)")
        if not has_contact:
            warnings.append("Missing contact-info p element (recommended)")

        # Extract and validate text lengths
        message_text = self._extract_text_from_html(
            content,
            r'<h2[^>]*class=["\']closing-message["\'][^>]*>(.*?)</h2>'
        )
        cta_text = self._extract_text_from_html(
            content,
            r'<p[^>]*class=["\']call-to-action["\'][^>]*>(.*?)</p>'
        )
        contact_text = self._extract_text_from_html(
            content,
            r'<p[^>]*class=["\']contact-info["\'][^>]*>(.*?)</p>'
        )

        # Validate closing message
        if message_text:
            message_len = self._count_characters(message_text)
            metrics["message_length"] = message_len

            if message_len < 20:
                warnings.append(
                    f"Closing message is short: {message_len} chars (recommended: 50-80)"
                )
            elif message_len > 120:
                violations.append(
                    f"Closing message too long: {message_len} chars (max: 120)"
                )
            elif message_len > 80:
                warnings.append(
                    f"Closing message slightly long: {message_len} chars (recommended: 50-80)"
                )

        # Validate call-to-action
        if cta_text:
            cta_len = self._count_characters(cta_text)
            metrics["cta_length"] = cta_len

            if cta_len < 40:
                warnings.append(
                    f"Call-to-action is short: {cta_len} chars (recommended: 80-120)"
                )
            elif cta_len > 150:
                violations.append(
                    f"Call-to-action too long: {cta_len} chars (max: 150)"
                )
            elif cta_len > 120:
                warnings.append(
                    f"Call-to-action slightly long: {cta_len} chars (recommended: 80-120)"
                )

        # Validate contact info
        if contact_text:
            contact_len = self._count_characters(contact_text)
            metrics["contact_length"] = contact_len

            if contact_len > 120:
                violations.append(
                    f"Contact info too long: {contact_len} chars (max: 120)"
                )

            # Check for email or website pattern
            has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_text))
            has_website = bool(re.search(r'(www\.|https?://)', contact_text, re.IGNORECASE))

            if not has_email and not has_website:
                warnings.append("Contact info should include email or website")

        # Check for common quality issues
        if message_text:
            message_lower = message_text.lower()
            if "thank you" not in message_lower and "thanks" not in message_lower:
                warnings.append("Closing message should include gratitude (e.g., 'Thank You')")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "metrics": metrics
        }
