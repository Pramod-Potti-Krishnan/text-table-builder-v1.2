"""
Hero slide generators for v1.2 Text Service.

Provides specialized generators for L29 hero slides following v1.1's proven pattern:
- TitleSlideGenerator: Opening slides with title, subtitle, attribution
- SectionDividerGenerator: Section transition slides
- ClosingSlideGenerator: Closing slides with CTA and contact info

Image-Enhanced Variants (NEW):
- TitleSlideWithImageGenerator: Title slides with AI-generated 16:9 background images
- SectionDividerWithImageGenerator: Section dividers with AI-generated backgrounds
- ClosingSlideWithImageGenerator: Closing slides with AI-generated backgrounds

All generators inherit from BaseHeroGenerator and generate complete HTML structures
(not field-by-field content) for maximum creative control.
"""

from .base_hero_generator import (
    BaseHeroGenerator,
    HeroGenerationRequest,
    HeroGenerationResponse
)
from .title_slide_generator import TitleSlideGenerator
from .section_divider_generator import SectionDividerGenerator
from .closing_slide_generator import ClosingSlideGenerator

# Image-enhanced variants
from .title_slide_with_image_generator import TitleSlideWithImageGenerator
from .title_slide_structured_with_image_generator import TitleSlideStructuredWithImageGenerator
from .section_divider_with_image_generator import SectionDividerWithImageGenerator
from .closing_slide_with_image_generator import ClosingSlideWithImageGenerator

__all__ = [
    "BaseHeroGenerator",
    "HeroGenerationRequest",
    "HeroGenerationResponse",
    "TitleSlideGenerator",
    "SectionDividerGenerator",
    "ClosingSlideGenerator",
    # Image-enhanced variants
    "TitleSlideWithImageGenerator",
    "TitleSlideStructuredWithImageGenerator",
    "SectionDividerWithImageGenerator",
    "ClosingSlideWithImageGenerator",
]
