#!/usr/bin/env python3
"""
Generate all 3 REVISED sequential layouts with:
- 25% longer sentences
- 5 sentences per column
- Light grey vertical dividers between columns
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

def generate_and_publish_sequential_revised():
    """Generate 3 REVISED sequential slides and publish as one presentation."""

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
            "description": "Display 3 sequential steps with numbered badges, titles, and 5 detailed sentences per step"
        },
        {
            "variant_id": "sequential_4col",
            "title": "Implementation Framework",
            "description": "Display 4 sequential phases with numbered badges, titles, and 5 sentences per phase"
        },
        {
            "variant_id": "sequential_5col",
            "title": "5-Stage Journey",
            "description": "Display 5 sequential stages with numbered badges, concise titles, and 5 sentences per stage"
        }
    ]

    slides = []

    for i, layout_info in enumerate(sequential_layouts, 1):
        variant_id = layout_info["variant_id"]
        title = layout_info["title"]
        description = layout_info["description"]

        print(f"\n{'='*70}")
        print(f"Generating REVISED {i}/3: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Sequential process visualization with comprehensive step descriptions",
            "tone": "professional",
            "audience": "business stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Sequential Layouts - REVISED",
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
            output_file = Path(f"test_output_{variant_id}_revised.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✓ Saved locally to: {output_file}")

            # Add to slides array
            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": title,
                    "subtitle": f"Variant: {variant_id} - REVISED",
                    "rich_content": html,
                    "presentation_name": "Sequential Layouts - REVISED",
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
    print(f"Publishing {len(slides)} REVISED sequential slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Sequential Layouts - REVISED (3 Variants)",
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
            print(f"🌐 VIEW ALL 3 REVISED SEQUENTIAL SLIDES:")
            print(f"   {url}\n")
            print(f"REVISED Specifications:")
            print(f"  1. Sequential 3 Col - 3 steps, 5 sentences each (119-131 chars)")
            print(f"  2. Sequential 4 Col - 4 steps, 5 sentences each (95-105 chars)")
            print(f"  3. Sequential 5 Col - 5 steps, 5 sentences each (78-85 chars)")
            print(f"\n{'='*70}\n")
            print("Changes Applied:")
            print("  ✓ Sentences increased by 25% in character count")
            print("  ✓ Changed from 2 paragraphs to 5 individual sentences per step")
            print("  ✓ Added light grey vertical dividers (50% height, centered)")
            print("  ✓ Dividers positioned between columns for visual separation")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_and_publish_sequential_revised()
