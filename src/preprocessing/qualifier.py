"""Relevance classification and domain filtering module.

Identifies discussions pertinent to first-time mutual fund SIP continuation,
rejecting off-topic conversations (e.g. F&O trading, US stocks, crypto, noise)
and logging each exclusion with a structured reason for auditability.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from src.connectors.base import RawRecord

logger = logging.getLogger("groww_discovery.preprocessing.qualifier")

DEFAULT_RELEVANT_KEYWORDS = [
    "sip",
    "sips",
    "mutual fund",
    "mutual funds",
    "mutualfund",
    "mutualfunds",
    "nav",
    "xirr",
    "cagr",
    "autopay",
    "mandate",
    "e-mandate",
    "emandate",
    "nach",
    "step up",
    "step-up",
    "folio",
    "amc",
    "elss",
    "index fund",
    "index funds",
    "flexi cap",
    "flexicap",
    "small cap",
    "smallcap",
    "mid cap",
    "midcap",
    "large cap",
    "largecap",
    "debt fund",
    "equity fund",
    "rupee cost averaging",
    "parag parikh",
    "quant mutual",
    "uti nifty",
    "mirae asset",
    "nippon india",
    "instalment",
    "installment",
]

DEFAULT_EXCLUSION_KEYWORDS = [
    "f&o",
    "f and o",
    "call option",
    "put option",
    "intraday",
    "future",
    "futures",
    "us stocks",
    "nasdaq",
    "crypto",
    "bitcoin",
    "bse index option",
    "margin trading",
    "scalping",
    "expiry",
    "strike price",
    "forex",
    "binary option",
    "ipo allotment",
    "ipo application",
    "jio platform ipo",
    "brokerage charges",
    "wallet withdrawal",
    "remove money in wallet",
]


class RelevanceClassifier:
    """Classifies raw investor conversations as relevant or excluded."""

    def __init__(
        self,
        relevant_keywords: Optional[List[str]] = None,
        exclusion_keywords: Optional[List[str]] = None,
        min_word_count: int = 4,
    ):
        self.relevant_keywords = relevant_keywords or DEFAULT_RELEVANT_KEYWORDS
        self.exclusion_keywords = exclusion_keywords or DEFAULT_EXCLUSION_KEYWORDS
        self.min_word_count = min_word_count

        # Build regex word-boundary patterns for keywords
        self._exclusion_patterns = [
            (k, re.compile(r"(?:\b|_)" + re.escape(k) + r"(?:\b|_)", re.IGNORECASE))
            for k in self.exclusion_keywords
        ]
        self._relevant_patterns = [
            (k, re.compile(r"(?:\b|_)" + re.escape(k) + r"(?:\b|_)", re.IGNORECASE))
            for k in self.relevant_keywords
        ]

    def qualify_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """Evaluate raw commentary text for mutual fund SIP research relevance.

        Args:
            text: Input text string.

        Returns:
            Tuple of (is_qualified: bool, exclusion_reason: Optional[str])
        """
        if not text or not text.strip():
            return False, "Empty or whitespace-only text"

        clean_text = text.strip()
        words = clean_text.split()
        if len(words) < self.min_word_count:
            return False, f"Insufficient context (< {self.min_word_count} words)"

        # Check for explicit exclusion criteria (F&O, US stocks, crypto, etc.)
        for keyword, pattern in self._exclusion_patterns:
            if pattern.search(clean_text):
                return False, f"Irrelevant domain: contains '{keyword}'"

        # Check for presence of at least one relevant mutual fund / SIP term
        has_relevant = any(pattern.search(clean_text) for _, pattern in self._relevant_patterns)
        if not has_relevant:
            return False, "No SIP/Mutual Fund terminology detected"

        return True, None

    def qualify_record(self, record: RawRecord) -> Tuple[bool, Optional[str]]:
        """Qualify a RawRecord based on raw_text and thread_context."""
        # Include parent title in relevance check if available
        combined_text = record.raw_text
        if record.thread_context and "parent_title" in record.thread_context:
            parent_title = record.thread_context["parent_title"]
            if parent_title:
                combined_text = f"{parent_title} {combined_text}"

        return self.qualify_text(combined_text)

    def batch_qualify(
        self, records: List[RawRecord]
    ) -> Tuple[List[RawRecord], List[Tuple[RawRecord, str]]]:
        """Split a list of records into qualified items and excluded items with reasons.

        Returns:
            Tuple of (qualified_records, excluded_records_with_reasons)
        """
        qualified: List[RawRecord] = []
        excluded: List[Tuple[RawRecord, str]] = []

        for record in records:
            is_valid, reason = self.qualify_record(record)
            if is_valid:
                qualified.append(record)
            else:
                excluded.append((record, reason or "Unspecified qualification rejection"))

        logger.info(
            "Qualification completed: %d qualified, %d excluded",
            len(qualified), len(excluded)
        )
        return qualified, excluded
