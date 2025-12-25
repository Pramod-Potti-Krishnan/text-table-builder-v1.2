"""
Theme Presets for Text Service v1.3.0

Embedded theme presets used as fallback when Layout Service is unavailable.
Per THEME_SYSTEM_DESIGN.md Section 12.2:
- Bulk sync from Layout Service is preferred
- These presets provide graceful fallback
- All color keys use snake_case

Version: 1.3.0
"""

from typing import Dict, Any


# =============================================================================
# Theme Presets (4 Themes)
# =============================================================================

THEME_PRESETS: Dict[str, Dict[str, Any]] = {
    "professional": {
        "theme_id": "professional",
        "version": "1.0.0",
        "typography": {
            "t1": {"size": 40, "weight": 700, "color": "#1f2937", "line_height": 1.2},
            "t2": {"size": 24, "weight": 600, "color": "#374151", "line_height": 1.3},
            "t3": {"size": 20, "weight": 500, "color": "#4b5563", "line_height": 1.4},
            "t4": {"size": 16, "weight": 400, "color": "#6b7280", "line_height": 1.5},
            "font_family": "Poppins, sans-serif",
            "font_family_heading": "Poppins, sans-serif",
        },
        "colors": {
            # Primary colors
            "primary": "#1e3a5f",
            "primary_dark": "#152a45",
            "primary_light": "#2d4a6f",
            # Accent colors
            "accent": "#3b82f6",
            "accent_dark": "#2563eb",
            "accent_light": "#60a5fa",
            # Tertiary colors
            "tertiary_1": "#8b5cf6",
            "tertiary_2": "#ec4899",
            "tertiary_3": "#f59e0b",
            # Background/Surface
            "background": "#ffffff",
            "surface": "#f8fafc",
            "border": "#e5e7eb",
            # Text colors
            "text_primary": "#1f2937",
            "text_secondary": "#374151",
            "text_muted": "#6b7280",
            # Chart colors
            "chart_1": "#3b82f6",
            "chart_2": "#10b981",
            "chart_3": "#f59e0b",
            "chart_4": "#ef4444",
            "chart_5": "#8b5cf6",
            "chart_6": "#ec4899",
            # Semantic colors
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        },
    },

    "executive": {
        "theme_id": "executive",
        "version": "1.0.0",
        "typography": {
            "t1": {"size": 30, "weight": 700, "color": "#111827", "line_height": 1.2},
            "t2": {"size": 22, "weight": 600, "color": "#1f2937", "line_height": 1.3},
            "t3": {"size": 18, "weight": 500, "color": "#374151", "line_height": 1.4},
            "t4": {"size": 14, "weight": 400, "color": "#4b5563", "line_height": 1.5},
            "font_family": "Inter, sans-serif",
            "font_family_heading": "Inter, sans-serif",
        },
        "colors": {
            # Primary - Darker, more sophisticated navy
            "primary": "#0f172a",
            "primary_dark": "#020617",
            "primary_light": "#1e293b",
            # Accent - Gold/amber for executive feel
            "accent": "#d97706",
            "accent_dark": "#b45309",
            "accent_light": "#f59e0b",
            # Tertiary
            "tertiary_1": "#6366f1",
            "tertiary_2": "#a855f7",
            "tertiary_3": "#14b8a6",
            # Background/Surface
            "background": "#ffffff",
            "surface": "#f8fafc",
            "border": "#e2e8f0",
            # Text colors - Darker for more contrast
            "text_primary": "#111827",
            "text_secondary": "#1f2937",
            "text_muted": "#4b5563",
            # Chart colors - Sophisticated palette
            "chart_1": "#0ea5e9",
            "chart_2": "#22c55e",
            "chart_3": "#d97706",
            "chart_4": "#dc2626",
            "chart_5": "#6366f1",
            "chart_6": "#a855f7",
            # Semantic
            "success": "#22c55e",
            "warning": "#d97706",
            "error": "#dc2626",
        },
    },

    "educational": {
        "theme_id": "educational",
        "version": "1.0.0",
        "typography": {
            "t1": {"size": 34, "weight": 700, "color": "#1e40af", "line_height": 1.25},
            "t2": {"size": 26, "weight": 600, "color": "#1e3a8a", "line_height": 1.35},
            "t3": {"size": 22, "weight": 500, "color": "#1f2937", "line_height": 1.45},
            "t4": {"size": 18, "weight": 400, "color": "#374151", "line_height": 1.55},
            "font_family": "Open Sans, sans-serif",
            "font_family_heading": "Montserrat, sans-serif",
        },
        "colors": {
            # Primary - Educational blue
            "primary": "#1e40af",
            "primary_dark": "#1e3a8a",
            "primary_light": "#3b82f6",
            # Accent - Green for learning/growth
            "accent": "#059669",
            "accent_dark": "#047857",
            "accent_light": "#10b981",
            # Tertiary - Variety for visual interest
            "tertiary_1": "#7c3aed",
            "tertiary_2": "#db2777",
            "tertiary_3": "#ea580c",
            # Background/Surface
            "background": "#ffffff",
            "surface": "#f0f9ff",
            "border": "#bfdbfe",
            # Text colors
            "text_primary": "#1e3a8a",
            "text_secondary": "#1f2937",
            "text_muted": "#6b7280",
            # Chart colors - Clear, distinct
            "chart_1": "#2563eb",
            "chart_2": "#059669",
            "chart_3": "#ea580c",
            "chart_4": "#dc2626",
            "chart_5": "#7c3aed",
            "chart_6": "#db2777",
            # Semantic
            "success": "#059669",
            "warning": "#ea580c",
            "error": "#dc2626",
        },
    },

    "children": {
        "theme_id": "children",
        "version": "1.0.0",
        "typography": {
            "t1": {"size": 36, "weight": 800, "color": "#7c3aed", "line_height": 1.3},
            "t2": {"size": 28, "weight": 700, "color": "#8b5cf6", "line_height": 1.4},
            "t3": {"size": 24, "weight": 600, "color": "#1f2937", "line_height": 1.5},
            "t4": {"size": 20, "weight": 500, "color": "#374151", "line_height": 1.6},
            "font_family": "Nunito, sans-serif",
            "font_family_heading": "Fredoka One, cursive",
        },
        "colors": {
            # Primary - Fun purple
            "primary": "#7c3aed",
            "primary_dark": "#6d28d9",
            "primary_light": "#8b5cf6",
            # Accent - Bright pink/magenta
            "accent": "#ec4899",
            "accent_dark": "#db2777",
            "accent_light": "#f472b6",
            # Tertiary - Playful colors
            "tertiary_1": "#06b6d4",
            "tertiary_2": "#22c55e",
            "tertiary_3": "#fbbf24",
            # Background/Surface - Soft, warm
            "background": "#fefce8",
            "surface": "#fef3c7",
            "border": "#fcd34d",
            # Text colors
            "text_primary": "#581c87",
            "text_secondary": "#6b21a8",
            "text_muted": "#7c3aed",
            # Chart colors - Bright, fun
            "chart_1": "#ec4899",
            "chart_2": "#22c55e",
            "chart_3": "#fbbf24",
            "chart_4": "#f97316",
            "chart_5": "#06b6d4",
            "chart_6": "#8b5cf6",
            # Semantic
            "success": "#22c55e",
            "warning": "#fbbf24",
            "error": "#f97316",
        },
    },
}


# =============================================================================
# CSS Class Definitions
# =============================================================================

# Maps typography levels to CSS class names
CSS_CLASS_MAP = {
    "t1": "deckster-t1",
    "t2": "deckster-t2",
    "t3": "deckster-t3",
    "t4": "deckster-t4",
    "emphasis": "deckster-emphasis",
    "bullet": "deckster-bullet",
    "heading": "deckster-heading",
    "subheading": "deckster-subheading",
    "body": "deckster-body",
    "caption": "deckster-caption",
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_theme_preset(theme_id: str) -> Dict[str, Any]:
    """
    Get theme preset by ID.

    Args:
        theme_id: Theme identifier

    Returns:
        Theme preset dictionary, defaults to 'professional' if not found
    """
    return THEME_PRESETS.get(theme_id, THEME_PRESETS["professional"])


def get_typography_spec(theme_id: str, level: str) -> Dict[str, Any]:
    """
    Get typography specification for a level.

    Args:
        theme_id: Theme identifier
        level: Typography level (t1, t2, t3, t4)

    Returns:
        Typography specification dictionary
    """
    theme = get_theme_preset(theme_id)
    typography = theme.get("typography", {})
    return typography.get(level, typography.get("t3", {}))


def get_color(theme_id: str, color_key: str) -> str:
    """
    Get color by key.

    Args:
        theme_id: Theme identifier
        color_key: Color key (e.g., 'primary', 'accent', 'text_primary')

    Returns:
        Hex color string
    """
    theme = get_theme_preset(theme_id)
    colors = theme.get("colors", {})
    return colors.get(color_key, "#000000")


def get_chart_colors(theme_id: str) -> list:
    """
    Get chart color palette for a theme.

    Args:
        theme_id: Theme identifier

    Returns:
        List of 6 chart colors
    """
    theme = get_theme_preset(theme_id)
    colors = theme.get("colors", {})
    return [
        colors.get("chart_1", "#3b82f6"),
        colors.get("chart_2", "#10b981"),
        colors.get("chart_3", "#f59e0b"),
        colors.get("chart_4", "#ef4444"),
        colors.get("chart_5", "#8b5cf6"),
        colors.get("chart_6", "#ec4899"),
    ]


def get_css_class(level: str) -> str:
    """
    Get CSS class name for a typography level.

    Args:
        level: Typography level or element type

    Returns:
        CSS class name (e.g., 'deckster-t1')
    """
    return CSS_CLASS_MAP.get(level, "deckster-body")


def build_inline_style(theme_id: str, level: str) -> str:
    """
    Build inline CSS style string for a typography level.

    Args:
        theme_id: Theme identifier
        level: Typography level (t1, t2, t3, t4)

    Returns:
        CSS style string
    """
    spec = get_typography_spec(theme_id, level)
    if not spec:
        return ""

    parts = []
    if "size" in spec:
        parts.append(f"font-size:{spec['size']}px")
    if "weight" in spec:
        parts.append(f"font-weight:{spec['weight']}")
    if "color" in spec:
        parts.append(f"color:{spec['color']}")
    if "line_height" in spec:
        parts.append(f"line-height:{spec['line_height']}")
    if "letter_spacing" in spec:
        parts.append(f"letter-spacing:{spec['letter_spacing']}")

    return ";".join(parts) + ";" if parts else ""


def get_all_theme_ids() -> list:
    """Get list of all available theme IDs."""
    return list(THEME_PRESETS.keys())


def validate_theme_id(theme_id: str) -> bool:
    """Check if theme ID is valid."""
    return theme_id in THEME_PRESETS
