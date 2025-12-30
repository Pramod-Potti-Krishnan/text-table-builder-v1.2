"""
Constraints and Space Calculations for Component Assembly
==========================================================

Handles:
- Space analysis using 32x18 grid system (1920x1080 HD)
- Character limit scaling based on available space
- Arrangement determination for component instances
- Variant assignment strategies

Grid System:
- Full slide: 32 columns x 18 rows
- Each cell: 60px x 60px
- Content area: typically 28x14 (after slide padding)
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from ...models.component_models import (
    SpaceAnalysis,
    CharLimits,
    LayoutSelection,
    ComponentDefinition,
    ArrangementType,
    SlotSpec
)


# =============================================================================
# Constants
# =============================================================================

# Grid system constants (HD 1920x1080)
GRID_COLUMNS = 32
GRID_ROWS = 18
CELL_SIZE_PX = 60

# Full slide dimensions
SLIDE_WIDTH_PX = 1920
SLIDE_HEIGHT_PX = 1080

# Typical content area (after slide header/footer)
DEFAULT_CONTENT_COLUMNS = 28
DEFAULT_CONTENT_ROWS = 14

# Default gaps and padding
DEFAULT_GAP_PX = 24
DEFAULT_PADDING_PX = 40


# =============================================================================
# Space Calculator
# =============================================================================

class SpaceCalculator:
    """
    Calculates available space and what components can fit.

    Uses the 32x18 grid system where each cell is 60px.
    """

    def __init__(
        self,
        grid_columns: int = GRID_COLUMNS,
        grid_rows: int = GRID_ROWS,
        cell_size: int = CELL_SIZE_PX
    ):
        self.grid_columns = grid_columns
        self.grid_rows = grid_rows
        self.cell_size = cell_size

    def analyze_space(
        self,
        grid_width: int,
        grid_height: int,
        padding_px: int = DEFAULT_PADDING_PX
    ) -> SpaceAnalysis:
        """
        Analyze available space for component placement.

        Args:
            grid_width: Available width in grid units
            grid_height: Available height in grid units
            padding_px: Padding around content area

        Returns:
            SpaceAnalysis with detailed space information
        """
        # Calculate pixel dimensions
        total_width_px = grid_width * self.cell_size
        total_height_px = grid_height * self.cell_size

        # Calculate usable area after padding
        usable_width_px = max(0, total_width_px - (2 * padding_px))
        usable_height_px = max(0, total_height_px - (2 * padding_px))

        # Determine space category
        space_category = self._categorize_space(grid_width, grid_height)

        # Calculate recommended counts for each component type
        recommended_counts = self._calculate_recommended_counts(
            grid_width, grid_height, usable_width_px, usable_height_px
        )

        # Determine valid layout options
        layout_options = self._determine_layout_options(grid_width, grid_height)

        return SpaceAnalysis(
            grid_width=grid_width,
            grid_height=grid_height,
            total_width_px=total_width_px,
            total_height_px=total_height_px,
            usable_width_px=usable_width_px,
            usable_height_px=usable_height_px,
            recommended_counts=recommended_counts,
            layout_options=layout_options,
            space_category=space_category
        )

    def _categorize_space(self, grid_width: int, grid_height: int) -> str:
        """Categorize space as small, medium, or large."""
        area = grid_width * grid_height

        if area < 48:  # Less than 8x6
            return "small"
        elif area < 120:  # Less than 12x10
            return "medium"
        else:
            return "large"

    def _calculate_recommended_counts(
        self,
        grid_width: int,
        grid_height: int,
        usable_width_px: int,
        usable_height_px: int
    ) -> Dict[str, int]:
        """Calculate recommended instance count per component type."""
        counts = {}

        # Metrics cards: need ~400px width each
        metrics_per_row = max(2, min(4, usable_width_px // 400))
        counts["metrics_card"] = metrics_per_row

        # Numbered cards: 2x2 or 3x2 grid
        if grid_height >= 12 and grid_width >= 16:
            counts["numbered_card"] = 4  # 2x2
        elif grid_height >= 8:
            counts["numbered_card"] = 4  # 2x2 compact
        else:
            counts["numbered_card"] = 2  # row

        # Comparison columns: 2-4 based on width
        cols = max(2, min(4, grid_width // 8))
        counts["comparison_column"] = cols

        # Colored sections: 3-5 based on height
        sections = max(2, min(5, grid_height // 3))
        counts["colored_section"] = sections

        # Sidebar box: usually 1
        counts["sidebar_box"] = 1

        return counts

    def _determine_layout_options(
        self,
        grid_width: int,
        grid_height: int
    ) -> List[str]:
        """Determine valid layout options for this space."""
        options = []

        # Row layouts
        if grid_height >= 5:
            if grid_width >= 16:
                options.append("row_4")
            if grid_width >= 12:
                options.append("row_3")
            if grid_width >= 8:
                options.append("row_2")

        # Grid layouts
        if grid_height >= 10:
            if grid_width >= 16:
                options.append("grid_2x2")
            if grid_width >= 24:
                options.append("grid_3x2")

        # Stacked layouts
        if grid_width >= 12:
            if grid_height >= 9:
                options.append("stacked_3")
            if grid_height >= 12:
                options.append("stacked_4")

        # Single layout always valid
        options.append("single")

        return options

    def calculate_instance_dimensions(
        self,
        total_width_px: int,
        total_height_px: int,
        instance_count: int,
        arrangement: ArrangementType,
        gap_px: int = DEFAULT_GAP_PX
    ) -> Tuple[int, int]:
        """
        Calculate dimensions for each component instance.

        Args:
            total_width_px: Total available width
            total_height_px: Total available height
            instance_count: Number of instances
            arrangement: Arrangement type
            gap_px: Gap between instances

        Returns:
            Tuple of (instance_width, instance_height)
        """
        if arrangement in [ArrangementType.ROW_2, ArrangementType.ROW_3, ArrangementType.ROW_4]:
            # Row layout: divide width by count
            cols = instance_count
            total_gap = gap_px * (cols - 1)
            instance_width = (total_width_px - total_gap) // cols
            instance_height = total_height_px
            return (instance_width, instance_height)

        elif arrangement == ArrangementType.GRID_2X2:
            # 2x2 grid
            cols, rows = 2, 2
            h_gap = gap_px * (cols - 1)
            v_gap = gap_px * (rows - 1)
            instance_width = (total_width_px - h_gap) // cols
            instance_height = (total_height_px - v_gap) // rows
            return (instance_width, instance_height)

        elif arrangement == ArrangementType.GRID_3X2:
            # 3x2 grid
            cols, rows = 3, 2
            h_gap = gap_px * (cols - 1)
            v_gap = gap_px * (rows - 1)
            instance_width = (total_width_px - h_gap) // cols
            instance_height = (total_height_px - v_gap) // rows
            return (instance_width, instance_height)

        elif arrangement in [ArrangementType.STACKED_2, ArrangementType.STACKED_3]:
            # Stacked layout: divide height by count
            rows = instance_count
            total_gap = gap_px * (rows - 1)
            instance_width = total_width_px
            instance_height = (total_height_px - total_gap) // rows
            return (instance_width, instance_height)

        else:  # SINGLE
            return (total_width_px, total_height_px)


# =============================================================================
# Character Limit Scaler
# =============================================================================

class CharacterLimitScaler:
    """
    Scales character limits based on available space.

    When space is tight, reduces max characters.
    When space is abundant, allows more characters.
    """

    def __init__(self):
        pass

    def scale_limits(
        self,
        slots: Dict[str, SlotSpec],
        scaling_factor: float,
        preserve_slots: Optional[List[str]] = None
    ) -> Dict[str, CharLimits]:
        """
        Scale character limits by a factor.

        Args:
            slots: Original slot specifications
            scaling_factor: Factor to scale by (0.7 = 70%, 1.2 = 120%)
            preserve_slots: Slots that should NOT be scaled

        Returns:
            Dictionary of scaled CharLimits per slot
        """
        preserve_slots = preserve_slots or []
        scaled = {}

        for slot_id, spec in slots.items():
            if slot_id in preserve_slots:
                # Don't scale preserved slots
                scaled[slot_id] = CharLimits(
                    min_chars=spec.min_chars,
                    max_chars=spec.max_chars,
                    baseline_chars=spec.baseline_chars or spec.max_chars
                )
            else:
                # Scale the limits
                baseline = spec.baseline_chars or ((spec.min_chars + spec.max_chars) // 2)
                scaled_baseline = int(baseline * scaling_factor)

                # Ensure min <= baseline <= max
                scaled_min = max(
                    spec.min_chars,
                    int(spec.min_chars * max(0.8, scaling_factor))
                )
                scaled_max = int(spec.max_chars * scaling_factor)

                # Clamp baseline
                scaled_baseline = max(scaled_min, min(scaled_max, scaled_baseline))

                scaled[slot_id] = CharLimits(
                    min_chars=scaled_min,
                    max_chars=scaled_max,
                    baseline_chars=scaled_baseline
                )

        return scaled

    def calculate_scaling_factor(
        self,
        available_width_px: int,
        available_height_px: int,
        ideal_width_px: int,
        ideal_height_px: int
    ) -> float:
        """
        Calculate scaling factor based on available vs ideal space.

        Args:
            available_width_px: Available width in pixels
            available_height_px: Available height in pixels
            ideal_width_px: Ideal width for component
            ideal_height_px: Ideal height for component

        Returns:
            Scaling factor (1.0 = ideal, <1.0 = compressed, >1.0 = expanded)
        """
        # Calculate area ratio
        available_area = available_width_px * available_height_px
        ideal_area = ideal_width_px * ideal_height_px

        if ideal_area == 0:
            return 1.0

        area_ratio = available_area / ideal_area

        # Convert to scaling factor (square root for more natural scaling)
        scaling_factor = area_ratio ** 0.5

        # Clamp to reasonable range
        return max(0.7, min(1.3, scaling_factor))


# =============================================================================
# Arrangement Selector
# =============================================================================

class ArrangementSelector:
    """
    Selects optimal arrangement for component instances.
    """

    def __init__(self, space_calculator: Optional[SpaceCalculator] = None):
        self.space_calculator = space_calculator or SpaceCalculator()

    def select_arrangement(
        self,
        component: ComponentDefinition,
        instance_count: int,
        grid_width: int,
        grid_height: int
    ) -> ArrangementType:
        """
        Select optimal arrangement for given component and space.

        Args:
            component: Component definition
            instance_count: Number of instances
            grid_width: Available width in grid units
            grid_height: Available height in grid units

        Returns:
            Selected ArrangementType
        """
        valid = component.arrangement_rules.valid_arrangements

        # Filter to arrangements that support the instance count
        candidates = self._filter_by_count(valid, instance_count)

        if not candidates:
            # Fallback to first valid arrangement
            return valid[0] if valid else ArrangementType.SINGLE

        # Score each candidate
        scores = []
        for arr in candidates:
            score = self._score_arrangement(
                arr, component, instance_count, grid_width, grid_height
            )
            scores.append((arr, score))

        # Return highest scored arrangement
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]

    def _filter_by_count(
        self,
        arrangements: List[ArrangementType],
        count: int
    ) -> List[ArrangementType]:
        """Filter arrangements that work with instance count."""
        valid = []
        for arr in arrangements:
            if arr == ArrangementType.ROW_2 and count == 2:
                valid.append(arr)
            elif arr == ArrangementType.ROW_3 and count == 3:
                valid.append(arr)
            elif arr == ArrangementType.ROW_4 and count == 4:
                valid.append(arr)
            elif arr == ArrangementType.GRID_2X2 and count == 4:
                valid.append(arr)
            elif arr == ArrangementType.GRID_3X2 and count == 6:
                valid.append(arr)
            elif arr == ArrangementType.STACKED_2 and count == 2:
                valid.append(arr)
            elif arr == ArrangementType.STACKED_3 and count == 3:
                valid.append(arr)
            elif arr == ArrangementType.SINGLE and count == 1:
                valid.append(arr)
        return valid

    def _score_arrangement(
        self,
        arrangement: ArrangementType,
        component: ComponentDefinition,
        instance_count: int,
        grid_width: int,
        grid_height: int
    ) -> float:
        """Score an arrangement (higher = better)."""
        score = 0.0

        # Preference bonus
        if component.arrangement_rules.prefer_row:
            if arrangement in [ArrangementType.ROW_2, ArrangementType.ROW_3, ArrangementType.ROW_4]:
                score += 10
        else:
            if arrangement in [ArrangementType.GRID_2X2, ArrangementType.GRID_3X2]:
                score += 10

        # Space efficiency
        space_analysis = self.space_calculator.analyze_space(grid_width, grid_height)
        if arrangement.value in space_analysis.layout_options:
            score += 5

        return score


# =============================================================================
# Variant Assigner
# =============================================================================

class VariantAssigner:
    """
    Assigns visual variants to component instances.
    """

    # Default variant cycling orders for different component types
    VARIANT_ORDERS = {
        "metrics_card": ["purple", "pink", "cyan", "green"],
        "numbered_card": ["blue", "green", "yellow", "pink"],
        "comparison_column": ["blue", "red", "green", "purple", "orange"],
        "colored_section": ["blue", "red", "green", "amber", "purple"],
        "sidebar_box": ["blue", "green", "purple", "amber"],
    }

    def assign_variants(
        self,
        component_id: str,
        instance_count: int,
        available_variants: List[str]
    ) -> List[str]:
        """
        Assign variants to each instance.

        Args:
            component_id: Component identifier
            instance_count: Number of instances
            available_variants: List of available variant IDs

        Returns:
            List of variant IDs (one per instance)
        """
        # Get preferred order for this component
        order = self.VARIANT_ORDERS.get(component_id, available_variants)

        # Filter to available variants
        ordered = [v for v in order if v in available_variants]

        # Add any remaining variants not in the order
        for v in available_variants:
            if v not in ordered:
                ordered.append(v)

        # Assign by cycling through variants
        assignments = []
        for i in range(instance_count):
            variant = ordered[i % len(ordered)]
            assignments.append(variant)

        return assignments


# =============================================================================
# Layout Builder (Combines all constraint logic)
# =============================================================================

class LayoutBuilder:
    """
    Builds complete layout configuration for a component.

    Combines space calculation, arrangement selection,
    character scaling, and variant assignment.
    """

    def __init__(self):
        self.space_calculator = SpaceCalculator()
        self.scaler = CharacterLimitScaler()
        self.arrangement_selector = ArrangementSelector(self.space_calculator)
        self.variant_assigner = VariantAssigner()

    def build_layout(
        self,
        component: ComponentDefinition,
        instance_count: int,
        grid_width: int,
        grid_height: int
    ) -> LayoutSelection:
        """
        Build complete layout configuration.

        Args:
            component: Component definition
            instance_count: Number of instances
            grid_width: Available width in grid units
            grid_height: Available height in grid units

        Returns:
            Complete LayoutSelection
        """
        # Analyze space
        space = self.space_calculator.analyze_space(grid_width, grid_height)

        # Select arrangement
        arrangement = self.arrangement_selector.select_arrangement(
            component, instance_count, grid_width, grid_height
        )

        # Calculate instance dimensions
        instance_width, instance_height = self.space_calculator.calculate_instance_dimensions(
            space.usable_width_px,
            space.usable_height_px,
            instance_count,
            arrangement,
            component.arrangement_rules.gap_px
        )

        # Calculate scaling factor
        ideal_width = (component.space_requirements.ideal_grid_width or
                       component.space_requirements.min_grid_width) * CELL_SIZE_PX
        ideal_height = (component.space_requirements.ideal_grid_height or
                        component.space_requirements.min_grid_height) * CELL_SIZE_PX

        scaling_factor = self.scaler.calculate_scaling_factor(
            instance_width, instance_height,
            ideal_width, ideal_height
        )

        # Scale character limits
        scaled_limits = self.scaler.scale_limits(
            component.slots,
            scaling_factor,
            component.scaling_rules.preserve_slots
        )

        # Assign variants
        available_variants = list(component.variants.keys())
        variant_assignments = self.variant_assigner.assign_variants(
            component.component_id,
            instance_count,
            available_variants
        )

        # Check if layout fits
        fits = (
            instance_width >= component.space_requirements.min_grid_width * CELL_SIZE_PX * 0.8 and
            instance_height >= component.space_requirements.min_grid_height * CELL_SIZE_PX * 0.8
        )

        return LayoutSelection(
            component_id=component.component_id,
            arrangement=arrangement,
            instance_count=instance_count,
            scaled_char_limits=scaled_limits,
            variant_assignments=variant_assignments,
            position_css={
                "width": f"{instance_width}px",
                "height": f"{instance_height}px",
                "gap": f"{component.arrangement_rules.gap_px}px"
            },
            fits_space=fits
        )
