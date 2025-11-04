#!/usr/bin/env python3
"""
Publish the 3 comparison templates to Railway as a presentation deck
"""
import requests
from pathlib import Path

RAILWAY_URL = "https://web-production-f0d13.up.railway.app"

def main():
    print("=" * 70)
    print("PUBLISHING 3 COMPARISON TEMPLATES TO RAILWAY")
    print("=" * 70)

    # Read the 3 generated HTML files
    template_dir = Path("generated_templates")

    templates = [
        ("comparison_2col", "Comparison 2 Columns - Traditional vs Digital Marketing"),
        ("comparison_3col", "Comparison 3 Columns - Startup Growth Stages"),
        ("comparison_4col", "Comparison 4 Columns - Product Tier Comparison")
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
                "presentation_name": "Comparison Layouts - 3 Variants",
                "company_logo": ""
            }
        }
        slides.append(slide)
        print(f"✓ Added {variant_id}")

    if not slides:
        print("\n❌ No slides to publish")
        return

    # Create presentation payload
    presentation = {
        "title": "Comparison Layouts - 3 Variants",
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
            print(f"\nPublished: {len(slides)}/3 templates")
            print(f"{'='*70}\n")
        else:
            print(f"\n❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
