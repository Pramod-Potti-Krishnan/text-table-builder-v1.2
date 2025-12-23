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

    def load_variant_spec(self, variant_id: str, layout_id: Optional[str] = None) -> Dict:
        """
        Load variant specification from JSON file.

        Args:
            variant_id: The variant identifier (e.g., "matrix_2x2")
            layout_id: Optional layout identifier (e.g., "C1") - if provided,
                       will try to load a layout-specific spec first

        Returns:
            Dictionary containing variant specification

        Raises:
            ValueError: If variant_id is not found
        """
        # Build cache key including layout_id if provided
        cache_key = f"{variant_id}_{layout_id}" if layout_id else variant_id

        # Check cache first
        if cache_key in self._spec_cache:
            return self._spec_cache[cache_key]

        # Get slide type from variant_id
        if variant_id not in self.variant_index["variant_lookup"]:
            raise ValueError(f"Unknown variant_id: {variant_id}")

        slide_type = self.variant_index["variant_lookup"][variant_id]

        # Try layout-specific spec first if layout_id is provided
        spec_path = None
        if layout_id:
            layout_spec_id = f"{variant_id}_{layout_id.lower()}"
            layout_spec_path = self.variant_specs_dir / slide_type / f"{layout_spec_id}.json"
            if layout_spec_path.exists():
                spec_path = layout_spec_path

        # Fall back to base spec
        if spec_path is None:
            spec_path = self.variant_specs_dir / slide_type / f"{variant_id}.json"

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
        presentation_context: Optional[str] = None,
        layout_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Build prompts for all elements in a variant.

        Args:
            variant_id: The variant identifier
            slide_context: Context about the current slide
            presentation_context: Optional presentation context
            layout_id: Optional layout ID for loading layout-specific specs

        Returns:
            List of dictionaries containing element info and prompts
        """
        spec = self.load_variant_spec(variant_id, layout_id)

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
        presentation_context: Optional[str] = None,
        layout_id: Optional[str] = None
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
            layout_id: Optional layout ID for loading layout-specific specs

        Returns:
            Complete prompt string for generating all slide elements
        """
        spec = self.load_variant_spec(variant_id, layout_id)

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

    def get_variant_metadata(self, variant_id: str, layout_id: str = "L25") -> Dict:
        """
        Get metadata about a variant (layout info, description, etc.).

        Args:
            variant_id: The variant identifier
            layout_id: Layout ID for template selection ('L25' or 'C1')
                       - L25: 720px content height (default)
                       - C1: 840px content height (20px top padding)

        Returns:
            Dictionary with variant metadata including resolved template_path
        """
        # Load layout-specific spec if available (e.g., comparison_2col_c1.json for C1)
        spec = self.load_variant_spec(variant_id, layout_id)

        # Get base template path from spec
        base_template_path = spec["template_path"]

        # Resolve template path based on layout_id
        # Note: If a C1-specific spec was loaded, its template_path already points to _c1.html
        # For fallback specs (non-layout-specific), we transform the path
        if layout_id == "C1" and not base_template_path.endswith("_c1.html"):
            # Transform: "app/templates/matrix/matrix_2x2.html"
            #        -> "app/templates/matrix/matrix_2x2_c1.html"
            template_path = base_template_path.replace(".html", "_c1.html")
        else:
            # Default: use template as-is from spec
            template_path = base_template_path

        return {
            "variant_id": spec["variant_id"],
            "slide_type": spec["slide_type"],
            "description": spec["description"],
            "template_path": template_path,
            "layout": spec.get("layout", {}),
            "element_count": len(spec["elements"]),
            "layout_id": layout_id
        }
