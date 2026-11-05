"""PII sanitization and text normalization module.

Scrubs personally identifiable information (Indian mobile numbers, PAN cards,
emails, bank account numbers, IFSC codes, UPI IDs, Aadhaar numbers) and cleans
unreadable Unicode artifacts from incoming text records.
"""

from datetime import datetime
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from src.connectors.base import RawRecord

logger = logging.getLogger("groww_discovery.preprocessing.sanitizer")

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "configs" / "pii_patterns.json"

# Built-in fallback regex patterns for Indian financial PII
BUILTIN_PATTERNS = [
    {
        "name": "indian_phone",
        "regex": r"(?:\+91[\-\s]?|91[\-\s]?|0)?[6-9]\d{9}\b",
        "replacement": "[REDACTED_PHONE]",
        "description": "Indian 10-digit mobile phone numbers with optional +91/91/0 prefix",
    },
    {
        "name": "pan_card",
        "regex": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        "replacement": "[REDACTED_PAN]",
        "description": "Indian Permanent Account Number (PAN)",
    },
    {
        "name": "email_address",
        "regex": r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b",
        "replacement": "[REDACTED_EMAIL]",
        "description": "Standard email addresses",
    },
    {
        "name": "ifsc_code",
        "regex": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
        "replacement": "[REDACTED_IFSC]",
        "description": "Indian Financial System Code (IFSC)",
    },
    {
        "name": "bank_account",
        "regex": r"(?i)\b(?:a/c|acc(?:ount)?(?:\s*no(?:\.|umber)?)?[:\s#]*)\s*\d{9,18}\b|\b\d{11,18}\b",
        "replacement": "[REDACTED_BANK_INFO]",
        "description": "Indian bank account numbers with keywords or 11-18 consecutive digits",
    },
    {
        "name": "upi_id",
        "regex": r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b",
        "replacement": "[REDACTED_UPI]",
        "description": "UPI Virtual Payment Address (VPA)",
    },
    {
        "name": "aadhaar_number",
        "regex": r"\b[2-9]\d{3}[\s\-]\d{4}[\s\-]\d{4}\b",
        "replacement": "[REDACTED_AADHAAR]",
        "description": "12-digit Indian Aadhaar number formatted with spaces or hyphens",
    },
]


class PIISanitizer:
    """Sanitizes text by masking sensitive Indian financial PII tokens."""

    def __init__(self, patterns_path: Optional[Union[str, Path]] = None):
        self.patterns = self._load_patterns(patterns_path)
        self.compiled_rules = [
            (p["name"], re.compile(p["regex"]), p["replacement"])
            for p in self.patterns
        ]

    def _load_patterns(self, custom_path: Optional[Union[str, Path]] = None) -> List[Dict[str, str]]:
        """Load pattern specifications from JSON config file or fallback to defaults."""
        path = Path(custom_path) if custom_path else DEFAULT_CONFIG_PATH
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                patterns = data.get("patterns", [])
                if patterns:
                    return patterns
            except Exception as e:
                logger.warning("Failed to load PII config from %s: %s. Using built-in patterns.", path, str(e))
        return BUILTIN_PATTERNS

    @staticmethod
    def normalize_text(text: str) -> str:
        """Strip non-printable Unicode control characters and collapse excessive whitespace."""
        if not text:
            return ""
        # Remove non-printable control characters except standard newlines and tabs
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", " ", text)
        # Collapse multiple spaces and newlines
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
        return cleaned.strip()

    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Sanitize text and return cleaned string along with list of matched redaction names.

        Args:
            text: Raw input text.

        Returns:
            Tuple of (sanitized_text, list_of_redaction_rule_names_applied)
        """
        if not text:
            return "", []

        cleaned = self.normalize_text(text)
        applied_redactions: List[str] = []

        for name, pattern, replacement in self.compiled_rules:
            if pattern.search(cleaned):
                cleaned = pattern.sub(replacement, cleaned)
                applied_redactions.append(name)

        return cleaned, applied_redactions

    def sanitize_record(self, record: RawRecord) -> Tuple[RawRecord, List[str]]:
        """Sanitize raw_text and thread_context of a RawRecord instance.

        Returns a new RawRecord with cleaned content and a list of applied redactions.
        """
        clean_text, applied = self.sanitize(record.raw_text)

        cleaned_context = None
        if record.thread_context:
            cleaned_context = {}
            for k, v in record.thread_context.items():
                if isinstance(v, str):
                    c_val, extra_applied = self.sanitize(v)
                    cleaned_context[k] = c_val
                    applied.extend(extra_applied)
                else:
                    cleaned_context[k] = v

        sanitized_record = RawRecord(
            raw_id=record.raw_id,
            source_platform=record.source_platform,
            source_url=record.source_url,
            author_id_hash=record.author_id_hash,
            published_at=record.published_at,
            collected_at=record.collected_at,
            raw_text=clean_text,
            thread_context=cleaned_context,
            product_context=record.product_context,
        )
        return sanitized_record, list(set(applied))
