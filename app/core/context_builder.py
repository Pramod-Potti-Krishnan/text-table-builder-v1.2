"""
Context Builder for v1.2 Deterministic Assembly Architecture

This module builds comprehensive context for slide content generation from
the Director's specifications and presentation metadata.

Architecture:
    Director input → Build slide context → Build presentation context
    → Include in element prompts → Generate contextual content
"""

from typing import Dict, List, Optional, Any


class ContextBuilder:
    """Builds context for slide and presentation-level content generation."""

    def __init__(self):
        """Initialize the ContextBuilder."""
        pass

    def build_slide_context(
        self,
        slide_title: str,
        slide_purpose: str,
        key_message: str,
        target_points: Optional[List[str]] = None,
        tone: str = "professional",
        audience: str = "business stakeholders"
    ) -> str:
        """
        Build context specific to the current slide.

        Args:
            slide_title: Title of the slide
            slide_purpose: Purpose or goal of this slide
            key_message: Main message to convey
            target_points: Optional list of specific points to include
            tone: Desired tone (professional, casual, formal, etc.)
            audience: Target audience description

        Returns:
            Formatted slide context string
        """
        context = f"""Slide Title: {slide_title}

Slide Purpose: {slide_purpose}

Key Message: {key_message}

Target Audience: {audience}
Tone: {tone}
"""

        if target_points:
            context += "\nTarget Points to Include:\n"
            for i, point in enumerate(target_points, 1):
                context += f"{i}. {point}\n"

        return context

    def build_presentation_context(
        self,
        presentation_title: str,
        presentation_type: str,
        industry: Optional[str] = None,
        company: Optional[str] = None,
        prior_slides_summary: Optional[str] = None,
        current_slide_number: Optional[int] = None,
        total_slides: Optional[int] = None
    ) -> str:
        """
        Build context about the overall presentation.

        Args:
            presentation_title: Title of the presentation
            presentation_type: Type (e.g., "Business Proposal", "Product Demo")
            industry: Industry context (e.g., "Technology", "Healthcare")
            company: Company name if applicable
            prior_slides_summary: Summary of what's been covered in prior slides
            current_slide_number: Current slide number
            total_slides: Total number of slides

        Returns:
            Formatted presentation context string
        """
        context = f"""Presentation: {presentation_title}
Presentation Type: {presentation_type}
"""

        if industry:
            context += f"Industry: {industry}\n"

        if company:
            context += f"Company: {company}\n"

        if current_slide_number and total_slides:
            context += f"\nSlide Position: {current_slide_number} of {total_slides}\n"

        if prior_slides_summary:
            context += f"""
Prior Slides Context:
{prior_slides_summary}

NOTE: Build upon the narrative established in prior slides. Do not repeat information already covered.
"""

        return context

    def build_element_context(
        self,
        element_id: str,
        element_role: str,
        relationship_to_other_elements: Optional[str] = None
    ) -> str:
        """
        Build context specific to an element's role in the slide.

        Args:
            element_id: Element identifier
            element_role: Role of this element (e.g., "introduce concept", "provide evidence")
            relationship_to_other_elements: How this element relates to others

        Returns:
            Formatted element context string
        """
        context = f"""Element: {element_id}
Role: {element_role}
"""

        if relationship_to_other_elements:
            context += f"""
Relationship to Other Elements:
{relationship_to_other_elements}
"""

        return context

    def build_complete_context(
        self,
        slide_spec: Dict[str, Any],
        presentation_spec: Optional[Dict[str, Any]] = None,
        element_relationships: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Build all context layers from specification dictionaries.

        Args:
            slide_spec: Dictionary with slide-level specifications:
                - slide_title (str)
                - slide_purpose (str)
                - key_message (str)
                - target_points (List[str], optional)
                - tone (str, optional, default="professional")
                - audience (str, optional, default="business stakeholders")

            presentation_spec: Optional dictionary with presentation-level specs:
                - presentation_title (str)
                - presentation_type (str)
                - industry (str, optional)
                - company (str, optional)
                - prior_slides_summary (str, optional)
                - current_slide_number (int, optional)
                - total_slides (int, optional)

            element_relationships: Optional dictionary mapping element_id to relationship description

        Returns:
            Dictionary with "slide_context" and optional "presentation_context" keys
        """
        # Build slide context
        slide_context = self.build_slide_context(
            slide_title=slide_spec["slide_title"],
            slide_purpose=slide_spec["slide_purpose"],
            key_message=slide_spec["key_message"],
            target_points=slide_spec.get("target_points"),
            tone=slide_spec.get("tone", "professional"),
            audience=slide_spec.get("audience", "business stakeholders")
        )

        result = {"slide_context": slide_context}

        # Build presentation context if provided
        if presentation_spec:
            presentation_context = self.build_presentation_context(
                presentation_title=presentation_spec["presentation_title"],
                presentation_type=presentation_spec["presentation_type"],
                industry=presentation_spec.get("industry"),
                company=presentation_spec.get("company"),
                prior_slides_summary=presentation_spec.get("prior_slides_summary"),
                current_slide_number=presentation_spec.get("current_slide_number"),
                total_slides=presentation_spec.get("total_slides")
            )
            result["presentation_context"] = presentation_context

        # Store element relationships for later use
        if element_relationships:
            result["element_relationships"] = element_relationships

        return result

    def augment_with_variant_context(
        self,
        base_context: str,
        variant_id: str,
        variant_description: str
    ) -> str:
        """
        Augment context with information about the chosen variant.

        Args:
            base_context: Existing context string
            variant_id: The variant being used
            variant_description: Description of the variant layout

        Returns:
            Augmented context string
        """
        augmented = base_context + f"""
Layout Variant: {variant_id}
Layout Description: {variant_description}

NOTE: Structure your content to fit this specific layout optimally.
"""
        return augmented
