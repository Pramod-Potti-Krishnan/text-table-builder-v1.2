#!/usr/bin/env python3
"""
Generate both hybrid layout variants with sample content:
- Hybrid Top 2x2: Grid on top, text box at bottom
- Hybrid Left 2x2: Grid on left, text box on right
"""
import sys
import os
import requests
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

RAILWAY_URL = "https://web-production-f0d13.up.railway.app"

def generate_and_publish_hybrid():
    """Generate 2 hybrid slides and publish as one presentation."""

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Hybrid layouts to generate
    hybrid_layouts = [
        {
            "variant_id": "hybrid_top_2x2",
            "title": "Strategic Framework Overview",
            "description": "Display 4 key components in a 2x2 grid (top) with supporting context text (bottom)"
        },
        {
            "variant_id": "hybrid_left_2x2",
            "title": "Solution Architecture",
            "description": "Display 4 core capabilities in a 2x2 grid (left) with detailed explanation text (right)"
        }
    ]

    slides = []

    for i, layout_info in enumerate(hybrid_layouts, 1):
        variant_id = layout_info["variant_id"]
        title = layout_info["title"]
        description = layout_info["description"]

        print(f"\n{'='*70}")
        print(f"Generating {i}/2: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Hybrid layout combining visual grid structure with supporting narrative",
            "tone": "professional",
            "audience": "business stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Hybrid Layouts Preview",
            "presentation_type": "Layout Gallery",
            "current_slide_number": i,
            "total_slides": len(hybrid_layouts)
        }

        try:
            # Generate slide
            result = generator.generate_slide_content(
                variant_id=variant_id,
                slide_spec=slide_spec,
                presentation_spec=presentation_spec
            )

            html = result["html"]

            # Save locally for inspection
            output_file = Path(f"test_output_{variant_id}.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✓ Saved locally to: {output_file}")

            # Add to slides array
            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": title,
                    "subtitle": f"Variant: {variant_id}",
                    "rich_content": html,
                    "presentation_name": "Hybrid Layouts Preview",
                    "logo": ""
                }
            }
            slides.append(slide)
            print(f"✓ Generated successfully")

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

    if not slides:
        print("\n❌ No slides generated")
        return

    # Publish all slides as one presentation
    print(f"\n{'='*70}")
    print(f"Publishing {len(slides)} hybrid slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Hybrid Layouts Preview (2 Variants)",
        "slides": slides
    }

    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/presentations",
            json=presentation_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code in [200, 201]:
            data = response.json()
            presentation_id = data.get("id")
            url_path = data.get("url", f"/p/{presentation_id}")
            url = f"{RAILWAY_URL}{url_path}"

            print(f"\n{'='*70}")
            print("✅ SUCCESS!")
            print(f"{'='*70}\n")
            print(f"🌐 VIEW BOTH HYBRID LAYOUTS:")
            print(f"   {url}\n")
            print(f"Hybrid Layout Specifications:")
            print(f"  1. Hybrid Top 2×2 - Grid on top, text box at bottom")
            print(f"     • 4 boxes: 25 chars heading, 90 chars description")
            print(f"     • Text box: 300 chars (center-aligned)")
            print(f"  2. Hybrid Left 2×2 - Grid on left, text box on right")
            print(f"     • 4 boxes: 25 chars heading, 90 chars description")
            print(f"     • Text box: 450 chars (left-aligned)")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_and_publish_hybrid()
