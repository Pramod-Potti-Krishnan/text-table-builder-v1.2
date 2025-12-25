#!/usr/bin/env python3
"""
Test C1 Slides - Mixed Variants

Generates 6 C1 slides:
- 4 from different variant categories (grid, comparison, sequential, metrics)
- 2 additional variants (table, asymmetric)

Calls Text Service on Railway, assembles in Layout Service, returns URL.

Usage:
    python3 test_c1_mixed_variants.py
"""

import requests
import json
import time

# Service URLs
TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

# 6 variants from different categories
TEST_VARIANTS = [
    # 4 from different categories
    {
        "variant_id": "grid_2x3",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Our Core Capabilities",
            "slide_purpose": "Present six key capabilities of our platform",
            "key_message": "Comprehensive solution for modern businesses",
            "tone": "professional",
            "audience": "executives"
        }
    },
    {
        "variant_id": "comparison_3col",
        "category": "Comparison",
        "slide_spec": {
            "slide_title": "Plan Comparison",
            "slide_purpose": "Compare three pricing tiers",
            "key_message": "Find the right plan for your needs",
            "tone": "professional",
            "audience": "potential customers"
        }
    },
    {
        "variant_id": "sequential_4col",
        "category": "Sequential",
        "slide_spec": {
            "slide_title": "Implementation Roadmap",
            "slide_purpose": "Show the four phases of project implementation",
            "key_message": "Clear path from planning to deployment",
            "tone": "professional",
            "audience": "project stakeholders"
        }
    },
    {
        "variant_id": "metrics_3col",
        "category": "Metrics",
        "slide_spec": {
            "slide_title": "Key Performance Indicators",
            "slide_purpose": "Highlight three critical metrics",
            "key_message": "Measurable results that matter",
            "tone": "professional",
            "audience": "business leaders"
        }
    },
    # 2 additional variants
    {
        "variant_id": "table_3col",
        "category": "Table",
        "slide_spec": {
            "slide_title": "Feature Comparison Matrix",
            "slide_purpose": "Compare features across product versions",
            "key_message": "Detailed feature breakdown",
            "tone": "professional",
            "audience": "technical buyers"
        }
    },
    {
        "variant_id": "asymmetric_8_4_3section",
        "category": "Asymmetric",
        "slide_spec": {
            "slide_title": "Market Analysis Overview",
            "slide_purpose": "Present market insights with supporting details",
            "key_message": "Data-driven market understanding",
            "tone": "professional",
            "audience": "investors"
        }
    }
]


def generate_slide(variant_config):
    """Call Text Service to generate slide content."""
    url = f"{TEXT_SERVICE_URL}/v1.2/generate"

    payload = {
        "variant_id": variant_config["variant_id"],
        "slide_spec": variant_config["slide_spec"],
        "presentation_spec": {
            "presentation_title": "C1 Mixed Variants Test",
            "presentation_type": "Test Presentation"
        }
    }

    print(f"  Calling Text Service for {variant_config['variant_id']}...")

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # LLM calls can take time
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Error: {response.status_code}")
            print(f"  Response: {response.text[:300]}")
            return None

    except Exception as e:
        print(f"  Exception: {str(e)}")
        return None


def create_presentation_slide(variant_config, text_service_result):
    """Convert Text Service result to Layout Service slide format."""
    return {
        "layout": "C1-text",
        "content": {
            "slide_title": variant_config["slide_spec"]["slide_title"],
            "subtitle": f"Category: {variant_config['category']} | Variant: {variant_config['variant_id']}",
            "body": text_service_result.get("html", ""),
            "footer_text": "C1 Mixed Variants Test",
            "logo": ""
        }
    }


def post_to_layout_service(slides):
    """Post slides to Layout Service and return URL."""
    url = f"{LAYOUT_SERVICE_URL}/api/presentations"

    presentation = {
        "title": "C1 Mixed Variants Test - Generated via Text Service",
        "slides": slides
    }

    print(f"\nPosting {len(slides)} slides to Layout Service...")

    try:
        response = requests.post(
            url,
            json=presentation,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code in [200, 201]:
            data = response.json()
            presentation_id = data.get("id")
            url_path = data.get("url", f"/p/{presentation_id}")
            view_url = f"{LAYOUT_SERVICE_URL}{url_path}"
            return view_url
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None

    except Exception as e:
        print(f"Exception: {str(e)}")
        return None


def main():
    print("=" * 80)
    print("C1 Mixed Variants Test")
    print("=" * 80)
    print(f"Text Service: {TEXT_SERVICE_URL}")
    print(f"Layout Service: {LAYOUT_SERVICE_URL}")
    print("=" * 80)

    slides = []
    successful = 0
    failed = 0

    for i, variant_config in enumerate(TEST_VARIANTS, 1):
        print(f"\n[{i}/6] {variant_config['category']}: {variant_config['variant_id']}")

        # Generate via Text Service
        result = generate_slide(variant_config)

        if result and result.get("html"):
            slide = create_presentation_slide(variant_config, result)
            slides.append(slide)
            successful += 1
            html_len = len(result.get("html", ""))
            print(f"  Success! HTML: {html_len} chars")
        else:
            failed += 1
            print(f"  Failed to generate")

    print("\n" + "=" * 80)
    print(f"Generation Complete: {successful}/6 successful, {failed} failed")
    print("=" * 80)

    if not slides:
        print("\nNo slides generated. Exiting.")
        return

    # Post to Layout Service
    view_url = post_to_layout_service(slides)

    if view_url:
        print("\n" + "=" * 80)
        print("SUCCESS! Presentation Created")
        print("=" * 80)
        print(f"\nVIEW URL:")
        print(f"  {view_url}")
        print("\n" + "=" * 80)
        print("\nUse arrow keys to navigate slides")
        print("Press 'G' for grid overlay, 'B' for borders")
        print("=" * 80)
    else:
        print("\nFailed to create presentation in Layout Service")


if __name__ == "__main__":
    main()
