#!/usr/bin/env python3
"""
Test Phase 2.5: Create presentation in Layout Service and open viewer
"""

import requests
import json
import subprocess

# Service URLs
TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

# Test variants
TEST_VARIANTS = [
    ("hybrid_left_2x2_c1", "Hybrid - Fix A"),
    ("grid_2x3_c1", "Grid - Fix B"),
    ("sequential_4col_c1", "Sequential - Fix B"),
    ("asymmetric_8_4_4section_c1", "Asymmetric - Fix A"),
]

def generate_slide(variant_id: str) -> dict:
    """Generate a slide with the given variant."""
    payload = {
        "variant_id": variant_id,
        "layout_id": "C1",
        "slide_spec": {
            "slide_title": f"Light Box Test: {variant_id}",
            "slide_purpose": "Testing CSS variable theming for dark mode",
            "key_message": "All text should switch to white in dark mode",
            "tone": "professional",
            "audience": "developers"
        },
        "presentation_spec": {
            "presentation_title": "Phase 2.5 Test",
            "presentation_type": "Test"
        },
        "theme_config": {
            "theme_id": "default",
            "theme_mode": "dark"
        }
    }

    response = requests.post(
        f"{TEXT_SERVICE_URL}/v1.2/generate",
        json=payload,
        timeout=90
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def create_presentation():
    """Create presentation with slides."""

    # First, generate all slides
    slides = []
    for variant_id, description in TEST_VARIANTS:
        print(f"Generating {variant_id}...")

        result = generate_slide(variant_id)

        if result and result.get("success"):
            html_content = result.get("html", "")
            slides.append({
                "layout": "L25",
                "content": {
                    "slide_title": f"{description}",
                    "rich_content": html_content
                },
                "background": {
                    "type": "solid",
                    "color": "#ffffff"  # Light background
                },
                "notes": f"Test: {variant_id}"
            })
            print(f"  Generated: {description}")
        else:
            print(f"  Failed to generate: {variant_id}")

    if not slides:
        print("No slides generated!")
        return None

    # Create presentation with all slides
    print(f"\nCreating presentation with {len(slides)} slides...")

    payload = {
        "title": "Light Box Fix Test - Phase 2.5",
        "slides": slides,
        "theme": {
            "theme_id": "default",
            "theme_mode": "light"
        }
    }

    create_resp = requests.post(
        f"{LAYOUT_SERVICE_URL}/api/presentations",
        json=payload,
        timeout=60
    )

    if create_resp.status_code != 200:
        print(f"Failed to create presentation: {create_resp.status_code} - {create_resp.text}")
        return None

    pres_data = create_resp.json()
    pres_id = pres_data["id"]
    print(f"Created presentation: {pres_id}")

    # Return viewer URL
    viewer_url = f"{LAYOUT_SERVICE_URL}/p/{pres_id}"
    return viewer_url

def main():
    print("=" * 60)
    print("PHASE 2.5: LIGHT BOX FIX - LAYOUT SERVICE VIEWER")
    print("=" * 60)

    viewer_url = create_presentation()

    if viewer_url:
        print(f"\n{'=' * 60}")
        print(f"VIEWER URL: {viewer_url}")
        print(f"{'=' * 60}")
        print("\nOpening in browser...")
        print("\nInstructions:")
        print("  - Use arrow keys to navigate slides")
        print("  - Press '1' for Light mode")
        print("  - Press '2' for Dark mode")
        print("  - In dark mode, ALL text should be WHITE")

        # Open in browser
        subprocess.run(["open", viewer_url])

        return viewer_url
    else:
        print("Failed to create presentation")
        return None

if __name__ == "__main__":
    main()
