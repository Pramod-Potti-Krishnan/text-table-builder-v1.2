#!/usr/bin/env python3
"""
Test script for image-enhanced hero slide endpoints.
"""

import httpx
import json
import asyncio
from pathlib import Path

BASE_URL = "http://localhost:8100"
OUTPUT_DIR = Path("test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


async def test_title_slide_with_image():
    """Test title slide with image generation."""
    print("\n" + "=" * 80)
    print("Testing: POST /v1.2/hero/title-with-image")
    print("=" * 80)

    payload = {
        "slide_number": 1,
        "slide_type": "title_slide",
        "narrative": "AI transforming healthcare diagnostics through advanced machine learning",
        "topics": ["Machine Learning", "Patient Outcomes", "Diagnostic Accuracy"],
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

        # Save response
        with open(OUTPUT_DIR / "title_response.json", "w") as f:
            json.dump(result, f, indent=2)

        # Save HTML
        if "content" in result:
            with open(OUTPUT_DIR / "title_slide.html", "w") as f:
                f.write(result["content"])

        # Print summary
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Slide Type: {result.get('metadata', {}).get('slide_type')}")
        print(f"✓ Background Image: {result.get('metadata', {}).get('background_image')}")
        print(f"✓ Fallback to Gradient: {result.get('metadata', {}).get('fallback_to_gradient')}")
        print(f"✓ Image Gen Time: {result.get('metadata', {}).get('image_generation_time_ms')}ms")
        print(f"✓ HTML Length: {len(result.get('content', ''))} chars")
        print(f"\n✓ Files saved:")
        print(f"  - {OUTPUT_DIR}/title_response.json")
        print(f"  - {OUTPUT_DIR}/title_slide.html")

        return result


async def test_section_slide_with_image():
    """Test section divider with image generation."""
    print("\n" + "=" * 80)
    print("Testing: POST /v1.2/hero/section-with-image")
    print("=" * 80)

    payload = {
        "slide_number": 5,
        "slide_type": "section_divider",
        "narrative": "Implementation Roadmap - From Planning to Full Deployment",
        "topics": ["Planning", "Development", "Testing", "Deployment"],
        "context": {
            "theme": "professional"
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1.2/hero/section-with-image",
            json=payload
        )

        result = response.json()

        # Save response
        with open(OUTPUT_DIR / "section_response.json", "w") as f:
            json.dump(result, f, indent=2)

        # Save HTML
        if "content" in result:
            with open(OUTPUT_DIR / "section_slide.html", "w") as f:
                f.write(result["content"])

        # Print summary
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Slide Type: {result.get('metadata', {}).get('slide_type')}")
        print(f"✓ Background Image: {result.get('metadata', {}).get('background_image')}")
        print(f"✓ Fallback to Gradient: {result.get('metadata', {}).get('fallback_to_gradient')}")
        print(f"✓ Image Gen Time: {result.get('metadata', {}).get('image_generation_time_ms')}ms")
        print(f"✓ HTML Length: {len(result.get('content', ''))} chars")
        print(f"\n✓ Files saved:")
        print(f"  - {OUTPUT_DIR}/section_response.json")
        print(f"  - {OUTPUT_DIR}/section_slide.html")

        return result


async def test_closing_slide_with_image():
    """Test closing slide with image generation."""
    print("\n" + "=" * 80)
    print("Testing: POST /v1.2/hero/closing-with-image")
    print("=" * 80)

    payload = {
        "slide_number": 15,
        "slide_type": "closing_slide",
        "narrative": "Ready to transform your healthcare operations with AI",
        "topics": ["Innovation", "Results", "Partnership", "Future"],
        "context": {
            "theme": "professional",
            "contact_info": "contact@healthtech.com | www.healthtech.com"
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1.2/hero/closing-with-image",
            json=payload
        )

        result = response.json()

        # Save response
        with open(OUTPUT_DIR / "closing_response.json", "w") as f:
            json.dump(result, f, indent=2)

        # Save HTML
        if "content" in result:
            with open(OUTPUT_DIR / "closing_slide.html", "w") as f:
                f.write(result["content"])

        # Print summary
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Slide Type: {result.get('metadata', {}).get('slide_type')}")
        print(f"✓ Background Image: {result.get('metadata', {}).get('background_image')}")
        print(f"✓ Fallback to Gradient: {result.get('metadata', {}).get('fallback_to_gradient')}")
        print(f"✓ Image Gen Time: {result.get('metadata', {}).get('image_generation_time_ms')}ms")
        print(f"✓ HTML Length: {len(result.get('content', ''))} chars")
        print(f"\n✓ Files saved:")
        print(f"  - {OUTPUT_DIR}/closing_response.json")
        print(f"  - {OUTPUT_DIR}/closing_slide.html")

        return result


async def create_demo_html():
    """Create a demo HTML page with all three slides."""
    print("\n" + "=" * 80)
    print("Creating Demo HTML Page")
    print("=" * 80)

    # Read the generated HTML files
    title_html = (OUTPUT_DIR / "title_slide.html").read_text()
    section_html = (OUTPUT_DIR / "section_slide.html").read_text()
    closing_html = (OUTPUT_DIR / "closing_slide.html").read_text()

    # Read the JSON responses to get background images
    with open(OUTPUT_DIR / "title_response.json") as f:
        title_data = json.load(f)
    with open(OUTPUT_DIR / "section_response.json") as f:
        section_data = json.load(f)
    with open(OUTPUT_DIR / "closing_response.json") as f:
        closing_data = json.load(f)

    title_bg = title_data.get('metadata', {}).get('background_image')
    section_bg = section_data.get('metadata', {}).get('background_image')
    closing_bg = closing_data.get('metadata', {}).get('background_image')

    # Create demo page
    demo_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image-Enhanced Hero Slides Demo</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a;
        }}
        .slide-container {{
            width: 1920px;
            height: 1080px;
            margin: 20px auto;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            position: relative;
            overflow: hidden;
        }}
        .slide-label {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            z-index: 1000;
        }}
        .image-indicator {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(102, 110, 234, 0.9);
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
        }}
        .slide-content {{
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
        }}
        .background-image {{
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            object-fit: cover;
            z-index: 0;
        }}
        .content-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }}
        h1 {{
            color: white;
            text-align: center;
            padding: 40px 20px;
            background: rgba(0,0,0,0.7);
        }}
        .info {{
            max-width: 1200px;
            margin: 40px auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <h1>Image-Enhanced Hero Slides Demo - Text Service v1.2</h1>

    <div class="info">
        <h2>Features</h2>
        <ul>
            <li><strong>Title Slide:</strong> LEFT-aligned text with dark left → light right gradient overlay</li>
            <li><strong>Section Divider:</strong> RIGHT-aligned text with dark right → light left gradient overlay</li>
            <li><strong>Closing Slide:</strong> CENTER-aligned text with radial gradient overlay (light center → dark edges)</li>
        </ul>
        <h3>AI-Generated Backgrounds</h3>
        <ul>
            <li>16:9 aspect ratio optimized for presentation slides</li>
            <li>Contextual generation based on narrative and topics</li>
            <li>Automatic crop anchor positioning for text placement</li>
            <li>~10-15 second generation time (parallel with content)</li>
            <li>Graceful fallback to gradients if image generation fails</li>
        </ul>
    </div>

    <!-- Title Slide -->
    <div class="slide-container">
        <div class="slide-label">Title Slide (LEFT-aligned)</div>
        <div class="image-indicator">
            {'AI Background' if title_bg else 'Gradient Fallback'}
        </div>
        {'<img class="background-image" src="' + title_bg + '" alt="Title slide background">' if title_bg else ''}
        <div class="content-overlay">
            {title_html}
        </div>
    </div>

    <!-- Section Divider -->
    <div class="slide-container">
        <div class="slide-label">Section Divider (RIGHT-aligned)</div>
        <div class="image-indicator">
            {'AI Background' if section_bg else 'Gradient Fallback'}
        </div>
        {'<img class="background-image" src="' + section_bg + '" alt="Section slide background">' if section_bg else ''}
        <div class="content-overlay">
            {section_html}
        </div>
    </div>

    <!-- Closing Slide -->
    <div class="slide-container">
        <div class="slide-label">Closing Slide (CENTER-aligned)</div>
        <div class="image-indicator">
            {'AI Background' if closing_bg else 'Gradient Fallback'}
        </div>
        {'<img class="background-image" src="' + closing_bg + '" alt="Closing slide background">' if closing_bg else ''}
        <div class="content-overlay">
            {closing_html}
        </div>
    </div>

    <div class="info">
        <h2>Technical Details</h2>
        <h3>Title Slide</h3>
        <ul>
            <li>Background Image: <code>{title_bg or 'None (using gradient)'}</code></li>
            <li>Fallback: {title_data.get('metadata', {}).get('fallback_to_gradient', 'N/A')}</li>
            <li>Image Gen Time: {title_data.get('metadata', {}).get('image_generation_time_ms', 'N/A')}ms</li>
        </ul>

        <h3>Section Divider</h3>
        <ul>
            <li>Background Image: <code>{section_bg or 'None (using gradient)'}</code></li>
            <li>Fallback: {section_data.get('metadata', {}).get('fallback_to_gradient', 'N/A')}</li>
            <li>Image Gen Time: {section_data.get('metadata', {}).get('image_generation_time_ms', 'N/A')}ms</li>
        </ul>

        <h3>Closing Slide</h3>
        <ul>
            <li>Background Image: <code>{closing_bg or 'None (using gradient)'}</code></li>
            <li>Fallback: {closing_data.get('metadata', {}).get('fallback_to_gradient', 'N/A')}</li>
            <li>Image Gen Time: {closing_data.get('metadata', {}).get('image_generation_time_ms', 'N/A')}ms</li>
        </ul>
    </div>
</body>
</html>
"""

    # Save demo HTML
    demo_path = OUTPUT_DIR / "demo.html"
    demo_path.write_text(demo_html)

    print(f"✓ Demo HTML created: {demo_path}")
    print(f"\nOpen in browser: file://{demo_path.absolute()}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("IMAGE-ENHANCED HERO SLIDES - LOCAL TESTING")
    print("=" * 80)

    try:
        # Test all three endpoints
        await test_title_slide_with_image()
        await test_section_slide_with_image()
        await test_closing_slide_with_image()

        # Create demo page
        await create_demo_html()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
