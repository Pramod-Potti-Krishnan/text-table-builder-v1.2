"""
I4 Generator - Narrow Image Right Layout

Layout: I4-image-right-narrow
- Content: 1440x840px (24 columns) on LEFT side
- Image: 360x1080px (7 columns) on RIGHT side

Use Case: Text-dominant layouts with narrow accent images, content-focused presentations
Best for: Large content area with visual accent on right
"""

from typing import Dict

from .base_iseries_generator import BaseISeriesGenerator


class I4Generator(BaseISeriesGenerator):
    """
    Generator for I4-image-right-narrow layout.

    Narrow (360px) full-height image on the right side,
    with large content area (1440x840px) on the left.
    """

    @property
    def layout_type(self) -> str:
        """Return layout type identifier."""
        return "I4"

    @property
    def image_position(self) -> str:
        """Return image position."""
        return "right"

    @property
    def image_dimensions(self) -> Dict[str, int]:
        """Return image dimensions in pixels."""
        return {"width": 360, "height": 1080}

    @property
    def content_dimensions(self) -> Dict[str, int]:
        """Return content area dimensions in pixels."""
        return {"width": 1440, "height": 840}
