"""
Service Coordination Module for Text & Table Builder v1.2

Provides content analysis and variant recommendation logic
for Director Agent integration.
"""

from .content_analyzer import (
    ContentAnalyzer,
    VARIANT_SPECS,
    TEXT_SERVICE_KEYWORDS,
    CHART_KEYWORDS,
)

__all__ = [
    "ContentAnalyzer",
    "VARIANT_SPECS",
    "TEXT_SERVICE_KEYWORDS",
    "CHART_KEYWORDS",
]
