"""
Element-Based Content Generator for v1.2 Deterministic Assembly Architecture

This module orchestrates the complete v1.2 content generation workflow:
1. Load variant spec based on variant_id
2. Build context from Director's input
3. Generate ONE complete prompt for all elements
4. Generate content in SINGLE LLM call (ensures content coherence)
5. Parse response into elements
6. Assemble content into template
7. Return final HTML

Architecture (REFACTORED - Single Call Per Slide):
    Director input → ElementPromptBuilder (complete slide prompt)
    → ONE LLM call → Parse all elements → TemplateAssembler → Final HTML

This ensures content coherence across elements and eliminates repetition.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .element_prompt_builder import ElementPromptBuilder
from .context_builder import ContextBuilder
from .template_assembler import TemplateAssembler


class ElementBasedContentGenerator:
    """
    Orchestrates element-based content generation for slides.

    This is the main entry point for v1.2 architecture.
    """

    def __init__(
        self,
        llm_service: Optional[Callable] = None,
        variant_specs_dir: str = "app/variant_specs",
        templates_dir: str = "app/templates",
        enable_parallel: bool = True,
        max_workers: int = 5
    ):
        """
        Initialize the ElementBasedContentGenerator.

        Args:
            llm_service: Callable that takes a prompt string and returns generated content
                        Signature: llm_service(prompt: str) -> str
            variant_specs_dir: Directory containing variant specifications
            templates_dir: Directory containing HTML templates
            enable_parallel: Whether to generate elements in parallel
            max_workers: Maximum number of parallel workers
        """
        self.llm_service = llm_service
        self.prompt_builder = ElementPromptBuilder(variant_specs_dir)
        self.context_builder = ContextBuilder()
        self.template_assembler = TemplateAssembler(templates_dir)
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers

    def generate_slide_content(
        self,
        variant_id: str,
        slide_spec: Dict[str, Any],
        presentation_spec: Optional[Dict[str, Any]] = None,
        element_relationships: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete slide content using SINGLE-CALL architecture.

        REFACTORED: Now generates ALL elements in ONE LLM call to ensure
        content coherence and eliminate redundancy across elements.

        Args:
            variant_id: The variant identifier (e.g., "matrix_2x2")
            slide_spec: Dictionary with slide-level specifications:
                - slide_title (str)
                - slide_purpose (str)
                - key_message (str)
                - target_points (List[str], optional)
                - tone (str, optional)
                - audience (str, optional)
            presentation_spec: Optional presentation-level context
            element_relationships: Optional element relationship descriptions

        Returns:
            Dictionary containing:
                - html: Assembled HTML string
                - elements: List of generated element contents
                - metadata: Generation metadata (model used, etc.)
                - variant_id: The variant used
                - template_path: Path to the template used

        Raises:
            ValueError: If variant_id is invalid or LLM service not configured
        """
        if not self.llm_service:
            raise ValueError("LLM service not configured. Cannot generate content.")

        # Step 1: Build contexts
        contexts = self.context_builder.build_complete_context(
            slide_spec=slide_spec,
            presentation_spec=presentation_spec,
            element_relationships=element_relationships
        )

        # Step 2: Get variant metadata and template path
        variant_metadata = self.prompt_builder.get_variant_metadata(variant_id)
        template_path = variant_metadata["template_path"]

        # Step 3: Build COMPLETE slide prompt (all elements at once)
        complete_prompt = self.prompt_builder.build_complete_slide_prompt(
            variant_id=variant_id,
            slide_context=contexts["slide_context"],
            presentation_context=contexts.get("presentation_context")
        )

        # Step 4: Generate content with ONE LLM call
        llm_response = self.llm_service(complete_prompt)

        # Step 5: Parse response into element contents
        element_contents = self._parse_complete_response(
            llm_response=llm_response,
            variant_id=variant_id
        )

        # Step 6: Build content map for template assembly
        content_map = self._build_content_map(element_contents)

        # Step 7: Assemble template
        assembled_html = self.template_assembler.assemble_template(
            template_path=template_path,
            content_map=content_map
        )

        # Step 8: Return result
        return {
            "html": assembled_html,
            "elements": element_contents,
            "metadata": {
                "variant_id": variant_id,
                "template_path": template_path,
                "element_count": len(element_contents),
                "generation_mode": "single_call"
            },
            "variant_id": variant_id,
            "template_path": template_path
        }

    async def generate_slide_content_async(
        self,
        variant_id: str,
        slide_spec: Dict[str, Any],
        presentation_spec: Optional[Dict[str, Any]] = None,
        element_relationships: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete slide content using SINGLE-CALL architecture (ASYNC).

        This is the production-quality async version for FastAPI endpoints.
        It properly works within FastAPI's event loop without conflicts.

        REFACTORED: Now generates ALL elements in ONE LLM call to ensure
        content coherence and eliminate redundancy across elements.

        Args:
            variant_id: The variant identifier (e.g., "matrix_2x2")
            slide_spec: Dictionary with slide-level specifications:
                - slide_title (str)
                - slide_purpose (str)
                - key_message (str)
                - target_points (List[str], optional)
                - tone (str, optional)
                - audience (str, optional)
            presentation_spec: Optional presentation-level context
            element_relationships: Optional element relationship descriptions

        Returns:
            Dictionary containing:
                - html: Assembled HTML string
                - elements: List of generated element contents
                - metadata: Generation metadata (model used, etc.)
                - variant_id: The variant used
                - template_path: Path to the template used

        Raises:
            ValueError: If variant_id is invalid or LLM service not configured
        """
        import time
        stage_start = time.time()

        if not self.llm_service:
            raise ValueError("LLM service not configured. Cannot generate content.")

        # Step 1: Build contexts (sync operations)
        contexts = self.context_builder.build_complete_context(
            slide_spec=slide_spec,
            presentation_spec=presentation_spec,
            element_relationships=element_relationships
        )

        # Step 2: Get variant metadata and template path (sync operations)
        variant_metadata = self.prompt_builder.get_variant_metadata(variant_id)
        template_path = variant_metadata["template_path"]

        # Step 3: Build COMPLETE slide prompt (all elements at once) (sync operation)
        complete_prompt = self.prompt_builder.build_complete_slide_prompt(
            variant_id=variant_id,
            slide_context=contexts["slide_context"],
            presentation_context=contexts.get("presentation_context")
        )

        # STAGE LOGGING: Prompt built
        prompt_time = int((time.time() - stage_start) * 1000)
        print(f"[GEN-PROMPT] variant={variant_id}, prompt_len={len(complete_prompt)}, build_time={prompt_time}ms")

        # Step 4: Generate content with ONE LLM call (ASYNC)
        llm_start = time.time()
        llm_response = await self.llm_service(complete_prompt)
        llm_time = int((time.time() - llm_start) * 1000)

        # STAGE LOGGING: LLM complete
        print(f"[GEN-LLM] variant={variant_id}, response_len={len(llm_response)}, llm_time={llm_time}ms")

        # Step 5: Parse response into element contents (sync operation)
        element_contents = self._parse_complete_response(
            llm_response=llm_response,
            variant_id=variant_id
        )

        # Step 6: Build content map for template assembly (sync operation)
        content_map = self._build_content_map(element_contents)

        # Step 7: Assemble template (sync operation)
        assembled_html = self.template_assembler.assemble_template(
            template_path=template_path,
            content_map=content_map
        )

        # STAGE LOGGING: HTML assembled
        total_time = int((time.time() - stage_start) * 1000)
        print(f"[GEN-HTML] variant={variant_id}, html_len={len(assembled_html)}, elements={len(element_contents)}, total_time={total_time}ms")

        # Step 8: Return result
        return {
            "html": assembled_html,
            "elements": element_contents,
            "metadata": {
                "variant_id": variant_id,
                "template_path": template_path,
                "element_count": len(element_contents),
                "generation_mode": "single_call_async"
            },
            "variant_id": variant_id,
            "template_path": template_path
        }

    def _parse_complete_response(
        self,
        llm_response: str,
        variant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Parse LLM response containing ALL elements into element content list.

        This method handles the single-call architecture where the LLM returns
        all elements in one JSON response.

        Args:
            llm_response: Raw LLM response string
            variant_id: The variant identifier

        Returns:
            List of element content dictionaries

        Raises:
            ValueError: If response cannot be parsed or is missing elements
        """
        # Parse JSON response
        try:
            all_elements_data = json.loads(llm_response)
        except json.JSONDecodeError:
            # Try to extract JSON from response (handles markdown code blocks)
            all_elements_data = self._extract_json_from_response(llm_response)

        # Load variant spec to get element structure
        spec = self.prompt_builder.load_variant_spec(variant_id)

        # Convert to element contents format
        element_contents = []

        for element in spec["elements"]:
            element_id = element["element_id"]
            element_type = element["element_type"]
            required_fields = element["required_fields"]
            placeholders = element["placeholders"]

            # Get this element's data from response
            if element_id not in all_elements_data:
                raise ValueError(
                    f"LLM response missing element: {element_id}. "
                    f"Expected elements: {[e['element_id'] for e in spec['elements']]}"
                )

            element_data = all_elements_data[element_id]

            # Validate required fields are present
            missing_fields = set(required_fields) - set(element_data.keys())
            if missing_fields:
                raise ValueError(
                    f"Element {element_id} missing required fields: {missing_fields}"
                )

            # Build element content dictionary
            element_content = {
                "element_id": element_id,
                "element_type": element_type,
                "placeholders": placeholders,
                "generated_content": element_data,
                "character_counts": {
                    field: len(str(value))
                    for field, value in element_data.items()
                }
            }

            element_contents.append(element_content)

        return element_contents

    # =========================================================================
    # DEPRECATED METHODS (kept for backward compatibility)
    # =========================================================================

    def _generate_elements_sequential(
        self,
        element_prompts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        [DEPRECATED] Generate element content sequentially (one at a time).

        This method is deprecated in favor of single-call architecture.
        Kept for backward compatibility only.

        Args:
            element_prompts: List of element prompt dictionaries

        Returns:
            List of dictionaries with generated content
        """
        element_contents = []

        for elem_prompt in element_prompts:
            content = self._generate_single_element(elem_prompt)
            element_contents.append(content)

        return element_contents

    def _generate_elements_parallel(
        self,
        element_prompts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        [DEPRECATED] Generate element content in parallel using ThreadPoolExecutor.

        This method is deprecated in favor of single-call architecture.
        Kept for backward compatibility only.

        Args:
            element_prompts: List of element prompt dictionaries

        Returns:
            List of dictionaries with generated content (in original order)
        """
        element_contents = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_elem = {
                executor.submit(self._generate_single_element, elem_prompt): i
                for i, elem_prompt in enumerate(element_prompts)
            }

            # Collect results in original order
            results = [None] * len(element_prompts)
            for future in as_completed(future_to_elem):
                index = future_to_elem[future]
                results[index] = future.result()

            element_contents = results

        return element_contents

    def _generate_single_element(
        self,
        element_prompt_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        [DEPRECATED] Generate content for a single element using LLM.

        This method is deprecated in favor of single-call architecture.
        Kept for backward compatibility only.

        Args:
            element_prompt_dict: Dictionary containing element prompt and metadata

        Returns:
            Dictionary with generated content and metadata
        """
        prompt = element_prompt_dict["prompt"]

        # Call LLM service
        llm_response = self.llm_service(prompt)

        # Parse JSON response
        try:
            generated_fields = json.loads(llm_response)
        except json.JSONDecodeError:
            # If LLM returns non-JSON, try to extract JSON from response
            generated_fields = self._extract_json_from_response(llm_response)

        # Validate that all required fields are present
        required_fields = element_prompt_dict["required_fields"]
        missing_fields = set(required_fields) - set(generated_fields.keys())

        if missing_fields:
            raise ValueError(
                f"LLM did not generate all required fields for {element_prompt_dict['element_id']}. "
                f"Missing: {missing_fields}"
            )

        return {
            "element_id": element_prompt_dict["element_id"],
            "element_type": element_prompt_dict["element_type"],
            "placeholders": element_prompt_dict["placeholders"],
            "generated_content": generated_fields,
            "character_counts": {
                field: len(value)
                for field, value in generated_fields.items()
            }
        }

    def _extract_json_from_response(self, response: str) -> Dict[str, str]:
        """
        Attempt to extract JSON from LLM response if it's not pure JSON.

        Args:
            response: LLM response string

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON cannot be extracted
        """
        # Try to find JSON block in markdown code fence
        import re

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Try to find raw JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        raise ValueError(f"Could not extract JSON from LLM response: {response[:200]}")

    def _build_content_map(
        self,
        element_contents: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Build content map for template assembly from generated elements.

        Args:
            element_contents: List of generated element content dictionaries

        Returns:
            Dictionary mapping placeholder names to content values
        """
        content_map = {}

        for elem_content in element_contents:
            placeholders = elem_content["placeholders"]
            generated_content = elem_content["generated_content"]

            # Map each field to its placeholder
            for field, placeholder in placeholders.items():
                if field in generated_content:
                    content_map[placeholder] = generated_content[field]

        return content_map

    def validate_character_counts(
        self,
        element_contents: List[Dict[str, Any]],
        variant_id: str
    ) -> Dict[str, Any]:
        """
        Validate that generated content meets character count requirements.

        Args:
            element_contents: List of generated element content
            variant_id: The variant identifier

        Returns:
            Dictionary with validation results:
                - valid (bool): Whether all counts are valid
                - violations (List): List of character count violations
        """
        spec = self.prompt_builder.load_variant_spec(variant_id)
        violations = []

        for i, element in enumerate(spec["elements"]):
            elem_content = element_contents[i]
            char_reqs = element["character_requirements"]
            char_counts = elem_content["character_counts"]

            for field, count in char_counts.items():
                req = char_reqs.get(field, {})
                min_chars = req.get("min", 0)
                max_chars = req.get("max", float('inf'))

                if not (min_chars <= count <= max_chars):
                    violations.append({
                        "element_id": elem_content["element_id"],
                        "field": field,
                        "actual_count": count,
                        "required_min": min_chars,
                        "required_max": max_chars
                    })

        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
