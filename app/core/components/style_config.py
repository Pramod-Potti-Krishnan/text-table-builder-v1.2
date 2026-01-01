"""
Style Configuration for Atomic Components
==========================================

Centralized style constants for consistent typography, colors, and layouts
across all non-METRICS atomic components.

METRICS components maintain their own distinct gradient-heavy styling.
All other components (SEQUENTIAL, COMPARISON, SECTIONS, CALLOUT, and new types)
use these standardized values.

v1.0.0: Initial style configuration with consistency rules
"""

from enum import Enum
from typing import Dict, Tuple


# =============================================================================
# Typography - Standardized Font Sizes
# =============================================================================

# Heading styles (component titles, section headers)
HEADING_FONT_SIZE = "28px"
HEADING_FONT_WEIGHT = "700"
HEADING_LINE_HEIGHT = "1.2"

# Body text styles (descriptions, bullet points)
BODY_FONT_SIZE = "21px"
BODY_FONT_WEIGHT = "400"
BODY_LINE_HEIGHT = "1.5"

# Step numbers (SEQUENTIAL component only)
STEP_NUMBER_FONT_SIZE = "62px"
STEP_NUMBER_FONT_WEIGHT = "900"


# =============================================================================
# Text Colors
# =============================================================================

# Primary text colors
TEXT_DARK = "#1f2937"           # Primary text on light backgrounds
TEXT_SECONDARY = "#374151"      # Secondary/muted text
TEXT_MUTED = "#6b7280"          # Tertiary/placeholder text
TEXT_LIGHT = "#ffffff"          # Text on dark backgrounds (METRICS only)

# Bullet colors
BULLET_COLOR_BLACK = "#374151"  # Standard black bullets
BULLET_COLOR_ACCENT = None      # Use accent_color from variant when colored


# =============================================================================
# Box Transparency
# =============================================================================

# Non-METRICS components use 60% transparency by default
BOX_OPACITY_DEFAULT = 0.6       # 60% transparent (for non-METRICS)
BOX_OPACITY_SOLID = 1.0         # Full opacity option
BOX_OPACITY_METRICS = 1.0       # METRICS always solid (gradients need it)


# =============================================================================
# Accent Color Palette (Matching Illustrator Service)
# =============================================================================

# Each accent has "bright" (gradient start) and "dark" (gradient end) values
ACCENT_COLORS: Dict[str, Dict[str, str]] = {
    "blue": {
        "bright": "#3b82f6",
        "dark": "#2563eb",
        "light_bg": "#f0f9ff",
        "light_bg_end": "#e0f2fe",
    },
    "purple": {
        "bright": "#8b5cf6",
        "dark": "#7c3aed",
        "light_bg": "#faf5ff",
        "light_bg_end": "#f3e8ff",
    },
    "green": {
        "bright": "#10b981",
        "dark": "#059669",
        "light_bg": "#f0fdf4",
        "light_bg_end": "#dcfce7",
    },
    "amber": {
        "bright": "#f59e0b",
        "dark": "#d97706",
        "light_bg": "#fffbeb",
        "light_bg_end": "#fef3c7",
    },
    "red": {
        "bright": "#ef4444",
        "dark": "#dc2626",
        "light_bg": "#fef2f2",
        "light_bg_end": "#fee2e2",
    },
    "pink": {
        "bright": "#ec4899",
        "dark": "#db2777",
        "light_bg": "#fdf2f8",
        "light_bg_end": "#fce7f3",
    },
    "cyan": {
        "bright": "#06b6d4",
        "dark": "#0891b2",
        "light_bg": "#ecfeff",
        "light_bg_end": "#cffafe",
    },
    "teal": {
        "bright": "#14b8a6",
        "dark": "#0d9488",
        "light_bg": "#f0fdfa",
        "light_bg_end": "#ccfbf1",
    },
}


# =============================================================================
# Layout Types
# =============================================================================

class LayoutType(str, Enum):
    """Layout arrangement options for atomic components."""
    HORIZONTAL = "horizontal"   # Side by side in a row
    VERTICAL = "vertical"       # Stacked in a column
    GRID = "grid"              # Grid layout (rows x cols)


# =============================================================================
# Helper Functions
# =============================================================================

def get_accent_gradient(color_name: str, direction: str = "135deg") -> str:
    """
    Get a CSS linear gradient for an accent color.

    Args:
        color_name: Key from ACCENT_COLORS (e.g., "blue", "purple")
        direction: CSS gradient direction (default: "135deg")

    Returns:
        CSS linear-gradient string
    """
    colors = ACCENT_COLORS.get(color_name, ACCENT_COLORS["blue"])
    return f"linear-gradient({direction}, {colors['bright']} 0%, {colors['dark']} 100%)"


def get_light_background_gradient(color_name: str, direction: str = "135deg") -> str:
    """
    Get a light background gradient for an accent color.
    Used for callout/sidebar backgrounds with dark text.

    Args:
        color_name: Key from ACCENT_COLORS (e.g., "blue", "purple")
        direction: CSS gradient direction (default: "135deg")

    Returns:
        CSS linear-gradient string with light colors
    """
    colors = ACCENT_COLORS.get(color_name, ACCENT_COLORS["blue"])
    return f"linear-gradient({direction}, {colors['light_bg']} 0%, {colors['light_bg_end']} 100%)"


def get_box_shadow(color_name: str, opacity: float = 0.3) -> str:
    """
    Get a CSS box shadow using an accent color.

    Args:
        color_name: Key from ACCENT_COLORS
        opacity: Shadow opacity (default: 0.3)

    Returns:
        CSS box-shadow string
    """
    colors = ACCENT_COLORS.get(color_name, ACCENT_COLORS["blue"])
    # Convert hex to rgba for shadow
    bright = colors['bright']
    r = int(bright[1:3], 16)
    g = int(bright[3:5], 16)
    b = int(bright[5:7], 16)
    return f"0 8px 24px rgba({r}, {g}, {b}, {opacity})"


def apply_transparency(background_css: str, opacity: float) -> str:
    """
    Apply transparency to a background CSS value.

    For solid colors: converts to rgba
    For gradients: wraps in container with opacity

    Args:
        background_css: Original background CSS
        opacity: Opacity value (0.0 - 1.0)

    Returns:
        Modified CSS with transparency applied
    """
    if opacity >= 1.0:
        return background_css

    # For simplicity, return opacity style to be applied to container
    # The actual component should wrap with a div that has this opacity
    return f"opacity: {opacity};"


# =============================================================================
# CSS Generation Helpers
# =============================================================================

def heading_style(color: str = TEXT_DARK) -> str:
    """Generate inline CSS for component headings."""
    return f"font-size: {HEADING_FONT_SIZE}; font-weight: {HEADING_FONT_WEIGHT}; color: {color}; line-height: {HEADING_LINE_HEIGHT};"


def body_style(color: str = TEXT_SECONDARY) -> str:
    """Generate inline CSS for body text."""
    return f"font-size: {BODY_FONT_SIZE}; font-weight: {BODY_FONT_WEIGHT}; color: {color}; line-height: {BODY_LINE_HEIGHT};"


def bullet_list_style(use_disc: bool = True, color: str = BULLET_COLOR_BLACK) -> str:
    """
    Generate inline CSS for bullet lists.

    Args:
        use_disc: If True, use native CSS disc bullets (black)
                  If False, uses custom positioned bullets
        color: Text color for bullet items
    """
    if use_disc:
        return f"list-style-type: disc; padding-left: 20px; margin: 0; color: {color};"
    else:
        return f"list-style: none; padding: 0; margin: 0; color: {color};"


# =============================================================================
# Component-Specific Defaults
# =============================================================================

# Default transparency by component type
COMPONENT_TRANSPARENCY: Dict[str, float] = {
    "metrics_card": BOX_OPACITY_SOLID,      # Solid - gradient backgrounds
    "numbered_card": BOX_OPACITY_DEFAULT,   # 60% transparent
    "comparison_column": BOX_OPACITY_DEFAULT,
    "colored_section": BOX_OPACITY_DEFAULT,
    "sidebar_box": BOX_OPACITY_DEFAULT,
    # New components (to be added)
    "text_bullets": BOX_OPACITY_DEFAULT,
    "bullet_box": BOX_OPACITY_DEFAULT,
    "table_basic": BOX_OPACITY_DEFAULT,
    "numbered_list": BOX_OPACITY_DEFAULT,
}


def get_default_transparency(component_id: str) -> float:
    """Get default transparency for a component type."""
    return COMPONENT_TRANSPARENCY.get(component_id, BOX_OPACITY_DEFAULT)
