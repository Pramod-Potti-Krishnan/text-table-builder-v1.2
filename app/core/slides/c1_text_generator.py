"""
C1 Text Generator - Combined Content Generation

Generates title + subtitle + body in a SINGLE LLM call, saving 2 LLM calls per slide.
This is the key innovation in the v1.2.1 endpoint restructuring.

Supports all 34 content variants via variant_id parameter.

Version: 1.2.1
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Callable

from .base_slide_generator import BaseSlideGenerator
from ...models.slides_models import (
    UnifiedSlideRequest,
    ContentSlideResponse,
    SlideLayoutType,
    ContentStyle,
    ALL_C1_VARIANTS,
    C1_VARIANT_CATEGORIES
)

logger = logging.getLogger(__name__)


class C1TextGenerator(BaseSlideGenerator):
    """
    Combined content slide generator.

    Key Innovation:
    - Generates title + subtitle + body in ONE LLM call
    - Saves 2 LLM calls per slide (from 3 to 1)
    - For a 10-slide deck with 6 content slides: 12 fewer LLM calls

    Supports all 34 content variants:
    - matrix (2): matrix_2x2, matrix_2x3
    - grid (9): grid_2x3, grid_3x2, etc.
    - comparison (3): comparison_2col, 3col, 4col
    - sequential (3): sequential_3col, 4col, 5col
    - asymmetric (3): asymmetric_8_4_3section, etc.
    - hybrid (2): hybrid_top_2x2, hybrid_left_2x2
    - metrics (4): metrics_3col, 4col, 3x2_grid, 2x2_grid
    - impact_quote (1): impact_quote
    - table (4): table_2col, 3col, 4col, 5col
    - single_column (3): single_column_3section, 4section, 5section
    """

    # Variant configuration for body structure guidance
    VARIANT_CONFIGS = {
        # Matrix variants - grid of cells with titles
        "matrix_2x2": {
            "description": "2x2 matrix with 4 cells",
            "body_template": "4 cells with title + description each",
            "structure": "grid layout"
        },
        "matrix_2x3": {
            "description": "2x3 matrix with 6 cells",
            "body_template": "6 cells with title + description each",
            "structure": "grid layout"
        },
        # Grid variants - bullet cards
        "grid_2x3": {"description": "2 rows x 3 columns", "body_template": "6 bullet cards"},
        "grid_3x2": {"description": "3 rows x 2 columns", "body_template": "6 bullet cards"},
        "grid_2x2_centered": {"description": "2x2 centered grid", "body_template": "4 bullet cards"},
        "grid_2x3_left": {"description": "2x3 left-aligned", "body_template": "6 bullet cards"},
        "grid_3x2_left": {"description": "3x2 left-aligned", "body_template": "6 bullet cards"},
        "grid_2x2_left": {"description": "2x2 left-aligned", "body_template": "4 bullet cards"},
        "grid_2x3_numbered": {"description": "2x3 numbered cards", "body_template": "6 numbered cards"},
        "grid_3x2_numbered": {"description": "3x2 numbered cards", "body_template": "6 numbered cards"},
        "grid_2x2_numbered": {"description": "2x2 numbered cards", "body_template": "4 numbered cards"},
        # Comparison variants
        "comparison_2col": {"description": "2-column comparison", "body_template": "2 columns with bullets"},
        "comparison_3col": {"description": "3-column comparison", "body_template": "3 columns with bullets"},
        "comparison_4col": {"description": "4-column comparison", "body_template": "4 columns with bullets"},
        # Sequential variants
        "sequential_3col": {"description": "3-step sequence", "body_template": "3 sequential steps"},
        "sequential_4col": {"description": "4-step sequence", "body_template": "4 sequential steps"},
        "sequential_5col": {"description": "5-step sequence", "body_template": "5 sequential steps"},
        # Asymmetric variants
        "asymmetric_8_4_3section": {"description": "8-4 split, 3 sections", "body_template": "asymmetric 3 sections"},
        "asymmetric_8_4_4section": {"description": "8-4 split, 4 sections", "body_template": "asymmetric 4 sections"},
        "asymmetric_8_4_5section": {"description": "8-4 split, 5 sections", "body_template": "asymmetric 5 sections"},
        # Hybrid variants
        "hybrid_top_2x2": {"description": "Top content + 2x2 grid", "body_template": "top section + 4 cards"},
        "hybrid_left_2x2": {"description": "Left content + 2x2 grid", "body_template": "left section + 4 cards"},
        # Metrics variants
        "metrics_3col": {"description": "3 large metrics", "body_template": "3 metrics with values"},
        "metrics_4col": {"description": "4 large metrics", "body_template": "4 metrics with values"},
        "metrics_3x2_grid": {"description": "3x2 metrics grid", "body_template": "6 metrics with values"},
        "metrics_2x2_grid": {"description": "2x2 metrics grid", "body_template": "4 metrics with values"},
        # Impact quote
        "impact_quote": {"description": "Large quote display", "body_template": "quote with attribution"},
        # Table variants
        "table_2col": {"description": "2-column table", "body_template": "table with 2 columns"},
        "table_3col": {"description": "3-column table", "body_template": "table with 3 columns"},
        "table_4col": {"description": "4-column table", "body_template": "table with 4 columns"},
        "table_5col": {"description": "5-column table", "body_template": "table with 5 columns"},
        # Single column variants
        "single_column_3section": {"description": "3 vertical sections", "body_template": "3 stacked sections"},
        "single_column_4section": {"description": "4 vertical sections", "body_template": "4 stacked sections"},
        "single_column_5section": {"description": "5 vertical sections", "body_template": "5 stacked sections"},
        # Default bullet list
        "bullets": {"description": "Simple bullet list", "body_template": "bullet point list"},
    }

    @property
    def layout_type(self) -> SlideLayoutType:
        return SlideLayoutType.C1_TEXT

    @property
    def response_model(self):
        return ContentSlideResponse

    def _get_variant_config(self, variant_id: str) -> Dict[str, Any]:
        """
        Get configuration for a variant.

        Args:
            variant_id: Variant identifier

        Returns:
            Variant configuration dictionary
        """
        config = self.VARIANT_CONFIGS.get(variant_id, self.VARIANT_CONFIGS["bullets"])
        config["variant_id"] = variant_id
        return config

    def _build_combined_prompt(
        self,
        request: UnifiedSlideRequest,
        variant_config: Dict[str, Any]
    ) -> str:
        """
        Build prompt for combined title + subtitle + body generation.

        Args:
            request: Unified slide request
            variant_config: Configuration for the target variant

        Returns:
            LLM prompt string
        """
        variant_id = variant_config.get("variant_id", "bullets")
        body_template = variant_config.get("body_template", "bullet point list")
        description = variant_config.get("description", "content slide")

        # Build content style guidance
        style_guidance = {
            ContentStyle.BULLETS: "Use bullet points (<ul><li>) for the body",
            ContentStyle.PARAGRAPHS: "Use paragraphs (<p>) for the body",
            ContentStyle.MIXED: "Mix paragraphs and bullets as appropriate",
        }
        content_style = style_guidance.get(request.content_style, style_guidance[ContentStyle.BULLETS])

        # Build context string
        context_str = ""
        if request.context:
            context_items = [f"- {k}: {v}" for k, v in request.context.items()]
            context_str = f"\n\nContext:\n" + "\n".join(context_items)

        # Build topics string
        topics_str = ""
        if request.topics:
            topics_str = f"\nKey topics to cover: {', '.join(request.topics)}"

        prompt = f"""Generate COMPLETE content slide as JSON. Return ONLY valid JSON, no markdown.

Required JSON structure:
{{
  "slide_title": "Compelling title (40-60 characters)",
  "subtitle": "Supporting context (60-100 characters)",
  "body": "<HTML content for {body_template}>"
}}

CONSTRAINTS:
- slide_title: 40-60 characters, impactful and clear
- subtitle: 60-100 characters, provides context
- body: Valid HTML using {content_style}

Narrative: {request.narrative}
Variant: {variant_id} ({description})
Body structure: {body_template}
{topics_str}{context_str}

{f"Override title: {request.slide_title}" if request.slide_title else ""}

Return ONLY the JSON object. Do NOT include ```json markers."""

        return prompt

    def _parse_json_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM.

        Handles common formatting issues like markdown wrappers.

        Args:
            raw_response: Raw LLM response

        Returns:
            Parsed dictionary with slide_title, subtitle, body
        """
        # Clean markdown wrappers
        content = self._clean_markdown_wrapper(raw_response)

        # Try to find JSON object in response
        try:
            # Direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{[^{}]*"slide_title"[^{}]*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback: try to extract fields manually
        logger.warning("Failed to parse JSON, attempting field extraction")

        fields = {"slide_title": "", "subtitle": None, "body": ""}

        # Extract title
        title_match = re.search(r'"slide_title"\s*:\s*"([^"]*)"', content)
        if title_match:
            fields["slide_title"] = title_match.group(1)

        # Extract subtitle
        subtitle_match = re.search(r'"subtitle"\s*:\s*"([^"]*)"', content)
        if subtitle_match:
            fields["subtitle"] = subtitle_match.group(1)

        # Extract body
        body_match = re.search(r'"body"\s*:\s*"(.*?)"(?=\s*[,}])', content, re.DOTALL)
        if body_match:
            fields["body"] = body_match.group(1).replace('\\"', '"').replace('\\n', '\n')

        return fields

    async def generate(
        self,
        request: UnifiedSlideRequest
    ) -> ContentSlideResponse:
        """
        Generate content slide with combined title + subtitle + body.

        Uses single LLM call for all three components (saves 2 calls).

        Args:
            request: UnifiedSlideRequest with narrative, topics, variant_id

        Returns:
            ContentSlideResponse with structured fields
        """
        start_time = time.time()
        variant_id = request.variant_id or "bullets"

        logger.info(f"[C1-text] Generating combined content for variant={variant_id}")

        try:
            # Get variant configuration
            variant_config = self._get_variant_config(variant_id)

            # Build combined prompt
            prompt = self._build_combined_prompt(request, variant_config)

            # Single LLM call for title + subtitle + body
            raw_response = await self._call_llm_with_logging(prompt, f"combined variant={variant_id}")

            # Parse JSON response
            parsed = self._parse_json_response(raw_response)

            # Extract fields
            slide_title = parsed.get("slide_title", "")
            subtitle = parsed.get("subtitle")
            body = parsed.get("body", "")

            # Use override title if provided
            if request.slide_title:
                slide_title = request.slide_title

            # Validate body content
            if body:
                validation = self._validate_html_security(body)
                if not validation["valid"]:
                    logger.warning(f"[C1-text] Body validation warnings: {validation['violations']}")
                    # Don't fail, just log

            # Build metadata
            metadata = self._build_metadata(
                request=request,
                start_time=start_time,
                extra={
                    "llm_calls": 1,
                    "generation_mode": "combined",
                    "variant_id": variant_id,
                    "variant_description": variant_config.get("description"),
                    "content_style": request.content_style.value,
                    "title_length": len(slide_title),
                    "subtitle_length": len(subtitle) if subtitle else 0,
                    "body_length": len(body),
                }
            )

            # Build response
            # Per SLIDE_GENERATION_INPUT_SPEC.md: C1-text uses background_color #ffffff
            response = ContentSlideResponse(
                slide_title=slide_title,
                subtitle=subtitle,
                body=body,
                rich_content=body,  # L25 alias
                background_color="#ffffff",  # Default per SPEC
                metadata=metadata
            )

            logger.info(
                f"[C1-text] Generated variant={variant_id} in {metadata['generation_time_ms']}ms "
                f"(title={len(slide_title)}, body={len(body)} chars)"
            )

            return response

        except Exception as e:
            elapsed = int((time.time() - start_time) * 1000)
            logger.error(f"[C1-text] Generation failed after {elapsed}ms: {e}")
            raise

    @classmethod
    def get_supported_variants(cls) -> Dict[str, Any]:
        """
        Get all supported variant configurations.

        Returns:
            Dictionary of variant_id -> config
        """
        return cls.VARIANT_CONFIGS

    @classmethod
    def get_variant_categories(cls) -> Dict[str, list]:
        """
        Get variants organized by category.

        Returns:
            Dictionary of category -> list of variant_ids
        """
        return C1_VARIANT_CATEGORIES
