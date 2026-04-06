"""CRM memory store for saving and loading company analyses."""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from utils.text_cleaner import TEXT_SUMMARY_LENGTH, truncate_text

MEMORY_DIR = Path(__file__).parent.parent / "data" / "memory"

# Strict allowlist: only word chars and hyphens (no dots, slashes, or spaces)
_SAFE_ID_RE = re.compile(r"^[\w\-]{1,100}$")


def _ensure_memory_dir() -> None:
    """Ensure the memory directory exists."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _safe_path(company_id: str) -> Path:
    """
    Convert a user-supplied company_id into a safe filesystem path.

    1. Sanitize: replace any character not in [word, hyphen] with '_'.
    2. Validate: assert the result matches the strict allowlist regex.
    3. Construct: join with MEMORY_DIR (no traversal possible).
    """
    sanitized = re.sub(r"[^\w\-]", "_", company_id.strip().lower())[:100]

    # Strict allowlist check — raises ValueError if somehow not safe
    if not _SAFE_ID_RE.match(sanitized):
        raise ValueError(f"Invalid company_id after sanitization: {sanitized!r}")

    # MEMORY_DIR is a fixed, trusted base; sanitized contains no separators
    return MEMORY_DIR / f"{sanitized}.json"


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
        "date": datetime.now(timezone.utc).isoformat(),
        "input": truncate_text(input_text, TEXT_SUMMARY_LENGTH),
        "structured_data": structured_data,
        "mindmap": mindmap,
        "insights": insights,
    }

    file_path = _safe_path(company_id)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    return str(file_path)


def load_analysis(company_id: str) -> Optional[dict]:
    """
    Load a company analysis from the CRM memory store.

    Returns the analysis dict, or None if not found.
    """
    file_path = _safe_path(company_id)

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
    file_path = _safe_path(company_id)

    if file_path.exists():
        file_path.unlink()
        return True
    return False
