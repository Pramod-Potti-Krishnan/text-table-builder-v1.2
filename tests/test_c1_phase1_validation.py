#!/usr/bin/env python3
"""
Test C1 Phase 1 Validation - 3 New C1 Spec Files
Date: 2025-12-23

Tests the 3 newly created C1 spec files:
1. metrics_4col_c1 - 4 metric cards with insights section
2. sequential_3col_c1 - 3 steps with 4 sentences each
3. grid_2x2_centered_c1 - 4 boxes with icon, title, description

Flow:
1. Call /v1.2/generate with each C1 variant_id
2. Collect all generated HTML
3. Post slides to Layout Service
4. Return viewable URL

Usage:
    python3 test_c1_phase1_validation.py
"""

import requests
import json
import time
from datetime import datetime

# Service URLs
TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

# Phase 1 Test Scenarios - 3 new C1 variants
PHASE1_TEST_SCENARIOS = [
    # 1. metrics_4col_c1
    {
        "variant_id": "metrics_4col_c1",
        "description": "4 Metric Cards with Insights (C1)",
        "slide_spec": {
            "slide_title": "Q4 2025 Performance Dashboard",
            "topics": ["Revenue Growth", "Customer Acquisition", "Product Quality", "Market Share"],
            "slide_purpose": "Present key business metrics with insights",
            "key_message": "Strong performance across all KPIs",
            "tone": "professional",
            "audience": "executives"
        }
    },

    # 2. sequential_3col_c1
    {
        "variant_id": "sequential_3col_c1",
        "description": "3-Step Process with 4 Sentences Each (C1)",
        "slide_spec": {
            "slide_title": "Implementation Roadmap",
            "topics": ["Discovery Phase", "Development Phase", "Deployment Phase"],
            "slide_purpose": "Show the implementation journey",
            "key_message": "Clear 3-phase approach to success",
            "tone": "professional",
            "audience": "stakeholders"
        }
    },

    # 3. grid_2x2_centered_c1
    {
        "variant_id": "grid_2x2_centered_c1",
        "description": "2x2 Grid with Icon, Title, Description (C1)",
        "slide_spec": {
            "slide_title": "Core Capabilities",
            "topics": ["Innovation", "Scalability", "Security", "Support"],
            "slide_purpose": "Highlight the four pillars of our platform",
            "key_message": "Comprehensive enterprise solution",
            "tone": "professional",
            "audience": "prospects"
        }
    },
]

TOTAL_SCENARIOS = len(PHASE1_TEST_SCENARIOS)


def generate_slide(scenario):
    """Generate slide content using the C1 variant."""
    url = f"{TEXT_SERVICE_URL}/v1.2/generate"

    payload = {
        "variant_id": scenario["variant_id"],
        "slide_spec": scenario["slide_spec"],
        "presentation_spec": {
            "presentation_title": "C1 Phase 1 Validation - 2025-12-23",
            "presentation_type": "Test Presentation"
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"    generate error: {response.status_code}")
            print(f"    Response: {response.text[:500]}")
            return None

    except Exception as e:
        print(f"    generate exception: {str(e)}")
        return None


def create_presentation_slide(scenario, text_result):
    """Create Layout Service slide format."""
    return {
        "layout": "C1-text",
        "content": {
            "slide_title": scenario["slide_spec"]["slide_title"],
            "subtitle": f"Variant: {scenario['variant_id']}",
            "body": text_result.get("html", ""),
            "footer_text": scenario["description"],
            "logo": ""
        }
    }


def post_to_layout_service(slides):
    """Post slides to Layout Service and return URL."""
    url = f"{LAYOUT_SERVICE_URL}/api/presentations"

    presentation = {
        "title": f"C1 Phase 1 Validation - {len(slides)} Variants - 2025-12-23",
        "slides": slides
    }

    print(f"\nPosting {len(slides)} slides to Layout Service...")

    try:
        response = requests.post(
            url,
            json=presentation,
            headers={"Content-Type": "application/json"},
            timeout=120
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
    start_time = time.time()

    print("=" * 80)
    print("C1 PHASE 1 VALIDATION - 3 NEW C1 SPEC FILES")
    print("Date: 2025-12-23")
    print("=" * 80)
    print(f"Text Service: {TEXT_SERVICE_URL}")
    print(f"Layout Service: {LAYOUT_SERVICE_URL}")
    print(f"Total Variants to Test: {TOTAL_SCENARIOS}")
    print("=" * 80)

    slides = []
    results = []
    successful = 0
    failed = 0

    for i, scenario in enumerate(PHASE1_TEST_SCENARIOS, 1):
        print(f"\n[{i}/{TOTAL_SCENARIOS}] {scenario['variant_id']}")
        print(f"  Description: {scenario['description']}")

        # Generate slide with C1 variant
        text_result = generate_slide(scenario)

        if text_result and text_result.get("html"):
            slide = create_presentation_slide(scenario, text_result)
            slides.append(slide)
            successful += 1
            html_len = len(text_result.get("html", ""))
            print(f"  SUCCESS: Generated {html_len} chars HTML")

            results.append({
                "variant_id": scenario["variant_id"],
                "description": scenario["description"],
                "html_length": html_len,
                "success": True
            })
        else:
            failed += 1
            results.append({
                "variant_id": scenario["variant_id"],
                "description": scenario["description"],
                "html_length": 0,
                "success": False
            })
            print(f"  FAILED: Could not generate slide")

    elapsed = time.time() - start_time

    # Summary Report
    print("\n" + "=" * 80)
    print("PHASE 1 VALIDATION RESULTS")
    print("=" * 80)
    print(f"\nSuccess: {successful}/{TOTAL_SCENARIOS}")
    print(f"Failed: {failed}/{TOTAL_SCENARIOS}")
    print(f"Time: {elapsed:.1f} seconds")

    print("\n" + "-" * 80)
    print("VARIANT RESULTS")
    print("-" * 80)
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        print(f"  [{status}] {r['variant_id']}: {r['html_length']} chars")
        print(f"         {r['description']}")

    if not slides:
        print("\nNo slides generated. Check for errors above.")
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
        print(f"\nSlides: {len(slides)}")
        print("Use arrow keys to navigate slides")
        print("=" * 80)
    else:
        print("\nFailed to create presentation in Layout Service")


if __name__ == "__main__":
    main()
