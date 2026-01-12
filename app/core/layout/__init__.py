"""
Layout Service Integration Module for Text & Table Builder v1.2

Provides grid-based text and table generation with constraint-aware
HTML+CSS output for the Layout Service integration.

Grid System: 32×18 grid (1920×1080px HD slides, 60×60px cells)

Endpoints supported:
- /api/ai/text/generate - Generate new text content
- /api/ai/text/transform - Transform existing text
- /api/ai/text/autofit - Fit text to element dimensions
- /api/ai/table/generate - Generate structured table
- /api/ai/table/transform - Modify table structure
- /api/ai/table/analyze - Get insights from table data
- /api/ai/slide/title - Generate slide title
- /api/ai/slide/subtitle - Generate slide subtitle
- /api/ai/slide/title-slide - Generate title slide content
- /api/ai/slide/section - Generate section divider content
- /api/ai/slide/closing - Generate closing slide content
- /api/ai/element/text - Generate generic text element
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
from .slide_text_generator import (
    SlideTextGenerator,
    TitleSlideGenerator,
    SectionSlideGenerator,
    ClosingSlideGenerator,
    GenericTextElementGenerator,
    create_slide_text_generator,
    create_title_slide_generator,
    create_section_slide_generator,
    create_closing_slide_generator,
    create_generic_text_generator
)

__all__ = [
    # Calculator
    "GridCalculator",

    # Base class
    "BaseLayoutGenerator",

    # Text generators (original)
    "TextGenerateGenerator",
    "TextTransformGenerator",
    "TextAutofitGenerator",

    # Table generators
    "TableGenerateGenerator",
    "TableTransformGenerator",
    "TableAnalyzeGenerator",

    # Slide text generators (32×18 grid)
    "SlideTextGenerator",
    "TitleSlideGenerator",
    "SectionSlideGenerator",
    "ClosingSlideGenerator",
    "GenericTextElementGenerator",

    # Factory functions
    "create_slide_text_generator",
    "create_title_slide_generator",
    "create_section_slide_generator",
    "create_closing_slide_generator",
    "create_generic_text_generator",
]
