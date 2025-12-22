#!/usr/bin/env python3
"""
Publish the 4 generated templates to Railway as a presentation deck
"""
import requests
from pathlib import Path

RAILWAY_URL = "https://web-production-f0d13.up.railway.app"

def main():
    print("=" * 70)
    print("PUBLISHING 4 TEMPLATES TO RAILWAY")
    print("=" * 70)

    # Read the 4 generated HTML files
    template_dir = Path("generated_templates")

    templates = [
        ("grid_2x3_left", "Grid 2×3 Left-Aligned - 50% Gap Reduction"),
        ("grid_2x3_numbered", "Grid 2×3 Numbered - 25% Char Increase"),
        ("grid_3x2_numbered", "Grid 3×2 Numbered - 25% Char Increase"),
        ("grid_2x2_numbered", "Grid 2×2 Numbered - 25% Char Increase")
    ]

    slides = []
    for variant_id, title in templates:
        html_file = template_dir / f"{variant_id}.html"

        if not html_file.exists():
            print(f"⚠ File not found: {html_file}")
            continue

        with open(html_file, 'r') as f:
            html_content = f.read()

        slide = {
            "layout": "L25",  # Using L25 layout for main content
            "content": {
                "slide_title": title,
                "subtitle": f"Variant: {variant_id}",
                "rich_content": html_content,
                "presentation_name": "Remaining 4 Grid Templates - With Fixes",
                "logo": ""
            }
        }
        slides.append(slide)
        print(f"✓ Added {variant_id}")

    if not slides:
        print("\n❌ No slides to publish")
        return

    # Create presentation payload
    presentation = {
        "title": "Remaining 4 Grid Templates - With Fixes",
        "slides": slides
    }

    print(f"\nPublishing {len(slides)} slides to Railway...")

    # Post to Railway
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/presentations",
            json=presentation,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code in [200, 201]:
            data = response.json()
            presentation_id = data.get("id")
            url_path = data.get("url", f"/p/{presentation_id}")
            view_url = f"{RAILWAY_URL}{url_path}"

            print(f"\n{'='*70}")
            print(f"✅ SUCCESS!")
            print(f"{'='*70}")
            print(f"\n🌐 VIEW URL:")
            print(f"   {view_url}")
            print(f"\nPublished: {len(slides)}/4 templates")
            print(f"{'='*70}\n")
        else:
            print(f"\n❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
