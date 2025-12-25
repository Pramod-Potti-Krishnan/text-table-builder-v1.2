"""
Placeholder Detector for Text Service CLI

Analyzes HTML templates to detect and group placeholders using
Text Service naming conventions.

Placeholder Patterns:
- {box_N_title}, {box_N_description}
- {section_N_heading}, {section_N_bullet_N}
- {metric_N_value}, {metric_N_label}
- {column_N_heading}, {column_N_items}
- {step_N_title}, {step_N_paragraph}
- {cell_N_M} (row_column)
- {header_N}
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class PlaceholderDetector:
    """
    Detects and analyzes placeholders in Text Service templates.

    Supports automatic grouping by element type and structure analysis.
    """

    # Known placeholder patterns in Text Service
    PLACEHOLDER_PATTERNS = {
        'box': re.compile(r'box_(\d+)_(\w+)'),
        'section': re.compile(r'section_(\d+)_(\w+)'),
        'metric': re.compile(r'metric_(\d+)_(\w+)'),
        'column': re.compile(r'col(?:umn)?_(\d+)_(\w+)'),
        'step': re.compile(r'step_(\d+)_(\w+)'),
        'item': re.compile(r'item_(\d+)_(\w+)'),
        'cell': re.compile(r'cell_(\d+)_(\d+)'),
        'header': re.compile(r'header_(\d+)'),
        'row': re.compile(r'row_(\d+)_(\w+)'),
    }

    # Common field names and their typical character counts
    COMMON_FIELDS = {
        'title': {'baseline': 30, 'min': 25, 'max': 40},
        'heading': {'baseline': 30, 'min': 25, 'max': 40},
        'description': {'baseline': 120, 'min': 100, 'max': 150},
        'paragraph': {'baseline': 200, 'min': 150, 'max': 250},
        'label': {'baseline': 20, 'min': 15, 'max': 30},
        'value': {'baseline': 15, 'min': 5, 'max': 25},
        'items': {'baseline': 150, 'min': 100, 'max': 200},
        'bullet': {'baseline': 60, 'min': 40, 'max': 80},
        'icon': {'baseline': 2, 'min': 1, 'max': 4},
    }

    def __init__(self):
        """Initialize detector."""
        self._placeholders: List[str] = []
        self._placeholder_groups: Dict[str, List[str]] = {}
        self._structure: Dict = {}

    def detect_placeholders(self, html_content: str) -> Dict:
        """
        Detect all placeholders in HTML template.

        Args:
            html_content: HTML template content

        Returns:
            Dict with detection results:
            - total_placeholders: Total placeholder count
            - unique_placeholders: Unique placeholder count
            - placeholder_list: List of all placeholders
            - placeholder_groups: Grouped by element type
            - structure: Analyzed structure
        """
        # Find all placeholders (excluding CSS variables)
        # Pattern: {word} where word starts with letter and contains only alphanumeric + underscore
        all_matches = re.findall(r'\{([a-z][a-z0-9_]*)\}', html_content, re.IGNORECASE)

        self._placeholders = all_matches
        self._placeholder_groups = self._group_placeholders(all_matches)
        self._structure = self._analyze_structure()

        return {
            'total_placeholders': len(all_matches),
            'unique_placeholders': len(set(all_matches)),
            'placeholder_list': list(set(all_matches)),
            'placeholder_groups': self._placeholder_groups,
            'structure': self._structure
        }

    def _group_placeholders(self, placeholders: List[str]) -> Dict[str, List[str]]:
        """
        Group placeholders by element type.

        Args:
            placeholders: List of placeholder names

        Returns:
            Dict mapping element group to list of placeholders
        """
        groups = defaultdict(list)
        ungrouped = []

        for placeholder in set(placeholders):
            grouped = False

            # Try each pattern
            for pattern_type, pattern in self.PLACEHOLDER_PATTERNS.items():
                match = pattern.match(placeholder)
                if match:
                    # Create group key (e.g., "box_1", "column_2")
                    element_num = match.group(1)
                    group_key = f"{pattern_type}_{element_num}"
                    groups[group_key].append(placeholder)
                    grouped = True
                    break

            if not grouped:
                ungrouped.append(placeholder)

        # Add ungrouped to 'other'
        if ungrouped:
            groups['other'] = ungrouped

        return dict(groups)

    def _analyze_structure(self) -> Dict:
        """
        Analyze placeholder structure.

        Returns:
            Dict with structure analysis
        """
        structure = {
            'has_boxes': False,
            'has_columns': False,
            'has_metrics': False,
            'has_sections': False,
            'has_steps': False,
            'has_cells': False,
            'element_count': 0,
            'element_type': 'unknown',
            'fields_per_element': {}
        }

        # Determine primary element type
        element_types = defaultdict(int)

        for group_key in self._placeholder_groups.keys():
            if group_key == 'other':
                continue

            # Extract type from group key
            parts = group_key.rsplit('_', 1)
            if len(parts) == 2:
                elem_type = parts[0]
                element_types[elem_type] += 1

        if element_types:
            # Find most common type
            primary_type = max(element_types, key=element_types.get)
            structure['element_type'] = primary_type
            structure['element_count'] = element_types[primary_type]

            # Set flags
            structure['has_boxes'] = 'box' in element_types
            structure['has_columns'] = 'column' in element_types or 'col' in element_types
            structure['has_metrics'] = 'metric' in element_types
            structure['has_sections'] = 'section' in element_types
            structure['has_steps'] = 'step' in element_types
            structure['has_cells'] = 'cell' in element_types

        # Analyze fields per element
        fields_per_element = defaultdict(set)
        for group_key, placeholders in self._placeholder_groups.items():
            if group_key == 'other':
                continue

            for placeholder in placeholders:
                # Extract field name
                parts = placeholder.split('_')
                if len(parts) >= 3:
                    field = '_'.join(parts[2:])  # Everything after element_N_
                    fields_per_element[group_key].add(field)

        structure['fields_per_element'] = {k: list(v) for k, v in fields_per_element.items()}

        return structure

    def validate_against_constraints(
        self,
        analysis: Dict,
        constraints: Dict
    ) -> Dict:
        """
        Validate placeholders against provided constraints.

        Args:
            analysis: Result from detect_placeholders()
            constraints: Constraints dict from constraints.json

        Returns:
            Validation result dict
        """
        issues = []
        placeholders = set(analysis.get('placeholder_list', []))

        # Check that all placeholders have constraints
        for placeholder in placeholders:
            # Parse element_id and field
            parts = placeholder.split('_')
            if len(parts) >= 3:
                element_id = f"{parts[0]}_{parts[1]}"
                field = '_'.join(parts[2:])

                if element_id not in constraints:
                    issues.append(f"No constraints for element '{element_id}'")
                elif field not in constraints.get(element_id, {}):
                    issues.append(f"No constraint for '{element_id}.{field}'")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def suggest_constraints(self, analysis: Dict) -> Dict:
        """
        Suggest character constraints based on detected placeholders.

        Args:
            analysis: Result from detect_placeholders()

        Returns:
            Suggested constraints dict
        """
        suggested = {}
        groups = analysis.get('placeholder_groups', {})

        for group_key, placeholders in groups.items():
            if group_key == 'other':
                continue

            # Parse element_id from group_key
            parts = group_key.rsplit('_', 1)
            if len(parts) == 2:
                element_type = parts[0]
                element_num = parts[1]
                element_id = f"{element_type}_{element_num}"

                suggested[element_id] = {}

                for placeholder in placeholders:
                    # Extract field name
                    ph_parts = placeholder.split('_')
                    if len(ph_parts) >= 3:
                        field = '_'.join(ph_parts[2:])

                        # Find base field type for defaults
                        base_field = field.split('_')[0]

                        if base_field in self.COMMON_FIELDS:
                            suggested[element_id][field] = self.COMMON_FIELDS[base_field].copy()
                        else:
                            # Default constraints
                            suggested[element_id][field] = {
                                'baseline': 50,
                                'min': 40,
                                'max': 60
                            }

        return suggested

    def generate_sample_content(self, analysis: Dict) -> Dict[str, str]:
        """
        Generate sample content for all placeholders.

        Args:
            analysis: Result from detect_placeholders()

        Returns:
            Dict mapping placeholder to sample content
        """
        samples = {}
        groups = analysis.get('placeholder_groups', {})

        for group_key, placeholders in groups.items():
            for placeholder in placeholders:
                # Generate based on field type
                parts = placeholder.split('_')
                if len(parts) >= 3:
                    field = '_'.join(parts[2:])
                    samples[placeholder] = self._generate_sample_for_field(field, placeholder)
                else:
                    samples[placeholder] = f"Sample {placeholder}"

        return samples

    def _generate_sample_for_field(self, field: str, placeholder: str) -> str:
        """Generate sample content for a specific field type."""
        base_field = field.split('_')[0].lower()

        samples = {
            'title': 'Strategic Growth Initiative',
            'heading': 'Key Performance Metrics',
            'description': 'Comprehensive analysis of market trends and competitive positioning strategies for sustainable growth.',
            'paragraph': 'Our data-driven approach combines advanced analytics with industry expertise to deliver actionable insights that drive business transformation.',
            'label': 'Revenue Growth',
            'value': '+24%',
            'items': '<li>Enhanced efficiency</li><li>Cost optimization</li><li>Quality improvement</li>',
            'bullet': 'Streamlined operations through automation',
            'icon': '📊',
        }

        if base_field in samples:
            return samples[base_field]
        elif 'bullet' in field:
            return 'Key insight or action item'
        elif 'icon' in field:
            return '✨'
        else:
            return f'Sample content for {placeholder}'


def detect_template_placeholders(html_content: str) -> Dict:
    """
    Convenience function to detect placeholders.

    Args:
        html_content: HTML template content

    Returns:
        Detection results dict
    """
    detector = PlaceholderDetector()
    return detector.detect_placeholders(html_content)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python placeholder_detector.py <template.html>")
        sys.exit(1)

    template_path = sys.argv[1]

    with open(template_path, 'r') as f:
        html_content = f.read()

    detector = PlaceholderDetector()
    result = detector.detect_placeholders(html_content)

    print(f"Total placeholders: {result['total_placeholders']}")
    print(f"Unique placeholders: {result['unique_placeholders']}")
    print(f"\nPlaceholder groups:")

    for group, placeholders in result['placeholder_groups'].items():
        print(f"  {group}: {placeholders}")

    print(f"\nStructure: {result['structure']}")

    # Generate suggested constraints
    suggested = detector.suggest_constraints(result)
    print(f"\nSuggested constraints:")
    for elem_id, fields in suggested.items():
        print(f"  {elem_id}: {list(fields.keys())}")
