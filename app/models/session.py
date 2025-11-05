"""
Session Models for Context Management
======================================

Models for managing presentation context across slides.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SlideContext(BaseModel):
    """
    Context information for a single slide.

    Stored in session to maintain content flow across presentation.
    """
    slide_id: str
    slide_number: int
    slide_title: Optional[str] = None

    # Generated content summary
    content_summary: str = Field(
        description="Brief summary of generated content for this slide"
    )

    # Key topics/themes
    key_themes: List[str] = Field(
        default_factory=list,
        description="Main themes/topics covered in this slide"
    )

    # Generated content type
    content_type: str = Field(
        description="Type of content (text, table, or both)"
    )

    # Timestamp
    generated_at: datetime = Field(
        default_factory=datetime.now
    )


class SessionContext(BaseModel):
    """
    Complete session context for a presentation.

    Tracks conversation history to ensure content flow and coherence.
    """
    presentation_id: str = Field(
        description="Unique presentation identifier"
    )

    # Presentation metadata
    presentation_theme: Optional[str] = None
    target_audience: Optional[str] = None
    overall_narrative: Optional[str] = None

    # Slide history (ordered by slide_number)
    slide_history: List[SlideContext] = Field(
        default_factory=list,
        description="Chronological history of generated slides"
    )

    # Session metadata
    created_at: datetime = Field(
        default_factory=datetime.now
    )
    last_updated: datetime = Field(
        default_factory=datetime.now
    )
    total_slides_generated: int = Field(
        default=0,
        description="Total number of slides generated in this session"
    )

    def add_slide(self, slide_context: SlideContext):
        """Add a new slide to the history."""
        self.slide_history.append(slide_context)
        self.total_slides_generated += 1
        self.last_updated = datetime.now()

        # Keep only recent slides (configurable via settings)
        max_history = 5  # Can be made configurable
        if len(self.slide_history) > max_history:
            self.slide_history = self.slide_history[-max_history:]

    def get_recent_context(self, max_slides: int = 3) -> List[Dict[str, Any]]:
        """
        Get recent slide context for LLM prompt.

        Returns:
            List of slide context summaries for prompt injection
        """
        recent_slides = self.slide_history[-max_slides:]
        return [
            {
                "slide_number": slide.slide_number,
                "slide_title": slide.slide_title,
                "summary": slide.content_summary,
                "themes": slide.key_themes
            }
            for slide in recent_slides
        ]

    def get_context_summary(self) -> str:
        """
        Get a text summary of the presentation context.

        Useful for injecting into LLM prompts.
        """
        if not self.slide_history:
            return "This is the first slide in the presentation."

        context_parts = []

        if self.presentation_theme:
            context_parts.append(f"Presentation theme: {self.presentation_theme}")

        if self.target_audience:
            context_parts.append(f"Target audience: {self.target_audience}")

        context_parts.append(f"\nPrevious slides covered:")
        for slide in self.slide_history[-3:]:  # Last 3 slides
            context_parts.append(
                f"  - Slide {slide.slide_number} ({slide.slide_title}): {slide.content_summary}"
            )

        return "\n".join(context_parts)


class SessionCacheEntry(BaseModel):
    """
    Entry for session cache (used with Redis or in-memory cache).
    """
    session_context: SessionContext
    ttl: int = Field(
        default=3600,
        description="Time to live in seconds"
    )
    created_at: float = Field(
        default_factory=lambda: datetime.now().timestamp()
    )

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        current_time = datetime.now().timestamp()
        return (current_time - self.created_at) > self.ttl
