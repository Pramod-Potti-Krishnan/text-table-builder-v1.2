#!/usr/bin/env python3
"""
Test script to verify background image injection fix.

Tests all three image-enhanced hero slide endpoints to verify:
1. Image is generated successfully
2. background-image: url(...) is embedded in the HTML content
3. metadata.background_image is still populated
4. visual_style parameter works correctly
"""

import httpx
import json
import asyncio
from pathlib import Path

BASE_URL = "http://localhost:8100"
OUTPUT_DIR = Path("test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


async def test_title_slide_with_image():
    """Test title slide with image - verify background-image in HTML."""
    print("\n" + "=" * 80)
    print("Testing Title Slide with Image")
    print("=" * 80)

    payload = {
        "slide_number": 1,
        "slide_type": "title_slide",
        "narrative": "AI transforming healthcare diagnostics through advanced machine learning",
        "topics": ["Machine Learning", "Patient Outcomes", "Diagnostic Accuracy"],
        "visual_style": "professional",  # Test visual style
        "context": {
            "theme": "professional",
            "audience": "healthcare professionals",
            "presentation_title": "AI in Healthcare: Transforming Diagnostics"
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1.2/hero/title-with-image",
            json=payload
        )

        result = response.json()
        content = result.get("content", "")
        metadata = result.get("metadata", {})

        # Check if background-image is in HTML
        has_bg_image_in_html = "background-image: url(" in content
        bg_url = metadata.get("background_image")
        fallback = metadata.get("fallback_to_gradient", True)

        print(f"✓ Status: {response.status_code}")
        print(f"✓ Fallback to Gradient: {fallback}")
        print(f"✓ Background URL in metadata: {bg_url is not None}")
        print(f"✓ background-image in HTML: {has_bg_image_in_html}")

        if has_bg_image_in_html:
            print("  ✅ SUCCESS: Background image is embedded in HTML!")
        else:
            print("  ❌ FAILURE: Background image NOT in HTML!")

        # Save for inspection
        with open(OUTPUT_DIR / "title_injection_test.html", "w") as f:
            f.write(content)

        return has_bg_image_in_html and not fallback


async def test_section_divider_with_image():
    """Test section divider with image - verify background-image in HTML."""
    print("\n" + "=" * 80)
    print("Testing Section Divider with Image")
    print("=" * 80)

    payload = {
        "slide_number": 5,
        "slide_type": "section_divider",
        "narrative": "Implementation roadmap and deployment strategy",
        "topics": ["Deployment", "Timeline", "Milestones"],
        "visual_style": "professional",
        "context": {
            "theme": "tech",
            "audience": "engineering team"
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1.2/hero/section-with-image",
            json=payload
        )

        result = response.json()
        content = result.get("content", "")
        metadata = result.get("metadata", {})

        has_bg_image_in_html = "background-image: url(" in content
        bg_url = metadata.get("background_image")
        fallback = metadata.get("fallback_to_gradient", True)

        print(f"✓ Status: {response.status_code}")
        print(f"✓ Fallback to Gradient: {fallback}")
        print(f"✓ Background URL in metadata: {bg_url is not None}")
        print(f"✓ background-image in HTML: {has_bg_image_in_html}")

        if has_bg_image_in_html:
            print("  ✅ SUCCESS: Background image is embedded in HTML!")
        else:
            print("  ❌ FAILURE: Background image NOT in HTML!")

        with open(OUTPUT_DIR / "section_injection_test.html", "w") as f:
            f.write(content)

        return has_bg_image_in_html and not fallback


async def test_closing_slide_with_image():
    """Test closing slide with image - verify background-image in HTML."""
    print("\n" + "=" * 80)
    print("Testing Closing Slide with Image")
    print("=" * 80)

    payload = {
        "slide_number": 15,
        "slide_type": "closing_slide",
        "narrative": "Ready to transform your healthcare operations with AI",
        "topics": ["AI Diagnostics", "Patient Outcomes", "Future of Healthcare"],
        "visual_style": "professional",
        "context": {
            "theme": "professional",
            "audience": "healthcare executives",
            "contact_info": "dr.jane@company.com | linkedin.com/in/drjane"
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1.2/hero/closing-with-image",
            json=payload
        )

        result = response.json()
        content = result.get("content", "")
        metadata = result.get("metadata", {})

        has_bg_image_in_html = "background-image: url(" in content
        bg_url = metadata.get("background_image")
        fallback = metadata.get("fallback_to_gradient", True)

        print(f"✓ Status: {response.status_code}")
        print(f"✓ Fallback to Gradient: {fallback}")
        print(f"✓ Background URL in metadata: {bg_url is not None}")
        print(f"✓ background-image in HTML: {has_bg_image_in_html}")

        if has_bg_image_in_html:
            print("  ✅ SUCCESS: Background image is embedded in HTML!")
        else:
            print("  ❌ FAILURE: Background image NOT in HTML!")

        with open(OUTPUT_DIR / "closing_injection_test.html", "w") as f:
            f.write(content)

        return has_bg_image_in_html and not fallback


async def test_visual_styles():
    """Test different visual styles (Ghibli, professional, kids)."""
    print("\n" + "=" * 80)
    print("Testing Visual Styles")
    print("=" * 80)

    styles = ["professional", "illustrated", "kids"]
    results = {}

    for style in styles:
        payload = {
            "slide_number": 1,
            "slide_type": "title_slide",
            "narrative": "Adventure in learning new technologies",
            "topics": ["Innovation", "Learning", "Growth"],
            "visual_style": style,
            "context": {
                "theme": "creative",
                "audience": "general"
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/v1.2/hero/title-with-image",
                json=payload
            )

            result = response.json()
            metadata = result.get("metadata", {})

            has_bg = "background-image: url(" in result.get("content", "")
            fallback = metadata.get("fallback_to_gradient", True)

            results[style] = has_bg and not fallback

            status = "✅" if results[style] else "❌"
            print(f"  {status} {style}: background-image={has_bg}, fallback={fallback}")

            # Save each style
            with open(OUTPUT_DIR / f"style_{style}_test.html", "w") as f:
                f.write(result.get("content", ""))

    return all(results.values())


async def main():
    """Run all tests."""
    print("=" * 80)
    print("BACKGROUND IMAGE INJECTION TEST")
    print("=" * 80)
    print(f"Testing against: {BASE_URL}")

    results = []

    # Test each endpoint
    results.append(("Title Slide", await test_title_slide_with_image()))
    results.append(("Section Divider", await test_section_divider_with_image()))
    results.append(("Closing Slide", await test_closing_slide_with_image()))
    results.append(("Visual Styles", await test_visual_styles()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("ALL TESTS PASSED! Background images are now embedded in HTML.")
    else:
        print("SOME TESTS FAILED! Check output files in test_outputs/")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
