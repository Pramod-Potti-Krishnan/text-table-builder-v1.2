"""
I3 Generator - Narrow Image Left Layout

Layout: I3-image-left-narrow
- Image: 360x1080px (6 columns) on LEFT side
- Content: 1500x840px (25 columns) on RIGHT side

Use Case: Text-heavy slides with narrow image accent, detailed content with supporting imagery
Best for: Maximum content space with visual accent
"""

from typing import Dict

from .base_iseries_generator import BaseISeriesGenerator


class I3Generator(BaseISeriesGenerator):
    """
    Generator for I3-image-left-narrow layout.

    Narrow (360px) full-height image on the left side,
    with large content area (1500x840px) on the right.
    This provides the LARGEST content area of all I-series layouts.
    """

    @property
    def layout_type(self) -> str:
        """Return layout type identifier."""
        return "I3"

    @property
    def image_position(self) -> str:
        """Return image position."""
        return "left"

    @property
    def image_dimensions(self) -> Dict[str, int]:
        """Return image dimensions in pixels."""
        return {"width": 360, "height": 1080}

    @property
    def content_dimensions(self) -> Dict[str, int]:
        """Return content area dimensions in pixels."""
        return {"width": 1500, "height": 840}
