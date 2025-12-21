"""
HTML Formatter - CSS Class vs Inline Style Output

Provides two output modes for generated HTML:
1. inline_styles: Full CSS in style attributes (current default)
2. css_classes: .deckster-t1 through .deckster-t4 class references

Per THEME_SYSTEM_DESIGN.md Section 12.3 Q4:
- CSS classes enable frontend theme switching via CSS class swap
- Inline styles provide standalone HTML with embedded styling

Version: 1.3.0
"""

import re
from typing import Optional, Dict, List
from app.models.requests import ThemeConfig
from app.core.theme.presets import (
    CSS_CLASS_MAP,
    get_theme_preset,
    get_typography_spec,
    build_inline_style
)


# =============================================================================
# CSS Class Formatting
# =============================================================================

def format_with_classes(text: str, level: str) -> str:
    """
    Format text with CSS class reference.

    Args:
        text: Text content
        level: Typography level (t1, t2, t3, t4) or element type

    Returns:
        HTML span with CSS class
    """
    css_class = CSS_CLASS_MAP.get(level, "deckster-body")
    return f'<span class="{css_class}">{text}</span>'


def format_heading_with_class(text: str) -> str:
    """Format heading with t1 class."""
    return f'<h2 class="deckster-t1">{text}</h2>'


def format_subheading_with_class(text: str) -> str:
    """Format subheading with t2 class."""
    return f'<h3 class="deckster-t2">{text}</h3>'


def format_body_with_class(text: str) -> str:
    """Format body text with t3 class."""
    return f'<p class="deckster-t3">{text}</p>'


def format_caption_with_class(text: str) -> str:
    """Format caption with t4 class."""
    return f'<span class="deckster-t4">{text}</span>'


def format_bullet_list_with_classes(items: List[str]) -> str:
    """
    Format bullet list with CSS classes.

    Args:
        items: List of bullet items

    Returns:
        HTML unordered list with classes
    """
    items_html = "\n".join(
        f'    <li class="deckster-bullet deckster-t3">{item}</li>'
        for item in items
    )
    return f'<ul class="deckster-list">\n{items_html}\n</ul>'


# =============================================================================
# Inline Style Formatting
# =============================================================================

def format_with_inline(
    text: str,
    level: str,
    theme_config: Optional[ThemeConfig] = None,
    theme_id: str = "professional"
) -> str:
    """
    Format text with inline CSS styles.

    Args:
        text: Text content
        level: Typography level (t1, t2, t3, t4)
        theme_config: Optional theme configuration
        theme_id: Theme ID for preset lookup

    Returns:
        HTML span with inline styles
    """
    style = _get_inline_style(level, theme_config, theme_id)
    return f'<span style="{style}">{text}</span>'


def format_heading_with_inline(
    text: str,
    theme_config: Optional[ThemeConfig] = None,
    theme_id: str = "professional"
) -> str:
    """Format heading with inline t1 styles."""
    style = _get_inline_style("t1", theme_config, theme_id)
    return f'<h2 style="{style}">{text}</h2>'


def format_subheading_with_inline(
    text: str,
    theme_config: Optional[ThemeConfig] = None,
    theme_id: str = "professional"
) -> str:
    """Format subheading with inline t2 styles."""
    style = _get_inline_style("t2", theme_config, theme_id)
    return f'<h3 style="{style}">{text}</h3>'


def format_body_with_inline(
    text: str,
    theme_config: Optional[ThemeConfig] = None,
    theme_id: str = "professional"
) -> str:
    """Format body text with inline t3 styles."""
    style = _get_inline_style("t3", theme_config, theme_id)
    return f'<p style="{style}">{text}</p>'


def format_bullet_list_with_inline(
    items: List[str],
    theme_config: Optional[ThemeConfig] = None,
    theme_id: str = "professional"
) -> str:
    """
    Format bullet list with inline styles.

    Args:
        items: List of bullet items
        theme_config: Optional theme configuration
        theme_id: Theme ID for preset lookup

    Returns:
        HTML unordered list with inline styles
    """
    item_style = _get_inline_style("t3", theme_config, theme_id)
    items_html = "\n".join(
        f'    <li style="{item_style}">{item}</li>'
        for item in items
    )

    list_style = "list-style-type:disc;margin-left:24px;padding:0;"
    return f'<ul style="{list_style}">\n{items_html}\n</ul>'


def _get_inline_style(
    level: str,
    theme_config: Optional[ThemeConfig],
    theme_id: str
) -> str:
    """Get inline style string for a typography level."""
    if theme_config and theme_config.typography:
        spec = theme_config.get_typography_spec(level)
        parts = [
            f"font-size:{spec.size}px",
            f"font-weight:{spec.weight}",
            f"color:{spec.color}",
            f"line-height:{spec.line_height}"
        ]
        if spec.letter_spacing:
            parts.append(f"letter-spacing:{spec.letter_spacing}")
        return ";".join(parts) + ";"

    # Fallback to theme presets
    return build_inline_style(theme_id, level)


# =============================================================================
# HTML Formatter Class
# =============================================================================

class HTMLFormatter:
    """
    Unified HTML formatter supporting both output modes.

    Usage:
        formatter = HTMLFormatter(styling_mode="css_classes")
        html = formatter.format_heading("Welcome")
    """

    def __init__(
        self,
        styling_mode: str = "inline_styles",
        theme_config: Optional[ThemeConfig] = None,
        theme_id: str = "professional"
    ):
        """
        Initialize the formatter.

        Args:
            styling_mode: "inline_styles" or "css_classes"
            theme_config: Optional theme configuration for inline styles
            theme_id: Theme ID for preset lookup
        """
        self.styling_mode = styling_mode
        self.theme_config = theme_config
        self.theme_id = theme_id
        self._classes_used: List[str] = []

    @property
    def uses_classes(self) -> bool:
        """Check if using CSS class mode."""
        return self.styling_mode == "css_classes"

    @property
    def css_classes_used(self) -> List[str]:
        """Get list of CSS classes used in this formatter."""
        return list(set(self._classes_used))

    def format_text(self, text: str, level: str) -> str:
        """
        Format text with specified typography level.

        Args:
            text: Text content
            level: Typography level (t1, t2, t3, t4)

        Returns:
            Formatted HTML
        """
        if self.uses_classes:
            self._classes_used.append(CSS_CLASS_MAP.get(level, "deckster-body"))
            return format_with_classes(text, level)
        else:
            return format_with_inline(text, level, self.theme_config, self.theme_id)

    def format_heading(self, text: str) -> str:
        """Format as heading (t1)."""
        if self.uses_classes:
            self._classes_used.append("deckster-t1")
            return format_heading_with_class(text)
        else:
            return format_heading_with_inline(text, self.theme_config, self.theme_id)

    def format_subheading(self, text: str) -> str:
        """Format as subheading (t2)."""
        if self.uses_classes:
            self._classes_used.append("deckster-t2")
            return format_subheading_with_class(text)
        else:
            return format_subheading_with_inline(text, self.theme_config, self.theme_id)

    def format_body(self, text: str) -> str:
        """Format as body text (t3)."""
        if self.uses_classes:
            self._classes_used.append("deckster-t3")
            return format_body_with_class(text)
        else:
            return format_body_with_inline(text, self.theme_config, self.theme_id)

    def format_caption(self, text: str) -> str:
        """Format as caption (t4)."""
        if self.uses_classes:
            self._classes_used.append("deckster-t4")
            return format_caption_with_class(text)
        else:
            return format_with_inline(text, "t4", self.theme_config, self.theme_id)

    def format_bullet_list(self, items: List[str]) -> str:
        """Format as bullet list."""
        if self.uses_classes:
            self._classes_used.extend(["deckster-list", "deckster-bullet", "deckster-t3"])
            return format_bullet_list_with_classes(items)
        else:
            return format_bullet_list_with_inline(items, self.theme_config, self.theme_id)

    def format_emphasis(self, text: str) -> str:
        """Format with emphasis styling."""
        if self.uses_classes:
            self._classes_used.append("deckster-emphasis")
            return f'<strong class="deckster-emphasis">{text}</strong>'
        else:
            # Get accent color from theme
            accent_color = "#3b82f6"  # Default
            if self.theme_config and self.theme_config.colors:
                accent_color = self.theme_config.colors.accent

            return f'<strong style="color:{accent_color};font-weight:600;">{text}</strong>'

    def wrap_content(self, html: str, container_class: str = "deckster-content") -> str:
        """
        Wrap content in a container div.

        Args:
            html: HTML content
            container_class: Container class name

        Returns:
            HTML wrapped in container div
        """
        if self.uses_classes:
            return f'<div class="{container_class}">{html}</div>'
        else:
            return f'<div class="{container_class}">{html}</div>'


# =============================================================================
# Conversion Utilities
# =============================================================================

def convert_inline_to_classes(html: str) -> str:
    """
    Convert inline-styled HTML to class-based HTML.

    This is a best-effort conversion that replaces common inline patterns
    with CSS class references.

    Args:
        html: HTML with inline styles

    Returns:
        HTML with CSS classes
    """
    # Pattern mappings (inline style pattern -> class)
    patterns = [
        (r'style="[^"]*font-size:\s*3[0-2]px[^"]*"', 'class="deckster-t1"'),
        (r'style="[^"]*font-size:\s*2[2-6]px[^"]*"', 'class="deckster-t2"'),
        (r'style="[^"]*font-size:\s*1[8-9]px[^"]*"', 'class="deckster-t3"'),
        (r'style="[^"]*font-size:\s*20px[^"]*"', 'class="deckster-t3"'),
        (r'style="[^"]*font-size:\s*1[4-7]px[^"]*"', 'class="deckster-t4"'),
    ]

    result = html
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)

    return result


def extract_classes_from_html(html: str) -> List[str]:
    """
    Extract all deckster CSS classes from HTML.

    Args:
        html: HTML content

    Returns:
        List of unique deckster class names
    """
    pattern = r'class="([^"]*deckster-[^"]*)"'
    matches = re.findall(pattern, html)

    classes = set()
    for match in matches:
        for cls in match.split():
            if cls.startswith("deckster-"):
                classes.add(cls)

    return list(classes)
