#!/usr/bin/env python3
"""
Generate and publish all 3 single_column layouts
Uses direct import pattern (not HTTP API)
"""

import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable

RAILWAY_URL = "https://web-production-f0d13.up.railway.app"

def generate_and_publish_single_column():
    """Generate 3 single_column slides and publish as one presentation."""

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Single column layouts to generate
    single_column_layouts = [
        {
            "variant_id": "single_column_3section",
            "title": "Digital Transformation Framework",
            "description": "Present 3 key strategic pillars for digital transformation, each with 4 detailed implementation points",
        },
        {
            "variant_id": "single_column_4section",
            "title": "Implementation Roadmap",
            "description": "Outline 4 critical phases of the transformation journey, each with 3 key deliverables and milestones",
        },
        {
            "variant_id": "single_column_5section",
            "title": "Success Metrics & KPIs",
            "description": "Define 5 essential measurement categories for tracking transformation progress, each with 2 core indicators",
        }
    ]

    slides = []

    for i, layout_info in enumerate(single_column_layouts, 1):
        variant_id = layout_info["variant_id"]
        title = layout_info["title"]
        description = layout_info["description"]

        print(f"\n{'='*70}")
        print(f"Generating {i}/3: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Structured presentation of key information with clear section headings and concise bullet points",
            "tone": "professional",
            "audience": "business stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Single Column Layouts - Digital Transformation",
            "presentation_type": "Layout Gallery",
            "current_slide_number": i,
            "total_slides": len(single_column_layouts)
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
                    "presentation_name": "Single Column Layouts",
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
    print(f"Publishing {len(slides)} single column slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Single Column Layouts (3 Variants)",
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
            print(f"🌐 VIEW ALL 3 SINGLE COLUMN LAYOUTS:")
            print(f"   {url}\n")
            print(f"Single Column Layout Specifications:")
            print(f"  1. Single Column 3-Section - 3 sections × 4 bullets each")
            print(f"     • Heading: 20 chars (19-21 range)")
            print(f"     • Bullets: 105 chars each (100-110 range)")
            print(f"     • Total: 12 bullets across 3 sections")
            print(f"  2. Single Column 4-Section - 4 sections × 3 bullets each")
            print(f"     • Heading: 20 chars (19-21 range)")
            print(f"     • Bullets: 105 chars each (100-110 range)")
            print(f"     • Total: 12 bullets across 4 sections")
            print(f"  3. Single Column 5-Section - 5 sections × 2 bullets each")
            print(f"     • Heading: 20 chars (19-21 range)")
            print(f"     • Bullets: 105 chars each (100-110 range)")
            print(f"     • Total: 10 bullets across 5 sections")
            print(f"\n{'='*70}\n")
            print("Layout Features:")
            print("  ✓ Full-width single column layout (zero padding)")
            print("  ✓ Colored section headings (Blue → Red → Green → Amber → Purple)")
            print("  ✓ Horizontal gradient rules under each heading")
            print("  ✓ Consistent bullet styling with disc markers")
            print("  ✓ Optimal for sequential information presentation")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_and_publish_single_column()
