"""
Variant Generator for Text Service CLI

Generates all files needed to integrate a new content slide variant:
- Variant spec JSON (app/variant_specs/{slide_type}/{variant_id}.json)
- HTML template (app/templates/{slide_type}/{variant_id}.html)
- Test script (tests/test_{variant_id}.py)
- Index update snippet (for variant_index.json)

Uses Jinja2 templates for code generation.
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, Template

from core.placeholder_detector import PlaceholderDetector
from core.spec_analyzer import SpecAnalyzer


class VariantGenerator:
    """
    Generates integration files for new content slide variants.
    """

    def __init__(self, service_root: Path, templates_dir: Path):
        """
        Initialize generator.

        Args:
            service_root: Path to Text Service v1.2 root
            templates_dir: Path to Jinja2 templates directory
        """
        self.service_root = Path(service_root)
        self.templates_dir = Path(templates_dir)

        # Set up Jinja2 environment
        template_path = self.templates_dir / 'variant'
        if template_path.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_path)),
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.jinja_env = None

    def generate_all(
        self,
        metadata: Dict,
        constraints: Dict,
        template_html: str
    ) -> Dict[str, str]:
        """
        Generate all integration files.

        Args:
            metadata: Variant metadata from metadata.json
            constraints: Character constraints from constraints.json
            template_html: HTML template content

        Returns:
            Dict mapping file paths to generated content
        """
        generated_files = {}

        # Analyze template
        detector = PlaceholderDetector()
        analysis = detector.detect_placeholders(template_html)

        # Build complete variant spec
        analyzer = SpecAnalyzer()
        variant_spec = analyzer.suggest_variant_spec(analysis, metadata)

        # Merge user-provided constraints
        if constraints:
            variant_spec = self._merge_constraints(variant_spec, constraints)

        # 1. Generate variant spec JSON
        variant_id = metadata['variant_id']
        slide_type = metadata['slide_type']

        spec_path = f"app/variant_specs/{slide_type}/{variant_id}.json"
        generated_files[spec_path] = self._generate_variant_spec_json(variant_spec)

        # 2. Copy/process HTML template
        template_path = f"app/templates/{slide_type}/{variant_id}.html"
        generated_files[template_path] = self._process_template(template_html)

        # 3. Generate test script
        test_path = f"tests/test_{variant_id}.py"
        generated_files[test_path] = self._generate_test_script(
            variant_spec, metadata, analysis
        )

        # 4. Generate index update snippet (stored as internal marker)
        generated_files['_index_update'] = self._generate_index_update(metadata)

        return generated_files

    def _generate_variant_spec_json(self, variant_spec: Dict) -> str:
        """Generate formatted variant spec JSON."""
        return json.dumps(variant_spec, indent=2)

    def _process_template(self, template_html: str) -> str:
        """
        Process HTML template for Text Service.

        Ensures:
        - Full container with width/height 100%
        - Inline styles preserved
        - Clean formatting
        """
        # Basic cleanup
        template = template_html.strip()

        # Ensure container has full dimensions if not present
        if 'width: 100%' not in template and 'width:100%' not in template:
            # Try to add to outermost div
            template = re.sub(
                r'(<div[^>]*style=["\'])([^"\']*)(["\')',
                r'\1width: 100%; height: 100%; \2\3',
                template,
                count=1
            )

        return template

    def _generate_test_script(
        self,
        variant_spec: Dict,
        metadata: Dict,
        analysis: Dict
    ) -> str:
        """Generate test script for the variant."""
        variant_id = metadata['variant_id']
        slide_type = metadata['slide_type']
        display_name = metadata.get('display_name', variant_id)

        # Generate sample data for test
        detector = PlaceholderDetector()
        sample_content = detector.generate_sample_content(analysis)

        # Build test script
        test_script = f'''#!/usr/bin/env python3
"""
Integration test for {display_name} variant.

Tests:
- Variant spec loading
- Element generation
- Template assembly
- Character count validation

Run with:
    python3 tests/test_{variant_id}.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


# Test configuration
API_BASE_URL = "http://localhost:8000"
VARIANT_ID = "{variant_id}"
SLIDE_TYPE = "{slide_type}"
OUTPUT_FILE = "test_outputs/test_{variant_id}_output.html"


async def test_{variant_id.replace("-", "_")}():
    """Test {display_name} variant generation."""
    print(f"Testing {display_name} ({variant_id})")
    print("=" * 60)

    # Test request payload
    payload = {{
        "variant_id": VARIANT_ID,
        "slide_spec": {{
            "slide_title": "Test {display_name}",
            "slide_purpose": "Demonstrate {variant_id} layout",
            "key_message": "This is a test of the {variant_id} variant",
            "tone": "professional",
            "audience": "general business audience"
        }},
        "presentation_spec": {{
            "presentation_title": "Test Presentation",
            "presentation_type": "Business Presentation",
            "current_slide_number": 1,
            "total_slides": 10
        }},
        "enable_parallel": True,
        "validate_character_counts": True
    }}

    print(f"\\nRequest payload:")
    print(json.dumps(payload, indent=2))

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{{API_BASE_URL}}/v1.2/generate",
                json=payload
            )

            if response.status_code != 200:
                print(f"\\nError: Status {{response.status_code}}")
                print(response.text)
                return False

            result = response.json()

            # Display results
            print(f"\\nResponse:")
            print(f"  Success: {{result.get('success')}}")
            print(f"  Elements generated: {{len(result.get('elements', []))}}")

            # Show element details
            print(f"\\nElements:")
            for elem in result.get('elements', []):
                print(f"  - {{elem.get('element_id')}}: {{elem.get('element_type')}}")
                char_counts = elem.get('character_counts', {{}})
                for field, count in char_counts.items():
                    print(f"      {{field}}: {{count}} chars")

            # Show validation
            validation = result.get('validation', {{}})
            print(f"\\nValidation:")
            print(f"  Valid: {{validation.get('valid')}}")
            if validation.get('violations'):
                print(f"  Violations: {{validation.get('violations')}}")

            # Save HTML output
            html_content = result.get('html', '')
            if html_content:
                output_path = Path(OUTPUT_FILE)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(html_content)
                print(f"\\nHTML saved to: {{OUTPUT_FILE}}")
                print(f"  Size: {{len(html_content)}} characters")

            print("\\n" + "=" * 60)
            print("Test PASSED" if result.get('success') else "Test FAILED")

            return result.get('success', False)

    except httpx.ConnectError:
        print(f"\\nError: Could not connect to {{API_BASE_URL}}")
        print("Make sure the Text Service is running:")
        print("  python3 main.py")
        return False
    except Exception as e:
        print(f"\\nError: {{e}}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_{variant_id.replace("-", "_")}())
    sys.exit(0 if success else 1)
'''

        return test_script

    def _generate_index_update(self, metadata: Dict) -> str:
        """Generate snippet for updating variant_index.json."""
        variant_id = metadata['variant_id']
        slide_type = metadata['slide_type']
        display_name = metadata.get('display_name', variant_id)

        snippet = f'''
# Add to variant_index.json:

# In "slide_types" > "{slide_type}" > "variants" array, add:
"{variant_id}"

# In "variant_lookup", add:
"{variant_id}": "{slide_type}"

# Example complete entry in slide_types:
{{
  "slide_type": "{slide_type}",
  "display_name": "{display_name}",
  "variants": [
    // ... existing variants ...
    "{variant_id}"
  ]
}}
'''
        return snippet

    def _merge_constraints(
        self,
        variant_spec: Dict,
        constraints: Dict
    ) -> Dict:
        """
        Merge user-provided constraints into variant spec.

        Args:
            variant_spec: Generated variant spec
            constraints: User-provided constraints

        Returns:
            Updated variant spec
        """
        for element in variant_spec.get('elements', []):
            element_id = element['element_id']

            if element_id in constraints:
                element['character_requirements'] = constraints[element_id]

        return variant_spec

    def _to_class_name(self, snake_case: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in snake_case.split('_'))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python variant_gen.py <input_dir>")
        sys.exit(1)

    input_dir = Path(sys.argv[1])

    with open(input_dir / 'metadata.json') as f:
        metadata = json.load(f)

    with open(input_dir / 'template.html') as f:
        template_html = f.read()

    constraints = {}
    constraints_path = input_dir / 'constraints.json'
    if constraints_path.exists():
        with open(constraints_path) as f:
            constraints = json.load(f)

    # Use current directory as service root for testing
    generator = VariantGenerator(
        Path.cwd().parent,
        Path(__file__).parent.parent / 'templates'
    )

    files = generator.generate_all(metadata, constraints, template_html)

    print(f"Generated {len(files)} files:")
    for path in files:
        if not path.startswith('_'):
            print(f"  {path}")
