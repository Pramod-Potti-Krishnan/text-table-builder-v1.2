"""
Layout Service API Routes for Text & Table Builder v1.2

Provides endpoints for the Layout Service integration enabling
grid-based text and table generation with constraint-aware HTML+CSS output.

Grid System: 32×18 grid (1920×1080px HD slides, 60×60px cells)

Text Endpoints:
- POST /api/ai/text/generate - Generate new text content from prompt
- POST /api/ai/text/transform - Transform existing text (expand, condense, etc.)
- POST /api/ai/text/autofit - Fit text to element dimensions

Slide-Specific Endpoints (32×18 grid):
- POST /api/ai/slide/title - Generate slide title (h2)
- POST /api/ai/slide/subtitle - Generate slide subtitle
- POST /api/ai/slide/title-slide - Generate complete title slide content
- POST /api/ai/slide/section - Generate section divider content
- POST /api/ai/slide/closing - Generate closing slide content
- POST /api/ai/element/text - Generate generic text element

Table Endpoints:
- POST /api/ai/table/generate - Generate structured table from prompt
- POST /api/ai/table/transform - Modify table structure/content
- POST /api/ai/table/analyze - Get insights from table data

Architecture:
- Each endpoint uses a specialized generator class
- All generators use async LLM service for FastAPI compatibility
- Output is HTML with inline CSS for reveal.js integration
- Grid constraints (32×18) determine content size limits
"""

from fastapi import APIRouter, Depends
from typing import Callable, Optional
import logging

from app.core.components import (
    ComponentAssemblyAgent,
    AgentResult
)
from app.core.layout import (
    GridCalculator,
    TextGenerateGenerator,
    TextTransformGenerator,
    TextAutofitGenerator,
    TableGenerateGenerator,
    TableTransformGenerator,
    TableAnalyzeGenerator,
    # New slide text generators
    SlideTextGenerator,
    TitleSlideGenerator,
    SectionSlideGenerator,
    ClosingSlideGenerator,
    GenericTextElementGenerator
)
from app.models.layout_models import (
    # Text models
    TextGenerateRequest,
    TextGenerateResponse,
    TextTransformRequest,
    TextTransformResponse,
    TextAutofitRequest,
    TextAutofitResponse,
    # Slide-specific text models (32×18 grid)
    SlideTextRequest,
    SlideTextResponse,
    SlideTextContentData,
    ElementDimensions,
    TextConstraintsUsed,
    TypographyApplied,
    TitleSlideRequest,
    TitleSlideResponse,
    SectionSlideRequest,
    SectionSlideResponse,
    ClosingSlideRequest,
    ClosingSlideResponse,
    GenericTextElementRequest,
    SlideTextType,
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
from app.services.theme_service_client import ThemeServiceClient

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


# Slide text generator dependencies (32×18 grid)
_theme_client: ThemeServiceClient = None


def get_theme_client() -> ThemeServiceClient:
    """Get or create singleton ThemeServiceClient."""
    global _theme_client
    if _theme_client is None:
        _theme_client = ThemeServiceClient()
    return _theme_client


def get_slide_text_generator(
    llm_service: Callable = Depends(get_async_llm_service),
    theme_client: ThemeServiceClient = Depends(get_theme_client)
) -> SlideTextGenerator:
    """Create SlideTextGenerator instance with theme support."""
    return SlideTextGenerator(llm_service, theme_client)


def get_title_slide_generator(
    llm_service: Callable = Depends(get_async_llm_service),
    theme_client: ThemeServiceClient = Depends(get_theme_client)
) -> TitleSlideGenerator:
    """Create TitleSlideGenerator instance with theme support."""
    return TitleSlideGenerator(llm_service, theme_client)


def get_section_slide_generator(
    llm_service: Callable = Depends(get_async_llm_service),
    theme_client: ThemeServiceClient = Depends(get_theme_client)
) -> SectionSlideGenerator:
    """Create SectionSlideGenerator instance with theme support."""
    return SectionSlideGenerator(llm_service, theme_client)


def get_closing_slide_generator(
    llm_service: Callable = Depends(get_async_llm_service),
    theme_client: ThemeServiceClient = Depends(get_theme_client)
) -> ClosingSlideGenerator:
    """Create ClosingSlideGenerator instance with theme support."""
    return ClosingSlideGenerator(llm_service, theme_client)


def get_generic_text_generator(
    llm_service: Callable = Depends(get_async_llm_service),
    theme_client: ThemeServiceClient = Depends(get_theme_client)
) -> GenericTextElementGenerator:
    """Create GenericTextElementGenerator instance with theme support."""
    return GenericTextElementGenerator(llm_service, theme_client)


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
# Slide-Specific Text Endpoints (32×18 Grid System)
# =============================================================================

@router.post("/slide/title", response_model=SlideTextResponse)
async def generate_slide_title(
    request: SlideTextRequest,
    generator: SlideTextGenerator = Depends(get_slide_text_generator)
) -> SlideTextResponse:
    """
    Generate slide title text with precise character constraints.

    Uses the 32×18 grid system (1920×1080px HD slides) with font-aware
    character calculations for accurate content sizing.

    **Grid System**:
    - 32 columns × 18 rows
    - Each cell: 60×60 pixels
    - Default outer padding: 10px (grid edge to element)
    - Default inner padding: 16px (element border to text)

    **Request Body**:
    - textType: Type of text (slide_title, slide_subtitle, etc.)
    - prompt: Content prompt or text to generate
    - context: Optional slide context
    - constraints: Grid constraints (gridWidth 1-32, gridHeight 1-18, padding)
    - typography: Optional typography overrides
    - themeId: Optional theme ID for styling

    **Response**:
    - success: Whether generation succeeded
    - data: Generated content with dimension/constraint metadata
      - content: Generated text
      - dimensions: Element and content dimensions in pixels
      - constraintsUsed: Character/line limits calculated
      - typographyApplied: Typography settings used
      - fits: Whether content fits within constraints

    **Example Request**:
    ```json
    {
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
    ```
    """
    try:
        # Ensure correct text type for slide title
        if request.textType not in [SlideTextType.SLIDE_TITLE, SlideTextType.SLIDE_SUBTITLE]:
            request.textType = SlideTextType.SLIDE_TITLE

        logger.info(
            f"Generating slide title (grid: {request.constraints.gridWidth}×{request.constraints.gridHeight})"
        )
        result = await generator.generate(request)
        logger.info(f"Slide title generation successful")
        return result

    except Exception as e:
        logger.error(f"Slide title generation failed: {e}")
        return SlideTextResponse(
            success=False,
            error=ErrorDetails(
                code="GENERATION_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/slide/subtitle", response_model=SlideTextResponse)
async def generate_slide_subtitle(
    request: SlideTextRequest,
    generator: SlideTextGenerator = Depends(get_slide_text_generator)
) -> SlideTextResponse:
    """
    Generate slide subtitle text with precise character constraints.

    Similar to /slide/title but optimized for subtitle typography (smaller font,
    lighter weight, secondary color).

    **Example Request**:
    ```json
    {
        "textType": "slide_subtitle",
        "prompt": "Supporting text for healthcare AI presentation",
        "constraints": {
            "gridWidth": 20,
            "gridHeight": 2
        },
        "themeId": "corporate-blue"
    }
    ```
    """
    try:
        # Ensure correct text type for slide subtitle
        request.textType = SlideTextType.SLIDE_SUBTITLE

        logger.info(
            f"Generating slide subtitle (grid: {request.constraints.gridWidth}×{request.constraints.gridHeight})"
        )
        result = await generator.generate(request)
        logger.info(f"Slide subtitle generation successful")
        return result

    except Exception as e:
        logger.error(f"Slide subtitle generation failed: {e}")
        return SlideTextResponse(
            success=False,
            error=ErrorDetails(
                code="GENERATION_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/slide/title-slide", response_model=TitleSlideResponse)
async def generate_title_slide(
    request: TitleSlideRequest,
    generator: TitleSlideGenerator = Depends(get_title_slide_generator)
) -> TitleSlideResponse:
    """
    Generate complete title slide content (title + subtitle + optional content).

    Generates all text elements for a title slide in one call, with each
    element sized appropriately based on its constraints.

    **Request Body**:
    - prompt: Content prompt for title slide theme
    - context: Optional presentation context
    - titleConstraints: Grid constraints for the title (required)
    - subtitleConstraints: Grid constraints for subtitle (optional)
    - contentConstraints: Grid constraints for additional content (optional)
    - typography: Optional typography overrides
    - themeId: Optional theme ID

    **Response**:
    - success: Whether generation succeeded
    - data: Generated content for each element
      - title: Title text with constraints
      - subtitle: Subtitle text with constraints (if requested)
      - content: Additional content (if requested)

    **Example Request**:
    ```json
    {
        "prompt": "Annual strategy presentation for tech company focused on AI innovation",
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
    ```
    """
    try:
        logger.info(
            f"Generating title slide (title grid: {request.titleConstraints.gridWidth}×{request.titleConstraints.gridHeight})"
        )
        result = await generator.generate(request)
        logger.info(f"Title slide generation successful")
        return result

    except Exception as e:
        logger.error(f"Title slide generation failed: {e}")
        return TitleSlideResponse(
            success=False,
            error=ErrorDetails(
                code="GENERATION_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/slide/section", response_model=SectionSlideResponse)
async def generate_section_slide(
    request: SectionSlideRequest,
    generator: SectionSlideGenerator = Depends(get_section_slide_generator)
) -> SectionSlideResponse:
    """
    Generate section divider slide content (title + optional subtitle).

    Creates text for section divider slides that separate presentation sections.

    **Request Body**:
    - prompt: Section theme or topic
    - context: Optional presentation context
    - titleConstraints: Grid constraints for section title (required)
    - subtitleConstraints: Grid constraints for subtitle (optional)
    - typography: Optional typography overrides
    - themeId: Optional theme ID

    **Example Request**:
    ```json
    {
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
    ```
    """
    try:
        logger.info(
            f"Generating section slide (title grid: {request.titleConstraints.gridWidth}×{request.titleConstraints.gridHeight})"
        )
        result = await generator.generate(request)
        logger.info(f"Section slide generation successful")
        return result

    except Exception as e:
        logger.error(f"Section slide generation failed: {e}")
        return SectionSlideResponse(
            success=False,
            error=ErrorDetails(
                code="GENERATION_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/slide/closing", response_model=ClosingSlideResponse)
async def generate_closing_slide(
    request: ClosingSlideRequest,
    generator: ClosingSlideGenerator = Depends(get_closing_slide_generator)
) -> ClosingSlideResponse:
    """
    Generate closing slide content (title + subtitle + CTA content).

    Creates text for closing slides with call-to-action or contact information.

    **Request Body**:
    - prompt: Closing slide theme (thank you, next steps, contact info, etc.)
    - context: Optional presentation context
    - titleConstraints: Grid constraints for closing title (required)
    - subtitleConstraints: Grid constraints for subtitle (optional)
    - contentConstraints: Grid constraints for CTA content (optional)
    - typography: Optional typography overrides
    - themeId: Optional theme ID

    **Example Request**:
    ```json
    {
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
    ```
    """
    try:
        logger.info(
            f"Generating closing slide (title grid: {request.titleConstraints.gridWidth}×{request.titleConstraints.gridHeight})"
        )
        result = await generator.generate(request)
        logger.info(f"Closing slide generation successful")
        return result

    except Exception as e:
        logger.error(f"Closing slide generation failed: {e}")
        return ClosingSlideResponse(
            success=False,
            error=ErrorDetails(
                code="GENERATION_FAILED",
                message=str(e),
                retryable=True
            )
        )


@router.post("/element/text", response_model=SlideTextResponse)
async def generate_text_element(
    request: GenericTextElementRequest,
    generator: GenericTextElementGenerator = Depends(get_generic_text_generator)
) -> SlideTextResponse:
    """
    Generate generic text element with full styling control.

    v1.4.0: Now uses component-based agentic generation by default.
    The agent reasons about storytelling needs and selects appropriate
    components (metrics cards, numbered cards, comparison columns, etc.)
    to produce Gold Standard-quality output.

    **Request Body**:
    - prompt: Content prompt or text to generate
    - context: Optional slide context
    - constraints: Grid constraints (1-32 columns, 1-18 rows)
    - typographyLevel: Typography level (h1, h2, h3, h4, body, subtitle, caption)
    - typography: Optional typography overrides
    - style: Optional text box styling (background, border, shadow, etc.)
    - listStyle: Optional list/bullet styling
    - themeId: Optional theme ID
    - use_components: Enable component-based generation (default: True)
    - audience: Target audience (executive, technical, general, educational, sales)
    - purpose: Slide purpose (inform, persuade, compare, explain, inspire)
    - component_hints: Optional hints for component selection

    **Typography Levels**:
    - h1: 72px, weight 700, line-height 1.2 (title slide title)
    - h2: 48px, weight 600, line-height 1.3 (slide title)
    - h3: 32px, weight 600, line-height 1.4 (subsection)
    - h4: 24px, weight 600, line-height 1.4 (card title)
    - body: 20px, weight 400, line-height 1.6 (regular text)
    - subtitle: 28px, weight 400, line-height 1.5 (subtitle)
    - caption: 16px, weight 400, line-height 1.4 (small text)

    **Component Types** (selected automatically by agent):
    - metrics_card: KPIs, statistics, performance numbers
    - numbered_card: Steps, phases, sequential items
    - comparison_column: Comparing options, pros/cons
    - colored_section: Categories with bullet lists
    - sidebar_box: Key insights, highlights, callouts

    **Example Request**:
    ```json
    {
        "prompt": "Show our Q4 performance with key metrics",
        "constraints": {
            "gridWidth": 15,
            "gridHeight": 8
        },
        "audience": "executive",
        "purpose": "inform"
    }
    ```
    """
    try:
        # v1.4.0: Use component-based generation if enabled
        if getattr(request, 'use_components', True):
            logger.info(
                f"[COMPONENT-AGENT] Generating with components "
                f"(grid: {request.constraints.gridWidth}×{request.constraints.gridHeight}, "
                f"audience: {getattr(request, 'audience', None)}, "
                f"purpose: {getattr(request, 'purpose', None)})"
            )

            # Get LLM service from generator
            llm_service = generator.llm_service

            # Create component assembly agent
            agent = ComponentAssemblyAgent(llm_service=llm_service)

            # Generate using component-based approach
            agent_result: AgentResult = await agent.generate(
                prompt=request.prompt,
                grid_width=request.constraints.gridWidth,
                grid_height=request.constraints.gridHeight,
                audience=getattr(request, 'audience', None),
                purpose=getattr(request, 'purpose', None),
                presentation_title=request.context.presentationTitle if request.context else None
            )

            if agent_result.success:
                logger.info(
                    f"[COMPONENT-AGENT] Success: {agent_result.assembly_info.component_type} "
                    f"x{agent_result.assembly_info.component_count} "
                    f"({agent_result.assembly_info.arrangement})"
                )

                # Calculate pixel dimensions
                pixel_width = request.constraints.gridWidth * 60  # 60px per cell
                pixel_height = request.constraints.gridHeight * 60
                content_width = pixel_width - 2 * (request.constraints.outerPadding + request.constraints.innerPadding)
                content_height = pixel_height - 2 * (request.constraints.outerPadding + request.constraints.innerPadding)

                # Build response with component metadata
                return SlideTextResponse(
                    success=True,
                    data=SlideTextContentData(
                        content=agent_result.html,
                        dimensions=ElementDimensions(
                            gridWidth=request.constraints.gridWidth,
                            gridHeight=request.constraints.gridHeight,
                            elementWidth=float(pixel_width),
                            elementHeight=float(pixel_height),
                            contentWidth=float(content_width),
                            contentHeight=float(content_height)
                        ),
                        constraintsUsed=TextConstraintsUsed(
                            charsPerLine=0,  # Component-based doesn't use char limits
                            maxLines=0,
                            maxCharacters=0,
                            targetCharacters=0,
                            minCharacters=0
                        ),
                        typographyApplied=TypographyApplied(
                            fontFamily="Poppins, sans-serif",
                            fontSize=20,
                            fontWeight=400,
                            lineHeight=1.6,
                            color="#374151",
                            source="component"
                        ),
                        characterCount=len(agent_result.html),
                        lineCount=agent_result.html.count('\n') + 1,
                        fits=True,
                        assembly_info={
                            "component_type": agent_result.assembly_info.component_type,
                            "component_count": agent_result.assembly_info.component_count,
                            "arrangement": agent_result.assembly_info.arrangement,
                            "variants_used": agent_result.assembly_info.variants_used,
                            "agent_reasoning": agent_result.assembly_info.agent_reasoning
                        } if agent_result.assembly_info else None
                    )
                )
            else:
                # Component generation failed, fall back to legacy generation
                component_error = agent_result.error
                logger.warning(
                    f"[COMPONENT-AGENT] Failed: {component_error}, falling back to legacy"
                )
                # Add debug info to help diagnose
                logger.error(
                    f"[COMPONENT-AGENT] Debug: reasoning={agent_result.reasoning}"
                )

        else:
            component_error = None

        # Legacy text generation (fallback or when use_components=False)
        logger.info(
            f"Generating text element (grid: {request.constraints.gridWidth}×{request.constraints.gridHeight}, "
            f"level: {request.typographyLevel})"
        )
        result = await generator.generate_from_request(request)
        logger.info(f"Text element generation successful")

        # Add component debug info to response if we fell back from component generation
        if getattr(request, 'use_components', True) and 'component_error' in locals() and component_error:
            # Inject debug info into the response data
            if result.data:
                result.data.assembly_info = {"debug_error": component_error}

        return result

    except Exception as e:
        logger.error(f"Text element generation failed: {e}")
        return SlideTextResponse(
            success=False,
            error=ErrorDetails(
                code="GENERATION_FAILED",
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
    Updated for 32×18 grid system (1920×1080px HD slides).
    """
    # Get grid info from calculator for accuracy
    grid_info = GridCalculator.get_grid_info()

    return {
        "status": "healthy",
        "service": "Text & Table Builder v1.2 - Layout Service Integration",
        "version": "2.0",
        "endpoints": {
            "text": {
                "generate": "/api/ai/text/generate",
                "transform": "/api/ai/text/transform",
                "autofit": "/api/ai/text/autofit"
            },
            "slide_text": {
                "title": "/api/ai/slide/title",
                "subtitle": "/api/ai/slide/subtitle",
                "title_slide": "/api/ai/slide/title-slide",
                "section": "/api/ai/slide/section",
                "closing": "/api/ai/slide/closing",
                "element": "/api/ai/element/text"
            },
            "table": {
                "generate": "/api/ai/table/generate",
                "transform": "/api/ai/table/transform",
                "analyze": "/api/ai/table/analyze"
            }
        },
        "grid_system": {
            "columns": GridCalculator.GRID_COLUMNS,  # 32
            "rows": GridCalculator.GRID_ROWS,  # 18
            "slide_width": GridCalculator.SLIDE_WIDTH,  # 1920px
            "slide_height": GridCalculator.SLIDE_HEIGHT,  # 1080px
            "cell_width": GridCalculator.CELL_WIDTH,  # 60px
            "cell_height": GridCalculator.CELL_HEIGHT,  # 60px
            "description": "32×18 grid system for HD slides (1920×1080px, 60px cells)"
        },
        "default_padding": {
            "outer": GridCalculator.DEFAULT_OUTER_PADDING,  # 10px
            "inner": GridCalculator.DEFAULT_INNER_PADDING,  # 16px
            "description": "Outer = grid edge to element border, Inner = element border to text"
        },
        "typography_defaults": grid_info.get("typography_defaults", {}),
        "capabilities": {
            "text_tones": ["professional", "conversational", "academic", "persuasive", "casual", "technical"],
            "text_formats": ["paragraph", "bullets", "numbered", "headline", "quote", "mixed"],
            "text_transformations": ["expand", "condense", "simplify", "formalize", "casualize", "bulletize", "paragraphize", "rephrase", "proofread", "translate"],
            "slide_text_types": ["slide_title", "slide_subtitle", "title_slide_title", "title_slide_subtitle", "section_title", "closing_title", "closing_subtitle"],
            "typography_levels": ["h1", "h2", "h3", "h4", "body", "subtitle", "caption"],
            "table_styles": ["minimal", "bordered", "striped", "modern", "professional", "colorful"],
            "table_transformations": ["add_column", "add_row", "remove_column", "remove_row", "sort", "summarize", "transpose", "expand", "merge_cells", "split_column"]
        }
    }


@router.get("/constraints/{grid_width}/{grid_height}")
async def get_grid_constraints(grid_width: int, grid_height: int):
    """
    Get content guidelines for specific grid dimensions.

    Useful for the Layout Service to understand content limits before
    calling generation endpoints. Updated for 32×18 grid system.

    **Path Parameters**:
    - grid_width: Grid columns (1-32)
    - grid_height: Grid rows (1-18)

    **Grid System**:
    - 32 columns × 18 rows (1920×1080px HD slides)
    - Each cell: 60×60 pixels
    - Default outer padding: 10px
    - Default inner padding: 16px

    **Response**:
    - Grid validation result
    - Character limits (min, max, target) based on typography
    - Word limits
    - Layout info (lines, chars per line)
    - Format recommendations
    - Table dimensions (for table elements)

    **Example**: /constraints/24/3 returns constraints for a 24-column × 3-row element
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
