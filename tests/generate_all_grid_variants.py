#!/usr/bin/env python3
"""
Generate All 9 Grid Variants for Review
"""
import sys
import os
import requests
from pathlib import Path

# Disable model routing via environment variable
os.environ["ENABLE_MODEL_ROUTING"] = "false"

sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable

LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

ALL_GRID_VARIANTS = {
    # Centered variants (35% extended content)
    "grid_2x3": "Grid 2×3 Centered - 6 Boxes with Icons",
    "grid_3x2": "Grid 3×2 Centered - 6 Boxes with Icons (Vertical)",
    "grid_2x2_centered": "Grid 2×2 Centered - 4 Boxes with Icons",

    # Left-aligned variants (70% extended content)
    "grid_2x3_left": "Grid 2×3 Left-Aligned - 6 Boxes with Icons",
    "grid_3x2_left": "Grid 3×2 Left-Aligned - 6 Boxes with Icons (Vertical)",
    "grid_2x2_left": "Grid 2×2 Left-Aligned - 4 Boxes with Icons",

    # Numbered variants (70% extended content)
    "grid_2x3_numbered": "Grid 2×3 Numbered - 6 Boxes with Sequential Numbers",
    "grid_3x2_numbered": "Grid 3×2 Numbered - 6 Boxes with Sequential Numbers (Vertical)",
    "grid_2x2_numbered": "Grid 2×2 Numbered - 4 Boxes with Sequential Numbers"
}

def main():
    print("=" * 80)
    print("ALL 9 GRID VARIANTS - Flash Model Only")
    print("=" * 80)

    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    slides = []

    for i, (variant_id, description) in enumerate(ALL_GRID_VARIANTS.items(), 1):
        print(f"\n[{i}/9] Generating: {variant_id}")

        slide_spec = {
            "slide_title": description,
            "slide_purpose": f"Visual review of {variant_id} layout",
            "key_message": "Grid layout demonstration with proper styling and content",
            "tone": "professional",
            "audience": "stakeholders"
        }

        try:
            result = generator.generate_slide_content(
                variant_id=variant_id,
                slide_spec=slide_spec
            )

            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": description,
                    "subtitle": f"Variant: {variant_id}",
                    "rich_content": result["html"],
                    "presentation_name": "All 9 Grid Variants Review",
                    "company_logo": ""
                }
            }

            slides.append(slide)
            print(f"    ✓ Generated successfully")

        except Exception as e:
            print(f"    ✗ Error: {str(e)[:200]}")

    if not slides:
        print("\n❌ No slides generated")
        return

    # Post to Railway
    print("\n" + "=" * 80)
    print(f"Posting {len(slides)} grid templates to Railway...")
    print("=" * 80)

    presentation = {
        "title": "All 9 Grid Variants - Complete Migration Review",
        "slides": slides
    }

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

        print("\n" + "=" * 80)
        print("✅ SUCCESS! All 9 Grid Variants Published")
        print("=" * 80)
        print(f"\n🌐 VIEW URL:")
        print(f"   {view_url}")
        print(f"\nGenerated: {len(slides)}/9 templates")
        print("\n" + "=" * 80)
    else:
        print(f"\n❌ Failed: {response.status_code}")

if __name__ == "__main__":
    main()
