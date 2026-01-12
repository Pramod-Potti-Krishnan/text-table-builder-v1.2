"""
Grid Calculator for Elementor Text Service v2.0

Calculates character limits, word counts, and layout constraints from
32x18 grid-based dimensions. The grid system maps to a standard
HD presentation slide (1920x1080 pixels).

Grid System:
- Width: 32 columns (each 60px at 1920px slide width)
- Height: 18 rows (each 60px at 1080px slide height)

Character Calculation:
- Based on font size, line height, and character width ratio
- Accounts for outer padding (grid edge to element border)
- Accounts for inner padding (element border to text)
- Uses 90% fill factor to avoid overflow
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TypographySpec:
    """Typography specification for constraint calculations."""
    font_size: int = 20           # pixels
    line_height: float = 1.6      # multiplier
    char_width_ratio: float = 0.5 # avg char width / font size
    font_family: str = "Poppins, sans-serif"


@dataclass
class ElementDimensions:
    """Calculated element dimensions in pixels."""
    element_width: float
    element_height: float
    content_width: float
    content_height: float
    grid_width: int
    grid_height: int
    outer_padding: int
    inner_padding: int


@dataclass
class TextConstraints:
    """Calculated text constraints for content generation."""
    chars_per_line: int
    max_lines: int
    max_characters: int
    target_characters: int
    min_characters: int
    font_size: int
    line_height_px: float


class GridCalculator:
    """
    Calculate content constraints from 32x18 grid dimensions.

    This calculator converts abstract grid units (1-32 columns, 1-18 rows)
    into concrete constraints like maximum characters, word counts, and
    optimal element dimensions based on typography specifications.
    """

    # Slide dimensions (1920x1080 HD)
    SLIDE_WIDTH = 1920   # pixels
    SLIDE_HEIGHT = 1080  # pixels

    # Grid system (32x18)
    GRID_COLUMNS = 32
    GRID_ROWS = 18

    # Each grid cell = 60x60 pixels
    CELL_WIDTH = SLIDE_WIDTH / GRID_COLUMNS   # 60px
    CELL_HEIGHT = SLIDE_HEIGHT / GRID_ROWS    # 60px

    # Default padding
    DEFAULT_OUTER_PADDING = 10  # pixels (grid edge to element border)
    DEFAULT_INNER_PADDING = 16  # pixels (element border to text)

    # Fill factor for safety margin
    FILL_FACTOR = 0.90  # Use 90% of calculated space

    # Word/reading calculations
    WORDS_PER_100_CHARS = 17  # Approximate word count ratio
    READING_SPEED_WPM = 200   # Average reading speed

    # Default typography tokens (can be overridden by theme)
    DEFAULT_TYPOGRAPHY = {
        "h1": TypographySpec(font_size=72, line_height=1.2, char_width_ratio=0.5),
        "h2": TypographySpec(font_size=48, line_height=1.3, char_width_ratio=0.5),
        "h3": TypographySpec(font_size=32, line_height=1.4, char_width_ratio=0.5),
        "h4": TypographySpec(font_size=24, line_height=1.4, char_width_ratio=0.5),
        "body": TypographySpec(font_size=20, line_height=1.6, char_width_ratio=0.5),
        "subtitle": TypographySpec(font_size=28, line_height=1.5, char_width_ratio=0.5),
        "caption": TypographySpec(font_size=16, line_height=1.4, char_width_ratio=0.5),
    }

    @classmethod
    def calculate_element_dimensions(
        cls,
        grid_width: int,
        grid_height: int,
        outer_padding: int = None,
        inner_padding: int = None
    ) -> ElementDimensions:
        """
        Calculate actual pixel dimensions for text content area.

        Args:
            grid_width: Grid columns (1-32)
            grid_height: Grid rows (1-18)
            outer_padding: Padding from grid edge to element border (default: 10px)
            inner_padding: Padding from element border to text (default: 16px)

        Returns:
            ElementDimensions with all calculated pixel values
        """
        # Use defaults if not specified
        outer_padding = outer_padding if outer_padding is not None else cls.DEFAULT_OUTER_PADDING
        inner_padding = inner_padding if inner_padding is not None else cls.DEFAULT_INNER_PADDING

        # Clamp grid values to valid range
        grid_width = max(1, min(cls.GRID_COLUMNS, grid_width))
        grid_height = max(1, min(cls.GRID_ROWS, grid_height))

        # Calculate element dimensions (after outer padding)
        element_width = (grid_width * cls.CELL_WIDTH) - (2 * outer_padding)
        element_height = (grid_height * cls.CELL_HEIGHT) - (2 * outer_padding)

        # Calculate content dimensions (after inner padding)
        content_width = element_width - (2 * inner_padding)
        content_height = element_height - (2 * inner_padding)

        return ElementDimensions(
            element_width=element_width,
            element_height=element_height,
            content_width=max(content_width, 0),
            content_height=max(content_height, 0),
            grid_width=grid_width,
            grid_height=grid_height,
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

    @classmethod
    def calculate_text_constraints(
        cls,
        content_width: float,
        content_height: float,
        font_size: int = 20,
        line_height: float = 1.6,
        char_width_ratio: float = 0.5,
        fill_factor: float = None
    ) -> TextConstraints:
        """
        Calculate character and line constraints for given dimensions and typography.

        Args:
            content_width: Available width for text in pixels
            content_height: Available height for text in pixels
            font_size: Font size in pixels
            line_height: Line height multiplier (e.g., 1.6)
            char_width_ratio: Average character width / font size (default 0.5)
            fill_factor: Percentage of space to use (default 0.9)

        Returns:
            TextConstraints with all calculated values
        """
        fill_factor = fill_factor if fill_factor is not None else cls.FILL_FACTOR

        # Calculate character width and line height in pixels
        avg_char_width = font_size * char_width_ratio
        line_height_px = font_size * line_height

        # Calculate how many characters fit per line and how many lines fit
        chars_per_line = int(content_width / avg_char_width) if avg_char_width > 0 else 0
        max_lines = int(content_height / line_height_px) if line_height_px > 0 else 0

        # Apply fill factor for safety margin
        max_characters = int(chars_per_line * max_lines * fill_factor)
        target_characters = int(max_characters * 0.8)
        min_characters = max(int(max_characters * 0.2), 10)

        return TextConstraints(
            chars_per_line=max(chars_per_line, 1),
            max_lines=max(max_lines, 1),
            max_characters=max(max_characters, 10),
            target_characters=max(target_characters, 10),
            min_characters=min_characters,
            font_size=font_size,
            line_height_px=line_height_px
        )

    @classmethod
    def calculate_constraints_for_text_type(
        cls,
        grid_width: int,
        grid_height: int,
        text_type: str = "body",
        outer_padding: int = None,
        inner_padding: int = None,
        typography_override: Optional[TypographySpec] = None
    ) -> Dict[str, Any]:
        """
        Calculate complete constraints for a specific text type.

        Args:
            grid_width: Grid columns (1-32)
            grid_height: Grid rows (1-18)
            text_type: Type of text (h1, h2, h3, h4, body, subtitle, caption)
            outer_padding: Override outer padding (default: 10px)
            inner_padding: Override inner padding (default: 16px)
            typography_override: Override typography spec

        Returns:
            Complete constraints dictionary
        """
        # Get typography spec
        if typography_override:
            typography = typography_override
        else:
            typography = cls.DEFAULT_TYPOGRAPHY.get(text_type, cls.DEFAULT_TYPOGRAPHY["body"])

        # Calculate dimensions
        dimensions = cls.calculate_element_dimensions(
            grid_width=grid_width,
            grid_height=grid_height,
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

        # Calculate text constraints
        constraints = cls.calculate_text_constraints(
            content_width=dimensions.content_width,
            content_height=dimensions.content_height,
            font_size=typography.font_size,
            line_height=typography.line_height,
            char_width_ratio=typography.char_width_ratio
        )

        return {
            "dimensions": {
                "grid_width": dimensions.grid_width,
                "grid_height": dimensions.grid_height,
                "element_width": dimensions.element_width,
                "element_height": dimensions.element_height,
                "content_width": dimensions.content_width,
                "content_height": dimensions.content_height,
                "outer_padding": dimensions.outer_padding,
                "inner_padding": dimensions.inner_padding
            },
            "text_constraints": {
                "chars_per_line": constraints.chars_per_line,
                "max_lines": constraints.max_lines,
                "max_characters": constraints.max_characters,
                "target_characters": constraints.target_characters,
                "min_characters": constraints.min_characters
            },
            "typography": {
                "text_type": text_type,
                "font_size": typography.font_size,
                "line_height": typography.line_height,
                "line_height_px": constraints.line_height_px,
                "char_width_ratio": typography.char_width_ratio,
                "font_family": typography.font_family
            }
        }

    @classmethod
    def calculate_word_count(cls, character_count: int) -> int:
        """
        Estimate word count from character count.

        Args:
            character_count: Number of characters

        Returns:
            Estimated word count
        """
        return int(character_count * cls.WORDS_PER_100_CHARS / 100)

    @classmethod
    def calculate_read_time(cls, word_count: int) -> float:
        """
        Estimate reading time in seconds.

        Args:
            word_count: Number of words

        Returns:
            Estimated reading time in seconds
        """
        return (word_count / cls.READING_SPEED_WPM) * 60

    @classmethod
    def get_content_guidelines(
        cls,
        grid_width: int,
        grid_height: int,
        text_type: str = "body",
        outer_padding: int = None,
        inner_padding: int = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive content guidelines for grid dimensions and text type.

        Args:
            grid_width: Grid columns (1-32)
            grid_height: Grid rows (1-18)
            text_type: Type of text (h1, h2, h3, h4, body, subtitle, caption)
            outer_padding: Override outer padding
            inner_padding: Override inner padding

        Returns:
            Dictionary with all content guidelines
        """
        # Get complete constraints
        result = cls.calculate_constraints_for_text_type(
            grid_width=grid_width,
            grid_height=grid_height,
            text_type=text_type,
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

        text_constraints = result["text_constraints"]
        max_chars = text_constraints["max_characters"]
        min_chars = text_constraints["min_characters"]
        target_chars = text_constraints["target_characters"]

        # Calculate word counts
        max_words = cls.calculate_word_count(max_chars)
        min_words = cls.calculate_word_count(min_chars)
        target_words = cls.calculate_word_count(target_chars)

        return {
            "grid": {
                "width": result["dimensions"]["grid_width"],
                "height": result["dimensions"]["grid_height"],
                "area": result["dimensions"]["grid_width"] * result["dimensions"]["grid_height"]
            },
            "dimensions": result["dimensions"],
            "text": {
                "characters": {
                    "min": min_chars,
                    "max": max_chars,
                    "target": target_chars
                },
                "words": {
                    "min": min_words,
                    "max": max_words,
                    "target": target_words
                },
                "layout": {
                    "lines": text_constraints["max_lines"],
                    "chars_per_line": text_constraints["chars_per_line"]
                },
                "read_time_seconds": round(cls.calculate_read_time(target_words), 1)
            },
            "typography": result["typography"],
            "recommendations": cls._get_format_recommendations(
                grid_width, grid_height, text_type
            )
        }

    @classmethod
    def calculate_table_dimensions(
        cls,
        grid_width: int,
        grid_height: int,
        outer_padding: int = None,
        inner_padding: int = None,
        header_font_size: int = 16,
        cell_font_size: int = 14
    ) -> Dict[str, Any]:
        """
        Calculate recommended table dimensions for grid constraints.

        Args:
            grid_width: Grid columns (1-32)
            grid_height: Grid rows (1-18)
            outer_padding: Override outer padding
            inner_padding: Override inner padding
            header_font_size: Font size for table headers
            cell_font_size: Font size for table cells

        Returns:
            Dictionary with table dimension recommendations
        """
        dimensions = cls.calculate_element_dimensions(
            grid_width=grid_width,
            grid_height=grid_height,
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

        # Estimate max columns (at least 80px per column)
        min_col_width = 80
        max_columns = max(1, int(dimensions.content_width / min_col_width))

        # Estimate max rows (header + data rows, ~32px per row)
        row_height = 32
        max_rows = max(1, int(dimensions.content_height / row_height) - 1)  # -1 for header

        # Calculate cell character limits
        avg_col_width = dimensions.content_width / max_columns if max_columns > 0 else 0
        cell_padding = 16  # horizontal padding in cells
        usable_cell_width = max(avg_col_width - cell_padding, 20)

        header_char_width = header_font_size * 0.5
        cell_char_width = cell_font_size * 0.5

        header_char_limit = int(usable_cell_width / header_char_width) if header_char_width > 0 else 10
        cell_char_limit = int(usable_cell_width / cell_char_width) if cell_char_width > 0 else 12

        return {
            "max_columns": min(max_columns, 12),  # Cap at 12 columns
            "max_rows": min(max_rows, 20),  # Cap at 20 data rows
            "header_char_limit": max(header_char_limit, 5),
            "cell_char_limit": max(cell_char_limit, 5),
            "total_cells": max_columns * (max_rows + 1),
            "dimensions": {
                "content_width": dimensions.content_width,
                "content_height": dimensions.content_height,
                "avg_column_width": avg_col_width,
                "row_height": row_height
            }
        }

    @classmethod
    def _get_format_recommendations(
        cls,
        grid_width: int,
        grid_height: int,
        text_type: str = "body"
    ) -> Dict[str, Any]:
        """
        Get format recommendations based on grid size and text type.

        Args:
            grid_width: Grid columns (1-32)
            grid_height: Grid rows (1-18)
            text_type: Type of text

        Returns:
            Dictionary with format recommendations
        """
        area = grid_width * grid_height

        # Heading types have different recommendations
        if text_type in ["h1", "h2"]:
            return {
                "preferred_format": "headline",
                "bullet_count": 0,
                "paragraph_count": 0,
                "suggestion": "Use concise headline or title text"
            }

        if text_type == "subtitle":
            return {
                "preferred_format": "subtitle",
                "bullet_count": 0,
                "paragraph_count": 1,
                "suggestion": "Use brief supporting subtitle text"
            }

        # Body text recommendations based on area
        # 32x18 grid = 576 max area, scale thresholds accordingly
        if area <= 24:  # ~4x6 or smaller
            return {
                "preferred_format": "headline",
                "bullet_count": 0,
                "paragraph_count": 0,
                "suggestion": "Use brief headline or single statement"
            }

        elif area <= 72:  # ~6x12 or 8x9
            return {
                "preferred_format": "bullets",
                "bullet_count": min(area // 12, 5),
                "paragraph_count": 1,
                "suggestion": "Use 2-4 bullet points or short paragraph"
            }

        elif area <= 144:  # ~12x12 or 8x18
            return {
                "preferred_format": "mixed",
                "bullet_count": min(area // 18, 6),
                "paragraph_count": 2,
                "suggestion": "Use paragraph with supporting bullets"
            }

        else:  # Larger areas
            return {
                "preferred_format": "paragraph",
                "bullet_count": min(area // 24, 8),
                "paragraph_count": 3,
                "suggestion": "Full paragraphs or detailed bullet lists"
            }

    @classmethod
    def validate_grid_constraints(
        cls,
        grid_width: int,
        grid_height: int
    ) -> Dict[str, Any]:
        """
        Validate grid constraints and return validation result.

        Args:
            grid_width: Grid width to validate (1-32)
            grid_height: Grid height to validate (1-18)

        Returns:
            Dictionary with validation result and any errors/warnings
        """
        errors = []
        warnings = []

        # Check width bounds
        if grid_width < 1:
            errors.append("Grid width must be at least 1")
        elif grid_width > cls.GRID_COLUMNS:
            errors.append(f"Grid width cannot exceed {cls.GRID_COLUMNS}")

        # Check height bounds
        if grid_height < 1:
            errors.append("Grid height must be at least 1")
        elif grid_height > cls.GRID_ROWS:
            errors.append(f"Grid height cannot exceed {cls.GRID_ROWS}")

        # Check minimum viable size for text
        if 0 < grid_width < 4 or 0 < grid_height < 2:
            warnings.append("Very small grid size may not display text content well")

        # Calculate area
        area = max(0, grid_width) * max(0, grid_height)
        if 0 < area < 8:
            warnings.append("Grid area is very small - consider using headline format only")

        # Clamp to valid values
        valid_width = max(1, min(cls.GRID_COLUMNS, grid_width))
        valid_height = max(1, min(cls.GRID_ROWS, grid_height))

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "grid_width": valid_width,
            "grid_height": valid_height,
            "grid_area": valid_width * valid_height,
            "pixel_dimensions": {
                "width": valid_width * cls.CELL_WIDTH,
                "height": valid_height * cls.CELL_HEIGHT
            }
        }

    @classmethod
    def get_grid_info(cls) -> Dict[str, Any]:
        """
        Get information about the grid system.

        Returns:
            Dictionary with grid system specifications
        """
        return {
            "slide_dimensions": {
                "width": cls.SLIDE_WIDTH,
                "height": cls.SLIDE_HEIGHT,
                "aspect_ratio": "16:9"
            },
            "grid_system": {
                "columns": cls.GRID_COLUMNS,
                "rows": cls.GRID_ROWS,
                "cell_width": cls.CELL_WIDTH,
                "cell_height": cls.CELL_HEIGHT
            },
            "default_padding": {
                "outer": cls.DEFAULT_OUTER_PADDING,
                "inner": cls.DEFAULT_INNER_PADDING
            },
            "fill_factor": cls.FILL_FACTOR,
            "typography_defaults": {
                text_type: {
                    "font_size": spec.font_size,
                    "line_height": spec.line_height,
                    "char_width_ratio": spec.char_width_ratio
                }
                for text_type, spec in cls.DEFAULT_TYPOGRAPHY.items()
            }
        }
