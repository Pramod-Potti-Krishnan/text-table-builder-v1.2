"""
Slides Module for Text Service v1.2 - Layout Service Aligned Endpoints

This module provides generators for the unified /v1.2/slides/* router
with Layout Service naming conventions (H1, H2, H3, C1, I1-I4).

Key Features:
- Combined generation for C1-text (saves 2 LLM calls per slide)
- Wrapper generators that reuse existing hero/iseries generators
- Field extraction for structured responses
- Backward compatibility with existing endpoints

Version: 1.2.1
"""

from .field_extractor import (
    extract_structured_fields,
    extract_title,
    extract_subtitle,
    strip_html_tags
)
from .base_slide_generator import BaseSlideGenerator
from .c1_text_generator import C1TextGenerator

# H-series generator wrappers (delegate to existing hero generators)
from .h1_generated_generator import H1GeneratedGenerator
from .h1_structured_generator import H1StructuredGenerator
from .h2_section_generator import H2SectionGenerator
from .h3_closing_generator import H3ClosingGenerator

__all__ = [
    # Field extraction
    'extract_structured_fields',
    'extract_title',
    'extract_subtitle',
    'strip_html_tags',

    # Base class
    'BaseSlideGenerator',

    # Generators
    'C1TextGenerator',
    'H1GeneratedGenerator',
    'H1StructuredGenerator',
    'H2SectionGenerator',
    'H3ClosingGenerator',
]
