"""Deduplication module combining exact SHA-256 hashing and near-duplicate MinHash/Jaccard filtering.

Identifies syndicated bot reviews, reposted forum discussions, and multi-platform
cross-posts to maintain dataset uniqueness and prevent sample distortion.
"""

import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src.connectors.base import RawRecord

logger = logging.getLogger("groww_discovery.preprocessing.deduplicator")


def get_char_ngrams(text: str, n: int = 3) -> Set[str]:
    """Generate a set of character n-grams from normalized text."""
    clean = re.sub(r"\s+", " ", text.lower().strip())
    if len(clean) < n:
        return {clean} if clean else set()
    return {clean[i : i + n] for i in range(len(clean) - n + 1)}


def calculate_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection_len = len(set_a.intersection(set_b))
    union_len = len(set_a.union(set_b))
    if union_len == 0:
        return 0.0
    return intersection_len / union_len


class Deduplicator:
    """Two-tier deduplicator for exact and near-duplicate text detection."""

    def __init__(self, near_duplicate_threshold: float = 0.85, ngram_size: int = 3):
        self.threshold = near_duplicate_threshold
        self.ngram_size = ngram_size

        # Exact hash mapping: sha256_hash -> original_raw_id
        self._exact_hash_map: Dict[str, str] = {}

        # Near duplicate inverted index: min-shingle -> list of record_ids
        self._shingle_index_map: Dict[str, List[str]] = {}
        self._cand_store: Dict[str, Tuple[Set[str], int]] = {}

        # Counter metrics
        self.exact_duplicates_count = 0
        self.near_duplicates_count = 0

    def reset(self) -> None:
        """Clear all deduplication caches and reset counters."""
        self._exact_hash_map.clear()
        self._shingle_index_map.clear()
        self._cand_store.clear()
        self.exact_duplicates_count = 0
        self.near_duplicates_count = 0

    @staticmethod
    def normalize_for_hash(text: str) -> str:
        """Standardize text for exact hash comparison."""
        # Lowercase, remove non-alphanumeric except spaces, collapse whitespace
        text_clean = text.lower()
        text_clean = re.sub(r"[^\w\s]", "", text_clean)
        return " ".join(text_clean.split())

    def check_duplicate(self, text: str, record_id: str) -> Tuple[bool, Optional[str], Optional[str], float]:
        """Check whether a text string is an exact or near duplicate of previously seen items.

        Returns:
            Tuple of (is_duplicate: bool, duplicate_type: Optional[str], matched_id: Optional[str], similarity: float)
            duplicate_type is either 'exact', 'near', or None.
        """
        norm_text = self.normalize_for_hash(text)
        if not norm_text:
            return False, None, None, 0.0

        # Tier 1: Exact Hash Deduplication (SHA-256)
        text_hash = hashlib.sha256(norm_text.encode("utf-8")).hexdigest()
        if text_hash in self._exact_hash_map:
            original_id = self._exact_hash_map[text_hash]
            self.exact_duplicates_count += 1
            logger.debug("Exact duplicate detected: %s matches %s", record_id, original_id)
            return True, "exact", original_id, 1.0

        # Tier 2: Near-Duplicate Detection (Inverted Prefix Shingle Indexing)
        ngrams = get_char_ngrams(norm_text, self.ngram_size)
        ngram_len = len(ngrams)

        if ngram_len >= 8:
            sorted_sample = sorted(ngrams)[:4]
            candidate_ids: Set[str] = set()
            for s in sorted_sample:
                if s in self._shingle_index_map:
                    candidate_ids.update(self._shingle_index_map[s])

            for cand_id in candidate_ids:
                cand_ngrams, cand_len = self._cand_store[cand_id]
                ratio = min(ngram_len, cand_len) / max(ngram_len, cand_len)
                if ratio < self.threshold:
                    continue
                inter_len = len(ngrams.intersection(cand_ngrams))
                union_len = ngram_len + cand_len - inter_len
                if union_len > 0:
                    sim = inter_len / union_len
                    if sim >= self.threshold:
                        self.near_duplicates_count += 1
                        logger.debug(
                            "Near duplicate detected: %s matches %s with similarity %.3f >= %.2f",
                            record_id, cand_id, sim, self.threshold
                        )
                        return True, "near", cand_id, round(sim, 3)

            # Not a near-duplicate -> register in candidate store and index
            self._cand_store[record_id] = (ngrams, ngram_len)
            for s in sorted_sample:
                if s not in self._shingle_index_map:
                    self._shingle_index_map[s] = []
                self._shingle_index_map[s].append(record_id)

        self._exact_hash_map[text_hash] = record_id
        return False, None, None, 0.0

    def filter_records(
        self, records: List[RawRecord]
    ) -> Tuple[List[RawRecord], List[Dict[str, Any]]]:
        """Process a list of RawRecord objects, returning unique records and drop logs.

        Args:
            records: Ingested raw records.

        Returns:
            Tuple of (kept_records, dropped_duplicate_records_metadata)
        """
        kept: List[RawRecord] = []
        dropped: List[Dict[str, Any]] = []

        for record in records:
            is_dup, dup_type, match_id, sim = self.check_duplicate(
                record.raw_text, record.raw_id
            )
            if is_dup:
                dropped.append({
                    "raw_id": record.raw_id,
                    "duplicate_type": dup_type,
                    "matched_id": match_id,
                    "similarity": round(sim, 3),
                    "reason": f"{dup_type.capitalize()} duplicate of {match_id} (sim: {round(sim, 3)})",
                })
            else:
                kept.append(record)

        logger.info(
            "Deduplication completed: %d kept, %d exact dropped, %d near dropped",
            len(kept), self.exact_duplicates_count, self.near_duplicates_count
        )
        return kept, dropped
