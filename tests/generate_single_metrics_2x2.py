#!/usr/bin/env python3
"""
Generate ONLY metrics_2x2_grid with updated specifications
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

def generate_single_metrics_2x2():
    """Generate ONLY metrics_2x2_grid and publish as single-slide presentation."""

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    print(f"\n{'='*70}")
    print(f"Generating UPDATED metrics_2x2_grid")
    print(f"{'='*70}")
    print(f"\nChanges Applied:")
    print(f"  ✓ H3 heading: 29px (matches slide 2)")
    print(f"  ✓ Bullet text: 20px (matches slide 2)")
    print(f"  ✓ Text box height: Matches bottom of cards (height: 105%)")
    print(f"  ✓ Bullets: 8 bullets (was 5)")
    print(f"  ✓ Char count: 44-55 chars per bullet (was 40-50)")
    print(f"\n{'='*70}\n")

    variant_id = "metrics_2x2_grid"
    title = "Core KPIs Overview"
    description = "Display 4 core metrics (left side) with 8-bullet insights (right side)"

    slide_spec = {
        "slide_title": title,
        "slide_purpose": description,
        "key_message": "Strategic insights with comprehensive key takeaways",
        "tone": "professional",
        "audience": "executive stakeholders"
    }

    presentation_spec = {
        "presentation_title": "Metrics 2×2 Grid - UPDATED",
        "presentation_type": "Executive KPI Dashboard",
        "current_slide_number": 1,
        "total_slides": 1
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
        output_file = Path(f"test_output_{variant_id}_FINAL.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ Saved locally to: {output_file}")

        # Create slide for Railway
        slide = {
            "layout": "L25",
            "content": {
                "slide_title": title,
                "subtitle": "Variant: metrics_2x2_grid - UPDATED",
                "rich_content": html,
                "presentation_name": "Metrics 2×2 Grid - UPDATED",
                "logo": ""
            }
        }

        # Publish to Railway
        print(f"\n{'='*70}")
        print(f"Publishing to Railway...")
        print(f"{'='*70}")

        presentation_payload = {
            "title": "Metrics 2×2 Grid - UPDATED (Single Slide)",
            "slides": [slide]
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

            print(f"\n{'='*70}")
            print("✅ SUCCESS!")
            print(f"{'='*70}\n")
            print(f"🌐 VIEW UPDATED METRICS 2×2 GRID:")
            print(f"   {url}\n")
            print(f"Updated Specifications:")
            print(f"  • H3 Heading: 29px (matches metrics_4col)")
            print(f"  • Bullet Text: 20px (matches metrics_4col)")
            print(f"  • Text Box Height: Extended to match card bottoms")
            print(f"  • Total Bullets: 8 (increased from 5)")
            print(f"  • Char Count: 44-55 per bullet (+10%)")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_single_metrics_2x2()
