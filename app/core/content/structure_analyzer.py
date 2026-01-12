"""
Structure Analyzer - Phase 1 of Multi-Step Content Generation

Analyzes narrative, topics, available_space, and content_context to determine
the optimal layout structure for content slides.

Per MULTI_STEP_CONTENT_STRUCTURE.md Section 3:
- Uses LLM to decide layout (single_column, 2_column, 3_column)
- ContentContext affects decisions (audience.max_bullets, purpose.structure_pattern)
- Returns StructurePlan with sections, emphasis points, rationale

Version: 1.3.0
"""

import json
import logging
from typing import List, Optional, Dict, Any

from app.models.space_models import (
    StructurePlan, SectionPlan, LayoutStructure
)
from app.models.content_context import ContentContext, get_default_content_context

logger = logging.getLogger(__name__)


# =============================================================================
# Structure Analysis Prompt Template
# =============================================================================

STRUCTURE_ANALYSIS_PROMPT = """Analyze the following content and available space to determine the optimal layout structure.

CONTENT:
- Narrative: {narrative}
- Topics: {topics}
- Slide Number: {slide_number}

AVAILABLE SPACE:
- Width: {width} pixels
- Height: {height} pixels
- Usable area (after 10% margins): {usable_width}x{usable_height} pixels

CONTENT CONTEXT:
- Audience: {audience_type} (max {max_bullets} bullets per section)
- Purpose: {purpose_type} (structure pattern: {structure_pattern})
- Content Depth: {content_depth}
- Emotional Tone: {emotional_tone}

LAYOUT OPTIONS:
1. single_column - Best for focused narrative, fewer topics (2-3)
2. 2_column - Best for comparisons, contrasts, 4-6 topics
3. 3_column - Best for many short items, 6+ topics
4. heading_plus_columns - Heading spans full width, content in columns below
5. grid_2x2 - 4 equal boxes, good for metrics or categories
6. grid_2x3 - 6 equal boxes, good for feature lists
7. grid_3x2 - 6 boxes in 3 columns, 2 rows

DECISION CRITERIA:
- Topic count: 1-3 topics → single_column, 4-6 → 2_column, 7+ → 3_column or grid
- Content type: Metrics/stats → grid, Comparison → 2_column, Narrative → single_column
- Audience: Kids → fewer sections (max 3), Executive → concise (max 4)
- Purpose: Persuade → emphasis on key point, Educate → sequential structure

Return a JSON object with this structure:
{{
    "layout_type": "2_column",
    "columns": 2,
    "has_heading": true,
    "heading_text": "Suggested heading text",
    "sections": [
        {{"title": "Section Title", "content_type": "bullets", "estimated_items": 3, "emphasis": false}},
        {{"title": "Another Section", "content_type": "bullets", "estimated_items": 4, "emphasis": true}}
    ],
    "emphasis_points": [1],
    "rationale": "Brief explanation of why this structure was chosen"
}}

Return ONLY the JSON object, no additional text."""


# =============================================================================
# Structure Analyzer Class
# =============================================================================

class StructureAnalyzer:
    """
    Phase 1: Analyzes content to determine optimal structure.

    Uses LLM to decide layout type, sections, and emphasis based on:
    - Narrative and topics
    - Available space dimensions
    - Content context (audience, purpose, time)
    """

    def __init__(self, llm_service):
        """
        Initialize the structure analyzer.

        Args:
            llm_service: LLM service for content analysis
        """
        self.llm_service = llm_service

    async def analyze(
        self,
        narrative: str,
        topics: List[str],
        available_width_px: int,
        available_height_px: int,
        content_context: Optional[ContentContext] = None,
        slide_number: int = 1
    ) -> StructurePlan:
        """
        Analyze content and determine optimal structure.

        Args:
            narrative: Main narrative or topic
            topics: List of key topics to cover
            available_width_px: Available width in pixels
            available_height_px: Available height in pixels
            content_context: Audience/Purpose/Time context
            slide_number: Slide number for context

        Returns:
            StructurePlan with layout type, sections, and emphasis
        """
        if content_context is None:
            content_context = get_default_content_context()

        # Calculate usable area (90% after margins)
        usable_width = int(available_width_px * 0.90)
        usable_height = int(available_height_px * 0.90)

        # Build prompt
        prompt = STRUCTURE_ANALYSIS_PROMPT.format(
            narrative=narrative,
            topics=", ".join(topics) if topics else "None specified",
            slide_number=slide_number,
            width=available_width_px,
            height=available_height_px,
            usable_width=usable_width,
            usable_height=usable_height,
            audience_type=content_context.audience.audience_type.value,
            max_bullets=content_context.get_max_bullets(),
            purpose_type=content_context.purpose.purpose_type.value,
            structure_pattern=content_context.purpose.structure_pattern,
            content_depth=content_context.time.content_depth,
            emotional_tone=content_context.purpose.emotional_tone
        )

        try:
            # Call LLM for structure analysis (callable function)
            response = await self.llm_service(prompt)

            # Parse JSON response
            structure_data = self._parse_response(response)

            # Build StructurePlan
            return self._build_structure_plan(structure_data, content_context)

        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
            # Return fallback structure
            return self._get_fallback_structure(topics, content_context)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structure data."""
        try:
            # Handle response that might have markdown code blocks
            text = response.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            if text.endswith("```"):
                text = text[:-3]

            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse structure response: {e}")
            return {}

    def _build_structure_plan(
        self,
        data: Dict[str, Any],
        content_context: ContentContext
    ) -> StructurePlan:
        """Build StructurePlan from parsed data."""
        # Get layout type
        layout_type_str = data.get("layout_type", "single_column")
        try:
            layout_type = LayoutStructure(layout_type_str)
        except ValueError:
            layout_type = LayoutStructure.SINGLE_COLUMN

        # Build sections
        sections = []
        for section_data in data.get("sections", []):
            sections.append(SectionPlan(
                title=section_data.get("title"),
                content_type=section_data.get("content_type", "bullets"),
                estimated_items=min(
                    section_data.get("estimated_items", 3),
                    content_context.get_max_bullets()
                ),
                emphasis=section_data.get("emphasis", False)
            ))

        return StructurePlan(
            layout_type=layout_type,
            columns=data.get("columns", 1),
            has_heading=data.get("has_heading", True),
            heading_text=data.get("heading_text"),
            sections=sections,
            emphasis_points=data.get("emphasis_points", []),
            rationale=data.get("rationale")
        )

    def _get_fallback_structure(
        self,
        topics: List[str],
        content_context: ContentContext
    ) -> StructurePlan:
        """Get fallback structure when LLM fails."""
        topic_count = len(topics)
        max_bullets = content_context.get_max_bullets()

        # Decide layout based on topic count
        if topic_count <= 3:
            layout_type = LayoutStructure.SINGLE_COLUMN
            columns = 1
        elif topic_count <= 6:
            layout_type = LayoutStructure.TWO_COLUMN
            columns = 2
        else:
            layout_type = LayoutStructure.THREE_COLUMN
            columns = 3

        # Create sections from topics
        sections = []
        for i, topic in enumerate(topics[:6]):  # Max 6 sections
            sections.append(SectionPlan(
                title=topic,
                content_type="bullets",
                estimated_items=min(3, max_bullets),
                emphasis=(i == 0)  # Emphasize first section
            ))

        return StructurePlan(
            layout_type=layout_type,
            columns=columns,
            has_heading=True,
            heading_text=None,  # Will be generated in Phase 3
            sections=sections,
            emphasis_points=[0] if sections else [],
            rationale="Fallback structure based on topic count"
        )

    def estimate_structure_from_topics(
        self,
        topics: List[str],
        content_context: Optional[ContentContext] = None
    ) -> StructurePlan:
        """
        Quick synchronous estimate without LLM call.

        Useful for previews or when LLM is unavailable.
        """
        if content_context is None:
            content_context = get_default_content_context()

        return self._get_fallback_structure(topics, content_context)
