#!/usr/bin/env python3
"""
Generate and save the 3 comparison layouts
"""
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Disable model routing
os.environ["ENABLE_MODEL_ROUTING"] = "false"

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable

def update_template_paths():
    """Update the template paths in comparison specs to point to multilateral_comparison folder."""
    specs_dir = Path("app/variant_specs/comparison")

    for spec_file in specs_dir.glob("*.json"):
        with open(spec_file, 'r') as f:
            spec = json.load(f)

        # Update template path
        variant_id = spec["variant_id"]
        spec["template_path"] = f"app/templates/multilateral_comparison/{variant_id}.html"

        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)

        print(f"✓ Updated {spec_file.name}")

def main():
    print("=" * 70)
    print("GENERATING 3 COMPARISON LAYOUTS")
    print("=" * 70)

    # Update template paths first
    print("\nUpdating template paths...")
    update_template_paths()

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Templates to generate
    templates = [
        ("comparison_2col", "Comparison 2 Columns - Traditional vs Digital Marketing"),
        ("comparison_3col", "Comparison 3 Columns - Startup Growth Stages"),
        ("comparison_4col", "Comparison 4 Columns - Product Tier Comparison")
    ]

    output_dir = Path("generated_templates")
    output_dir.mkdir(exist_ok=True)

    for variant_id, description in templates:
        print(f"\n{'='*70}")
        print(f"Generating: {variant_id}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": description,
            "slide_purpose": f"Compare different options or categories using {variant_id.split('_')[1]} layout",
            "key_message": "Clear comparison of distinct categories with detailed bullet points",
            "tone": "professional",
            "audience": "executive stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Comparison Layouts Showcase",
            "presentation_type": "Template Gallery",
            "current_slide_number": 1,
            "total_slides": 3
        }

        try:
            result = generator.generate_slide_content(
                variant_id=variant_id,
                slide_spec=slide_spec,
                presentation_spec=presentation_spec
            )

            # Save HTML
            html_file = output_dir / f"{variant_id}.html"
            with open(html_file, 'w') as f:
                f.write(result["html"])

            print(f"✓ Saved to {html_file}")
            print(f"  Content preview:")

            # Show a preview of generated content
            html_content = result["html"]
            if "column_1_heading" in html_content:
                print(f"    ⚠ Warning: Placeholders not replaced!")
            else:
                print(f"    ✓ Content successfully generated")

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*70}")
    print(f"✅ Templates saved to: {output_dir}/")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
