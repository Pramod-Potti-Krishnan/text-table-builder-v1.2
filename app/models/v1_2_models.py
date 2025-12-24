"""
Pydantic Models for v1.2 Element-Based Content Generation API

These models define the request and response structures for the v1.2 endpoint
which uses deterministic assembly architecture.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SlideSpecification(BaseModel):
    """Specification for slide-level context."""

    slide_title: str = Field(..., description="Title of the slide")
    slide_purpose: str = Field(..., description="Purpose or goal of this slide")
    key_message: str = Field(..., description="Main message to convey")
    target_points: Optional[List[str]] = Field(
        None,
        description="Optional list of specific points to include"
    )
    tone: str = Field(
        default="professional",
        description="Desired tone (professional, casual, formal, etc.)"
    )
    audience: str = Field(
        default="business stakeholders",
        description="Target audience description"
    )


class PresentationSpecification(BaseModel):
    """Specification for presentation-level context."""

    presentation_title: str = Field(..., description="Title of the presentation")
    presentation_type: str = Field(
        ...,
        description="Type of presentation (e.g., 'Business Proposal', 'Product Demo')"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry context (e.g., 'Technology', 'Healthcare')"
    )
    company: Optional[str] = Field(
        None,
        description="Company name if applicable"
    )
    prior_slides_summary: Optional[str] = Field(
        None,
        description="Summary of what's been covered in prior slides"
    )
    current_slide_number: Optional[int] = Field(
        None,
        description="Current slide number"
    )
    total_slides: Optional[int] = Field(
        None,
        description="Total number of slides in presentation"
    )


class ThemeSettings(BaseModel):
    """
    Theme settings passed from Director for CSS variable theming (v1.2.2).

    This enables light/dark mode switching when USE_CSS_VARIABLES=true.
    The theme_mode value is passed to the Layout Service for CSS variable resolution.
    """

    theme_id: str = Field(
        default="corporate-blue",
        description="Theme identifier (e.g., 'corporate-blue', 'elegant-emerald')"
    )
    theme_mode: str = Field(
        default="light",
        description="Theme mode: 'light' or 'dark'"
    )


class V1_2_GenerationRequest(BaseModel):
    """Request model for v1.2 element-based content generation."""

    variant_id: str = Field(
        ...,
        description="Variant identifier (e.g., 'matrix_2x2', 'table_3col')",
        example="matrix_2x2"
    )
    layout_id: Optional[str] = Field(
        default="L25",
        description="Layout ID for template selection: 'L25' (720px content height) or 'C1' (840px content height)"
    )
    slide_spec: SlideSpecification = Field(
        ...,
        description="Slide-level specifications and context"
    )
    presentation_spec: Optional[PresentationSpecification] = Field(
        None,
        description="Optional presentation-level context"
    )
    element_relationships: Optional[Dict[str, str]] = Field(
        None,
        description="Optional dictionary mapping element_id to relationship description"
    )
    enable_parallel: bool = Field(
        default=True,
        description="Whether to generate elements in parallel for faster processing"
    )
    validate_character_counts: bool = Field(
        default=True,
        description="Whether to validate generated content against character count requirements"
    )
    theme_settings: Optional[ThemeSettings] = Field(
        None,
        description="Optional theme settings for CSS variable theming (v1.2.2)"
    )


class ElementContent(BaseModel):
    """Generated content for a single element."""

    element_id: str = Field(..., description="Element identifier")
    element_type: str = Field(..., description="Type of element")
    placeholders: Dict[str, str] = Field(
        ...,
        description="Mapping of field names to placeholder names"
    )
    generated_content: Dict[str, str] = Field(
        ...,
        description="Generated content for each field"
    )
    character_counts: Dict[str, int] = Field(
        ...,
        description="Character counts for each generated field"
    )


class CharacterCountViolation(BaseModel):
    """Details about a character count requirement violation."""

    element_id: str
    field: str
    actual_count: int
    required_min: int
    required_max: int


class ValidationResult(BaseModel):
    """Character count validation results."""

    valid: bool = Field(..., description="Whether all counts are valid")
    violations: List[CharacterCountViolation] = Field(
        default_factory=list,
        description="List of character count violations"
    )


class GenerationMetadata(BaseModel):
    """Metadata about the generation process."""

    variant_id: str
    template_path: str
    element_count: int
    generation_mode: str = Field(
        ...,
        description="Generation mode: 'parallel' or 'sequential'"
    )


class V1_2_GenerationResponse(BaseModel):
    """Response model for v1.2 element-based content generation."""

    success: bool = Field(..., description="Whether generation succeeded")
    html: Optional[str] = Field(
        None,
        description="Assembled HTML for the slide"
    )
    elements: Optional[List[ElementContent]] = Field(
        None,
        description="List of generated element contents"
    )
    metadata: Optional[GenerationMetadata] = Field(
        None,
        description="Generation metadata"
    )
    validation: Optional[ValidationResult] = Field(
        None,
        description="Character count validation results (if validation enabled)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )
    variant_id: Optional[str] = Field(
        None,
        description="The variant identifier used"
    )
    template_path: Optional[str] = Field(
        None,
        description="Path to the template used"
    )


class VariantInfo(BaseModel):
    """Information about an available variant."""

    variant_id: str
    slide_type: str
    description: str
    layout: str


class AvailableVariantsResponse(BaseModel):
    """Response listing all available variants."""

    total_variants: int
    slide_types: Dict[str, List[VariantInfo]]
