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

        # Build rich prompt based on v1.1 world-class template
        prompt = f"""Generate HTML content for a CLOSING SLIDE (L29 Hero Layout).

## 🎯 Slide Purpose
**Cognitive Function**: Drive action with clear next steps and contact info
**When to Use**: Final slide ONLY - lasting impression
**Word Count Target**: 65-85 words total

## 📋 Content Requirements

1. **Closing Message** (5-8 words)
   - Thank you OR key takeaway
   - Memorable summary
   - Positive and actionable
   - Question format recommended: "Ready to Transform Your Business?"
   - Or statement: "Your Success Starts Here"
   - Derive from: {narrative}

2. **Supporting Text** (15-25 words)
   - Value proposition recap
   - Results or benefits summary from topics: {', '.join(topics) if topics else 'N/A'}
   - Next steps or opportunity
   - Why they should act

3. **Call-to-Action Button** (3-5 words, REQUIRED)
   - Clear action: "Schedule Demo", "Contact Us", "Get Started"
   - Prominent button styling with white background
   - Easy to read and click

4. **Contact Information** (3-5 items)
   - Email address
   - Website URL
   - Phone number (optional)
   - Format: "email | website | phone"
   {f"- Use provided contact: {contact_info}" if contact_info else ""}

## 🎨 MANDATORY Styling (CRITICAL - DO NOT SKIP)

### Typography (EXACT sizes required):
- Closing Message: font-size: 72px; font-weight: 700
- Supporting Text: font-size: 36px; font-weight: 400
- CTA Button: font-size: 32px; font-weight: 700
- Contact Info: font-size: 28px; font-weight: 400

### Visual Requirements (ALL REQUIRED):
- ✅ Gradient background (choose from options below)
- ✅ White text color on all elements
- ✅ Text shadows on ALL text (0 4px 12px rgba for h2)
- ✅ Center alignment (text-align: center)
- ✅ CTA button: white background, colored text matching gradient
- ✅ Button shadow: 0 8px 24px rgba(0,0,0,0.3)
- ✅ Generous spacing (48-64px between elements)
- ✅ 80px padding around edges

### Layout (EXACT structure):
- Full-screen: width: 100%; height: 100%
- Flexbox centered: display: flex; justify-content: center; align-items: center
- Vertical stack: flex-direction: column

### CTA Button Requirements (CRITICAL):
padding: 32px 72px;
background: white;
color: #667eea;  /* Matches gradient */
border-radius: 12px;
box-shadow: 0 8px 24px rgba(0,0,0,0.3);
font-weight: 700;

## 🎨 Gradient Options (Choose based on theme: {theme}):
Professional: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)
Bold/Modern: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Warm: linear-gradient(135deg, #ffa751 0%, #ffe259 100%)
Deep Navy: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)

## ✨ GOLDEN EXAMPLE (Follow this EXACTLY):
```html
<div style="width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 80px;">

  <h2 style="font-size: 72px;
             color: white;
             font-weight: 700;
             text-align: center;
             margin: 0 0 48px 0;
             line-height: 1.2;
             text-shadow: 0 4px 12px rgba(0,0,0,0.3);">
    Ready to Transform Your Operations?
  </h2>

  <p style="font-size: 36px;
            color: rgba(255,255,255,0.95);
            text-align: center;
            max-width: 1400px;
            line-height: 1.6;
            margin: 0 0 56px 0;
            text-shadow: 0 2px 8px rgba(0,0,0,0.2);">
    Join 500+ organizations using AI to reduce costs, increase efficiency, and deliver superior customer experiences. Let's discuss your specific use cases and ROI opportunities.
  </p>

  <div style="padding: 32px 72px;
              font-size: 32px;
              background: white;
              color: #667eea;
              border-radius: 12px;
              font-weight: 700;
              box-shadow: 0 8px 24px rgba(0,0,0,0.3);
              margin-bottom: 48px;">
    Schedule Your Demo Today
  </div>

  <div style="font-size: 28px;
              color: rgba(255,255,255,0.9);
              text-align: center;
              text-shadow: 0 2px 6px rgba(0,0,0,0.2);">
    contact@aiplatform.com | www.aiplatform.com | 1-800-AI-TRANSFORM
  </div>

</div>
```

## 📤 OUTPUT INSTRUCTIONS
- Return ONLY complete inline-styled HTML (like example above)
- NO markdown code blocks (```html)
- NO explanations or comments
- MUST include ALL inline styles shown
- MUST use gradient background
- MUST use large font sizes (72px/36px/32px/28px)
- MUST include white CTA button with colored text
- Word count target: 65-85 words

**Content Inputs**:
Narrative: {narrative}
Topics: {', '.join(topics) if topics else 'N/A'}
Theme: {theme}
Audience: {audience}

Generate the closing slide HTML NOW with ALL styling inline:"""

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

        # Check for required inline-styled structure (v1.1-style)
        has_container = bool(re.search(r'<div[^>]*style=.*linear-gradient', content, re.DOTALL))
        has_message = bool(re.search(r'<h2[^>]*style=.*font-size:\s*72px', content, re.DOTALL))
        has_cta = bool(re.search(r'<div[^>]*style=.*font-size:\s*32px.*background:\s*white', content, re.DOTALL))
        has_contact = bool(re.search(r'<div[^>]*style=.*font-size:\s*28px', content, re.DOTALL))

        if not has_container:
            violations.append("Missing gradient background div container")
        if not has_message:
            violations.append("Missing 72px h2 closing message element")
        if not has_cta:
            warnings.append("Missing 32px white CTA button element (recommended)")
        if not has_contact:
            warnings.append("Missing 28px contact info element (recommended)")

        # Extract and validate text lengths (match by tag and inline styles)
        message_text = self._extract_text_from_html(
            content,
            r'<h2[^>]*>(.*?)</h2>'
        )
        cta_text = self._extract_text_from_html(
            content,
            r'<div[^>]*style=.*font-size:\s*32px.*background:\s*white[^>]*>(.*?)</div>'
        )
        contact_text = self._extract_text_from_html(
            content,
            r'<div[^>]*style=.*font-size:\s*28px[^>]*>(.*?)</div>'
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
