"""
Content Generation Module for Text Service v1.3.0

This module implements the 3-phase multi-step content generation pipeline:

Phase 1: Structure Analysis (LLM)
    - Analyzes narrative, topics, available_space, content_context
    - Decides optimal layout structure (columns, sections, emphasis)
    - Returns StructurePlan

Phase 2: Space Calculation (Deterministic)
    - Takes StructurePlan + ThemeConfig
    - Calculates character budgets based on font sizes
    - Returns SpaceBudget

Phase 3: Content Generation (LLM)
    - Uses StructurePlan + SpaceBudget + ContentContext
    - Generates styled HTML within exact constraints
    - Returns final content with theme colors

Per MULTI_STEP_CONTENT_STRUCTURE.md and THEME_SYSTEM_DESIGN.md Section 12.

Version: 1.3.0
"""

from .structure_analyzer import StructureAnalyzer
from .space_calculator import SpaceCalculator
from .html_formatter import HTMLFormatter, format_with_classes, format_with_inline
from .multi_step_generator import MultiStepGenerator

__all__ = [
    "StructureAnalyzer",
    "SpaceCalculator",
    "HTMLFormatter",
    "format_with_classes",
    "format_with_inline",
    "MultiStepGenerator",
]
