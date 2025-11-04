#!/usr/bin/env python3
"""
Generate all 3 COMPLETE sequential layouts with ALL feedback incorporated:
- 4 sentences per column (reduced from 5)
- Title char counts: 3col (26-29), 4col (22-23), 5col (17-19) [-10%]
- Sentence char counts: 3col (101-111), 4col (77-85), 5col (66-72)
- Center-aligned sentences
- No vertical dividers (removed)
- No top padding (padding: 0 40px 40px 40px)
- Gap increased 2x: 24px → 48px
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

def generate_and_publish_sequential_complete():
    """Generate 3 COMPLETE sequential slides and publish as one presentation."""

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
        print(f"Generating COMPLETE {i}/3: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Sequential process visualization with comprehensive step descriptions",
            "tone": "professional",
            "audience": "business stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Sequential Layouts - COMPLETE",
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
            output_file = Path(f"test_output_{variant_id}_complete.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✓ Saved locally to: {output_file}")

            # Add to slides array
            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": title,
                    "subtitle": f"Variant: {variant_id} - COMPLETE",
                    "rich_content": html,
                    "presentation_name": "Sequential Layouts - COMPLETE",
                    "company_logo": ""
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
    print(f"Publishing {len(slides)} COMPLETE sequential slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Sequential Layouts - COMPLETE (3 Variants)",
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
            print(f"🌐 VIEW ALL 3 COMPLETE SEQUENTIAL SLIDES:")
            print(f"   {url}\n")
            print(f"COMPLETE Specifications:")
            print(f"  1. Sequential 3 Col - 3 steps, 4 sentences")
            print(f"     • Title: 26-29 chars (27 baseline, -10%)")
            print(f"     • Sentences: 101-111 chars (106 baseline, -15%)")
            print(f"  2. Sequential 4 Col - 4 steps, 4 sentences")
            print(f"     • Title: 22-23 chars (22 baseline, -10%)")
            print(f"     • Sentences: 77-85 chars (81 baseline, -15% then -15%)")
            print(f"  3. Sequential 5 Col - 5 steps, 4 sentences")
            print(f"     • Title: 17-19 chars (18 baseline, -10%)")
            print(f"     • Sentences: 66-72 chars (69 baseline, -15%)")
            print(f"\n{'='*70}\n")
            print("ALL Changes Applied:")
            print("  ✓ Reduced from 5 to 4 sentences per column")
            print("  ✓ Title char counts reduced by 10% across all slides")
            print("  ✓ 3col: Sentence char count reduced by 15%")
            print("  ✓ 4col: Sentence char count reduced by 15% (twice: -5% then -15%)")
            print("  ✓ 5col: Sentence char count reduced by 15%")
            print("  ✓ Sentences center-aligned (as originally)")
            print("  ✓ Top padding removed (padding: 0 40px 40px 40px)")
            print("  ✓ Gap between columns increased 2x (24px→48px)")
            print("  ✓ Grey vertical dividers removed")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_and_publish_sequential_complete()
