"""
I-Series Layout Generators for Text Service v1.2

This module provides generators for I-series layouts (I1, I2, I3, I4)
that combine portrait images with text content.

Layout Overview:
- I1: Wide image (660x1080) on LEFT, content on right
- I2: Wide image (660x1080) on RIGHT, content on left
- I3: Narrow image (360x1080) on LEFT, content on right
- I4: Narrow image (360x1080) on RIGHT, content on left

Usage:
    from app.core.iseries import I1Generator, I2Generator, I3Generator, I4Generator

    generator = I1Generator(llm_service)
    result = await generator.generate(request)
"""

from .base_iseries_generator import BaseISeriesGenerator
from .i1_generator import I1Generator
from .i2_generator import I2Generator
from .i3_generator import I3Generator
from .i4_generator import I4Generator

__all__ = [
    "BaseISeriesGenerator",
    "I1Generator",
    "I2Generator",
    "I3Generator",
    "I4Generator",
]
