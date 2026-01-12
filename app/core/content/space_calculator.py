"""
Space Calculator - Phase 2 of Multi-Step Content Generation

Deterministic calculation of character budgets based on:
- StructurePlan from Phase 1
- ThemeConfig (font sizes affect character counts)
- Available space dimensions

Per MULTI_STEP_CONTENT_STRUCTURE.md Section 4:
- 10% margins on all sides (90% usable)
- Character budget = width / (font_size * char_width_ratio)
- Line budget = height / (font_size * line_height)

Version: 1.3.0
"""

import logging
from typing import Optional, List

from app.models.space_models import (
    StructurePlan, SpaceBudget, SectionBudget, LayoutStructure
)
from app.models.requests import ThemeConfig, TypographySpec

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default character width ratio (avg char width / font size)
# Typical for proportional fonts like Poppins
DEFAULT_CHAR_WIDTH_RATIO = 0.5

# Margin factor (10% margins = 90% usable)
MARGIN_FACTOR = 0.90

# Minimum gap between columns (pixels)
COLUMN_GAP_PX = 40

# Heading height allocation (percentage of total height)
HEADING_HEIGHT_RATIO = 0.15

# Default typography specs (fallback)
DEFAULT_TYPOGRAPHY = {
    "t1": {"size": 32, "weight": 700, "line_height": 1.2},
    "t2": {"size": 24, "weight": 600, "line_height": 1.3},
    "t3": {"size": 20, "weight": 500, "line_height": 1.4},
    "t4": {"size": 16, "weight": 400, "line_height": 1.5},
}


# =============================================================================
# Space Calculator Class
# =============================================================================

class SpaceCalculator:
    """
    Phase 2: Calculates character budgets based on space and theme.

    This is a deterministic calculation (no LLM) that computes:
    - Heading character limit
    - Section character limits
    - Lines per section
    - Characters per line

    Theme affects calculations through font sizes:
    - Larger fonts → fewer characters per line
    - Larger line heights → fewer lines per section
    """

    def __init__(self, char_width_ratio: float = DEFAULT_CHAR_WIDTH_RATIO):
        """
        Initialize the space calculator.

        Args:
            char_width_ratio: Ratio of avg character width to font size
        """
        self.char_width_ratio = char_width_ratio

    def calculate(
        self,
        structure: StructurePlan,
        available_width_px: int,
        available_height_px: int,
        theme_config: Optional[ThemeConfig] = None
    ) -> SpaceBudget:
        """
        Calculate character budgets for the structure.

        Args:
            structure: StructurePlan from Phase 1
            available_width_px: Total available width in pixels
            available_height_px: Total available height in pixels
            theme_config: Theme configuration for font specs

        Returns:
            SpaceBudget with character limits for each element
        """
        # Calculate usable area (after margins)
        usable_width = int(available_width_px * MARGIN_FACTOR)
        usable_height = int(available_height_px * MARGIN_FACTOR)

        # Get typography specs
        heading_spec = self._get_typography_spec(theme_config, "t1")
        body_spec = self._get_typography_spec(theme_config, "t3")

        # Calculate heading budget
        heading_height_px = int(usable_height * HEADING_HEIGHT_RATIO) if structure.has_heading else 0
        heading_max_chars = self._calculate_chars_per_line(usable_width, heading_spec["size"])

        # Calculate body area
        body_height_px = usable_height - heading_height_px
        body_width_px = usable_width

        # Calculate column dimensions
        columns = structure.columns
        total_gap = COLUMN_GAP_PX * (columns - 1) if columns > 1 else 0
        column_width_px = (body_width_px - total_gap) // columns if columns > 0 else body_width_px

        # Calculate lines and chars for body
        body_line_height_px = body_spec["size"] * body_spec["line_height"]
        total_lines = int(body_height_px / body_line_height_px)
        chars_per_line = self._calculate_chars_per_line(column_width_px, body_spec["size"])

        # Calculate section budgets
        section_budgets = self._calculate_section_budgets(
            structure=structure,
            column_width_px=column_width_px,
            body_height_px=body_height_px,
            body_spec=body_spec,
            chars_per_line=chars_per_line,
            total_lines=total_lines
        )

        # Calculate total body chars
        total_body_chars = sum(sb.max_chars for sb in section_budgets)

        return SpaceBudget(
            total_width_px=available_width_px,
            total_height_px=available_height_px,
            usable_width_px=usable_width,
            usable_height_px=usable_height,
            heading_max_chars=heading_max_chars,
            heading_typography="t1",
            section_budgets=section_budgets,
            columns=columns,
            column_width_px=column_width_px,
            total_lines=total_lines,
            total_body_chars=total_body_chars,
            char_width_ratio=self.char_width_ratio
        )

    def _get_typography_spec(
        self,
        theme_config: Optional[ThemeConfig],
        level: str
    ) -> dict:
        """Get typography spec for a level."""
        if theme_config and theme_config.typography:
            spec = theme_config.get_typography_spec(level)
            return {
                "size": spec.size,
                "weight": spec.weight,
                "line_height": spec.line_height
            }

        # Fallback to defaults
        return DEFAULT_TYPOGRAPHY.get(level, DEFAULT_TYPOGRAPHY["t3"])

    def _calculate_chars_per_line(self, width_px: int, font_size: int) -> int:
        """Calculate characters per line based on width and font size."""
        char_width = font_size * self.char_width_ratio
        return int(width_px / char_width) if char_width > 0 else 50

    def _calculate_section_budgets(
        self,
        structure: StructurePlan,
        column_width_px: int,
        body_height_px: int,
        body_spec: dict,
        chars_per_line: int,
        total_lines: int
    ) -> List[SectionBudget]:
        """Calculate budget for each section."""
        sections = structure.sections
        if not sections:
            # Single section for entire body
            return [SectionBudget(
                section_index=0,
                max_chars=chars_per_line * total_lines,
                max_lines=total_lines,
                chars_per_line=chars_per_line,
                typography_level="t3"
            )]

        section_count = len(sections)

        # Distribute lines among sections based on layout
        if structure.layout_type in (LayoutStructure.TWO_COLUMN, LayoutStructure.THREE_COLUMN):
            # Columns: sections distributed across columns
            sections_per_column = (section_count + structure.columns - 1) // structure.columns
            lines_per_section = total_lines // sections_per_column if sections_per_column > 0 else total_lines
        else:
            # Single column: stack sections vertically
            lines_per_section = total_lines // section_count if section_count > 0 else total_lines

        # Build section budgets
        budgets = []
        for i, section in enumerate(sections):
            # Emphasized sections get more lines
            section_lines = lines_per_section
            if section.emphasis or i in structure.emphasis_points:
                section_lines = int(section_lines * 1.25)

            # Typography level based on content type
            typo_level = "t3"  # Default body text
            if section.content_type == "heading":
                typo_level = "t2"

            budgets.append(SectionBudget(
                section_index=i,
                max_chars=chars_per_line * section_lines,
                max_lines=section_lines,
                chars_per_line=chars_per_line,
                typography_level=typo_level
            ))

        return budgets

    def estimate_utilization(
        self,
        budget: SpaceBudget,
        actual_heading_chars: int,
        actual_section_chars: List[int]
    ) -> float:
        """
        Calculate space utilization percentage.

        Args:
            budget: Calculated space budget
            actual_heading_chars: Actual heading character count
            actual_section_chars: List of actual section character counts

        Returns:
            Utilization percentage (0-100)
        """
        total_budget = budget.heading_max_chars + budget.total_body_chars
        total_actual = actual_heading_chars + sum(actual_section_chars)

        if total_budget == 0:
            return 0.0

        return (total_actual / total_budget) * 100

    def get_space_summary(self, budget: SpaceBudget) -> dict:
        """Get human-readable summary of space budget."""
        return {
            "total_area": f"{budget.total_width_px}x{budget.total_height_px}px",
            "usable_area": f"{budget.usable_width_px}x{budget.usable_height_px}px",
            "columns": budget.columns,
            "column_width": f"{budget.column_width_px}px",
            "heading_chars": budget.heading_max_chars,
            "total_body_chars": budget.total_body_chars,
            "total_lines": budget.total_lines,
            "sections": len(budget.section_budgets),
            "expected_utilization": f"{budget.utilization_percentage():.1f}%"
        }


# =============================================================================
# Utility Functions
# =============================================================================

def calculate_quick_budget(
    width_px: int,
    height_px: int,
    columns: int = 1,
    font_size: int = 20,
    line_height: float = 1.4
) -> dict:
    """
    Quick calculation without full StructurePlan.

    Useful for estimates or when structure is unknown.

    Args:
        width_px: Available width in pixels
        height_px: Available height in pixels
        columns: Number of columns
        font_size: Body font size
        line_height: Line height multiplier

    Returns:
        Dictionary with character budgets
    """
    usable_width = int(width_px * MARGIN_FACTOR)
    usable_height = int(height_px * MARGIN_FACTOR)

    # Column width
    total_gap = COLUMN_GAP_PX * (columns - 1) if columns > 1 else 0
    column_width = (usable_width - total_gap) // columns if columns > 0 else usable_width

    # Character and line calculations
    char_width = font_size * DEFAULT_CHAR_WIDTH_RATIO
    chars_per_line = int(column_width / char_width)
    line_px = font_size * line_height
    total_lines = int(usable_height / line_px)

    return {
        "usable_width_px": usable_width,
        "usable_height_px": usable_height,
        "column_width_px": column_width,
        "chars_per_line": chars_per_line,
        "total_lines": total_lines,
        "total_chars": chars_per_line * total_lines * columns,
        "chars_per_column": chars_per_line * total_lines
    }
