#!/usr/bin/env python3
"""
Visual Validation Script for v1.2 - All 24 Variants

This script generates content for all 24 variants using real Gemini LLM
and posts them to the Railway layout service for visual validation.

Usage:
    export GCP_PROJECT_ID=deckster-xyz
    python3 visual_validation.py
"""

import sys
import os
import json
import requests
from pathlib import Path
from typing import Dict, List

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable

# Railway Layout Service URL
LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

# Variant descriptions for slide titles
VARIANT_DESCRIPTIONS = {
    "matrix_2x2": "Matrix 2×2 Layout - Four Equal Boxes",
    "matrix_2x3": "Matrix 2×3 Layout - Six Equal Boxes",
    "grid_2x3": "Grid 2×3 Layout - Title + Item Lists",
    "grid_3x2": "Grid 3×2 Layout - Title + Item Lists",
    "comparison_2col": "Comparison 2-Column Layout",
    "comparison_3col": "Comparison 3-Column Layout",
    "comparison_4col": "Comparison 4-Column Layout",
    "sequential_3col": "Sequential 3-Step Process",
    "sequential_4col": "Sequential 4-Step Process",
    "sequential_5col": "Sequential 5-Step Process",
    "asymmetric_8_4_3section": "Asymmetric Layout - 3 Sections + Sidebar",
    "asymmetric_8_4_4section": "Asymmetric Layout - 4 Sections + Sidebar",
    "asymmetric_8_4_5section": "Asymmetric Layout - 5 Sections + Sidebar",
    "hybrid_top_2x2": "Hybrid Layout - Grid Top, Text Bottom",
    "hybrid_left_2x2": "Hybrid Layout - Grid Left, Text Right",
    "metrics_3col": "Metrics 3-Column with Insights",
    "metrics_4col": "Metrics 4-Column with Key Insights",
    "metrics_3x2_grid": "Metrics 3×2 Grid with Insights",
    "metrics_2x2_grid": "Metrics 2×2 Large Cards",
    "impact_quote": "Customer Success Story - Bordered Quote",
    "table_2col": "Table 2-Column (Category + 1 Data)",
    "table_3col": "Table 3-Column (Category + 2 Data)",
    "table_4col": "Table 4-Column (Category + 3 Data)",
    "table_5col": "Table 5-Column (Category + 4 Data)",
}


def generate_all_variants():
    """Generate content for all 24 variants using Gemini."""
    print("=" * 80)
    print("Visual Validation - Generating All 24 Variants")
    print("=" * 80)

    # Check prerequisites
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("❌ GCP_PROJECT_ID not set")
        print("   Run: export GCP_PROJECT_ID=deckster-xyz")
        sys.exit(1)

    print(f"\n✓ GCP_PROJECT_ID: {project_id}")

    # Create generator with real Gemini LLM
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

    print(f"✓ Generator initialized with Gemini")

    # Generate content for each variant
    slides = []

    for i, (variant_id, description) in enumerate(VARIANT_DESCRIPTIONS.items(), 1):
        print(f"\n[{i}/24] Generating: {variant_id}")
        print(f"    Description: {description}")

        # Define slide spec for this variant
        slide_spec = {
            "slide_title": description,
            "slide_purpose": f"Visual validation of {variant_id} variant layout and content generation",
            "key_message": "This is a test slide to validate the layout structure, content generation, and visual appearance",
            "tone": "professional",
            "audience": "technical reviewers"
        }

        try:
            # Generate content
            result = generator.generate_slide_content(
                variant_id=variant_id,
                slide_spec=slide_spec
            )

            # Create slide for layout service
            slide = {
                "layout": "L25",  # Main content shell
                "content": {
                    "slide_title": description,
                    "subtitle": f"Variant: {variant_id}",
                    "rich_content": result["html"],
                    "presentation_name": "v1.2 Visual Validation",
                    "company_logo": ""
                }
            }

            slides.append(slide)

            print(f"    ✓ Generated ({len(result['html'])} chars)")

        except Exception as e:
            print(f"    ❌ Error: {e}")
            # Continue with other variants even if one fails

    return slides


def post_to_layout_service(slides: List[Dict]):
    """Post generated slides to Railway layout service."""
    print("\n" + "=" * 80)
    print("Posting to Layout Service")
    print("=" * 80)

    # Create presentation payload
    presentation = {
        "title": "v1.2 Visual Validation - All 24 Variants",
        "slides": slides
    }

    # POST to layout service
    url = f"{LAYOUT_SERVICE_URL}/api/presentations"

    print(f"\nPosting to: {url}")
    print(f"Slides: {len(slides)}")

    try:
        response = requests.post(
            url,
            json=presentation,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            presentation_id = data.get("id")
            view_url = f"{LAYOUT_SERVICE_URL}{data.get('url', f'/p/{presentation_id}')}"

            print("\n" + "=" * 80)
            print("✅ SUCCESS! Presentation Created")
            print("=" * 80)
            print(f"\nPresentation ID: {presentation_id}")
            print(f"\n🌐 VIEW URL:")
            print(f"   {view_url}")
            print("\n" + "=" * 80)

            return view_url

        else:
            print(f"\n❌ Failed to create presentation")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None

    except Exception as e:
        print(f"\n❌ Error posting to layout service: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("v1.2 Visual Validation Tool")
    print("Generates all 24 variants and creates Railway presentation")
    print("=" * 80)

    # Step 1: Generate all variants
    slides = generate_all_variants()

    if not slides:
        print("\n❌ No slides generated")
        sys.exit(1)

    print(f"\n✓ Generated {len(slides)}/24 variants successfully")

    # Step 2: Post to layout service
    view_url = post_to_layout_service(slides)

    if view_url:
        print("\n📋 Next Steps:")
        print(f"   1. Open the URL above in your browser")
        print(f"   2. Use arrow keys to navigate slides")
        print(f"   3. Validate each layout visually")
        print(f"   4. Check for content coherence and formatting")
        print(f"   5. Press 'G' for grid overlay, 'B' for borders")
        print("\n✅ Visual validation ready!")
    else:
        print("\n⚠️  Could not create presentation")
        print("    Slides generated but not uploaded")
        print("    Check layout service URL and try again")


if __name__ == "__main__":
    main()
