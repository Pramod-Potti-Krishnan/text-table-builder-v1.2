#!/usr/bin/env python3
"""Visual validation test for I-series (I1-I4) image+content layouts.

Generates content via Text Service, assembles in Layout Service, opens in browser.
"""

import requests
import json
from datetime import datetime

TEXT_SERVICE = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE = "https://web-production-f0d13.up.railway.app"

# I-series layout configurations
ISERIES_CONFIGS = [
    {
        "text_endpoint": "I1",
        "layout_name": "I1-image-left",
        "narrative": "Our leadership team drives innovation across all business units",
        "slide_title": "Leadership Team",
        "subtitle": "Driving Innovation",
        "topics": ["Strategic Vision", "Technical Excellence", "Customer Focus"],
        "image_prompt_hint": "professional team collaboration in modern office"
    },
    {
        "text_endpoint": "I2",
        "layout_name": "I2-image-right",
        "narrative": "Product features that transform how businesses operate",
        "slide_title": "Product Features",
        "subtitle": "Transform Your Business",
        "topics": ["AI-Powered Analytics", "Real-time Collaboration", "Scalable Infrastructure"],
        "image_prompt_hint": "modern technology product interface"
    },
    {
        "text_endpoint": "I3",
        "layout_name": "I3-image-left-narrow",
        "narrative": "Client success story showing measurable business impact",
        "slide_title": "Client Success",
        "subtitle": "Measurable Results",
        "topics": ["50% Cost Reduction", "3x Revenue Growth", "99.9% Uptime"],
        "image_prompt_hint": "business success growth chart celebration"
    },
    {
        "text_endpoint": "I4",
        "layout_name": "I4-image-right-narrow",
        "narrative": "Strategic partner ecosystem enabling global reach",
        "slide_title": "Partner Ecosystem",
        "subtitle": "Global Reach",
        "topics": ["Technology Partners", "Distribution Network", "Integration Hub"],
        "image_prompt_hint": "strategic partnership handshake global network"
    }
]


def generate_iseries_slide(config: dict, slide_number: int) -> dict:
    """Generate I-series slide content from Text Service."""
    print(f"\n  Calling Text Service /v1.2/slides/{config['text_endpoint']}...")

    payload = {
        "slide_number": slide_number,
        "narrative": config["narrative"],
        "slide_title": config["slide_title"],
        "subtitle": config["subtitle"],
        "topics": config["topics"],
        "visual_style": "illustrated",
        "image_prompt_hint": config["image_prompt_hint"],
        "content_style": "bullets",
        "max_bullets": 5,
        "context": {"audience": "executives", "tone": "professional"}
    }

    resp = requests.post(
        f"{TEXT_SERVICE}/v1.2/slides/{config['text_endpoint']}",
        json=payload,
        timeout=120  # Image generation can take time
    )

    if resp.status_code != 200:
        print(f"    ERROR: {resp.status_code} - {resp.text[:200]}")
        return None

    data = resp.json()
    print(f"    Got image_url: {data.get('image_url', 'MISSING')[:60]}...")
    print(f"    Got slide_title: {len(data.get('slide_title', ''))} chars")
    print(f"    Got body: {len(data.get('body', ''))} chars")

    return data


def map_to_layout_service(text_response: dict, config: dict) -> dict:
    """Map Text Service response to Layout Service slide format."""
    return {
        "layout": config["layout_name"],
        "content": {
            "slide_title": text_response.get("slide_title", config["slide_title"]),
            "subtitle": text_response.get("subtitle", config["subtitle"]),
            "image_url": text_response.get("image_url", ""),
            "body": text_response.get("body", ""),
            "presentation_name": "I-Series Layout Test"
        }
    }


def create_presentation(slides: list) -> str:
    """Create presentation in Layout Service and return URL."""
    print("\n  Creating presentation in Layout Service...")

    payload = {
        "title": "I-Series Layout Test",
        "slides": slides
    }

    resp = requests.post(
        f"{LAYOUT_SERVICE}/api/presentations",
        json=payload,
        timeout=30
    )

    if resp.status_code in [200, 201]:
        data = resp.json()
        pres_id = data.get("id")
        url = f"{LAYOUT_SERVICE}/p/{pres_id}"
        print(f"    Created presentation: {pres_id}")
        return url
    else:
        print(f"    ERROR: {resp.status_code} - {resp.text[:300]}")
        return None


def main():
    print("\n" + "="*70)
    print("  I-SERIES (I1-I4) VISUAL VALIDATION TEST")
    print("  Generating 4 slides with AI images + content")
    print("="*70)

    slides = []

    for i, config in enumerate(ISERIES_CONFIGS, 1):
        print(f"\n{'='*60}")
        print(f"Slide {i}: {config['layout_name']} - {config['slide_title']}")
        print('='*60)

        # Step 1: Generate from Text Service
        text_response = generate_iseries_slide(config, i)
        if not text_response:
            print(f"  FAILED to generate slide {i}")
            continue

        # Step 2: Map to Layout Service format
        slide_payload = map_to_layout_service(text_response, config)
        slides.append(slide_payload)
        print(f"  Mapped to {config['layout_name']} layout")

    if not slides:
        print("\n  ERROR: No slides generated!")
        return None

    # Step 3: Create presentation
    print(f"\n{'='*60}")
    print(f"Creating presentation with {len(slides)} slides")
    print('='*60)

    url = create_presentation(slides)

    if url:
        print("\n" + "="*70)
        print("  SUCCESS!")
        print("="*70)
        print(f"\n  Presentation URL: {url}")
        print(f"  Slides: {len(slides)}")
        return url
    else:
        print("\n  FAILED to create presentation")
        return None


if __name__ == "__main__":
    url = main()
    if url:
        print(f"\n  Opening in browser...")
        import subprocess
        subprocess.run(["open", url])
