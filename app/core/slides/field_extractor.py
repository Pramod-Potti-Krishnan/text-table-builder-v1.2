"""
Field Extractor for Slides Module

Extracts structured fields from generated HTML content for Layout Service integration.
Provides plain text extraction from HTML elements.

Version: 1.2.1
"""

import re
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


def strip_html_tags(html: str) -> str:
    """
    Remove HTML tags from string, returning plain text.

    Args:
        html: HTML string with tags

    Returns:
        Plain text with tags removed
    """
    if not html:
        return ""

    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', ' ', html)

    # Normalize whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()

    return clean


def extract_title(html: str) -> Optional[str]:
    """
    Extract title text from HTML content.

    Looks for h1, h2, or elements with title-like styling.

    Args:
        html: HTML content

    Returns:
        Extracted title text or None
    """
    if not html:
        return None

    # Try h1 first
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if h1_match:
        return strip_html_tags(h1_match.group(1))

    # Try h2 if no h1
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL | re.IGNORECASE)
    if h2_match:
        return strip_html_tags(h2_match.group(1))

    # Try elements with large font size (title-like)
    large_text = re.search(r'font-size:\s*(?:4[89]|[5-9]\d|[1-9]\d\d)px[^>]*>([^<]+)<', html, re.IGNORECASE)
    if large_text:
        return strip_html_tags(large_text.group(1))

    return None


def extract_subtitle(html: str) -> Optional[str]:
    """
    Extract subtitle text from HTML content.

    Looks for elements with subtitle-like styling (font-size ~42px, muted colors).

    Args:
        html: HTML content

    Returns:
        Extracted subtitle text or None
    """
    if not html:
        return None

    # Look for font-size around 42px (common subtitle size)
    subtitle_match = re.search(
        r'font-size:\s*(?:3[89]|4[0-5])px[^>]*>([^<]+)<',
        html,
        re.IGNORECASE
    )
    if subtitle_match:
        return strip_html_tags(subtitle_match.group(1))

    # Look for h3 elements (often used for subtitles)
    h3_match = re.search(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL | re.IGNORECASE)
    if h3_match:
        return strip_html_tags(h3_match.group(1))

    # Look for elements with muted color classes
    muted_match = re.search(
        r'class="[^"]*(?:subtitle|muted|secondary)[^"]*"[^>]*>([^<]+)<',
        html,
        re.IGNORECASE
    )
    if muted_match:
        return strip_html_tags(muted_match.group(1))

    return None


def extract_section_number(html: str) -> Optional[str]:
    """
    Extract section number from section divider slide.

    Looks for patterns like "01", "02", "Section 1", etc.

    Args:
        html: HTML content

    Returns:
        Section number string or None
    """
    if not html:
        return None

    # Look for explicit section number pattern (01, 02, etc.)
    number_match = re.search(r'>\s*(\d{1,2})\s*<', html)
    if number_match:
        return number_match.group(1).zfill(2)

    # Look for "Section X" or "Part X"
    section_match = re.search(r'(?:Section|Part|Chapter)\s*(\d+)', html, re.IGNORECASE)
    if section_match:
        return section_match.group(1).zfill(2)

    return None


def extract_author_info(html: str) -> Optional[str]:
    """
    Extract author/attribution information from title slide.

    Looks for author names, company info, attribution text.

    Args:
        html: HTML content

    Returns:
        Author info string or None
    """
    if not html:
        return None

    # Look for attribution div or author class
    author_match = re.search(
        r'class="[^"]*(?:author|attribution|presenter)[^"]*"[^>]*>(.*?)</(?:div|span|p)>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    if author_match:
        return strip_html_tags(author_match.group(1))

    # Look for "By" or "Presented by" pattern
    by_match = re.search(r'(?:By|Presented by|Author:?)\s*([^<\n]+)', html, re.IGNORECASE)
    if by_match:
        return strip_html_tags(by_match.group(1))

    return None


def extract_contact_info(html: str) -> Optional[str]:
    """
    Extract contact information from closing slide.

    Looks for email, phone, website patterns.

    Args:
        html: HTML content

    Returns:
        Contact info string or None
    """
    if not html:
        return None

    contact_parts = []

    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', html)
    if email_match:
        contact_parts.append(email_match.group(0))

    # Extract phone
    phone_match = re.search(r'[\+\d\-\(\)\s]{10,}', html)
    if phone_match:
        contact_parts.append(phone_match.group(0).strip())

    # Extract URL
    url_match = re.search(r'(?:https?://)?(?:www\.)?[\w\.-]+\.\w{2,}(?:/\S*)?', html)
    if url_match:
        contact_parts.append(url_match.group(0))

    return ' | '.join(contact_parts) if contact_parts else None


def extract_closing_message(html: str) -> Optional[str]:
    """
    Extract closing message from closing slide.

    Looks for "Thank You", "Questions?", etc.

    Args:
        html: HTML content

    Returns:
        Closing message string or None
    """
    if not html:
        return None

    # Common closing messages
    closing_patterns = [
        r'(Thank\s*You[\s!?]*)',
        r'(Questions\s*\??)',
        r'(Contact\s*Us)',
        r'(Get\s*in\s*Touch)',
        r'(Let\'s\s*Connect)',
    ]

    for pattern in closing_patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_background_image(html: str) -> Optional[str]:
    """
    Extract background image URL from HTML content.

    Args:
        html: HTML content

    Returns:
        Image URL or None
    """
    if not html:
        return None

    # Look for background-image in style
    bg_match = re.search(r'background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)', html, re.IGNORECASE)
    if bg_match:
        return bg_match.group(1)

    # Look for img src
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if img_match:
        return img_match.group(1)

    return None


def extract_structured_fields(html: str, layout_type: str) -> Dict[str, Any]:
    """
    Extract structured fields from generated HTML based on layout type.

    Args:
        html: Generated HTML content
        layout_type: Layout type identifier (H1-generated, H1-structured, H2-section, etc.)

    Returns:
        Dictionary with extracted structured fields
    """
    fields: Dict[str, Any] = {}

    if not html:
        logger.warning("Empty HTML provided for field extraction")
        return fields

    # Common fields for all layouts
    fields["slide_title"] = extract_title(html)
    fields["subtitle"] = extract_subtitle(html)

    # Layout-specific extractions
    if layout_type in ("H1-structured", "H1_STRUCTURED"):
        fields["author_info"] = extract_author_info(html)
        # Extract date if present
        date_match = re.search(r'(\d{4}|\w+\s+\d{4})', html)
        if date_match:
            fields["date_info"] = date_match.group(1)

    elif layout_type in ("H1-generated", "H1_GENERATED", "L29"):
        fields["background_image"] = extract_background_image(html)
        # Check if fallback gradient is used
        fields["image_fallback"] = "linear-gradient" in html and not extract_background_image(html)

    elif layout_type in ("H2-section", "H2_SECTION"):
        fields["section_number"] = extract_section_number(html)

    elif layout_type in ("H3-closing", "H3_CLOSING"):
        fields["contact_info"] = extract_contact_info(html)
        fields["closing_message"] = extract_closing_message(html)

    # Log extraction summary
    extracted = {k: v for k, v in fields.items() if v is not None}
    logger.debug(f"Extracted {len(extracted)} fields from {layout_type}: {list(extracted.keys())}")

    return fields


def extract_body_content(html: str) -> Optional[str]:
    """
    Extract main body content from HTML (bullets, paragraphs).

    Used for I-series content_html extraction.

    Args:
        html: HTML content

    Returns:
        Body content HTML or None
    """
    if not html:
        return None

    # Look for ul/ol lists
    list_match = re.search(r'(<[uo]l[^>]*>.*?</[uo]l>)', html, re.DOTALL | re.IGNORECASE)
    if list_match:
        return list_match.group(1)

    # Look for content div
    content_match = re.search(
        r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    if content_match:
        return content_match.group(1).strip()

    # Look for multiple paragraphs
    paragraphs = re.findall(r'<p[^>]*>.*?</p>', html, re.DOTALL | re.IGNORECASE)
    if len(paragraphs) > 1:
        return '\n'.join(paragraphs)

    return None
