#!/usr/bin/env python3
"""Test I-series variants - 3 from I1, 4 from I3."""

import requests
import json

TEXT_SERVICE = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE = "https://web-production-f0d13.up.railway.app"

# Test configurations - 3 from I1, 4 from I3
TEST_CONFIGS = [
    # I1 variants (3)
    {
        "variant_id": "single_column_3section_i1",
        "layout_name": "I1-image-left",
        "title": "Strategic Vision",
        "subtitle": "Three Pillars of Success",
        "narrative": "Our company strategy focuses on innovation, customer excellence, and sustainable growth",
        "topics": ["Innovation Leadership", "Customer Excellence", "Sustainable Growth"],
        "image_prompt_hint": "futuristic city skyline with green technology"
    },
    {
        "variant_id": "sequential_2col_i1",
        "layout_name": "I1-image-left",
        "title": "Implementation Roadmap",
        "subtitle": "Phase 1 to Phase 2",
        "narrative": "Our two-phase implementation approach ensures smooth transition and measurable results",
        "topics": ["Phase 1: Foundation", "Phase 2: Scale"],
        "image_prompt_hint": "roadmap journey path with milestones"
    },
    {
        "variant_id": "comparison_2col_i1",
        "layout_name": "I1-image-left",
        "title": "Before vs After",
        "subtitle": "Transformation Results",
        "narrative": "Compare the dramatic improvements achieved through our digital transformation initiative",
        "topics": ["Before Implementation", "After Implementation"],
        "image_prompt_hint": "transformation butterfly metamorphosis"
    },
    # I3 variants (4)
    {
        "variant_id": "single_column_4section_i3",
        "layout_name": "I3-image-left-narrow",
        "title": "Core Competencies",
        "subtitle": "Four Key Strengths",
        "narrative": "Our four core competencies drive competitive advantage in the market",
        "topics": ["Technical Excellence", "Customer Focus", "Innovation", "Agility"],
        "image_prompt_hint": "professional team brainstorming in modern office"
    },
    {
        "variant_id": "single_column_5section_i3",
        "layout_name": "I3-image-left-narrow",
        "title": "Five-Year Plan",
        "subtitle": "Strategic Milestones",
        "narrative": "Our comprehensive five-year strategic plan outlines key milestones for growth",
        "topics": ["Year 1: Foundation", "Year 2: Growth", "Year 3: Expansion", "Year 4: Scale", "Year 5: Leadership"],
        "image_prompt_hint": "mountain climbing reaching summit achievement"
    },
    {
        "variant_id": "sequential_3col_i3",
        "layout_name": "I3-image-left-narrow",
        "title": "Development Process",
        "subtitle": "Three-Stage Workflow",
        "narrative": "Our streamlined development process ensures quality delivery in three stages",
        "topics": ["Design", "Develop", "Deploy"],
        "image_prompt_hint": "software development workflow diagram abstract"
    },
    {
        "variant_id": "comparison_3col_i3",
        "layout_name": "I3-image-left-narrow",
        "title": "Product Tiers",
        "subtitle": "Choose Your Plan",
        "narrative": "Compare our three product tiers to find the perfect fit for your needs",
        "topics": ["Basic", "Professional", "Enterprise"],
        "image_prompt_hint": "product tiers pricing comparison abstract"
    }
]


def generate_variant_slide(config: dict, slide_number: int) -> dict:
    """Generate I-series slide with specific variant."""
    print(f"\n  Generating {config['variant_id']}...")

    layout_type = "I1" if "_i1" in config["variant_id"] else "I3"

    payload = {
        "slide_number": slide_number,
        "layout_type": layout_type,
        "title": config["title"],
        "subtitle": config["subtitle"],
        "narrative": config["narrative"],
        "topics": config["topics"],
        "visual_style": "illustrated",
        "image_prompt_hint": config["image_prompt_hint"],
        "content_style": "bullets",
        "variant_id": config["variant_id"]
    }

    resp = requests.post(
        f"{TEXT_SERVICE}/v1.2/iseries/{layout_type}",
        json=payload,
        timeout=120
    )

    if resp.status_code != 200:
        print(f"    ERROR: {resp.status_code} - {resp.text[:200]}")
        return None

    data = resp.json()
    print(f"    Got image: {data.get('image_url', 'MISSING')[:50]}...")
    print(f"    Got body: {len(data.get('body', ''))} chars")

    return {
        "layout": config["layout_name"],
        "content": {
            "slide_title": data.get("slide_title", config["title"]),
            "subtitle": data.get("subtitle", config["subtitle"]),
            "image_url": data.get("image_url", ""),
            "body": data.get("body", ""),
            "presentation_name": "I-Series Variants Test"
        }
    }


def create_presentation(slides: list) -> str:
    """Create presentation in Layout Service."""
    print("\n  Creating presentation...")

    resp = requests.post(
        f"{LAYOUT_SERVICE}/api/presentations",
        json={"title": "I-Series Variants Test", "slides": slides},
        timeout=30
    )

    if resp.status_code in [200, 201]:
        pres_id = resp.json().get("id")
        return f"{LAYOUT_SERVICE}/p/{pres_id}"
    else:
        print(f"    ERROR: {resp.status_code} - {resp.text[:200]}")
        return None


def main():
    print("\n" + "="*70)
    print("  I-SERIES VARIANTS TEST")
    print("  3 from I1 + 4 from I3 = 7 slides")
    print("="*70)

    slides = []

    for i, config in enumerate(TEST_CONFIGS, 1):
        print(f"\n{'='*60}")
        print(f"Slide {i}: {config['variant_id']}")
        print(f"Layout: {config['layout_name']}")
        print('='*60)

        slide = generate_variant_slide(config, i)
        if slide:
            slides.append(slide)
        else:
            print(f"  FAILED")

    if not slides:
        print("\n  ERROR: No slides generated!")
        return None

    print(f"\n{'='*60}")
    print(f"Creating presentation with {len(slides)} slides")
    print('='*60)

    url = create_presentation(slides)

    if url:
        print("\n" + "="*70)
        print("  SUCCESS!")
        print("="*70)
        print(f"\n  URL: {url}")
        return url

    return None


if __name__ == "__main__":
    url = main()
    if url:
        print(f"\n  Opening browser...")
        import subprocess
        subprocess.run(["open", url])
