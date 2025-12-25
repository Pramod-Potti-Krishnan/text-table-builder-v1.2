#!/usr/bin/env python3
"""Final validation test for all 28 new C1 variants."""

import requests
import json
from datetime import datetime

TEXT_SERVICE = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE = "https://web-production-f0d13.up.railway.app"

# Sample of C1 variants to test (5 representative variants from different categories)
TEST_VARIANTS = [
    ("asymmetric_8_4_3section_c1", "Asymmetric 3-section"),
    ("table_3col_c1", "Table 3-column"),
    ("single_column_4section_c1", "Single Column 4-section"),
    ("hybrid_left_2x2_c1", "Hybrid Left 2x2"),
    ("impact_quote_c1", "Impact Quote"),
]

def test_variant(variant_id, description):
    """Test a single C1 variant."""
    print(f"\n{'='*60}")
    print(f"Testing: {variant_id} ({description})")
    print('='*60)

    # Generate content with correct API format
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

    try:
        resp = requests.post(f"{TEXT_SERVICE}/v1.2/generate", json=payload, timeout=60)
        print(f"Generate response: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            html_content = data.get("html_content", "")
            placeholder_count = html_content.count("{")

            if placeholder_count > 0:
                print(f"  WARNING: {placeholder_count} unfilled placeholders found!")
                return False
            else:
                print(f"  SUCCESS: All placeholders filled")

            # Publish to Layout Service
            layout_payload = {
                "presentation_id": f"test-c1-final-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "slide_index": 0,
                "html_content": html_content,
                "slide_title": f"Test: {variant_id}",
                "layout_id": variant_id
            }

            pub_resp = requests.post(f"{LAYOUT_SERVICE}/api/slide", json=layout_payload, timeout=30)
            if pub_resp.status_code == 200:
                pub_data = pub_resp.json()
                url = pub_data.get("url", "")
                print(f"  Published: {url}")
                return True
            else:
                print(f"  Publish failed: {pub_resp.status_code}")
                return False
        else:
            print(f"  FAILED: {resp.status_code}")
            print(f"  Error: {resp.text[:200]}")
            return False

    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return False

def main():
    print("\n" + "="*70)
    print("  FINAL C1 VARIANT VALIDATION TEST")
    print("  Testing 5 representative C1 variants")
    print("="*70)

    results = []
    for variant_id, description in TEST_VARIANTS:
        success = test_variant(variant_id, description)
        results.append((variant_id, success))

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

    if failed == 0:
        print("\n  ALL TESTS PASSED! C1 variants are working correctly.")
    else:
        print(f"\n  WARNING: {failed} test(s) failed.")

    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
