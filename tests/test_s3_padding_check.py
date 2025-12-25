#!/usr/bin/env python3
"""
Test S3 Layout - Comparison, Metrics, Hybrid
Quick test to verify left padding changes in S3 layout.
"""

import requests
import time

TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

TEST_VARIANTS = [
    {
        "variant_id": "comparison_3col",
        "category": "Comparison",
        "slide_spec": {
            "slide_title": "Platform Comparison",
            "slide_purpose": "Compare three platform options side by side",
            "key_message": "Choose the right platform for your needs",
            "tone": "professional",
            "audience": "decision makers"
        }
    },
    {
        "variant_id": "metrics_3col",
        "category": "Metrics",
        "slide_spec": {
            "slide_title": "Key Performance Indicators",
            "slide_purpose": "Highlight three critical business metrics",
            "key_message": "Measurable results that drive success",
            "tone": "professional",
            "audience": "executives"
        }
    },
    {
        "variant_id": "hybrid_top_2x2",
        "category": "Hybrid",
        "slide_spec": {
            "slide_title": "Solution Components",
            "slide_purpose": "Display four solution components with summary",
            "key_message": "Integrated solution architecture",
            "tone": "professional",
            "audience": "technical team"
        }
    },
]


def generate_slide(variant_config):
    """Call Text Service to generate slide content."""
    url = f"{TEXT_SERVICE_URL}/v1.2/generate"

    payload = {
        "variant_id": variant_config["variant_id"],
        "layout_id": "C1",  # Use C1 templates (840px height, zero left padding)
        "slide_spec": variant_config["slide_spec"],
        "presentation_spec": {
            "presentation_title": "S3 Padding Test",
            "presentation_type": "Test"
        }
    }

    print(f"  Generating {variant_config['variant_id']}...")

    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None


def main():
    start = time.time()
    print("=" * 60)
    print("S3 PADDING TEST - Comparison, Metrics, Hybrid")
    print("=" * 60)

    slides = []

    for i, variant in enumerate(TEST_VARIANTS, 1):
        print(f"\n[{i}/3] {variant['category']}: {variant['variant_id']}")
        result = generate_slide(variant)

        if result and result.get("html"):
            slides.append({
                "layout": "C1-text",  # C1 text layout
                "content": {
                    "slide_title": variant["slide_spec"]["slide_title"],
                    "subtitle": f"{variant['category']} | {variant['variant_id']}",
                    "body": result.get("html", ""),
                    "footer_text": "S3 Padding Test",
                    "logo": ""
                }
            })
            print(f"  Success! HTML: {len(result.get('html', ''))} chars")
        else:
            print(f"  Failed!")

    if slides:
        print(f"\nPosting {len(slides)} slides to Layout Service...")
        response = requests.post(
            f"{LAYOUT_SERVICE_URL}/api/presentations",
            json={"title": "S3 Padding Test - Comparison, Metrics, Hybrid", "slides": slides},
            timeout=120
        )

        if response.status_code in [200, 201]:
            data = response.json()
            url = f"{LAYOUT_SERVICE_URL}{data.get('url', '/p/' + data.get('id'))}"
            print(f"\n{'=' * 60}")
            print(f"SUCCESS! View at:")
            print(f"{url}")
            print(f"{'=' * 60}")
            print(f"Time: {time.time() - start:.1f}s")
            return url

    return None


if __name__ == "__main__":
    main()
