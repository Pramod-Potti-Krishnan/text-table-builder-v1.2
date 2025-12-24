"""
Test I-Series Content Variants

Tests 3 random I-series content variants with the new content_variant parameter.
Each variant uses reduced character counts appropriate for image+content layouts.

Usage:
    python tests/test_iseries_variants.py
"""

import asyncio
import httpx
import json
import random
import time
from datetime import datetime

# Service URLs
TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"

# All available I-series variants
ISERIES_VARIANTS = [
    # Single Column variants
    {"variant_id": "single_column_3section_i1", "layout_type": "I1", "description": "3 sections, 4 bullets, wide image"},
    {"variant_id": "single_column_3section_i3", "layout_type": "I3", "description": "3 sections, 4 bullets, narrow image"},
    {"variant_id": "single_column_4section_i1", "layout_type": "I1", "description": "4 sections, 3 bullets, wide image"},
    {"variant_id": "single_column_4section_i3", "layout_type": "I3", "description": "4 sections, 3 bullets, narrow image"},
    {"variant_id": "single_column_5section_i1", "layout_type": "I1", "description": "5 sections, 2 bullets, wide image"},
    {"variant_id": "single_column_5section_i3", "layout_type": "I3", "description": "5 sections, 2 bullets, narrow image"},
    # Comparison variants
    {"variant_id": "comparison_2col_i1", "layout_type": "I1", "description": "2 columns comparison, wide image"},
    {"variant_id": "comparison_2col_i3", "layout_type": "I3", "description": "2 columns comparison, narrow image"},
    {"variant_id": "comparison_3col_i1", "layout_type": "I2", "description": "3 columns comparison, wide image"},
    {"variant_id": "comparison_3col_i3", "layout_type": "I4", "description": "3 columns comparison, narrow image"},
    # Sequential variants
    {"variant_id": "sequential_2col_i1", "layout_type": "I1", "description": "2 steps sequential, wide image"},
    {"variant_id": "sequential_2col_i3", "layout_type": "I3", "description": "2 steps sequential, narrow image"},
    {"variant_id": "sequential_3col_i1", "layout_type": "I2", "description": "3 steps sequential, wide image"},
    {"variant_id": "sequential_3col_i3", "layout_type": "I4", "description": "3 steps sequential, narrow image"},
]

# Sample narratives for testing
SAMPLE_NARRATIVES = [
    {
        "title": "Digital Transformation Strategy",
        "narrative": "Modern enterprises must embrace digital transformation to stay competitive. Key areas include cloud migration, AI integration, and process automation.",
        "topics": ["Cloud Infrastructure", "AI/ML Adoption", "Process Automation", "Data Analytics", "Security"]
    },
    {
        "title": "Sustainable Business Practices",
        "narrative": "Implementing sustainable practices drives long-term value through reduced costs, improved brand reputation, and regulatory compliance.",
        "topics": ["Carbon Footprint Reduction", "Renewable Energy", "Circular Economy", "ESG Reporting", "Green Supply Chain"]
    },
    {
        "title": "Customer Experience Excellence",
        "narrative": "Exceptional customer experience differentiates leading brands. Focus on personalization, omnichannel engagement, and proactive service.",
        "topics": ["Personalization", "Omnichannel Strategy", "Self-Service", "Feedback Loops", "Loyalty Programs"]
    }
]


async def test_variant(client: httpx.AsyncClient, variant: dict, narrative: dict, slide_num: int) -> dict:
    """
    Test a single I-series variant.

    Args:
        client: HTTP client
        variant: Variant config with variant_id and layout_type
        narrative: Test narrative with title, narrative, topics
        slide_num: Slide number for the request

    Returns:
        Test result dict
    """
    print(f"\n{'='*60}")
    print(f"Testing: {variant['variant_id']}")
    print(f"Layout: {variant['layout_type']} - {variant['description']}")
    print(f"{'='*60}")

    request_payload = {
        "slide_number": slide_num,
        "layout_type": variant["layout_type"],
        "title": narrative["title"],
        "narrative": narrative["narrative"],
        "topics": narrative["topics"][:4],  # Limit topics
        "visual_style": "illustrated",
        "content_style": "bullets",
        "content_variant": variant["variant_id"]  # NEW: Using content_variant
    }

    print(f"\nRequest payload:")
    print(json.dumps(request_payload, indent=2))

    start_time = time.time()

    try:
        response = await client.post(
            f"{TEXT_SERVICE_URL}/v1.2/iseries/generate",
            json=request_payload,
            timeout=120.0
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        if response.status_code == 200:
            result = response.json()

            print(f"\n[SUCCESS] Generated in {elapsed_ms}ms")
            print(f"  - Image URL: {result.get('image_url', 'None (fallback)')[:80]}...")
            print(f"  - Image fallback: {result.get('image_fallback', False)}")
            print(f"  - Background: {result.get('background_color', '#ffffff')}")

            # Show metadata
            metadata = result.get("metadata", {})
            print(f"\n  Metadata:")
            print(f"    - Layout type: {metadata.get('layout_type')}")
            print(f"    - Generation mode: {metadata.get('generation_mode', 'unknown')}")
            print(f"    - Generation time: {metadata.get('generation_time_ms', 0)}ms")

            # Check for variant spec in metadata
            variant_spec = metadata.get("variant_spec", {})
            if variant_spec:
                print(f"    - Variant ID: {variant_spec.get('variant_id')}")
                print(f"    - I-Series layout: {variant_spec.get('iseries_layout')}")
                print(f"    - Slide type: {variant_spec.get('slide_type')}")

            # Show content preview
            content_html = result.get("content_html", "")
            content_preview = content_html[:300].replace("\n", " ")
            print(f"\n  Content preview (first 300 chars):")
            print(f"    {content_preview}...")

            return {
                "variant_id": variant["variant_id"],
                "success": True,
                "elapsed_ms": elapsed_ms,
                "image_fallback": result.get("image_fallback", False),
                "metadata": metadata
            }
        else:
            print(f"\n[FAILED] Status {response.status_code}: {response.text[:200]}")
            return {
                "variant_id": variant["variant_id"],
                "success": False,
                "elapsed_ms": elapsed_ms,
                "error": f"Status {response.status_code}"
            }

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"\n[ERROR] {str(e)}")
        return {
            "variant_id": variant["variant_id"],
            "success": False,
            "elapsed_ms": elapsed_ms,
            "error": str(e)
        }


async def main():
    """Run tests for 3 random I-series variants."""
    print("\n" + "="*70)
    print("I-SERIES CONTENT VARIANT TEST")
    print(f"Testing 3 random variants from {len(ISERIES_VARIANTS)} available")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70)

    # Pick 3 random variants (one from each category if possible)
    single_col = [v for v in ISERIES_VARIANTS if v["variant_id"].startswith("single_column")]
    comparison = [v for v in ISERIES_VARIANTS if v["variant_id"].startswith("comparison")]
    sequential = [v for v in ISERIES_VARIANTS if v["variant_id"].startswith("sequential")]

    selected_variants = [
        random.choice(single_col),
        random.choice(comparison),
        random.choice(sequential)
    ]

    print(f"\nSelected variants:")
    for i, v in enumerate(selected_variants, 1):
        print(f"  {i}. {v['variant_id']} ({v['layout_type']})")

    results = []

    async with httpx.AsyncClient() as client:
        for i, variant in enumerate(selected_variants):
            narrative = SAMPLE_NARRATIVES[i % len(SAMPLE_NARRATIVES)]
            result = await test_variant(client, variant, narrative, slide_num=i+1)
            results.append(result)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    successful = sum(1 for r in results if r["success"])
    total_time = sum(r["elapsed_ms"] for r in results)

    print(f"\nResults: {successful}/{len(results)} successful")
    print(f"Total time: {total_time}ms")
    print(f"Average time: {total_time // len(results)}ms per variant")

    print("\nDetailed results:")
    for r in results:
        status = "[OK]" if r["success"] else "[FAIL]"
        print(f"  {status} {r['variant_id']}: {r['elapsed_ms']}ms")
        if not r["success"]:
            print(f"       Error: {r.get('error', 'Unknown')}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
