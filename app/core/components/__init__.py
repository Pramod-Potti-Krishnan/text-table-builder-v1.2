"""
Component Assembly System for Agentic Element Generation
=========================================================

This module provides a component-based approach to slide content generation.
Instead of generating raw HTML, an LLM agent reasons about storytelling needs
and selects appropriate pre-designed components to assemble polished output.

Components:
- registry.py: ComponentRegistry - loads and caches component definitions
- agent.py: ComponentAssemblyAgent - master orchestrator with CoT reasoning
- atomic_generator.py: AtomicComponentGenerator - direct component generation
- tools.py: Agent tools (analyze_space, select_layout, etc.)
- constraints.py: Space calculations and scaling rules

Usage (CoT-based agent selection):
    from app.core.components import ComponentAssemblyAgent, get_registry

    agent = ComponentAssemblyAgent(llm_service=my_llm_service)
    result = await agent.generate(
        prompt="Show our Q4 metrics",
        grid_width=12,
        grid_height=8,
        audience="executive",
        purpose="inform"
    )

Usage (Direct atomic component generation):
    from app.core.components import AtomicComponentGenerator

    generator = AtomicComponentGenerator(llm_service=my_llm_service)
    result = await generator.generate(
        component_type="colored_section",
        prompt="Key benefits of our initiative",
        count=3,
        grid_width=24,
        grid_height=12,
        items_per_instance=4  # 4 bullets per section
    )
"""

from .registry import ComponentRegistry, get_registry, get_cached_registry
from .constraints import (
    SpaceCalculator,
    CharacterLimitScaler,
    LayoutBuilder,
    ArrangementSelector,
    VariantAssigner,
    GRID_COLUMNS,
    GRID_ROWS,
    CELL_SIZE_PX
)
from .tools import (
    analyze_space,
    get_available_components,
    get_component_details,
    select_component_layout,
    generate_component_content,
    assemble_html,
    get_tools_description,
    AVAILABLE_TOOLS
)
from .agent import (
    ComponentAssemblyAgent,
    AgentResult,
    generate_with_components,
    AGENT_SYSTEM_PROMPT
)
from .atomic_generator import (
    AtomicComponentGenerator,
    AtomicResult,
    generate_atomic_component
)

__all__ = [
    # Registry
    "ComponentRegistry",
    "get_registry",
    "get_cached_registry",
    # Constraints
    "SpaceCalculator",
    "CharacterLimitScaler",
    "LayoutBuilder",
    "ArrangementSelector",
    "VariantAssigner",
    "GRID_COLUMNS",
    "GRID_ROWS",
    "CELL_SIZE_PX",
    # Tools
    "analyze_space",
    "get_available_components",
    "get_component_details",
    "select_component_layout",
    "generate_component_content",
    "assemble_html",
    "get_tools_description",
    "AVAILABLE_TOOLS",
    # Agent
    "ComponentAssemblyAgent",
    "AgentResult",
    "generate_with_components",
    "AGENT_SYSTEM_PROMPT",
    # Atomic Generator
    "AtomicComponentGenerator",
    "AtomicResult",
    "generate_atomic_component",
]
