"""
Component Registry for Agentic Element Generation
==================================================

Loads, caches, and provides access to component definitions.
Components are loaded from JSON files in app/components/.

Usage:
    registry = ComponentRegistry()
    component = registry.get_component("metrics_card")
    all_summaries = registry.get_all_summaries()
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from functools import lru_cache

from ...models.component_models import (
    ComponentDefinition,
    ComponentSummary,
    ComponentIndex,
    SlotSpec,
    ComponentVariant,
    SpaceRequirements,
    ArrangementRules,
    ScalingRules,
    ArrangementType
)


class ComponentRegistry:
    """
    Registry for component definitions.

    Loads components from JSON files and provides fast access
    for the assembly agent.
    """

    # Singleton instance
    _instance: Optional["ComponentRegistry"] = None

    def __new__(cls, *args, **kwargs):
        """Ensure singleton pattern for registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        components_dir: Optional[str] = None,
        auto_load: bool = True
    ):
        """
        Initialize the component registry.

        Args:
            components_dir: Path to components directory (default: app/components)
            auto_load: Whether to load components on initialization
        """
        if self._initialized:
            return

        # Determine components directory
        if components_dir:
            self.components_dir = Path(components_dir)
        else:
            # Default: relative to this file's location
            self.components_dir = Path(__file__).parent.parent.parent / "components"

        self._components: Dict[str, ComponentDefinition] = {}
        self._index: Optional[ComponentIndex] = None
        self._initialized = True

        if auto_load:
            self.load_all_components()

    def load_all_components(self) -> None:
        """Load all component definitions from JSON files."""
        # First try to load the index
        index_path = self.components_dir / "component_index.json"
        if index_path.exists():
            self._load_from_index(index_path)
        else:
            # Fallback: scan directory for JSON files
            self._scan_and_load()

    def _load_from_index(self, index_path: Path) -> None:
        """Load components using the index file."""
        with open(index_path, "r") as f:
            index_data = json.load(f)

        self._index = ComponentIndex(**index_data)

        for component_id, file_path in self._index.components.items():
            full_path = self.components_dir / file_path
            if full_path.exists():
                self._load_component_file(full_path)
            else:
                print(f"Warning: Component file not found: {full_path}")

    def _scan_and_load(self) -> None:
        """Scan components directory and load all JSON files."""
        if not self.components_dir.exists():
            print(f"Warning: Components directory not found: {self.components_dir}")
            return

        for json_file in self.components_dir.glob("*.json"):
            if json_file.name != "component_index.json":
                self._load_component_file(json_file)

    def _load_component_file(self, file_path: Path) -> None:
        """Load a single component definition from JSON."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            component = self._parse_component_data(data)
            self._components[component.component_id] = component

        except json.JSONDecodeError as e:
            print(f"Error parsing component file {file_path}: {e}")
        except Exception as e:
            print(f"Error loading component file {file_path}: {e}")

    def _parse_component_data(self, data: Dict) -> ComponentDefinition:
        """Parse raw JSON data into ComponentDefinition."""
        # Parse slots
        slots = {}
        for slot_id, slot_data in data.get("slots", {}).items():
            slots[slot_id] = SlotSpec(**slot_data)

        # Parse variants
        variants = {}
        for variant_id, variant_data in data.get("variants", {}).items():
            variants[variant_id] = ComponentVariant(
                variant_id=variant_id,
                **variant_data
            )

        # Parse space requirements
        space_req = SpaceRequirements(**data.get("space_requirements", {}))

        # Parse arrangement rules
        arr_data = data.get("arrangement_rules", {})
        if "valid_arrangements" in arr_data:
            arr_data["valid_arrangements"] = [
                ArrangementType(a) if isinstance(a, str) else a
                for a in arr_data["valid_arrangements"]
            ]
        arrangement_rules = ArrangementRules(**arr_data)

        # Parse scaling rules
        scaling_rules = ScalingRules(**data.get("scaling_rules", {}))

        return ComponentDefinition(
            component_id=data["component_id"],
            description=data.get("description", ""),
            use_cases=data.get("use_cases", []),
            template=data.get("template", ""),
            slots=slots,
            variants=variants,
            space_requirements=space_req,
            arrangement_rules=arrangement_rules,
            scaling_rules=scaling_rules,
            wrapper_template=data.get("wrapper_template")
        )

    def get_component(self, component_id: str) -> Optional[ComponentDefinition]:
        """
        Get a component definition by ID.

        Args:
            component_id: The component identifier

        Returns:
            ComponentDefinition or None if not found
        """
        return self._components.get(component_id)

    def get_all_components(self) -> Dict[str, ComponentDefinition]:
        """Get all loaded component definitions."""
        return self._components.copy()

    def get_component_ids(self) -> List[str]:
        """Get list of all component IDs."""
        return list(self._components.keys())

    def get_all_summaries(self) -> List[ComponentSummary]:
        """
        Get summaries of all components.

        Used by the get_available_components tool.
        """
        summaries = []
        for component in self._components.values():
            summary = ComponentSummary(
                component_id=component.component_id,
                description=component.description,
                use_cases=component.use_cases,
                min_space=f"{component.space_requirements.min_grid_width}x{component.space_requirements.min_grid_height} grid",
                slot_count=len(component.slots),
                variant_count=len(component.variants)
            )
            summaries.append(summary)
        return summaries

    def get_components_by_use_case(self, use_case: str) -> List[ComponentDefinition]:
        """
        Find components matching a use case keyword.

        Args:
            use_case: Keyword to match (e.g., "metrics", "comparison")

        Returns:
            List of matching components
        """
        use_case_lower = use_case.lower()
        matching = []
        for component in self._components.values():
            # Check description
            if use_case_lower in component.description.lower():
                matching.append(component)
                continue
            # Check use_cases list
            for uc in component.use_cases:
                if use_case_lower in uc.lower():
                    matching.append(component)
                    break
        return matching

    def get_components_that_fit(
        self,
        grid_width: int,
        grid_height: int
    ) -> List[ComponentDefinition]:
        """
        Get components that fit within given space.

        Args:
            grid_width: Available width in grid units
            grid_height: Available height in grid units

        Returns:
            List of components that fit
        """
        fitting = []
        for component in self._components.values():
            space_req = component.space_requirements
            if (space_req.min_grid_width <= grid_width and
                    space_req.min_grid_height <= grid_height):
                fitting.append(component)
        return fitting

    def reload(self) -> None:
        """Reload all components from disk."""
        self._components.clear()
        self.load_all_components()

    @property
    def component_count(self) -> int:
        """Number of loaded components."""
        return len(self._components)

    def __contains__(self, component_id: str) -> bool:
        """Check if component exists."""
        return component_id in self._components

    def __repr__(self) -> str:
        return f"<ComponentRegistry: {self.component_count} components>"


# =============================================================================
# Global Registry Instance
# =============================================================================

def get_registry() -> ComponentRegistry:
    """Get the global component registry instance."""
    return ComponentRegistry()


@lru_cache(maxsize=1)
def get_cached_registry() -> ComponentRegistry:
    """Get cached registry instance (use for performance)."""
    return ComponentRegistry()
