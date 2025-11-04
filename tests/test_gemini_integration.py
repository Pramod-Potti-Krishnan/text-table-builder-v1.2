#!/usr/bin/env python3
"""
Test v1.2 with Real Gemini Integration

This script tests the complete v1.2 workflow with actual Gemini models
via Vertex AI using Application Default Credentials.

Prerequisites:
1. Google Cloud SDK installed
2. Authenticated: gcloud auth application-default login
3. GCP_PROJECT_ID environment variable set
4. Vertex AI API enabled in Google Cloud Console

Usage:
    # Set up environment
    export GCP_PROJECT_ID=your-project-id

    # Run test
    python3 test_gemini_integration.py
"""

import sys
import os
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable, get_llm_service


def test_llm_service():
    """Test LLM service initialization and basic generation."""
    print("\n" + "="*80)
    print("TEST 1: LLM Service Initialization")
    print("="*80)

    try:
        service = get_llm_service()
        print(f"✓ LLM service initialized")
        print(f"  - Model routing enabled: {service.enable_model_routing}")
        print(f"  - Flash model: {service.flash_model}")
        print(f"  - Pro model: {service.pro_model}")

        # Test simple generation
        print("\nTesting simple generation...")
        test_prompt = """Generate content for a metric card.

Required Fields: number, label, description

CHARACTER COUNT REQUIREMENTS (STRICT):
  - number: 1-10 characters (target: 5)
  - label: 19-21 characters (target: 20)
  - description: 76-84 characters (target: 80)

RESPONSE FORMAT:
Return a JSON object with the required fields.

Example format:
{
  "number": "42%",
  "label": "Revenue Growth Rate",
  "description": "Year-over-year revenue increased significantly due to strong market demand"
}
"""

        response = service.generate(test_prompt)
        print(f"✓ Generation successful")
        print(f"  Response length: {len(response)} characters")

        # Try to parse JSON
        try:
            data = json.loads(response)
            print(f"✓ Valid JSON response")
            print(f"  Fields: {list(data.keys())}")
            for field, value in data.items():
                print(f"  - {field}: {len(value)} chars")
        except json.JSONDecodeError:
            print(f"⚠ Response is not valid JSON")
            print(f"  Response preview: {response[:200]}")

        # Show usage stats
        stats = service.get_usage_stats()
        print(f"\n✓ Usage stats:")
        print(f"  - Total calls: {stats['total_calls']}")
        print(f"  - Flash calls: {stats['flash_calls']} ({stats['flash_percentage']:.1f}%)")
        print(f"  - Pro calls: {stats['pro_calls']} ({stats['pro_percentage']:.1f}%)")
        print(f"  - Total tokens: {stats['total_tokens']}")

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_element_generation():
    """Test element-based generation with real Gemini."""
    print("\n" + "="*80)
    print("TEST 2: Element-Based Generation (matrix_2x2)")
    print("="*80)

    try:
        # Create generator with real LLM
        llm_callable = create_llm_callable()
        generator = ElementBasedContentGenerator(
            llm_service=llm_callable,
            variant_specs_dir="app/variant_specs",
            templates_dir="app/templates",
            enable_parallel=False  # Sequential for easier debugging
        )

        print("✓ Generator initialized with Gemini integration")

        # Define slide spec
        slide_spec = {
            "slide_title": "Our Core Values",
            "slide_purpose": "Communicate company values to executive stakeholders",
            "key_message": "Innovation, strategic growth, customer success, and team empowerment drive our organization",
            "tone": "professional",
            "audience": "executive stakeholders"
        }

        presentation_spec = {
            "presentation_title": "Q4 Business Review",
            "presentation_type": "Business Presentation",
            "current_slide_number": 5,
            "total_slides": 20
        }

        print("\nGenerating slide content...")
        print(f"  Variant: matrix_2x2")
        print(f"  Elements: 4")
        print(f"  Mode: sequential")

        # Generate content
        result = generator.generate_slide_content(
            variant_id="matrix_2x2",
            slide_spec=slide_spec,
            presentation_spec=presentation_spec
        )

        print(f"✓ Generation successful")
        print(f"  - HTML length: {len(result['html'])} characters")
        print(f"  - Elements generated: {len(result['elements'])}")
        print(f"  - Generation mode: {result['metadata']['generation_mode']}")

        # Display element details
        print(f"\n✓ Element details:")
        for elem in result['elements']:
            print(f"  - {elem['element_id']} ({elem['element_type']})")
            for field, value in elem['generated_content'].items():
                char_count = len(value)
                print(f"    · {field}: {char_count} chars - {value[:50]}...")

        # Validate character counts
        validation = generator.validate_character_counts(
            element_contents=result['elements'],
            variant_id="matrix_2x2"
        )

        print(f"\n✓ Character count validation: {validation['valid']}")
        if not validation["valid"]:
            print(f"  ⚠ Violations found: {len(validation['violations'])}")
            for v in validation['violations'][:3]:  # Show first 3
                print(f"    - {v['element_id']}.{v['field']}: "
                      f"{v['actual_count']} chars "
                      f"(expected {v['required_min']}-{v['required_max']})")

        # Get LLM service stats
        service = get_llm_service()
        stats = service.get_usage_stats()
        print(f"\n✓ LLM usage for this generation:")
        print(f"  - Total calls: {stats['total_calls']}")
        print(f"  - Total tokens: {stats['total_tokens']}")
        print(f"  - Avg tokens/call: {stats['total_tokens'] / stats['total_calls']:.0f}")

        # Save generated HTML
        output_path = Path("test_output_gemini.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['html'])
        print(f"\n✓ Saved generated HTML to: {output_path}")

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_prerequisites():
    """Check that prerequisites are met."""
    print("\n" + "="*80)
    print("Checking Prerequisites")
    print("="*80)

    issues = []

    # Check GCP_PROJECT_ID
    project_id = os.getenv("GCP_PROJECT_ID")
    if project_id:
        print(f"✓ GCP_PROJECT_ID: {project_id}")
    else:
        print(f"✗ GCP_PROJECT_ID not set")
        issues.append("Set GCP_PROJECT_ID environment variable")

    # Check for credentials
    try:
        from google.auth import default
        credentials, project = default()
        print(f"✓ Google Cloud credentials found")
        if project:
            print(f"  Default project: {project}")
    except Exception as e:
        print(f"✗ Google Cloud credentials not found")
        print(f"  Error: {e}")
        issues.append("Run: gcloud auth application-default login")

    # Check Vertex AI library
    try:
        import vertexai
        print(f"✓ Vertex AI library installed")
    except ImportError:
        print(f"✗ Vertex AI library not installed")
        issues.append("Install: pip install google-cloud-aiplatform>=1.70.0")

    if issues:
        print(f"\n⚠ Please fix the following issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False

    print(f"\n✓ All prerequisites met")
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("v1.2 Gemini Integration Test")
    print("="*80)

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix issues above and try again.")
        sys.exit(1)

    # Run tests
    success = True

    # Test 1: LLM Service
    if not test_llm_service():
        success = False

    # Test 2: Element Generation
    if not test_element_generation():
        success = False

    # Summary
    print("\n" + "="*80)
    if success:
        print("✅ All tests passed!")
        print("="*80)
        print("\nv1.2 is fully integrated with Gemini via Vertex AI.")
        print("You can now use the v1.2 API with real LLM generation.")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        print("="*80)
        print("\nPlease check the errors above and ensure:")
        print("1. GCP_PROJECT_ID is set correctly")
        print("2. gcloud auth application-default login is done")
        print("3. Vertex AI API is enabled in your GCP project")
        sys.exit(1)
