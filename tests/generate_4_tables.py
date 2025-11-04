#!/usr/bin/env python3
"""
Generate all 4 table layouts and publish as a single presentation
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

def generate_and_publish_tables():
    """Generate 4 table slides and publish as one presentation."""

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Table layouts to generate
    tables = [
        {
            "variant_id": "table_2col",
            "title": "Product Comparison: Features vs Benefits",
            "description": "Compare product features across 5 key categories with 2-column layout"
        },
        {
            "variant_id": "table_3col",
            "title": "Service Tiers: Basic, Pro, Enterprise",
            "description": "Compare three service tiers across 5 dimensions with 3-column layout"
        },
        {
            "variant_id": "table_4col",
            "title": "Quarterly Performance: Q1-Q4",
            "description": "Display quarterly performance metrics across 4 quarters with 4-column layout"
        },
        {
            "variant_id": "table_5col",
            "title": "Team Comparison: 5 Departments",
            "description": "Compare 5 departments across key metrics with 5-column layout"
        }
    ]

    slides = []

    for i, table_info in enumerate(tables, 1):
        variant_id = table_info["variant_id"]
        title = table_info["title"]
        description = table_info["description"]

        print(f"\n{'='*70}")
        print(f"Generating {i}/4: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Clear data presentation in table format",
            "tone": "professional",
            "audience": "executive stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Table Layouts Showcase",
            "presentation_type": "Data Tables Gallery",
            "current_slide_number": i,
            "total_slides": len(tables)
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
                    "presentation_name": "Table Layouts Showcase",
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
    print(f"Publishing {len(slides)} table slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Table Layouts Showcase - All 4 Table Types",
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
            print(f"🌐 VIEW ALL 4 TABLE SLIDES:")
            print(f"   {url}\n")
            print(f"Published slides:")
            print(f"  1. Table 2 Columns - Product Features vs Benefits")
            print(f"  2. Table 3 Columns - Service Tiers (Basic, Pro, Enterprise)")
            print(f"  3. Table 4 Columns - Quarterly Performance (Q1-Q4)")
            print(f"  4. Table 5 Columns - Team Comparison (5 Departments)")
            print(f"\n{'='*70}\n")
            print("Table Features:")
            print("  ✓ Professional gradient headers (purple → blue)")
            print("  ✓ Alternating row colors for readability")
            print("  ✓ Bold category labels")
            print("  ✓ Responsive column widths")
            print("  ✓ Clean border styling")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_and_publish_tables()
