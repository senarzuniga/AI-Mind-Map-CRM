"""CRM memory store for saving and loading company analyses."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

MEMORY_DIR = Path(__file__).parent.parent / "data" / "memory"


def _ensure_memory_dir() -> None:
    """Ensure the memory directory exists."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def save_analysis(
    company_id: str,
    company_name: str,
    input_text: str,
    structured_data: dict,
    mindmap: dict,
    insights: dict,
) -> str:
    """
    Save a company analysis to the CRM memory store.

    Returns the file path where the analysis was saved.
    """
    _ensure_memory_dir()

    record = {
        "company_id": company_id,
        "company_name": company_name,
        "date": datetime.utcnow().isoformat(),
        "input": input_text[:500] + "..." if len(input_text) > 500 else input_text,
        "structured_data": structured_data,
        "mindmap": mindmap,
        "insights": insights,
    }

    # Use company_id as the filename (sanitized)
    safe_id = _sanitize_id(company_id)
    file_path = MEMORY_DIR / f"{safe_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    return str(file_path)


def load_analysis(company_id: str) -> Optional[dict]:
    """
    Load a company analysis from the CRM memory store.

    Returns the analysis dict, or None if not found.
    """
    safe_id = _sanitize_id(company_id)
    file_path = MEMORY_DIR / f"{safe_id}.json"

    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_companies() -> list:
    """
    List all companies stored in the CRM memory.

    Returns a list of dicts with company_id, company_name, and date.
    """
    _ensure_memory_dir()
    companies = []

    for file_path in sorted(MEMORY_DIR.glob("*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                record = json.load(f)
            companies.append(
                {
                    "company_id": record.get("company_id", file_path.stem),
                    "company_name": record.get("company_name", "Unknown"),
                    "date": record.get("date", "Unknown"),
                }
            )
        except (json.JSONDecodeError, OSError):
            continue

    return companies


def delete_analysis(company_id: str) -> bool:
    """
    Delete a company analysis from the CRM memory store.

    Returns True if deleted, False if not found.
    """
    safe_id = _sanitize_id(company_id)
    file_path = MEMORY_DIR / f"{safe_id}.json"

    if file_path.exists():
        file_path.unlink()
        return True
    return False


def _sanitize_id(company_id: str) -> str:
    """Sanitize a company ID for use as a filename."""
    import re
    sanitized = re.sub(r"[^\w\-]", "_", company_id.strip().lower())
    return sanitized[:100]  # Limit length
