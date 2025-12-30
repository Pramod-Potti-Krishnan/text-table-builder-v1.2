"""
Agent Tools for Component-Based Assembly
=========================================

These tools are used by the ComponentAssemblyAgent to:
1. analyze_space - Understand available space
2. get_available_components - List component options
3. select_component_layout - Configure arrangement
4. generate_component_content - Create content for slots
5. assemble_html - Build final HTML

Each tool has a clear interface for the agent to use.
"""

from typing import Dict, List, Optional, Any, Callable
import json

from .registry import ComponentRegistry, get_registry
from .constraints import (
    SpaceCalculator,
    CharacterLimitScaler,
    LayoutBuilder,
    CELL_SIZE_PX
)
from ...models.component_models import (
    SpaceAnalysis,
    ComponentSummary,
    LayoutSelection,
    GeneratedContent,
    AssemblyResult,
    CharLimits,
    ComponentDefinition
)


# =============================================================================
# Tool 1: analyze_space
# =============================================================================

def analyze_space(
    grid_width: int,
    grid_height: int,
    padding_px: int = 40
) -> SpaceAnalysis:
    """
    Analyze available space and determine what can fit.

    This tool helps the agent understand the canvas before
    making component selection decisions.

    Args:
        grid_width: Available width in grid units (1-32)
        grid_height: Available height in grid units (1-18)
        padding_px: Padding around content area

    Returns:
        SpaceAnalysis with:
        - total_width_px, total_height_px
        - usable_width_px, usable_height_px
        - recommended_counts per component type
        - layout_options (valid arrangements)
        - space_category (small/medium/large)
    """
    calculator = SpaceCalculator()
    return calculator.analyze_space(grid_width, grid_height, padding_px)


# =============================================================================
# Tool 2: get_available_components
# =============================================================================

def get_available_components() -> List[ComponentSummary]:
    """
    Get list of all available components with their use cases.

    This tool helps the agent understand what components are
    available for selection.

    Returns:
        List of ComponentSummary with:
        - component_id
        - description
        - use_cases
        - min_space required
        - slot_count
        - variant_count
    """
    registry = get_registry()
    return registry.get_all_summaries()


def get_component_details(component_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific component.

    Args:
        component_id: The component to look up

    Returns:
        Dictionary with full component details or None if not found
    """
    registry = get_registry()
    component = registry.get_component(component_id)

    if not component:
        return None

    return {
        "component_id": component.component_id,
        "description": component.description,
        "use_cases": component.use_cases,
        "slots": {
            slot_id: {
                "min_chars": spec.min_chars,
                "max_chars": spec.max_chars,
                "description": spec.description,
                "format_hint": spec.format_hint
            }
            for slot_id, spec in component.slots.items()
        },
        "variants": list(component.variants.keys()),
        "space_requirements": {
            "min_grid_width": component.space_requirements.min_grid_width,
            "min_grid_height": component.space_requirements.min_grid_height
        },
        "arrangement_rules": {
            "min_instances": component.arrangement_rules.min_instances,
            "max_instances": component.arrangement_rules.max_instances,
            "valid_arrangements": [a.value for a in component.arrangement_rules.valid_arrangements]
        }
    }


# =============================================================================
# Tool 3: select_component_layout
# =============================================================================

def select_component_layout(
    component_id: str,
    instance_count: int,
    grid_width: int,
    grid_height: int
) -> Optional[LayoutSelection]:
    """
    Determine optimal layout for selected component.

    This tool configures how the component instances will be
    arranged in the available space.

    Args:
        component_id: Which component to use
        instance_count: How many instances to show
        grid_width: Available width in grid units
        grid_height: Available height in grid units

    Returns:
        LayoutSelection with:
        - arrangement (row_3, grid_2x2, etc.)
        - adjusted_count (may differ from requested)
        - scaled_char_limits per slot
        - variant_assignments (color per instance)
        - fits_space (bool)

        Returns None if component not found.
    """
    registry = get_registry()
    component = registry.get_component(component_id)

    if not component:
        return None

    # Clamp instance count to valid range
    min_count = component.arrangement_rules.min_instances
    max_count = component.arrangement_rules.max_instances
    actual_count = max(min_count, min(max_count, instance_count))

    # Build layout using constraint system
    builder = LayoutBuilder()
    layout = builder.build_layout(
        component=component,
        instance_count=actual_count,
        grid_width=grid_width,
        grid_height=grid_height
    )

    return layout


# =============================================================================
# Tool 4: generate_component_content
# =============================================================================

async def generate_component_content(
    component_id: str,
    user_prompt: str,
    instance_count: int,
    char_limits: Dict[str, CharLimits],
    llm_service: Optional[Callable] = None,
    context: Optional[Dict[str, Any]] = None
) -> List[GeneratedContent]:
    """
    Generate content for all component instances.

    This tool uses the LLM to generate content that fills
    the component slots.

    Args:
        component_id: Which component to generate for
        user_prompt: What content the user wants
        instance_count: How many instances
        char_limits: Scaled character limits per slot
        llm_service: Async callable that takes prompt and returns content
        context: Optional context (audience, purpose, etc.)

    Returns:
        List of GeneratedContent (one per instance) with:
        - instance_index
        - slot_values (dict of slot_id -> content)
        - character_counts
    """
    registry = get_registry()
    component = registry.get_component(component_id)

    if not component:
        raise ValueError(f"Component not found: {component_id}")

    if not llm_service:
        raise ValueError("LLM service required for content generation")

    # Build the content generation prompt
    prompt = _build_content_generation_prompt(
        component=component,
        user_prompt=user_prompt,
        instance_count=instance_count,
        char_limits=char_limits,
        context=context
    )

    # Call LLM service
    llm_response = await llm_service(prompt)

    # Parse response into GeneratedContent list
    contents = _parse_content_response(llm_response, instance_count, component)

    return contents


def _build_content_generation_prompt(
    component: ComponentDefinition,
    user_prompt: str,
    instance_count: int,
    char_limits: Dict[str, CharLimits],
    context: Optional[Dict[str, Any]] = None
) -> str:
    """Build prompt for content generation."""

    # Build slot descriptions
    slot_specs = []
    for slot_id, limits in char_limits.items():
        spec = component.slots.get(slot_id)
        if spec:
            slot_specs.append(
                f"  - {slot_id}: {spec.description} "
                f"({limits.min_chars}-{limits.max_chars} chars"
                f"{', format: ' + spec.format_hint if spec.format_hint else ''})"
            )

    slots_text = "\n".join(slot_specs)

    # Build context section
    context_text = ""
    if context:
        if context.get("audience"):
            context_text += f"Audience: {context['audience']}\n"
        if context.get("purpose"):
            context_text += f"Purpose: {context['purpose']}\n"
        if context.get("presentation_title"):
            context_text += f"Presentation: {context['presentation_title']}\n"

    prompt = f"""Generate content for {instance_count} {component.component_id} component(s).

USER REQUEST:
{user_prompt}

{f'CONTEXT:' + chr(10) + context_text if context_text else ''}

COMPONENT: {component.description}

SLOTS TO FILL (for each instance):
{slots_text}

REQUIREMENTS:
1. Generate EXACTLY {instance_count} instances
2. Each instance must have ALL slots filled
3. Content must be DIFFERENT across instances (no repetition)
4. Stay within character limits
5. Content should be coherent and support the overall message

OUTPUT FORMAT:
Return a JSON object with instance data:
{{
  "instances": [
    {{
      "slot_id_1": "content for slot 1",
      "slot_id_2": "content for slot 2",
      ...
    }},
    ...
  ]
}}

Generate the content now:"""

    return prompt


def _parse_content_response(
    llm_response: str,
    instance_count: int,
    component: ComponentDefinition
) -> List[GeneratedContent]:
    """Parse LLM response into GeneratedContent list."""
    import re

    # Try to extract JSON from response
    try:
        data = json.loads(llm_response)
    except json.JSONDecodeError:
        # Try to find JSON in markdown code block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                raise ValueError(f"Could not parse LLM response as JSON: {llm_response[:200]}")

    # Extract instances
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


# =============================================================================
# Tool 5: assemble_html
# =============================================================================

def assemble_html(
    component_id: str,
    layout: LayoutSelection,
    content: List[GeneratedContent]
) -> AssemblyResult:
    """
    Assemble final HTML from components and content.

    This tool combines the component template with generated
    content to produce the final HTML output.

    Args:
        component_id: Which component to assemble
        layout: Layout configuration from select_component_layout
        content: Generated content from generate_component_content

    Returns:
        AssemblyResult with:
        - html: Complete HTML string
        - component_id
        - instance_count
        - arrangement
        - variants_used
        - total_characters
    """
    registry = get_registry()
    component = registry.get_component(component_id)

    if not component:
        raise ValueError(f"Component not found: {component_id}")

    # Generate HTML for each instance
    instance_htmls = []
    total_chars = 0

    for i, gen_content in enumerate(content):
        # Get variant for this instance
        variant_id = layout.variant_assignments[i] if i < len(layout.variant_assignments) else list(component.variants.keys())[0]
        variant = component.variants.get(variant_id)

        # Fill template with content and variant values
        html = component.template

        # Replace content placeholders
        for slot_id, value in gen_content.slot_values.items():
            html = html.replace(f"{{{slot_id}}}", str(value))
            total_chars += len(str(value))

        # Replace variant placeholders
        if variant:
            if variant.gradient:
                html = html.replace("{gradient}", variant.gradient)
            if variant.background:
                html = html.replace("{background}", variant.background)
            if variant.shadow:
                html = html.replace("{shadow}", variant.shadow)
            if variant.accent_color:
                html = html.replace("{accent_color}", variant.accent_color)
            if variant.text_color:
                html = html.replace("{text_color}", variant.text_color)

            # Handle variant-specific placeholders (like {number_color})
            for attr in ["number_color", "heading_color"]:
                attr_value = getattr(variant, attr, None) if hasattr(variant, attr) else variant.model_extra.get(attr) if hasattr(variant, 'model_extra') else None
                if attr_value:
                    html = html.replace(f"{{{attr}}}", attr_value)

        # Handle padding placeholder
        html = html.replace("{padding}", f"{component.space_requirements.padding_px}px")

        # Handle margin_bottom for stacked layouts
        if i < len(content) - 1:
            html = html.replace("{margin_bottom}", f"{component.arrangement_rules.gap_px}px")
        else:
            html = html.replace("{margin_bottom}", "0")

        instance_htmls.append(html)

    # Wrap instances if wrapper template exists
    if component.wrapper_template and len(instance_htmls) > 1:
        wrapper = component.wrapper_template

        # Determine columns/rows for wrapper
        if layout.arrangement in ["row_2", "row_3", "row_4"]:
            wrapper = wrapper.replace("{column_count}", str(len(instance_htmls)))
            wrapper = wrapper.replace("{row_count}", "1")
        elif layout.arrangement == "grid_2x2":
            wrapper = wrapper.replace("{column_count}", "2")
            wrapper = wrapper.replace("{row_count}", "2")
        elif layout.arrangement == "grid_3x2":
            wrapper = wrapper.replace("{column_count}", "3")
            wrapper = wrapper.replace("{row_count}", "2")
        else:
            wrapper = wrapper.replace("{column_count}", "1")
            wrapper = wrapper.replace("{row_count}", str(len(instance_htmls)))

        wrapper = wrapper.replace("{gap}", str(component.arrangement_rules.gap_px))
        wrapper = wrapper.replace("{instances}", "\n".join(instance_htmls))

        final_html = wrapper
    else:
        final_html = "\n".join(instance_htmls)

    return AssemblyResult(
        html=final_html,
        component_id=component_id,
        instance_count=len(content),
        arrangement=layout.arrangement.value if hasattr(layout.arrangement, 'value') else str(layout.arrangement),
        variants_used=layout.variant_assignments[:len(content)],
        total_characters=total_chars
    )


# =============================================================================
# Tool Registry (for agent use)
# =============================================================================

AVAILABLE_TOOLS = {
    "analyze_space": {
        "function": analyze_space,
        "description": "Analyze available space and determine what can fit",
        "parameters": {
            "grid_width": "Available width in grid units (1-32)",
            "grid_height": "Available height in grid units (1-18)",
            "padding_px": "Optional padding around content (default 40)"
        }
    },
    "get_available_components": {
        "function": get_available_components,
        "description": "Get list of all available components with use cases",
        "parameters": {}
    },
    "get_component_details": {
        "function": get_component_details,
        "description": "Get detailed information about a specific component",
        "parameters": {
            "component_id": "The component to look up"
        }
    },
    "select_component_layout": {
        "function": select_component_layout,
        "description": "Determine optimal layout for selected component",
        "parameters": {
            "component_id": "Which component to use",
            "instance_count": "How many instances to show",
            "grid_width": "Available width in grid units",
            "grid_height": "Available height in grid units"
        }
    },
    "generate_component_content": {
        "function": generate_component_content,
        "description": "Generate content for component slots using LLM",
        "parameters": {
            "component_id": "Which component to generate for",
            "user_prompt": "What content the user wants",
            "instance_count": "How many instances",
            "char_limits": "Scaled character limits per slot",
            "llm_service": "Async LLM service callable",
            "context": "Optional context dict"
        }
    },
    "assemble_html": {
        "function": assemble_html,
        "description": "Assemble final HTML from components and content",
        "parameters": {
            "component_id": "Which component to assemble",
            "layout": "Layout configuration",
            "content": "Generated content list"
        }
    }
}


def get_tools_description() -> str:
    """Get formatted description of all available tools for agent prompt."""
    lines = ["Available Tools:"]
    for name, info in AVAILABLE_TOOLS.items():
        lines.append(f"\n{name}: {info['description']}")
        if info['parameters']:
            lines.append("  Parameters:")
            for param, desc in info['parameters'].items():
                lines.append(f"    - {param}: {desc}")
    return "\n".join(lines)
