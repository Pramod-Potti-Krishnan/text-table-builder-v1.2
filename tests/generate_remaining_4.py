#!/usr/bin/env python3
"""
Generate the remaining 4 grid templates:
- grid_2x3_left (with 50% gap reduction)
- grid_2x3_numbered (with 25% char increase)
- grid_3x2_numbered (with 25% char increase)
- grid_2x2_numbered (with 25% char increase)
"""
import sys
import os
import requests
from pathlib import Path

# Disable model routing
os.environ["ENABLE_MODEL_ROUTING"] = "false"

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable
import time

LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"


def generate_template(generator, variant_id, description):
    """Generate a single template."""
    print(f"\n{'='*70}")
    print(f"Generating: {variant_id}")
    print(f"Description: {description}")
    print('='*70)

    slide_spec = {
        "slide_title": f"Template: {variant_id}",
        "slide_purpose": description,
        "key_message": "Demonstrating the grid layout with professional content",
        "tone": "professional",
        "audience": "executive stakeholders"
    }

    presentation_spec = {
        "presentation_title": "Grid Templates Showcase",
        "presentation_type": "Template Gallery",
        "current_slide_number": 1,
        "total_slides": 9
    }

    try:
        result = generator.generate_slide_content(
            variant_id=variant_id,
            slide_spec=slide_spec,
            presentation_spec=presentation_spec
        )
        print(f"✓ {variant_id} generated successfully")
        return result
    except Exception as e:
        print(f"✗ {variant_id} failed: {e}")
        return None


def main():
    print("=" * 70)
    print("GENERATING REMAINING 4 GRID TEMPLATES")
    print("=" * 70)

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates",
        enable_parallel=True,
        max_workers=5
    )

    # Templates to generate
    templates = [
        ("grid_2x3_left", "2x3 grid left-aligned layout with 50% reduced gap"),
        ("grid_2x3_numbered", "2x3 grid numbered layout with 25% increased character count"),
        ("grid_3x2_numbered", "3x2 grid numbered layout with 25% increased character count"),
        ("grid_2x2_numbered", "2x2 grid numbered layout with 25% increased character count")
    ]

    results = {}
    for variant_id, description in templates:
        result = generate_template(generator, variant_id, description)
        if result:
            results[variant_id] = result
        time.sleep(2)  # Small delay between generations

    print("\n" + "=" * 70)
    print("PUBLISHING TO RAILWAY")
    print("=" * 70)

    # Publish all successful results
    if results:
        slides = []
        template_names = {
            "grid_2x3_left": "Grid 2×3 Left-Aligned - 50% Gap Reduction",
            "grid_2x3_numbered": "Grid 2×3 Numbered - 25% Char Increase",
            "grid_3x2_numbered": "Grid 3×2 Numbered - 25% Char Increase",
            "grid_2x2_numbered": "Grid 2×2 Numbered - 25% Char Increase"
        }

        for variant_id, result in results.items():
            slide = {
                "variant_id": variant_id,
                "content": {
                    "slide_title": template_names.get(variant_id, variant_id),
                    "subtitle": f"Variant: {variant_id}",
                    "rich_content": result["html"],
                    "presentation_name": "Remaining 4 Grid Templates - With Fixes",
                    "logo": ""
                }
            }
            slides.append(slide)

        presentation = {
            "title": "Remaining 4 Grid Templates - With Fixes",
            "slides": slides
        }

        # Post to layout service
        response = requests.post(
            f"{LAYOUT_SERVICE_URL}/api/presentations",
            json=presentation,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code in [200, 201]:
            data = response.json()
            presentation_id = data.get("id")
            url_path = data.get("url", f"/p/{presentation_id}")
            view_url = f"{LAYOUT_SERVICE_URL}{url_path}"

            print(f"\n{'='*70}")
            print(f"✅ SUCCESS! Published {len(results)}/4 templates")
            print(f"{'='*70}")
            print(f"\n🌐 VIEW URL:")
            print(f"   {view_url}")
            print(f"\nGenerated: {len(results)}/4 templates")
            print(f"{'='*70}\n")
        else:
            print(f"\n❌ Publishing failed: {response.status_code}")
    else:
        print("\n❌ No templates generated successfully")


if __name__ == "__main__":
    main()
