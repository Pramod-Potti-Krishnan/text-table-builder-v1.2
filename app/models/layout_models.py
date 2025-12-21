"""
Layout Service Integration Models for Text & Table Builder v1.2

Pydantic models for the Layout Service API endpoints that enable
grid-based text and table generation with constraint-aware HTML+CSS output.

Grid System: 32×18 grid (1920×1080px HD slide, 60×60px per cell)

Endpoints:
- POST /api/ai/text/generate - Generate new text content
- POST /api/ai/text/transform - Transform existing text
- POST /api/ai/text/autofit - Fit text to element dimensions
- POST /api/ai/table/generate - Generate structured table
- POST /api/ai/table/transform - Modify table structure
- POST /api/ai/table/analyze - Get insights from table data
- POST /api/ai/slide/title - Generate slide title
- POST /api/ai/slide/subtitle - Generate slide subtitle
- POST /api/ai/slide/title-slide - Generate title slide content
- POST /api/ai/slide/section - Generate section divider content
- POST /api/ai/slide/closing - Generate closing slide content
- POST /api/ai/element/text - Generate generic text element
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
import uuid


# =============================================================================
# Enums
# =============================================================================

class TextTone(str, Enum):
    """Writing tone for text generation."""
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    ACADEMIC = "academic"
    PERSUASIVE = "persuasive"
    CASUAL = "casual"
    TECHNICAL = "technical"


class TextFormat(str, Enum):
    """Output structure format."""
    PARAGRAPH = "paragraph"
    BULLETS = "bullets"
    NUMBERED = "numbered"
    HEADLINE = "headline"
    QUOTE = "quote"
    MIXED = "mixed"


class BulletStyle(str, Enum):
    """Bullet point styles for lists."""
    DISC = "disc"
    CIRCLE = "circle"
    SQUARE = "square"
    DASH = "dash"
    ARROW = "arrow"
    CHECK = "check"


class TextTransformation(str, Enum):
    """Text transformation operations."""
    EXPAND = "expand"
    CONDENSE = "condense"
    SIMPLIFY = "simplify"
    FORMALIZE = "formalize"
    CASUALIZE = "casualize"
    BULLETIZE = "bulletize"
    PARAGRAPHIZE = "paragraphize"
    REPHRASE = "rephrase"
    PROOFREAD = "proofread"
    TRANSLATE = "translate"


class AutofitStrategy(str, Enum):
    """Strategy for auto-fitting text to element dimensions."""
    REDUCE_FONT = "reduce_font"
    TRUNCATE = "truncate"
    SMART_CONDENSE = "smart_condense"
    OVERFLOW = "overflow"


class TableStylePreset(str, Enum):
    """Table styling presets."""
    MINIMAL = "minimal"
    BORDERED = "bordered"
    STRIPED = "striped"
    MODERN = "modern"
    PROFESSIONAL = "professional"
    COLORFUL = "colorful"


class TableTransformation(str, Enum):
    """Table transformation operations."""
    ADD_COLUMN = "add_column"
    ADD_ROW = "add_row"
    REMOVE_COLUMN = "remove_column"
    REMOVE_ROW = "remove_row"
    SORT = "sort"
    SUMMARIZE = "summarize"
    TRANSPOSE = "transpose"
    EXPAND = "expand"
    MERGE_CELLS = "merge_cells"
    SPLIT_COLUMN = "split_column"


class TableAnalysisType(str, Enum):
    """Types of table analysis."""
    SUMMARY = "summary"
    TRENDS = "trends"
    OUTLIERS = "outliers"
    VISUALIZATION = "visualization"


class TextErrorCode(str, Enum):
    """Error codes for text operations."""
    INVALID_PROMPT = "INVALID_PROMPT"
    CONTEXT_MISSING = "CONTEXT_MISSING"
    GENERATION_FAILED = "GENERATION_FAILED"
    CONTENT_FILTERED = "CONTENT_FILTERED"
    RATE_LIMITED = "RATE_LIMITED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INVALID_GRID = "INVALID_GRID"
    TRANSFORM_FAILED = "TRANSFORM_FAILED"
    AUTOFIT_FAILED = "AUTOFIT_FAILED"


class TableErrorCode(str, Enum):
    """Error codes for table operations."""
    INVALID_STRUCTURE = "INVALID_STRUCTURE"
    GENERATION_FAILED = "GENERATION_FAILED"
    DATA_INCONSISTENT = "DATA_INCONSISTENT"
    RATE_LIMITED = "RATE_LIMITED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INVALID_GRID = "INVALID_GRID"
    TRANSFORM_FAILED = "TRANSFORM_FAILED"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"


class SlideTextType(str, Enum):
    """Types of slide-specific text content."""
    SLIDE_TITLE = "slide_title"
    SLIDE_SUBTITLE = "slide_subtitle"
    TITLE_SLIDE_TITLE = "title_slide_title"
    TITLE_SLIDE_SUBTITLE = "title_slide_subtitle"
    TITLE_SLIDE_CONTENT = "title_slide_content"
    SECTION_TITLE = "section_title"
    SECTION_SUBTITLE = "section_subtitle"
    CLOSING_TITLE = "closing_title"
    CLOSING_SUBTITLE = "closing_subtitle"
    CLOSING_CONTENT = "closing_content"
    BODY_TEXT = "body_text"
    CAPTION = "caption"


class TypographyLevel(str, Enum):
    """Typography hierarchy levels matching theme tokens."""
    H1 = "h1"  # Title slide main title (72px)
    H2 = "h2"  # Slide title / Section heading (48px)
    H3 = "h3"  # Subsection heading (32px)
    H4 = "h4"  # Card/box title (24px)
    BODY = "body"  # Regular paragraph (20px)
    SUBTITLE = "subtitle"  # Slide subtitle (28px)
    CAPTION = "caption"  # Small text, footnotes (16px)


# =============================================================================
# Shared Models
# =============================================================================

class SlideContext(BaseModel):
    """Context about the current slide and presentation."""
    presentationTitle: str = Field(
        ...,
        description="Title of the presentation"
    )
    presentationTheme: Optional[str] = Field(
        None,
        description="Theme identifier (professional, minimal, bold, etc.)"
    )
    slideIndex: int = Field(
        ...,
        ge=0,
        description="Current slide index (0-based)"
    )
    slideCount: int = Field(
        ...,
        ge=1,
        description="Total number of slides in the deck"
    )
    slideTitle: Optional[str] = Field(
        None,
        description="Current slide title if available"
    )
    slideContext: Optional[str] = Field(
        None,
        description="AI-generated slide context or summary"
    )
    previousSlideContent: Optional[str] = Field(
        None,
        description="Brief summary of previous slide content"
    )
    nextSlideContent: Optional[str] = Field(
        None,
        description="Brief summary of next slide content"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentationTitle": "Q4 2024 Business Review",
                "presentationTheme": "professional",
                "slideIndex": 3,
                "slideCount": 15,
                "slideTitle": "Financial Highlights",
                "slideContext": "Key financial metrics and performance indicators",
                "previousSlideContent": "Market overview and competitive landscape",
                "nextSlideContent": "Regional breakdown of revenue"
            }
        }


class GridConstraints(BaseModel):
    """
    Grid-based constraints for content generation.

    Grid System: 32×18 grid mapping to 1920×1080px HD slide
    - Each cell is 60×60 pixels
    - Default outer padding: 10px (grid edge to element border)
    - Default inner padding: 16px (element border to text)
    """
    gridWidth: int = Field(
        ...,
        ge=1,
        le=32,
        description="Element width in grid units (1-32 columns)"
    )
    gridHeight: int = Field(
        ...,
        ge=1,
        le=18,
        description="Element height in grid units (1-18 rows)"
    )
    outerPadding: int = Field(
        default=10,
        ge=0,
        le=30,
        description="Padding from grid edge to element border in pixels"
    )
    innerPadding: int = Field(
        default=16,
        ge=0,
        le=40,
        description="Padding from element border to text in pixels"
    )
    maxCharacters: Optional[int] = Field(
        None,
        description="Override calculated max characters"
    )
    minCharacters: Optional[int] = Field(
        None,
        description="Minimum characters required"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "gridWidth": 20,
                "gridHeight": 4,
                "outerPadding": 10,
                "innerPadding": 16,
                "maxCharacters": None,
                "minCharacters": 100
            }
        }


class TextOptions(BaseModel):
    """Optional settings for text generation."""
    tone: Optional[TextTone] = Field(
        TextTone.PROFESSIONAL,
        description="Writing tone"
    )
    format: Optional[TextFormat] = Field(
        TextFormat.PARAGRAPH,
        description="Output structure"
    )
    language: Optional[str] = Field(
        "en",
        description="ISO language code"
    )
    bulletStyle: Optional[BulletStyle] = Field(
        None,
        description="Bullet style for lists"
    )
    includeEmoji: Optional[bool] = Field(
        False,
        description="Allow emoji in output"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tone": "professional",
                "format": "bullets",
                "language": "en",
                "bulletStyle": "disc",
                "includeEmoji": False
            }
        }


class TypographyConfig(BaseModel):
    """
    Typography configuration for text generation.

    Can be used to override theme defaults or specify custom typography.
    Values should match theme token structure for consistency.
    """
    fontFamily: str = Field(
        default="Poppins, sans-serif",
        description="CSS font-family value"
    )
    fontSize: int = Field(
        default=20,
        ge=10,
        le=120,
        description="Font size in pixels"
    )
    fontWeight: int = Field(
        default=400,
        ge=100,
        le=900,
        description="Font weight (100-900)"
    )
    lineHeight: float = Field(
        default=1.6,
        ge=1.0,
        le=3.0,
        description="Line height multiplier"
    )
    letterSpacing: str = Field(
        default="0",
        description="Letter spacing (CSS value like '0', '-0.02em', '0.5px')"
    )
    color: str = Field(
        default="#374151",
        description="Text color (hex or CSS color)"
    )
    textTransform: Optional[str] = Field(
        default=None,
        description="CSS text-transform (none, uppercase, lowercase, capitalize)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "fontFamily": "Poppins, sans-serif",
                "fontSize": 20,
                "fontWeight": 400,
                "lineHeight": 1.6,
                "letterSpacing": "0",
                "color": "#374151",
                "textTransform": None
            }
        }


class TextBoxStyle(BaseModel):
    """
    Text box styling for visual appearance.

    Enables transparent (default), colored, gradient, or bordered text boxes.
    """
    background: str = Field(
        default="transparent",
        description="Background color (CSS color, 'transparent', or gradient)"
    )
    backgroundGradient: Optional[str] = Field(
        default=None,
        description="CSS gradient (e.g., 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)')"
    )
    borderWidth: str = Field(
        default="0px",
        description="Border width (CSS value)"
    )
    borderColor: str = Field(
        default="transparent",
        description="Border color (CSS color)"
    )
    borderRadius: str = Field(
        default="8px",
        description="Border radius (CSS value)"
    )
    boxShadow: str = Field(
        default="none",
        description="Box shadow (CSS value)"
    )
    opacity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Element opacity (0.0-1.0)"
    )
    padding: Optional[str] = Field(
        default=None,
        description="Override inner padding (CSS value, uses GridConstraints.innerPadding if not set)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "background": "transparent",
                "backgroundGradient": None,
                "borderWidth": "0px",
                "borderColor": "transparent",
                "borderRadius": "8px",
                "boxShadow": "none",
                "opacity": 1.0,
                "padding": None
            }
        }


class ListStyle(BaseModel):
    """Styling for bullet and numbered lists."""
    bulletType: BulletStyle = Field(
        default=BulletStyle.DISC,
        description="Bullet character type"
    )
    bulletColor: Optional[str] = Field(
        default=None,
        description="Bullet color (uses theme primary if not set)"
    )
    bulletSize: str = Field(
        default="0.4em",
        description="Bullet size relative to text"
    )
    listIndent: str = Field(
        default="1.5em",
        description="List indentation from left"
    )
    itemSpacing: str = Field(
        default="0.5em",
        description="Space between list items"
    )
    numberedStyle: str = Field(
        default="decimal",
        description="Numbered list style (decimal, lower-alpha, upper-alpha, lower-roman, upper-roman)"
    )
    nestedIndent: str = Field(
        default="1.5em",
        description="Additional indent for nested lists"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "bulletType": "disc",
                "bulletColor": "#1e40af",
                "bulletSize": "0.4em",
                "listIndent": "1.5em",
                "itemSpacing": "0.5em",
                "numberedStyle": "decimal",
                "nestedIndent": "1.5em"
            }
        }


class ErrorDetails(BaseModel):
    """Error response details."""
    code: str = Field(
        ...,
        description="Error code from TextErrorCode or TableErrorCode"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    retryable: bool = Field(
        False,
        description="Whether the client should retry"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": "GENERATION_FAILED",
                "message": "LLM service returned an invalid response",
                "retryable": True
            }
        }


# =============================================================================
# Text Request Models
# =============================================================================

class TextGenerateRequest(BaseModel):
    """Request for generating new text content."""
    prompt: str = Field(
        ...,
        min_length=1,
        description="User's content description or request"
    )
    presentationId: str = Field(
        ...,
        description="UUID of the presentation"
    )
    slideId: str = Field(
        ...,
        description="UUID of the slide"
    )
    elementId: str = Field(
        ...,
        description="UUID of the target element"
    )
    context: SlideContext = Field(
        ...,
        description="Slide and presentation context"
    )
    constraints: GridConstraints = Field(
        ...,
        description="Grid-based size constraints"
    )
    options: Optional[TextOptions] = Field(
        None,
        description="Generation options"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write an executive summary about Q4 results highlighting revenue growth and market expansion",
                "presentationId": "550e8400-e29b-41d4-a716-446655440000",
                "slideId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "elementId": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
                "context": {
                    "presentationTitle": "Q4 2024 Business Review",
                    "slideIndex": 3,
                    "slideCount": 15,
                    "slideTitle": "Executive Summary"
                },
                "constraints": {
                    "gridWidth": 8,
                    "gridHeight": 4
                },
                "options": {
                    "tone": "professional",
                    "format": "paragraph"
                }
            }
        }


class TextTransformRequest(BaseModel):
    """Request for transforming existing text content."""
    sourceContent: str = Field(
        ...,
        description="Original HTML text content to transform"
    )
    transformation: TextTransformation = Field(
        ...,
        description="Type of transformation to apply"
    )
    presentationId: str = Field(
        ...,
        description="UUID of the presentation"
    )
    slideId: str = Field(
        ...,
        description="UUID of the slide"
    )
    elementId: str = Field(
        ...,
        description="UUID of the target element"
    )
    context: SlideContext = Field(
        ...,
        description="Slide and presentation context"
    )
    constraints: GridConstraints = Field(
        ...,
        description="Grid-based size constraints"
    )
    options: Optional[TextOptions] = Field(
        None,
        description="Transformation options"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sourceContent": "<p>Our Q4 revenue exceeded expectations with 15% growth year-over-year.</p>",
                "transformation": "expand",
                "presentationId": "550e8400-e29b-41d4-a716-446655440000",
                "slideId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "elementId": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
                "context": {
                    "presentationTitle": "Q4 2024 Business Review",
                    "slideIndex": 3,
                    "slideCount": 15
                },
                "constraints": {
                    "gridWidth": 8,
                    "gridHeight": 6
                }
            }
        }


class TextAutofitRequest(BaseModel):
    """Request for auto-fitting text to element dimensions."""
    content: str = Field(
        ...,
        description="Current HTML text content"
    )
    presentationId: str = Field(
        ...,
        description="UUID of the presentation"
    )
    slideId: str = Field(
        ...,
        description="UUID of the slide"
    )
    elementId: str = Field(
        ...,
        description="UUID of the target element"
    )
    targetFit: GridConstraints = Field(
        ...,
        description="Target grid dimensions"
    )
    strategy: AutofitStrategy = Field(
        AutofitStrategy.SMART_CONDENSE,
        description="Strategy for fitting content"
    )
    preserveFormatting: Optional[bool] = Field(
        True,
        description="Preserve bullets, numbering, etc."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "<ul><li>Revenue increased 15%</li><li>Market share expanded to 28%</li><li>Customer satisfaction at all-time high</li><li>New product launches successful</li></ul>",
                "presentationId": "550e8400-e29b-41d4-a716-446655440000",
                "slideId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "elementId": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
                "targetFit": {
                    "gridWidth": 4,
                    "gridHeight": 3
                },
                "strategy": "smart_condense",
                "preserveFormatting": True
            }
        }


# =============================================================================
# Slide-Specific Text Request Models (32×18 Grid)
# =============================================================================

class SlideTextRequest(BaseModel):
    """
    Request for generating slide-specific text content.

    This is the primary request model for the new slide-specific endpoints.
    Uses the 32×18 grid system with font-aware character/line calculations.
    """
    textType: SlideTextType = Field(
        ...,
        description="Type of slide text to generate"
    )
    prompt: str = Field(
        ...,
        min_length=1,
        description="Content prompt or text to format"
    )
    context: Optional[SlideContext] = Field(
        None,
        description="Slide and presentation context"
    )
    constraints: GridConstraints = Field(
        ...,
        description="Grid-based size constraints (32×18 grid)"
    )
    typography: Optional[TypographyConfig] = Field(
        None,
        description="Typography overrides (uses theme defaults if not provided)"
    )
    style: Optional[TextBoxStyle] = Field(
        None,
        description="Text box styling (transparent by default)"
    )
    listStyle: Optional[ListStyle] = Field(
        None,
        description="List/bullet styling (for bullet point content)"
    )
    themeId: Optional[str] = Field(
        default=None,
        description="Theme ID for styling (fetches from Theme Service)"
    )
    options: Optional[TextOptions] = Field(
        None,
        description="Additional text generation options"
    )
    # v1.3.0: Content context for audience/purpose-aware generation
    content_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Content context: audience, purpose, time settings"
    )

    class Config:
        extra = "ignore"  # v1.3.0: Forward compatibility
        json_schema_extra = {
            "example": {
                "textType": "slide_title",
                "prompt": "Create a title about AI transformation in healthcare",
                "constraints": {
                    "gridWidth": 28,
                    "gridHeight": 2,
                    "outerPadding": 10,
                    "innerPadding": 16
                },
                "themeId": "corporate-blue"
            }
        }


class TitleSlideRequest(BaseModel):
    """
    Request for generating complete title slide content.

    Generates title, subtitle, and optional tagline/content for title slides.
    """
    prompt: str = Field(
        ...,
        min_length=1,
        description="Content prompt for title slide"
    )
    context: Optional[SlideContext] = Field(
        None,
        description="Presentation context"
    )
    titleConstraints: GridConstraints = Field(
        ...,
        description="Grid constraints for the title element"
    )
    subtitleConstraints: Optional[GridConstraints] = Field(
        None,
        description="Grid constraints for the subtitle element"
    )
    contentConstraints: Optional[GridConstraints] = Field(
        None,
        description="Grid constraints for additional content"
    )
    typography: Optional[TypographyConfig] = Field(
        None,
        description="Typography overrides"
    )
    style: Optional[TextBoxStyle] = Field(
        None,
        description="Text box styling"
    )
    themeId: Optional[str] = Field(
        default=None,
        description="Theme ID for styling"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Annual strategy presentation for tech company focused on AI innovation",
                "titleConstraints": {
                    "gridWidth": 24,
                    "gridHeight": 3,
                    "outerPadding": 10,
                    "innerPadding": 20
                },
                "subtitleConstraints": {
                    "gridWidth": 20,
                    "gridHeight": 2
                },
                "themeId": "corporate-blue"
            }
        }


class SectionSlideRequest(BaseModel):
    """
    Request for generating section divider slide content.

    Generates section title and optional subtitle for section dividers.
    """
    prompt: str = Field(
        ...,
        min_length=1,
        description="Content prompt for section title"
    )
    context: Optional[SlideContext] = Field(
        None,
        description="Presentation context"
    )
    titleConstraints: GridConstraints = Field(
        ...,
        description="Grid constraints for the section title"
    )
    subtitleConstraints: Optional[GridConstraints] = Field(
        None,
        description="Grid constraints for section subtitle"
    )
    typography: Optional[TypographyConfig] = Field(
        None,
        description="Typography overrides"
    )
    style: Optional[TextBoxStyle] = Field(
        None,
        description="Text box styling"
    )
    themeId: Optional[str] = Field(
        default=None,
        description="Theme ID for styling"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Section about market analysis and competitive landscape",
                "titleConstraints": {
                    "gridWidth": 24,
                    "gridHeight": 3
                },
                "subtitleConstraints": {
                    "gridWidth": 20,
                    "gridHeight": 2
                },
                "themeId": "corporate-blue"
            }
        }


class ClosingSlideRequest(BaseModel):
    """
    Request for generating closing slide content.

    Generates title, subtitle, and call-to-action content for closing slides.
    """
    prompt: str = Field(
        ...,
        min_length=1,
        description="Content prompt for closing slide"
    )
    context: Optional[SlideContext] = Field(
        None,
        description="Presentation context"
    )
    titleConstraints: GridConstraints = Field(
        ...,
        description="Grid constraints for the closing title"
    )
    subtitleConstraints: Optional[GridConstraints] = Field(
        None,
        description="Grid constraints for closing subtitle"
    )
    contentConstraints: Optional[GridConstraints] = Field(
        None,
        description="Grid constraints for CTA content"
    )
    typography: Optional[TypographyConfig] = Field(
        None,
        description="Typography overrides"
    )
    style: Optional[TextBoxStyle] = Field(
        None,
        description="Text box styling"
    )
    themeId: Optional[str] = Field(
        default=None,
        description="Theme ID for styling"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Thank you slide with contact info and next steps",
                "titleConstraints": {
                    "gridWidth": 24,
                    "gridHeight": 3
                },
                "subtitleConstraints": {
                    "gridWidth": 20,
                    "gridHeight": 2
                },
                "contentConstraints": {
                    "gridWidth": 16,
                    "gridHeight": 4
                },
                "themeId": "corporate-blue"
            }
        }


class GenericTextElementRequest(BaseModel):
    """
    Request for generating a generic text element with full styling control.

    This is the most flexible request model, suitable for any text element.
    """
    prompt: str = Field(
        ...,
        min_length=1,
        description="Content prompt or text to format"
    )
    context: Optional[SlideContext] = Field(
        None,
        description="Slide and presentation context"
    )
    constraints: GridConstraints = Field(
        ...,
        description="Grid-based size constraints"
    )
    typographyLevel: Optional[TypographyLevel] = Field(
        TypographyLevel.BODY,
        description="Typography level to use from theme"
    )
    typography: Optional[TypographyConfig] = Field(
        None,
        description="Typography overrides"
    )
    style: Optional[TextBoxStyle] = Field(
        None,
        description="Text box styling"
    )
    listStyle: Optional[ListStyle] = Field(
        None,
        description="List/bullet styling"
    )
    themeId: Optional[str] = Field(
        default=None,
        description="Theme ID for styling"
    )
    options: Optional[TextOptions] = Field(
        None,
        description="Additional text generation options"
    )
    # v1.3.0: Content context for audience/purpose-aware generation
    content_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Content context: audience, purpose, time settings"
    )
    styling_mode: str = Field(
        default="inline_styles",
        description="Output mode: 'inline_styles' or 'css_classes'"
    )

    class Config:
        extra = "ignore"  # v1.3.0: Forward compatibility
        json_schema_extra = {
            "example": {
                "prompt": "Write 3 bullet points about sustainability initiatives",
                "constraints": {
                    "gridWidth": 15,
                    "gridHeight": 8
                },
                "typographyLevel": "body",
                "style": {
                    "background": "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)",
                    "borderWidth": "1px",
                    "borderColor": "#0ea5e9",
                    "borderRadius": "12px",
                    "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
                },
                "options": {
                    "format": "bullets"
                },
                "content_context": {
                    "audience": {"audience_type": "professional", "avoid_jargon": False},
                    "purpose": {"purpose_type": "inform", "include_cta": False}
                }
            }
        }


# =============================================================================
# Table Request Models
# =============================================================================

class TableStructure(BaseModel):
    """Requested table structure."""
    columns: int = Field(
        ...,
        ge=1,
        le=10,
        description="Number of columns (1-10)"
    )
    rows: int = Field(
        ...,
        ge=1,
        le=20,
        description="Number of data rows (1-20)"
    )
    hasHeader: bool = Field(
        True,
        description="First row is header"
    )
    hasFooter: Optional[bool] = Field(
        False,
        description="Last row is summary/footer"
    )


class TableStyle(BaseModel):
    """Table styling options."""
    preset: Optional[TableStylePreset] = Field(
        TableStylePreset.PROFESSIONAL,
        description="Style preset"
    )
    headerStyle: Optional[str] = Field(
        "bold",
        description="Header style: bold, highlight, minimal"
    )
    alternatingRows: Optional[bool] = Field(
        True,
        description="Use alternating row colors"
    )
    borderStyle: Optional[str] = Field(
        "light",
        description="Border style: none, light, medium, heavy"
    )
    alignment: Optional[str] = Field(
        "auto",
        description="Text alignment: left, center, right, auto"
    )


class TableDataOptions(BaseModel):
    """Options for table data formatting."""
    includeUnits: Optional[bool] = Field(
        False,
        description="Add units to numeric columns"
    )
    formatNumbers: Optional[bool] = Field(
        True,
        description="Apply number formatting"
    )
    dateFormat: Optional[str] = Field(
        None,
        description="Date format pattern"
    )
    currency: Optional[str] = Field(
        None,
        description="Currency code for money values"
    )


class TableGenerateRequest(BaseModel):
    """Request for generating a new table."""
    prompt: str = Field(
        ...,
        min_length=1,
        description="Description of table content"
    )
    presentationId: str = Field(
        ...,
        description="UUID of the presentation"
    )
    slideId: str = Field(
        ...,
        description="UUID of the slide"
    )
    elementId: str = Field(
        ...,
        description="UUID of the target element"
    )
    context: SlideContext = Field(
        ...,
        description="Slide and presentation context"
    )
    structure: Optional[TableStructure] = Field(
        None,
        description="Requested table structure (auto-calculated if not provided)"
    )
    constraints: GridConstraints = Field(
        ...,
        description="Grid-based size constraints"
    )
    style: Optional[TableStyle] = Field(
        None,
        description="Styling options"
    )
    dataOptions: Optional[TableDataOptions] = Field(
        None,
        description="Data formatting options"
    )
    seedData: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional seed data to base table on"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a comparison table of Q3 vs Q4 revenue by region",
                "presentationId": "550e8400-e29b-41d4-a716-446655440000",
                "slideId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "elementId": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
                "context": {
                    "presentationTitle": "Q4 2024 Business Review",
                    "slideIndex": 5,
                    "slideCount": 15,
                    "slideTitle": "Regional Performance"
                },
                "constraints": {
                    "gridWidth": 10,
                    "gridHeight": 5
                },
                "style": {
                    "preset": "professional",
                    "alternatingRows": True
                }
            }
        }


class TableTransformRequest(BaseModel):
    """Request for transforming a table."""
    sourceTable: str = Field(
        ...,
        description="HTML table content to transform"
    )
    transformation: TableTransformation = Field(
        ...,
        description="Type of transformation"
    )
    presentationId: str = Field(
        ...,
        description="UUID of the presentation"
    )
    slideId: str = Field(
        ...,
        description="UUID of the slide"
    )
    elementId: str = Field(
        ...,
        description="UUID of the target element"
    )
    constraints: GridConstraints = Field(
        ...,
        description="Grid-based size constraints"
    )
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Transformation-specific options"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sourceTable": "<table><thead><tr><th>Region</th><th>Q3</th><th>Q4</th></tr></thead><tbody><tr><td>North America</td><td>$45M</td><td>$52M</td></tr></tbody></table>",
                "transformation": "add_row",
                "presentationId": "550e8400-e29b-41d4-a716-446655440000",
                "slideId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "elementId": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
                "constraints": {
                    "gridWidth": 10,
                    "gridHeight": 6
                },
                "options": {
                    "content": "Add Europe region data"
                }
            }
        }


class TableAnalyzeRequest(BaseModel):
    """Request for analyzing table data."""
    sourceTable: str = Field(
        ...,
        description="HTML table content to analyze"
    )
    analysisType: TableAnalysisType = Field(
        TableAnalysisType.SUMMARY,
        description="Type of analysis to perform"
    )
    presentationId: str = Field(
        ...,
        description="UUID of the presentation"
    )
    slideId: str = Field(
        ...,
        description="UUID of the slide"
    )
    elementId: str = Field(
        ...,
        description="UUID of the target element"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sourceTable": "<table><thead><tr><th>Region</th><th>Q3</th><th>Q4</th><th>Growth</th></tr></thead><tbody><tr><td>North America</td><td>$45M</td><td>$52M</td><td>+15%</td></tr><tr><td>Europe</td><td>$32M</td><td>$38M</td><td>+19%</td></tr></tbody></table>",
                "analysisType": "summary",
                "presentationId": "550e8400-e29b-41d4-a716-446655440000",
                "slideId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "elementId": "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
            }
        }


# =============================================================================
# Response Models
# =============================================================================

class ContentMetadata(BaseModel):
    """Metadata about generated content."""
    characterCount: int = Field(
        ...,
        description="Total character count"
    )
    wordCount: int = Field(
        ...,
        description="Total word count"
    )
    estimatedReadTime: float = Field(
        ...,
        description="Estimated read time in seconds"
    )
    format: TextFormat = Field(
        ...,
        description="Detected or applied format"
    )
    tone: TextTone = Field(
        ...,
        description="Detected or applied tone"
    )


class ContentSuggestions(BaseModel):
    """Suggestions for content alternatives."""
    alternativeVersions: List[str] = Field(
        default_factory=list,
        description="Up to 3 alternative HTML versions"
    )
    expandable: bool = Field(
        False,
        description="Content can be expanded with more detail"
    )
    reducible: bool = Field(
        False,
        description="Content can be shortened"
    )


class TextContent(BaseModel):
    """Generated text content."""
    html: str = Field(
        ...,
        description="HTML content with inline CSS"
    )


class TextContentData(BaseModel):
    """Data payload for text generation response."""
    generationId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking/regeneration"
    )
    content: TextContent = Field(
        ...,
        description="Generated content"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Content metadata"
    )
    suggestions: Optional[ContentSuggestions] = Field(
        None,
        description="Alternative versions and hints"
    )


class TextGenerateResponse(BaseModel):
    """Response for text generation."""
    success: bool = Field(
        ...,
        description="Whether generation succeeded"
    )
    data: Optional[TextContentData] = Field(
        None,
        description="Generated content data"
    )
    error: Optional[ErrorDetails] = Field(
        None,
        description="Error details if failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "generationId": "550e8400-e29b-41d4-a716-446655440001",
                    "content": {
                        "html": "<p style=\"font-family: 'Inter', sans-serif; font-size: 18px; color: #1f2937; line-height: 1.6;\">Our Q4 performance exceeded all expectations, with revenue growing 15% year-over-year to reach $52 million. Market expansion initiatives drove 28% increase in customer acquisition.</p>"
                    },
                    "metadata": {
                        "characterCount": 215,
                        "wordCount": 32,
                        "estimatedReadTime": 8.5,
                        "format": "paragraph",
                        "tone": "professional"
                    },
                    "suggestions": {
                        "alternativeVersions": [
                            "<p style=\"...\">Q4 delivered exceptional results...</p>",
                            "<p style=\"...\">Revenue soared 15% in Q4...</p>"
                        ],
                        "expandable": True,
                        "reducible": False
                    }
                }
            }
        }


# =============================================================================
# Slide-Specific Response Models (32×18 Grid)
# =============================================================================

class ElementDimensions(BaseModel):
    """Calculated element dimensions from grid constraints."""
    gridWidth: int = Field(..., description="Grid columns used")
    gridHeight: int = Field(..., description="Grid rows used")
    elementWidth: float = Field(..., description="Total element width in pixels")
    elementHeight: float = Field(..., description="Total element height in pixels")
    contentWidth: float = Field(..., description="Text area width (after padding) in pixels")
    contentHeight: float = Field(..., description="Text area height (after padding) in pixels")


class TextConstraintsUsed(BaseModel):
    """Character/line constraints calculated for content generation."""
    charsPerLine: int = Field(..., description="Maximum characters per line")
    maxLines: int = Field(..., description="Maximum lines that fit")
    maxCharacters: int = Field(..., description="Total maximum characters")
    targetCharacters: int = Field(..., description="Recommended character count (90%)")
    minCharacters: int = Field(..., description="Minimum characters suggested")


class TypographyApplied(BaseModel):
    """Typography settings applied during generation."""
    fontFamily: str = Field(..., description="Font family used")
    fontSize: int = Field(..., description="Font size in pixels")
    fontWeight: int = Field(..., description="Font weight")
    lineHeight: float = Field(..., description="Line height multiplier")
    color: str = Field(..., description="Text color")
    source: str = Field(
        default="default",
        description="Source of typography: 'default', 'theme', or 'override'"
    )


class SlideTextContentData(BaseModel):
    """Data payload for slide text generation response."""
    generationId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking/regeneration"
    )
    content: str = Field(
        ...,
        description="Generated text content (may include HTML formatting)"
    )
    dimensions: ElementDimensions = Field(
        ...,
        description="Calculated element dimensions"
    )
    constraintsUsed: TextConstraintsUsed = Field(
        ...,
        description="Character/line constraints used"
    )
    typographyApplied: TypographyApplied = Field(
        ...,
        description="Typography settings applied"
    )
    characterCount: int = Field(
        ...,
        description="Actual character count of generated content"
    )
    lineCount: int = Field(
        ...,
        description="Actual line count of generated content"
    )
    fits: bool = Field(
        ...,
        description="Whether content fits within constraints"
    )


class SlideTextResponse(BaseModel):
    """Response for slide text generation endpoints."""
    success: bool = Field(..., description="Whether generation succeeded")
    data: Optional[SlideTextContentData] = Field(
        None,
        description="Generated content data"
    )
    error: Optional[ErrorDetails] = Field(
        None,
        description="Error details if failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "generationId": "550e8400-e29b-41d4-a716-446655440001",
                    "content": "Transforming Healthcare with AI",
                    "dimensions": {
                        "gridWidth": 28,
                        "gridHeight": 2,
                        "elementWidth": 1660,
                        "elementHeight": 100,
                        "contentWidth": 1628,
                        "contentHeight": 68
                    },
                    "constraintsUsed": {
                        "charsPerLine": 67,
                        "maxLines": 1,
                        "maxCharacters": 60,
                        "targetCharacters": 54,
                        "minCharacters": 12
                    },
                    "typographyApplied": {
                        "fontFamily": "Poppins, sans-serif",
                        "fontSize": 48,
                        "fontWeight": 600,
                        "lineHeight": 1.3,
                        "color": "#1f2937",
                        "source": "theme"
                    },
                    "characterCount": 34,
                    "lineCount": 1,
                    "fits": True
                }
            }
        }


class TitleSlideContentData(BaseModel):
    """Data payload for title slide generation response."""
    generationId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking"
    )
    title: SlideTextContentData = Field(..., description="Title content data")
    subtitle: Optional[SlideTextContentData] = Field(
        None,
        description="Subtitle content data"
    )
    content: Optional[SlideTextContentData] = Field(
        None,
        description="Additional content data"
    )


class TitleSlideResponse(BaseModel):
    """Response for title slide generation."""
    success: bool = Field(..., description="Whether generation succeeded")
    data: Optional[TitleSlideContentData] = Field(
        None,
        description="Generated content data"
    )
    error: Optional[ErrorDetails] = Field(
        None,
        description="Error details if failed"
    )


class SectionSlideContentData(BaseModel):
    """Data payload for section slide generation response."""
    generationId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking"
    )
    title: SlideTextContentData = Field(..., description="Section title content data")
    subtitle: Optional[SlideTextContentData] = Field(
        None,
        description="Section subtitle content data"
    )


class SectionSlideResponse(BaseModel):
    """Response for section slide generation."""
    success: bool = Field(..., description="Whether generation succeeded")
    data: Optional[SectionSlideContentData] = Field(
        None,
        description="Generated content data"
    )
    error: Optional[ErrorDetails] = Field(
        None,
        description="Error details if failed"
    )


class ClosingSlideContentData(BaseModel):
    """Data payload for closing slide generation response."""
    generationId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking"
    )
    title: SlideTextContentData = Field(..., description="Closing title content data")
    subtitle: Optional[SlideTextContentData] = Field(
        None,
        description="Closing subtitle content data"
    )
    content: Optional[SlideTextContentData] = Field(
        None,
        description="CTA content data"
    )


class ClosingSlideResponse(BaseModel):
    """Response for closing slide generation."""
    success: bool = Field(..., description="Whether generation succeeded")
    data: Optional[ClosingSlideContentData] = Field(
        None,
        description="Generated content data"
    )
    error: Optional[ErrorDetails] = Field(
        None,
        description="Error details if failed"
    )


class TransformChanges(BaseModel):
    """Changes made during transformation."""
    characterDelta: int = Field(
        ...,
        description="Character count change (positive = longer)"
    )
    significantChanges: List[str] = Field(
        default_factory=list,
        description="List of notable modifications"
    )


class TextTransformData(BaseModel):
    """Data payload for text transform response."""
    transformationId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking"
    )
    content: TextContent = Field(
        ...,
        description="Transformed content"
    )
    changes: TransformChanges = Field(
        ...,
        description="Changes made"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Content metadata"
    )


class TextTransformResponse(BaseModel):
    """Response for text transformation."""
    success: bool
    data: Optional[TextTransformData] = None
    error: Optional[ErrorDetails] = None


class AutofitResult(BaseModel):
    """Result of autofit operation."""
    content: str = Field(
        ...,
        description="Adjusted HTML content"
    )
    recommendedFontSize: Optional[int] = Field(
        None,
        description="Recommended font size in pixels"
    )
    fits: bool = Field(
        ...,
        description="Whether content fits in element"
    )
    overflow: Optional[Dict[str, Any]] = Field(
        None,
        description="Overflow details if any"
    )


class TextAutofitResponse(BaseModel):
    """Response for text autofit."""
    success: bool
    data: Optional[AutofitResult] = None
    error: Optional[ErrorDetails] = None


# =============================================================================
# Table Response Models
# =============================================================================

class TableMetadata(BaseModel):
    """Metadata about generated table."""
    rowCount: int = Field(
        ...,
        description="Number of data rows"
    )
    columnCount: int = Field(
        ...,
        description="Number of columns"
    )
    hasHeader: bool = Field(
        True,
        description="Table has header row"
    )
    hasFooter: bool = Field(
        False,
        description="Table has footer row"
    )
    columnTypes: List[str] = Field(
        default_factory=list,
        description="Detected type per column (text, numeric, date, mixed)"
    )
    hasNumericData: bool = Field(
        False,
        description="Table contains numeric data"
    )
    hasDateData: bool = Field(
        False,
        description="Table contains date data"
    )


class TableContent(BaseModel):
    """Generated table content."""
    html: str = Field(
        ...,
        description="Complete table HTML with inline CSS"
    )


class TableContentData(BaseModel):
    """Data payload for table generation response."""
    generationId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking"
    )
    content: TableContent = Field(
        ...,
        description="Generated table content"
    )
    metadata: TableMetadata = Field(
        ...,
        description="Table metadata"
    )
    editInfo: Optional[Dict[str, Any]] = Field(
        None,
        description="Edit hints (editable cells, suggested widths)"
    )


class TableGenerateResponse(BaseModel):
    """Response for table generation."""
    success: bool
    data: Optional[TableContentData] = None
    error: Optional[ErrorDetails] = None


class TableTransformData(BaseModel):
    """Data payload for table transform response."""
    transformationId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking"
    )
    content: TableContent = Field(
        ...,
        description="Transformed table content"
    )
    metadata: TableMetadata = Field(
        ...,
        description="Updated table metadata"
    )


class TableTransformResponse(BaseModel):
    """Response for table transformation."""
    success: bool
    data: Optional[TableTransformData] = None
    error: Optional[ErrorDetails] = None


class TableInsight(BaseModel):
    """Single insight from table analysis."""
    type: str = Field(
        ...,
        description="Insight type: trend, comparison, highlight, outlier"
    )
    title: str = Field(
        ...,
        description="Short insight title"
    )
    description: str = Field(
        ...,
        description="Detailed description"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)"
    )


class TableAnalysisData(BaseModel):
    """Data payload for table analysis response."""
    analysisId: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for tracking"
    )
    summary: str = Field(
        ...,
        description="Natural language summary"
    )
    insights: List[TableInsight] = Field(
        default_factory=list,
        description="List of insights"
    )
    statistics: Optional[Dict[str, Any]] = Field(
        None,
        description="Column statistics if applicable"
    )
    recommendations: Optional[Dict[str, Any]] = Field(
        None,
        description="Recommendations (chart type, highlighting, sorting)"
    )
    metadata: TableMetadata = Field(
        ...,
        description="Table metadata"
    )


class TableAnalyzeResponse(BaseModel):
    """Response for table analysis."""
    success: bool
    data: Optional[TableAnalysisData] = None
    error: Optional[ErrorDetails] = None
