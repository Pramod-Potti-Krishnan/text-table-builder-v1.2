"""
Layout Service API Routes for Text & Table Builder v1.2

Provides endpoints for the Layout Service integration enabling
grid-based text and table generation with constraint-aware HTML+CSS output.

Text Endpoints:
- POST /api/ai/text/generate - Generate new text content from prompt
- POST /api/ai/text/transform - Transform existing text (expand, condense, etc.)
- POST /api/ai/text/autofit - Fit text to element dimensions

Table Endpoints:
- POST /api/ai/table/generate - Generate structured table from prompt
- POST /api/ai/table/transform - Modify table structure/content
- POST /api/ai/table/analyze - Get insights from table data

Architecture:
- Each endpoint uses a specialized generator class
- All generators use async LLM service for FastAPI compatibility
- Output is HTML with inline CSS for reveal.js integration
- Grid constraints (12x8) determine content size limits
"""

from fastapi import APIRouter, Depends
from typing import Callable
import logging

from app.core.layout import (
    GridCalculator,
    TextGenerateGenerator,
    TextTransformGenerator,
    TextAutofitGenerator,
    TableGenerateGenerator,
    TableTransformGenerator,
    TableAnalyzeGenerator
)
from app.models.layout_models import (
    # Text models
    TextGenerateRequest,
    TextGenerateResponse,
    TextTransformRequest,
    TextTransformResponse,
    TextAutofitRequest,
    TextAutofitResponse,
    # Table models
    TableGenerateRequest,
    TableGenerateResponse,
    TableTransformRequest,
    TableTransformResponse,
    TableAnalyzeRequest,
    TableAnalyzeResponse,
    # Shared models
    ErrorDetails
)
from app.services import create_llm_callable_async

logger = logging.getLogger(__name__)

# Create router for Layout Service endpoints
router = APIRouter(prefix="/api/ai", tags=["layout", "ai"])


# =============================================================================
# Dependencies
# =============================================================================

def get_async_llm_service() -> Callable:
    """
    Get async LLM service for Layout Service generation.

    Uses the same async LLM service as content slides for consistency.
    Uses Vertex AI with Application Default Credentials (ADC).

    Returns:
        Async callable that takes prompt string and returns content string
    """
    return create_llm_callable_async()


# Text generator dependencies
def get_text_generate_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> TextGenerateGenerator:
    """Create TextGenerateGenerator instance."""
    return TextGenerateGenerator(llm_service)


def get_text_transform_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> TextTransformGenerator:
    """Create TextTransformGenerator instance."""
    return TextTransformGenerator(llm_service)


def get_text_autofit_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> TextAutofitGenerator:
    """Create TextAutofitGenerator instance."""
    return TextAutofitGenerator(llm_service)


# Table generator dependencies
def get_table_generate_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> TableGenerateGenerator:
    """Create TableGenerateGenerator instance."""
    return TableGenerateGenerator(llm_service)


def get_table_transform_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> TableTransformGenerator:
    """Create TableTransformGenerator instance."""
    return TableTransformGenerator(llm_service)


def get_table_analyze_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> TableAnalyzeGenerator:
    """Create TableAnalyzeGenerator instance."""
    return TableAnalyzeGenerator(llm_service)


# =============================================================================
# Text Endpoints
# =============================================================================

@router.post("/text/generate", response_model=TextGenerateResponse)
async def generate_text(
    request: TextGenerateRequest,
    generator: TextGenerateGenerator = Depends(get_text_generate_generator)
) -> TextGenerateResponse:
    """
    Generate new text content based on prompt and grid constraints.

    The Layout Service calls this endpoint when a user creates a new text element
    and provides a prompt. The content is sized to fit within the grid dimensions.

    **Request Body**:
    - prompt: User's content description (e.g., "Write an executive summary about Q4 results")
    - presentationId: UUID of the presentation
    - slideId: UUID of the slide
    - elementId: UUID of the target element
    - context: Slide context (presentationTitle, slideIndex, slideCount, etc.)
    - constraints: Grid constraints (gridWidth 1-12, gridHeight 1-8)
    - options: Optional settings (tone, format, bulletStyle, includeEmoji)

    **Response**:
    - success: Whether generation succeeded
    - data: Generated content with metadata and suggestions
      - generationId: UUID for tracking
      - content.html: HTML content with inline CSS
      - metadata: characterCount, wordCount, estimatedReadTime, format, tone
      - suggestions: alternativeVersions (up to 3), expandable, reducible

    **Grid Constraints**:
    - gridWidth: 1-12 columns (each ~80px at 960px slide width)
    - gridHeight: 1-8 rows (each ~90px at 720px slide height)
    - Character limits calculated automatically from grid dimensions

    **Example Request**:
    ```json
    {
        "prompt": "Write 3 bullet points about revenue growth",
        "presentationId": "550e8400-e29b-41d4-a716-446655440000",
        "slideId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "elementId": "elem-001",
        "context": {
            "presentationTitle": "Q4 Review",
            "slideIndex": 3,
            "slideCount": 15
        },
        "constraints": {"gridWidth": 6, "gridHeight": 4},
        "options": {"tone": "professional", "format": "bullets"}
    }
    ```
    """
    try:
        logger.info(
            f"Generating text content for element {request.elementId} "
            f"(grid: {request.constraints.gridWidth}x{request.constraints.gridHeight})"
        )
        result = await generator.generate(request)
        logger.info(f"Text generation successful for element {request.elementId}")
        return result

    except ValueError as e:
        logger.error(f"Validation error in text generation: {e}")
        return TextGenerateResponse(
            success=False,
            error=ErrorDetails(
                code="INVALID_PROMPT",
                message=str(e),
                retryable=False
            )
        )

    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        return TextGenerateResponse(
            success=False,
            error=ErrorDetails(
                code="GENERATION_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/text/transform", response_model=TextTransformResponse)
async def transform_text(
    request: TextTransformRequest,
    generator: TextTransformGenerator = Depends(get_text_transform_generator)
) -> TextTransformResponse:
    """
    Transform existing text content.

    Applies various transformations to existing HTML content while respecting
    grid constraints. Useful for expanding, condensing, or reformatting content.

    **Transformations Available**:
    - expand: Add more detail and explanation
    - condense: Shorten while keeping key points
    - simplify: Use simpler language
    - formalize: Make more professional
    - casualize: Make more conversational
    - bulletize: Convert to bullet points
    - paragraphize: Convert bullets to paragraphs
    - rephrase: Rewrite with different words
    - proofread: Fix grammar and spelling
    - translate: Translate to different language

    **Request Body**:
    - sourceContent: Original HTML content to transform
    - transformation: Type of transformation to apply
    - presentationId, slideId, elementId: IDs for tracking
    - context: Slide context
    - constraints: Grid constraints for output size

    **Response**:
    - success: Whether transformation succeeded
    - data: Transformed content with change tracking
      - transformationId: UUID for tracking
      - content.html: Transformed HTML
      - changes: characterDelta, significantChanges
      - metadata: Updated character counts, etc.

    **Example Request**:
    ```json
    {
        "sourceContent": "<p>Our Q4 revenue grew 15%.</p>",
        "transformation": "expand",
        "presentationId": "...",
        "slideId": "...",
        "elementId": "...",
        "context": {"presentationTitle": "Q4 Review", "slideIndex": 3, "slideCount": 15},
        "constraints": {"gridWidth": 8, "gridHeight": 4}
    }
    ```
    """
    try:
        logger.info(
            f"Transforming text ({request.transformation.value}) for element {request.elementId}"
        )
        result = await generator.generate(request)
        logger.info(f"Text transformation successful for element {request.elementId}")
        return result

    except ValueError as e:
        logger.error(f"Validation error in text transformation: {e}")
        return TextTransformResponse(
            success=False,
            error=ErrorDetails(
                code="INVALID_PROMPT",
                message=str(e),
                retryable=False
            )
        )

    except Exception as e:
        logger.error(f"Text transformation failed: {e}")
        return TextTransformResponse(
            success=False,
            error=ErrorDetails(
                code="TRANSFORM_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/text/autofit", response_model=TextAutofitResponse)
async def autofit_text(
    request: TextAutofitRequest,
    generator: TextAutofitGenerator = Depends(get_text_autofit_generator)
) -> TextAutofitResponse:
    """
    Auto-fit text content to element dimensions.

    When text overflows an element, this endpoint can help fit it using
    various strategies.

    **Strategies Available**:
    - reduce_font: Suggest a smaller font size
    - truncate: Cut content with ellipsis
    - smart_condense: AI-powered content shortening (preserves meaning)
    - overflow: Return unchanged (allow overflow)

    **Request Body**:
    - content: Current HTML text content
    - presentationId, slideId, elementId: IDs for tracking
    - targetFit: Grid constraints to fit within
    - strategy: How to handle overflow
    - preserveFormatting: Keep bullets/numbering (default: true)

    **Response**:
    - success: Whether autofit succeeded
    - data: Fitted content
      - content: Adjusted HTML (may be unchanged)
      - recommendedFontSize: Suggested font size (for reduce_font strategy)
      - fits: Whether content now fits
      - overflow: Overflow details if any

    **Example Request**:
    ```json
    {
        "content": "<ul><li>Point 1</li><li>Point 2</li>...</ul>",
        "presentationId": "...",
        "slideId": "...",
        "elementId": "...",
        "targetFit": {"gridWidth": 4, "gridHeight": 3},
        "strategy": "smart_condense",
        "preserveFormatting": true
    }
    ```
    """
    try:
        logger.info(
            f"Auto-fitting text ({request.strategy.value}) for element {request.elementId}"
        )
        result = await generator.generate(request)
        logger.info(f"Text autofit successful for element {request.elementId}")
        return result

    except ValueError as e:
        logger.error(f"Validation error in text autofit: {e}")
        return TextAutofitResponse(
            success=False,
            error=ErrorDetails(
                code="INVALID_PROMPT",
                message=str(e),
                retryable=False
            )
        )

    except Exception as e:
        logger.error(f"Text autofit failed: {e}")
        return TextAutofitResponse(
            success=False,
            error=ErrorDetails(
                code="AUTOFIT_FAILED",
                message=str(e),
                retryable=True
            )
        )


# =============================================================================
# Table Endpoints
# =============================================================================

@router.post("/table/generate", response_model=TableGenerateResponse)
async def generate_table(
    request: TableGenerateRequest,
    generator: TableGenerateGenerator = Depends(get_table_generate_generator)
) -> TableGenerateResponse:
    """
    Generate a new table from prompt and grid constraints.

    Creates an HTML table with data relevant to the user's prompt.
    Table dimensions are automatically calculated based on grid size.

    **Request Body**:
    - prompt: Description of table content (e.g., "Q3 vs Q4 revenue by region")
    - presentationId, slideId, elementId: IDs for tracking
    - context: Slide context
    - structure: Optional requested structure (columns, rows, hasHeader, hasFooter)
    - constraints: Grid constraints (determines max columns/rows)
    - style: Optional styling (preset, headerStyle, alternatingRows, borderStyle)
    - dataOptions: Optional data formatting (includeUnits, formatNumbers, currency)
    - seedData: Optional data to base the table on

    **Style Presets**:
    - minimal: Clean, borderless
    - bordered: All borders visible
    - striped: Alternating row colors
    - modern: Contemporary with gradients
    - professional: Corporate blue theme
    - colorful: Vibrant pink/purple theme

    **Response**:
    - success: Whether generation succeeded
    - data: Generated table
      - generationId: UUID for tracking
      - content.html: Complete table HTML with inline CSS
      - metadata: rowCount, columnCount, columnTypes, etc.
      - editInfo: editableCells, suggestedColumnWidths

    **Example Request**:
    ```json
    {
        "prompt": "Create a comparison table of Q3 vs Q4 revenue by region",
        "presentationId": "...",
        "slideId": "...",
        "elementId": "...",
        "context": {"presentationTitle": "Q4 Review", "slideIndex": 5, "slideCount": 15},
        "constraints": {"gridWidth": 10, "gridHeight": 5},
        "style": {"preset": "professional", "alternatingRows": true}
    }
    ```
    """
    try:
        logger.info(
            f"Generating table for element {request.elementId} "
            f"(grid: {request.constraints.gridWidth}x{request.constraints.gridHeight})"
        )
        result = await generator.generate(request)
        logger.info(f"Table generation successful for element {request.elementId}")
        return result

    except ValueError as e:
        logger.error(f"Validation error in table generation: {e}")
        return TableGenerateResponse(
            success=False,
            error=ErrorDetails(
                code="INVALID_STRUCTURE",
                message=str(e),
                retryable=False
            )
        )

    except Exception as e:
        logger.error(f"Table generation failed: {e}")
        return TableGenerateResponse(
            success=False,
            error=ErrorDetails(
                code="GENERATION_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/table/transform", response_model=TableTransformResponse)
async def transform_table(
    request: TableTransformRequest,
    generator: TableTransformGenerator = Depends(get_table_transform_generator)
) -> TableTransformResponse:
    """
    Transform existing table structure or content.

    Modifies an existing HTML table by adding/removing rows or columns,
    sorting, summarizing, or other structural changes.

    **Transformations Available**:
    - add_column: Add a new column (optionally at specific position)
    - add_row: Add a new row (optionally at specific position)
    - remove_column: Remove column at index
    - remove_row: Remove row at index
    - sort: Sort by column in asc/desc order
    - summarize: Add totals/averages row
    - transpose: Swap rows and columns
    - expand: Add more rows with similar data
    - merge_cells: Merge adjacent cells with same values
    - split_column: Split column into multiple columns

    **Request Body**:
    - sourceTable: HTML table to transform
    - transformation: Type of transformation
    - presentationId, slideId, elementId: IDs for tracking
    - constraints: Grid constraints for output size
    - options: Transformation-specific options

    **Options by Transformation**:
    - add_column/add_row: position, content
    - remove_column/remove_row: index
    - sort: sortColumn, sortDirection (asc/desc)
    - summarize: summaryType (totals/averages/counts)
    - expand: expandPrompt

    **Example Request**:
    ```json
    {
        "sourceTable": "<table>...</table>",
        "transformation": "add_row",
        "presentationId": "...",
        "slideId": "...",
        "elementId": "...",
        "constraints": {"gridWidth": 10, "gridHeight": 6},
        "options": {"content": "Add Europe region data"}
    }
    ```
    """
    try:
        logger.info(
            f"Transforming table ({request.transformation.value}) for element {request.elementId}"
        )
        result = await generator.generate(request)
        logger.info(f"Table transformation successful for element {request.elementId}")
        return result

    except ValueError as e:
        logger.error(f"Validation error in table transformation: {e}")
        return TableTransformResponse(
            success=False,
            error=ErrorDetails(
                code="INVALID_STRUCTURE",
                message=str(e),
                retryable=False
            )
        )

    except Exception as e:
        logger.error(f"Table transformation failed: {e}")
        return TableTransformResponse(
            success=False,
            error=ErrorDetails(
                code="TRANSFORM_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/table/analyze", response_model=TableAnalyzeResponse)
async def analyze_table(
    request: TableAnalyzeRequest,
    generator: TableAnalyzeGenerator = Depends(get_table_analyze_generator)
) -> TableAnalyzeResponse:
    """
    Analyze table data and return insights.

    Examines an HTML table and provides natural language insights,
    statistics, and recommendations.

    **Analysis Types**:
    - summary: Key statistics and main takeaways
    - trends: Patterns, correlations, growth/decline
    - outliers: Unusual values and anomalies
    - visualization: Recommended chart type for the data

    **Request Body**:
    - sourceTable: HTML table to analyze
    - analysisType: Type of analysis to perform
    - presentationId, slideId, elementId: IDs for tracking

    **Response**:
    - success: Whether analysis succeeded
    - data: Analysis results
      - analysisId: UUID for tracking
      - summary: Natural language summary
      - insights: List of insights (type, title, description, confidence)
      - statistics: Column-level statistics (min, max, average, etc.)
      - recommendations: suggestedChartType, suggestedHighlights, suggestedSorting
      - metadata: Table metadata

    **Example Request**:
    ```json
    {
        "sourceTable": "<table><thead><tr><th>Region</th><th>Q3</th><th>Q4</th></tr></thead>...</table>",
        "analysisType": "summary",
        "presentationId": "...",
        "slideId": "...",
        "elementId": "..."
    }
    ```
    """
    try:
        logger.info(
            f"Analyzing table ({request.analysisType.value}) for element {request.elementId}"
        )
        result = await generator.generate(request)
        logger.info(f"Table analysis successful for element {request.elementId}")
        return result

    except ValueError as e:
        logger.error(f"Validation error in table analysis: {e}")
        return TableAnalyzeResponse(
            success=False,
            error=ErrorDetails(
                code="INVALID_STRUCTURE",
                message=str(e),
                retryable=False
            )
        )

    except Exception as e:
        logger.error(f"Table analysis failed: {e}")
        return TableAnalyzeResponse(
            success=False,
            error=ErrorDetails(
                code="ANALYSIS_FAILED",
                message=str(e),
                retryable=True
            )
        )


# =============================================================================
# Utility Endpoints
# =============================================================================

@router.get("/health")
async def layout_health_check():
    """
    Health check endpoint for Layout Service integration.

    Returns status and capability information for all Layout Service endpoints.
    """
    return {
        "status": "healthy",
        "service": "Text & Table Builder v1.2 - Layout Service Integration",
        "endpoints": {
            "text": {
                "generate": "/api/ai/text/generate",
                "transform": "/api/ai/text/transform",
                "autofit": "/api/ai/text/autofit"
            },
            "table": {
                "generate": "/api/ai/table/generate",
                "transform": "/api/ai/table/transform",
                "analyze": "/api/ai/table/analyze"
            }
        },
        "grid_system": {
            "columns": 12,
            "rows": 8,
            "description": "12-column x 8-row grid system for element sizing"
        },
        "capabilities": {
            "text_tones": ["professional", "conversational", "academic", "persuasive", "casual", "technical"],
            "text_formats": ["paragraph", "bullets", "numbered", "headline", "quote", "mixed"],
            "text_transformations": ["expand", "condense", "simplify", "formalize", "casualize", "bulletize", "paragraphize", "rephrase", "proofread", "translate"],
            "table_styles": ["minimal", "bordered", "striped", "modern", "professional", "colorful"],
            "table_transformations": ["add_column", "add_row", "remove_column", "remove_row", "sort", "summarize", "transpose", "expand", "merge_cells", "split_column"]
        }
    }


@router.get("/constraints/{grid_width}/{grid_height}")
async def get_grid_constraints(grid_width: int, grid_height: int):
    """
    Get content guidelines for specific grid dimensions.

    Useful for the Layout Service to understand content limits before
    calling generation endpoints.

    **Path Parameters**:
    - grid_width: Grid width (1-12)
    - grid_height: Grid height (1-8)

    **Response**:
    - Grid validation result
    - Character limits (min, max, target)
    - Word limits
    - Layout info (lines, chars per line)
    - Format recommendations
    - Table dimensions (for table elements)
    """
    # Validate grid
    validation = GridCalculator.validate_grid_constraints(grid_width, grid_height)

    if not validation["valid"]:
        return {
            "valid": False,
            "errors": validation["errors"],
            "warnings": validation["warnings"]
        }

    # Get text guidelines
    text_guidelines = GridCalculator.get_content_guidelines(
        validation["grid_width"],
        validation["grid_height"]
    )

    # Get table guidelines
    table_guidelines = GridCalculator.calculate_table_dimensions(
        validation["grid_width"],
        validation["grid_height"]
    )

    return {
        "valid": True,
        "grid": {
            "width": validation["grid_width"],
            "height": validation["grid_height"],
            "area": validation["grid_area"]
        },
        "text": text_guidelines,
        "table": table_guidelines,
        "warnings": validation["warnings"]
    }
