"""Text cleaning utilities for preprocessing input text."""
import re
import unicodedata

# Maximum characters to keep in a cleaned text before truncation
MAX_CLEAN_TEXT_LENGTH = 12_000

# Default length for short text previews/summaries
TEXT_SUMMARY_LENGTH = 500


def clean_text(text_input) -> str:
    """
    Clean and normalize input text for AI processing.

    Steps:
    1. Normalize unicode characters
    2. Remove null bytes and control characters
    3. Normalize whitespace
    4. Remove excessive blank lines
    5. Truncate to max token-friendly length
    """
    def process_chunk(chunk):
        if not chunk or not chunk.strip():
            return ""

        # Normalize unicode (e.g., convert special quotes to ASCII)
        chunk = unicodedata.normalize("NFKD", chunk)

        # Remove null bytes and non-printable control characters (keep newlines/tabs)
        chunk = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", chunk)

        # Collapse multiple spaces/tabs into a single space
        chunk = re.sub(r"[ \t]+", " ", chunk)

        # Collapse more than 2 consecutive newlines into 2
        chunk = re.sub(r"\n{3,}", "\n\n", chunk)

        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in chunk.splitlines()]
        chunk = "\n".join(lines)

        # Final strip
        return chunk.strip()

    cleaned_text = ""
    for chunk in text_input:
        cleaned_text += process_chunk(chunk)

    # Truncate to ~12,000 characters to avoid token overflows
    if len(cleaned_text) > MAX_CLEAN_TEXT_LENGTH:
        cleaned_text = cleaned_text[:MAX_CLEAN_TEXT_LENGTH] + "\n\n[Content truncated for processing...]"

    return cleaned_text


def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """Extract simple keyword list from text (no NLP dependency)."""
    # Remove punctuation and lowercase
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    words = cleaned.split()

    # Simple stopword removal
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can", "that",
        "this", "these", "those", "it", "its", "we", "our", "you", "your",
        "they", "their", "he", "she", "his", "her", "not", "also", "more",
    }

    # Count word frequency
    freq: dict = {}
    for word in words:
        if len(word) > 3 and word not in stopwords:
            freq[word] = freq.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Return text truncated to max_length characters with optional suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix
