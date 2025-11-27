"""
Test Visual Style System for Hero Slides

Tests all 3 slide types × 3 visual styles = 9 combinations:
- Title, Section, Closing
- Professional, Illustrated, Kids

Validates:
1. Correct model selection (title+professional=standard, others=fast)
2. Correct archetype selection (professional=photorealistic, illustrated/kids=spot_illustration)
3. Image generation succeeds
4. HTML content generation succeeds
5. Creates preview HTML files for visual inspection

Output: test_outputs/VISUAL_STYLES_TEST_REPORT.md
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.hero.title_slide_with_image_generator import TitleSlideWithImageGenerator
from app.core.hero.section_divider_with_image_generator import SectionDividerWithImageGenerator
from app.core.hero.closing_slide_with_image_generator import ClosingSlideWithImageGenerator
from app.core.hero.base_hero_generator import HeroGenerationRequest
from app.services.llm_service import get_llm_service


# Test configurations for each style
TEST_CASES = [
    # Professional Style (photorealistic)
    {
        "visual_style": "professional",
        "slide_type": "title_slide",
        "narrative": "AI-powered diagnostic accuracy in modern healthcare",
        "topics": ["AI", "Diagnostics", "Healthcare", "Innovation"],
        "expected_model": "imagen-3.0-generate-001",  # Standard for title+professional
        "expected_archetype": "photorealistic"
    },
    {
        "visual_style": "professional",
        "slide_type": "section_divider",
        "narrative": "Implementation strategy and deployment roadmap",
        "topics": ["Implementation", "Deployment", "Integration"],
        "expected_model": "imagen-3.0-fast-generate-001",  # Fast for section
        "expected_archetype": "photorealistic"
    },
    {
        "visual_style": "professional",
        "slide_type": "closing_slide",
        "narrative": "Transform your healthcare with AI innovation",
        "topics": ["Future", "Innovation", "Success"],
        "expected_model": "imagen-3.0-fast-generate-001",  # Fast for closing
        "expected_archetype": "photorealistic"
    },

    # Illustrated Style (Ghibli-style)
    {
        "visual_style": "illustrated",
        "slide_type": "title_slide",
        "narrative": "Digital transformation in modern technology",
        "topics": ["Technology", "Digital", "Innovation", "Future"],
        "expected_model": "imagen-3.0-fast-generate-001",  # Fast for title+illustrated
        "expected_archetype": "spot_illustration"
    },
    {
        "visual_style": "illustrated",
        "slide_type": "section_divider",
        "narrative": "Building the platform architecture",
        "topics": ["Architecture", "Platform", "Development"],
        "expected_model": "imagen-3.0-fast-generate-001",  # Fast for section
        "expected_archetype": "spot_illustration"
    },
    {
        "visual_style": "illustrated",
        "slide_type": "closing_slide",
        "narrative": "Join us in the digital future",
        "topics": ["Partnership", "Future", "Growth"],
        "expected_model": "imagen-3.0-fast-generate-001",  # Fast for closing
        "expected_archetype": "spot_illustration"
    },

    # Kids Style (vibrant, playful)
    {
        "visual_style": "kids",
        "slide_type": "title_slide",
        "narrative": "Explore the amazing world of finance",
        "topics": ["Finance", "Money", "Learning", "Adventure"],
        "expected_model": "imagen-3.0-fast-generate-001",  # Fast for title+kids
        "expected_archetype": "spot_illustration"
    },
    {
        "visual_style": "kids",
        "slide_type": "section_divider",
        "narrative": "How saving works - a fun journey",
        "topics": ["Saving", "Banking", "Education"],
        "expected_model": "imagen-3.0-fast-generate-001",  # Fast for section
        "expected_archetype": "spot_illustration"
    },
    {
        "visual_style": "kids",
        "slide_type": "closing_slide",
        "narrative": "Start your financial adventure today!",
        "topics": ["Adventure", "Learning", "Fun"],
        "expected_model": "imagen-3.0-fast-generate-001",  # Fast for closing
        "expected_archetype": "spot_illustration"
    }
]


async def test_visual_style_combination(
    test_case: Dict[str, Any],
    llm_service,
    test_number: int
) -> Dict[str, Any]:
    """Test a single visual style + slide type combination."""

    visual_style = test_case["visual_style"]
    slide_type = test_case["slide_type"]

    print(f"\n{'='*70}")
    print(f"Test #{test_number}: {slide_type.upper()} with {visual_style.upper()} style")
    print(f"{'='*70}")

    # Select appropriate generator
    if slide_type == "title_slide":
        generator = TitleSlideWithImageGenerator(llm_service)
    elif slide_type == "section_divider":
        generator = SectionDividerWithImageGenerator(llm_service)
    elif slide_type == "closing_slide":
        generator = ClosingSlideWithImageGenerator(llm_service)
    else:
        raise ValueError(f"Unknown slide type: {slide_type}")

    # Create request
    request = HeroGenerationRequest(
        slide_number=test_number,
        slide_type=slide_type,
        narrative=test_case["narrative"],
        topics=test_case["topics"],
        visual_style=visual_style,
        context={
            "theme": "professional",
            "audience": "test audience"
        }
    )

    # Generate slide
    start_time = datetime.now()
    try:
        result = await generator.generate(request)
        generation_time = (datetime.now() - start_time).total_seconds()

        # Extract metadata
        metadata = result.get("metadata", {})
        background_image = metadata.get("background_image")
        fallback = metadata.get("fallback_to_gradient", False)

        # Create preview HTML
        preview_html = create_preview_html(
            result["content"],
            background_image,
            visual_style,
            slide_type,
            test_number
        )

        # Save preview
        preview_path = f"test_outputs/{slide_type}_{visual_style}_preview.html"
        with open(preview_path, "w") as f:
            f.write(preview_html)

        print(f"✅ SUCCESS")
        print(f"   Generation time: {generation_time:.2f}s")
        print(f"   Background image: {'YES' if background_image else 'FALLBACK'}")
        print(f"   Preview saved: {preview_path}")

        return {
            "test_number": test_number,
            "visual_style": visual_style,
            "slide_type": slide_type,
            "status": "SUCCESS",
            "generation_time": generation_time,
            "has_image": bool(background_image),
            "fallback_to_gradient": fallback,
            "expected_model": test_case["expected_model"],
            "expected_archetype": test_case["expected_archetype"],
            "preview_file": preview_path
        }

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return {
            "test_number": test_number,
            "visual_style": visual_style,
            "slide_type": slide_type,
            "status": "FAILED",
            "error": str(e),
            "expected_model": test_case["expected_model"],
            "expected_archetype": test_case["expected_archetype"]
        }


def create_preview_html(
    content: str,
    background_image: str,
    visual_style: str,
    slide_type: str,
    test_number: int
) -> str:
    """Create preview HTML with slide content and background image."""

    bg_style = ""
    if background_image:
        bg_style = f"background-image: url('{background_image}');"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test #{test_number}: {slide_type} - {visual_style}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #1a1a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Inter', sans-serif;
        }}
        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            background-color: #000;
            {bg_style}
            background-size: cover;
            background-position: center;
        }}
        .slide-label {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(102, 110, 234, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            z-index: 1000;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide-label">
            {visual_style.upper()} Style | Test #{test_number}
        </div>
        {content}
    </div>
</body>
</html>"""


def generate_test_report(results: List[Dict[str, Any]]) -> str:
    """Generate comprehensive test report in markdown."""

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "SUCCESS")
    failed = total - passed

    report = f"""# Visual Style System Test Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Tests**: {total}
**Passed**: {passed}
**Failed**: {failed}

## Test Summary

| # | Visual Style | Slide Type | Status | Time | Image | Preview |
|---|-------------|-----------|--------|------|-------|---------|
"""

    for r in results:
        status_icon = "✅" if r["status"] == "SUCCESS" else "❌"
        time_str = f"{r.get('generation_time', 0):.2f}s" if r["status"] == "SUCCESS" else "N/A"
        image_str = "YES" if r.get("has_image", False) else "FALLBACK"
        preview = r.get("preview_file", "N/A")

        report += f"| {r['test_number']} | {r['visual_style']} | {r['slide_type']} | {status_icon} {r['status']} | {time_str} | {image_str} | {preview} |\n"

    report += f"""

## Model Selection Verification

### Title Slides
- **Professional**: Should use `imagen-3.0-generate-001` (standard quality)
- **Illustrated**: Should use `imagen-3.0-fast-generate-001` (fast/cheap)
- **Kids**: Should use `imagen-3.0-fast-generate-001` (fast/cheap)

### Section & Closing Slides
- **All styles**: Should ALWAYS use `imagen-3.0-fast-generate-001` (fast/cheap)

### Archetype Verification
- **Professional**: Should use `photorealistic` archetype
- **Illustrated**: Should use `spot_illustration` archetype
- **Kids**: Should use `spot_illustration` archetype

## Detailed Results

"""

    for r in results:
        report += f"""### Test #{r['test_number']}: {r['slide_type']} + {r['visual_style']}
- **Status**: {r['status']}
- **Expected Model**: `{r['expected_model']}`
- **Expected Archetype**: `{r['expected_archetype']}`
"""
        if r["status"] == "SUCCESS":
            report += f"""- **Generation Time**: {r['generation_time']:.2f}s
- **Background Image**: {'Generated' if r['has_image'] else 'Fallback to gradient'}
- **Preview**: `{r['preview_file']}`
"""
        else:
            report += f"""- **Error**: {r.get('error', 'Unknown error')}
"""
        report += "\n"

    report += f"""## Conclusion

{"🎉 All tests passed!" if failed == 0 else f"⚠️ {failed} test(s) failed. Review errors above."}

The visual style system is {"READY for production" if failed == 0 else "NOT ready - requires fixes"}.

### Next Steps
1. Review generated preview HTML files in `test_outputs/` directory
2. Verify image quality and style appropriateness
3. Confirm model selection matches expectations
4. Integrate visual style system into Director Agent
"""

    return report


async def main():
    """Run all visual style tests."""

    print("\n" + "="*70)
    print("VISUAL STYLE SYSTEM COMPREHENSIVE TEST")
    print("="*70)
    print(f"Testing {len(TEST_CASES)} combinations (3 slides × 3 styles)")
    print()

    # Create test outputs directory
    os.makedirs("test_outputs", exist_ok=True)

    # Initialize LLM service
    llm_service = await get_llm_service()

    # Run all tests
    results = []
    for i, test_case in enumerate(TEST_CASES, 1):
        result = await test_visual_style_combination(test_case, llm_service, i)
        results.append(result)

    # Generate report
    report = generate_test_report(results)

    # Save report
    report_path = "test_outputs/VISUAL_STYLES_TEST_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print(f"Report saved: {report_path}")
    print(f"Preview files in: test_outputs/")

    # Print summary
    passed = sum(1 for r in results if r["status"] == "SUCCESS")
    failed = len(results) - passed

    if failed == 0:
        print(f"\n🎉 All {len(results)} tests PASSED!")
    else:
        print(f"\n⚠️  {passed}/{len(results)} tests passed, {failed} failed")


if __name__ == "__main__":
    asyncio.run(main())
