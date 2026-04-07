"""File loader utility for reading PDF, TXT, and Markdown files."""
import io
from pathlib import Path


def load_file(uploaded_file) -> str:
    """
    Load and extract text from an uploaded file.

    Supports PDF, TXT, and Markdown file types.
    Returns the extracted text as a string.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return _load_pdf(uploaded_file)
    elif filename.endswith((".txt", ".md", ".markdown")):
        return _load_text(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {Path(uploaded_file.name).suffix}")


def _load_pdf(uploaded_file) -> str:
    """Extract text from a PDF file."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except ImportError:
        raise ImportError("pypdf is required to read PDF files. Install with: pip install pypdf")


def _load_text(uploaded_file) -> str:
    """Extract text from a TXT or Markdown file."""
    raw = uploaded_file.read()
    # Try UTF-8 first, fall back to latin-1
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")
