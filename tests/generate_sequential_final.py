#!/usr/bin/env python3
"""
Generate all 3 FINAL sequential layouts with ALL feedback incorporated:
- 4 sentences per column (reduced from 5)
- Char counts: 3col -15% (101-111), 4col -5% (90-100), 5col -15% (66-72)
- Left-aligned sentences
- Vertical dividers: Start 15% after sentence start, end 15% before sentence end
- Gap increased 2x: 24px → 48px
- Dividers centered between columns
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

def generate_and_publish_sequential_final():
    """Generate 3 FINAL sequential slides and publish as one presentation."""

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Sequential layouts to generate
    sequential_layouts = [
        {
            "variant_id": "sequential_3col",
            "title": "Our Strategic Process",
            "description": "Display 3 sequential steps with numbered badges, titles, and 4 detailed sentences per step"
        },
        {
            "variant_id": "sequential_4col",
            "title": "Implementation Framework",
            "description": "Display 4 sequential phases with numbered badges, titles, and 4 sentences per phase"
        },
        {
            "variant_id": "sequential_5col",
            "title": "5-Stage Journey",
            "description": "Display 5 sequential stages with numbered badges, concise titles, and 4 sentences per stage"
        }
    ]

    slides = []

    for i, layout_info in enumerate(sequential_layouts, 1):
        variant_id = layout_info["variant_id"]
        title = layout_info["title"]
        description = layout_info["description"]

        print(f"\n{'='*70}")
        print(f"Generating FINAL {i}/3: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Sequential process visualization with comprehensive step descriptions",
            "tone": "professional",
            "audience": "business stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Sequential Layouts - FINAL",
            "presentation_type": "Process Visualization Gallery",
            "current_slide_number": i,
            "total_slides": len(sequential_layouts)
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
            output_file = Path(f"test_output_{variant_id}_final.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✓ Saved locally to: {output_file}")

            # Add to slides array
            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": title,
                    "subtitle": f"Variant: {variant_id} - FINAL",
                    "rich_content": html,
                    "presentation_name": "Sequential Layouts - FINAL",
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
    print(f"Publishing {len(slides)} FINAL sequential slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Sequential Layouts - FINAL (3 Variants)",
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
            print(f"🌐 VIEW ALL 3 FINAL SEQUENTIAL SLIDES:")
            print(f"   {url}\n")
            print(f"FINAL Specifications:")
            print(f"  1. Sequential 3 Col - 3 steps, 4 sentences (101-111 chars, -15%)")
            print(f"  2. Sequential 4 Col - 4 steps, 4 sentences (90-100 chars, -5%)")
            print(f"  3. Sequential 5 Col - 5 steps, 4 sentences (66-72 chars, -15%)")
            print(f"\n{'='*70}\n")
            print("ALL Changes Applied:")
            print("  ✓ Reduced from 5 to 4 sentences per column")
            print("  ✓ 3col: Char count reduced by 15% (125→106 baseline)")
            print("  ✓ 4col: Char count reduced by 5% (100→95 baseline)")
            print("  ✓ 5col: Char count reduced by 15% (81→69 baseline)")
            print("  ✓ Sentences left-aligned (was center)")
            print("  ✓ Gap between columns increased 2x (24px→48px)")
            print("  ✓ Vertical dividers positioned with 15% offset from sentence area")
            print("  ✓ Dividers centered between columns (dead center)")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_and_publish_sequential_final()
