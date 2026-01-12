"""
I1 Generator - Wide Image Left Layout

Layout: I1-image-left
- Image: 660x1080px (12 columns) on LEFT side
- Content: 1200x840px (20 columns) on RIGHT side

Use Case: Product showcases, team profiles, case studies with prominent imagery
"""

from typing import Dict

from .base_iseries_generator import BaseISeriesGenerator


class I1Generator(BaseISeriesGenerator):
    """
    Generator for I1-image-left layout.

    Wide (660px) full-height image on the left side,
    with content area (1200x840px) on the right.
    """

    @property
    def layout_type(self) -> str:
        """Return layout type identifier."""
        return "I1"

    @property
    def image_position(self) -> str:
        """Return image position."""
        return "left"

    @property
    def image_dimensions(self) -> Dict[str, int]:
        """Return image dimensions in pixels."""
        return {"width": 660, "height": 1080}

    @property
    def content_dimensions(self) -> Dict[str, int]:
        """Return content area dimensions in pixels."""
        return {"width": 1200, "height": 840}
