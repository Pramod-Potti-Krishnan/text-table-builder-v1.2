"""
Generate test slides for all 4 metrics variants and publish to Railway.

This script:
1. Generates HTML for each of the 4 metrics variants
2. Publishes all 4 slides to the layout service on Railway
3. Returns the presentation URL for validation
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.element_based_generator import ElementBasedContentGenerator
from app.core.llm_client import get_llm_client
import requests


async def generate_metrics_slides():
    """Generate all 4 metrics variant slides."""

    # Initialize LLM client
    llm_client = get_llm_client()

    # Create synchronous wrapper for LLM service
    def llm_service(prompt: str) -> str:
        """Synchronous wrapper that runs async LLM generation."""
        # Run the async operation in the current event loop
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(llm_client.generate(prompt))
        return response.content

    # Initialize generator
    generator = ElementBasedContentGenerator(
        llm_service=llm_service,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    # Define test scenarios for each variant
    test_scenarios = [
        {
            "variant_id": "metrics_3col",
            "slide_spec": {
                "slide_title": "Q4 Performance Highlights",
                "slide_purpose": "Present key performance metrics from Q4",
                "key_message": "Strong growth across all key metrics",
                "tone": "professional",
                "audience": "executive stakeholders"
            },
            "presentation_spec": {
                "presentation_title": "Q4 Business Review",
                "presentation_type": "Business Quarterly Review",
                "current_slide_number": 5,
                "total_slides": 20
            }
        },
        {
            "variant_id": "metrics_4col",
            "slide_spec": {
                "slide_title": "Annual Growth Metrics",
                "slide_purpose": "Show year-over-year growth across key metrics",
                "key_message": "Consistent growth and customer satisfaction",
                "tone": "professional",
                "audience": "board of directors"
            },
            "presentation_spec": {
                "presentation_title": "Annual Performance Report",
                "presentation_type": "Annual Review",
                "current_slide_number": 8,
                "total_slides": 25
            }
        },
        {
            "variant_id": "metrics_3x2_grid",
            "slide_spec": {
                "slide_title": "Business Performance Dashboard",
                "slide_purpose": "Comprehensive view of all key business metrics",
                "key_message": "Healthy growth across all operational areas",
                "tone": "professional",
                "audience": "management team"
            },
            "presentation_spec": {
                "presentation_title": "Monthly Business Review",
                "presentation_type": "Monthly Dashboard",
                "current_slide_number": 3,
                "total_slides": 15
            }
        },
        {
            "variant_id": "metrics_2x2_grid",
            "slide_spec": {
                "slide_title": "Core KPIs Overview",
                "slide_purpose": "Present the most critical business KPIs with insights",
                "key_message": "Strong performance with clear action items",
                "tone": "professional",
                "audience": "executive team"
            },
            "presentation_spec": {
                "presentation_title": "Executive Dashboard",
                "presentation_type": "Executive Summary",
                "current_slide_number": 2,
                "total_slides": 10
            }
        }
    ]

    generated_slides = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*80}")
        print(f"Generating Slide {i}/4: {scenario['variant_id']}")
        print(f"{'='*80}")

        try:
            # Generate slide content
            result = await generator.generate_slide_content(
                variant_id=scenario["variant_id"],
                slide_spec=scenario["slide_spec"],
                presentation_spec=scenario["presentation_spec"]
            )

            print(f"✅ Generated {scenario['variant_id']}")
            print(f"   Elements: {len(result['elements'])}")
            print(f"   HTML length: {len(result['html'])} characters")

            # Save locally for inspection
            output_file = Path(f"test_output_{scenario['variant_id']}.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['html'])
            print(f"   Saved to: {output_file}")

            generated_slides.append({
                "slide_title": scenario["slide_spec"]["slide_title"],
                "rich_content": result['html'],
                "layout_id": "L25",  # All metrics slides use L25
                "variant_id": scenario['variant_id']
            })

        except Exception as e:
            print(f"❌ Error generating {scenario['variant_id']}: {e}")
            import traceback
            traceback.print_exc()
            continue

    return generated_slides


async def publish_to_railway(slides):
    """Publish slides to Railway layout service."""

    print(f"\n{'='*80}")
    print(f"Publishing {len(slides)} slides to Railway...")
    print(f"{'='*80}")

    # Railway layout service URL
    LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

    # Transform slides to v7.5 format
    formatted_slides = []
    for slide in slides:
        formatted_slides.append({
            "layout": "L25",
            "content": {
                "slide_title": slide["slide_title"],
                "subtitle": f"Variant: {slide['variant_id']}",
                "rich_content": slide["rich_content"]
            }
        })

    # Create presentation payload in v7.5 format
    presentation_data = {
        "title": "Metrics Layouts Showcase - Updated",
        "slides": formatted_slides
    }

    try:
        # Post to layout service
        response = requests.post(
            f"{LAYOUT_SERVICE_URL}/api/presentations",
            json=presentation_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            presentation_id = result.get("id")
            presentation_url = f"{LAYOUT_SERVICE_URL}{result.get('url')}"

            print(f"\n✅ SUCCESS! Presentation published to Railway")
            print(f"\n{'='*80}")
            print(f"🎉 PRESENTATION URL:")
            print(f"   {presentation_url}")
            print(f"{'='*80}\n")

            return presentation_url
        else:
            print(f"❌ Failed to publish: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error publishing to Railway: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Main execution."""
    print("\n" + "="*80)
    print("METRICS TEMPLATES TEST GENERATION")
    print("="*80)
    print("\nGenerating test slides for:")
    print("  1. metrics_3col (3 cards + 4 bullets)")
    print("  2. metrics_4col (4 cards + 4 bullets)")
    print("  3. metrics_3x2_grid (6 cards, no insights)")
    print("  4. metrics_2x2_grid (4 cards side-by-side with 5 bullet insights)")
    print("\n" + "="*80 + "\n")

    # Generate slides
    slides = await generate_metrics_slides()

    if not slides:
        print("\n❌ No slides generated. Exiting.")
        return

    print(f"\n✅ Successfully generated {len(slides)} slides")

    # Publish to Railway
    url = await publish_to_railway(slides)

    if url:
        print("\n" + "="*80)
        print("✅ ALL TASKS COMPLETED")
        print("="*80)
        print(f"\nPresentation URL: {url}")
        print("\nReview the slides and provide feedback for platinum approval!")
        print("="*80 + "\n")
    else:
        print("\n❌ Failed to publish to Railway")
        print("Local HTML files saved for inspection")


if __name__ == "__main__":
    asyncio.run(main())
