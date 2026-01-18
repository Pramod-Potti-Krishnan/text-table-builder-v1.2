"""
Atomic Component API Routes for Text & Table Builder v1.2
==========================================================

Provides dedicated endpoints for direct atomic component generation
at /v1.2/atomic/{TYPE} paths. These endpoints bypass the Chain of Thought
reasoning layer for deterministic, fast generation with explicit parameterization.

Endpoints:
- POST /v1.2/atomic/METRICS - Generate 1-4 metric cards
- POST /v1.2/atomic/SEQUENTIAL - Generate 1-6 numbered steps
- POST /v1.2/atomic/COMPARISON - Generate 1-4 comparison columns
- POST /v1.2/atomic/SECTIONS - Generate 1-5 colored sections
- POST /v1.2/atomic/CALLOUT - Generate 1-2 callout boxes

Features:
- Explicit control over component type and count
- Flexible bullet/item counts for SECTIONS, COMPARISON, CALLOUT
- Grid-based space calculation (32x18 system)
- Context-aware content generation
- Placeholder mode for instant generation without LLM

v1.1.0: Added count=1 support for all types + placeholder_mode
v1.0.0: Initial atomic component endpoints
"""

import asyncio
import logging
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException

from app.core.components.atomic_generator import AtomicComponentGenerator
from app.models.atomic_models import (
    AtomicType,
    LayoutType,
    ATOMIC_TYPE_MAP,
    AtomicComponentResponse,
    AtomicMetadata,
    MetricsAtomicRequest,
    SequentialAtomicRequest,
    ComparisonAtomicRequest,
    SectionsAtomicRequest,
    CalloutAtomicRequest,
    TextBulletsAtomicRequest,
    BulletBoxAtomicRequest,
    TableAtomicRequest,
    NumberedListAtomicRequest,
    TextBoxAtomicRequest
)
from app.services import create_llm_callable_async

logger = logging.getLogger(__name__)

# Create router for Atomic Component endpoints
router = APIRouter(prefix="/v1.2/atomic", tags=["atomic", "components"])


# =============================================================================
# Dependencies
# =============================================================================

def get_async_llm_service() -> Callable:
    """
    Get async LLM service for atomic component generation.

    Uses Vertex AI with Application Default Credentials (ADC).

    Returns:
        Async callable that takes prompt string and returns content string
    """
    return create_llm_callable_async()


def get_atomic_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> AtomicComponentGenerator:
    """Create AtomicComponentGenerator instance."""
    return AtomicComponentGenerator(llm_service=llm_service)


# =============================================================================
# Helper Functions
# =============================================================================

def _calculate_position(request) -> dict | None:
    """
    Calculate grid position from request. Returns None if no position specified.

    Grid System:
    - 32 columns x 18 rows
    - Cell size: 60px per unit (1920x1080 slide)
    - Content safe zone: rows 4-17, cols 2-31
    - CSS Grid format: grid_row="start/end", grid_column="start/end"

    Args:
        request: AtomicComponentRequest with optional start_col, start_row,
                 position_width, position_height fields

    Returns:
        Dict with position info or None if no position specified
    """
    # Only calculate position if at least one position field is specified
    if request.start_col is None and request.start_row is None:
        return None

    # Use defaults if not specified
    start_col = request.start_col if request.start_col is not None else 2
    start_row = request.start_row if request.start_row is not None else 4
    width = request.position_width if request.position_width is not None else request.gridWidth
    height = request.position_height if request.position_height is not None else request.gridHeight

    # Calculate end positions (CSS Grid uses exclusive end)
    end_row = min(start_row + height, 19)
    end_col = min(start_col + width, 33)

    return {
        "start_col": start_col,
        "start_row": start_row,
        "width": width,
        "height": height,
        "grid_row": f"{start_row}/{end_row}",
        "grid_column": f"{start_col}/{end_col}"
    }


def _build_response(result, position_data: dict | None = None) -> AtomicComponentResponse:
    """Convert AtomicResult to AtomicComponentResponse."""
    return AtomicComponentResponse(
        success=result.success,
        html=result.html if result.success else None,
        component_type=result.component_type,
        instance_count=result.instance_count,
        arrangement=result.arrangement,
        variants_used=result.variants_used,
        character_counts=result.character_counts,
        metadata=result.metadata,
        error=result.error,
        grid_position=position_data
    )


# =============================================================================
# POST /v1.2/atomic/METRICS
# =============================================================================

@router.post("/METRICS", response_model=AtomicComponentResponse)
async def generate_metrics(
    request: MetricsAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate METRICS atomic component (1-4 gradient metric cards).

    Each metric card contains:
    - metric_number: The main value (e.g., "95%", "$2.4M", "1.2x")
    - metric_label: Short UPPERCASE label (e.g., "REVENUE GROWTH")
    - metric_description: Supporting context sentence

    **Request Body**:
    - prompt: Content request describing metrics to generate
    - count: Number of metric cards (1-4, default: 3)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Q4 performance: revenue up 23%, customers grew 45%, margin improved to 18%",
        "count": 3,
        "gridWidth": 28,
        "gridHeight": 8
    }
    ```

    **Color Variants**: purple, pink, cyan, green
    """
    try:
        # Calculate grid position if specified
        position_data = _calculate_position(request)

        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.METRICS],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=None,  # Metrics don't have flexible items
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols,
            metrics_config=request.metrics_config
        )
        return _build_response(result, position_data)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-METRICS-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/SEQUENTIAL
# =============================================================================

@router.post("/SEQUENTIAL", response_model=AtomicComponentResponse)
async def generate_sequential(
    request: SequentialAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate SEQUENTIAL atomic component (1-6 numbered step cards).

    Each numbered card contains:
    - card_number: Step number (1-6)
    - card_title: Step title (e.g., "Discovery Phase")
    - card_description: Detailed explanation

    **Request Body**:
    - prompt: Content request describing the process/steps
    - count: Number of steps (1-6, default: 4)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Employee onboarding process: orientation, training, mentorship, evaluation",
        "count": 4,
        "gridWidth": 28,
        "gridHeight": 10
    }
    ```

    **Color Variants**: blue, green, yellow, pink
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.SEQUENTIAL],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=None,  # Sequential cards don't have flexible items
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-SEQUENTIAL-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/COMPARISON
# =============================================================================

@router.post("/COMPARISON", response_model=AtomicComponentResponse)
async def generate_comparison(
    request: ComparisonAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate COMPARISON atomic component (1-4 comparison columns).

    Each comparison column contains:
    - column_heading: Column title (e.g., "Option A", "Pros", "Before")
    - item_1 through item_N: Comparison points (1-7 items per column)

    **Request Body**:
    - prompt: Content request describing comparison
    - count: Number of columns (1-4, default: 3)
    - items_per_column: Items per column (1-7, default: 5)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Compare Standard, Professional, and Enterprise pricing plans",
        "count": 3,
        "items_per_column": 5,
        "gridWidth": 28,
        "gridHeight": 14
    }
    ```

    **Color Variants**: blue, red, green, purple, orange
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.COMPARISON],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.items_per_column,
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-COMPARISON-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/SECTIONS
# =============================================================================

@router.post("/SECTIONS", response_model=AtomicComponentResponse)
async def generate_sections(
    request: SectionsAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate SECTIONS atomic component (1-5 colored sections with bullets).

    Each section contains:
    - section_heading: Section title (e.g., "Key Benefits", "Phase 1")
    - bullet_1 through bullet_N: Bullet points (1-5 bullets per section)

    **Request Body**:
    - prompt: Content request describing sections
    - count: Number of sections (1-5, default: 3)
    - bullets_per_section: Bullets per section (1-5, default: 3)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Sustainability initiative benefits: cost savings, brand reputation, environmental impact",
        "count": 3,
        "bullets_per_section": 4,
        "gridWidth": 24,
        "gridHeight": 12
    }
    ```

    **Color Variants**: blue, red, green, amber, purple
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.SECTIONS],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.bullets_per_section,
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-SECTIONS-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/CALLOUT
# =============================================================================

@router.post("/CALLOUT", response_model=AtomicComponentResponse)
async def generate_callout(
    request: CalloutAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate CALLOUT atomic component (1-2 sidebar/callout boxes).

    Each callout box contains:
    - sidebar_heading: Box heading (e.g., "Key Insights", "Remember")
    - item_1 through item_N: Bullet points (1-7 items per box)

    **Request Body**:
    - prompt: Content request describing callout content
    - count: Number of callout boxes (1-2, default: 1)
    - items_per_box: Items per box (1-7, default: 4)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Key takeaways from our market analysis",
        "count": 1,
        "items_per_box": 5,
        "gridWidth": 10,
        "gridHeight": 12
    }
    ```

    **Color Variants**: blue, green, purple, amber
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.CALLOUT],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.items_per_box,
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-CALLOUT-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/TEXT_BULLETS
# =============================================================================

@router.post("/TEXT_BULLETS", response_model=AtomicComponentResponse)
async def generate_text_bullets(
    request: TextBulletsAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate TEXT_BULLETS atomic component (1-4 simple text boxes with bullets).

    Each text box contains:
    - subtitle: Section subtitle/heading
    - bullet_1 through bullet_N: Bullet points (1-7 bullets per box)

    **Request Body**:
    - prompt: Content request describing the bullet content
    - count: Number of text boxes (1-4, default: 2)
    - bullets_per_box: Bullets per box (1-7, default: 4)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Key features of our new product: performance, reliability, ease of use",
        "count": 2,
        "bullets_per_box": 4,
        "gridWidth": 24,
        "gridHeight": 10
    }
    ```

    **Color Variants**: white, light_gray, light_blue, light_purple
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.TEXT_BULLETS],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.bullets_per_box,
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-TEXT_BULLETS-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/BULLET_BOX
# =============================================================================

@router.post("/BULLET_BOX", response_model=AtomicComponentResponse)
async def generate_bullet_box(
    request: BulletBoxAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate BULLET_BOX atomic component (1-4 rectangular bordered boxes).

    Each bullet box contains:
    - box_heading: Box heading/title
    - item_1 through item_N: Bullet items (1-7 items per box)

    **Request Body**:
    - prompt: Content request describing the box content
    - count: Number of boxes (1-4, default: 2)
    - items_per_box: Items per box (1-7, default: 5)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Project deliverables for Phase 1 and Phase 2",
        "count": 2,
        "items_per_box": 5,
        "gridWidth": 24,
        "gridHeight": 12
    }
    ```

    **Color Variants**: gray, blue, green, purple, amber
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.BULLET_BOX],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.items_per_box,
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-BULLET_BOX-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/TABLE
# =============================================================================

@router.post("/TABLE", response_model=AtomicComponentResponse)
async def generate_table(
    request: TableAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate TABLE atomic component (1-2 HTML tables).

    Each table contains:
    - header_1 through header_N: Column headers
    - rowX_colY: Cell content for each row/column

    **Request Body**:
    - prompt: Content request describing the table data
    - count: Number of tables (1-2, default: 1)
    - columns: Columns per table (2-6, default: 3)
    - rows: Data rows per table (2-10, default: 4)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Compare pricing plans: Basic, Pro, Enterprise with features and pricing",
        "count": 1,
        "columns": 3,
        "rows": 4,
        "gridWidth": 28,
        "gridHeight": 10
    }
    ```

    **Color Variants**: gray, blue, green, purple
    """
    try:
        # Calculate grid position if specified
        position_data = _calculate_position(request)

        # For TABLE, we need special handling since it has columns AND rows
        # items_per_instance will represent the structure as columns * rows
        table_structure = {"columns": request.columns, "rows": request.rows}

        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.TABLE],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.rows,  # Pass rows as items_per_instance
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols,
            table_config=request.table_config
        )
        return _build_response(result, position_data)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-TABLE-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/NUMBERED_LIST
# =============================================================================

@router.post("/NUMBERED_LIST", response_model=AtomicComponentResponse)
async def generate_numbered_list(
    request: NumberedListAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate NUMBERED_LIST atomic component (1-4 numbered lists).

    Each numbered list contains:
    - list_title: List title/heading
    - item_1 through item_N: Numbered items (1-10 items per list)

    **Request Body**:
    - prompt: Content request describing the list content
    - count: Number of lists (1-4, default: 2)
    - items_per_list: Items per list (1-10, default: 5)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request**:
    ```json
    {
        "prompt": "Top 5 priorities for Q1: hiring, product launch, market expansion...",
        "count": 2,
        "items_per_list": 5,
        "gridWidth": 24,
        "gridHeight": 12
    }
    ```

    **Color Variants**: blue, green, purple, amber, gray
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.NUMBERED_LIST],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.items_per_list,
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-NUMBERED_LIST-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/TEXT_BOX
# =============================================================================

@router.post("/TEXT_BOX", response_model=AtomicComponentResponse)
async def generate_text_box(
    request: TextBoxAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate TEXT_BOX atomic component (1-6 configurable text boxes).

    Each text box contains:
    - box_heading: Title for the box
    - item_1 through item_N: Content items (1-7 per box)

    **Request Body**:
    - prompt: Content request describing what to generate
    - count: Number of text boxes (1-6, default: 3)
    - items_per_box: Items per box (1-7, default: 4)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - color_variant: Simple color name (purple, blue, red, green, yellow, cyan, orange, teal, pink, indigo) - auto-selects matching accent variant
    - variant: Full variant ID (alternative to color_variant)
    - theme_mode: 'light' or 'dark' - affects text colors for accent variants
    - background_style: 'colored' or 'transparent'
    - color_scheme: 'gradient', 'solid', or 'accent'
    - list_style: 'bullets', 'numbers', or 'none'
    - context: Optional slide/presentation context
    - placeholder_mode: If true, use placeholder content (no LLM call)

    **Example Request with color_variant** (recommended):
    ```json
    {
        "prompt": "Key product features: performance, security, ease of use",
        "count": 3,
        "items_per_box": 4,
        "gridWidth": 28,
        "gridHeight": 12,
        "color_variant": "green",
        "theme_mode": "light"
    }
    ```

    **Simple Color Names** (maps to accent variants with pastel backgrounds):
    purple, blue, red, green, yellow, cyan, orange, teal, pink, indigo

    When using color_variant, all associated colors are automatically applied:
    - Pastel background for the box
    - Dark-colored heading font (for plain/highlighted title_style)
    - Dark badge with white text (for colored-bg title_style)

    **Full Accent Variant IDs** (use with 'variant' parameter):
    accent_1_purple, accent_2_blue, accent_3_red, accent_4_green, accent_5_yellow,
    accent_6_cyan, accent_7_orange, accent_8_teal, accent_9_pink, accent_10_indigo

    **Legacy Gradient Variants**: gradient_purple, gradient_pink, gradient_cyan, gradient_green, gradient_orange, gradient_pastel
    """
    try:
        # Calculate grid position if specified
        position_data = _calculate_position(request)

        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.TEXT_BOX],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.items_per_box,
            context=request.context,
            variant=request.variant,
            placeholder_mode=request.placeholder_mode,
            transparency=request.transparency,
            layout=request.layout,
            grid_cols=request.grid_cols,
            theme_mode=request.theme_mode,
            heading_align=request.heading_align,
            content_align=request.content_align,
            title_min_chars=request.title_min_chars,
            title_max_chars=request.title_max_chars,
            item_min_chars=request.item_min_chars,
            item_max_chars=request.item_max_chars,
            list_style=request.list_style,
            use_lorem_ipsum=request.use_lorem_ipsum,
            # New styling parameters
            background_style=request.background_style,
            color_scheme=request.color_scheme,
            corners=request.corners,
            border=request.border,
            title_style=request.title_style,
            show_title=request.show_title,
            existing_colors=request.existing_colors
        )
        return _build_response(result, position_data)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-TEXT_BOX-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# GET /v1.2/atomic/health
# =============================================================================

@router.get("/health")
async def atomic_health():
    """
    Health check for atomic component endpoints.

    Returns available atomic component types and their configurations.
    """
    return {
        "status": "healthy",
        "service": "atomic-components",
        "version": "1.2.0",
        "features": {
            "placeholder_mode": True,
            "single_element_support": True,
            "layout_options": ["horizontal", "vertical", "grid"],
            "transparency_control": True
        },
        "endpoints": {
            "METRICS": {
                "path": "/v1.2/atomic/METRICS",
                "component_id": "metrics_card",
                "count_range": "1-4",
                "flexible_items": False
            },
            "SEQUENTIAL": {
                "path": "/v1.2/atomic/SEQUENTIAL",
                "component_id": "numbered_card",
                "count_range": "1-6",
                "flexible_items": False
            },
            "COMPARISON": {
                "path": "/v1.2/atomic/COMPARISON",
                "component_id": "comparison_column",
                "count_range": "1-4",
                "flexible_items": True,
                "items_range": "1-7 items per column"
            },
            "SECTIONS": {
                "path": "/v1.2/atomic/SECTIONS",
                "component_id": "colored_section",
                "count_range": "1-5",
                "flexible_items": True,
                "items_range": "1-5 bullets per section"
            },
            "CALLOUT": {
                "path": "/v1.2/atomic/CALLOUT",
                "component_id": "sidebar_box",
                "count_range": "1-2",
                "flexible_items": True,
                "items_range": "1-7 items per box"
            },
            "TEXT_BULLETS": {
                "path": "/v1.2/atomic/TEXT_BULLETS",
                "component_id": "text_bullets",
                "count_range": "1-4",
                "flexible_items": True,
                "items_range": "1-7 bullets per box"
            },
            "BULLET_BOX": {
                "path": "/v1.2/atomic/BULLET_BOX",
                "component_id": "bullet_box",
                "count_range": "1-4",
                "flexible_items": True,
                "items_range": "1-7 items per box"
            },
            "TABLE": {
                "path": "/v1.2/atomic/TABLE",
                "component_id": "table_basic",
                "count_range": "1-2",
                "flexible_items": True,
                "columns_range": "2-6",
                "rows_range": "2-10"
            },
            "NUMBERED_LIST": {
                "path": "/v1.2/atomic/NUMBERED_LIST",
                "component_id": "numbered_list",
                "count_range": "1-4",
                "flexible_items": True,
                "items_range": "1-10 items per list"
            },
            "TEXT_BOX": {
                "path": "/v1.2/atomic/TEXT_BOX",
                "component_id": "text_box",
                "count_range": "1-6",
                "flexible_items": True,
                "items_range": "1-7 items per box"
            }
        },
        "grid_system": {
            "columns": 32,
            "rows": 18,
            "cell_size_px": 60,
            "slide_dimensions": "1920x1080"
        }
    }


# =============================================================================
# GET /v1.2/atomic/components
# =============================================================================

@router.get("/components")
async def list_atomic_components():
    """
    List all available atomic component types.

    Returns detailed specifications for each atomic component.
    """
    return {
        "components": [
            {
                "type": "METRICS",
                "component_id": "metrics_card",
                "description": "Gradient-filled metric cards with large numbers, labels, and descriptions",
                "use_cases": ["KPIs", "statistics", "performance metrics", "data points"],
                "slots": ["metric_number", "metric_label", "metric_description"],
                "instance_range": {"min": 1, "max": 4},
                "variants": ["purple", "pink", "cyan", "green"],
                "flexible_items": False,
                "supports_placeholder_mode": True,
                "default_transparency": 1.0
            },
            {
                "type": "SEQUENTIAL",
                "component_id": "numbered_card",
                "description": "Numbered step cards for processes, phases, or sequential items",
                "use_cases": ["steps", "phases", "workflows", "processes"],
                "slots": ["card_number", "card_title", "card_description"],
                "instance_range": {"min": 1, "max": 6},
                "variants": ["blue", "green", "yellow", "pink"],
                "flexible_items": False,
                "supports_placeholder_mode": True,
                "default_transparency": 0.6
            },
            {
                "type": "COMPARISON",
                "component_id": "comparison_column",
                "description": "Comparison columns with headings and flexible item lists",
                "use_cases": ["comparisons", "pros/cons", "options", "alternatives"],
                "slots": ["column_heading", "item_1..item_N"],
                "instance_range": {"min": 1, "max": 4},
                "items_per_instance_range": {"min": 1, "max": 7},
                "variants": ["blue", "red", "green", "purple", "orange"],
                "flexible_items": True,
                "supports_placeholder_mode": True,
                "default_transparency": 0.6
            },
            {
                "type": "SECTIONS",
                "component_id": "colored_section",
                "description": "Colored sections with headings and flexible bullet lists",
                "use_cases": ["categories", "topics", "grouped content", "key points"],
                "slots": ["section_heading", "bullet_1..bullet_N"],
                "instance_range": {"min": 1, "max": 5},
                "items_per_instance_range": {"min": 1, "max": 5},
                "variants": ["blue", "red", "green", "amber", "purple"],
                "flexible_items": True,
                "supports_placeholder_mode": True,
                "default_transparency": 0.6
            },
            {
                "type": "CALLOUT",
                "component_id": "sidebar_box",
                "description": "Gradient callout boxes with headings and flexible item lists",
                "use_cases": ["key insights", "highlights", "takeaways", "tips"],
                "slots": ["sidebar_heading", "item_1..item_N"],
                "instance_range": {"min": 1, "max": 2},
                "items_per_instance_range": {"min": 1, "max": 7},
                "variants": ["blue", "green", "purple", "amber"],
                "flexible_items": True,
                "supports_placeholder_mode": True,
                "default_transparency": 0.6
            },
            {
                "type": "TEXT_BULLETS",
                "component_id": "text_bullets",
                "description": "Simple text boxes with subtitle and bullet points",
                "use_cases": ["key points", "features", "benefits", "summary items"],
                "slots": ["subtitle", "bullet_1..bullet_N"],
                "instance_range": {"min": 1, "max": 4},
                "items_per_instance_range": {"min": 1, "max": 7},
                "variants": ["white", "light_gray", "light_blue", "light_purple"],
                "flexible_items": True,
                "supports_placeholder_mode": True,
                "default_transparency": 0.6
            },
            {
                "type": "BULLET_BOX",
                "component_id": "bullet_box",
                "description": "Rectangular boxes with sharp corners and borders for formal content",
                "use_cases": ["formal lists", "structured content", "boxed information"],
                "slots": ["box_heading", "item_1..item_N"],
                "instance_range": {"min": 1, "max": 4},
                "items_per_instance_range": {"min": 1, "max": 7},
                "variants": ["gray", "blue", "green", "purple", "amber"],
                "flexible_items": True,
                "supports_placeholder_mode": True,
                "default_transparency": 0.6
            },
            {
                "type": "TABLE",
                "component_id": "table_basic",
                "description": "Clean HTML tables with header row and data rows",
                "use_cases": ["data tables", "comparison tables", "feature matrices", "schedules"],
                "slots": ["header_1..header_N", "rowX_colY"],
                "instance_range": {"min": 1, "max": 2},
                "columns_range": {"min": 2, "max": 6},
                "rows_range": {"min": 2, "max": 10},
                "variants": ["gray", "blue", "green", "purple"],
                "flexible_items": True,
                "supports_placeholder_mode": True,
                "default_transparency": 0.6
            },
            {
                "type": "NUMBERED_LIST",
                "component_id": "numbered_list",
                "description": "Numbered lists with title and ordered items",
                "use_cases": ["ordered lists", "priorities", "rankings", "step-by-step"],
                "slots": ["list_title", "item_1..item_N"],
                "instance_range": {"min": 1, "max": 4},
                "items_per_instance_range": {"min": 1, "max": 10},
                "variants": ["blue", "green", "purple", "amber", "gray"],
                "flexible_items": True,
                "supports_placeholder_mode": True,
                "default_transparency": 0.6
            },
            {
                "type": "TEXT_BOX",
                "component_id": "text_box",
                "description": "Configurable text boxes with pastel or gradient backgrounds and dark/light mode support",
                "use_cases": ["key points", "features", "benefits", "grouped content", "section summaries"],
                "slots": ["box_heading", "item_1..item_N"],
                "instance_range": {"min": 1, "max": 6},
                "items_per_instance_range": {"min": 1, "max": 7},
                "variants": [
                    "accent_1_purple", "accent_2_blue", "accent_3_red", "accent_4_green", "accent_5_yellow",
                    "accent_6_cyan", "accent_7_orange", "accent_8_teal", "accent_9_pink", "accent_10_indigo",
                    "gradient_purple", "gradient_pink", "gradient_cyan", "gradient_green", "gradient_orange", "gradient_pastel"
                ],
                "theme_mode_support": True,
                "flexible_items": True,
                "supports_placeholder_mode": True,
                "default_transparency": 1.0
            }
        ]
    }
