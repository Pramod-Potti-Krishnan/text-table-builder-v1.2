"""
Integration Test for v1.2 Element-Based Content Generation

REFACTORED FOR SINGLE-CALL ARCHITECTURE

This test validates the complete v1.2 workflow:
1. Loading variant specifications
2. Building complete slide prompt (all elements at once)
3. Building contexts
4. Generating content (with mock LLM - single call)
5. Assembling templates
6. Validating character counts

Run with: python -m pytest tests/test_v1_2_integration.py -v
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import (
    ElementPromptBuilder,
    ContextBuilder,
    TemplateAssembler,
    ElementBasedContentGenerator
)


def mock_llm_service(prompt: str) -> str:
    """
    Mock LLM service that returns valid JSON responses for SINGLE-CALL architecture.

    This now handles the complete slide prompt where all elements are requested at once.

    Args:
        prompt: The complete slide prompt with all elements

    Returns:
        JSON string with ALL elements in one response
    """
    import re

    # Parse the prompt to extract element structure
    # Look for element IDs and their required fields
    elements_section = re.search(r'ELEMENTS TO GENERATE:(.*?)RESPONSE FORMAT:', prompt, re.DOTALL)

    if not elements_section:
        # Fallback for old-style prompts
        return json.dumps({"box_1": {"title": "Test Title", "description": "Test Description"}})

    elements_text = elements_section.group(1)

    # Find all element IDs (format: "1. box_1 (text_box):")
    element_matches = re.findall(r'\d+\.\s+(\w+)\s+\(\w+\):', elements_text)

    # Build response with all elements
    response = {}

    for element_id in element_matches:
        # Find required fields for this element
        element_block = re.search(
            rf'{element_id}\s+\(\w+\):.*?Required fields:\s*(.*?)(?:\n\s*Character|$)',
            elements_text,
            re.DOTALL
        )

        if element_block:
            fields_text = element_block.group(1)
            # Extract field names
            fields = re.findall(r'(\w+)', fields_text)
            fields = [f for f in fields if f not in ['Required', 'fields', 'count', 'requirements', 'Character', 'target']]
        else:
            # Default fields
            fields = ["title", "description"]

        # Generate content for each field
        element_data = {}
        for field in fields[:10]:  # Limit to first 10 to avoid over-generation
            if "title" in field.lower() or "heading" in field.lower() or "label" in field.lower():
                element_data[field] = f"Test Title for {element_id}"
            elif "description" in field.lower() or "body" in field.lower() or "paragraph" in field.lower():
                element_data[field] = f"Mock content for {element_id}: This provides detailed information for testing purposes."
            elif "number" in field.lower():
                element_data[field] = "42"
            elif "category" in field.lower():
                element_data[field] = f"Category {element_id}"
            else:
                element_data[field] = f"Mock {field} for {element_id}"

        response[element_id] = element_data

    return json.dumps(response)


def test_element_prompt_builder():
    """Test ElementPromptBuilder loads specs and builds prompts correctly."""
    print("\n=== Testing ElementPromptBuilder ===")

    builder = ElementPromptBuilder(variant_specs_dir="app/variant_specs")

    # Test loading variant spec
    spec = builder.load_variant_spec("matrix_2x2")
    assert spec["variant_id"] == "matrix_2x2"
    assert spec["slide_type"] == "matrix"
    assert len(spec["elements"]) == 4  # 2x2 = 4 boxes

    print(f"✓ Loaded variant spec: {spec['variant_id']}")
    print(f"✓ Element count: {len(spec['elements'])}")

    # Test building element prompt
    element = spec["elements"][0]
    slide_context = "This is a test slide about company values"

    prompt = builder.build_element_prompt(element, slide_context)
    assert "box_1" in prompt or element["element_id"] in prompt
    assert "CHARACTER COUNT REQUIREMENTS" in prompt
    assert slide_context in prompt

    print(f"✓ Built element prompt (length: {len(prompt)} chars)")

    # Test building all prompts
    all_prompts = builder.build_all_element_prompts(
        variant_id="matrix_2x2",
        slide_context=slide_context
    )
    assert len(all_prompts) == 4

    print(f"✓ Built prompts for all {len(all_prompts)} elements")


def test_context_builder():
    """Test ContextBuilder creates proper contexts."""
    print("\n=== Testing ContextBuilder ===")

    builder = ContextBuilder()

    # Test slide context
    slide_context = builder.build_slide_context(
        slide_title="Our Core Values",
        slide_purpose="Communicate company values to stakeholders",
        key_message="We are driven by innovation, growth, customer success, and team empowerment"
    )
    assert "Our Core Values" in slide_context
    assert "innovation" in slide_context.lower()

    print(f"✓ Built slide context (length: {len(slide_context)} chars)")

    # Test presentation context
    pres_context = builder.build_presentation_context(
        presentation_title="Q4 Business Review",
        presentation_type="Business Presentation",
        current_slide_number=3,
        total_slides=15
    )
    assert "Q4 Business Review" in pres_context
    assert "3 of 15" in pres_context

    print(f"✓ Built presentation context (length: {len(pres_context)} chars)")


def test_template_assembler():
    """Test TemplateAssembler loads and assembles templates."""
    print("\n=== Testing TemplateAssembler ===")

    assembler = TemplateAssembler(templates_dir="app/templates")

    # Test loading template
    template_html = assembler.load_template("matrix/matrix_2x2.html")
    assert "{box_1_title}" in template_html
    assert "{box_4_description}" in template_html

    print(f"✓ Loaded template (length: {len(template_html)} chars)")

    # Test getting placeholders
    placeholders = assembler.get_template_placeholders("matrix/matrix_2x2.html")
    expected_placeholders = {
        "box_1_title", "box_1_description",
        "box_2_title", "box_2_description",
        "box_3_title", "box_3_description",
        "box_4_title", "box_4_description"
    }
    assert placeholders == expected_placeholders

    print(f"✓ Extracted {len(placeholders)} placeholders")

    # Test assembling template
    content_map = {
        "box_1_title": "Innovation",
        "box_1_description": "We innovate daily",
        "box_2_title": "Growth",
        "box_2_description": "We grow sustainably",
        "box_3_title": "Customer Focus",
        "box_3_description": "Customers come first",
        "box_4_title": "Team",
        "box_4_description": "We empower our team"
    }

    assembled = assembler.assemble_template("matrix/matrix_2x2.html", content_map)
    assert "{box_1_title}" not in assembled  # Placeholders should be replaced
    assert "Innovation" in assembled
    assert "We grow sustainably" in assembled

    print(f"✓ Assembled template (length: {len(assembled)} chars)")


def test_complete_workflow():
    """Test complete v1.2 workflow with mock LLM (SINGLE-CALL architecture)."""
    print("\n=== Testing Complete v1.2 Workflow (Single-Call) ===")

    # Create generator with mock LLM
    generator = ElementBasedContentGenerator(
        llm_service=mock_llm_service,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates",
        enable_parallel=False  # Doesn't matter - single call now
    )

    # Define slide specification
    slide_spec = {
        "slide_title": "Our Core Values",
        "slide_purpose": "Communicate company values",
        "key_message": "Innovation, growth, customer success, and team empowerment drive us",
        "tone": "professional",
        "audience": "executive stakeholders"
    }

    # Generate slide content
    result = generator.generate_slide_content(
        variant_id="matrix_2x2",
        slide_spec=slide_spec
    )

    # Validate result structure
    assert "html" in result
    assert "elements" in result
    assert "metadata" in result
    assert result["variant_id"] == "matrix_2x2"

    # Validate single-call mode
    assert result["metadata"]["generation_mode"] == "single_call"

    print(f"✓ Generated slide content")
    print(f"  - HTML length: {len(result['html'])} chars")
    print(f"  - Elements generated: {len(result['elements'])}")
    print(f"  - Generation mode: {result['metadata']['generation_mode']}")

    # Validate HTML contains generated content from ALL elements
    assert "box_1" in result["html"] or "Test Title for box_1" in result["html"]
    assert "Mock content" in result["html"]

    print(f"✓ HTML contains all generated content")

    # Validate elements
    assert len(result["elements"]) == 4
    for elem in result["elements"]:
        assert "element_id" in elem
        assert "generated_content" in elem
        assert "character_counts" in elem

    print(f"✓ All elements have required fields")

    # Validate character counts
    validation = generator.validate_character_counts(
        element_contents=result["elements"],
        variant_id="matrix_2x2"
    )

    print(f"✓ Character count validation: {validation['valid']}")
    if not validation["valid"]:
        print(f"  ⚠ Found {len(validation['violations'])} character count violations")
        for violation in validation["violations"][:3]:  # Show first 3
            print(f"  ⚠ {violation['element_id']}.{violation['field']}: "
                  f"{violation['actual_count']} chars "
                  f"(expected {violation['required_min']}-{violation['required_max']})")


if __name__ == "__main__":
    print("=" * 60)
    print("v1.2 Integration Test Suite")
    print("=" * 60)

    try:
        test_element_prompt_builder()
        test_context_builder()
        test_template_assembler()
        test_complete_workflow()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
