"""Presentation Builder: generates slide-like output from analysis data."""
import json
from typing import Optional


def build_slides(presentation_data: dict) -> list:
    """
    Convert presentation data into a list of slide dicts.

    Each slide has: title, type, content (list of strings)
    """
    return presentation_data.get("slides", [])


def format_slide_as_text(slide: dict) -> str:
    """Format a single slide as plain text for display."""
    lines = [f"# {slide.get('title', 'Slide')}"]
    lines.append("")
    for item in slide.get("content", []):
        lines.append(f"• {item}")
    return "\n".join(lines)


def presentation_to_markdown(presentation_data: dict) -> str:
    """Convert full presentation to a markdown string."""
    lines = [f"# {presentation_data.get('title', 'Presentation')}", ""]

    for i, slide in enumerate(presentation_data.get("slides", []), 1):
        lines.append(f"## Slide {i}: {slide.get('title', '')}")
        lines.append("")
        for item in slide.get("content", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
