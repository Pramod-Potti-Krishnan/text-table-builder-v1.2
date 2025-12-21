"""
Multi-Step Content Generator - Orchestrates 3-Phase Generation

Coordinates the three phases of content generation:
1. Structure Analysis (LLM) - Determines optimal layout
2. Space Calculation (Deterministic) - Calculates character budgets
3. Content Generation (LLM) - Generates styled content within constraints

Per MULTI_STEP_CONTENT_STRUCTURE.md:
- Achieves ~85% space utilization vs ~30% with single-step
- Trade-off: 2 LLM calls instead of 1
- Theme affects Phase 2 (font sizes) and Phase 3 (colors)
- ContentContext affects Phase 1 (structure) and Phase 3 (tone)

Version: 1.3.0
"""

import json
import logging
import time
from typing import List, Optional, Dict, Any

from app.models.space_models import (
    StructurePlan, SpaceBudget, GenerationContext, LayoutStructure
)
from app.models.content_context import ContentContext, get_default_content_context
from app.models.requests import ThemeConfig
from app.models.slides_models import ContentSlideResponse

from .structure_analyzer import StructureAnalyzer
from .space_calculator import SpaceCalculator
from .html_formatter import HTMLFormatter

logger = logging.getLogger(__name__)


# =============================================================================
# Content Generation Prompt Template
# =============================================================================

CONTENT_GENERATION_PROMPT = """Generate content for a presentation slide based on the following specifications.

STRUCTURE:
- Layout: {layout_type} with {columns} column(s)
- Heading: {heading_text}
- Sections: {section_count}

CONTENT CONTEXT:
- Audience: {audience_type} ({complexity_descriptor})
- Purpose: {purpose_type}
- Tone: {emotional_tone}
- Max words per sentence: {max_sentence_words}

SPACE BUDGET:
- Heading: max {heading_max_chars} characters
- Sections (each):
{section_budgets}

NARRATIVE:
{narrative}

TOPICS:
{topics}

OUTPUT FORMAT (JSON):
{{
    "heading": "Concise heading text (within {heading_max_chars} chars)",
    "sections": [
        {{
            "title": "Section title (optional)",
            "content": "Section content as HTML",
            "items": ["bullet 1", "bullet 2", "..."]
        }}
    ]
}}

STYLE REQUIREMENTS:
- {tone_instructions}
- Use {styling_mode} for HTML output
{styling_instructions}

Return ONLY the JSON object, no additional text."""


# =============================================================================
# Multi-Step Generator Class
# =============================================================================

class MultiStepGenerator:
    """
    Orchestrates 3-phase content generation.

    Phases:
    1. Structure Analysis - LLM decides layout structure
    2. Space Calculation - Deterministic character budgets
    3. Content Generation - LLM generates within constraints

    Usage:
        generator = MultiStepGenerator(llm_service)
        response = await generator.generate(
            narrative="Key benefits of AI",
            topics=["Speed", "Accuracy", "Cost"],
            available_width_px=1800,
            available_height_px=840,
            theme_config=theme,
            content_context=context
        )
    """

    def __init__(self, llm_service):
        """
        Initialize the multi-step generator.

        Args:
            llm_service: LLM service for text generation
        """
        self.llm_service = llm_service
        self.structure_analyzer = StructureAnalyzer(llm_service)
        self.space_calculator = SpaceCalculator()

    async def generate(
        self,
        narrative: str,
        topics: List[str],
        available_width_px: int,
        available_height_px: int,
        theme_config: Optional[ThemeConfig] = None,
        content_context: Optional[ContentContext] = None,
        styling_mode: str = "inline_styles",
        slide_number: int = 1,
        variant_id: Optional[str] = None
    ) -> ContentSlideResponse:
        """
        Generate content using 3-phase pipeline.

        Args:
            narrative: Main narrative or topic
            topics: List of key topics
            available_width_px: Available width in pixels
            available_height_px: Available height in pixels
            theme_config: Theme configuration
            content_context: Audience/Purpose/Time context
            styling_mode: "inline_styles" or "css_classes"
            slide_number: Slide number for context
            variant_id: Optional variant ID hint

        Returns:
            ContentSlideResponse with generated content
        """
        start_time = time.time()
        phases_completed = []

        if content_context is None:
            content_context = get_default_content_context()

        # Get theme ID for tracking
        theme_id = theme_config.theme_id if theme_config else "professional"

        try:
            # =====================================================
            # Phase 1: Structure Analysis (LLM)
            # =====================================================
            phase1_start = time.time()

            structure = await self.structure_analyzer.analyze(
                narrative=narrative,
                topics=topics,
                available_width_px=available_width_px,
                available_height_px=available_height_px,
                content_context=content_context,
                slide_number=slide_number
            )
            phases_completed.append("structure")
            phase1_time = int((time.time() - phase1_start) * 1000)

            logger.info(f"Phase 1 complete: {structure.layout_type.value}, {len(structure.sections)} sections")

            # =====================================================
            # Phase 2: Space Calculation (Deterministic)
            # =====================================================
            phase2_start = time.time()

            budget = self.space_calculator.calculate(
                structure=structure,
                available_width_px=available_width_px,
                available_height_px=available_height_px,
                theme_config=theme_config
            )
            phases_completed.append("space")
            phase2_time = int((time.time() - phase2_start) * 1000)

            logger.info(f"Phase 2 complete: {budget.total_body_chars} chars available")

            # =====================================================
            # Phase 3: Content Generation (LLM)
            # =====================================================
            phase3_start = time.time()

            content = await self._generate_content(
                narrative=narrative,
                topics=topics,
                structure=structure,
                budget=budget,
                theme_config=theme_config,
                content_context=content_context,
                styling_mode=styling_mode
            )
            phases_completed.append("content")
            phase3_time = int((time.time() - phase3_start) * 1000)

            logger.info(f"Phase 3 complete: content generated")

            # =====================================================
            # Build Response
            # =====================================================
            total_time = int((time.time() - start_time) * 1000)

            # Initialize formatter to track CSS classes
            formatter = HTMLFormatter(
                styling_mode=styling_mode,
                theme_config=theme_config,
                theme_id=theme_id
            )

            # Format content
            formatted = self._format_content(content, formatter)

            return ContentSlideResponse(
                slide_title=formatted["slide_title"],
                subtitle=formatted.get("subtitle"),
                body=formatted["body"],
                rich_content=formatted["body"],  # Alias
                background_color="#ffffff",
                metadata={
                    "slide_number": slide_number,
                    "variant_id": variant_id or "multi_step",
                    "llm_calls": 2,  # Structure + Content
                    "generation_mode": "multi_step",
                    "theme_id": theme_id,
                    "theme_version": theme_config.version if theme_config else None,
                    "theme_source": "config" if theme_config else "fallback",
                    "styling_mode": styling_mode,
                    "css_classes_used": formatter.css_classes_used if styling_mode == "css_classes" else [],
                    "content_context": {
                        "audience_type": content_context.audience.audience_type.value,
                        "purpose_type": content_context.purpose.purpose_type.value,
                        "duration_minutes": content_context.time.duration_minutes
                    },
                    "multi_step": {
                        "enabled": True,
                        "phases_completed": phases_completed,
                        "structure_plan": {
                            "layout_type": structure.layout_type.value,
                            "columns": structure.columns,
                            "sections": len(structure.sections),
                            "rationale": structure.rationale
                        },
                        "space_budget": {
                            "heading_chars": budget.heading_max_chars,
                            "body_chars": budget.total_body_chars,
                            "total_lines": budget.total_lines
                        },
                        "phase_times_ms": {
                            "structure": phase1_time,
                            "space": phase2_time,
                            "content": phase3_time
                        }
                    },
                    "generation_time_ms": total_time
                }
            )

        except Exception as e:
            logger.error(f"Multi-step generation failed: {e}")
            # Fall back to simple generation
            return await self._fallback_generation(
                narrative=narrative,
                topics=topics,
                theme_config=theme_config,
                content_context=content_context,
                styling_mode=styling_mode,
                slide_number=slide_number,
                error=str(e)
            )

    async def _generate_content(
        self,
        narrative: str,
        topics: List[str],
        structure: StructurePlan,
        budget: SpaceBudget,
        theme_config: Optional[ThemeConfig],
        content_context: ContentContext,
        styling_mode: str
    ) -> Dict[str, Any]:
        """Generate content within structure and budget constraints."""
        # Build section budget descriptions
        section_budget_lines = []
        for sb in budget.section_budgets:
            section_budget_lines.append(
                f"  - Section {sb.section_index + 1}: max {sb.max_chars} chars, {sb.max_lines} lines"
            )

        # Styling instructions based on mode
        if styling_mode == "css_classes":
            styling_instructions = """- Use CSS classes: .deckster-t1, .deckster-t2, .deckster-t3, .deckster-t4
- Example: <h2 class="deckster-t1">Heading</h2>
- Do NOT include inline styles"""
        else:
            styling_instructions = """- Use inline CSS styles for all HTML elements
- Include font-size, font-weight, color in style attributes
- Example: <h2 style="font-size:32px;font-weight:700;color:#1f2937;">Heading</h2>"""

        # Build prompt
        prompt = CONTENT_GENERATION_PROMPT.format(
            layout_type=structure.layout_type.value,
            columns=structure.columns,
            heading_text=structure.heading_text or "Generate appropriate heading",
            section_count=len(structure.sections),
            audience_type=content_context.audience.audience_type.value,
            complexity_descriptor=content_context.get_complexity_descriptor(),
            purpose_type=content_context.purpose.purpose_type.value,
            emotional_tone=content_context.purpose.emotional_tone,
            max_sentence_words=content_context.audience.max_sentence_words,
            heading_max_chars=budget.heading_max_chars,
            section_budgets="\n".join(section_budget_lines),
            narrative=narrative,
            topics=", ".join(topics) if topics else "Expand on narrative",
            tone_instructions=content_context.get_tone_instructions(),
            styling_mode=styling_mode,
            styling_instructions=styling_instructions
        )

        # Call LLM
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.5
        )

        # Parse response
        return self._parse_content_response(response)

    def _parse_content_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM content response."""
        try:
            text = response.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            if text.endswith("```"):
                text = text[:-3]

            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse content response: {e}")
            return {"heading": "Content", "sections": []}

    def _format_content(
        self,
        content: Dict[str, Any],
        formatter: HTMLFormatter
    ) -> Dict[str, Any]:
        """Format raw content into HTML."""
        heading = content.get("heading", "")
        sections = content.get("sections", [])

        # Format heading
        slide_title = formatter.format_heading(heading)

        # Format sections into body
        body_parts = []
        for section in sections:
            # Section title if present
            if section.get("title"):
                body_parts.append(formatter.format_subheading(section["title"]))

            # Section content
            if section.get("content"):
                body_parts.append(section["content"])
            elif section.get("items"):
                body_parts.append(formatter.format_bullet_list(section["items"]))

        body = "\n".join(body_parts)

        return {
            "slide_title": slide_title,
            "subtitle": None,  # Could be extracted from content if needed
            "body": body
        }

    async def _fallback_generation(
        self,
        narrative: str,
        topics: List[str],
        theme_config: Optional[ThemeConfig],
        content_context: ContentContext,
        styling_mode: str,
        slide_number: int,
        error: str
    ) -> ContentSlideResponse:
        """Fallback to simple single-step generation."""
        logger.warning(f"Using fallback generation due to: {error}")

        formatter = HTMLFormatter(
            styling_mode=styling_mode,
            theme_config=theme_config,
            theme_id=theme_config.theme_id if theme_config else "professional"
        )

        # Simple content generation
        slide_title = formatter.format_heading(narrative[:60])

        if topics:
            body = formatter.format_bullet_list(topics)
        else:
            body = formatter.format_body(narrative)

        return ContentSlideResponse(
            slide_title=slide_title,
            subtitle=None,
            body=body,
            rich_content=body,
            background_color="#ffffff",
            metadata={
                "slide_number": slide_number,
                "llm_calls": 0,
                "generation_mode": "fallback",
                "styling_mode": styling_mode,
                "css_classes_used": formatter.css_classes_used,
                "fallback_reason": error,
                "multi_step": {
                    "enabled": False,
                    "phases_completed": [],
                    "error": error
                }
            }
        )


# =============================================================================
# Quick Generation Utility
# =============================================================================

async def generate_multi_step(
    llm_service,
    narrative: str,
    topics: List[str],
    width_grids: int = 30,
    height_grids: int = 14,
    theme_id: str = "professional",
    audience_type: str = "professional",
    purpose_type: str = "inform",
    styling_mode: str = "inline_styles"
) -> ContentSlideResponse:
    """
    Convenience function for multi-step generation with defaults.

    Args:
        llm_service: LLM service
        narrative: Main narrative
        topics: Key topics
        width_grids: Width in grids (60px each)
        height_grids: Height in grids
        theme_id: Theme identifier
        audience_type: Audience type
        purpose_type: Purpose type
        styling_mode: Output mode

    Returns:
        ContentSlideResponse
    """
    from app.models.content_context import build_content_context
    from app.core.theme.presets import get_theme_preset

    # Build context
    content_context = build_content_context(audience_type, purpose_type)

    # Get theme config from presets
    theme_data = get_theme_preset(theme_id)
    theme_config = ThemeConfig(theme_id=theme_id)

    # Calculate pixel dimensions
    width_px = width_grids * 60
    height_px = height_grids * 60

    # Generate
    generator = MultiStepGenerator(llm_service)
    return await generator.generate(
        narrative=narrative,
        topics=topics,
        available_width_px=width_px,
        available_height_px=height_px,
        theme_config=theme_config,
        content_context=content_context,
        styling_mode=styling_mode
    )
