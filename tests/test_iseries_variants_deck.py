#!/usr/bin/env python3
"""
Test I-Series Variants - Create Deck in Layout Service

Generates 3 random I-series slides with content variants and publishes
them to the Layout Service as a viewable presentation.
"""

import requests
import json
import random
from datetime import datetime

TEXT_SERVICE = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE = "https://web-production-f0d13.up.railway.app"

# I-series layout configurations with compatible variants
ISERIES_CONFIGS = {
    "I1": {
        "layout_name": "I1-image-left",
        "image_position": "left",
        "image_type": "wide",
        "compatible_variants": [
            "single_column_3section_i1",
            "single_column_4section_i1",
            "single_column_5section_i1",
            "comparison_2col_i1",
            "comparison_3col_i1",
            "sequential_2col_i1",
            "sequential_3col_i1"
        ]
    },
    "I2": {
        "layout_name": "I2-image-right",
        "image_position": "right",
        "image_type": "wide",
        "compatible_variants": [
            "single_column_3section_i1",
            "single_column_4section_i1",
            "single_column_5section_i1",
            "comparison_2col_i1",
            "comparison_3col_i1",
            "sequential_2col_i1",
            "sequential_3col_i1"
        ]
    },
    "I3": {
        "layout_name": "I3-image-left-narrow",
        "image_position": "left",
        "image_type": "narrow",
        "compatible_variants": [
            "single_column_3section_i3",
            "single_column_4section_i3",
            "single_column_5section_i3",
            "comparison_2col_i3",
            "comparison_3col_i3",
            "sequential_2col_i3",
            "sequential_3col_i3"
        ]
    },
    "I4": {
        "layout_name": "I4-image-right-narrow",
        "image_position": "right",
        "image_type": "narrow",
        "compatible_variants": [
            "single_column_3section_i3",
            "single_column_4section_i3",
            "single_column_5section_i3",
            "comparison_2col_i3",
            "comparison_3col_i3",
            "sequential_2col_i3",
            "sequential_3col_i3"
        ]
    }
}

# Sample content for slides
SAMPLE_CONTENT = [
    {
        "title": "Digital Transformation",
        "subtitle": "Embrace the Future",
        "narrative": "Modern enterprises must embrace digital transformation to stay competitive. Key areas include cloud migration, AI integration, and process automation.",
        "topics": ["Cloud Infrastructure", "AI/ML Adoption", "Process Automation", "Data Analytics"],
        "image_hint": "futuristic digital transformation technology abstract"
    },
    {
        "title": "Sustainable Growth",
        "subtitle": "Building for Tomorrow",
        "narrative": "Implementing sustainable practices drives long-term value through reduced costs, improved brand reputation, and regulatory compliance.",
        "topics": ["Carbon Reduction", "Renewable Energy", "Circular Economy", "ESG Reporting"],
        "image_hint": "sustainable green business growth nature technology"
    },
    {
        "title": "Customer Excellence",
        "subtitle": "Exceeding Expectations",
        "narrative": "Exceptional customer experience differentiates leading brands. Focus on personalization, omnichannel engagement, and proactive service.",
        "topics": ["Personalization", "Omnichannel", "Self-Service", "Loyalty Programs"],
        "image_hint": "happy customer service excellence satisfaction"
    },
    {
        "title": "Innovation Pipeline",
        "subtitle": "Ideas to Impact",
        "narrative": "A robust innovation pipeline transforms creative ideas into market-leading products through structured ideation, rapid prototyping, and iterative development.",
        "topics": ["Ideation Process", "Rapid Prototyping", "Market Testing", "Scale-up"],
        "image_hint": "innovation lightbulb ideas creative technology"
    },
    {
        "title": "Team Performance",
        "subtitle": "Achieving Together",
        "narrative": "High-performing teams combine clear goals, effective communication, and continuous learning to deliver exceptional results consistently.",
        "topics": ["Goal Alignment", "Collaboration Tools", "Skill Development", "Recognition"],
        "image_hint": "team collaboration success achievement business"
    }
]


def generate_iseries_slide(layout_type: str, content_variant: str, content: dict, slide_number: int) -> dict:
    """Generate I-series slide with content variant from Text Service."""
    config = ISERIES_CONFIGS[layout_type]

    print(f"\n  Calling Text Service /v1.2/iseries/generate...")
    print(f"    Layout: {layout_type} ({config['layout_name']})")
    print(f"    Variant: {content_variant}")

    payload = {
        "slide_number": slide_number,
        "layout_type": layout_type,
        "title": content["title"],
        "subtitle": content["subtitle"],
        "narrative": content["narrative"],
        "topics": content["topics"],
        "visual_style": "illustrated",
        "content_style": "bullets",
        "image_prompt_hint": content["image_hint"],
        "content_variant": content_variant  # NEW: Using content variant
    }

    resp = requests.post(
        f"{TEXT_SERVICE}/v1.2/iseries/generate",
        json=payload,
        timeout=120
    )

    if resp.status_code != 200:
        print(f"    ERROR: {resp.status_code} - {resp.text[:200]}")
        return None

    data = resp.json()

    # Check metadata for variant info
    metadata = data.get("metadata", {})
    variant_spec = metadata.get("variant_spec", {})

    print(f"    Image URL: {data.get('image_url', 'FALLBACK')[:60]}...")
    print(f"    Image fallback: {data.get('image_fallback', False)}")
    print(f"    Generation mode: {metadata.get('generation_mode', 'unknown')}")
    if variant_spec:
        print(f"    Variant loaded: {variant_spec.get('variant_id', 'N/A')}")
        print(f"    I-series layout: {variant_spec.get('iseries_layout', 'N/A')}")

    return data


def map_to_layout_service(text_response: dict, layout_type: str, content: dict) -> dict:
    """Map Text Service I-series response to Layout Service slide format."""
    config = ISERIES_CONFIGS[layout_type]

    return {
        "layout": config["layout_name"],
        "content": {
            "slide_title": content["title"],
            "subtitle": content["subtitle"],
            "image_url": text_response.get("image_url", ""),
            "body": text_response.get("content_html", ""),
            "presentation_name": "I-Series Variants Test"
        }
    }


def create_presentation(slides: list, title: str) -> str:
    """Create presentation in Layout Service and return URL."""
    print("\n  Creating presentation in Layout Service...")

    payload = {
        "title": title,
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
    print("  I-SERIES VARIANTS TEST - DECK GENERATION")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print("="*70)

    # Select 3 random layout types
    layout_types = random.sample(list(ISERIES_CONFIGS.keys()), 3)

    # Select random content for each
    contents = random.sample(SAMPLE_CONTENT, 3)

    print(f"\n  Selected layouts: {', '.join(layout_types)}")

    slides = []
    slide_info = []

    for i, (layout_type, content) in enumerate(zip(layout_types, contents), 1):
        config = ISERIES_CONFIGS[layout_type]

        # Pick a random compatible variant
        content_variant = random.choice(config["compatible_variants"])

        print(f"\n{'='*60}")
        print(f"  SLIDE {i}: {layout_type} - {content['title']}")
        print(f"  Variant: {content_variant}")
        print('='*60)

        # Generate slide from Text Service
        text_response = generate_iseries_slide(layout_type, content_variant, content, i)

        if not text_response:
            print(f"  FAILED to generate slide {i}")
            continue

        # Map to Layout Service format
        slide_payload = map_to_layout_service(text_response, layout_type, content)
        slides.append(slide_payload)

        slide_info.append({
            "slide": i,
            "layout": layout_type,
            "variant": content_variant,
            "title": content["title"],
            "image_fallback": text_response.get("image_fallback", False)
        })

    if not slides:
        print("\n  ERROR: No slides generated!")
        return None

    # Create presentation
    print(f"\n{'='*60}")
    print(f"  Creating presentation with {len(slides)} slides")
    print('='*60)

    title = f"I-Series Variants Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    url = create_presentation(slides, title)

    if url:
        print("\n" + "="*70)
        print("  SUCCESS!")
        print("="*70)
        print(f"\n  Presentation URL: {url}")
        print(f"\n  Slides generated:")
        for info in slide_info:
            fallback = " (fallback)" if info["image_fallback"] else ""
            print(f"    {info['slide']}. {info['layout']} + {info['variant']}: {info['title']}{fallback}")
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
