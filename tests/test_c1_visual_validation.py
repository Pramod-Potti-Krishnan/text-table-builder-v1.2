#!/usr/bin/env python3
"""Visual validation test for C1 variants.

Generates content via Text Service, publishes to Layout Service using C1-text layout,
and outputs URLs for browser viewing.
"""

import requests
import json
from datetime import datetime

TEXT_SERVICE = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE = "https://web-production-f0d13.up.railway.app"

# 5 representative C1 variants to test (including 2 comparison ones)
TEST_VARIANTS = [
    ("comparison_3col_c1", "Comparison 3-Column"),
    ("comparison_2col_c1", "Comparison 2-Column"),
    ("asymmetric_8_4_4section_c1", "Asymmetric 4-Section"),
    ("table_4col_c1", "Table 4-Column"),
    ("single_column_3section_c1", "Single Column 3-Section"),
]


def generate_content(variant_id: str) -> str:
    """Generate HTML content from Text Service."""
    payload = {
        "variant_id": variant_id,
        "slide_spec": {
            "slide_title": "Digital Transformation Strategy",
            "slide_purpose": "Outline key digital transformation initiatives",
            "key_message": "Strategic technology adoption drives business growth",
            "target_points": [
                "AI integration for process automation",
                "Cloud migration for scalability",
                "Data-driven decision making",
                "Change management best practices"
            ],
            "tone": "professional",
            "audience": "Executive leadership team"
        }
    }

    resp = requests.post(f"{TEXT_SERVICE}/v1.2/generate", json=payload, timeout=60)
    if resp.status_code != 200:
        raise Exception(f"Text Service error: {resp.status_code} - {resp.text[:200]}")

    data = resp.json()
    # Response uses 'html' field, not 'html_content'
    return data.get("html", "")


def publish_to_layout_service(html_content: str, slide_title: str, variant_id: str) -> str:
    """Publish slide to Layout Service using C1-text layout."""
    presentation_id = f"c1-visual-test-{datetime.now().strftime('%Y%m%d%H%M%S')}-{variant_id.replace('_', '-')}"

    # Create presentation with slide included
    slide_payload = {
        "layout": "C1-text",
        "content": {
            "slide_title": slide_title,
            "subtitle": f"Testing {variant_id}",
            "body": html_content,
            "footer_text": "C1 Variant Test"
        }
    }

    create_payload = {
        "presentation_id": presentation_id,
        "title": f"C1 Test: {variant_id}",
        "slides": [slide_payload]
    }

    create_resp = requests.post(
        f"{LAYOUT_SERVICE}/api/presentations",
        json=create_payload,
        timeout=30
    )

    if create_resp.status_code in [200, 201]:
        data = create_resp.json()
        pres_id = data.get("id", presentation_id)
        viewer_url = f"{LAYOUT_SERVICE}/p/{pres_id}"
        return viewer_url
    else:
        raise Exception(f"Layout Service error: {create_resp.status_code} - {create_resp.text[:300]}")


def test_variant(variant_id: str, description: str) -> tuple:
    """Test a single C1 variant and return URL."""
    print(f"\n{'='*60}")
    print(f"Testing: {variant_id} ({description})")
    print('='*60)

    try:
        # Step 1: Generate content from Text Service
        print("  1. Generating content from Text Service...")
        html_content = generate_content(variant_id)

        if not html_content:
            print("  ERROR: No HTML content generated")
            return (False, None)

        placeholder_count = html_content.count("{")
        if placeholder_count > 0:
            print(f"  WARNING: {placeholder_count} unfilled placeholders!")
        else:
            print(f"  Content generated: {len(html_content)} chars")

        # Step 2: Publish to Layout Service
        print("  2. Publishing to Layout Service with C1-text layout...")
        url = publish_to_layout_service(
            html_content=html_content,
            slide_title="Digital Transformation Strategy",
            variant_id=variant_id
        )
        print(f"  SUCCESS: {url}")
        return (True, url)

    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return (False, None)


def main():
    print("\n" + "="*70)
    print("  C1 VARIANT VISUAL VALIDATION TEST")
    print("  Testing 5 variants with C1-text layout")
    print("="*70)

    results = []
    urls = []

    for variant_id, description in TEST_VARIANTS:
        success, url = test_variant(variant_id, description)
        results.append((variant_id, success))
        if url:
            urls.append((variant_id, url))

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)

    passed = sum(1 for _, s in results if s)
    failed = len(results) - passed

    for variant_id, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {variant_id}")

    print(f"\n  Total: {passed}/{len(results)} passed")

    if urls:
        print("\n" + "="*70)
        print("  VIEW SLIDES IN BROWSER:")
        print("="*70)
        for variant_id, url in urls:
            print(f"  {variant_id}:")
            print(f"    {url}")

    return urls


if __name__ == "__main__":
    urls = main()
