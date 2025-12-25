"""
Spec Analyzer for Text Service CLI

Analyzes placeholder structures and metadata to suggest
variant specification structure for Text Service v1.2.

Generates variant spec JSON based on:
- Detected placeholders
- Metadata configuration
- Text Service patterns
"""

import re
from typing import Dict, List, Optional, Any
from collections import defaultdict


class SpecAnalyzer:
    """
    Analyzes templates and suggests variant specification structure.
    """

    # Element type mappings
    ELEMENT_TYPE_MAPPING = {
        'box': 'text_box',
        'column': 'comparison_column',
        'col': 'comparison_column',
        'metric': 'metric_card',
        'section': 'colored_section',
        'step': 'sequential_step',
        'item': 'list_item',
        'cell': 'table_cell',
        'header': 'table_header',
        'row': 'table_row',
    }

    # Common field names for each element type
    ELEMENT_FIELDS = {
        'text_box': ['title', 'description'],
        'comparison_column': ['heading', 'items'],
        'metric_card': ['value', 'label', 'description'],
        'colored_section': ['heading', 'bullet_1', 'bullet_2', 'bullet_3'],
        'sequential_step': ['title', 'paragraph'],
        'list_item': ['title', 'description'],
        'table_cell': [],
        'table_header': [],
        'table_row': ['category', 'value_1', 'value_2', 'value_3'],
    }

    def __init__(self):
        """Initialize analyzer."""
        pass

    def suggest_variant_spec(
        self,
        placeholder_analysis: Dict,
        metadata: Dict
    ) -> Dict:
        """
        Suggest variant specification based on analysis.

        Args:
            placeholder_analysis: Result from PlaceholderDetector
            metadata: User-provided metadata

        Returns:
            Suggested variant spec dict
        """
        elements = self._build_elements(placeholder_analysis, metadata)

        spec = {
            'variant_id': metadata.get('variant_id', 'new_variant'),
            'slide_type': metadata.get('slide_type', 'unknown'),
            'template_path': self._build_template_path(metadata),
            'description': metadata.get('description', ''),
            'elements': elements,
            'layout': self._suggest_layout(placeholder_analysis, metadata)
        }

        return spec

    def _build_elements(
        self,
        placeholder_analysis: Dict,
        metadata: Dict
    ) -> List[Dict]:
        """
        Build elements list from placeholder analysis.

        Args:
            placeholder_analysis: Result from PlaceholderDetector
            metadata: User-provided metadata

        Returns:
            List of element specifications
        """
        elements = []
        groups = placeholder_analysis.get('placeholder_groups', {})
        structure = placeholder_analysis.get('structure', {})

        # Get user-defined elements if provided
        user_elements = {
            e['element_id']: e
            for e in metadata.get('elements', [])
        }

        for group_key, placeholders in groups.items():
            if group_key == 'other':
                continue

            # Parse element info
            parts = group_key.rsplit('_', 1)
            if len(parts) != 2:
                continue

            element_type_key = parts[0]
            element_num = parts[1]
            element_id = f"{element_type_key}_{element_num}"

            # Determine element type
            element_type = self.ELEMENT_TYPE_MAPPING.get(
                element_type_key, 'text_box'
            )

            # Get user-defined element or create new
            if element_id in user_elements:
                element = user_elements[element_id].copy()
            else:
                element = {
                    'element_id': element_id,
                    'element_type': element_type,
                }

            # Build required fields from placeholders
            required_fields = []
            placeholder_map = {}

            for placeholder in placeholders:
                ph_parts = placeholder.split('_')
                if len(ph_parts) >= 3:
                    field = '_'.join(ph_parts[2:])
                    required_fields.append(field)
                    placeholder_map[field] = placeholder

            element['required_fields'] = element.get('required_fields', required_fields)
            element['placeholders'] = element.get('placeholders', placeholder_map)

            # Add character requirements
            if 'character_requirements' not in element:
                element['character_requirements'] = self._suggest_char_requirements(
                    required_fields
                )

            elements.append(element)

        # Sort by element_id
        elements.sort(key=lambda e: self._element_sort_key(e['element_id']))

        return elements

    def _element_sort_key(self, element_id: str) -> tuple:
        """Generate sort key for element_id."""
        match = re.match(r'([a-z]+)_(\d+)', element_id)
        if match:
            return (match.group(1), int(match.group(2)))
        return (element_id, 0)

    def _suggest_char_requirements(self, fields: List[str]) -> Dict:
        """
        Suggest character requirements for fields.

        Args:
            fields: List of field names

        Returns:
            Character requirements dict
        """
        requirements = {}

        for field in fields:
            base_field = field.split('_')[0].lower()

            # Default requirements based on field type
            defaults = {
                'title': {'baseline': 30, 'min': 25, 'max': 35},
                'heading': {'baseline': 30, 'min': 25, 'max': 35},
                'description': {'baseline': 120, 'min': 100, 'max': 140},
                'paragraph': {'baseline': 200, 'min': 170, 'max': 230},
                'label': {'baseline': 20, 'min': 15, 'max': 25},
                'value': {'baseline': 15, 'min': 5, 'max': 25},
                'items': {'baseline': 150, 'min': 120, 'max': 180},
                'bullet': {'baseline': 60, 'min': 50, 'max': 70},
                'icon': {'baseline': 2, 'min': 1, 'max': 4},
                'category': {'baseline': 25, 'min': 20, 'max': 30},
            }

            if base_field in defaults:
                requirements[field] = defaults[base_field].copy()
            else:
                # Generic default
                requirements[field] = {
                    'baseline': 50,
                    'min': 40,
                    'max': 60
                }

        return requirements

    def _suggest_layout(
        self,
        placeholder_analysis: Dict,
        metadata: Dict
    ) -> Dict:
        """
        Suggest layout configuration.

        Args:
            placeholder_analysis: Result from PlaceholderDetector
            metadata: User-provided metadata

        Returns:
            Layout dict
        """
        # Use user-provided layout if available
        if 'layout' in metadata and metadata['layout']:
            return metadata['layout']

        structure = placeholder_analysis.get('structure', {})
        element_count = structure.get('element_count', 0)
        element_type = structure.get('element_type', 'unknown')

        layout = {}

        # Suggest based on element type and count
        if structure.get('has_boxes'):
            if element_count == 4:
                layout = {'columns': 2, 'rows': 2, 'total_boxes': 4}
            elif element_count == 6:
                layout = {'columns': 3, 'rows': 2, 'total_boxes': 6}
            elif element_count == 9:
                layout = {'columns': 3, 'rows': 3, 'total_boxes': 9}
            else:
                layout = {'total_boxes': element_count}

        elif structure.get('has_columns'):
            layout = {'columns': element_count, 'layout_type': 'vertical_columns'}

        elif structure.get('has_metrics'):
            if element_count <= 4:
                layout = {'columns': element_count, 'layout_type': 'metrics_row'}
            else:
                layout = {'columns': 3, 'rows': 2, 'layout_type': 'metrics_grid'}

        elif structure.get('has_steps'):
            layout = {'steps': element_count, 'layout_type': 'sequential'}

        elif structure.get('has_sections'):
            layout = {'sections': element_count, 'layout_type': 'asymmetric'}

        elif structure.get('has_cells'):
            layout = {'layout_type': 'table'}

        else:
            layout = {'element_count': element_count}

        return layout

    def _build_template_path(self, metadata: Dict) -> str:
        """Build template path from metadata."""
        slide_type = metadata.get('slide_type', 'unknown')
        variant_id = metadata.get('variant_id', 'new_variant')
        return f"app/templates/{slide_type}/{variant_id}.html"

    def analyze_existing_variant(self, variant_spec: Dict) -> Dict:
        """
        Analyze an existing variant spec for insights.

        Args:
            variant_spec: Existing variant specification

        Returns:
            Analysis dict
        """
        analysis = {
            'variant_id': variant_spec.get('variant_id'),
            'slide_type': variant_spec.get('slide_type'),
            'element_count': len(variant_spec.get('elements', [])),
            'element_types': [],
            'total_placeholders': 0,
            'character_constraints': {},
        }

        for element in variant_spec.get('elements', []):
            analysis['element_types'].append(element.get('element_type'))
            analysis['total_placeholders'] += len(element.get('required_fields', []))

            char_reqs = element.get('character_requirements', {})
            for field, reqs in char_reqs.items():
                analysis['character_constraints'][
                    f"{element['element_id']}.{field}"
                ] = reqs

        return analysis

    def compare_specs(self, spec1: Dict, spec2: Dict) -> Dict:
        """
        Compare two variant specs.

        Args:
            spec1: First variant spec
            spec2: Second variant spec

        Returns:
            Comparison dict
        """
        comparison = {
            'same_slide_type': spec1.get('slide_type') == spec2.get('slide_type'),
            'element_count_diff': len(spec1.get('elements', [])) - len(spec2.get('elements', [])),
            'spec1_elements': [e['element_id'] for e in spec1.get('elements', [])],
            'spec2_elements': [e['element_id'] for e in spec2.get('elements', [])],
        }

        # Find common and different elements
        set1 = set(comparison['spec1_elements'])
        set2 = set(comparison['spec2_elements'])

        comparison['common_elements'] = list(set1 & set2)
        comparison['spec1_only'] = list(set1 - set2)
        comparison['spec2_only'] = list(set2 - set1)

        return comparison


def suggest_variant_spec(placeholder_analysis: Dict, metadata: Dict) -> Dict:
    """
    Convenience function to suggest variant spec.

    Args:
        placeholder_analysis: Result from PlaceholderDetector
        metadata: User-provided metadata

    Returns:
        Suggested variant spec dict
    """
    analyzer = SpecAnalyzer()
    return analyzer.suggest_variant_spec(placeholder_analysis, metadata)


if __name__ == "__main__":
    # Test with sample data
    sample_analysis = {
        'placeholder_groups': {
            'box_1': ['box_1_title', 'box_1_description'],
            'box_2': ['box_2_title', 'box_2_description'],
            'box_3': ['box_3_title', 'box_3_description'],
            'box_4': ['box_4_title', 'box_4_description'],
        },
        'structure': {
            'has_boxes': True,
            'element_count': 4,
            'element_type': 'box',
        }
    }

    sample_metadata = {
        'variant_id': 'matrix_2x2',
        'slide_type': 'matrix',
        'description': 'Test 2x2 matrix layout'
    }

    analyzer = SpecAnalyzer()
    spec = analyzer.suggest_variant_spec(sample_analysis, sample_metadata)

    import json
    print(json.dumps(spec, indent=2))
