"""
Space and Structure Models for Multi-Step Content Generation v1.3.0

Models for the 3-phase content generation pipeline:
- Phase 1 Output: StructurePlan (LLM decides layout structure)
- Phase 2 Output: SpaceBudget (deterministic character calculations)
- Phase 3 Input: Both above + theme + content_context

Per MULTI_STEP_CONTENT_STRUCTURE.md Section 2-4.

Version: 1.3.0
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Structure Layout Types
# =============================================================================

class LayoutStructure(str, Enum):
    """
    Layout structure types decided by Phase 1 analysis.

    Per MULTI_STEP_CONTENT_STRUCTURE.md Section 3.
    """
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "2_column"
    THREE_COLUMN = "3_column"
    HEADING_PLUS_COLUMNS = "heading_plus_columns"
    GRID_2X2 = "grid_2x2"
    GRID_2X3 = "grid_2x3"
    GRID_3X2 = "grid_3x2"


class EmphasisType(str, Enum):
    """Types of emphasis for content elements."""
    BOLD = "bold"
    HIGHLIGHT = "highlight"
    ACCENT_COLOR = "accent_color"
    BOX = "box"
    ICON = "icon"


# =============================================================================
# Phase 1 Output: Structure Plan
# =============================================================================

class SectionPlan(BaseModel):
    """Plan for a single content section."""
    title: Optional[str] = Field(
        default=None,
        description="Section title/heading"
    )
    content_type: str = Field(
        default="bullets",
        description="Content type: bullets, paragraph, numbered, mixed"
    )
    estimated_items: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Estimated number of items (bullets, paragraphs)"
    )
    emphasis: bool = Field(
        default=False,
        description="Whether this section should be emphasized"
    )


class StructurePlan(BaseModel):
    """
    Phase 1 Output: LLM-determined content structure.

    The Structure Analyzer (LLM) examines the narrative, topics,
    available_space, and content_context to decide the optimal layout.

    Per MULTI_STEP_CONTENT_STRUCTURE.md Section 3.
    """
    layout_type: LayoutStructure = Field(
        description="Layout structure type"
    )
    columns: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Number of columns"
    )
    has_heading: bool = Field(
        default=True,
        description="Whether to include a main heading"
    )
    heading_text: Optional[str] = Field(
        default=None,
        description="Suggested heading text (refined in Phase 3)"
    )
    sections: List[SectionPlan] = Field(
        default_factory=list,
        description="Planned sections with content types"
    )
    emphasis_points: List[int] = Field(
        default_factory=list,
        description="Indices of sections to emphasize"
    )
    rationale: Optional[str] = Field(
        default=None,
        description="Brief explanation of structure choice"
    )

    def total_sections(self) -> int:
        """Get total number of sections."""
        return len(self.sections)

    def has_emphasis(self) -> bool:
        """Check if any section has emphasis."""
        return len(self.emphasis_points) > 0 or any(s.emphasis for s in self.sections)

    class Config:
        json_schema_extra = {
            "example": {
                "layout_type": "2_column",
                "columns": 2,
                "has_heading": True,
                "heading_text": "Benefits of Cloud Migration",
                "sections": [
                    {"title": "Cost Savings", "content_type": "bullets", "estimated_items": 3},
                    {"title": "Scalability", "content_type": "bullets", "estimated_items": 3}
                ],
                "emphasis_points": [0],
                "rationale": "2-column layout balances space with 3 topics"
            }
        }


# =============================================================================
# Phase 2 Output: Space Budget
# =============================================================================

class SectionBudget(BaseModel):
    """Character budget for a single section."""
    section_index: int = Field(
        description="Index of the section (0-based)"
    )
    max_chars: int = Field(
        description="Maximum characters for this section"
    )
    max_lines: int = Field(
        description="Maximum lines for this section"
    )
    chars_per_line: int = Field(
        description="Characters per line (based on font size)"
    )
    typography_level: str = Field(
        default="t3",
        description="Typography level to use (t1-t4)"
    )


class SpaceBudget(BaseModel):
    """
    Phase 2 Output: Deterministic character budget calculations.

    The Space Calculator takes StructurePlan + ThemeConfig and computes
    exact character limits for each element based on:
    - Available pixel dimensions (from available_space)
    - Font sizes (from theme_config.typography)
    - Line heights (from theme_config)
    - 10% margins and padding

    Per MULTI_STEP_CONTENT_STRUCTURE.md Section 4.
    """
    # Overall dimensions
    total_width_px: int = Field(
        description="Total available width in pixels"
    )
    total_height_px: int = Field(
        description="Total available height in pixels"
    )
    usable_width_px: int = Field(
        description="Usable width after margins (90%)"
    )
    usable_height_px: int = Field(
        description="Usable height after margins (90%)"
    )

    # Heading budget
    heading_max_chars: int = Field(
        description="Maximum characters for heading"
    )
    heading_typography: str = Field(
        default="t1",
        description="Typography level for heading"
    )

    # Section budgets
    section_budgets: List[SectionBudget] = Field(
        default_factory=list,
        description="Character budgets per section"
    )

    # Column layout info
    columns: int = Field(
        default=1,
        description="Number of columns"
    )
    column_width_px: int = Field(
        description="Width per column in pixels"
    )

    # Total available space
    total_lines: int = Field(
        description="Total available lines (body area)"
    )
    total_body_chars: int = Field(
        description="Total character budget for body content"
    )

    # Font metrics used
    char_width_ratio: float = Field(
        default=0.5,
        description="Character width ratio (avg char width / font size)"
    )

    def get_section_budget(self, index: int) -> Optional[SectionBudget]:
        """Get budget for a specific section."""
        for budget in self.section_budgets:
            if budget.section_index == index:
                return budget
        return None

    def utilization_percentage(self) -> float:
        """Calculate expected space utilization."""
        if self.total_body_chars == 0:
            return 0.0
        used = sum(sb.max_chars for sb in self.section_budgets) + self.heading_max_chars
        return (used / (self.total_body_chars + self.heading_max_chars)) * 100

    class Config:
        json_schema_extra = {
            "example": {
                "total_width_px": 1800,
                "total_height_px": 840,
                "usable_width_px": 1620,
                "usable_height_px": 756,
                "heading_max_chars": 68,
                "heading_typography": "t1",
                "section_budgets": [
                    {"section_index": 0, "max_chars": 400, "max_lines": 12, "chars_per_line": 74, "typography_level": "t3"},
                    {"section_index": 1, "max_chars": 400, "max_lines": 12, "chars_per_line": 74, "typography_level": "t3"}
                ],
                "columns": 2,
                "column_width_px": 790,
                "total_lines": 23,
                "total_body_chars": 1702,
                "char_width_ratio": 0.5
            }
        }


# =============================================================================
# Complete Generation Context (Phase 3 Input)
# =============================================================================

class GenerationContext(BaseModel):
    """
    Complete context for Phase 3 content generation.

    Combines all inputs needed for the final LLM call:
    - Original narrative and topics
    - Structure plan (from Phase 1)
    - Space budget (from Phase 2)
    - Theme configuration
    - Content context (audience/purpose/time)
    """
    # Original inputs
    narrative: str = Field(
        description="Original narrative/topic"
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Key topics to cover"
    )

    # Phase 1 output
    structure_plan: StructurePlan = Field(
        description="Structure plan from Phase 1"
    )

    # Phase 2 output
    space_budget: SpaceBudget = Field(
        description="Space budget from Phase 2"
    )

    # Theme configuration (simplified for prompt)
    theme_id: str = Field(
        default="professional",
        description="Theme ID"
    )
    colors: Dict[str, str] = Field(
        default_factory=dict,
        description="Key colors to use in content"
    )

    # Content context (simplified for prompt)
    audience_type: str = Field(
        default="professional",
        description="Audience type"
    )
    purpose_type: str = Field(
        default="inform",
        description="Purpose type"
    )
    max_sentence_words: int = Field(
        default=15,
        description="Maximum words per sentence"
    )
    emotional_tone: str = Field(
        default="neutral",
        description="Emotional tone"
    )

    # Output preferences
    styling_mode: str = Field(
        default="inline_styles",
        description="Output mode: inline_styles or css_classes"
    )

    def to_prompt_context(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM prompt."""
        return {
            "narrative": self.narrative,
            "topics": self.topics,
            "layout_type": self.structure_plan.layout_type.value,
            "columns": self.structure_plan.columns,
            "sections": [
                {
                    "title": s.title,
                    "content_type": s.content_type,
                    "max_chars": self.space_budget.get_section_budget(i).max_chars if self.space_budget.get_section_budget(i) else 300,
                    "emphasis": s.emphasis,
                }
                for i, s in enumerate(self.structure_plan.sections)
            ],
            "heading_max_chars": self.space_budget.heading_max_chars,
            "audience_type": self.audience_type,
            "purpose_type": self.purpose_type,
            "max_sentence_words": self.max_sentence_words,
            "emotional_tone": self.emotional_tone,
            "styling_mode": self.styling_mode,
            "colors": self.colors,
            "theme_id": self.theme_id,
        }

    class Config:
        json_schema_extra = {
            "example": {
                "narrative": "Benefits of cloud migration",
                "topics": ["Cost savings", "Scalability", "Security"],
                "structure_plan": {"layout_type": "2_column", "columns": 2},
                "space_budget": {"total_width_px": 1800, "usable_width_px": 1620},
                "theme_id": "professional",
                "audience_type": "professional",
                "purpose_type": "inform",
                "styling_mode": "inline_styles"
            }
        }
