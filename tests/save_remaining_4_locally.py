#!/usr/bin/env python3
"""
Generate and save the remaining 4 grid templates locally
"""
import sys
import os
import json
from pathlib import Path

# Disable model routing
os.environ["ENABLE_MODEL_ROUTING"] = "false"

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable


def main():
    print("=" * 70)
    print("GENERATING AND SAVING 4 TEMPLATES LOCALLY")
    print("=" * 70)

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Templates to generate
    templates = [
        ("grid_2x3_left", "Grid 2×3 Left-Aligned - 50% Gap Reduction"),
        ("grid_2x3_numbered", "Grid 2×3 Numbered - 25% Char Increase"),
        ("grid_3x2_numbered", "Grid 3×2 Numbered - 25% Char Increase"),
        ("grid_2x2_numbered", "Grid 2×2 Numbered - 25% Char Increase")
    ]

    output_dir = Path("generated_templates")
    output_dir.mkdir(exist_ok=True)

    for variant_id, description in templates:
        print(f"\nGenerating: {variant_id}")

        slide_spec = {
            "slide_title": description,
            "slide_purpose": f"Demonstrate {variant_id} layout with professional content",
            "key_message": "Professional grid layout for business presentations",
            "tone": "professional",
            "audience": "executive stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Grid Templates Showcase",
            "presentation_type": "Template Gallery",
            "current_slide_number": 1,
            "total_slides": 4
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

            print(f"  ✓ Saved to {html_file}")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"\n{'='*70}")
    print(f"✅ Templates saved to: {output_dir}/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
