# Agenda Slide Content Generation

You are generating content for an **Agenda Slide** in a professional presentation.

## Context

**Presentation Title**: {presentation_title}
**Presentation Type**: {presentation_type}
**Tone**: {tone}
**Target Audience**: {audience}

## Slide Purpose

{slide_purpose}

## Content Requirements

Generate an agenda that:
1. Clearly outlines the main topics to be covered
2. Uses concise, action-oriented language
3. Follows a logical progression
4. Matches the overall presentation tone

## Character Constraints

| Field | Target | Min | Max |
|-------|--------|-----|-----|
| Title | 40 | 30 | 50 |
| Subtitle | 80 | 60 | 100 |
| Each Item | 50 | 40 | 60 |

## Output Format

Return a JSON object with:
```json
{
  "title": "Agenda title here",
  "subtitle": "Brief description of what will be covered",
  "items": [
    {"number": 1, "text": "First topic"},
    {"number": 2, "text": "Second topic"},
    {"number": 3, "text": "Third topic"},
    {"number": 4, "text": "Fourth topic"}
  ]
}
```

## Guidelines

- Use active voice and strong verbs
- Keep items parallel in structure
- Ensure logical flow between topics
- Match the formality level to the audience
- Do NOT use placeholder text
