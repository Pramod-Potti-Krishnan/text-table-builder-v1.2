#!/usr/bin/env python3
"""
Generate all 4 UPDATED metrics layouts (with feedback incorporated) and publish as a single presentation
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
    """Generate 4 UPDATED metrics slides and publish as one presentation."""

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
            "description": "Display 3 key metrics with vibrant gradient cards and 4-bullet insights"
        },
        {
            "variant_id": "metrics_4col",
            "title": "Annual Growth Metrics",
            "description": "Display 4 key metrics with gradient cards (reduced font) and 4 insights bullets"
        },
        {
            "variant_id": "metrics_3x2_grid",
            "title": "Business Performance Dashboard",
            "description": "Display 6 metrics in 3x2 grid format (NO insights box - removed)"
        },
        {
            "variant_id": "metrics_2x2_grid",
            "title": "Core KPIs Overview",
            "description": "Display 4 core metrics (left side) with 5-bullet insights (right side)"
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
            "presentation_title": "Metrics Layouts Showcase - UPDATED",
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
                    "presentation_name": "Metrics Layouts Showcase - UPDATED",
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
    print(f"Publishing {len(slides)} UPDATED metrics slides as ONE presentation...")
    print(f"{'='*70}")

    presentation_payload = {
        "title": "Metrics Layouts Showcase - UPDATED (4 Types)",
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
            print(f"🌐 VIEW ALL 4 UPDATED METRICS SLIDES:")
            print(f"   {url}\n")
            print(f"Updated Slides (Feedback Incorporated):")
            print(f"  1. Metrics 3 Col - Converted to 4 bullets (reduced spacing)")
            print(f"  2. Metrics 4 Col - 10% reduced metric font size")
            print(f"  3. Metrics 3×2 Grid - Insights box REMOVED (cards to top)")
            print(f"  4. Metrics 2×2 Grid - Side-by-side layout (cards left, 5 bullets right)")
            print(f"\n{'='*70}\n")
            print("Changes Applied:")
            print("  ✓ Metrics 3col: 4 bullets (90-100 chars), reduced line spacing")
            print("  ✓ Metrics 4col: Metric numbers reduced from 86px to 77px")
            print("  ✓ Metrics 3x2: Insights box removed, cards moved to top")
            print("  ✓ Metrics 2x2: Cards 80% width left, insights 20% width right")
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
