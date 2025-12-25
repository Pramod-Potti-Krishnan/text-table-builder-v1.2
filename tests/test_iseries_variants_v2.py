#!/usr/bin/env python3
"""Test I-series slides - using correct endpoint and mapping."""

import requests
import json

TEXT_SERVICE = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE = "https://web-production-f0d13.up.railway.app"

# Test configurations - 3 from I1, 4 from I3
TEST_CONFIGS = [
    # I1 variants (3)
    {
        "endpoint": "I1",
        "layout_name": "I1-image-left",
        "slide_title": "Strategic Vision",
        "subtitle": "Three Pillars of Success",
        "narrative": "Our company strategy focuses on innovation, customer excellence, and sustainable growth",
        "topics": ["Innovation Leadership", "Customer Excellence", "Sustainable Growth"],
        "image_prompt_hint": "futuristic city skyline with green technology"
    },
    {
        "endpoint": "I1",
        "layout_name": "I1-image-left",
        "slide_title": "Implementation Roadmap",
        "subtitle": "Phase 1 to Phase 2",
        "narrative": "Our two-phase implementation approach ensures smooth transition and measurable results",
        "topics": ["Phase 1: Foundation", "Phase 2: Scale"],
        "image_prompt_hint": "roadmap journey path with milestones"
    },
    {
        "endpoint": "I1",
        "layout_name": "I1-image-left",
        "slide_title": "Before vs After",
        "subtitle": "Transformation Results",
        "narrative": "Compare the dramatic improvements achieved through our digital transformation initiative",
        "topics": ["Before Implementation", "After Implementation"],
        "image_prompt_hint": "transformation butterfly metamorphosis"
    },
    # I3 variants (4)
    {
        "endpoint": "I3",
        "layout_name": "I3-image-left-narrow",
        "slide_title": "Core Competencies",
        "subtitle": "Four Key Strengths",
        "narrative": "Our four core competencies drive competitive advantage in the market",
        "topics": ["Technical Excellence", "Customer Focus", "Innovation", "Agility"],
        "image_prompt_hint": "professional team brainstorming in modern office"
    },
    {
        "endpoint": "I3",
        "layout_name": "I3-image-left-narrow",
        "slide_title": "Five-Year Plan",
        "subtitle": "Strategic Milestones",
        "narrative": "Our comprehensive five-year strategic plan outlines key milestones for growth",
        "topics": ["Year 1: Foundation", "Year 2: Growth", "Year 3: Expansion", "Year 4: Scale", "Year 5: Leadership"],
        "image_prompt_hint": "mountain climbing reaching summit achievement"
    },
    {
        "endpoint": "I3",
        "layout_name": "I3-image-left-narrow",
        "slide_title": "Development Process",
        "subtitle": "Three-Stage Workflow",
        "narrative": "Our streamlined development process ensures quality delivery in three stages",
        "topics": ["Design", "Develop", "Deploy"],
        "image_prompt_hint": "software development workflow diagram abstract"
    },
    {
        "endpoint": "I3",
        "layout_name": "I3-image-left-narrow",
        "slide_title": "Product Tiers",
        "subtitle": "Choose Your Plan",
        "narrative": "Compare our three product tiers to find the perfect fit for your needs",
        "topics": ["Basic", "Professional", "Enterprise"],
        "image_prompt_hint": "product tiers pricing comparison abstract"
    }
]


def generate_slide(config: dict, slide_number: int) -> dict:
    """Generate I-series slide using /v1.2/slides endpoint."""
    print(f"\n  Calling /v1.2/slides/{config['endpoint']}...")

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
        f"{TEXT_SERVICE}/v1.2/slides/{config['endpoint']}",
        json=payload,
        timeout=120
    )

    if resp.status_code != 200:
        print(f"    ERROR: {resp.status_code} - {resp.text[:300]}")
        return None

    data = resp.json()
    
    # Debug: show all keys
    print(f"    Response keys: {list(data.keys())}")
    
    # Get body from response (try multiple possible field names)
    body = data.get("body") or data.get("content_html") or data.get("rich_content") or ""
    image_url = data.get("image_url", "")
    
    print(f"    Got image: {image_url[:50] if image_url else 'NONE'}...")
    print(f"    Got body: {len(body)} chars")

    # Map to Layout Service format per SLIDE_GENERATION_INPUT_SPEC.md
    return {
        "layout": config["layout_name"],
        "content": {
            "slide_title": data.get("slide_title", config["slide_title"]),
            "subtitle": data.get("subtitle", config["subtitle"]),
            "image_url": image_url,
            "body": body,
            "presentation_name": "I-Series Test"
        }
    }


def create_presentation(slides: list) -> str:
    """Create presentation in Layout Service."""
    print("\n  Creating presentation...")

    resp = requests.post(
        f"{LAYOUT_SERVICE}/api/presentations",
        json={"title": "I-Series Test", "slides": slides},
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
    print("  I-SERIES TEST (v2 - correct endpoint)")
    print("  3 from I1 + 4 from I3 = 7 slides")
    print("="*70)

    slides = []

    for i, config in enumerate(TEST_CONFIGS, 1):
        print(f"\n{'='*60}")
        print(f"Slide {i}: {config['endpoint']} - {config['slide_title']}")
        print('='*60)

        slide = generate_slide(config, i)
        if slide:
            slides.append(slide)

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
