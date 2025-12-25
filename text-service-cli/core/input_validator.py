"""
Input Validator for Text Service CLI

Validates integration input files for both content variants and hero generators.

For variants:
- template.html (required) - HTML template with placeholders
- metadata.json (required) - Variant metadata and elements
- constraints.json (optional) - Character count constraints

For heroes:
- metadata.json (required) - Hero type metadata
- prompt_template.md (required) - LLM prompt template
- validation_rules.json (required) - Output validation rules
- example_html.html (optional) - Example output
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup


class InputValidator:
    """Validates Text Service integration inputs."""

    # Required metadata fields for variants
    REQUIRED_VARIANT_METADATA = [
        'variant_id',
        'slide_type',
        'description',
        'elements',
        'layout'
    ]

    # Required metadata fields for hero generators
    REQUIRED_HERO_METADATA = [
        'hero_type',
        'display_name',
        'description',
        'endpoint_path',
        'html_structure',
        'character_constraints'
    ]

    # Valid slide types in Text Service
    VALID_SLIDE_TYPES = [
        'matrix', 'grid', 'comparison', 'sequential', 'asymmetric',
        'hybrid', 'metrics', 'single_column', 'impact_quote', 'table'
    ]

    def __init__(self, input_dir: Path, format_type: str):
        """
        Initialize validator.

        Args:
            input_dir: Path to input directory
            format_type: 'variant' or 'hero'
        """
        self.input_dir = Path(input_dir)
        self.format_type = format_type
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, Dict]:
        """
        Validate all input files based on format type.

        Returns:
            Tuple of (is_valid, validation_results)
        """
        if self.format_type == 'variant':
            results = self._validate_variant_inputs()
        else:
            results = self._validate_hero_inputs()

        results['errors'] = self.errors
        results['warnings'] = self.warnings

        is_valid = len(self.errors) == 0
        return is_valid, results

    def _validate_variant_inputs(self) -> Dict:
        """Validate content variant input files."""
        return {
            'template': self._validate_template(),
            'metadata': self._validate_variant_metadata(),
            'constraints': self._validate_variant_constraints(),
        }

    def _validate_hero_inputs(self) -> Dict:
        """Validate hero generator input files."""
        return {
            'metadata': self._validate_hero_metadata(),
            'prompt_template': self._validate_prompt_template(),
            'validation_rules': self._validate_validation_rules(),
            'example_html': self._validate_example_html(),
        }

    def _validate_template(self) -> Dict:
        """Validate template.html for variants."""
        template_path = self.input_dir / 'template.html'

        if not template_path.exists():
            self.errors.append("template.html not found")
            return {'valid': False, 'path': None}

        try:
            with open(template_path, 'r') as f:
                html_content = f.read()

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Check for Text Service placeholder pattern: {element_id_field}
            # More strict pattern to avoid CSS variables like {--color}
            placeholders = re.findall(r'\{([a-z][a-z0-9_]*)\}', html_content, re.IGNORECASE)

            if not placeholders:
                self.warnings.append("No placeholders found in template.html")

            # Check for invalid patterns
            invalid_patterns = re.findall(r'\{[^a-z}][^}]*\}', html_content, re.IGNORECASE)
            if invalid_patterns:
                self.warnings.append(
                    f"Found non-standard placeholders: {invalid_patterns[:5]}"
                )

            # Check file size
            file_size = template_path.stat().st_size
            if file_size > 500_000:  # 500KB
                self.warnings.append(f"template.html is large ({file_size} bytes)")

            # Check for inline styles (recommended for Text Service)
            has_inline_styles = bool(soup.find(attrs={'style': True}))
            if not has_inline_styles:
                self.warnings.append(
                    "No inline styles found. Text Service templates should use inline styles."
                )

            return {
                'valid': True,
                'path': str(template_path),
                'size': file_size,
                'placeholders': len(placeholders),
                'unique_placeholders': len(set(placeholders)),
                'has_inline_styles': has_inline_styles
            }

        except Exception as e:
            self.errors.append(f"Error reading template.html: {e}")
            return {'valid': False, 'error': str(e)}

    def _validate_variant_metadata(self) -> Dict:
        """Validate metadata.json for variants."""
        metadata_path = self.input_dir / 'metadata.json'

        if not metadata_path.exists():
            self.errors.append("metadata.json not found")
            return {'valid': False, 'path': None}

        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            # Check required fields
            missing_fields = []
            for field in self.REQUIRED_VARIANT_METADATA:
                if field not in metadata:
                    missing_fields.append(field)

            if missing_fields:
                self.errors.append(f"metadata.json missing required fields: {missing_fields}")

            # Validate variant_id format (snake_case)
            if 'variant_id' in metadata:
                variant_id = metadata['variant_id']
                if not re.match(r'^[a-z][a-z0-9_]*$', variant_id):
                    self.errors.append(
                        f"variant_id '{variant_id}' should be snake_case (lowercase, underscores)"
                    )

            # Validate slide_type
            if 'slide_type' in metadata:
                slide_type = metadata['slide_type']
                if slide_type not in self.VALID_SLIDE_TYPES:
                    self.warnings.append(
                        f"slide_type '{slide_type}' not in known types: {self.VALID_SLIDE_TYPES}"
                    )

            # Validate elements array
            if 'elements' in metadata:
                elements = metadata['elements']
                if not isinstance(elements, list):
                    self.errors.append("elements must be an array")
                else:
                    for i, elem in enumerate(elements):
                        if 'element_id' not in elem:
                            self.errors.append(f"Element {i} missing element_id")
                        if 'element_type' not in elem:
                            self.warnings.append(f"Element {i} missing element_type")
                        if 'required_fields' not in elem:
                            self.warnings.append(f"Element {i} missing required_fields")

            # Validate layout
            if 'layout' in metadata:
                layout = metadata['layout']
                if not isinstance(layout, dict):
                    self.errors.append("layout must be an object")

            return {
                'valid': len([e for e in self.errors if 'metadata.json' in e]) == 0,
                'path': str(metadata_path),
                'variant_id': metadata.get('variant_id'),
                'slide_type': metadata.get('slide_type'),
                'elements': len(metadata.get('elements', []))
            }

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in metadata.json: {e}")
            return {'valid': False, 'error': str(e)}
        except Exception as e:
            self.errors.append(f"Error reading metadata.json: {e}")
            return {'valid': False, 'error': str(e)}

    def _validate_variant_constraints(self) -> Dict:
        """Validate constraints.json for variants (optional)."""
        constraints_path = self.input_dir / 'constraints.json'

        if not constraints_path.exists():
            # Optional file
            self.warnings.append(
                "constraints.json not found. Will auto-generate baseline constraints."
            )
            return {'valid': True, 'optional': True, 'path': None}

        try:
            with open(constraints_path, 'r') as f:
                constraints = json.load(f)

            # Validate constraint format (Text Service style)
            # Format: { "element_id": { "field": { "baseline": N, "min": N, "max": N } } }
            total_constraints = 0

            for element_id, fields in constraints.items():
                if not isinstance(fields, dict):
                    self.errors.append(f"Invalid format for element '{element_id}'")
                    continue

                for field_name, limits in fields.items():
                    if not isinstance(limits, dict):
                        self.errors.append(
                            f"Invalid constraint format for {element_id}.{field_name}"
                        )
                        continue

                    # Check for required keys
                    if 'baseline' not in limits:
                        self.warnings.append(
                            f"Missing 'baseline' for {element_id}.{field_name}"
                        )
                    if 'min' not in limits or 'max' not in limits:
                        self.warnings.append(
                            f"Missing 'min' or 'max' for {element_id}.{field_name}"
                        )

                    total_constraints += 1

            return {
                'valid': len([e for e in self.errors if 'constraints.json' in e]) == 0,
                'path': str(constraints_path),
                'elements': len(constraints),
                'total_constraints': total_constraints
            }

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in constraints.json: {e}")
            return {'valid': False, 'error': str(e)}
        except Exception as e:
            self.errors.append(f"Error reading constraints.json: {e}")
            return {'valid': False, 'error': str(e)}

    def _validate_hero_metadata(self) -> Dict:
        """Validate metadata.json for hero generators."""
        metadata_path = self.input_dir / 'metadata.json'

        if not metadata_path.exists():
            self.errors.append("metadata.json not found")
            return {'valid': False, 'path': None}

        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            # Check required fields
            missing_fields = []
            for field in self.REQUIRED_HERO_METADATA:
                if field not in metadata:
                    missing_fields.append(field)

            if missing_fields:
                self.errors.append(f"metadata.json missing required fields: {missing_fields}")

            # Validate hero_type format (snake_case)
            if 'hero_type' in metadata:
                hero_type = metadata['hero_type']
                if not re.match(r'^[a-z][a-z0-9_]*$', hero_type):
                    self.errors.append(
                        f"hero_type '{hero_type}' should be snake_case"
                    )

            # Validate endpoint_path format (kebab-case)
            if 'endpoint_path' in metadata:
                endpoint = metadata['endpoint_path']
                if not re.match(r'^[a-z][a-z0-9-]*$', endpoint):
                    self.errors.append(
                        f"endpoint_path '{endpoint}' should be kebab-case"
                    )

            # Validate html_structure
            if 'html_structure' in metadata:
                structure = metadata['html_structure']
                if not isinstance(structure, dict):
                    self.errors.append("html_structure must be an object")

            # Validate character_constraints
            if 'character_constraints' in metadata:
                constraints = metadata['character_constraints']
                if not isinstance(constraints, dict):
                    self.errors.append("character_constraints must be an object")
                else:
                    for field, limits in constraints.items():
                        if 'min' not in limits or 'max' not in limits:
                            self.warnings.append(
                                f"character_constraints.{field} should have min and max"
                            )

            return {
                'valid': len([e for e in self.errors if 'metadata.json' in e]) == 0,
                'path': str(metadata_path),
                'hero_type': metadata.get('hero_type'),
                'endpoint_path': metadata.get('endpoint_path'),
                'display_name': metadata.get('display_name')
            }

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in metadata.json: {e}")
            return {'valid': False, 'error': str(e)}
        except Exception as e:
            self.errors.append(f"Error reading metadata.json: {e}")
            return {'valid': False, 'error': str(e)}

    def _validate_prompt_template(self) -> Dict:
        """Validate prompt_template.md for hero generators."""
        prompt_path = self.input_dir / 'prompt_template.md'

        if not prompt_path.exists():
            self.errors.append("prompt_template.md not found")
            return {'valid': False, 'path': None}

        try:
            with open(prompt_path, 'r') as f:
                content = f.read()

            # Check for minimum content
            if len(content) < 100:
                self.warnings.append("prompt_template.md seems too short")

            # Check for template variables
            template_vars = re.findall(r'\{(\w+)\}', content)
            expected_vars = ['narrative', 'topics', 'theme', 'audience']
            missing_vars = [v for v in expected_vars if v not in template_vars]

            if missing_vars:
                self.warnings.append(
                    f"prompt_template.md missing common variables: {missing_vars}"
                )

            # Check for section headers
            has_headers = bool(re.search(r'^#+\s', content, re.MULTILINE))
            if not has_headers:
                self.warnings.append(
                    "prompt_template.md has no markdown headers. Consider adding structure."
                )

            return {
                'valid': True,
                'path': str(prompt_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'template_vars': len(template_vars)
            }

        except Exception as e:
            self.errors.append(f"Error reading prompt_template.md: {e}")
            return {'valid': False, 'error': str(e)}

    def _validate_validation_rules(self) -> Dict:
        """Validate validation_rules.json for hero generators."""
        rules_path = self.input_dir / 'validation_rules.json'

        if not rules_path.exists():
            self.errors.append("validation_rules.json not found")
            return {'valid': False, 'path': None}

        try:
            with open(rules_path, 'r') as f:
                rules = json.load(f)

            # Check for required sections
            expected_sections = ['required_elements', 'character_limits', 'forbidden_patterns']
            missing_sections = [s for s in expected_sections if s not in rules]

            if missing_sections:
                self.warnings.append(
                    f"validation_rules.json missing sections: {missing_sections}"
                )

            # Validate required_elements format
            if 'required_elements' in rules:
                elements = rules['required_elements']
                if not isinstance(elements, list):
                    self.errors.append("required_elements must be an array")

            # Validate character_limits format
            if 'character_limits' in rules:
                limits = rules['character_limits']
                if not isinstance(limits, dict):
                    self.errors.append("character_limits must be an object")

            # Validate forbidden_patterns format
            if 'forbidden_patterns' in rules:
                patterns = rules['forbidden_patterns']
                if not isinstance(patterns, list):
                    self.errors.append("forbidden_patterns must be an array")

            return {
                'valid': len([e for e in self.errors if 'validation_rules.json' in e]) == 0,
                'path': str(rules_path),
                'required_elements': len(rules.get('required_elements', [])),
                'character_limits': len(rules.get('character_limits', {})),
                'forbidden_patterns': len(rules.get('forbidden_patterns', []))
            }

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in validation_rules.json: {e}")
            return {'valid': False, 'error': str(e)}
        except Exception as e:
            self.errors.append(f"Error reading validation_rules.json: {e}")
            return {'valid': False, 'error': str(e)}

    def _validate_example_html(self) -> Dict:
        """Validate example_html.html (optional)."""
        example_path = self.input_dir / 'example_html.html'

        if not example_path.exists():
            return {'valid': True, 'optional': True, 'path': None}

        try:
            with open(example_path, 'r') as f:
                html_content = f.read()

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            return {
                'valid': True,
                'path': str(example_path),
                'size': len(html_content)
            }

        except Exception as e:
            self.warnings.append(f"Error reading example_html.html: {e}")
            return {'valid': False, 'error': str(e)}

    def get_summary(self) -> str:
        """Get validation summary as formatted string."""
        lines = []

        lines.append("Validation Summary:")
        lines.append(f"  Format type: {self.format_type}")
        lines.append(f"  Errors: {len(self.errors)}")
        lines.append(f"  Warnings: {len(self.warnings)}")

        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  {error}")

        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  {warning}")

        return '\n'.join(lines)


def validate_input_directory(input_dir: Path, format_type: str) -> Tuple[bool, Dict]:
    """
    Convenience function to validate input directory.

    Args:
        input_dir: Path to input directory
        format_type: 'variant' or 'hero'

    Returns:
        Tuple of (is_valid, validation_results)
    """
    validator = InputValidator(input_dir, format_type)
    return validator.validate_all()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python input_validator.py <input_directory> <variant|hero>")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    format_type = sys.argv[2]

    if format_type not in ['variant', 'hero']:
        print("Format type must be 'variant' or 'hero'")
        sys.exit(1)

    validator = InputValidator(input_dir, format_type)
    is_valid, results = validator.validate_all()

    print(validator.get_summary())
    print(f"\nOverall valid: {is_valid}")

    if not is_valid:
        sys.exit(1)
