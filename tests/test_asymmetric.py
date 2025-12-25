#!/usr/bin/env python3
"""Quick test for asymmetric template sidebar height."""

import requests
import time

TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

TEST_VARIANTS = [
    {
        "variant_id": "asymmetric_8_4_3section",
        "slide_spec": {
            "slide_title": "Market Analysis Overview",
            "slide_purpose": "Present market insights with action items",
            "key_message": "Data-driven market understanding",
            "tone": "professional",
            "audience": "executives"
        }
    },
    {
        "variant_id": "asymmetric_8_4_4section",
        "slide_spec": {
            "slide_title": "Product Strategy",
            "slide_purpose": "Product overview with four key areas",
            "key_message": "Comprehensive product view",
            "tone": "professional",
            "audience": "product team"
        }
    },
    {
        "variant_id": "asymmetric_8_4_5section",
        "slide_spec": {
            "slide_title": "Research Findings",
            "slide_purpose": "Present research with five key findings",
            "key_message": "Evidence-based insights",
            "tone": "professional",
            "audience": "research team"
        }
    },
]

def main():
    print("Waiting 25s for Railway deployment...")
    time.sleep(25)

    print("=" * 60)
    print("ASYMMETRIC TEMPLATE TEST - Extended Sidebar")
    print("=" * 60)

    slides = []

    for i, variant in enumerate(TEST_VARIANTS, 1):
        print(f"\n[{i}/3] Generating {variant['variant_id']}...")

        payload = {
            "variant_id": variant["variant_id"],
            "layout_id": "C1",
            "slide_spec": variant["slide_spec"],
            "presentation_spec": {"presentation_title": "Asymmetric Test"}
        }

        response = requests.post(f"{TEXT_SERVICE_URL}/v1.2/generate", json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()
            slides.append({
                "layout": "C1-text",
                "content": {
                    "slide_title": variant["slide_spec"]["slide_title"],
                    "subtitle": f"Asymmetric | {variant['variant_id']}",
                    "body": result.get("html", ""),
                    "footer_text": "Asymmetric Sidebar Test"
                }
            })
            print(f"  Success! HTML: {len(result.get('html', ''))} chars")
        else:
            print(f"  Error: {response.status_code}")

    if slides:
        print(f"\nPosting {len(slides)} slides...")
        response = requests.post(
            f"{LAYOUT_SERVICE_URL}/api/presentations",
            json={"title": "Asymmetric Extended Sidebar Test", "slides": slides},
            timeout=120
        )

        if response.status_code in [200, 201]:
            data = response.json()
            url = f"{LAYOUT_SERVICE_URL}{data.get('url', '/p/' + data.get('id'))}"
            print(f"\n{'=' * 60}")
            print(f"SUCCESS! View at:")
            print(url)
            print(f"{'=' * 60}")
            return url

if __name__ == "__main__":
    main()
