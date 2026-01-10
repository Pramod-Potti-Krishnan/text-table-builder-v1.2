"""
Component Models for Agentic Element Generation
================================================

Pydantic models for the component-based assembly system.
These models define the structure for:
- Component definitions (JSON schema)
- Slot specifications (character limits, descriptions)
- Layout arrangements and space requirements
- Agent tool inputs/outputs

v1.0.0: Initial component assembly architecture
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Enums and Type Definitions
# =============================================================================

class ComponentType(str, Enum):
    """Available component types for assembly."""
    METRICS_CARD = "metrics_card"
    NUMBERED_CARD = "numbered_card"
    COMPARISON_COLUMN = "comparison_column"
    COLORED_SECTION = "colored_section"
    SIDEBAR_BOX = "sidebar_box"


class ArrangementType(str, Enum):
    """Valid arrangement patterns for components."""
    ROW_2 = "row_2"
    ROW_3 = "row_3"
    ROW_4 = "row_4"
    GRID_2X2 = "grid_2x2"
    GRID_2X3 = "grid_2x3"
    GRID_3X2 = "grid_3x2"
    STACKED_2 = "stacked_2"
    STACKED_3 = "stacked_3"
    STACKED_4 = "stacked_4"
    STACKED_5 = "stacked_5"
    SINGLE = "single"


class AudienceType(str, Enum):
    """Target audience types for storytelling decisions."""
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    GENERAL = "general"
    EDUCATIONAL = "educational"
    SALES = "sales"


class PurposeType(str, Enum):
    """Slide purpose types for storytelling decisions."""
    INFORM = "inform"
    PERSUADE = "persuade"
    COMPARE = "compare"
    EXPLAIN = "explain"
    INSPIRE = "inspire"


# =============================================================================
# Slot and Character Limit Models
# =============================================================================

class SlotSpec(BaseModel):
    """
    Specification for a single content slot within a component.

    Defines character limits and description for content generation.
    """
    min_chars: int = Field(
        default=5,
        description="Minimum character count for this slot"
    )
    max_chars: int = Field(
        default=100,
        description="Maximum character count for this slot"
    )
    baseline_chars: Optional[int] = Field(
        default=None,
        description="Ideal/target character count (used for scaling)"
    )
    description: str = Field(
        description="Description of what content goes in this slot"
    )
    format_hint: Optional[str] = Field(
        default=None,
        description="Format hint (e.g., 'UPPERCASE', 'sentence_case', 'number')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "min_chars": 6,
                "max_chars": 18,
                "baseline_chars": 12,
                "description": "Short label in UPPERCASE",
                "format_hint": "UPPERCASE"
            }
        }


class CharLimits(BaseModel):
    """Scaled character limits for a specific slot."""
    min_chars: int
    max_chars: int
    baseline_chars: int

    @property
    def range(self) -> int:
        return self.max_chars - self.min_chars


# =============================================================================
# Variant Models (Colors, Gradients, Styles)
# =============================================================================

class ComponentVariant(BaseModel):
    """
    Visual variant definition for a component.

    Each component can have multiple color/style variants that get
    assigned during layout configuration.
    """
    variant_id: str = Field(
        description="Unique identifier for this variant (e.g., 'purple', 'cyan')"
    )
    gradient: Optional[str] = Field(
        default=None,
        description="CSS gradient value"
    )
    background: Optional[str] = Field(
        default=None,
        description="CSS background color (if not gradient)"
    )
    shadow: Optional[str] = Field(
        default=None,
        description="CSS box-shadow value"
    )
    border: Optional[str] = Field(
        default=None,
        description="CSS border value"
    )
    accent_color: Optional[str] = Field(
        default=None,
        description="Accent color for bullets, icons, etc."
    )
    text_color: Optional[str] = Field(
        default=None,
        description="Text color override for this variant"
    )
    heading_color: Optional[str] = Field(
        default=None,
        description="Color for section/column headings"
    )
    content_background: Optional[str] = Field(
        default=None,
        description="Background color/gradient for content area"
    )

    class Config:
        extra = "allow"  # Allow additional variant properties
        json_schema_extra = {
            "example": {
                "variant_id": "purple",
                "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "shadow": "0 10px 30px rgba(102, 126, 234, 0.3)",
                "text_color": "#ffffff",
                "heading_color": "#667eea",
                "content_background": "linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%)"
            }
        }


# =============================================================================
# Space and Layout Requirements
# =============================================================================

class SpaceRequirements(BaseModel):
    """
    Space requirements for a component type.

    Uses the 32x18 grid system where each cell is 60px.
    """
    min_grid_width: int = Field(
        default=4,
        description="Minimum width in grid units (32-grid system)"
    )
    min_grid_height: int = Field(
        default=4,
        description="Minimum height in grid units (18-grid system)"
    )
    ideal_grid_width: Optional[int] = Field(
        default=None,
        description="Ideal width for optimal display"
    )
    ideal_grid_height: Optional[int] = Field(
        default=None,
        description="Ideal height for optimal display"
    )
    padding_px: int = Field(
        default=24,
        description="Internal padding in pixels"
    )
    min_width_px: Optional[int] = Field(
        default=None,
        description="Minimum width in pixels (calculated from grid if not set)"
    )
    min_height_px: Optional[int] = Field(
        default=None,
        description="Minimum height in pixels (calculated from grid if not set)"
    )


class ArrangementRules(BaseModel):
    """
    Rules for arranging multiple instances of a component.
    """
    min_instances: int = Field(
        default=1,
        description="Minimum number of component instances"
    )
    max_instances: int = Field(
        default=6,
        description="Maximum number of component instances"
    )
    valid_arrangements: List[ArrangementType] = Field(
        default_factory=lambda: [ArrangementType.ROW_3, ArrangementType.ROW_4],
        description="Valid arrangement patterns for this component"
    )
    gap_px: int = Field(
        default=24,
        description="Gap between component instances in pixels"
    )
    prefer_row: bool = Field(
        default=True,
        description="Prefer row arrangement over grid when possible"
    )


class ScalingRules(BaseModel):
    """
    Rules for scaling component content when space is constrained.
    """
    compress_slot: Optional[str] = Field(
        default=None,
        description="Which slot to reduce first when compressing"
    )
    min_scale: float = Field(
        default=0.8,
        description="Minimum scale factor (0.8 = 80% of baseline)"
    )
    expand_slot: Optional[str] = Field(
        default=None,
        description="Which slot to increase when expanding"
    )
    max_scale: float = Field(
        default=1.2,
        description="Maximum scale factor (1.2 = 120% of baseline)"
    )
    preserve_slots: List[str] = Field(
        default_factory=list,
        description="Slots that should NOT be scaled (keep exact limits)"
    )


# =============================================================================
# Component Definition (Main Model)
# =============================================================================

class ComponentDefinition(BaseModel):
    """
    Complete component definition loaded from JSON files.

    This is the main model representing a reusable UI component
    that can be assembled by the agent.
    """
    component_id: str = Field(
        description="Unique identifier for this component"
    )
    description: str = Field(
        description="Human-readable description of the component"
    )
    use_cases: List[str] = Field(
        default_factory=list,
        description="List of use cases this component is good for"
    )
    template: str = Field(
        description="HTML template with {placeholder} variables"
    )
    slots: Dict[str, SlotSpec] = Field(
        description="Content slots with character limits"
    )
    variants: Dict[str, ComponentVariant] = Field(
        description="Visual variants (colors, gradients)"
    )
    space_requirements: SpaceRequirements = Field(
        default_factory=SpaceRequirements,
        description="Space requirements for this component"
    )
    arrangement_rules: ArrangementRules = Field(
        default_factory=ArrangementRules,
        description="Rules for arranging multiple instances"
    )
    scaling_rules: ScalingRules = Field(
        default_factory=ScalingRules,
        description="Rules for scaling content"
    )
    wrapper_template: Optional[str] = Field(
        default=None,
        description="Optional wrapper HTML for multiple instances"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "component_id": "metrics_card",
                "description": "Gradient-filled metric card with number, label, description",
                "use_cases": ["KPIs", "statistics", "performance metrics"],
                "template": "<div style=\"...\">...</div>",
                "slots": {
                    "metric_number": {"min_chars": 2, "max_chars": 6, "description": "The main metric value"},
                    "metric_label": {"min_chars": 6, "max_chars": 18, "description": "Short label in UPPERCASE"}
                },
                "variants": {
                    "purple": {"gradient": "linear-gradient(...)"}
                }
            }
        }


# =============================================================================
# Agent Input/Output Models
# =============================================================================

class SpaceAnalysis(BaseModel):
    """
    Output from analyze_space tool.

    Provides detailed analysis of available space for component placement.
    """
    grid_width: int = Field(description="Available width in grid units")
    grid_height: int = Field(description="Available height in grid units")
    total_width_px: int = Field(description="Total width in pixels")
    total_height_px: int = Field(description="Total height in pixels")
    usable_width_px: int = Field(description="Usable width after padding")
    usable_height_px: int = Field(description="Usable height after padding")
    recommended_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Recommended instance count per component type"
    )
    layout_options: List[str] = Field(
        default_factory=list,
        description="Valid layout options for this space"
    )
    space_category: str = Field(
        default="medium",
        description="Space category: 'small', 'medium', 'large'"
    )


class ComponentSummary(BaseModel):
    """
    Summary of a component for the agent's decision-making.

    Returned by get_available_components tool.
    """
    component_id: str
    description: str
    use_cases: List[str]
    min_space: str = Field(description="Minimum space needed (e.g., '6x5 grid')")
    slot_count: int
    variant_count: int


class LayoutSelection(BaseModel):
    """
    Output from select_component_layout tool.

    Defines how to arrange selected components in the available space.
    """
    component_id: str
    arrangement: ArrangementType
    instance_count: int
    scaled_char_limits: Dict[str, CharLimits] = Field(
        description="Scaled character limits per slot"
    )
    variant_assignments: List[str] = Field(
        description="Variant ID for each instance"
    )
    position_css: Dict[str, str] = Field(
        default_factory=dict,
        description="CSS positioning for the layout"
    )
    fits_space: bool = Field(
        default=True,
        description="Whether the layout fits the available space"
    )


class GeneratedContent(BaseModel):
    """
    Content generated for component slots.

    Output from generate_component_content tool.
    """
    instance_index: int = Field(description="Which instance (0-indexed)")
    slot_values: Dict[str, str] = Field(description="Generated content per slot")
    character_counts: Dict[str, int] = Field(description="Actual character counts")


class AssemblyResult(BaseModel):
    """
    Final HTML assembly result.

    Output from assemble_html tool.
    """
    html: str = Field(description="Complete HTML string")
    component_id: str
    instance_count: int
    arrangement: str
    variants_used: List[str]
    total_characters: int


# =============================================================================
# Agent Context Models
# =============================================================================

class InputContext(BaseModel):
    """
    Input context provided to the agent.

    This is given as INPUT, not reasoned about.
    """
    prompt: str = Field(description="User's content request")
    grid_width: int = Field(description="Available width in grid units")
    grid_height: int = Field(description="Available height in grid units")
    audience: Optional[AudienceType] = Field(
        default=None,
        description="Target audience type"
    )
    purpose: Optional[PurposeType] = Field(
        default=None,
        description="Slide purpose"
    )
    presentation_title: Optional[str] = Field(
        default=None,
        description="Overall presentation title for context"
    )
    slide_position: Optional[int] = Field(
        default=None,
        description="Position of this slide in the deck"
    )


class StorytellingNeeds(BaseModel):
    """
    Agent's reasoning about storytelling needs.

    Step 1 of the Chain of Thought process.
    """
    main_message: str = Field(description="The key message to convey")
    needs_evidence: bool = Field(
        default=False,
        description="Does audience need metrics/data/proof?"
    )
    needs_explanation: bool = Field(
        default=False,
        description="Does audience need bullets/descriptions?"
    )
    needs_comparison: bool = Field(
        default=False,
        description="Does audience need to compare options?"
    )
    needs_process: bool = Field(
        default=False,
        description="Does audience need to understand steps/sequence?"
    )
    needs_callout: bool = Field(
        default=False,
        description="Does content need a highlight/sidebar?"
    )
    evidence_priority: str = Field(
        default="medium",
        description="Priority for evidence: 'high', 'medium', 'low'"
    )


class SpaceBudget(BaseModel):
    """
    Agent's space allocation decision.

    Step 2 of the Chain of Thought process.
    """
    allocations: Dict[str, int] = Field(
        description="Space allocation percentages (e.g., {'metrics': 40, 'explanation': 60})"
    )
    reasoning: str = Field(description="Why this allocation was chosen")


class ComponentChoice(BaseModel):
    """
    Agent's component selection.

    Step 3 of the Chain of Thought process.
    """
    primary_component: str = Field(description="Main component to use")
    primary_count: int = Field(description="Number of primary component instances")
    secondary_component: Optional[str] = Field(
        default=None,
        description="Optional secondary component"
    )
    secondary_count: Optional[int] = Field(
        default=None,
        description="Number of secondary component instances"
    )
    selection_reasoning: str = Field(description="Why these components were chosen")


class AssemblyInfo(BaseModel):
    """
    Metadata about the assembly process.

    Included in API response for transparency.
    """
    component_type: str
    component_count: int
    arrangement: str
    variants_used: List[str]
    agent_reasoning: str = Field(description="Chain of thought reasoning summary")
    storytelling_needs: Optional[StorytellingNeeds] = None
    space_budget: Optional[SpaceBudget] = None


# =============================================================================
# Component Index Model
# =============================================================================

class ComponentIndex(BaseModel):
    """
    Index of all available components.

    Loaded from component_index.json for quick lookup.
    """
    components: Dict[str, str] = Field(
        description="Map of component_id to JSON file path"
    )
    categories: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Components grouped by category"
    )
    version: str = Field(
        default="1.0.0",
        description="Component system version"
    )
