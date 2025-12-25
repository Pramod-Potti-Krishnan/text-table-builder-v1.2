#!/usr/bin/env python3
"""
Phase 1 CSS Variable Theming Test

Tests the 5 pilot themed templates with dark/light mode variants.
Creates a presentation in Layout Service with 5 slides for visual validation.

Usage:
    # Set environment variable to enable themed templates
    USE_CSS_VARIABLES=true python3 tests/test_phase1_theming.py

    # Or with custom URLs:
    TEXT_SERVICE_URL=http://localhost:8000 LAYOUT_SERVICE_URL=http://localhost:8504 \
    USE_CSS_VARIABLES=true python3 tests/test_phase1_theming.py

Requirements:
    - Text Service running (local or production)
    - Layout Service running (local or production)
    - USE_CSS_VARIABLES=true in Text Service environment
"""

import os
import sys
import json
import httpx
import asyncio
import webbrowser
from datetime import datetime

# Service URLs (default to Railway production, can override with env vars)
TEXT_SERVICE_URL = os.getenv("TEXT_SERVICE_URL", "https://web-production-5daf.up.railway.app")
LAYOUT_SERVICE_URL = os.getenv("LAYOUT_SERVICE_URL", "https://web-production-f0d13.up.railway.app")

# Test configurations: 2 templates × 2-3 variants each = 5 slides
TEST_SLIDES = [
    # Slide 1: metrics_3col_c1 - Light Mode
    {
        "variant_id": "metrics_3col_c1",
        "layout_id": "C1",
        "slide_spec": {
            "slide_title": "Q4 2024 Performance Metrics",
            "slide_purpose": "Display key performance indicators for Q4",
            "key_message": "Strong growth across all metrics",
            "tone": "professional",
            "audience": "executive leadership"
        },
        "theme_settings": {
            "theme_id": "corporate-blue",
            "theme_mode": "light"
        },
        "slide_label": "Metrics - Light Mode"
    },
    # Slide 2: metrics_3col_c1 - Dark Mode
    {
        "variant_id": "metrics_3col_c1",
        "layout_id": "C1",
        "slide_spec": {
            "slide_title": "Q4 2024 Performance Metrics",
            "slide_purpose": "Display key performance indicators for Q4",
            "key_message": "Strong growth across all metrics",
            "tone": "professional",
            "audience": "executive leadership"
        },
        "theme_settings": {
            "theme_id": "corporate-blue",
            "theme_mode": "dark"
        },
        "slide_label": "Metrics - Dark Mode"
    },
    # Slide 3: comparison_3col_c1 - Light Mode
    {
        "variant_id": "comparison_3col_c1",
        "layout_id": "C1",
        "slide_spec": {
            "slide_title": "Cloud Provider Comparison",
            "slide_purpose": "Compare AWS, Azure, and GCP capabilities",
            "key_message": "Each provider has unique strengths",
            "tone": "analytical",
            "audience": "technical decision makers"
        },
        "theme_settings": {
            "theme_id": "corporate-blue",
            "theme_mode": "light"
        },
        "slide_label": "Comparison - Light Mode"
    },
    # Slide 4: comparison_3col_c1 - Dark Mode
    {
        "variant_id": "comparison_3col_c1",
        "layout_id": "C1",
        "slide_spec": {
            "slide_title": "Cloud Provider Comparison",
            "slide_purpose": "Compare AWS, Azure, and GCP capabilities",
            "key_message": "Each provider has unique strengths",
            "tone": "analytical",
            "audience": "technical decision makers"
        },
        "theme_settings": {
            "theme_id": "corporate-blue",
            "theme_mode": "dark"
        },
        "slide_label": "Comparison - Dark Mode"
    },
    # Slide 5: grid_2x2_centered_c1 - Dark Mode (bonus)
    {
        "variant_id": "grid_2x2_centered_c1",
        "layout_id": "C1",
        "slide_spec": {
            "slide_title": "Strategic Priorities",
            "slide_purpose": "Outline 2025 focus areas",
            "key_message": "Four key areas driving growth",
            "tone": "strategic",
            "audience": "board members"
        },
        "theme_settings": {
            "theme_id": "corporate-blue",
            "theme_mode": "dark"
        },
        "slide_label": "Grid - Dark Mode"
    }
]


async def generate_slide_content(client: httpx.AsyncClient, config: dict) -> dict:
    """Call Text Service to generate slide content."""
    print(f"\n  Generating: {config['slide_label']}")
    print(f"    Variant: {config['variant_id']}")
    print(f"    Theme Mode: {config['theme_settings']['theme_mode']}")

    payload = {
        "variant_id": config["variant_id"],
        "layout_id": config.get("layout_id", "C1"),
        "slide_spec": config["slide_spec"],
        "theme_settings": config["theme_settings"],
        "enable_parallel": True,
        "validate_character_counts": False
    }

    try:
        response = await client.post(
            f"{TEXT_SERVICE_URL}/v1.2/generate",
            json=payload,
            timeout=120.0
        )
        response.raise_for_status()
        result = response.json()

        # Text Service returns "html" not "html_content"
        html_content = result.get("html") or result.get("html_content", "")

        # Check if themed template was used (look for CSS variables)
        uses_css_vars = "var(--" in html_content
        print(f"    ✓ Generated ({len(html_content)} chars)")
        print(f"    CSS Variables: {'Yes ✓' if uses_css_vars else 'No (using fallback template)'}")

        return {
            "success": True,
            "html_content": html_content,
            "uses_css_variables": uses_css_vars,
            "label": config["slide_label"],
            "theme_mode": config["theme_settings"]["theme_mode"]
        }

    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.json()
        except:
            error_detail = e.response.text[:200]
        print(f"    ✗ HTTP Error: {e.response.status_code}")
        print(f"    Detail: {error_detail}")
        return {
            "success": False,
            "error": str(e),
            "label": config["slide_label"]
        }
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "label": config["slide_label"]
        }


async def create_presentation(client: httpx.AsyncClient, slides: list) -> dict:
    """Create presentation in Layout Service with generated slides."""
    print("\n📦 Creating presentation in Layout Service...")

    # Build slides array for presentation
    presentation_slides = []
    for i, slide in enumerate(slides):
        if slide["success"]:
            # Determine background based on theme_mode
            bg_color = "#0f172a" if slide["theme_mode"] == "dark" else "#ffffff"

            presentation_slides.append({
                "layout": "L25",  # Main Content Shell layout
                "content": {
                    "slide_title": slide["label"],  # L25 expects slide_title
                    "rich_content": slide["html_content"]  # L25 expects rich_content, NOT body_content
                },
                "background": {
                    "type": "solid",
                    "color": bg_color
                },
                "notes": f"Test slide: {slide['label']}"
            })

    payload = {
        "title": f"Phase 1 Theming Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "slides": presentation_slides,
        "theme": {
            "theme_id": "corporate-blue",
            "theme_mode": "light"  # Default, individual slides have their own backgrounds
        }
    }

    try:
        response = await client.post(
            f"{LAYOUT_SERVICE_URL}/api/presentations",
            json=payload,
            timeout=60.0
        )
        response.raise_for_status()
        result = response.json()

        presentation_id = result.get("id")
        print(f"  ✓ Created presentation: {presentation_id}")

        return {
            "success": True,
            "presentation_id": presentation_id,
            "slide_count": len(presentation_slides)
        }

    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.json()
        except:
            error_detail = e.response.text[:500]
        print(f"  ✗ HTTP Error: {e.response.status_code}")
        print(f"  Detail: {error_detail}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        print(f"  ✗ Error creating presentation: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def main():
    print("=" * 60)
    print("Phase 1 CSS Variable Theming Test")
    print("=" * 60)
    print(f"\nText Service:   {TEXT_SERVICE_URL}")
    print(f"Layout Service: {LAYOUT_SERVICE_URL}")
    print(f"Test Slides:    {len(TEST_SLIDES)}")

    # Check if CSS variables are enabled
    use_css_vars = os.getenv("USE_CSS_VARIABLES", "false").lower() == "true"
    print(f"\nUSE_CSS_VARIABLES: {use_css_vars}")
    if not use_css_vars:
        print("⚠️  Warning: USE_CSS_VARIABLES is not enabled in this process!")
        print("   Note: The Text Service must have this enabled in its environment.")

    print("\n" + "-" * 60)
    print("Step 1: Generate slide content from Text Service")
    print("-" * 60)

    async with httpx.AsyncClient() as client:
        # Generate all slides
        slides = []
        for config in TEST_SLIDES:
            result = await generate_slide_content(client, config)
            slides.append(result)

        # Summary
        successful = sum(1 for s in slides if s["success"])
        css_var_count = sum(1 for s in slides if s.get("uses_css_variables", False))

        print(f"\n  Summary: {successful}/{len(slides)} slides generated")
        print(f"  Using CSS Variables: {css_var_count}/{successful}")

        if successful == 0:
            print("\n❌ No slides generated. Check service connectivity.")
            return

        print("\n" + "-" * 60)
        print("Step 2: Create presentation in Layout Service")
        print("-" * 60)

        result = await create_presentation(client, slides)

        if result["success"]:
            presentation_id = result["presentation_id"]
            viewer_url = f"{LAYOUT_SERVICE_URL}/p/{presentation_id}#/1"

            print("\n" + "=" * 60)
            print("✅ Test Complete!")
            print("=" * 60)
            print(f"\nPresentation ID: {presentation_id}")
            print(f"Slides Created:  {result['slide_count']}")
            print(f"\n🔗 Viewer URL:")
            print(f"   {viewer_url}")

            # Open in browser
            print("\n📖 Opening in browser...")
            webbrowser.open(viewer_url)

        else:
            print(f"\n❌ Failed to create presentation: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())
