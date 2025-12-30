"""
Component Assembly Agent with Chain of Thought Reasoning
=========================================================

The ComponentAssemblyAgent is the master orchestrator that:
1. Receives input context (prompt, grid, audience, purpose)
2. Reasons through storytelling needs (CoT Step 1)
3. Plans space allocation (CoT Step 2)
4. Selects components (CoT Step 3)
5. Configures layout (CoT Step 4)
6. Generates content and assembles HTML (CoT Step 5)

This agent uses tools to perform each step, maintaining
transparency about its reasoning process.
"""

import json
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass

from .registry import get_registry
from .tools import (
    analyze_space,
    get_available_components,
    select_component_layout,
    generate_component_content,
    assemble_html,
    get_tools_description
)
from .constraints import LayoutBuilder
from ...models.component_models import (
    InputContext,
    StorytellingNeeds,
    SpaceBudget,
    ComponentChoice,
    AssemblyInfo,
    AudienceType,
    PurposeType,
    SpaceAnalysis,
    LayoutSelection,
    AssemblyResult
)


# =============================================================================
# System Prompt for Chain of Thought Reasoning
# =============================================================================

AGENT_SYSTEM_PROMPT = """You are a presentation slide designer. You will receive INPUT CONTEXT containing:
- User prompt (what content to present)
- Audience type (executives, technical, general, etc.)
- Purpose (inform, persuade, inspire, educate)
- Grid constraints (available space)

Given this input, reason through the problem step-by-step:

1. STORYTELLING NEEDS: Given [audience] + [purpose], determine what elements
   the audience needs to understand this content:
   - Evidence/proof? → metrics, data points
   - Explanation? → bullets, descriptions
   - Comparison? → columns, before/after
   - Process? → numbered steps
   - Highlight? → callout box, sidebar

2. SPACE BUDGETING: Allocate percentages of available space:
   - "I'll give 40% to metrics for credibility"
   - "60% for the main explanation with bullets"

3. COMPONENT MATCHING: Select components that fit your space budget.
   - metrics_card: KPIs, statistics, numbers with labels
   - numbered_card: Steps, phases, numbered key points
   - comparison_column: Comparing options, pros/cons
   - colored_section: Categories with bullet lists
   - sidebar_box: Key insights, highlights, callouts

4. LAYOUT & ASSEMBLY: Configure arrangement and generate content.

OUTPUT FORMAT:
Return a JSON object with your reasoning:
{
  "storytelling_needs": {
    "main_message": "The key insight to convey",
    "needs_evidence": true/false,
    "needs_explanation": true/false,
    "needs_comparison": true/false,
    "needs_process": true/false,
    "needs_callout": true/false,
    "evidence_priority": "high/medium/low"
  },
  "space_budget": {
    "allocations": {"component_type": percentage, ...},
    "reasoning": "Why this allocation"
  },
  "component_choice": {
    "primary_component": "component_id",
    "primary_count": number,
    "secondary_component": "component_id or null",
    "secondary_count": number or null,
    "selection_reasoning": "Why these components"
  }
}

ALWAYS explain your reasoning. Never jump straight to component selection
without explaining WHY that component fits the story."""


# =============================================================================
# Agent Result Dataclass
# =============================================================================

@dataclass
class AgentResult:
    """Result from ComponentAssemblyAgent.generate()"""
    success: bool
    html: str
    assembly_info: AssemblyInfo
    reasoning: Dict[str, Any]
    error: Optional[str] = None


# =============================================================================
# Component Assembly Agent
# =============================================================================

class ComponentAssemblyAgent:
    """
    Master orchestrator for component-based slide generation.

    Uses Chain of Thought reasoning to:
    1. Understand storytelling needs
    2. Plan space allocation
    3. Select appropriate components
    4. Generate content
    5. Assemble final HTML
    """

    def __init__(
        self,
        llm_service: Optional[Callable] = None,
        enable_reasoning_output: bool = True
    ):
        """
        Initialize the agent.

        Args:
            llm_service: Async callable that takes prompt string and returns response
            enable_reasoning_output: Whether to include reasoning in output
        """
        self.llm_service = llm_service
        self.enable_reasoning_output = enable_reasoning_output
        self.registry = get_registry()
        self.layout_builder = LayoutBuilder()

    async def generate(
        self,
        prompt: str,
        grid_width: int,
        grid_height: int,
        audience: Optional[str] = None,
        purpose: Optional[str] = None,
        presentation_title: Optional[str] = None,
        slide_position: Optional[int] = None
    ) -> AgentResult:
        """
        Generate slide content using component assembly.

        This is the main entry point that orchestrates the full
        Chain of Thought reasoning process.

        Args:
            prompt: User's content request
            grid_width: Available width in grid units
            grid_height: Available height in grid units
            audience: Target audience type
            purpose: Slide purpose
            presentation_title: Optional presentation context
            slide_position: Optional slide position

        Returns:
            AgentResult with HTML, assembly info, and reasoning
        """
        try:
            # Step 0: Build input context
            context = InputContext(
                prompt=prompt,
                grid_width=grid_width,
                grid_height=grid_height,
                audience=AudienceType(audience) if audience else None,
                purpose=PurposeType(purpose) if purpose else None,
                presentation_title=presentation_title,
                slide_position=slide_position
            )

            # Step 1-3: Get agent's reasoning about component selection
            reasoning = await self._reason_about_components(context)

            if not reasoning:
                return AgentResult(
                    success=False,
                    html="",
                    assembly_info=None,
                    reasoning={},
                    error="Failed to reason about component selection"
                )

            # Extract component choice
            component_choice = reasoning.get("component_choice", {})
            primary_component = component_choice.get("primary_component")
            primary_count = component_choice.get("primary_count", 3)

            if not primary_component:
                return AgentResult(
                    success=False,
                    html="",
                    assembly_info=None,
                    reasoning=reasoning,
                    error="No component selected"
                )

            # Step 4: Select layout
            layout = select_component_layout(
                component_id=primary_component,
                instance_count=primary_count,
                grid_width=grid_width,
                grid_height=grid_height
            )

            if not layout:
                return AgentResult(
                    success=False,
                    html="",
                    assembly_info=None,
                    reasoning=reasoning,
                    error=f"Failed to configure layout for {primary_component}"
                )

            # Step 5: Generate content
            content = await generate_component_content(
                component_id=primary_component,
                user_prompt=prompt,
                instance_count=layout.instance_count,
                char_limits=layout.scaled_char_limits,
                llm_service=self.llm_service,
                context={
                    "audience": audience,
                    "purpose": purpose,
                    "presentation_title": presentation_title
                }
            )

            if not content:
                return AgentResult(
                    success=False,
                    html="",
                    assembly_info=None,
                    reasoning=reasoning,
                    error="Failed to generate content"
                )

            # Step 6: Assemble HTML
            result = assemble_html(
                component_id=primary_component,
                layout=layout,
                content=content
            )

            # Build assembly info
            storytelling = reasoning.get("storytelling_needs", {})
            space_budget = reasoning.get("space_budget", {})

            assembly_info = AssemblyInfo(
                component_type=primary_component,
                component_count=layout.instance_count,
                arrangement=result.arrangement,
                variants_used=result.variants_used,
                agent_reasoning=component_choice.get("selection_reasoning", ""),
                storytelling_needs=StorytellingNeeds(**storytelling) if storytelling else None,
                space_budget=SpaceBudget(**space_budget) if space_budget else None
            )

            return AgentResult(
                success=True,
                html=result.html,
                assembly_info=assembly_info,
                reasoning=reasoning if self.enable_reasoning_output else {}
            )

        except Exception as e:
            return AgentResult(
                success=False,
                html="",
                assembly_info=None,
                reasoning={},
                error=str(e)
            )

    async def _reason_about_components(
        self,
        context: InputContext
    ) -> Optional[Dict[str, Any]]:
        """
        Use LLM to reason about component selection.

        This implements the Chain of Thought process:
        1. Storytelling needs analysis
        2. Space budget planning
        3. Component selection
        """
        if not self.llm_service:
            # Fallback to heuristic-based selection
            return self._heuristic_component_selection(context)

        # Get available components info
        components = get_available_components()
        component_info = "\n".join([
            f"- {c.component_id}: {c.description} (use cases: {', '.join(c.use_cases[:3])})"
            for c in components
        ])

        # Analyze space
        space = analyze_space(context.grid_width, context.grid_height)

        # Build reasoning prompt
        prompt = f"""{AGENT_SYSTEM_PROMPT}

INPUT CONTEXT:
- Prompt: "{context.prompt}"
- Audience: {context.audience.value if context.audience else "general"}
- Purpose: {context.purpose.value if context.purpose else "inform"}
- Grid: {context.grid_width}x{context.grid_height} ({space.space_category} space)
- Layout options: {', '.join(space.layout_options)}

AVAILABLE COMPONENTS:
{component_info}

RECOMMENDED COUNTS (based on space):
{json.dumps(space.recommended_counts, indent=2)}

Now reason through the problem and output your decision as JSON:"""

        # Call LLM
        response = await self.llm_service(prompt)

        # Parse response
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            # If parsing fails, use heuristic
            return self._heuristic_component_selection(context)

    def _heuristic_component_selection(
        self,
        context: InputContext
    ) -> Dict[str, Any]:
        """
        Fallback heuristic-based component selection.

        Used when LLM is not available or fails.
        """
        prompt_lower = context.prompt.lower()

        # Detect content type from prompt
        needs_evidence = any(word in prompt_lower for word in
            ["metric", "kpi", "number", "percent", "growth", "revenue", "performance", "data"])
        needs_process = any(word in prompt_lower for word in
            ["step", "phase", "process", "stage", "workflow", "sequence"])
        needs_comparison = any(word in prompt_lower for word in
            ["compare", "versus", "vs", "difference", "option", "alternative", "pros", "cons"])
        needs_explanation = any(word in prompt_lower for word in
            ["explain", "describe", "overview", "summary", "key points", "benefits"])

        # Select component based on detected needs
        if needs_evidence:
            primary_component = "metrics_card"
            primary_count = 3
            reasoning = "Prompt indicates need for metrics/data visualization"
        elif needs_process:
            primary_component = "numbered_card"
            primary_count = 4
            reasoning = "Prompt indicates a sequential/process flow"
        elif needs_comparison:
            primary_component = "comparison_column"
            primary_count = 3
            reasoning = "Prompt indicates comparison between options"
        elif needs_explanation:
            primary_component = "colored_section"
            primary_count = 3
            reasoning = "Prompt indicates explanatory content with categories"
        else:
            # Default to colored section for general content
            primary_component = "colored_section"
            primary_count = 3
            reasoning = "Default selection for general content"

        # Adjust count based on space
        space = analyze_space(context.grid_width, context.grid_height)
        recommended = space.recommended_counts.get(primary_component, primary_count)
        primary_count = min(primary_count, recommended)

        # Determine evidence priority based on audience
        evidence_priority = "medium"
        if context.audience == AudienceType.EXECUTIVE:
            evidence_priority = "high"
        elif context.audience == AudienceType.TECHNICAL:
            evidence_priority = "high"

        return {
            "storytelling_needs": {
                "main_message": "Content based on user prompt",
                "needs_evidence": needs_evidence,
                "needs_explanation": needs_explanation,
                "needs_comparison": needs_comparison,
                "needs_process": needs_process,
                "needs_callout": False,
                "evidence_priority": evidence_priority
            },
            "space_budget": {
                "allocations": {primary_component: 100},
                "reasoning": f"Using full space for {primary_component}"
            },
            "component_choice": {
                "primary_component": primary_component,
                "primary_count": primary_count,
                "secondary_component": None,
                "secondary_count": None,
                "selection_reasoning": reasoning
            }
        }


# =============================================================================
# Quick Generation Function
# =============================================================================

async def generate_with_components(
    prompt: str,
    grid_width: int,
    grid_height: int,
    llm_service: Callable,
    audience: Optional[str] = None,
    purpose: Optional[str] = None
) -> AgentResult:
    """
    Convenience function for quick component-based generation.

    Args:
        prompt: User's content request
        grid_width: Available width in grid units
        grid_height: Available height in grid units
        llm_service: Async LLM service callable
        audience: Optional audience type
        purpose: Optional slide purpose

    Returns:
        AgentResult with HTML and assembly info
    """
    agent = ComponentAssemblyAgent(llm_service=llm_service)
    return await agent.generate(
        prompt=prompt,
        grid_width=grid_width,
        grid_height=grid_height,
        audience=audience,
        purpose=purpose
    )
