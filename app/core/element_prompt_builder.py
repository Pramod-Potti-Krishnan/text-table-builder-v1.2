"""
Element Prompt Builder for v1.2 Deterministic Assembly Architecture

This module builds targeted prompts for individual slide elements based on
variant specifications. Each element gets a precise prompt with character
count requirements and context.

Architecture:
    Director specifies variant_id → Load variant spec → Build element prompts
    → Generate content per element → Assemble into template
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ElementPromptBuilder:
    """Builds targeted prompts for individual slide elements."""

    def __init__(self, variant_specs_dir: str = "app/variant_specs"):
        """
        Initialize the ElementPromptBuilder.

        Args:
            variant_specs_dir: Directory containing variant specification JSON files
        """
        self.variant_specs_dir = Path(variant_specs_dir)
        self.variant_index = self._load_variant_index()
        self._spec_cache: Dict[str, Dict] = {}

    def _load_variant_index(self) -> Dict:
        """Load the master variant index."""
        index_path = self.variant_specs_dir / "variant_index.json"
        with open(index_path, 'r') as f:
            return json.load(f)

    def load_variant_spec(self, variant_id: str, layout_id: str = "L25") -> Dict:
        """
        Load variant specification from JSON file.
        Supports layout-aware resolution: when layout_id is not "L25",
        tries to find a layout-specific variant first (e.g., comparison_2col_c1).

        Args:
            variant_id: The variant identifier (e.g., "matrix_2x2")
            layout_id: Layout ID for template selection ("L25" or "C1")

        Returns:
            Dictionary containing variant specification

        Raises:
            ValueError: If variant_id is not found
        """
        # Build cache key that includes layout_id for layout-specific caching
        cache_key = f"{variant_id}_{layout_id}" if layout_id != "L25" else variant_id

        # Check cache first
        if cache_key in self._spec_cache:
            return self._spec_cache[cache_key]

        # For non-L25 layouts, try layout-specific variant first
        effective_variant_id = variant_id
        if layout_id != "L25":
            layout_variant_id = f"{variant_id}_{layout_id.lower()}"
            if layout_variant_id in self.variant_index["variant_lookup"]:
                effective_variant_id = layout_variant_id

        # Get slide type from variant_id
        if effective_variant_id not in self.variant_index["variant_lookup"]:
            raise ValueError(f"Unknown variant_id: {effective_variant_id}")

        slide_type = self.variant_index["variant_lookup"][effective_variant_id]

        # Load spec file
        spec_path = self.variant_specs_dir / slide_type / f"{effective_variant_id}.json"

        if not spec_path.exists():
            raise ValueError(f"Variant spec not found: {spec_path}")

        with open(spec_path, 'r') as f:
            spec = json.load(f)

        # Cache for future use
        self._spec_cache[cache_key] = spec

        return spec

    def build_element_prompt(
        self,
        element: Dict,
        slide_context: str,
        presentation_context: Optional[str] = None
    ) -> str:
        """
        Build a targeted prompt for a single element.

        Args:
            element: Element specification from variant JSON
            slide_context: Context about the current slide (title, purpose)
            presentation_context: Optional context about presentation and prior slides

        Returns:
            Formatted prompt string for LLM generation
        """
        element_id = element["element_id"]
        element_type = element["element_type"]
        required_fields = element["required_fields"]
        char_reqs = element["character_requirements"]

        # Build character requirements section
        char_req_lines = []
        for field in required_fields:
            req = char_reqs[field]
            char_req_lines.append(
                f"  - {field}: {req['min']}-{req['max']} characters "
                f"(target: {req['baseline']})"
            )

        char_req_text = "\n".join(char_req_lines)

        # Build the element prompt
        prompt = f"""Generate content for slide element: {element_id}

Element Type: {element_type}
Required Fields: {', '.join(required_fields)}

CHARACTER COUNT REQUIREMENTS (STRICT):
{char_req_text}

SLIDE CONTEXT:
{slide_context}
"""

        # Add presentation context if provided
        if presentation_context:
            prompt += f"""
PRESENTATION CONTEXT:
{presentation_context}
"""

        # Add element-specific instructions based on type
        element_instructions = self._get_element_type_instructions(element_type)

        if element_instructions:
            prompt += f"""
ELEMENT INSTRUCTIONS:
{element_instructions}
"""

        prompt += """
RESPONSE FORMAT:
Return a JSON object with the required fields. Each field must meet the character count requirements exactly.

Example format:
{
"""

        for i, field in enumerate(required_fields):
            comma = "," if i < len(required_fields) - 1 else ""
            prompt += f'  "{field}": "your content here"{comma}\n'

        prompt += "}\n"

        return prompt

    def _get_element_type_instructions(self, element_type: str) -> str:
        """
        Get specific instructions based on element type.

        Args:
            element_type: Type of element (text_box, metric_card, etc.)

        Returns:
            Instructions specific to this element type
        """
        instructions = {
            "text_box": (
                "- Title should be concise and descriptive\n"
                "- Description should explain the concept clearly\n"
                "- Use professional, business-appropriate language"
            ),
            "list_box": (
                "- Title should categorize the list items\n"
                "- Items should be returned as HTML <ul> list with <li> tags\n"
                "- Each list item should be concise (1-2 lines)\n"
                "- Maintain parallel structure across items"
            ),
            "comparison_column": (
                "- Heading should clearly identify what's being compared\n"
                "- Items should be returned as HTML <ul> list with <li> tags\n"
                "- IMPORTANT: Start each list item with a bold subheading followed by colon\n"
                "- Format: <li><strong>Subheading:</strong> Description text here</li>\n"
                "- Example: <li><strong>Focus:</strong> Reaching a broad audience through mass media.</li>\n"
                "- Use consistent subheading categories across columns for easy comparison\n"
                "- Focus on distinct, comparable points\n"
                "- Use parallel structure for easy comparison"
            ),
            "comparison_column_explicit": (
                "- Heading should clearly identify what's being compared\n"
                "- Each item (item_1 through item_7) should be a single point\n"
                "- IMPORTANT: Start each item with a bold subheading followed by colon\n"
                "- Format: <strong>Subheading:</strong> Description text here\n"
                "- Example: <strong>Focus:</strong> Reaching a broad audience through mass media.\n"
                "- DO NOT include bullets or list tags - template provides bullet symbols\n"
                "- Use consistent subheading categories across columns for easy comparison\n"
                "- Focus on distinct, comparable points\n"
                "- Use parallel structure for easy comparison"
            ),
            "sequential_step": (
                "- Number should indicate the step sequence (1, 2, 3, etc.)\n"
                "- Title should summarize the step action\n"
                "- Paragraphs should explain the step in detail\n"
                "- Maintain logical flow between steps"
            ),
            "metric_card": (
                "- Number should be the key metric value (number with unit if applicable)\n"
                "- Label should identify what the metric represents\n"
                "- Description should provide context or insight about the metric\n"
                "- Use impactful, data-driven language"
            ),
            "colored_section": (
                "- Heading should categorize the section theme\n"
                "- Bullets should be concise, actionable points\n"
                "- Maximum 95 characters OR 15 words per bullet\n"
                "- Use clear, direct language"
            ),
            "sidebar_list": (
                "- Heading should identify the sidebar purpose\n"
                "- Each item should be brief and informative\n"
                "- Items typically represent implementation phases or key points\n"
                "- Keep items parallel in structure"
            ),
            "table_headers": (
                "- Header_category should describe the row categories\n"
                "- Column headers should describe the data in each column\n"
                "- Keep headers concise and clear"
            ),
            "table_row": (
                "- Category should identify the row subject\n"
                "- Column values should be concise and data-focused\n"
                "- Maintain consistency with other rows"
            ),
            "text_content": (
                "- Heading/subheading should introduce the topic\n"
                "- Paragraphs should flow logically\n"
                "- Use clear, professional language\n"
                "- Maintain consistent tone throughout"
            ),
            "quote_content": (
                "- Quote should be impactful and memorable\n"
                "- Attribution should identify the source clearly\n"
                "- Quote should be relevant to the presentation theme"
            ),
            "insights_box": (
                "- Heading should be a short title for the insights section\n"
                "- Text should provide key takeaway or insight\n"
                "- Should synthesize the metrics above\n"
                "- Use clear, actionable language"
            ),
            "icon_card": (
                "- Icon MUST be semantically meaningful and represent the card's topic\n"
                "- Choose professional business/tech icons that match the title\n"
                "- Title should be concise and descriptive\n"
                "- Description should explain the concept clearly\n"
                "- Use professional, business-appropriate language"
            ),
            "numbered_card": (
                "- Title should be concise and descriptive\n"
                "- Description should explain the concept clearly\n"
                "- Use professional, business-appropriate language\n"
                "- Content should flow logically with the numbered sequence"
            )
        }

        return instructions.get(element_type, "")

    def build_all_element_prompts(
        self,
        variant_id: str,
        slide_context: str,
        presentation_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Build prompts for all elements in a variant.

        Args:
            variant_id: The variant identifier
            slide_context: Context about the current slide
            presentation_context: Optional presentation context

        Returns:
            List of dictionaries containing element info and prompts
        """
        spec = self.load_variant_spec(variant_id)

        element_prompts = []
        for element in spec["elements"]:
            prompt = self.build_element_prompt(
                element,
                slide_context,
                presentation_context
            )

            element_prompts.append({
                "element_id": element["element_id"],
                "element_type": element["element_type"],
                "required_fields": element["required_fields"],
                "placeholders": element["placeholders"],
                "prompt": prompt,
                "character_requirements": element["character_requirements"]
            })

        return element_prompts

    def build_complete_slide_prompt(
        self,
        variant_id: str,
        slide_context: str,
        presentation_context: Optional[str] = None
    ) -> str:
        """
        Build a single prompt for generating ALL elements of a slide at once.

        This is the NEW v1.2 single-call architecture that ensures content coherence.
        Instead of generating each element separately, we ask the LLM to generate
        all elements together so they are contextually related and don't repeat.

        Args:
            variant_id: The variant identifier
            slide_context: Context about the current slide
            presentation_context: Optional presentation context

        Returns:
            Complete prompt string for generating all slide elements
        """
        spec = self.load_variant_spec(variant_id)

        # Build the prompt header
        prompt = f"""Generate complete content for a presentation slide.

VARIANT: {variant_id} ({spec['description']})
SLIDE TYPE: {spec['slide_type']}
TOTAL ELEMENTS: {len(spec['elements'])}

SLIDE CONTEXT:
{slide_context}
"""

        if presentation_context:
            prompt += f"""
PRESENTATION CONTEXT:
{presentation_context}
"""

        prompt += """
IMPORTANT: Generate ALL elements together to ensure content coherence. Each element should cover a DIFFERENT aspect - avoid repetition or redundancy across elements.

"""

        # Add element structure details
        prompt += "ELEMENTS TO GENERATE:\n\n"

        for i, element in enumerate(spec["elements"], 1):
            element_id = element["element_id"]
            element_type = element["element_type"]
            required_fields = element["required_fields"]
            char_reqs = element["character_requirements"]

            prompt += f"{i}. {element_id} ({element_type}):\n"
            prompt += f"   Required fields: {', '.join(required_fields)}\n"
            prompt += "   Character count requirements:\n"

            for field in required_fields:
                req = char_reqs[field]
                prompt += f"     - {field}: {req['min']}-{req['max']} characters (target: {req['baseline']})\n"

            # Add element-specific instructions
            element_instructions = self._get_element_type_instructions(element_type)
            if element_instructions:
                prompt += f"   Instructions:\n"
                for line in element_instructions.split('\n'):
                    if line.strip():
                        prompt += f"     {line}\n"

            # Add field-specific instructions from character_requirements
            for field in required_fields:
                req = char_reqs[field]
                if "instruction" in req:
                    if not element_instructions:
                        prompt += f"   Instructions:\n"
                        element_instructions = True  # Mark that we've added instructions header
                    prompt += f"     - {field}: {req['instruction']}\n"

            prompt += "\n"

        # Add JSON response format
        prompt += """RESPONSE FORMAT:
Return a single JSON object with all elements. The structure should be:

{
"""

        for i, element in enumerate(spec["elements"]):
            element_id = element["element_id"]
            required_fields = element["required_fields"]
            comma = "," if i < len(spec["elements"]) - 1 else ""

            prompt += f'  "{element_id}": {{\n'
            for j, field in enumerate(required_fields):
                field_comma = "," if j < len(required_fields) - 1 else ""
                prompt += f'    "{field}": "content here"{field_comma}\n'
            prompt += f'  }}{comma}\n'

        prompt += """}

CRITICAL INSTRUCTIONS:
1. Generate ALL elements in ONE response
2. Ensure each element has DIFFERENT content (no repetition)
3. All content should be coherent and work together as one slide
4. Follow character count requirements strictly
5. Return ONLY valid JSON with no additional text
"""

        return prompt

    def get_variant_metadata(self, variant_id: str) -> Dict:
        """
        Get metadata about a variant (layout info, description, etc.).

        Args:
            variant_id: The variant identifier

        Returns:
            Dictionary with variant metadata
        """
        spec = self.load_variant_spec(variant_id)

        return {
            "variant_id": spec["variant_id"],
            "slide_type": spec["slide_type"],
            "description": spec["description"],
            "template_path": spec["template_path"],
            "layout": spec.get("layout", {}),
            "element_count": len(spec["elements"])
        }
