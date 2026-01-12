"""
Atomic Component Generator for Direct Component Generation
============================================================

Direct atomic component generation without Chain of Thought reasoning.
Unlike ComponentAssemblyAgent, this class:
- Takes explicit component type and count
- Does NOT reason about which component to use
- Supports flexible bullet/item counts
- Provides faster, more deterministic output

Supports 5 atomic component types:
- METRICS (metrics_card): 1-4 metric cards
- SEQUENTIAL (numbered_card): 1-6 numbered steps
- COMPARISON (comparison_column): 1-4 columns with 1-7 items each
- SECTIONS (colored_section): 1-5 sections with 1-5 bullets each
- CALLOUT (sidebar_box): 1-2 callout boxes with 1-7 items each

v1.1.0: Added count=1 support for all types + placeholder_mode
v1.0.0: Initial atomic component endpoints
"""

import json
import logging
import time
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from copy import deepcopy

from .registry import get_registry
from .constraints import (
    SpaceCalculator,
    CharacterLimitScaler,
    LayoutBuilder,
    CELL_SIZE_PX
)
from .style_config import (
    HEADING_FONT_SIZE,
    BODY_FONT_SIZE,
    BODY_LINE_HEIGHT,
    TEXT_SECONDARY,
    BOX_OPACITY_DEFAULT,
    BOX_OPACITY_SOLID,
    get_default_transparency
)
from ...models.component_models import (
    ComponentDefinition,
    SlotSpec,
    CharLimits,
    GeneratedContent,
    LayoutSelection,
    AssemblyResult
)
from ...models.atomic_models import (
    AtomicContext,
    AtomicMetadata,
    AtomicComponentResponse,
    LayoutType,
    ATOMIC_TYPE_MAP
)

logger = logging.getLogger(__name__)


# =============================================================================
# Lorem Ipsum Generator
# =============================================================================

# Standard Lorem Ipsum text pool for generating placeholder content
LOREM_IPSUM_TEXT = """Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium totam rem aperiam eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est qui dolorem ipsum quia dolor sit amet consectetur adipisci velit sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem."""

def generate_lorem_ipsum(min_chars: int, max_chars: int, start_offset: int = 0) -> str:
    """
    Generate Lorem Ipsum text within specified character bounds.

    Args:
        min_chars: Minimum characters (will continue adding words to reach this)
        max_chars: Maximum characters (hard ceiling)
        start_offset: Offset into the Lorem text to start from (for variety)

    Returns:
        Text between min_chars and max_chars, respecting word boundaries
    """
    if max_chars <= 0:
        return ""

    # Use the offset to get variety in the output
    words = LOREM_IPSUM_TEXT.split()
    num_words = len(words)

    # Start from offset position (wrap around if needed)
    offset_words = start_offset % num_words
    rotated_words = words[offset_words:] + words[:offset_words]

    # Build text, ensuring we reach min_chars while staying under max_chars
    result = ""
    word_idx = 0
    words_used = 0

    while word_idx < len(rotated_words) * 2:  # Allow wrap-around once
        word = rotated_words[word_idx % len(rotated_words)]
        next_len = len(result) + len(word) + (1 if result else 0)

        if next_len <= max_chars:
            result = f"{result} {word}" if result else word
            word_idx += 1
            words_used += 1

            # If we've reached min_chars, check if we can stop
            if len(result) >= min_chars:
                # Check if adding next word would exceed max
                if word_idx < len(rotated_words) * 2:
                    next_word = rotated_words[word_idx % len(rotated_words)]
                    if len(result) + len(next_word) + 1 > max_chars:
                        break
        else:
            # Next word would exceed max_chars
            if len(result) >= min_chars:
                break  # We have enough
            else:
                # Haven't reached min yet, skip this word and try next
                word_idx += 1
                if words_used > num_words:  # Safety: don't loop forever
                    break

    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()

    # End with period if we have room
    if result and not result.endswith("."):
        if len(result) < max_chars:
            result = result.rstrip(",;:") + "."

    return result


def generate_lorem_title(min_chars: int, max_chars: int, index: int = 0) -> str:
    """
    Generate Lorem Ipsum text for headings within character bounds.

    Args:
        min_chars: Minimum characters for the title
        max_chars: Maximum characters for the title
        index: Index for variety (starts from different positions in Lorem text)

    Returns:
        Lorem Ipsum text between min_chars and max_chars at word boundaries
    """
    words = LOREM_IPSUM_TEXT.split()
    num_words = len(words)

    # Start from different positions for variety
    start = (index * 3) % num_words
    rotated_words = words[start:] + words[:start]

    # Build title from Lorem words, ensuring we reach min_chars
    result = ""
    word_idx = 0
    words_used = 0

    while word_idx < len(rotated_words) * 2:  # Allow wrap-around once
        word = rotated_words[word_idx % len(rotated_words)]
        test = result + (" " if result else "") + word

        if len(test) <= max_chars:
            result = test
            word_idx += 1
            words_used += 1

            # If we've reached min_chars, check if we can stop
            if len(result) >= min_chars:
                # Check if adding next word would exceed max
                if word_idx < len(rotated_words) * 2:
                    next_word = rotated_words[word_idx % len(rotated_words)]
                    if len(result) + len(next_word) + 1 > max_chars:
                        break
        else:
            # Next word would exceed max_chars
            if len(result) >= min_chars:
                break  # We have enough
            else:
                # Haven't reached min yet, skip and try next
                word_idx += 1
                if words_used > num_words:  # Safety
                    break

    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()

    return result


# =============================================================================
# Result Dataclass
# =============================================================================

@dataclass
class AtomicResult:
    """Result from AtomicComponentGenerator.generate()"""
    success: bool
    html: str
    component_type: str
    instance_count: int
    arrangement: str
    variants_used: List[str]
    character_counts: Dict[str, List[int]]
    metadata: AtomicMetadata
    error: Optional[str] = None


# =============================================================================
# Atomic Component Generator
# =============================================================================

class AtomicComponentGenerator:
    """
    Direct atomic component generation without CoT reasoning.

    Provides explicit control over component type, count, and item structure.
    Faster than ComponentAssemblyAgent as it skips reasoning about component selection.
    """

    def __init__(self, llm_service: Optional[Callable] = None):
        """
        Initialize the generator.

        Args:
            llm_service: Async callable that takes prompt string and returns response
        """
        self.llm_service = llm_service
        self.registry = get_registry()
        self.layout_builder = LayoutBuilder()
        self.space_calculator = SpaceCalculator()
        self.scaler = CharacterLimitScaler()

    async def generate(
        self,
        component_type: str,
        prompt: str,
        count: int,
        grid_width: int,
        grid_height: int,
        items_per_instance: Optional[int] = None,
        context: Optional[AtomicContext] = None,
        variant: Optional[str] = None,
        placeholder_mode: bool = False,
        transparency: Optional[float] = None,
        layout: LayoutType = LayoutType.HORIZONTAL,
        grid_cols: Optional[int] = None,
        theme_mode: str = "light",
        heading_align: str = "left",
        content_align: str = "left",
        title_min_chars: int = 30,
        title_max_chars: int = 40,
        item_min_chars: int = 80,
        item_max_chars: int = 100,
        list_style: str = "bullets",
        use_lorem_ipsum: bool = False,
        # New styling parameters
        background_style: str = "colored",
        color_scheme: str = "accent",  # Default to accent for title_style compatibility
        corners: str = "rounded",
        border: bool = False,
        title_style: str = "plain",
        show_title: bool = True,
        existing_colors: Optional[List[str]] = None
    ) -> AtomicResult:
        """
        Generate atomic component with explicit parameters.

        Args:
            component_type: Internal component ID (e.g., 'metrics_card', 'colored_section')
            prompt: Content request describing what to generate
            count: Number of component instances
            grid_width: Available width in grid units (4-32)
            grid_height: Available height in grid units (4-18)
            items_per_instance: Number of bullets/items per instance (for flexible components)
            context: Optional slide/presentation context
            variant: Optional specific color variant to use
            placeholder_mode: If True, generate placeholder content without LLM call
            transparency: Box opacity (0.0-1.0). If None, uses default:
                          - metrics_card: 1.0 (solid - gradient backgrounds)
                          - all others: 0.6 (60% transparent)
            layout: Layout arrangement (horizontal, vertical, or grid)
            grid_cols: Number of columns for grid layout (auto-calculated if None)
            list_style: List style - 'bullets' (disc), 'numbers' (ordered), or 'none' (plain text)
            use_lorem_ipsum: If True with placeholder_mode, use Lorem Ipsum text instead of generic placeholders

        Returns:
            AtomicResult with HTML, metadata, and character counts
        """
        start_time = time.time()

        try:
            # Step 1: Load base component definition
            component = self.registry.get_component(component_type)
            if not component:
                return self._error_result(
                    f"Component not found: {component_type}",
                    component_type,
                    count,
                    start_time
                )

            logger.info(
                f"[ATOMIC-{component_type.upper()}] count={count}, "
                f"items_per={items_per_instance}, grid={grid_width}x{grid_height}"
            )

            # Step 2: Create dynamic slots if items_per_instance specified
            dynamic_slots = self._create_dynamic_slots(
                component, items_per_instance
            ) if items_per_instance else component.slots

            # Step 3: Build layout (arrangement, character limits, variants)
            layout = self._build_layout(
                component, count, grid_width, grid_height, dynamic_slots, variant,
                layout_type=layout, grid_cols=grid_cols
            )

            # Step 3b: Apply color scheme filtering and collision avoidance (TEXT_BOX only)
            if component.component_id == "text_box":
                layout = self._apply_color_scheme_filter(
                    component, layout, color_scheme, existing_colors
                )

            # Step 4: Generate content (placeholder or LLM)
            if placeholder_mode:
                # Generate placeholder content without LLM call
                contents = self._generate_placeholder_content(
                    component_type=component_type,
                    slots=dynamic_slots,
                    instance_count=count,
                    use_lorem_ipsum=use_lorem_ipsum,
                    title_min_chars=title_min_chars,
                    title_max_chars=title_max_chars,
                    item_min_chars=item_min_chars,
                    item_max_chars=item_max_chars
                )
                mode_str = "Lorem Ipsum" if use_lorem_ipsum else "Placeholder"
                logger.info(f"[ATOMIC-{component_type.upper()}] {mode_str} mode - no LLM call")
            else:
                # Generate content via LLM
                contents = await self._generate_content(
                    component_type=component_type,
                    component_description=component.description,
                    slots=dynamic_slots,
                    char_limits=layout.scaled_char_limits,
                    prompt=prompt,
                    instance_count=count,
                    items_per_instance=items_per_instance,
                    context=context,
                    title_max_chars=title_max_chars,
                    item_max_chars=item_max_chars
                )

            if not contents:
                return self._error_result(
                    "Failed to generate content",
                    component_type,
                    count,
                    start_time
                )

            # Step 5: Determine transparency (default varies by component type)
            actual_transparency = transparency
            if actual_transparency is None:
                actual_transparency = get_default_transparency(component_type)

            # Step 6: Assemble HTML with dynamic template and transparency
            html, char_counts = self._assemble_html(
                component=component,
                layout=layout,
                contents=contents,
                items_per_instance=items_per_instance,
                transparency=actual_transparency,
                theme_mode=theme_mode,
                heading_align=heading_align,
                content_align=content_align,
                list_style=list_style,
                # New styling parameters
                background_style=background_style,
                color_scheme=color_scheme,
                corners=corners,
                border=border,
                title_style=title_style,
                show_title=show_title,
                existing_colors=existing_colors
            )

            # Calculate metadata
            elapsed_ms = int((time.time() - start_time) * 1000)
            space_analysis = self.space_calculator.analyze_space(grid_width, grid_height)

            # Calculate scaling factor
            instance_width = int(layout.position_css.get("width", "0px").replace("px", ""))
            instance_height = int(layout.position_css.get("height", "0px").replace("px", ""))
            ideal_width = (component.space_requirements.ideal_grid_width or
                          component.space_requirements.min_grid_width) * CELL_SIZE_PX
            ideal_height = (component.space_requirements.ideal_grid_height or
                           component.space_requirements.min_grid_height) * CELL_SIZE_PX
            scaling_factor = self.scaler.calculate_scaling_factor(
                instance_width, instance_height, ideal_width, ideal_height
            )

            metadata = AtomicMetadata(
                generation_time_ms=elapsed_ms,
                model_used="placeholder" if placeholder_mode else "gemini-1.5-flash",
                grid_dimensions={"width": grid_width, "height": grid_height},
                space_category=space_analysis.space_category,
                scaling_factor=round(scaling_factor, 2)
            )

            logger.info(
                f"[ATOMIC-{component_type.upper()}-OK] count={count}, "
                f"time={elapsed_ms}ms, html={len(html)} chars"
            )

            return AtomicResult(
                success=True,
                html=html,
                component_type=component_type,
                instance_count=count,
                arrangement=layout.arrangement.value if hasattr(layout.arrangement, 'value') else str(layout.arrangement),
                variants_used=layout.variant_assignments[:count],
                character_counts=char_counts,
                metadata=metadata
            )

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"[ATOMIC-{component_type.upper()}-ERROR] {e}\n{tb}")
            return self._error_result(str(e), component_type, count, start_time)

    def _create_dynamic_slots(
        self,
        component: ComponentDefinition,
        items_per_instance: int
    ) -> Dict[str, SlotSpec]:
        """
        Create dynamic slots based on requested item count.

        For components with flexible bullet/item counts (colored_section,
        comparison_column, sidebar_box), generate the correct number of slots.
        """
        # Identify the slot pattern (bullet_N or item_N)
        slot_prefix = None
        template_slot = None

        for slot_id in component.slots:
            if slot_id.startswith("bullet_"):
                slot_prefix = "bullet_"
                template_slot = component.slots.get("bullet_1")
                break
            elif slot_id.startswith("item_"):
                slot_prefix = "item_"
                template_slot = component.slots.get("item_1")
                break

        if not slot_prefix or not template_slot:
            # No flexible slots, return original
            return component.slots

        # Build dynamic slots
        dynamic_slots = {}

        # Copy non-item slots (like section_heading, column_heading, sidebar_heading)
        for slot_id, spec in component.slots.items():
            if not slot_id.startswith(slot_prefix):
                dynamic_slots[slot_id] = spec

        # Generate requested number of item slots
        for i in range(1, items_per_instance + 1):
            slot_key = f"{slot_prefix}{i}"
            if slot_key in component.slots:
                # Use existing slot spec
                dynamic_slots[slot_key] = component.slots[slot_key]
            else:
                # Clone from template
                dynamic_slots[slot_key] = SlotSpec(
                    min_chars=template_slot.min_chars,
                    max_chars=template_slot.max_chars,
                    baseline_chars=template_slot.baseline_chars,
                    description=f"{slot_prefix.replace('_', ' ').title()}{i}",
                    format_hint=template_slot.format_hint
                )

        return dynamic_slots

    def _generate_placeholder_content(
        self,
        component_type: str,
        slots: Dict[str, SlotSpec],
        instance_count: int,
        use_lorem_ipsum: bool = False,
        title_min_chars: int = 30,
        title_max_chars: int = 40,
        item_min_chars: int = 80,
        item_max_chars: int = 100
    ) -> List[GeneratedContent]:
        """
        Generate placeholder content without LLM call.

        Returns static placeholder content that can be replaced later
        when user triggers content generation with full context.

        Args:
            component_type: Type of component to generate content for
            slots: Dictionary of slot specifications
            instance_count: Number of instances to generate
            use_lorem_ipsum: If True, generate Lorem Ipsum text with proper character limits
            title_min_chars: Minimum characters for title/heading slots
            title_max_chars: Maximum characters for title/heading slots
            item_min_chars: Minimum characters for item/bullet slots
            item_max_chars: Maximum characters for item/bullet slots
        """
        PLACEHOLDER_TEMPLATES = {
            "metrics_card": {
                "metric_number": ["$X.XM", "$XX%", "XX.X", "$XXK"],
                "metric_label": ["METRIC LABEL", "KEY METRIC", "PERFORMANCE", "GROWTH"],
                "metric_description": ["Description of this metric and its significance to the presentation"]
            },
            "numbered_card": {
                "card_number": ["1", "2", "3", "4", "5", "6"],
                "card_title": ["Step Title", "Phase Name", "Stage Title", "Action Item"],
                "card_description": ["Description of this step in the process and what it accomplishes"]
            },
            "colored_section": {
                "section_heading": ["Section Heading"],
                "bullet_1": ["First key point for this section"],
                "bullet_2": ["Second key point for this section"],
                "bullet_3": ["Third key point for this section"],
                "bullet_4": ["Fourth key point for this section"],
                "bullet_5": ["Fifth key point for this section"]
            },
            "comparison_column": {
                "column_heading": ["Column Title"],
                "item_1": ["First comparison point for this column"],
                "item_2": ["Second comparison point for this column"],
                "item_3": ["Third comparison point for this column"],
                "item_4": ["Fourth comparison point for this column"],
                "item_5": ["Fifth comparison point for this column"],
                "item_6": ["Sixth comparison point for this column"],
                "item_7": ["Seventh comparison point for this column"]
            },
            "sidebar_box": {
                "sidebar_heading": ["Callout Title"],
                "item_1": ["Key highlight or important note"],
                "item_2": ["Additional detail or context"],
                "item_3": ["Third key point"],
                "item_4": ["Fourth key point"],
                "item_5": ["Fifth key point"],
                "item_6": ["Sixth key point"],
                "item_7": ["Seventh key point"]
            },
            "text_bullets": {
                "subtitle": ["Section Subtitle"],
                "bullet_1": ["First bullet point for this section"],
                "bullet_2": ["Second bullet point for this section"],
                "bullet_3": ["Third bullet point for this section"],
                "bullet_4": ["Fourth bullet point for this section"],
                "bullet_5": ["Fifth bullet point for this section"],
                "bullet_6": ["Sixth bullet point for this section"],
                "bullet_7": ["Seventh bullet point for this section"]
            },
            "bullet_box": {
                "box_heading": ["Box Heading"],
                "item_1": ["First item in this box"],
                "item_2": ["Second item in this box"],
                "item_3": ["Third item in this box"],
                "item_4": ["Fourth item in this box"],
                "item_5": ["Fifth item in this box"],
                "item_6": ["Sixth item in this box"],
                "item_7": ["Seventh item in this box"]
            },
            "table_basic": {
                "header_1": ["Column 1"],
                "header_2": ["Column 2"],
                "header_3": ["Column 3"],
                "row1_col1": ["Row 1 Data"],
                "row1_col2": ["Row 1 Data"],
                "row1_col3": ["Row 1 Data"],
                "row2_col1": ["Row 2 Data"],
                "row2_col2": ["Row 2 Data"],
                "row2_col3": ["Row 2 Data"],
                "row3_col1": ["Row 3 Data"],
                "row3_col2": ["Row 3 Data"],
                "row3_col3": ["Row 3 Data"],
                "row4_col1": ["Row 4 Data"],
                "row4_col2": ["Row 4 Data"],
                "row4_col3": ["Row 4 Data"]
            },
            "numbered_list": {
                "list_title": ["List Title"],
                "item_1": ["First numbered item in the list"],
                "item_2": ["Second numbered item in the list"],
                "item_3": ["Third numbered item in the list"],
                "item_4": ["Fourth numbered item in the list"],
                "item_5": ["Fifth numbered item in the list"],
                "item_6": ["Sixth numbered item in the list"],
                "item_7": ["Seventh numbered item in the list"],
                "item_8": ["Eighth numbered item in the list"],
                "item_9": ["Ninth numbered item in the list"],
                "item_10": ["Tenth numbered item in the list"]
            },
            "text_box": {
                "box_heading": ["Section Heading"],
                "item_1": ["First key point for this section"],
                "item_2": ["Second key point for this section"],
                "item_3": ["Third key point for this section"],
                "item_4": ["Fourth key point for this section"],
                "item_5": ["Fifth key point for this section"],
                "item_6": ["Sixth key point for this section"],
                "item_7": ["Seventh key point for this section"]
            }
        }

        templates = PLACEHOLDER_TEMPLATES.get(component_type, {})
        contents = []

        for i in range(instance_count):
            slot_values = {}
            for slot_idx, slot_id in enumerate(slots):
                if use_lorem_ipsum:
                    # Generate Lorem Ipsum content respecting character limits
                    # Determine if this is a title/heading slot or an item/bullet slot
                    is_heading = any(x in slot_id.lower() for x in ['heading', 'title', 'subtitle', 'label'])

                    if is_heading:
                        # Use Lorem title with min/max char limits
                        slot_values[slot_id] = generate_lorem_title(
                            min_chars=title_min_chars,
                            max_chars=title_max_chars,
                            index=i * 10 + slot_idx
                        )
                    else:
                        # Use Lorem Ipsum text with min/max char limits
                        # Use different offsets to get variety across instances and slots
                        offset = (i * 20 + slot_idx * 7) % 100
                        slot_values[slot_id] = generate_lorem_ipsum(
                            min_chars=item_min_chars,
                            max_chars=item_max_chars,
                            start_offset=offset
                        )
                elif slot_id in templates:
                    values = templates[slot_id]
                    slot_values[slot_id] = values[i % len(values)]
                else:
                    # Generic placeholder for dynamic slots
                    slot_values[slot_id] = f"[{slot_id.replace('_', ' ').title()}]"

            contents.append(GeneratedContent(
                instance_index=i,
                slot_values=slot_values,
                character_counts={k: len(v) for k, v in slot_values.items()}
            ))

        return contents

    def _build_layout(
        self,
        component: ComponentDefinition,
        instance_count: int,
        grid_width: int,
        grid_height: int,
        dynamic_slots: Dict[str, SlotSpec],
        variant: Optional[str] = None,
        layout_type: LayoutType = LayoutType.HORIZONTAL,
        grid_cols: Optional[int] = None
    ) -> LayoutSelection:
        """
        Build layout configuration with dynamic slots and layout type.

        Args:
            layout_type: Layout arrangement (horizontal, vertical, or grid)
            grid_cols: Number of columns for grid layout (auto-calculated if None)
        """
        import math

        # Create a modified component with dynamic slots for layout building
        modified_component = deepcopy(component)
        modified_component.slots = dynamic_slots

        # Use LayoutBuilder for core layout logic
        layout = self.layout_builder.build_layout(
            modified_component,
            instance_count,
            grid_width,
            grid_height
        )

        # Override arrangement based on layout_type
        if layout_type == LayoutType.VERTICAL:
            # Stacked in a column
            layout.arrangement = f"stacked_{instance_count}"
        elif layout_type == LayoutType.GRID:
            # Grid layout with specified or auto-calculated columns
            cols = grid_cols if grid_cols else min(instance_count, 3)
            rows = math.ceil(instance_count / cols)
            layout.arrangement = f"grid_{rows}x{cols}"
        else:
            # HORIZONTAL - side by side in a row (default behavior)
            layout.arrangement = f"row_{instance_count}"

        # Override variant if specified
        if variant and variant in component.variants:
            layout.variant_assignments = [variant] * instance_count

        return layout

    def _apply_color_scheme_filter(
        self,
        component: ComponentDefinition,
        layout: LayoutSelection,
        color_scheme: str = "accent",  # Default to accent for title_style compatibility
        existing_colors: Optional[List[str]] = None
    ) -> LayoutSelection:
        """
        Apply color scheme filtering and collision avoidance to variant assignments.

        Args:
            component: Component definition with variants
            layout: Layout selection to modify
            color_scheme: 'gradient', 'solid', or 'accent'
            existing_colors: List of color names to avoid (e.g., ['purple', 'blue'])

        Returns:
            Modified layout with filtered variant assignments
        """
        # Only apply to text_box component
        if component.component_id != "text_box":
            return layout

        all_variants = list(component.variants.keys())
        instance_count = layout.instance_count

        # Filter variants by color_scheme
        if color_scheme == "gradient":
            filtered = [v for v in all_variants if v.startswith("gradient_")]
        elif color_scheme == "accent":
            filtered = [v for v in all_variants if v.startswith("accent_")]
        else:  # solid - use accent variants (solid colors, no gradient)
            filtered = [v for v in all_variants if v.startswith("accent_")]

        # If no variants match the filter, fall back to all variants
        if not filtered:
            filtered = all_variants

        # Remove variants matching existing_colors (collision avoidance)
        if existing_colors:
            available = []
            for v in filtered:
                # Extract color name from variant ID (e.g., "accent_1_purple" -> "purple")
                parts = v.split("_")
                color_name = parts[-1] if len(parts) > 1 else v
                if color_name.lower() not in [c.lower() for c in existing_colors]:
                    available.append(v)
            # Only use filtered if we still have options
            if available:
                filtered = available

        # Select variants for requested count (cycle if needed)
        selected = []
        for i in range(instance_count):
            selected.append(filtered[i % len(filtered)])

        layout.variant_assignments = selected
        logger.info(
            f"[ATOMIC-TEXT_BOX] Color scheme filter: scheme={color_scheme}, "
            f"existing={existing_colors}, selected={selected[:3]}..."
        )

        return layout

    async def _generate_content(
        self,
        component_type: str,
        component_description: str,
        slots: Dict[str, SlotSpec],
        char_limits: Dict[str, CharLimits],
        prompt: str,
        instance_count: int,
        items_per_instance: Optional[int],
        context: Optional[AtomicContext],
        title_max_chars: int = 40,
        item_max_chars: int = 100
    ) -> List[GeneratedContent]:
        """
        Generate content for all component instances via LLM.

        Args:
            title_max_chars: Maximum characters for title/heading (used for text_box)
            item_max_chars: Maximum characters per bullet/item (used for text_box)
        """
        if not self.llm_service:
            raise ValueError("LLM service required for content generation")

        # Build slot descriptions
        slot_specs = []
        for slot_id in sorted(slots.keys()):
            limits = char_limits.get(slot_id)
            spec = slots.get(slot_id)
            if limits and spec:
                slot_specs.append(
                    f"  - {slot_id}: {spec.description} "
                    f"({limits.min_chars}-{limits.max_chars} chars"
                    f"{', format: ' + spec.format_hint if spec.format_hint else ''})"
                )

        slots_text = "\n".join(slot_specs)

        # Build context section
        context_text = ""
        if context:
            if context.audience:
                context_text += f"Audience: {context.audience}\n"
            if context.tone:
                context_text += f"Tone: {context.tone}\n"
            if context.slide_purpose:
                context_text += f"Purpose: {context.slide_purpose}\n"
            if context.presentation_title:
                context_text += f"Presentation: {context.presentation_title}\n"
            if context.industry:
                context_text += f"Industry: {context.industry}\n"

        # Build text_box-specific character limit instructions
        text_box_char_limits = ""
        if component_type == "text_box":
            text_box_char_limits = f"""
TEXT BOX CHARACTER LIMITS:
- Heading (box_heading): Maximum {title_max_chars} characters
- Each bullet item: Maximum {item_max_chars} characters
"""

        # Build the prompt
        llm_prompt = f"""Generate content for {instance_count} {component_type} component(s).

USER REQUEST:
{prompt}

{f'CONTEXT:{chr(10)}{context_text}' if context_text else ''}

COMPONENT: {component_description}
{text_box_char_limits}
SLOTS TO FILL (for each of the {instance_count} instances):
{slots_text}

REQUIREMENTS:
1. Generate EXACTLY {instance_count} instances
2. Each instance must have ALL slots filled
3. Content must be DIFFERENT across instances (no repetition)
4. Stay within character limits strictly
5. Content should be coherent and professional

OUTPUT FORMAT:
Return a JSON object:
{{
  "instances": [
    {{
      "slot_id_1": "content for slot 1",
      "slot_id_2": "content for slot 2",
      ...
    }},
    ...repeat for {instance_count} instances...
  ]
}}

Generate the content now:"""

        # Call LLM
        logger.info(f"[ATOMIC-LLM] Calling LLM for {component_type} x{instance_count}")
        llm_response = await self.llm_service(llm_prompt)
        logger.info(f"[ATOMIC-LLM] Response received, {len(llm_response)} chars")

        # Parse response
        return self._parse_llm_response(llm_response, instance_count, slots)

    def _parse_llm_response(
        self,
        llm_response: str,
        instance_count: int,
        slots: Dict[str, SlotSpec]
    ) -> List[GeneratedContent]:
        """Parse LLM response into GeneratedContent list."""

        def clean_json(text: str) -> str:
            """Clean common LLM JSON errors like trailing commas."""
            # Remove trailing commas before } or ]
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            # Remove any control characters
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
            return text

        # Try to extract JSON
        try:
            data = json.loads(clean_json(llm_response))
        except json.JSONDecodeError:
            # Try to find JSON in markdown code block
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
            if json_match:
                data = json.loads(clean_json(json_match.group(1)))
            else:
                # Try to find raw JSON
                json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_match:
                    data = json.loads(clean_json(json_match.group(0)))
                else:
                    raise ValueError(f"Could not parse LLM response as JSON: {llm_response[:300]}")

        if not isinstance(data, dict) or "instances" not in data:
            raise ValueError(f"Invalid response structure: {type(data)}")

        instances = data.get("instances", [])

        # Build GeneratedContent list
        contents = []
        for i, instance_data in enumerate(instances[:instance_count]):
            char_counts = {
                slot_id: len(str(value))
                for slot_id, value in instance_data.items()
            }
            contents.append(GeneratedContent(
                instance_index=i,
                slot_values=instance_data,
                character_counts=char_counts
            ))

        return contents

    def _assemble_html(
        self,
        component: ComponentDefinition,
        layout: LayoutSelection,
        contents: List[GeneratedContent],
        items_per_instance: Optional[int],
        transparency: float = 1.0,
        theme_mode: str = "light",
        heading_align: str = "left",
        content_align: str = "left",
        list_style: str = "bullets",
        # New styling parameters
        background_style: str = "colored",
        color_scheme: str = "accent",  # Default to accent for title_style compatibility
        corners: str = "rounded",
        border: bool = False,
        title_style: str = "plain",
        show_title: bool = True,
        existing_colors: Optional[List[str]] = None
    ) -> tuple[str, Dict[str, List[int]]]:
        """
        Assemble final HTML with optional dynamic template generation.

        Args:
            component: Component definition
            layout: Layout selection with arrangements and variants
            contents: Generated content for each instance
            items_per_instance: Optional flexible item count
            transparency: Box opacity (0.0-1.0). Values < 1.0 add opacity CSS.

        Returns tuple of (html_string, character_counts_per_slot)
        """
        char_counts: Dict[str, List[int]] = {}
        instance_htmls = []

        # NOTE: Removed opacity wrapper that was applying to entire component.
        # CSS opacity affects ALL child elements including text.
        # Component templates now use rgba() backgrounds for transparency instead.

        for i, gen_content in enumerate(contents):
            # Get variant for this instance
            variant_id = layout.variant_assignments[i] if i < len(layout.variant_assignments) else list(component.variants.keys())[0]
            variant = component.variants.get(variant_id)

            # Generate dynamic template if needed
            if items_per_instance:
                template = self._generate_dynamic_template(
                    component, items_per_instance,
                    heading_align=heading_align,
                    content_align=content_align,
                    list_style=list_style,
                    # New styling parameters
                    corners=corners,
                    border=border,
                    title_style=title_style,
                    show_title=show_title
                )
            else:
                template = component.template

            html = template

            # Replace content placeholders
            for slot_id, value in gen_content.slot_values.items():
                html = html.replace(f"{{{slot_id}}}", str(value))

                # Track character counts
                if slot_id not in char_counts:
                    char_counts[slot_id] = []
                char_counts[slot_id].append(len(str(value)))

            # Auto-inject section number for colored_section (1-indexed)
            if component.component_id == "colored_section":
                html = html.replace("{section_number}", str(i + 1))

            # Replace variant placeholders
            if variant:
                if variant.gradient:
                    html = html.replace("{gradient}", variant.gradient)

                # Handle background_style: transparent overrides variant background
                if component.component_id == "text_box" and background_style == "transparent":
                    html = html.replace("{background}", "transparent")
                elif variant.background:
                    html = html.replace("{background}", variant.background)

                if variant.shadow:
                    html = html.replace("{shadow}", variant.shadow)
                if variant.accent_color:
                    html = html.replace("{accent_color}", variant.accent_color)

                # Handle title_badge_bg for colored-bg title style
                # First check model_extra for title_badge_bg, then fall back to text_color (if not white)
                if component.component_id == "text_box" and title_style == "colored-bg":
                    badge_bg = None
                    if hasattr(variant, 'model_extra') and variant.model_extra:
                        badge_bg = variant.model_extra.get("title_badge_bg")
                    if not badge_bg:
                        # Fall back to text_color if not white, otherwise use default purple
                        badge_bg = variant.text_color if variant.text_color and variant.text_color.lower() != "white" else "#805AA0"
                    html = html.replace("{title_badge_bg}", badge_bg)

                # Handle theme_mode for text_box accent variants (dark mode text colors)
                text_color_applied = False
                item_color_applied = False
                if component.component_id == "text_box" and theme_mode == "dark":
                    if hasattr(variant, 'model_extra') and variant.model_extra:
                        if "text_color_dark" in variant.model_extra:
                            html = html.replace("{text_color}", variant.model_extra["text_color_dark"])
                            text_color_applied = True
                        if "item_color_dark" in variant.model_extra:
                            html = html.replace("{item_color}", variant.model_extra["item_color_dark"])
                            item_color_applied = True

                # Standard text_color (if not already applied by dark mode)
                # For text_box: use CSS variable for dark/light mode auto-switching
                if variant.text_color and not text_color_applied:
                    css_var = None
                    if hasattr(variant, 'model_extra') and variant.model_extra:
                        css_var = variant.model_extra.get("css_var")
                    if css_var and component.component_id == "text_box":
                        # Use CSS variable with fallback for dark/light mode switching
                        # Layout Service provides --accent-text-{color} variables
                        heading_color = f"var(--accent-text-{css_var}, {variant.text_color})"
                    else:
                        heading_color = variant.text_color
                    html = html.replace("{text_color}", heading_color)

                # Handle item_color from model_extra (if not already applied by dark mode)
                if not item_color_applied and hasattr(variant, 'model_extra') and variant.model_extra:
                    if "item_color" in variant.model_extra:
                        html = html.replace("{item_color}", variant.model_extra["item_color"])

                # Handle variant-specific placeholders including content_background
                for attr in ["number_color", "heading_color", "content_background", "border_radius"]:
                    attr_value = getattr(variant, attr, None)
                    if attr_value is None and hasattr(variant, 'model_extra') and variant.model_extra is not None:
                        attr_value = variant.model_extra.get(attr)
                    if attr_value:
                        html = html.replace(f"{{{attr}}}", attr_value)

            # Handle padding placeholder
            html = html.replace("{padding}", f"{component.space_requirements.padding_px}px")

            # Handle margin_bottom for stacked layouts
            if i < len(contents) - 1:
                html = html.replace("{margin_bottom}", f"{component.arrangement_rules.gap_px}px")
            else:
                html = html.replace("{margin_bottom}", "0")

            instance_htmls.append(html)

        # Wrap instances if wrapper template exists
        # For text_box: Always apply wrapper (even for single instance) to constrain height with fit-content
        if component.wrapper_template and (len(instance_htmls) > 1 or component.component_id == "text_box"):
            wrapper = component.wrapper_template

            arrangement = layout.arrangement.value if hasattr(layout.arrangement, 'value') else str(layout.arrangement)

            # Parse arrangement to determine grid dimensions
            import re
            if arrangement.startswith("row_"):
                # Horizontal: row_N means N columns, 1 row
                cols = len(instance_htmls)
                rows = 1
            elif arrangement.startswith("stacked_"):
                # Vertical: stacked_N means 1 column, N rows
                cols = 1
                rows = len(instance_htmls)
            elif arrangement.startswith("grid_"):
                # Grid: grid_RxC means C columns, R rows
                match = re.match(r'grid_(\d+)x(\d+)', arrangement)
                if match:
                    rows = int(match.group(1))
                    cols = int(match.group(2))
                else:
                    cols = min(len(instance_htmls), 3)
                    rows = (len(instance_htmls) + cols - 1) // cols
            else:
                # Default to vertical stacking
                cols = 1
                rows = len(instance_htmls)

            wrapper = wrapper.replace("{column_count}", str(cols))
            wrapper = wrapper.replace("{row_count}", str(rows))
            wrapper = wrapper.replace("{gap}", str(component.arrangement_rules.gap_px))
            wrapper = wrapper.replace("{instances}", "\n".join(instance_htmls))

            final_html = wrapper
        else:
            final_html = "\n".join(instance_htmls)

        return final_html, char_counts

    def _generate_dynamic_template(
        self,
        component: ComponentDefinition,
        items_per_instance: int,
        heading_align: str = "left",
        content_align: str = "left",
        list_style: str = "bullets",
        # New styling parameters
        corners: str = "rounded",
        border: bool = False,
        title_style: str = "plain",
        show_title: bool = True
    ) -> str:
        """
        Generate a dynamic template with the correct number of items.

        Handles colored_section (bullets) and comparison_column/sidebar_box (items).
        Enhanced templates with gradient backgrounds, styled bullets, and card layouts.

        Args:
            component: Component definition
            items_per_instance: Number of items/bullets per instance
            heading_align: Text alignment for headings ('left', 'center', 'right')
            content_align: Text alignment for content/bullets ('left', 'center', 'right')
            list_style: List style - 'bullets' (disc), 'numbers' (ordered list), or 'none' (plain text)
            corners: Corner style - 'rounded' (12px) or 'square' (0px)
            border: Show border around boxes
            title_style: Title rendering - 'plain', 'highlighted', or 'colored-bg' (badge)
            show_title: Show or hide the title
        """
        component_id = component.component_id

        if component_id == "colored_section":
            # Build styled bullet list HTML with black disc bullets (21px body text)
            bullets_html = ""
            for i in range(1, items_per_instance + 1):
                margin = "0" if i == items_per_instance else "8px"
                bullets_html += f'<li style="margin-bottom: {margin}; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: {TEXT_SECONDARY};">{{bullet_{i}}}</li>'

            # Enhanced template with gradient background, left border, numbered badge (28px heading)
            return f'''<div style="background: {{background}}; border-left: 5px solid {{heading_color}}; border-radius: 0 12px 12px 0; padding: 20px 24px; margin-bottom: {{margin_bottom}}; box-shadow: 0 4px 12px {{shadow}};"><h3 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: {{heading_color}}; margin: 0 0 14px 0; line-height: 1.2; display: flex; align-items: center;"><span style="background: {{heading_color}}; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; margin-right: 12px;">{{section_number}}</span>{{section_heading}}</h3><ul style="list-style-type: disc; margin: 0; padding-left: 20px;">{bullets_html}</ul></div>'''

        elif component_id == "comparison_column":
            # Build styled bullet list HTML with black disc bullets (21px body text)
            items_html = ""
            for i in range(1, items_per_instance + 1):
                margin = "0" if i == items_per_instance else "12px"
                items_html += f'<li style="margin-bottom: {margin}; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: {TEXT_SECONDARY};">{{item_{i}}}</li>'

            # Enhanced template with gradient header, card styling (28px heading)
            return f'''<div style="background: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 6px 20px {{shadow}};"><div style="background: {{gradient}}; padding: 16px 20px;"><h3 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: white; margin: 0;">{{column_heading}}</h3></div><div style="padding: 18px; background: {{content_background}};"><ul style="list-style-type: disc; margin: 0; padding-left: 20px;">{items_html}</ul></div></div>'''

        elif component_id == "sidebar_box":
            # Build items HTML for sidebar with black disc bullets
            items_html = ""
            for i in range(1, items_per_instance + 1):
                margin = "0" if i == items_per_instance else "14px"
                items_html += f'<li style="margin-bottom: {margin};">{{item_{i}}}</li>'

            # Use dark text colors for light gradient backgrounds with black disc bullets
            return f'''<div style="padding: 32px; border-radius: 12px; background: {{gradient}}; border-left: 4px solid {{accent_color}}; box-shadow: 0 4px 12px rgba(0,0,0,0.05);"><h4 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: {{accent_color}}; margin: 0 0 20px 0; line-height: 1.2;">{{sidebar_heading}}</h4><ul style="list-style-type: disc; padding-left: 20px; margin: 0; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: {TEXT_SECONDARY};">{items_html}</ul></div>'''

        elif component_id == "text_bullets":
            # Build bullet list HTML for text_bullets
            bullets_html = ""
            for i in range(1, items_per_instance + 1):
                margin = "0" if i == items_per_instance else "10px"
                bullets_html += f'<li style="margin-bottom: {margin};">{{bullet_{i}}}</li>'

            return f'''<div style="padding: 24px; background: {{background}}; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);"><h4 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: #1f2937; margin: 0 0 16px 0; line-height: 1.2;">{{subtitle}}</h4><ul style="list-style-type: disc; margin: 0; padding-left: 20px; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: {TEXT_SECONDARY};">{bullets_html}</ul></div>'''

        elif component_id == "bullet_box":
            # Build items HTML for bullet_box with sharp corners and border
            items_html = ""
            for i in range(1, items_per_instance + 1):
                margin = "0" if i == items_per_instance else "10px"
                items_html += f'<li style="margin-bottom: {margin};">{{item_{i}}}</li>'

            return f'''<div style="padding: 24px; background: {{background}}; border: 2px solid {{border_color}}; border-radius: 0;"><h4 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: #1f2937; margin: 0 0 16px 0; line-height: 1.2; padding-bottom: 12px; border-bottom: 1px solid {{border_color}};">{{box_heading}}</h4><ul style="list-style-type: disc; margin: 0; padding-left: 20px; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: {TEXT_SECONDARY};">{items_html}</ul></div>'''

        elif component_id == "numbered_list":
            # Build numbered list HTML
            items_html = ""
            for i in range(1, items_per_instance + 1):
                margin = "0" if i == items_per_instance else "10px"
                items_html += f'<li style="margin-bottom: {margin};">{{item_{i}}}</li>'

            return f'''<div style="padding: 24px; background: {{background}}; border-radius: 12px; border-left: 4px solid {{accent_color}}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);"><h4 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: #1f2937; margin: 0 0 16px 0; line-height: 1.2;">{{list_title}}</h4><ol style="margin: 0; padding-left: 24px; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: {TEXT_SECONDARY}; counter-reset: item;">{items_html}</ol></div>'''

        elif component_id == "text_box":
            # Build items HTML for text_box based on list_style
            # list_style: 'bullets' (disc), 'numbers' (ordered), 'none' (plain text)

            if list_style == "numbers":
                # Ordered list with numbers
                items_html = ""
                for i in range(1, items_per_instance + 1):
                    margin = "0" if i == items_per_instance else "8px"
                    items_html += f'<li style="margin-bottom: {margin};">{{item_{i}}}</li>'
                list_html = f'<ol style="margin: 0; padding-left: 24px; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: var(--text-primary, {{item_color}}); text-align: {content_align};">{items_html}</ol>'
            elif list_style == "none":
                # Plain text without bullets or numbers
                items_html = ""
                for i in range(1, items_per_instance + 1):
                    margin = "0" if i == items_per_instance else "12px"
                    items_html += f'<p style="margin: 0 0 {margin} 0; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: var(--text-primary, {{item_color}}); text-align: {content_align};">{{item_{i}}}</p>'
                list_html = f'<div style="margin: 0;">{items_html}</div>'
            else:
                # Default: bullets (disc)
                items_html = ""
                for i in range(1, items_per_instance + 1):
                    margin = "0" if i == items_per_instance else "8px"
                    items_html += f'<li style="margin-bottom: {margin};">{{item_{i}}}</li>'
                list_html = f'<ul style="list-style-type: disc; margin: 0; padding-left: 20px; font-size: {BODY_FONT_SIZE}; line-height: {BODY_LINE_HEIGHT}; color: var(--text-primary, {{item_color}}); text-align: {content_align};">{items_html}</ul>'

            # Determine border CSS
            border_css = "border: 2px solid rgba(0,0,0,0.1); " if border else ""

            # Build heading HTML based on title_style and show_title
            if not show_title:
                heading_html = ""
                # Standard border_radius for all corners
                border_radius = "0px" if corners == "square" else "12px"
            elif title_style == "colored-bg":
                # Badge style: full-width dark color background, white text
                # Badge sits ON TOP of content box with coordinated corners
                badge_radius = "12px 12px 0 0" if corners != "square" else "0"
                heading_html = f'''<div style="display: block; width: 100%; background: {{title_badge_bg}}; color: #FFFFFF; padding: 12px 24px; border-radius: {badge_radius}; margin: 0; box-sizing: border-box;"><h3 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: #FFFFFF; margin: 0; line-height: 1.2; text-align: {heading_align};">{{box_heading}}</h3></div>'''
                # Content box has only bottom corners rounded (top connects to badge)
                border_radius = "0 0 12px 12px" if corners != "square" else "0"
            elif title_style == "highlighted":
                # Emphasized: larger, bolder, colored (Accent Dark/Light Pastel)
                heading_html = f'''<h3 style="font-size: 32px; font-weight: 800; color: {{text_color}}; margin: 0 0 16px 0; line-height: 1.2; text-align: {heading_align}; text-transform: uppercase; letter-spacing: 0.5px;">{{box_heading}}</h3>'''
                border_radius = "0px" if corners == "square" else "12px"
            elif title_style == "neutral":
                # Non-colored: same color as body text (#374151 light / #FFFFFF dark)
                heading_html = f'''<h3 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: {{item_color}}; margin: 0 0 16px 0; line-height: 1.2; text-align: {heading_align};">{{box_heading}}</h3>'''
                border_radius = "0px" if corners == "square" else "12px"
            else:
                # plain (default) - colored (Accent Dark/Light Pastel)
                heading_html = f'''<h3 style="font-size: {HEADING_FONT_SIZE}; font-weight: 700; color: {{text_color}}; margin: 0 0 16px 0; line-height: 1.2; text-align: {heading_align};">{{box_heading}}</h3>'''
                border_radius = "0px" if corners == "square" else "12px"

            # Build final template with new styling parameters
            if title_style == "colored-bg" and show_title:
                # Badge outside content box, wrapped in flex-column container for vertical stacking
                return f'''<div style="display: flex; flex-direction: column; width: 100%;">{heading_html}<div style="padding: 16px 24px 24px 24px; background: {{background}}; border-radius: {border_radius}; {border_css}box-shadow: 0 8px 24px rgba(0,0,0,0.1);">{list_html}</div></div>'''
            else:
                return f'''<div style="padding: 24px; background: {{background}}; border-radius: {border_radius}; {border_css}box-shadow: 0 8px 24px rgba(0,0,0,0.1);">{heading_html}{list_html}</div>'''

        else:
            # Return original template for components without flexible items
            return component.template

    def _error_result(
        self,
        error: str,
        component_type: str,
        count: int,
        start_time: float
    ) -> AtomicResult:
        """Create an error result."""
        elapsed_ms = int((time.time() - start_time) * 1000)

        return AtomicResult(
            success=False,
            html="",
            component_type=component_type,
            instance_count=count,
            arrangement="none",
            variants_used=[],
            character_counts={},
            metadata=AtomicMetadata(
                generation_time_ms=elapsed_ms,
                model_used="none",
                grid_dimensions={"width": 0, "height": 0},
                space_category="unknown",
                scaling_factor=1.0
            ),
            error=error
        )


# =============================================================================
# Convenience Function
# =============================================================================

async def generate_atomic_component(
    component_type: str,
    prompt: str,
    count: int,
    grid_width: int,
    grid_height: int,
    llm_service: Callable,
    items_per_instance: Optional[int] = None,
    context: Optional[AtomicContext] = None,
    variant: Optional[str] = None,
    placeholder_mode: bool = False,
    transparency: Optional[float] = None,
    layout: LayoutType = LayoutType.HORIZONTAL,
    grid_cols: Optional[int] = None,
    theme_mode: str = "light",
    heading_align: str = "left",
    content_align: str = "left",
    title_max_chars: int = 40,
    item_max_chars: int = 100
) -> AtomicResult:
    """
    Convenience function for quick atomic component generation.

    Args:
        component_type: Internal component ID
        prompt: Content request
        count: Number of instances
        grid_width: Grid width (4-32)
        grid_height: Grid height (4-18)
        llm_service: Async LLM service callable
        items_per_instance: Optional flexible item count
        context: Optional context
        variant: Optional color variant
        placeholder_mode: If True, use placeholder content (no LLM call)
        transparency: Box opacity (0.0-1.0). If None, uses component default
        layout: Layout arrangement (horizontal, vertical, or grid)
        grid_cols: Number of columns for grid layout (auto-calculated if None)
        theme_mode: Theme mode ('light' or 'dark') for text_box accent variants
        heading_align: Text alignment for headings ('left', 'center', 'right')
        content_align: Text alignment for content/bullets ('left', 'center', 'right')
        title_max_chars: Maximum characters for title/heading (10-100)
        item_max_chars: Maximum characters per bullet/item (30-200)

    Returns:
        AtomicResult with generated HTML
    """
    generator = AtomicComponentGenerator(llm_service=llm_service)
    return await generator.generate(
        component_type=component_type,
        prompt=prompt,
        count=count,
        grid_width=grid_width,
        grid_height=grid_height,
        items_per_instance=items_per_instance,
        context=context,
        variant=variant,
        placeholder_mode=placeholder_mode,
        transparency=transparency,
        layout=layout,
        grid_cols=grid_cols,
        theme_mode=theme_mode,
        heading_align=heading_align,
        content_align=content_align,
        title_max_chars=title_max_chars,
        item_max_chars=item_max_chars
    )
