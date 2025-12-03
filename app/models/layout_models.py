"""
Layout Service Integration Models for Text & Table Builder v1.2

Pydantic models for the Layout Service API endpoints that enable
grid-based text and table generation with constraint-aware HTML+CSS output.

Endpoints:
- POST /api/ai/text/generate - Generate new text content
- POST /api/ai/text/transform - Transform existing text
- POST /api/ai/text/autofit - Fit text to element dimensions
- POST /api/ai/table/generate - Generate structured table
- POST /api/ai/table/transform - Modify table structure
- POST /api/ai/table/analyze - Get insights from table data
"""

from enum import Enum
from typing import List, Dict, Any, Optional
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
    """Grid-based constraints for content generation."""
    gridWidth: int = Field(
        ...,
        ge=1,
        le=12,
        description="Element width in grid units (1-12 columns)"
    )
    gridHeight: int = Field(
        ...,
        ge=1,
        le=8,
        description="Element height in grid units (1-8 rows)"
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
                "gridWidth": 6,
                "gridHeight": 4,
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
