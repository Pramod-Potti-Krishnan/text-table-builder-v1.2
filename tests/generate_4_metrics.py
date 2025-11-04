#!/usr/bin/env python3
"""
Generate all 4 metrics layouts and publish as a single presentation
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

def generate_and_publish_metrics():
    """Generate 4 metrics slides and publish as one presentation."""

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Metrics layouts to generate
    metrics = [
        {
            "variant_id": "metrics_3col",
            "title": "Q4 Performance Highlights",
            "description": "Display 3 key metrics with vibrant gradient cards and insights box"
        },
        {
            "variant_id": "metrics_4col",
            "title": "Annual Growth Metrics",
            "description": "Display 4 key metrics with gradient cards and insights summary"
        },
        {
            "variant_id": "metrics_3x2_grid",
            "title": "Business Performance Dashboard",
            "description": "Display 6 metrics in 3x2 grid format with insights box"
        },
        {
            "variant_id": "metrics_2x2_grid",
            "title": "Core KPIs Overview",
            "description": "Display 4 core metrics in 2x2 grid with insights box"
        }
    ]

    slides = []

    for i, metric_info in enumerate(metrics, 1):
        variant_id = metric_info["variant_id"]
        title = metric_info["title"]
        description = metric_info["description"]

        print(f"\n{'='*70}")
        print(f"Generating {i}/4: {variant_id} - {title}")
        print(f"{'='*70}")

        slide_spec = {
            "slide_title": title,
            "slide_purpose": description,
            "key_message": "Impact metrics with visual gradient cards",
            "tone": "professional",
            "audience": "executive stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Metrics Layouts Showcase",
            "presentation_type": "Data Visualization Gallery",
            "current_slide_number": i,
            "total_slides": len(metrics)
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
                    "presentation_name": "Metrics Layouts Showcase",
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
    print(f"Publishing {len(slides)} metrics slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Metrics Layouts Showcase - All 4 Metrics Types",
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
            print(f"🌐 VIEW ALL 4 METRICS SLIDES:")
            print(f"   {url}\n")
            print(f"Published slides:")
            print(f"  1. Metrics 3 Columns - Q4 Performance Highlights")
            print(f"  2. Metrics 4 Columns - Annual Growth Metrics")
            print(f"  3. Metrics 3×2 Grid - Business Performance Dashboard")
            print(f"  4. Metrics 2×2 Grid - Core KPIs Overview")
            print(f"\n{'='*70}\n")
            print("Metrics Features:")
            print("  ✓ Vibrant gradient cards (purple, pink, blue, cyan, orange)")
            print("  ✓ Large bold numbers (86px-115px)")
            print("  ✓ Uppercase labels with letter spacing")
            print("  ✓ Key Insights box with grey border")
            print("  ✓ Soft box shadows for depth")
            print(f"\n{'='*70}\n")

        else:
            print(f"\n❌ Failed to publish: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_and_publish_metrics()
