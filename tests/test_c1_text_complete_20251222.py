#!/usr/bin/env python3
"""
Test C1 Text Complete - All 34 Variants
Date: 2025-12-22

Generates all 34 C1 variant slides:
- Grid (9): 2x2_centered, 2x2_left, 2x2_numbered, 2x3, 2x3_left, 2x3_numbered, 3x2, 3x2_left, 3x2_numbered
- Sequential (3): 3col, 4col, 5col
- Comparison (3): 2col, 3col, 4col
- Metrics (4): 2x2_grid, 3col, 3x2_grid, 4col
- Matrix (2): 2x2, 2x3
- Asymmetric (3): 8_4_3section, 8_4_4section, 8_4_5section
- Hybrid (2): left_2x2, top_2x2
- Single Column (3): 3section, 4section, 5section
- Table (4): 2col, 3col, 4col, 5col
- Impact Quote (1): impact_quote

Calls Text Service on Railway, assembles in Layout Service, returns URL.

Usage:
    python3 test_c1_text_complete_20251222.py
"""

import requests
import json
import time
from datetime import datetime

# Service URLs
TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

# All 34 C1 variants with appropriate slide specs
TEST_VARIANTS = [
    # =========================================================================
    # GRID (9 variants) - Zero left padding
    # =========================================================================
    {
        "variant_id": "grid_2x2_centered",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Four Pillars of Success",
            "slide_purpose": "Present four key success factors in a centered layout",
            "key_message": "Balance across all dimensions",
            "tone": "professional",
            "audience": "executives"
        }
    },
    {
        "variant_id": "grid_2x2_left",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Core Capabilities",
            "slide_purpose": "Showcase four main capabilities with left-aligned content",
            "key_message": "Comprehensive platform features",
            "tone": "professional",
            "audience": "technical buyers"
        }
    },
    {
        "variant_id": "grid_2x2_numbered",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Implementation Steps",
            "slide_purpose": "Present four numbered implementation phases",
            "key_message": "Clear sequential approach",
            "tone": "professional",
            "audience": "project managers"
        }
    },
    {
        "variant_id": "grid_2x3",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Service Portfolio",
            "slide_purpose": "Display six key services in a 2x3 grid",
            "key_message": "Comprehensive service offering",
            "tone": "professional",
            "audience": "potential clients"
        }
    },
    {
        "variant_id": "grid_2x3_left",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Product Features",
            "slide_purpose": "Showcase six product features with left alignment",
            "key_message": "Feature-rich solution",
            "tone": "professional",
            "audience": "product evaluators"
        }
    },
    {
        "variant_id": "grid_2x3_numbered",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Six-Step Process",
            "slide_purpose": "Present a six-step numbered process",
            "key_message": "Systematic approach to success",
            "tone": "professional",
            "audience": "operations team"
        }
    },
    {
        "variant_id": "grid_3x2",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Market Segments",
            "slide_purpose": "Display six market segments in 3x2 layout",
            "key_message": "Diverse market coverage",
            "tone": "professional",
            "audience": "sales team"
        }
    },
    {
        "variant_id": "grid_3x2_left",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Team Departments",
            "slide_purpose": "Showcase six departments with descriptions",
            "key_message": "Strong organizational structure",
            "tone": "professional",
            "audience": "new employees"
        }
    },
    {
        "variant_id": "grid_3x2_numbered",
        "category": "Grid",
        "slide_spec": {
            "slide_title": "Priority Actions",
            "slide_purpose": "Present six prioritized action items",
            "key_message": "Clear action plan",
            "tone": "professional",
            "audience": "leadership team"
        }
    },

    # =========================================================================
    # SEQUENTIAL (3 variants) - Zero left padding
    # =========================================================================
    {
        "variant_id": "sequential_3col",
        "category": "Sequential",
        "slide_spec": {
            "slide_title": "Three-Phase Approach",
            "slide_purpose": "Show a three-phase project approach",
            "key_message": "Structured methodology",
            "tone": "professional",
            "audience": "project stakeholders"
        }
    },
    {
        "variant_id": "sequential_4col",
        "category": "Sequential",
        "slide_spec": {
            "slide_title": "Implementation Roadmap",
            "slide_purpose": "Present four phases of implementation",
            "key_message": "Clear path from planning to deployment",
            "tone": "professional",
            "audience": "implementation team"
        }
    },
    {
        "variant_id": "sequential_5col",
        "category": "Sequential",
        "slide_spec": {
            "slide_title": "Customer Journey",
            "slide_purpose": "Map the five stages of customer journey",
            "key_message": "End-to-end customer experience",
            "tone": "professional",
            "audience": "marketing team"
        }
    },

    # =========================================================================
    # COMPARISON (3 variants) - Zero left padding
    # =========================================================================
    {
        "variant_id": "comparison_2col",
        "category": "Comparison",
        "slide_spec": {
            "slide_title": "Before vs After",
            "slide_purpose": "Compare current state with future state",
            "key_message": "Transformation benefits",
            "tone": "professional",
            "audience": "decision makers"
        }
    },
    {
        "variant_id": "comparison_3col",
        "category": "Comparison",
        "slide_spec": {
            "slide_title": "Plan Comparison",
            "slide_purpose": "Compare three pricing tiers",
            "key_message": "Find the right plan for your needs",
            "tone": "professional",
            "audience": "potential customers"
        }
    },
    {
        "variant_id": "comparison_4col",
        "category": "Comparison",
        "slide_spec": {
            "slide_title": "Vendor Comparison",
            "slide_purpose": "Compare four vendor options",
            "key_message": "Informed vendor selection",
            "tone": "professional",
            "audience": "procurement team"
        }
    },

    # =========================================================================
    # METRICS (4 variants) - 40px left padding (kept)
    # =========================================================================
    {
        "variant_id": "metrics_2x2_grid",
        "category": "Metrics",
        "slide_spec": {
            "slide_title": "Quarterly Dashboard",
            "slide_purpose": "Display four key quarterly metrics",
            "key_message": "Strong quarterly performance",
            "tone": "professional",
            "audience": "board members"
        }
    },
    {
        "variant_id": "metrics_3col",
        "category": "Metrics",
        "slide_spec": {
            "slide_title": "Key Performance Indicators",
            "slide_purpose": "Highlight three critical metrics",
            "key_message": "Measurable results that matter",
            "tone": "professional",
            "audience": "business leaders"
        }
    },
    {
        "variant_id": "metrics_3x2_grid",
        "category": "Metrics",
        "slide_spec": {
            "slide_title": "Performance Overview",
            "slide_purpose": "Present six performance metrics in a grid",
            "key_message": "Comprehensive performance view",
            "tone": "professional",
            "audience": "management team"
        }
    },
    {
        "variant_id": "metrics_4col",
        "category": "Metrics",
        "slide_spec": {
            "slide_title": "Growth Metrics",
            "slide_purpose": "Display four growth-related metrics",
            "key_message": "Sustained growth trajectory",
            "tone": "professional",
            "audience": "investors"
        }
    },

    # =========================================================================
    # MATRIX (2 variants) - Zero left padding
    # =========================================================================
    {
        "variant_id": "matrix_2x2",
        "category": "Matrix",
        "slide_spec": {
            "slide_title": "Strategic Quadrants",
            "slide_purpose": "Present four strategic quadrants",
            "key_message": "Balanced strategic approach",
            "tone": "professional",
            "audience": "strategy team"
        }
    },
    {
        "variant_id": "matrix_2x3",
        "category": "Matrix",
        "slide_spec": {
            "slide_title": "Priority Matrix",
            "slide_purpose": "Display six items in a priority matrix",
            "key_message": "Clear prioritization framework",
            "tone": "professional",
            "audience": "project managers"
        }
    },

    # =========================================================================
    # ASYMMETRIC (3 variants) - Zero left padding
    # =========================================================================
    {
        "variant_id": "asymmetric_8_4_3section",
        "category": "Asymmetric",
        "slide_spec": {
            "slide_title": "Market Analysis",
            "slide_purpose": "Present market insights with sidebar details",
            "key_message": "Data-driven market understanding",
            "tone": "professional",
            "audience": "analysts"
        }
    },
    {
        "variant_id": "asymmetric_8_4_4section",
        "category": "Asymmetric",
        "slide_spec": {
            "slide_title": "Product Overview",
            "slide_purpose": "Main content with four supporting points",
            "key_message": "Comprehensive product view",
            "tone": "professional",
            "audience": "product team"
        }
    },
    {
        "variant_id": "asymmetric_8_4_5section",
        "category": "Asymmetric",
        "slide_spec": {
            "slide_title": "Research Findings",
            "slide_purpose": "Present research with five key findings",
            "key_message": "Evidence-based insights",
            "tone": "professional",
            "audience": "research team"
        }
    },

    # =========================================================================
    # HYBRID (2 variants) - Zero left padding
    # =========================================================================
    {
        "variant_id": "hybrid_left_2x2",
        "category": "Hybrid",
        "slide_spec": {
            "slide_title": "Solution Framework",
            "slide_purpose": "2x2 grid with supporting bullet list",
            "key_message": "Integrated solution approach",
            "tone": "professional",
            "audience": "solution architects"
        }
    },
    {
        "variant_id": "hybrid_top_2x2",
        "category": "Hybrid",
        "slide_spec": {
            "slide_title": "Capabilities Overview",
            "slide_purpose": "2x2 grid on top with summary below",
            "key_message": "Complete capability set",
            "tone": "professional",
            "audience": "technical evaluators"
        }
    },

    # =========================================================================
    # SINGLE COLUMN (3 variants) - Zero left padding
    # =========================================================================
    {
        "variant_id": "single_column_3section",
        "category": "Single Column",
        "slide_spec": {
            "slide_title": "Executive Summary",
            "slide_purpose": "Present three key sections vertically",
            "key_message": "Clear executive overview",
            "tone": "professional",
            "audience": "executives"
        }
    },
    {
        "variant_id": "single_column_4section",
        "category": "Single Column",
        "slide_spec": {
            "slide_title": "Project Status",
            "slide_purpose": "Four project status sections",
            "key_message": "Comprehensive status update",
            "tone": "professional",
            "audience": "stakeholders"
        }
    },
    {
        "variant_id": "single_column_5section",
        "category": "Single Column",
        "slide_spec": {
            "slide_title": "Department Report",
            "slide_purpose": "Five department updates in sequence",
            "key_message": "Cross-functional visibility",
            "tone": "professional",
            "audience": "leadership"
        }
    },

    # =========================================================================
    # TABLE (4 variants) - 40px left padding (kept)
    # =========================================================================
    {
        "variant_id": "table_2col",
        "category": "Table",
        "slide_spec": {
            "slide_title": "Feature Matrix",
            "slide_purpose": "Two-column feature comparison table",
            "key_message": "Clear feature breakdown",
            "tone": "professional",
            "audience": "technical buyers"
        }
    },
    {
        "variant_id": "table_3col",
        "category": "Table",
        "slide_spec": {
            "slide_title": "Product Comparison",
            "slide_purpose": "Three-column product comparison table",
            "key_message": "Detailed product breakdown",
            "tone": "professional",
            "audience": "evaluators"
        }
    },
    {
        "variant_id": "table_4col",
        "category": "Table",
        "slide_spec": {
            "slide_title": "Quarterly Results",
            "slide_purpose": "Four-column quarterly data table",
            "key_message": "Year-over-year comparison",
            "tone": "professional",
            "audience": "finance team"
        }
    },
    {
        "variant_id": "table_5col",
        "category": "Table",
        "slide_spec": {
            "slide_title": "Regional Performance",
            "slide_purpose": "Five-column regional performance table",
            "key_message": "Regional breakdown",
            "tone": "professional",
            "audience": "regional managers"
        }
    },

    # =========================================================================
    # IMPACT QUOTE (1 variant) - 40px left padding (kept)
    # =========================================================================
    {
        "variant_id": "impact_quote",
        "category": "Impact Quote",
        "slide_spec": {
            "slide_title": "Customer Testimonial",
            "slide_purpose": "Display an impactful customer quote",
            "key_message": "Customer success story",
            "tone": "inspiring",
            "audience": "prospects"
        }
    },
]

TOTAL_VARIANTS = len(TEST_VARIANTS)


def generate_slide(variant_config, index):
    """Call Text Service to generate slide content."""
    url = f"{TEXT_SERVICE_URL}/v1.2/generate"

    payload = {
        "variant_id": variant_config["variant_id"],
        "slide_spec": variant_config["slide_spec"],
        "presentation_spec": {
            "presentation_title": "C1 Text Complete Test - 2025-12-22",
            "presentation_type": "Test Presentation"
        }
    }

    print(f"  Calling Text Service for {variant_config['variant_id']}...")

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # LLM calls can take time
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Error: {response.status_code}")
            print(f"  Response: {response.text[:300]}")
            return None

    except Exception as e:
        print(f"  Exception: {str(e)}")
        return None


def create_presentation_slide(variant_config, text_service_result):
    """Convert Text Service result to Layout Service slide format."""
    return {
        "layout": "C1-text",
        "content": {
            "slide_title": variant_config["slide_spec"]["slide_title"],
            "subtitle": f"{variant_config['category']} | {variant_config['variant_id']}",
            "body": text_service_result.get("html", ""),
            "footer_text": "C1 Text Complete Test - 2025-12-22",
            "logo": ""
        }
    }


def post_to_layout_service(slides):
    """Post slides to Layout Service and return URL."""
    url = f"{LAYOUT_SERVICE_URL}/api/presentations"

    presentation = {
        "title": f"C1 Text Complete - All {len(slides)} Variants - 2025-12-22",
        "slides": slides
    }

    print(f"\nPosting {len(slides)} slides to Layout Service...")

    try:
        response = requests.post(
            url,
            json=presentation,
            headers={"Content-Type": "application/json"},
            timeout=120
        )

        if response.status_code in [200, 201]:
            data = response.json()
            presentation_id = data.get("id")
            url_path = data.get("url", f"/p/{presentation_id}")
            view_url = f"{LAYOUT_SERVICE_URL}{url_path}"
            return view_url
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None

    except Exception as e:
        print(f"Exception: {str(e)}")
        return None


def main():
    start_time = time.time()

    print("=" * 80)
    print("C1 TEXT COMPLETE TEST - ALL 34 VARIANTS")
    print("Date: 2025-12-22")
    print("=" * 80)
    print(f"Text Service: {TEXT_SERVICE_URL}")
    print(f"Layout Service: {LAYOUT_SERVICE_URL}")
    print(f"Total Variants: {TOTAL_VARIANTS}")
    print("=" * 80)

    slides = []
    successful = 0
    failed = 0
    failed_variants = []

    for i, variant_config in enumerate(TEST_VARIANTS, 1):
        print(f"\n[{i}/{TOTAL_VARIANTS}] {variant_config['category']}: {variant_config['variant_id']}")

        # Generate via Text Service
        result = generate_slide(variant_config, i)

        if result and result.get("html"):
            slide = create_presentation_slide(variant_config, result)
            slides.append(slide)
            successful += 1
            html_len = len(result.get("html", ""))
            print(f"  Success! HTML: {html_len} chars")
        else:
            failed += 1
            failed_variants.append(variant_config['variant_id'])
            print(f"  Failed to generate")

    elapsed = time.time() - start_time

    print("\n" + "=" * 80)
    print(f"Generation Complete: {successful}/{TOTAL_VARIANTS} successful, {failed} failed")
    print(f"Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print("=" * 80)

    if failed_variants:
        print(f"\nFailed variants: {', '.join(failed_variants)}")

    if not slides:
        print("\nNo slides generated. Exiting.")
        return

    # Post to Layout Service
    view_url = post_to_layout_service(slides)

    if view_url:
        print("\n" + "=" * 80)
        print("SUCCESS! Presentation Created")
        print("=" * 80)
        print(f"\nVIEW URL:")
        print(f"  {view_url}")
        print("\n" + "=" * 80)
        print(f"\nSlides: {len(slides)}")
        print("Use arrow keys to navigate slides")
        print("Press 'G' for grid overlay, 'B' for borders")
        print("=" * 80)
    else:
        print("\nFailed to create presentation in Layout Service")


if __name__ == "__main__":
    main()
