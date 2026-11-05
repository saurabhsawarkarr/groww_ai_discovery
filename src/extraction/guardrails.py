"""Guardrails and deterministic verification for qualitative evidence extraction.

Enforces zero model hallucination in evidence quotes through exact substring
matching, boundary index locating for UI highlighting, and unknown attribute tracking.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("groww_discovery.extraction.guardrails")

CORE_INVESTOR_DIMENSIONS = [
    "investor_context",
    "motivation",
    "expectation",
    "trigger_or_situation",
    "friction_or_concern",
    "monitoring_behaviour",
    "workaround",
    "reported_outcome",
]


def normalize_whitespace_lower(text: str) -> str:
    """Normalize internal whitespaces and lowercase for substring comparison."""
    if not text:
        return ""
    # Strip smart quotes and standardize punctuation
    cleaned = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return " ".join(cleaned.split()).lower()


def validate_substring(raw_text: str, quote: str) -> bool:
    """Deterministic Zero-Hallucination quote verification.

    Normalizes whitespace and verifies that quote exists as an exact contiguous
    substring of raw_text.
    """
    if not raw_text or not quote:
        return False

    clean_raw = normalize_whitespace_lower(raw_text)
    clean_quote = normalize_whitespace_lower(quote)

    if not clean_quote or len(clean_quote) < 3:
        return False

    return clean_quote in clean_raw


def clean_quote_delimiters(quote: str) -> str:
    """Strip leading and trailing quote marks that LLMs commonly prepend/append."""
    if not quote:
        return ""
    cleaned = quote.strip()
    # Strip enclosing quotes
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1].strip()
    return cleaned


def find_quote_span(raw_text: str, quote: str) -> Optional[Tuple[int, int]]:
    """Locate the exact character start and end index of quote within raw_text.

    Supports UI quote highlights and source provenance audits.
    """
    if not raw_text or not quote:
        return None

    cleaned_quote = clean_quote_delimiters(quote)
    if not cleaned_quote:
        return None

    # Case-insensitive direct search
    pattern = re.escape(cleaned_quote)
    match = re.search(pattern, raw_text, re.IGNORECASE)
    if match:
        return match.span()

    # Whitespace-flexible regex search
    words = [re.escape(w) for w in cleaned_quote.split()]
    if words:
        fuzzy_pattern = r"\s+".join(words)
        match = re.search(fuzzy_pattern, raw_text, re.IGNORECASE)
        if match:
            return match.span()

    return None


def audit_missing_dimensions(payload: Dict[str, Any]) -> List[str]:
    """Catalog which core discovery dimensions were not explicitly stated."""
    missing: List[str] = []
    for dim in CORE_INVESTOR_DIMENSIONS:
        val = payload.get(dim)
        if val is None or str(val).strip().lower() in ["", "none", "null", "unknown"]:
            missing.append(dim)
    return missing
