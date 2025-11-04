"""
Core v1.2 Deterministic Assembly Architecture

This package contains the core components for element-based content generation:
- ElementPromptBuilder: Builds targeted prompts for individual elements
- ContextBuilder: Builds slide and presentation context
- TemplateAssembler: Loads and assembles HTML templates
- ElementBasedContentGenerator: Main orchestrator for v1.2 workflow
"""

from .element_prompt_builder import ElementPromptBuilder
from .context_builder import ContextBuilder
from .template_assembler import TemplateAssembler
from .element_based_generator import ElementBasedContentGenerator

__all__ = [
    "ElementPromptBuilder",
    "ContextBuilder",
    "TemplateAssembler",
    "ElementBasedContentGenerator",
]
