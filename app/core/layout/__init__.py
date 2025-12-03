"""
Layout Service Integration Module for Text & Table Builder v1.2

Provides grid-based text and table generation with constraint-aware
HTML+CSS output for the Layout Service integration.

Endpoints supported:
- /api/ai/text/generate - Generate new text content
- /api/ai/text/transform - Transform existing text
- /api/ai/text/autofit - Fit text to element dimensions
- /api/ai/table/generate - Generate structured table
- /api/ai/table/transform - Modify table structure
- /api/ai/table/analyze - Get insights from table data
"""

from .grid_calculator import GridCalculator
from .base_layout_generator import BaseLayoutGenerator
from .text_generator import (
    TextGenerateGenerator,
    TextTransformGenerator,
    TextAutofitGenerator
)
from .table_generator import (
    TableGenerateGenerator,
    TableTransformGenerator,
    TableAnalyzeGenerator
)

__all__ = [
    # Calculator
    "GridCalculator",

    # Base class
    "BaseLayoutGenerator",

    # Text generators
    "TextGenerateGenerator",
    "TextTransformGenerator",
    "TextAutofitGenerator",

    # Table generators
    "TableGenerateGenerator",
    "TableTransformGenerator",
    "TableAnalyzeGenerator",
]
