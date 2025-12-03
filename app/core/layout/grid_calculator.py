"""
Grid Calculator for Layout Service Integration

Calculates character limits, word counts, and table dimensions from
12x8 grid-based constraints. The grid system maps to a standard
presentation slide (960x720 pixels at 72dpi).

Grid System:
- Width: 12 columns (each ~80px at 960px slide width)
- Height: 8 rows (each ~90px at 720px slide height)

Character Calculation:
- Based on average character width and line height
- Accounts for padding within elements
- Uses 85% fill factor to avoid overflow
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class GridCalculator:
    """
    Calculate content constraints from grid dimensions.

    This calculator converts abstract grid units (1-12 columns, 1-8 rows)
    into concrete constraints like maximum characters, word counts, and
    optimal table dimensions.
    """

    # Slide dimensions (standard 16:9 aspect ratio at common resolution)
    SLIDE_WIDTH = 960   # pixels
    SLIDE_HEIGHT = 540  # pixels (16:9 ratio)

    # Grid system
    GRID_COLUMNS = 12
    GRID_ROWS = 8

    # Typography assumptions (based on Inter font at 16-18px)
    CHAR_WIDTH_PX = 8.5     # Average character width
    LINE_HEIGHT_PX = 28     # Line height in pixels
    WORDS_PER_100_CHARS = 17  # Approximate word count ratio
    READING_SPEED_WPM = 200   # Average reading speed

    # Layout assumptions
    PADDING_PX = 16          # Padding inside elements
    FILL_FACTOR = 0.85       # Don't fill 100% to avoid overflow

    # Character guidelines from spec (per grid width)
    CHARS_PER_LINE_BY_WIDTH = {
        1: 10,
        2: 20,
        3: 35,
        4: 50,
        5: 65,
        6: 80,
        7: 95,
        8: 110,
        9: 125,
        10: 140,
        11: 155,
        12: 170
    }

    # Lines per grid height (at standard font size)
    LINES_PER_HEIGHT = {
        1: 2,
        2: 4,
        3: 6,
        4: 9,
        5: 11,
        6: 14,
        7: 16,
        8: 19
    }

    # Table constraints by grid dimensions
    MAX_COLUMNS_BY_WIDTH = {
        1: 1, 2: 2, 3: 2, 4: 3, 5: 4,
        6: 5, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10
    }

    MAX_ROWS_BY_HEIGHT = {
        1: 2, 2: 3, 3: 5, 4: 7,
        5: 9, 6: 12, 7: 14, 8: 16
    }

    @classmethod
    def calculate_max_characters(
        cls,
        grid_width: int,
        grid_height: int,
        custom_fill_factor: float = None
    ) -> int:
        """
        Calculate maximum characters for given grid dimensions.

        Uses the spec's character guidelines combined with line calculations.
        Applies an 85% fill factor by default to prevent overflow.

        Args:
            grid_width: Grid width (1-12)
            grid_height: Grid height (1-8)
            custom_fill_factor: Override default fill factor (0.0-1.0)

        Returns:
            Maximum character count
        """
        # Clamp values to valid range
        grid_width = max(1, min(12, grid_width))
        grid_height = max(1, min(8, grid_height))

        # Get chars per line from spec
        chars_per_line = cls.CHARS_PER_LINE_BY_WIDTH.get(grid_width, 170)

        # Get number of lines from spec
        num_lines = cls.LINES_PER_HEIGHT.get(grid_height, 19)

        # Apply fill factor
        fill_factor = custom_fill_factor if custom_fill_factor else cls.FILL_FACTOR

        max_chars = int(chars_per_line * num_lines * fill_factor)

        # Ensure minimum useful value
        return max(max_chars, 50)

    @classmethod
    def calculate_min_characters(
        cls,
        grid_width: int,
        grid_height: int
    ) -> int:
        """
        Calculate minimum recommended characters for grid dimensions.

        Uses approximately 20% of max capacity as minimum to ensure
        the element doesn't look empty.

        Args:
            grid_width: Grid width (1-12)
            grid_height: Grid height (1-8)

        Returns:
            Minimum character count
        """
        max_chars = cls.calculate_max_characters(grid_width, grid_height)
        return max(int(max_chars * 0.2), 20)

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
    def calculate_table_dimensions(
        cls,
        grid_width: int,
        grid_height: int
    ) -> Dict[str, Any]:
        """
        Calculate recommended table dimensions for grid constraints.

        Args:
            grid_width: Grid width (1-12)
            grid_height: Grid height (1-8)

        Returns:
            Dictionary with:
            - max_columns: Maximum recommended columns
            - max_rows: Maximum recommended data rows
            - cell_char_limit: Maximum characters per cell
            - header_char_limit: Maximum characters per header cell
        """
        # Clamp values
        grid_width = max(1, min(12, grid_width))
        grid_height = max(1, min(8, grid_height))

        # Get constraints from lookup tables
        max_columns = cls.MAX_COLUMNS_BY_WIDTH.get(grid_width, 10)
        max_rows = cls.MAX_ROWS_BY_HEIGHT.get(grid_height, 16)

        # Calculate cell character limits
        # Each column gets roughly equal width
        column_width_px = (cls.SLIDE_WIDTH / cls.GRID_COLUMNS * grid_width - 2 * cls.PADDING_PX) / max_columns
        cell_char_limit = max(int((column_width_px - 10) / cls.CHAR_WIDTH_PX), 10)

        # Headers can be slightly shorter (bold text is wider)
        header_char_limit = int(cell_char_limit * 0.85)

        return {
            "max_columns": max_columns,
            "max_rows": max_rows,
            "cell_char_limit": cell_char_limit,
            "header_char_limit": header_char_limit,
            "total_cells": max_columns * (max_rows + 1)  # +1 for header
        }

    @classmethod
    def get_content_guidelines(
        cls,
        grid_width: int,
        grid_height: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive content guidelines for grid dimensions.

        Combines character limits, word counts, read times, and
        recommendations into a single response.

        Args:
            grid_width: Grid width (1-12)
            grid_height: Grid height (1-8)

        Returns:
            Dictionary with all content guidelines
        """
        max_chars = cls.calculate_max_characters(grid_width, grid_height)
        min_chars = cls.calculate_min_characters(grid_width, grid_height)
        target_chars = int((max_chars + min_chars) / 2)

        max_words = cls.calculate_word_count(max_chars)
        target_words = cls.calculate_word_count(target_chars)

        lines = cls.LINES_PER_HEIGHT.get(grid_height, 19)
        chars_per_line = cls.CHARS_PER_LINE_BY_WIDTH.get(grid_width, 170)

        return {
            "characters": {
                "min": min_chars,
                "max": max_chars,
                "target": target_chars
            },
            "words": {
                "min": cls.calculate_word_count(min_chars),
                "max": max_words,
                "target": target_words
            },
            "layout": {
                "lines": lines,
                "chars_per_line": chars_per_line
            },
            "read_time_seconds": cls.calculate_read_time(target_words),
            "recommendations": cls._get_format_recommendations(grid_width, grid_height)
        }

    @classmethod
    def _get_format_recommendations(
        cls,
        grid_width: int,
        grid_height: int
    ) -> Dict[str, Any]:
        """
        Get format recommendations based on grid size.

        Args:
            grid_width: Grid width (1-12)
            grid_height: Grid height (1-8)

        Returns:
            Dictionary with format recommendations
        """
        area = grid_width * grid_height

        # Small elements (1-6 grid units)
        if area <= 6:
            return {
                "preferred_format": "headline",
                "bullet_count": 0,
                "paragraph_count": 0,
                "suggestion": "Use brief headline or single statement"
            }

        # Medium elements (7-16 grid units)
        elif area <= 16:
            return {
                "preferred_format": "bullets",
                "bullet_count": min(area // 3, 5),
                "paragraph_count": 1,
                "suggestion": "Use 2-4 bullet points or short paragraph"
            }

        # Large elements (17-32 grid units)
        elif area <= 32:
            return {
                "preferred_format": "mixed",
                "bullet_count": min(area // 4, 6),
                "paragraph_count": 2,
                "suggestion": "Use paragraph with supporting bullets"
            }

        # Very large elements (33+ grid units)
        else:
            return {
                "preferred_format": "paragraph",
                "bullet_count": min(area // 5, 8),
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
            grid_width: Grid width to validate
            grid_height: Grid height to validate

        Returns:
            Dictionary with validation result and any errors
        """
        errors = []
        warnings = []

        # Check width bounds
        if grid_width < 1:
            errors.append("Grid width must be at least 1")
        elif grid_width > 12:
            errors.append("Grid width cannot exceed 12")

        # Check height bounds
        if grid_height < 1:
            errors.append("Grid height must be at least 1")
        elif grid_height > 8:
            errors.append("Grid height cannot exceed 8")

        # Check minimum viable size
        if grid_width < 2 or grid_height < 2:
            warnings.append("Very small grid size may not display content well")

        # Check for text content
        area = grid_width * grid_height
        if area < 4:
            warnings.append("Grid area is very small - consider using headline format only")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "grid_width": max(1, min(12, grid_width)),
            "grid_height": max(1, min(8, grid_height)),
            "grid_area": area
        }
