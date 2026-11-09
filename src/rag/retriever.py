"""Hybrid BM25 + Semantic Vector Evidence Retriever with Multi-Stage Fallback.

Indexes the 3,052 verified mutual fund & SIP customer discourse records
and retrieves top-K verbatim customer evidence chunks using Reciprocal Rank Fusion (RRF).

Includes:
- Intelligent stopword filtering and domain typo correction (e.g. contuning -> continuing).
- Churn intent expansion (not continuing / stop / cancel / drop).
- Strict corpus noise cleaning (filters [removed], [deleted], and off-topic stock trading rants).
- Multi-Stage Fallback Architecture (Direct RRF -> Synonym Expansion -> Thematic Centroids).
"""

import csv
import json
import logging
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

logger = logging.getLogger("groww_discovery.rag.retriever")

# Low-signal stopwords that should not dominate search scoring
STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "of", "to", "in", "for", "with", "on", "at", "by", "from",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "their", "there", "they", "them", "these", "those", "this", "that", "it", "its",
    "what", "which", "who", "whom", "whose", "why", "how", "when", "where",
    "people", "user", "users", "app", "apps", "groww", "show", "shows", "trading"
}

# Domain typo corrections for common search queries
TYPO_CORRECTIONS: Dict[str, str] = {
    "contuning": "continuing",
    "continuning": "continuing",
    "canceling": "cancelling",
    "cancelation": "cancellation",
    "withdrawl": "withdrawal",
    "drawdow": "drawdown",
    "retun": "return",
    "retuns": "returns",
    "mandat": "mandate",
    "autopaye": "autopay",
}

# Domain synonym expansion map for financial & customer discourse
QUERY_SYNONYMS: Dict[str, List[str]] = {
    "autopay": ["mandate", "e-mandate", "nach", "bank debit", "auto debit", "deduction"],
    "mandate": ["autopay", "e-mandate", "nach", "standing instruction", "authorization"],
    "fail": ["reject", "failed", "failure", "bounce", "drop", "declined", "error"],
    "failed": ["reject", "failure", "bounce", "drop", "declined", "error"],
    "failure": ["reject", "failed", "bounce", "drop", "declined"],
    "bounce": ["ecs", "penalty", "insufficient", "fine", "dishonour", "charge"],
    "ecs": ["bounce", "penalty", "charge", "insufficient", "fine"],
    "penalty": ["charge", "fine", "bounce", "ecs", "fee", "450"],
    "overlap": ["diversif", "too many funds", "duplicate", "clutter", "redundant"],
    "diversification": ["overlap", "portfolio", "many funds", "clutter"],
    "xirr": ["cagr", "annualized", "return calculation", "paper loss", "short term"],
    "cagr": ["xirr", "annualized", "return", "growth", "percentage"],
    "drawdown": ["loss", "negative", "red", "crash", "dip", "fall", "correction"],
    "loss": ["drawdown", "negative", "red", "crash", "dip", "paper loss"],
    "negative": ["loss", "red", "drawdown", "dip", "minus"],
    "red": ["negative", "loss", "drawdown", "crash", "dip"],
    "fd": ["fixed deposit", "guarantee", "safe", "linear", "interest"],
    "nav": ["allotment", "t+2", "delay", "processing", "settlement", "cut-off"],
    "delay": ["processing", "t+2", "pending", "slow", "allotment", "settlement"],
    "settlement": ["nav", "t+2", "allotment", "processing", "demat"],
    "pause": ["skip", "snooze", "temporary", "hold", "resume"],
    "snooze": ["pause", "skip", "temporary", "hold"],
    "cancel": ["stop", "delete", "withdraw", "exit", "close", "discontinue"],
    "cancellation": ["stop", "delete", "cancel", "churn", "exit", "discontinue"],
    "npci": ["mandate", "limit", "1 lakh", "authorization", "ceiling"],
    "continue": ["habit", "discipline", "long term", "12 month", "continuer", "wealth"],
    "continuing": ["habit", "discipline", "long term", "12 month", "continuer"],
    "continuer": ["continue", "habit", "discipline", "long term", "12 month"],
}

THEME_KEYWORDS: Dict[str, List[str]] = {
    "THEME-01": ["mandate", "autopay", "bank", "debit", "bounce", "fail", "npci", "silent", "dropped"],
    "THEME-02": ["overlap", "diversif", "too many", "funds", "portfolio", "duplicate", "clutter"],
    "THEME-03": ["ecs", "penalty", "charge", "insufficient", "fine", "bounce", "cashflow", "450", "pause", "snooze"],
    "THEME-04": ["xirr", "cagr", "annualized", "early", "month 1", "month 2", "month 3", "paper loss"],
    "THEME-05": ["fixed deposit", "fd", "crash", "negative return", "red portfolio", "volatility", "panic", "drawdown", "loss"],
    "THEME-06": ["nav", "t+2", "allotment", "delay", "processing", "settlement", "timing", "pending"],
    "THEME-07": ["continuer", "habit", "discipline", "long term", "12 month", "goal", "wealth"],
}

# Regex to identify genuine mutual fund and SIP conversations
MF_SIP_PATTERN = re.compile(
    r"\b(sips?|mutual\s+funds?|mandates?|autopay|nav|xirr|cagr|folio|instalments?|amc|demat|portfolio|redemption|units)\b",
    re.IGNORECASE,
)


def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words."""
    return re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())


def _preprocess_query(query: str) -> Tuple[List[str], List[str]]:
    """Tokenize query, apply typo corrections, and separate informative terms from stopwords."""
    raw = _tokenize(query)
    corrected = [TYPO_CORRECTIONS.get(w, w) for w in raw]
    q_str = " ".join(corrected)

    # Check for churn / discontinuation intent
    is_churn_intent = any(
        p in q_str
        for p in [
            "not continuing",
            "not continue",
            "stop",
            "cancel",
            "discontinue",
            "quit",
            "churn",
            "drop out",
            "why leave",
            "why people stop",
            "why stop",
            "why cancel",
        ]
    )

    informative = [w for w in corrected if w not in STOPWORDS]

    # If churn intent is present, boost core churn & failure terms
    if is_churn_intent:
        for extra in ["stop", "stopped", "cancel", "cancelled", "discontinue", "churn", "pause", "paused", "bounce", "drop", "drawdown", "penalty", "loss"]:
            if extra not in informative:
                informative.append(extra)

    return informative if informative else corrected, corrected


class HybridEvidenceRetriever:
    """Production-grade hybrid retriever combining BM25 lexical search and TF-IDF cosine similarity
    with noise filtering and multi-tier fallback resilience.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.data_dir = data_dir or (self.project_root / "data")
        self.records: List[Dict[str, Any]] = []
        self.doc_tokens: List[List[str]] = []
        self.inverted_index: Dict[str, List[Tuple[int, int]]] = {}  # term -> [(doc_idx, tf)]
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.idf: Dict[str, float] = {}
        self.k1 = 1.5
        self.b = 0.75

        # Semantic TF-IDF vectors
        self.vocab: Dict[str, int] = {}
        self.tfidf_vectors: List[Dict[int, float]] = []
        self.tfidf_norms: List[float] = []

        # Theme centroid cache
        self.theme_centroids: Dict[str, List[int]] = {}

        # Last retrieval metadata for debugging & fallback auditing
        self.last_retrieval_meta: Dict[str, Any] = {}

        self._load_corpus()
        self._build_indexes()

    def _load_corpus(self) -> None:
        """Load the 3,052 conversation corpus from CSV with noise filtering and thematic JSON."""
        csv_path = self.data_dir / "processed" / "cleaned_3k_sip_conversations.csv"
        themes_path = self.data_dir / "processed" / "major_themes_3k_discovery.json"

        theme_map = {}
        if themes_path.exists():
            try:
                with open(themes_path, "r", encoding="utf-8") as f:
                    themes_info = json.load(f).get("themes", [])
                    for t in themes_info:
                        theme_map[t["theme_id"]] = t
            except Exception as e:
                logger.warning(f"Could not load themes info: {e}")

        if csv_path.exists():
            try:
                with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        raw_text = row.get("cleaned_investor_text", "").strip()
                        if len(raw_text) < 35:
                            continue

                        # Clean noise: strip trailing [removed] / [deleted]
                        clean_text = raw_text.replace("\n[removed]", "").replace("[removed]", "").replace("\n[deleted]", "").replace("[deleted]", "").strip()
                        if len(clean_text) < 35:
                            continue

                        # Filter out off-topic stock trading rants that have zero mutual fund / SIP relevance
                        t_low = clean_text.lower()
                        if any(k in t_low for k in ["doesn't even show positions", "buy and sell stocks", "intraday positions", "f&o option"]):
                            if not MF_SIP_PATTERN.search(clean_text):
                                continue

                        # Identify likely theme tag based on content
                        assigned_theme = "THEME-01"
                        if any(w in t_low for w in ["mandate", "autopay", "bank debit", "fail", "reject"]):
                            assigned_theme = "THEME-01"
                        elif any(w in t_low for w in ["overlap", "diversif", "too many funds", "duplicate", "portfolio"]):
                            assigned_theme = "THEME-02"
                        elif any(w in t_low for w in ["ecs", "penalty", "charge", "insufficient", "fine", "pause", "snooze"]):
                            assigned_theme = "THEME-03"
                        elif any(w in t_low for w in ["xirr", "cagr", "annualized", "early return", "180 days"]):
                            assigned_theme = "THEME-04"
                        elif any(w in t_low for w in ["negative return", "loss", "crash", "red portfolio", "drawdown", "volatility", "dip", "fixed deposit", "fd"]):
                            assigned_theme = "THEME-05"
                        elif any(w in t_low for w in ["nav", "allotment", "t+2", "delay", "timing", "settlement"]):
                            assigned_theme = "THEME-06"
                        elif any(w in t_low for w in ["continue", "discipline", "habit", "long term", "5 year", "10 year", "12 month"]):
                            assigned_theme = "THEME-07"
                        elif any(w in t_low for w in ["stop", "cancel", "discontinue", "left groww", "deleted"]):
                            assigned_theme = "THEME-03"

                        # Infer journey stage
                        stage = "newly_started"
                        if any(w in t_low for w in ["stopped", "cancelled", "deleted", "left groww", "discontinued"]):
                            stage = "stopped"
                        elif any(w in t_low for w in ["pause", "hold", "skip", "snooze"]):
                            stage = "paused"
                        elif any(w in t_low for w in ["started", "beginner", "first time", "first sip"]):
                            stage = "newly_started"
                        elif any(w in t_low for w in ["year", "months", "continuing", "regular", "discipline"]):
                            stage = "continuing"

                        self.records.append({
                            "doc_id": row.get("raw_id") or f"doc_{len(self.records)+1}",
                            "platform": row.get("platform", "unknown"),
                            "source_url": row.get("source_url", ""),
                            "published_at": row.get("published_at", "")[:10] if row.get("published_at") else "Recent",
                            "text": clean_text,
                            "quote": clean_text[:240] + ("..." if len(clean_text) > 240 else ""),
                            "full_text": clean_text,
                            "theme_id": assigned_theme,
                            "journey_stage": stage,
                            "author_hash": row.get("raw_id", "")[:12],
                        })
            except Exception as e:
                logger.warning(f"Error loading CSV corpus: {e}")

        # Fallback if CSV empty: Load representative quotes from themes JSON
        if not self.records and theme_map:
            for t_id, t in theme_map.items():
                for q in t.get("representative_quotes", []):
                    self.records.append({
                        "doc_id": q.get("raw_id", f"quote_{len(self.records)+1}"),
                        "platform": q.get("platform", "forum"),
                        "source_url": q.get("source_url", ""),
                        "published_at": q.get("published_date", "2026-03-14"),
                        "text": q.get("quote", ""),
                        "quote": q.get("quote", ""),
                        "full_text": q.get("quote", ""),
                        "theme_id": t_id,
                        "journey_stage": "newly_started",
                        "author_hash": q.get("raw_id", "")[:12],
                    })

    def _build_indexes(self) -> None:
        """Build BM25 inverted index and TF-IDF vector matrix."""
        if not self.records:
            return

        n_docs = len(self.records)
        df: Dict[str, int] = {}

        # 1. Tokenize all documents and record theme indices
        for doc_idx, doc in enumerate(self.records):
            searchable_content = f"{doc['text']} {doc['platform']} {doc['journey_stage']} {doc['theme_id']}"
            tokens = _tokenize(searchable_content)
            self.doc_tokens.append(tokens)
            self.doc_lengths.append(len(tokens))

            # Count document frequencies
            unique_tokens = set(tokens)
            for t in unique_tokens:
                df[t] = df.get(t, 0) + 1

            # Populate theme centroids
            tid = doc.get("theme_id", "THEME-01")
            if tid not in self.theme_centroids:
                self.theme_centroids[tid] = []
            self.theme_centroids[tid].append(doc_idx)

        self.avg_doc_len = sum(self.doc_lengths) / max(1, n_docs)

        # 2. Build vocabulary and IDF
        for idx, (term, freq) in enumerate(sorted(df.items())):
            # BM25 probabilistic IDF with smoothing
            self.idf[term] = math.log((n_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            self.vocab[term] = idx

        # 3. Build inverted index for BM25
        for doc_idx, tokens in enumerate(self.doc_tokens):
            term_counts: Dict[str, int] = {}
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1

            for term, count in term_counts.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append((doc_idx, count))

            # 4. Build normalized TF-IDF vector for cosine similarity
            vec: Dict[int, float] = {}
            norm_sq = 0.0
            doc_len = max(1, len(tokens))
            for term, count in term_counts.items():
                if term in self.vocab:
                    term_id = self.vocab[term]
                    weight = (count / doc_len) * self.idf[term]
                    vec[term_id] = weight
                    norm_sq += weight * weight
            self.tfidf_vectors.append(vec)
            self.tfidf_norms.append(math.sqrt(norm_sq) if norm_sq > 0 else 1.0)

    def bm25_search(self, query_tokens: List[str], top_n: int = 50) -> List[Tuple[int, float]]:
        """Score all matching documents using Okapi BM25 with term relevance boosting."""
        scores: Dict[int, float] = {}
        for token in query_tokens:
            if token not in self.inverted_index:
                continue
            idf_val = self.idf[token]

            # Boost high-signal financial and churn terms
            boost = 1.0
            if token in ["sip", "sips", "mutual", "mandate", "autopay"]:
                boost = 2.5
            elif token in ["stop", "stopped", "cancel", "cancelled", "discontinue", "churn", "pause", "paused"]:
                boost = 3.0
            elif token in ["bounce", "penalty", "loss", "drawdown", "negative"]:
                boost = 2.0

            for doc_idx, tf in self.inverted_index[token]:
                doc_len = self.doc_lengths[doc_idx]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                term_score = boost * idf_val * (numerator / max(0.001, denominator))
                scores[doc_idx] = scores.get(doc_idx, 0.0) + term_score

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_n]

    def vector_search(self, query_tokens: List[str], top_n: int = 50) -> List[Tuple[int, float]]:
        """Score documents using TF-IDF cosine similarity."""
        query_vec: Dict[int, float] = {}
        q_norm_sq = 0.0
        q_len = max(1, len(query_tokens))
        for token in query_tokens:
            if token in self.vocab and token in self.idf:
                term_id = self.vocab[token]
                weight = (1.0 / q_len) * self.idf[token]
                query_vec[term_id] = query_vec.get(term_id, 0.0) + weight
                q_norm_sq += weight * weight

        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0
        if not query_vec:
            return []

        scores: Dict[int, float] = {}
        for term_id, q_weight in query_vec.items():
            for doc_idx, doc_vec in enumerate(self.tfidf_vectors):
                if term_id in doc_vec:
                    dot = q_weight * doc_vec[term_id]
                    scores[doc_idx] = scores.get(doc_idx, 0.0) + dot

        cos_scores = []
        for doc_idx, dot_val in scores.items():
            sim = dot_val / (q_norm * self.tfidf_norms[doc_idx])
            cos_scores.append((doc_idx, sim))

        cos_scores.sort(key=lambda x: x[1], reverse=True)
        return cos_scores[:top_n]

    def _expand_tokens(self, tokens: List[str]) -> Tuple[List[str], List[str]]:
        """Expand tokens using the domain synonym vocabulary."""
        expanded = list(tokens)
        added_synonyms = []
        for tok in tokens:
            if tok in QUERY_SYNONYMS:
                for syn in QUERY_SYNONYMS[tok]:
                    for s_tok in _tokenize(syn):
                        if s_tok not in expanded:
                            expanded.append(s_tok)
                            added_synonyms.append(s_tok)
        return expanded, added_synonyms

    def _detect_nearest_theme(self, tokens: List[str]) -> str:
        """Identify the closest thematic cluster for token set."""
        theme_scores: Dict[str, int] = {k: 0 for k in THEME_KEYWORDS}
        for tok in tokens:
            for theme_id, kw_list in THEME_KEYWORDS.items():
                for kw in kw_list:
                    if tok in kw or kw in tok:
                        theme_scores[theme_id] += 1
        best_theme = max(theme_scores.items(), key=lambda x: x[1])
        return best_theme[0] if best_theme[1] > 0 else "THEME-01"

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        platform_filter: Optional[str] = None,
        journey_stage_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Execute hybrid search using Reciprocal Rank Fusion (RRF) with noise filtering and multi-stage fallback."""
        if not self.records:
            return []

        informative_tokens, all_tokens = _preprocess_query(query)
        search_tokens = informative_tokens if informative_tokens else all_tokens

        if not search_tokens:
            self.last_retrieval_meta = {"fallback_tier": "None", "is_fallback": False, "matches_found": 0}
            return []

        # =====================================================================
        # TIER 1: Direct Hybrid Search with Informative Tokens
        # =====================================================================
        bm25_ranks = self.bm25_search(search_tokens, top_n=60)
        vector_ranks = self.vector_search(search_tokens, top_n=60)
        results = self._rank_and_filter(
            bm25_ranks=bm25_ranks,
            vector_ranks=vector_ranks,
            top_k=top_k,
            platform_filter=platform_filter,
            journey_stage_filter=journey_stage_filter,
        )

        tier_used = "Tier 1: Direct Hybrid RRF"
        is_fallback = False
        expanded_terms: List[str] = []

        # =====================================================================
        # TIER 2: Synonym Query Expansion Fallback (if results < top_k)
        # =====================================================================
        if len(results) < top_k:
            expanded_tokens, added = self._expand_tokens(search_tokens)
            if added:
                exp_bm25 = self.bm25_search(expanded_tokens, top_n=60)
                exp_vector = self.vector_search(expanded_tokens, top_n=60)
                expanded_results = self._rank_and_filter(
                    bm25_ranks=exp_bm25,
                    vector_ranks=exp_vector,
                    top_k=top_k,
                    platform_filter=platform_filter,
                    journey_stage_filter=journey_stage_filter,
                )
                if len(expanded_results) > len(results):
                    results = expanded_results
                    tier_used = "Tier 2: Synonym Query Expansion Fallback"
                    is_fallback = True
                    expanded_terms = added

        # =====================================================================
        # TIER 3: Thematic Cluster Centroid Fallback (if still 0 matches)
        # =====================================================================
        if len(results) == 0:
            nearest_theme = self._detect_nearest_theme(search_tokens)
            doc_indices = self.theme_centroids.get(nearest_theme, [])[:top_k]
            results = []
            for d_idx in doc_indices:
                rec = dict(self.records[d_idx])
                rec["similarity_score"] = 0.65
                rec["bm25_hit"] = False
                rec["thematic_fallback"] = True
                results.append(rec)
            tier_used = f"Tier 3: Thematic Centroid Fallback ({nearest_theme})"
            is_fallback = True

        # Store metadata for introspection
        self.last_retrieval_meta = {
            "query": query,
            "tokens": search_tokens,
            "fallback_tier": tier_used,
            "is_fallback": is_fallback,
            "expanded_terms": expanded_terms,
            "matches_found": len(results),
        }

        return results

    def _rank_and_filter(
        self,
        bm25_ranks: List[Tuple[int, float]],
        vector_ranks: List[Tuple[int, float]],
        top_k: int,
        platform_filter: Optional[str] = None,
        journey_stage_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform Reciprocal Rank Fusion (RRF) and apply metadata filters."""
        rrf_constant = 60
        fused_scores: Dict[int, float] = {}

        for rank, (doc_idx, _) in enumerate(bm25_ranks):
            fused_scores[doc_idx] = fused_scores.get(doc_idx, 0.0) + (1.0 / (rrf_constant + rank + 1))

        for rank, (doc_idx, _) in enumerate(vector_ranks):
            fused_scores[doc_idx] = fused_scores.get(doc_idx, 0.0) + (1.0 / (rrf_constant + rank + 1))

        sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        results = []

        for doc_idx, score in sorted_docs:
            rec = self.records[doc_idx]

            # Apply platform filter
            if platform_filter and platform_filter.lower() != "all":
                if rec["platform"].lower() != platform_filter.lower():
                    continue

            # Apply journey stage filter
            if journey_stage_filter and journey_stage_filter.lower() != "all":
                if rec["journey_stage"].lower() != journey_stage_filter.lower():
                    continue

            # Normalize RRF score to 0.60 - 0.99 range
            norm_score = min(0.99, max(0.60, score * 50.0))

            result_item = dict(rec)
            result_item["similarity_score"] = round(norm_score, 3)
            result_item["bm25_hit"] = doc_idx in [x[0] for x in bm25_ranks[:10]]
            results.append(result_item)

            if len(results) >= top_k:
                break

        return results
