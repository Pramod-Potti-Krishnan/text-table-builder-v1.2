"""
Atomic Component Models for Direct Component Generation
========================================================

Pydantic models for the /v1.2/atomic/{TYPE} endpoints that provide
direct access to atomic component generation without CoT reasoning.

Supports 5 atomic component types:
- METRICS (metrics_card): 1-4 metric cards
- SEQUENTIAL (numbered_card): 1-6 numbered steps
- COMPARISON (comparison_column): 1-4 columns with flexible items
- SECTIONS (colored_section): 1-5 sections with flexible bullets
- CALLOUT (sidebar_box): 1-2 callout boxes with flexible items

v1.1.0: Added count=1 support for all types + placeholder_mode

v1.0.0: Initial atomic component endpoints
"""

from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field, model_validator
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class AtomicType(str, Enum):
    """Atomic component type identifiers (UPPERCASE for URL paths)."""
    METRICS = "METRICS"
    SEQUENTIAL = "SEQUENTIAL"
    COMPARISON = "COMPARISON"
    SECTIONS = "SECTIONS"
    CALLOUT = "CALLOUT"
    TEXT_BULLETS = "TEXT_BULLETS"
    BULLET_BOX = "BULLET_BOX"
    TABLE = "TABLE"
    NUMBERED_LIST = "NUMBERED_LIST"
    TEXT_BOX = "TEXT_BOX"


class LayoutType(str, Enum):
    """Layout arrangement options for atomic components."""
    HORIZONTAL = "horizontal"   # Side by side in a row
    VERTICAL = "vertical"       # Stacked in a column
    GRID = "grid"              # Grid layout (rows x cols)


# Map from atomic type to internal component_id
ATOMIC_TYPE_MAP = {
    AtomicType.METRICS: "metrics_card",
    AtomicType.SEQUENTIAL: "numbered_card",
    AtomicType.COMPARISON: "comparison_column",
    AtomicType.SECTIONS: "colored_section",
    AtomicType.CALLOUT: "sidebar_box",
    AtomicType.TEXT_BULLETS: "text_bullets",
    AtomicType.BULLET_BOX: "bullet_box",
    AtomicType.TABLE: "table_basic",
    AtomicType.NUMBERED_LIST: "numbered_list",
    AtomicType.TEXT_BOX: "text_box"
}

# Color name to variant ID mapping for TEXT_BOX
# Maps simple color names to full accent variant IDs
COLOR_NAME_TO_VARIANT = {
    "purple": "accent_1_purple",
    "blue": "accent_2_blue",
    "red": "accent_3_red",
    "green": "accent_4_green",
    "yellow": "accent_5_yellow",
    "cyan": "accent_6_cyan",
    "orange": "accent_7_orange",
    "teal": "accent_8_teal",
    "pink": "accent_9_pink",
    "indigo": "accent_10_indigo",
}


# =============================================================================
# Context Models
# =============================================================================

class AtomicContext(BaseModel):
    """
    Optional context for content generation.

    Provides slide-level and presentation-level context to guide
    the LLM in generating appropriate content.
    """
    # Slide-level context
    slide_title: Optional[str] = Field(
        None,
        max_length=100,
        description="Title of the slide this component appears on"
    )
    slide_purpose: Optional[str] = Field(
        None,
        max_length=200,
        description="Purpose of this slide (inform, persuade, compare, etc.)"
    )
    key_message: Optional[str] = Field(
        None,
        max_length=200,
        description="The key takeaway message for the audience"
    )
    audience: Optional[str] = Field(
        None,
        description="Target audience (executive, technical, general, etc.)"
    )
    tone: Optional[str] = Field(
        default="professional",
        description="Desired tone (professional, conversational, technical, etc.)"
    )

    # Presentation-level context
    presentation_title: Optional[str] = Field(
        None,
        max_length=100,
        description="Overall presentation title"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry context (tech, healthcare, finance, etc.)"
    )
    company: Optional[str] = Field(
        None,
        description="Company name for context"
    )
    prior_slides_summary: Optional[str] = Field(
        None,
        max_length=500,
        description="Summary of prior slides for continuity"
    )


# =============================================================================
# Base Request Model
# =============================================================================

class AtomicComponentRequest(BaseModel):
    """
    Base request model for all atomic component endpoints.

    All atomic endpoints share these common fields.
    """
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Content request describing what to generate",
        json_schema_extra={"example": "Show quarterly revenue growth across regions"}
    )
    gridWidth: int = Field(
        ...,
        ge=4,
        le=32,
        description="Available width in grid units (32-grid system, 60px per unit)"
    )
    gridHeight: int = Field(
        ...,
        ge=4,
        le=18,
        description="Available height in grid units (18-grid system, 60px per unit)"
    )
    context: Optional[AtomicContext] = Field(
        None,
        description="Optional slide/presentation context for content generation"
    )
    variant: Optional[str] = Field(
        None,
        description="Specific color variant to use (or auto-assign if null)"
    )
    placeholder_mode: bool = Field(
        default=False,
        description="If true, generate placeholder content without LLM call"
    )
    layout: LayoutType = Field(
        default=LayoutType.HORIZONTAL,
        description="Layout arrangement: horizontal (row), vertical (column), or grid"
    )
    grid_cols: Optional[int] = Field(
        default=None,
        ge=1,
        le=6,
        description="Number of columns for grid layout (auto-calculated if null)"
    )
    transparency: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Box opacity (0.0-1.0). Uses component default if null"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key performance metrics for Q4 2024",
                "gridWidth": 24,
                "gridHeight": 10,
                "layout": "horizontal",
                "context": {
                    "audience": "executive",
                    "tone": "professional"
                }
            }
        }


# =============================================================================
# Component Configuration Models
# =============================================================================

class MetricsConfigData(BaseModel):
    """METRICS configuration data for styling metric cards."""
    corners: str = Field(default="rounded", description="Corner style: 'rounded' or 'square'")
    border: bool = Field(default=False, description="Show border around metric cards")
    alignment: str = Field(default="center", description="Text alignment: 'left', 'center', or 'right'")
    color_scheme: str = Field(default="gradient", description="Color scheme: 'gradient', 'solid', or 'accent'")
    color_variant: Optional[Literal["purple", "blue", "red", "green", "yellow", "cyan", "orange", "teal", "pink", "indigo"]] = Field(
        default=None,
        description="Specific color to use for all metric cards (overrides auto-color rotation)"
    )


class TableConfigData(BaseModel):
    """TABLE configuration data for styling data tables."""
    stripe_rows: bool = Field(default=True, description="Enable alternating row background colors (banded rows linked to header color)")
    corners: str = Field(default="square", description="Corner style: 'rounded' or 'square'")
    header_style: str = Field(default="solid", description="Header row style: 'solid', 'pastel', or 'minimal'")
    alignment: str = Field(default="left", description="Cell text alignment: 'left', 'center', or 'right'")
    border_style: str = Field(default="light", description="Border thickness: 'none', 'light', 'medium', or 'heavy'")
    header_color: Optional[Literal["purple", "blue", "red", "green", "yellow", "cyan", "orange", "teal", "pink", "indigo"]] = Field(
        default=None,
        description="Header row color (affects banded rows when stripe_rows is True)"
    )
    first_column_bold: bool = Field(default=False, description="Bold text in the first column")
    last_column_bold: bool = Field(default=False, description="Bold text in the last column")
    show_total_row: bool = Field(default=False, description="Show total row with double line above")
    # Character limit fields for table content generation
    header_min_chars: int = Field(default=5, ge=5, le=500, description="Min chars for header cells")
    header_max_chars: int = Field(default=25, ge=5, le=500, description="Max chars for header cells")
    cell_min_chars: int = Field(default=10, ge=5, le=500, description="Min chars for body cells")
    cell_max_chars: int = Field(default=50, ge=5, le=500, description="Max chars for body cells")


# =============================================================================
# Endpoint-Specific Request Models
# =============================================================================

class MetricsAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/METRICS

    Generates 1-4 metric cards with number, label, and description.
    Supports unitary elements (count=1) for modular composition.
    """
    count: int = Field(
        default=3,
        ge=1,
        le=4,
        description="Number of metric cards to generate (1-4)"
    )
    metrics_config: Optional[MetricsConfigData] = Field(
        default=None,
        description="Optional styling configuration for metrics cards"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Show Q4 performance: revenue growth 23%, customer acquisition up 45%, profit margin 18%",
                "count": 3,
                "gridWidth": 28,
                "gridHeight": 8
            }
        }


class SequentialAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/SEQUENTIAL

    Generates 1-6 numbered cards for steps, phases, or sequential items.
    Supports unitary elements (count=1) for modular composition.
    """
    count: int = Field(
        default=4,
        ge=1,
        le=6,
        description="Number of sequential steps to generate (1-6)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "4-step employee onboarding process: orientation, training, mentorship, evaluation",
                "count": 4,
                "gridWidth": 28,
                "gridHeight": 10
            }
        }


class ComparisonAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/COMPARISON

    Generates 1-4 comparison columns with flexible item counts.
    Supports unitary elements (count=1) for modular composition.
    """
    count: int = Field(
        default=3,
        ge=1,
        le=4,
        description="Number of comparison columns (1-4)"
    )
    items_per_column: int = Field(
        default=5,
        ge=1,
        le=7,
        description="Number of comparison items per column (1-7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Compare our Standard, Professional, and Enterprise plans",
                "count": 3,
                "items_per_column": 5,
                "gridWidth": 28,
                "gridHeight": 14
            }
        }


class SectionsAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/SECTIONS

    Generates 1-5 colored sections with flexible bullet counts.
    Supports unitary elements (count=1) for modular composition.
    """
    count: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of sections to generate (1-5)"
    )
    bullets_per_section: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of bullets per section (1-5)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key benefits of our sustainability initiative: cost savings, brand reputation, environmental impact",
                "count": 3,
                "bullets_per_section": 4,
                "gridWidth": 24,
                "gridHeight": 12
            }
        }


class CalloutAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/CALLOUT

    Generates 1-2 callout/sidebar boxes with flexible item counts.
    """
    count: int = Field(
        default=1,
        ge=1,
        le=2,
        description="Number of callout boxes (1-2)"
    )
    items_per_box: int = Field(
        default=4,
        ge=1,
        le=7,
        description="Number of items per callout box (1-7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key takeaways from our market analysis",
                "count": 1,
                "items_per_box": 5,
                "gridWidth": 10,
                "gridHeight": 12
            }
        }


class TextBulletsAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/TEXT_BULLETS

    Generates 1-4 simple text boxes with subtitle and bullet points.
    Clean, minimal design for straightforward content presentation.
    """
    count: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Number of text bullet boxes (1-4)"
    )
    bullets_per_box: int = Field(
        default=4,
        ge=1,
        le=7,
        description="Number of bullet points per box (1-7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key benefits and features of our new product line",
                "count": 2,
                "bullets_per_box": 4,
                "gridWidth": 24,
                "gridHeight": 10
            }
        }


class BulletBoxAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/BULLET_BOX

    Generates 1-4 rectangular boxes with sharp corners and borders.
    Professional, structured appearance for formal content.
    """
    count: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Number of bullet boxes (1-4)"
    )
    items_per_box: int = Field(
        default=5,
        ge=1,
        le=7,
        description="Number of items per box (1-7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Project requirements and deliverables for Q1",
                "count": 2,
                "items_per_box": 5,
                "gridWidth": 24,
                "gridHeight": 12
            }
        }


class TableAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/TABLE

    Generates 1-2 HTML tables with header row and data rows.
    Professional styling with alternating row colors.
    """
    count: int = Field(
        default=1,
        ge=1,
        le=2,
        description="Number of tables (1-2)"
    )
    columns: int = Field(
        default=3,
        ge=2,
        le=6,
        description="Number of columns per table (2-6)"
    )
    rows: int = Field(
        default=4,
        ge=2,
        le=10,
        description="Number of data rows per table (2-10)"
    )
    table_config: Optional[TableConfigData] = Field(
        default=None,
        description="Optional styling configuration for tables"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Product comparison table: features, pricing, availability",
                "count": 1,
                "columns": 3,
                "rows": 4,
                "gridWidth": 28,
                "gridHeight": 10
            }
        }


class NumberedListAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/NUMBERED_LIST

    Generates 1-4 numbered lists with title and ordered items.
    Clean numbered format for sequential or prioritized content.
    """
    count: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Number of numbered lists (1-4)"
    )
    items_per_list: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of items per list (1-10)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Top priorities and action items for the quarter",
                "count": 2,
                "items_per_list": 5,
                "gridWidth": 24,
                "gridHeight": 12
            }
        }


class TextBoxAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/TEXT_BOX

    Generates 1-6 configurable text boxes with various styling options.
    Supports gradient backgrounds, borders, different list styles.
    """
    count: int = Field(
        default=3,
        ge=1,
        le=6,
        description="Number of text boxes (1-6)"
    )
    items_per_box: int = Field(
        default=4,
        ge=1,
        le=7,
        description="Number of items per box (1-7)"
    )
    background_style: str = Field(
        default="colored",
        description="Background style: 'colored' or 'transparent'"
    )
    color_scheme: str = Field(
        default="accent",
        description="Color scheme: 'gradient', 'solid', or 'accent' (accent recommended for title_style options)"
    )
    list_style: str = Field(
        default="bullets",
        description="List style: 'bullets', 'numbers', or 'none'"
    )
    corners: str = Field(
        default="rounded",
        description="Corner style: 'rounded' or 'square'"
    )
    border: bool = Field(
        default=False,
        description="Show border around boxes"
    )
    show_title: bool = Field(
        default=True,
        description="Show title in each box"
    )
    theme_mode: str = Field(
        default="light",
        description="Theme mode: 'light' or 'dark' - affects text colors for accent variants"
    )
    heading_align: str = Field(
        default="left",
        description="Heading text alignment: 'left', 'center', or 'right'"
    )
    content_align: str = Field(
        default="left",
        description="Content/bullet text alignment: 'left', 'center', or 'right'"
    )
    title_min_chars: int = Field(
        default=30,
        ge=5,
        le=500,
        description="Minimum characters for title/heading (5-500). Must be <= title_max_chars"
    )
    title_max_chars: int = Field(
        default=40,
        ge=5,
        le=500,
        description="Maximum characters for title/heading (5-500)"
    )
    item_min_chars: int = Field(
        default=80,
        ge=5,
        le=500,
        description="Minimum characters per bullet/item (5-500). Must be <= item_max_chars"
    )
    item_max_chars: int = Field(
        default=100,
        ge=5,
        le=500,
        description="Maximum characters per bullet/item (5-500)"
    )
    use_lorem_ipsum: bool = Field(
        default=False,
        description="If True with placeholder_mode, generate Lorem Ipsum text with proper character limits instead of generic placeholders"
    )
    title_style: str = Field(
        default="plain",
        description="Title rendering style: 'plain' (colored text), 'highlighted' (bold, larger, colored), 'neutral' (same color as body text), or 'colored-bg' (badge with dark background, white text)"
    )
    existing_colors: Optional[List[str]] = Field(
        default=None,
        description="List of color names already in use (e.g., ['purple', 'blue']) for collision avoidance. Only applies when background_style='colored'"
    )
    color_variant: Optional[Literal["purple", "blue", "red", "green", "yellow", "cyan", "orange", "teal", "pink", "indigo"]] = Field(
        default=None,
        description="Simple color name that auto-selects the matching accent variant with all associated colors (pastel background, dark heading, badge colors)"
    )

    @model_validator(mode='after')
    def validate_and_resolve(self) -> 'TextBoxAtomicRequest':
        """Validate char bounds and resolve color_variant to full variant ID."""
        # Validate character bounds
        if self.title_min_chars > self.title_max_chars:
            raise ValueError(
                f"title_min_chars ({self.title_min_chars}) must be <= title_max_chars ({self.title_max_chars})"
            )
        if self.item_min_chars > self.item_max_chars:
            raise ValueError(
                f"item_min_chars ({self.item_min_chars}) must be <= item_max_chars ({self.item_max_chars})"
            )

        # Resolve color_variant to full variant ID (only if variant not already set)
        if self.color_variant and not self.variant:
            self.variant = COLOR_NAME_TO_VARIANT.get(self.color_variant)

        return self

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key features of our product: performance, security, ease of use",
                "count": 3,
                "items_per_box": 4,
                "gridWidth": 28,
                "gridHeight": 12,
                "background_style": "colored",
                "color_scheme": "accent",
                "list_style": "bullets",
                "color_variant": "green",
                "theme_mode": "light",
                "heading_align": "left",
                "content_align": "left",
                "title_min_chars": 30,
                "title_max_chars": 40,
                "item_min_chars": 80,
                "item_max_chars": 100,
                "use_lorem_ipsum": False,
                "title_style": "plain",
                "existing_colors": None
            }
        }


# =============================================================================
# Response Models
# =============================================================================

class AtomicMetadata(BaseModel):
    """Metadata about atomic component generation."""

    model_config = {"protected_namespaces": ()}

    generation_time_ms: int = Field(
        ...,
        description="Time taken to generate content in milliseconds"
    )
    model_used: str = Field(
        ...,
        description="LLM model used for content generation"
    )
    grid_dimensions: Dict[str, int] = Field(
        ...,
        description="Grid dimensions used (width, height)"
    )
    space_category: str = Field(
        ...,
        description="Space category: 'small', 'medium', or 'large'"
    )
    scaling_factor: float = Field(
        ...,
        description="Character limit scaling factor applied (0.7-1.3)"
    )


class AtomicComponentResponse(BaseModel):
    """
    Response model for all atomic component endpoints.

    Returns generated HTML along with metadata about the generation.
    """
    success: bool = Field(
        ...,
        description="Whether generation succeeded"
    )
    html: Optional[str] = Field(
        None,
        description="Generated HTML string"
    )
    component_type: str = Field(
        ...,
        description="Atomic component type used (e.g., 'metrics_card')"
    )
    instance_count: int = Field(
        ...,
        description="Number of component instances generated"
    )
    arrangement: str = Field(
        ...,
        description="Layout arrangement used (e.g., 'row_3', 'stacked_4')"
    )
    variants_used: List[str] = Field(
        ...,
        description="Color variants applied to each instance"
    )
    character_counts: Dict[str, List[int]] = Field(
        ...,
        description="Character counts per slot per instance"
    )
    metadata: Optional[AtomicMetadata] = Field(
        None,
        description="Generation metadata (timing, model, scaling)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "html": "<div style=\"...\">...</div>",
                "component_type": "colored_section",
                "instance_count": 3,
                "arrangement": "stacked_3",
                "variants_used": ["blue", "green", "amber"],
                "character_counts": {
                    "section_heading": [18, 22, 20],
                    "bullet_1": [65, 58, 72],
                    "bullet_2": [61, 69, 64],
                    "bullet_3": [70, 62, 68]
                },
                "metadata": {
                    "generation_time_ms": 1250,
                    "model_used": "gemini-1.5-flash",
                    "grid_dimensions": {"width": 24, "height": 12},
                    "space_category": "large",
                    "scaling_factor": 1.05
                }
            }
        }
