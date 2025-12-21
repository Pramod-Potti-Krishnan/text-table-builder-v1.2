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

Version: 1.3.0 - Added theme_config and content_context support
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

        v1.3.0: Uses theme_config for dynamic typography and colors,
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

        # Extract typography from theme_config with defaults
        if theme_config and "typography" in theme_config:
            typo = theme_config["typography"]
            hero_title = typo.get("hero_title", {})
            closing_size = hero_title.get("size", 72)
            closing_weight = hero_title.get("weight", 700)
            t1 = typo.get("t1", {})
            supporting_size = t1.get("size", 36)
            cta_size = typo.get("t2", {}).get("size", 32)
            contact_size = typo.get("t3", {}).get("size", 28)
        else:
            closing_size, closing_weight = 72, 700
            supporting_size = 36
            cta_size = 32
            contact_size = 28

        # Extract colors from theme_config
        if theme_config and "colors" in theme_config:
            colors = theme_config["colors"]
            primary = colors.get("primary", "#667eea")
            secondary = colors.get("secondary", "#764ba2")
            gradient = f"linear-gradient(135deg, {primary} 0%, {secondary} 100%)"
            button_text_color = primary  # Button text matches gradient
        else:
            gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            button_text_color = "#667eea"

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

        # Build rich prompt based on v1.1 world-class template
        prompt = f"""Generate HTML content for a CLOSING SLIDE (L29 Hero Layout).

## 🎯 Slide Purpose
**Cognitive Function**: Drive action with clear next steps and contact info
**When to Use**: Final slide ONLY - lasting impression
**Word Count Target**: 65-85 words total
{context_section}
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
- Closing Message: font-size: {closing_size}px; font-weight: {closing_weight}
- Supporting Text: font-size: {supporting_size}px; font-weight: 400
- CTA Button: font-size: {cta_size}px; font-weight: 700
- Contact Info: font-size: {contact_size}px; font-weight: 400

### Visual Requirements (ALL REQUIRED):
- ✅ Gradient background: {gradient}
- ✅ White text color on all elements
- ✅ Text shadows on ALL text (0 4px 12px rgba for h2)
- ✅ Center alignment (text-align: center)
- ✅ CTA button: white background, colored text ({button_text_color})
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
color: {button_text_color};
border-radius: 12px;
box-shadow: 0 8px 24px rgba(0,0,0,0.3);
font-weight: 700;

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

  <h2 style="font-size: {closing_size}px;
             color: white;
             font-weight: {closing_weight};
             text-align: center;
             margin: 0 0 48px 0;
             line-height: 1.2;
             text-shadow: 0 4px 12px rgba(0,0,0,0.3);">
    Ready to Transform Your Operations?
  </h2>

  <p style="font-size: {supporting_size}px;
            color: rgba(255,255,255,0.95);
            text-align: center;
            max-width: 1400px;
            line-height: 1.6;
            margin: 0 0 56px 0;
            text-shadow: 0 2px 8px rgba(0,0,0,0.2);">
    Join 500+ organizations using AI to reduce costs, increase efficiency, and deliver superior customer experiences. Let's discuss your specific use cases and ROI opportunities.
  </p>

  <div style="padding: 32px 72px;
              font-size: {cta_size}px;
              background: white;
              color: {button_text_color};
              border-radius: 12px;
              font-weight: 700;
              box-shadow: 0 8px 24px rgba(0,0,0,0.3);
              margin-bottom: 48px;">
    Schedule Your Demo Today
  </div>

  <div style="font-size: {contact_size}px;
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
- MUST use the exact font sizes ({closing_size}px/{supporting_size}px/{cta_size}px/{contact_size}px)
- MUST include white CTA button with colored text ({button_text_color})
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
