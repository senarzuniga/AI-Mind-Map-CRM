"""Input parser: normalizes and prepares input for AI processing."""
from pathlib import Path

from utils.text_cleaner import clean_text


def parse(input_data) -> str:
    """
    Parse input data into clean text ready for AI processing.

    Accepts:
    - str: raw text or concept
    - bytes: raw file bytes (decoded as UTF-8)
    - Path: file path to read

    Returns cleaned text string.
    """
    if isinstance(input_data, Path):
        raw = input_data.read_text(encoding="utf-8", errors="replace")
    elif isinstance(input_data, bytes):
        try:
            raw = input_data.decode("utf-8")
        except UnicodeDecodeError:
            raw = input_data.decode("latin-1")
    elif isinstance(input_data, str):
        raw = input_data
    else:
        raise TypeError(f"Unsupported input type: {type(input_data)}")

    return clean_text(raw)
