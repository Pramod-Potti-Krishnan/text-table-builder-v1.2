#!/usr/bin/env python3
"""
Publish 3 comparison slides as a single presentation using existing HTML
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

def publish_all_3_slides():
    """Generate 3 comparison slides and publish as one presentation."""

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Templates to generate
    templates = [
        {
            "variant_id": "comparison_2col",
            "title": "Traditional vs Digital Marketing",
            "description": "Compare traditional and digital marketing approaches"
        },
        {
            "variant_id": "comparison_3col",
            "title": "Startup Growth Stages",
            "description": "Compare three critical stages of startup growth"
        },
        {
            "variant_id": "comparison_4col",
            "title": "Product Tier Comparison",
            "description": "Compare four product tiers with features"
        }
    ]

    slides = []

    for i, template_info in enumerate(templates, 1):
        variant_id = template_info["variant_id"]
        title = template_info["title"]
        description = template_info["description"]

        print(f"\n{'='*70}")
        print(f"Generating {i}/3: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Clear comparison with standard black bullets",
            "tone": "professional",
            "audience": "executive stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Comparison Layouts Showcase",
            "presentation_type": "Template Gallery",
            "current_slide_number": i,
            "total_slides": len(templates)
        }

        try:
            # Generate slide
            result = generator.generate_slide_content(
                variant_id=variant_id,
                slide_spec=slide_spec,
                presentation_spec=presentation_spec
            )

            html = result["html"]

            # Add to slides array
            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": title,
                    "subtitle": f"Variant: {variant_id}",
                    "rich_content": html,
                    "presentation_name": "Comparison Layouts Showcase",
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
    print(f"Publishing {len(slides)} slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Comparison Layouts Showcase - All 3 Variants",
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
            print(f"🌐 VIEW ALL 3 SLIDES:")
            print(f"   {url}\n")
            print(f"Published slides:")
            print(f"  1. Traditional vs Digital Marketing (comparison_2col)")
            print(f"  2. Startup Growth Stages (comparison_3col)")
            print(f"  3. Product Tier Comparison (comparison_4col)")
            print(f"\n{'='*70}\n")
            print("Features:")
            print("  ✓ H3 headers at 32px (reduced from 36px)")
            print("  ✓ Black bullets from LLM-generated HTML lists")
            print("  ✓ Updated spacing (2col: +20%, 4col: +12%)")
            print("  ✓ Updated character counts")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    publish_all_3_slides()
