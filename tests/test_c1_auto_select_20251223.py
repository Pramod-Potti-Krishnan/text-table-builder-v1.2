#!/usr/bin/env python3
"""
Test C1 Auto-Select Feature - Variant Recommendation
Date: 2025-12-23

Tests the auto-select feature where the Text Service recommends the best variant
based on content characteristics instead of explicitly specifying variant_id.

Flow:
1. Send content to /v1.2/recommend-variant
2. Get recommended variant with confidence score
3. Generate slide using recommended variant
4. Publish to Layout Service

Usage:
    python3 test_c1_auto_select_20251223.py
"""

import requests
import json
import time
from datetime import datetime

# Service URLs
TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

# Just 3 test scenarios - different content types
AUTO_SELECT_TEST_SCENARIOS = [
    # Scenario 1: Comparison content (should recommend comparison_3col)
    {
        "scenario_id": "compare_three_options",
        "description": "Should recommend comparison_3col",
        "slide_content": {
            "title": "Pricing Tiers Comparison",
            "topics": ["Basic", "Professional", "Enterprise"],
            "topic_count": 3
        },
        "content_hints": {
            "is_comparison": True,
            "has_numbers": True,
            "detected_keywords": ["compare", "tier", "pricing"]
        },
        "available_space": {"width": 1800, "height": 720}
    },

    # Scenario 2: Metrics content (should recommend metrics_3col or metrics_4col)
    {
        "scenario_id": "four_key_metrics",
        "description": "Should recommend metrics_4col",
        "slide_content": {
            "title": "Quarterly Dashboard",
            "topics": ["Revenue: $5M", "Customers: 10K", "CSAT: 92%", "Uptime: 99.9%"],
            "topic_count": 4
        },
        "content_hints": {
            "is_comparison": False,
            "has_numbers": True,
            "detected_keywords": ["dashboard", "quarterly", "metrics"]
        },
        "available_space": {"width": 1800, "height": 720}
    },

    # Scenario 3: Sequential/Process content (should recommend sequential_3col)
    {
        "scenario_id": "three_step_process",
        "description": "Should recommend sequential_3col",
        "slide_content": {
            "title": "Implementation Journey",
            "topics": ["Step 1: Plan", "Step 2: Build", "Step 3: Launch"],
            "topic_count": 3
        },
        "content_hints": {
            "is_comparison": False,
            "has_numbers": True,
            "detected_keywords": ["step", "process", "journey", "phase"]
        },
        "available_space": {"width": 1800, "height": 720}
    },
]

TOTAL_SCENARIOS = len(AUTO_SELECT_TEST_SCENARIOS)


def test_can_handle(scenario):
    """Test if service can handle this content type."""
    url = f"{TEXT_SERVICE_URL}/v1.2/can-handle"

    payload = {
        "slide_content": scenario["slide_content"],
        "content_hints": scenario["content_hints"],
        "available_space": scenario["available_space"]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"    can-handle error: {response.status_code}")
            return None

    except Exception as e:
        print(f"    can-handle exception: {str(e)}")
        return None


def get_recommended_variant(scenario):
    """Get variant recommendation from Text Service."""
    url = f"{TEXT_SERVICE_URL}/v1.2/recommend-variant"

    payload = {
        "slide_content": scenario["slide_content"],
        "content_hints": scenario["content_hints"],
        "available_space": scenario["available_space"]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"    recommend-variant error: {response.status_code}")
            print(f"    Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"    recommend-variant exception: {str(e)}")
        return None


def generate_slide_with_variant(scenario, variant_id):
    """Generate slide content using the recommended variant."""
    url = f"{TEXT_SERVICE_URL}/v1.2/generate"

    payload = {
        "variant_id": variant_id,
        "slide_spec": {
            "slide_title": scenario["slide_content"]["title"],
            "topics": scenario["slide_content"]["topics"],
            "slide_purpose": scenario["description"],
            "key_message": f"Auto-selected: {variant_id}",
            "tone": "professional",
            "audience": "executives"
        },
        "presentation_spec": {
            "presentation_title": "C1 Auto-Select Test - 2025-12-23",
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
            return None

    except Exception as e:
        print(f"    generate exception: {str(e)}")
        return None


def create_presentation_slide(scenario, text_result, variant_id, confidence):
    """Create Layout Service slide format."""
    return {
        "layout": "C1-text",
        "content": {
            "slide_title": scenario["slide_content"]["title"],
            "subtitle": f"Auto-Selected: {variant_id} (confidence: {confidence:.0%})",
            "body": text_result.get("html", ""),
            "footer_text": f"Scenario: {scenario['scenario_id']}",
            "logo": ""
        }
    }


def post_to_layout_service(slides):
    """Post slides to Layout Service and return URL."""
    url = f"{LAYOUT_SERVICE_URL}/api/presentations"

    presentation = {
        "title": f"C1 Auto-Select Test - {len(slides)} Scenarios - 2025-12-23",
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
    print("C1 AUTO-SELECT TEST - VARIANT RECOMMENDATION")
    print("Date: 2025-12-23")
    print("=" * 80)
    print(f"Text Service: {TEXT_SERVICE_URL}")
    print(f"Layout Service: {LAYOUT_SERVICE_URL}")
    print(f"Total Scenarios: {TOTAL_SCENARIOS}")
    print("=" * 80)

    slides = []
    results = []
    successful = 0
    failed = 0

    for i, scenario in enumerate(AUTO_SELECT_TEST_SCENARIOS, 1):
        print(f"\n[{i}/{TOTAL_SCENARIOS}] {scenario['scenario_id']}")
        print(f"  Description: {scenario['description']}")
        print(f"  Topics: {scenario['slide_content']['topics']}")

        # Step 1: Test can-handle
        can_handle_result = test_can_handle(scenario)
        if can_handle_result:
            print(f"  Can Handle: {can_handle_result.get('can_handle', False)} "
                  f"(confidence: {can_handle_result.get('confidence', 0):.0%})")

        # Step 2: Get recommended variant
        recommendation = get_recommended_variant(scenario)

        if not recommendation or not recommendation.get("recommended_variants"):
            print(f"  No variant recommendation received")
            failed += 1
            results.append({
                "scenario": scenario["scenario_id"],
                "expected": scenario["description"],
                "recommended": None,
                "confidence": 0,
                "success": False
            })
            continue

        # Get top recommendation
        top_rec = recommendation["recommended_variants"][0]
        variant_id = top_rec["variant_id"]
        confidence = top_rec.get("confidence", 0)
        reason = top_rec.get("reason", "")

        print(f"  Recommended: {variant_id} (confidence: {confidence:.0%})")
        print(f"  Reason: {reason}")

        # Step 3: Generate slide with recommended variant
        text_result = generate_slide_with_variant(scenario, variant_id)

        if text_result and text_result.get("html"):
            slide = create_presentation_slide(scenario, text_result, variant_id, confidence)
            slides.append(slide)
            successful += 1
            html_len = len(text_result.get("html", ""))
            print(f"  Generated: {html_len} chars HTML")

            results.append({
                "scenario": scenario["scenario_id"],
                "expected": scenario["description"],
                "recommended": variant_id,
                "confidence": confidence,
                "reason": reason,
                "success": True
            })
        else:
            failed += 1
            results.append({
                "scenario": scenario["scenario_id"],
                "expected": scenario["description"],
                "recommended": variant_id,
                "confidence": confidence,
                "success": False
            })
            print(f"  Failed to generate slide")

    elapsed = time.time() - start_time

    # Summary Report
    print("\n" + "=" * 80)
    print("AUTO-SELECT TEST RESULTS")
    print("=" * 80)
    print(f"\nSuccess: {successful}/{TOTAL_SCENARIOS}")
    print(f"Failed: {failed}/{TOTAL_SCENARIOS}")
    print(f"Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")

    print("\n" + "-" * 80)
    print("RECOMMENDATION SUMMARY")
    print("-" * 80)
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        rec = r["recommended"] or "None"
        conf = f"{r['confidence']:.0%}" if r["confidence"] else "N/A"
        print(f"  [{status}] {r['scenario']}: {rec} ({conf})")
        print(f"        Expected: {r['expected']}")

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
        print(f"\nSlides: {len(slides)}")
        print("Use arrow keys to navigate slides")
        print("=" * 80)
    else:
        print("\nFailed to create presentation in Layout Service")


if __name__ == "__main__":
    main()
