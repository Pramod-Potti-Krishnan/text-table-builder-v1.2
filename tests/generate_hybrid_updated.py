#!/usr/bin/env python3
"""
Generate UPDATED hybrid layout variants with all changes:
- Hybrid Top 2x2: No top padding, text box with bold highlights for key points
- Hybrid Left 2x2: No top padding, 7 bullets (65-70 chars each)
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

def generate_and_publish_hybrid_updated():
    """Generate 2 UPDATED hybrid slides and publish as one presentation."""

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
            "description": "Display 4 key components in a 2x2 grid (top) with supporting context text (bottom). Use <strong> tags to highlight 2-3 key phrases in the text box.",
            "additional_instructions": "In the text_box_content, wrap 2-3 important phrases or key points with <strong> tags for emphasis. Example: '<strong>critical success factor</strong>' or '<strong>strategic advantage</strong>'"
        },
        {
            "variant_id": "hybrid_left_2x2",
            "title": "Solution Architecture",
            "description": "Display 4 core capabilities in a 2x2 grid (left) with 7 concise bullet points (right). Use <strong> tags to highlight key terms in bullets.",
            "additional_instructions": "In the bullet points, wrap 1-2 important words or key terms with <strong> tags for emphasis. Example: '<strong>Enhanced security</strong>' or 'Provides <strong>real-time monitoring</strong>'"
        }
    ]

    slides = []

    for i, layout_info in enumerate(hybrid_layouts, 1):
        variant_id = layout_info["variant_id"]
        title = layout_info["title"]
        description = layout_info["description"]
        additional = layout_info.get("additional_instructions", "")

        print(f"\n{'='*70}")
        print(f"Generating UPDATED {i}/2: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Hybrid layout combining visual grid structure with supporting narrative",
            "tone": "professional",
            "audience": "business stakeholders"
        }

        if additional:
            slide_spec["additional_instructions"] = additional

        presentation_spec = {
            "presentation_title": "Hybrid Layouts - UPDATED",
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
            output_file = Path(f"test_output_{variant_id}_updated.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✓ Saved locally to: {output_file}")

            # Add to slides array
            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": title,
                    "subtitle": f"Variant: {variant_id} - UPDATED",
                    "rich_content": html,
                    "presentation_name": "Hybrid Layouts - UPDATED",
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
    print(f"Publishing {len(slides)} UPDATED hybrid slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Hybrid Layouts - UPDATED (2 Variants)",
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
            print(f"🌐 VIEW BOTH UPDATED HYBRID LAYOUTS:")
            print(f"   {url}\n")
            print(f"UPDATED Hybrid Layout Specifications:")
            print(f"  1. Hybrid Top 2×2 - Grid on top, text box at bottom")
            print(f"     • No top padding (padding: 0 40px 40px 40px)")
            print(f"     • 4 boxes: 25 chars heading, 135 chars description (+50%)")
            print(f"     • Text box: 300 chars with <strong> tags for key phrases")
            print(f"  2. Hybrid Left 2×2 - Grid on left, 7 bullets on right")
            print(f"     • No top padding (padding: 0 40px 40px 40px)")
            print(f"     • 4 boxes: 25 chars heading, 135 chars description (+50%)")
            print(f"     • 7 bullets: 65-70 chars each (68 baseline)")
            print(f"\n{'='*70}\n")
            print("ALL Changes Applied:")
            print("  ✓ Removed top padding from both layouts")
            print("  ✓ Box descriptions increased by 50% (90 → 135 chars)")
            print("  ✓ hybrid_top_2x2: Text box with bold highlights for emphasis")
            print("  ✓ hybrid_left_2x2: Converted to 7 bullet format (65-70 chars)")
            print("  ✓ Both layouts use <strong> tags for key terms/phrases")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_and_publish_hybrid_updated()
