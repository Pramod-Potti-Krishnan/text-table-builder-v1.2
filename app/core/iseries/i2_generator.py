"""
I2 Generator - Wide Image Right Layout

Layout: I2-image-right
- Content: 1140x840px (19 columns) on LEFT side
- Image: 660x1080px (12 columns) on RIGHT side

Use Case: Balanced content with imagery on right, case studies, portfolio pieces
"""

from typing import Dict

from .base_iseries_generator import BaseISeriesGenerator


class I2Generator(BaseISeriesGenerator):
    """
    Generator for I2-image-right layout.

    Wide (660px) full-height image on the right side,
    with content area (1140x840px) on the left.
    """

    @property
    def layout_type(self) -> str:
        """Return layout type identifier."""
        return "I2"

    @property
    def image_position(self) -> str:
        """Return image position."""
        return "right"

    @property
    def image_dimensions(self) -> Dict[str, int]:
        """Return image dimensions in pixels."""
        return {"width": 660, "height": 1080}

    @property
    def content_dimensions(self) -> Dict[str, int]:
        """Return content area dimensions in pixels."""
        return {"width": 1140, "height": 840}
