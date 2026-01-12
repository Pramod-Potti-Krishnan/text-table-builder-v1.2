"""
Unified Slides Models for Text Service v1.3.0 - Layout Service Aligned

This module provides unified request/response models for the /v1.2/slides/* router.
Aligned with Layout Service naming conventions (H1, H2, H3, C1, I1-I4).

Key Features:
- Combined generation for C1-text (title + subtitle + body in ONE LLM call)
- Enhanced responses with structured fields alongside HTML
- Backward-compatible with existing endpoints
- L29/L25 aliases for Layout Service integration
- v1.3.0: theme_config, content_context, styling_mode, available_space support

Version: 1.3.0
"""

from typing import Dict, Any, Optional, List, Literal, TYPE_CHECKING
from pydantic import BaseModel, Field, field_validator
from enum import Enum

# Avoid circular imports by using TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.requests import ThemeConfig
    from app.models.content_context import ContentContext


# =============================================================================
# Styling Mode for v1.3.0
# =============================================================================

class StylingMode(str, Enum):
    """
    Output styling mode for generated HTML.

    Per THEME_SYSTEM_DESIGN.md Section 12.3 Q4:
    - inline_styles: Full CSS in style attributes (current default)
    - css_classes: .deckster-t1 through .deckster-t4 class references
    """
    INLINE_STYLES = "inline_styles"
    CSS_CLASSES = "css_classes"


# =============================================================================
# Available Space Model for Multi-Step Generation
# =============================================================================

class AvailableSpace(BaseModel):
    """
    Available space for content generation.

    Passed by Director to enable multi-step generation with accurate
    character budget calculations.
    """
    width: int = Field(
        description="Width in grids or pixels"
    )
    height: int = Field(
        description="Height in grids or pixels"
    )
    unit: str = Field(
        default="grids",
        description="Unit: 'grids' (60px each) or 'pixels'"
    )

    def to_pixels(self) -> tuple:
        """Convert to pixel dimensions."""
        if self.unit == "pixels":
            return (self.width, self.height)
        # 60px per grid
        return (self.width * 60, self.height * 60)

    class Config:
        json_schema_extra = {
            "example": {
                "width": 30,
                "height": 14,
                "unit": "grids"
            }
        }


class SlideLayoutType(str, Enum):
    """
    Slide layout types aligned with Layout Service conventions.

    H-series: Hero slides (title, section dividers, closing)
    C-series: Content slides
    I-series: Image+text side-by-side layouts
    L-series: Aliases for layout IDs
    """
    # H-series: Hero slides
    H1_GENERATED = "H1-generated"     # Title slide with AI-generated image
    H1_STRUCTURED = "H1-structured"   # Title slide without image (gradient background)
    H2_SECTION = "H2-section"         # Section divider slide
    H3_CLOSING = "H3-closing"         # Closing slide with contact info

    # C-series: Content slides
    C1_TEXT = "C1-text"               # Content slide with title+subtitle+body (combined gen)

    # I-series: Image+text layouts
    I1 = "I1"   # Wide image left (660x1080)
    I2 = "I2"   # Wide image right (660x1080)
    I3 = "I3"   # Narrow image left (360x1080)
    I4 = "I4"   # Narrow image right (360x1080)

    # Layout ID aliases (for Layout Service compatibility)
    L29 = "L29"   # Alias for H1-generated (hero with image)
    L25 = "L25"   # Alias for C1-text (content slide)


class VisualStyle(str, Enum):
    """Visual style for image generation."""
    PROFESSIONAL = "professional"   # Photorealistic, corporate
    ILLUSTRATED = "illustrated"     # Ghibli-style, anime, artistic
    KIDS = "kids"                   # Bright, playful, cartoon


class ContentStyle(str, Enum):
    """Content formatting style."""
    BULLETS = "bullets"         # Bullet point list
    PARAGRAPHS = "paragraphs"   # Paragraph format
    MIXED = "mixed"             # Combination of both


# ---------------------------------------------------------
# Unified Request Model
# ---------------------------------------------------------

class UnifiedSlideRequest(BaseModel):
    """
    Unified request model for all /v1.2/slides/* endpoints.

    Accepts layout-specific fields based on the target slide type.
    Use only the fields relevant to your slide type.
    """
    # Required fields
    slide_number: int = Field(
        ...,
        description="Slide number in presentation",
        ge=1
    )
    narrative: str = Field(
        ...,
        description="Narrative or topic for content generation",
        min_length=1
    )

    # Common optional fields
    topics: List[str] = Field(
        default_factory=list,
        description="Key topics to expand into content"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context: theme, audience, domain, etc."
    )

    # H1 (Title slide) specific fields
    presentation_title: Optional[str] = Field(
        default=None,
        description="H1: Main presentation title"
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="H1/C1: Subtitle or tagline"
    )
    author_name: Optional[str] = Field(
        default=None,
        description="H1-structured: Author or presenter name"
    )
    date_info: Optional[str] = Field(
        default=None,
        description="H1-structured: Date or event information"
    )

    # H2 (Section divider) specific fields
    section_number: Optional[str] = Field(
        default=None,
        description="H2: Section number (e.g., '01', '02')"
    )
    section_title: Optional[str] = Field(
        default=None,
        description="H2: Section title"
    )

    # H3 (Closing slide) specific fields
    contact_email: Optional[str] = Field(
        default=None,
        description="H3: Contact email address"
    )
    contact_phone: Optional[str] = Field(
        default=None,
        description="H3: Contact phone number"
    )
    website_url: Optional[str] = Field(
        default=None,
        description="H3: Website URL"
    )
    closing_message: Optional[str] = Field(
        default=None,
        description="H3: Closing message (e.g., 'Thank You', 'Questions?')"
    )

    # C1 (Content slide) specific fields
    variant_id: Optional[str] = Field(
        default=None,
        description="C1: Content variant ID (matrix_2x2, grid_3x2, bullets, etc.)"
    )
    content_style: ContentStyle = Field(
        default=ContentStyle.BULLETS,
        description="C1: Content formatting style"
    )
    slide_title: Optional[str] = Field(
        default=None,
        description="C1: Override slide title (otherwise generated)"
    )

    # Image configuration (H1-generated, I-series)
    visual_style: VisualStyle = Field(
        default=VisualStyle.ILLUSTRATED,
        description="Visual style for generated images"
    )
    image_prompt_hint: Optional[str] = Field(
        default=None,
        description="Optional hint for image generation prompt"
    )

    # I-series specific fields
    max_bullets: int = Field(
        default=5,
        ge=3,
        le=8,
        description="I-series: Maximum bullet points for content"
    )

    # =========================================================================
    # v1.3.0: Theme System Integration Parameters
    # =========================================================================

    # Theme configuration (full typography + colors)
    theme_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="v1.3.0: Full theme configuration with typography (t1-t4) and colors"
    )

    # Content context (Audience/Purpose/Time)
    content_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="v1.3.0: Content context with audience, purpose, and time settings"
    )

    # Styling mode for HTML output
    styling_mode: str = Field(
        default="inline_styles",
        description="v1.3.0: Output mode - 'inline_styles' or 'css_classes'"
    )

    # Available space for multi-step generation
    available_space: Optional[Dict[str, Any]] = Field(
        default=None,
        description="v1.3.0: Available space {width, height, unit} for multi-step generation"
    )

    class Config:
        # Ignore unknown fields for forward compatibility (per Q2 answer)
        extra = "ignore"
        json_schema_extra = {
            "examples": [
                {
                    "name": "H1-generated (Title with Image)",
                    "value": {
                        "slide_number": 1,
                        "narrative": "AI-Powered Healthcare Revolution",
                        "presentation_title": "The Future of Medicine",
                        "subtitle": "Transforming Patient Care with AI",
                        "visual_style": "illustrated",
                        "context": {"audience": "healthcare executives"}
                    }
                },
                {
                    "name": "C1-text (Content Slide)",
                    "value": {
                        "slide_number": 3,
                        "narrative": "Key benefits of our solution",
                        "topics": ["50% faster processing", "99.9% uptime", "30% cost reduction"],
                        "variant_id": "bullets",
                        "content_style": "bullets"
                    }
                },
                {
                    "name": "H2-section (Section Divider)",
                    "value": {
                        "slide_number": 5,
                        "narrative": "Implementation Roadmap",
                        "section_number": "02",
                        "section_title": "Implementation",
                        "visual_style": "professional"
                    }
                }
            ]
        }


# ---------------------------------------------------------
# Response Models with Structured Fields
# ---------------------------------------------------------

class HeroSlideResponse(BaseModel):
    """
    SPEC-COMPLIANT response model for H-series (hero) slide generation.

    Per SLIDE_GENERATION_INPUT_SPEC.md:
    - H1-generated/L29: Uses hero_content (full-slide HTML, 1920x1080)
    - H1-structured/H2-section/H3-closing: Uses individual HTML fields + background_color

    ALL text fields contain HTML with inline CSS (not plain text).
    """
    # For H1-generated/L29 ONLY: Full-slide HTML (covers entire 1920x1080)
    hero_content: Optional[str] = Field(
        default=None,
        description="H1-generated/L29: Complete slide HTML (1920x1080) with embedded background"
    )

    # Legacy field - kept for backward compatibility, deprecated for new endpoints
    content: Optional[str] = Field(
        default=None,
        description="[DEPRECATED] Use hero_content for H1-generated, or individual fields for structured layouts"
    )

    # Structured fields - ALL are HTML strings with inline CSS
    # Per SLIDE_GENERATION_INPUT_SPEC.md Section 3
    slide_title: Optional[str] = Field(
        default=None,
        description="HTML: Title with inline styles, e.g. \"<h1 style='font-size:72px;color:#fff'>Title</h1>\""
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="HTML: Subtitle with inline styles, e.g. \"<p style='font-size:32px'>Subtitle</p>\""
    )

    # H1-structured specific - HTML with inline CSS
    author_info: Optional[str] = Field(
        default=None,
        description="H1-structured: HTML author/attribution, e.g. \"Name <span style='opacity:0.7'>| Date</span>\""
    )
    date_info: Optional[str] = Field(
        default=None,
        description="H1-structured: HTML date information"
    )

    # H2-section specific - HTML with inline CSS
    section_number: Optional[str] = Field(
        default=None,
        description="H2: HTML section number, e.g. \"<span style='font-size:120px'>01</span>\""
    )

    # H3-closing specific - HTML with inline CSS
    contact_info: Optional[str] = Field(
        default=None,
        description="H3: HTML contact info, e.g. \"<a href='mailto:...' style='color:#93c5fd'>email</a>\""
    )
    closing_message: Optional[str] = Field(
        default=None,
        description="H3: HTML closing message"
    )

    # CRITICAL: Background fields (per SLIDE_GENERATION_INPUT_SPEC.md)
    # Required for H1-structured, H2-section, H3-closing
    # NOT needed for H1-generated/L29 (background is embedded in hero_content)
    background_color: Optional[str] = Field(
        default=None,
        description="Hex color: #1e3a5f (H1-structured, H3-closing), #374151 (H2-section)"
    )
    background_image: Optional[str] = Field(
        default=None,
        description="Optional background image URL"
    )

    # Image metadata (H1-generated only)
    image_fallback: bool = Field(
        default=False,
        description="True if using placeholder instead of generated image"
    )

    # Generation metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata: slide_type, validation, timings"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "H1-generated (Full-slide HTML)",
                    "value": {
                        "hero_content": "<div style='width:100%;height:100%;background:linear-gradient(135deg,#1e3a5f,#3b82f6);display:flex;align-items:center;justify-content:center;'><h1 style='color:white;font-size:72px;'>Welcome</h1></div>",
                        "background_color": None,
                        "background_image": None,
                        "metadata": {"slide_type": "H1-generated", "slide_number": 1}
                    }
                },
                {
                    "name": "H1-structured (Individual fields + background)",
                    "value": {
                        "hero_content": None,
                        "slide_title": "<h1 style='font-size:72px;color:#ffffff;font-weight:700;'>The Future of Healthcare</h1>",
                        "subtitle": "<p style='font-size:32px;color:rgba(255,255,255,0.9);'>AI-Powered Diagnostics</p>",
                        "author_info": "<div style='font-size:18px;color:rgba(255,255,255,0.7);'>Dr. Jane Smith <span style='opacity:0.7'>| December 2024</span></div>",
                        "background_color": "#1e3a5f",
                        "background_image": "https://example.com/hero-bg.jpg",
                        "metadata": {"slide_type": "H1-structured", "slide_number": 1}
                    }
                },
                {
                    "name": "H2-section",
                    "value": {
                        "hero_content": None,
                        "section_number": "<span style='font-size:120px;font-weight:800;color:#fbbf24;'>02</span>",
                        "slide_title": "<h2 style='font-size:48px;color:#ffffff;'>Implementation</h2>",
                        "background_color": "#374151",
                        "metadata": {"slide_type": "H2-section", "slide_number": 5}
                    }
                },
                {
                    "name": "H3-closing",
                    "value": {
                        "hero_content": None,
                        "slide_title": "<h1 style='font-size:72px;color:#ffffff;'>Thank You</h1>",
                        "subtitle": "<p style='font-size:28px;color:rgba(255,255,255,0.9);'>Questions?</p>",
                        "contact_info": "<div style='font-size:20px;'><a href='mailto:team@company.com' style='color:#93c5fd;'>team@company.com</a></div>",
                        "background_color": "#1e3a5f",
                        "metadata": {"slide_type": "H3-closing", "slide_number": 12}
                    }
                }
            ]
        }


class ContentSlideResponse(BaseModel):
    """
    SPEC-COMPLIANT response model for C1-text (content) slide generation.

    Per SLIDE_GENERATION_INPUT_SPEC.md Section 4:
    - All text fields are HTML strings with inline CSS
    - Includes background_color (default #ffffff) and optional background_image

    Combined generation returns title + subtitle + body in a single LLM call,
    saving 2 LLM calls per slide.
    """
    # Structured fields - ALL are HTML strings with inline CSS
    slide_title: str = Field(
        ...,
        description="HTML: Title with inline styles, e.g. \"<h2 style='font-size:42px;font-weight:600;'>Title</h2>\""
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="HTML: Subtitle with inline styles, e.g. \"<p style='font-size:24px;color:#6b7280;'>Subtitle</p>\""
    )
    body: str = Field(
        ...,
        description="HTML: Body content with inline styles (bullets, paragraphs, etc.)"
    )

    # Aliases for Layout Service compatibility
    rich_content: Optional[str] = Field(
        default=None,
        description="Alias for body (L25 compatibility)"
    )

    # Optional assembled HTML
    html: Optional[str] = Field(
        default=None,
        description="Optional fully assembled HTML (if template provided)"
    )

    # CRITICAL: Background fields (per SLIDE_GENERATION_INPUT_SPEC.md)
    background_color: str = Field(
        default="#ffffff",
        description="Hex background color (default: #ffffff for content slides)"
    )
    background_image: Optional[str] = Field(
        default=None,
        description="Optional background image URL"
    )

    # Generation metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata: llm_calls, generation_mode, variant_id"
    )

    @field_validator('rich_content', mode='before')
    @classmethod
    def set_rich_content(cls, v, info):
        """Auto-populate rich_content from body if not provided."""
        if v is None and 'body' in info.data:
            return info.data.get('body')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "slide_title": "<h2 style='font-size:42px;font-weight:600;'>Key Benefits of AI Integration</h2>",
                "subtitle": "<p style='font-size:24px;color:#6b7280;'>Transform operations with intelligent automation</p>",
                "body": "<ul class='content-list' style='list-style-type:disc;margin-left:24px;'><li>50% faster processing</li><li>99.9% uptime guarantee</li><li>30% cost reduction</li></ul>",
                "rich_content": "<ul class='content-list'>...</ul>",
                "background_color": "#ffffff",
                "background_image": None,
                "metadata": {
                    "llm_calls": 1,
                    "generation_mode": "combined",
                    "variant_id": "bullets",
                    "generation_time_ms": 2100
                }
            }
        }


class ISeriesSlideResponse(BaseModel):
    """
    SPEC-COMPLIANT response model for I-series (image+text) slide generation.

    Per SLIDE_GENERATION_INPUT_SPEC.md Section 5:
    - All HTML slots contain inline CSS styles
    - Includes background_color (default #ffffff)
    - background_image NOT recommended (conflicts with layout's primary image)

    Returns structured HTML content for each slot plus Layout Service aliases.
    """
    # Slot-based HTML content - ALL with inline CSS styles
    image_html: str = Field(
        ...,
        description="HTML: Image slot with styled img tag or placeholder"
    )
    title_html: str = Field(
        ...,
        description="HTML: Title with inline styles, e.g. \"<h2 style='font-size:2.5rem;font-weight:600;'>Title</h2>\""
    )
    subtitle_html: Optional[str] = Field(
        default=None,
        description="HTML: Subtitle with inline styles"
    )
    content_html: str = Field(
        ...,
        description="HTML: Main content area with inline styles (bullets/paragraphs)"
    )

    # Image metadata
    image_url: Optional[str] = Field(
        default=None,
        description="Generated image URL (None if fallback)"
    )
    image_fallback: bool = Field(
        default=False,
        description="True if using placeholder instead of generated image"
    )

    # Layout Service aliases - also HTML with inline CSS
    slide_title: str = Field(
        ...,
        description="HTML: Same as title_html (Layout Service compatibility)"
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="HTML: Same as subtitle_html (Layout Service compatibility)"
    )
    body: str = Field(
        ...,
        description="HTML: Same as content_html (Layout Service compatibility)"
    )

    # CRITICAL: Background color (per SLIDE_GENERATION_INPUT_SPEC.md)
    # background_image NOT recommended for I-series (conflicts with layout's primary image)
    background_color: str = Field(
        default="#ffffff",
        description="Hex background color (default: #ffffff for I-series)"
    )

    # Generation metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata: layout_type, dimensions, timings"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "image_html": "<div style='width:100%;height:100%;'><img src='https://...' style='width:100%;height:100%;object-fit:cover;'/></div>",
                "title_html": "<h2 style='font-size:2.5rem;font-weight:600;color:#1a1a2e;'>Team Overview</h2>",
                "subtitle_html": "<p style='font-size:1.25rem;color:#6b7280;'>Leadership & Innovation</p>",
                "content_html": "<ul style='list-style-type:disc;margin-left:24px;'><li>Engineering excellence</li><li>Design innovation</li></ul>",
                "image_url": "https://storage.googleapis.com/...",
                "image_fallback": False,
                "slide_title": "<h2 style='font-size:2.5rem;font-weight:600;color:#1a1a2e;'>Team Overview</h2>",
                "subtitle": "<p style='font-size:1.25rem;color:#6b7280;'>Leadership & Innovation</p>",
                "body": "<ul style='list-style-type:disc;margin-left:24px;'><li>Engineering excellence</li><li>Design innovation</li></ul>",
                "background_color": "#f8fafc",
                "metadata": {
                    "layout_type": "I1",
                    "image_position": "left",
                    "image_dimensions": {"width": 660, "height": 1080},
                    "content_dimensions": {"width": 1200, "height": 840},
                    "generation_time_ms": 12500
                }
            }
        }


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def resolve_layout_alias(layout_type: SlideLayoutType) -> SlideLayoutType:
    """
    Resolve layout aliases to their canonical types.

    Args:
        layout_type: Input layout type (may be an alias)

    Returns:
        Canonical layout type
    """
    aliases = {
        SlideLayoutType.L29: SlideLayoutType.H1_GENERATED,
        SlideLayoutType.L25: SlideLayoutType.C1_TEXT,
    }
    return aliases.get(layout_type, layout_type)


def get_response_model(layout_type: SlideLayoutType):
    """
    Get the appropriate response model class for a layout type.

    Args:
        layout_type: Slide layout type

    Returns:
        Response model class (HeroSlideResponse, ContentSlideResponse, or ISeriesSlideResponse)
    """
    resolved = resolve_layout_alias(layout_type)

    # H-series → HeroSlideResponse
    if resolved in (SlideLayoutType.H1_GENERATED, SlideLayoutType.H1_STRUCTURED,
                    SlideLayoutType.H2_SECTION, SlideLayoutType.H3_CLOSING):
        return HeroSlideResponse

    # C-series → ContentSlideResponse
    if resolved == SlideLayoutType.C1_TEXT:
        return ContentSlideResponse

    # I-series → ISeriesSlideResponse
    if resolved in (SlideLayoutType.I1, SlideLayoutType.I2,
                    SlideLayoutType.I3, SlideLayoutType.I4):
        return ISeriesSlideResponse

    # Default fallback
    return HeroSlideResponse


# C1 variant categories (for documentation)
C1_VARIANT_CATEGORIES = {
    "matrix": ["matrix_2x2", "matrix_2x3"],
    "grid": [
        "grid_2x3", "grid_3x2", "grid_2x2_centered",
        "grid_2x3_left", "grid_3x2_left", "grid_2x2_left",
        "grid_2x3_numbered", "grid_3x2_numbered", "grid_2x2_numbered"
    ],
    "comparison": ["comparison_2col", "comparison_3col", "comparison_4col"],
    "sequential": ["sequential_3col", "sequential_4col", "sequential_5col"],
    "asymmetric": ["asymmetric_8_4_3section", "asymmetric_8_4_4section", "asymmetric_8_4_5section"],
    "hybrid": ["hybrid_top_2x2", "hybrid_left_2x2"],
    "metrics": ["metrics_3col", "metrics_4col", "metrics_3x2_grid", "metrics_2x2_grid"],
    "impact_quote": ["impact_quote"],
    "table": ["table_2col", "table_3col", "table_4col", "table_5col"],
    "single_column": ["single_column_3section", "single_column_4section", "single_column_5section"]
}

# Flatten to list of all variants
ALL_C1_VARIANTS = [v for variants in C1_VARIANT_CATEGORIES.values() for v in variants]
