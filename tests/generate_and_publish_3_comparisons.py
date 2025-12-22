#!/usr/bin/env python3
"""
Generate 3 comparison layouts and publish to Railway with colored bullets
"""
import sys
import os
import json
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

def generate_and_publish():
    """Generate 3 comparison slides and publish to Railway."""

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
            "description": "Compare traditional and digital marketing approaches with detailed characteristics"
        },
        {
            "variant_id": "comparison_3col",
            "title": "Startup Growth Stages",
            "description": "Compare three critical stages of startup growth: Seed, Growth, and Scale"
        },
        {
            "variant_id": "comparison_4col",
            "title": "Product Tier Comparison",
            "description": "Compare four product tiers: Basic, Standard, Premium, and Enterprise"
        }
    ]

    results = []

    for template_info in templates:
        variant_id = template_info["variant_id"]
        title = template_info["title"]
        description = template_info["description"]

        print(f"\n{'='*70}")
        print(f"Generating: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Clear comparison with colored bullet markers",
            "tone": "professional",
            "audience": "executive stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Comparison Layouts with Colored Bullets",
            "presentation_type": "Template Showcase",
            "current_slide_number": len(results) + 1,
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

            # Publish to Railway using v7.5 API format
            print(f"Publishing to Railway...")

            # Create presentation with single slide
            presentation_payload = {
                "title": f"Comparison: {title}",
                "slides": [
                    {
                        "layout": "L25",
                        "content": {
                            "slide_title": title,
                            "subtitle": f"Colored bullets - {variant_id}",
                            "rich_content": html,
                            "presentation_name": "Comparison Layouts Showcase",
                            "logo": ""
                        }
                    }
                ]
            }

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

                results.append({
                    "variant_id": variant_id,
                    "title": title,
                    "url": url,
                    "presentation_id": presentation_id
                })

                print(f"✓ Published successfully!")
                print(f"  URL: {url}")
            else:
                print(f"✗ Failed to publish: {response.status_code}")
                print(f"  Response: {response.text}")

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

    # Print summary
    print(f"\n{'='*70}")
    print("✅ COMPARISON LAYOUTS WITH COLORED BULLETS")
    print(f"{'='*70}\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Variant: {result['variant_id']}")
        print(f"   URL: {result['url']}")
        print()

    print("Features:")
    print("  ✓ Colored bullet markers (blue, red, green, purple)")
    print("  ✓ Black bullet text (#1f2937)")
    print("  ✓ H3 headers at 32px (reduced from 36px)")
    print("  ✓ Updated spacing and character counts")
    print("  ✓ CSS ::before pseudo-elements for bullets")
    print()

    return results

if __name__ == "__main__":
    generate_and_publish()
