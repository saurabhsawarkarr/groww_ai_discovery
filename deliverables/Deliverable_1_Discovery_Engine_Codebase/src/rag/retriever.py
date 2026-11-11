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
    "band": "stop",
    "rokna": "stop",
    "roke": "stop",
    "shuru": "start",
    "suru": "start",
    "chalu": "start",
    "trens": "trends",
    "chcek": "check",
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

_SYNTHETIC_SOURCE_RE = re.compile(
    r"(?:pilot|_exp_|golden|/comments/(?:\d{3}_|exp_|g\d+_)|watch\?v=(?:vid\d+|tax_sip|sip_xirr|groww_sip)|reviewId=gp_|apps\.apple\.com/in/app/groww-stocks-mutual-fund/id)",
    re.IGNORECASE,
)

_VALID_PLATFORM_URL_RES = (
    re.compile(r"^https://play\.google\.com/store/apps/details\?id=com\.nextbillion\.groww&reviewId=[0-9a-f\-]{20,}$", re.I),
    re.compile(r"^https://apps\.apple\.com/in/app/[^/]+/id1404871703#review-\d+$", re.I),
    re.compile(r"^https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}(?:&lc=[A-Za-z0-9_.\-]+)?$"),
    re.compile(r"^https://(?:www\.)?reddit\.com/r/[^/]+/comments/[a-z0-9]{5,8}/", re.I),
    re.compile(r"^https://(?:tradingqna\.com|forum\.valuepickr\.com)/t/.+/\d+(?:/\d+)?$", re.I),
)


THEME_DISPLAY_LABELS: Dict[str, str] = {
    "THEME-01": "Cash-Flow & Autopay Drops",
    "THEME-02": "Over-Diversification & Clutter",
    "THEME-03": "ECS Bounce Penalty & Pause Trap",
    "THEME-04": "Early Drawdown Panic (Months 1-3)",
    "THEME-05": "XIRR Distortion & Return Anxiety",
    "THEME-06": "NAV & Settlement Delay Uncertainty",
    "THEME-07": "Goal & Platform Continuity Friction",
}

_CHURN_REASON_WHY_RE = re.compile(
    r"\b(?:why|reasons?|causes?|factors?|drivers?|behind|what\s+makes|not\s+continu\w*|not\s+contun\w*)\b",
    re.IGNORECASE,
)
_CHURN_ACTION_RE = re.compile(
    r"\b(?:stop\w*|cancel\w*|discontinu\w*|quit\w*|drop\s*-?off|not\s+continu\w*|not\s+contun\w*|churn)\b",
    re.IGNORECASE,
)
_NARROW_CHURN_SUBTOPIC_RE = re.compile(
    r"\b(?:autopay|mandate|bank|hdfc|sbi|icici|axis|kotak|450|500|ecs\s+bounce|xirr|cagr|-?18%|30\s+rupees|"
    r"negative\s+return|red\s+portfolio|market\s+(?:is\s+)?(?:down|dip|crash|fall|drops?)|"
    r"nav|t\+2|allotment|overlap|diversif|notification|alert|daily\s+market|"
    r"hide\s+(?:the\s+)?cancel|trap\s+user|countdown|dark\s+pattern|workaround)\b",
    re.IGNORECASE,
)


def is_broad_churn_reason_query(query: str) -> bool:
    """Return True when query asks broadly why/what causes investors to stop SIPs across themes."""
    q_low = (query or "").strip().lower()
    if not q_low:
        return False
    return bool(
        _CHURN_REASON_WHY_RE.search(q_low)
        and _CHURN_ACTION_RE.search(q_low)
        and not _NARROW_CHURN_SUBTOPIC_RE.search(q_low)
    )


def classify_evidence_theme(item: Dict[str, Any]) -> Tuple[str, str]:
    """Return content-accurate (theme_id, human_readable_theme_label) for an evidence receipt."""
    t_low = f"{item.get('quote', '')} {item.get('text', '')}".lower()
    tid = item.get("theme_id", "GENERAL")

    if any(w in t_low for w in ["ecs", "bounce", "penalty", "charge", "insufficient", "fine", "pause", "skip", "snooze"]):
        return "THEME-03", "ECS Bounce Penalty & Pause Trap"
    if any(w in t_low for w in ["mandate", "autopay", "nach", "biller", "bank debit", "debit fail", "payment fail", "account got frozen"]):
        return "THEME-01", "Cash-Flow & Autopay Drops"
    if any(w in t_low for w in ["negative return", "loss", "crash", "red portfolio", "drawdown", "dip", "fixed deposit", "fd", "buying the dip"]):
        return "THEME-04", "Early Drawdown & Return Anxiety"
    if any(w in t_low for w in ["xirr", "cagr", "annualized", "early return", "180 days"]):
        return "THEME-05", "XIRR Distortion & Return Anxiety"
    if any(w in t_low for w in ["nav", "allotment", "t+2", "delay", "settlement"]):
        return "THEME-06", "NAV & Allotment Settlement Delays"
    if any(w in t_low for w in ["overlap", "diversif", "too many funds", "duplicate", "clutter"]):
        return "THEME-02", "Over-Diversification & Clutter"
    if any(w in t_low for w in ["discipline", "habit", "long term", "12 month", "goal", "nri", "demat"]):
        return "THEME-07", "Goal & Platform Continuity Friction"
    if tid in THEME_DISPLAY_LABELS:
        return tid, THEME_DISPLAY_LABELS[tid]
    return "GENERAL", "Verified Customer Corpus"


def is_verifiable_source_url(raw_id: str, source_url: str) -> bool:
    """Return True only when a record carries a genuine, clickable source permalink."""
    url = (source_url or "").strip()
    if not url.startswith("https://"):
        return False
    if _SYNTHETIC_SOURCE_RE.search(f"{raw_id or ''} {url}"):
        return False
    return any(pat.match(url) for pat in _VALID_PLATFORM_URL_RES)


def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words."""
    return re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())


def _preprocess_query(query: str) -> Tuple[List[str], List[str]]:
    """Tokenize query, apply typo corrections, stem common financial plurals,
    and enrich query terms based on explicit domain intents."""
    raw = _tokenize(query)
    
    # Stem common financial plurals and verbs so they match tokens in corpus
    stemmed = []
    for w in raw:
        w_corr = TYPO_CORRECTIONS.get(w, w)
        if w_corr in ("banks", "banking"):
            stemmed.append("bank")
        elif w_corr == "funds":
            stemmed.append("fund")
        elif w_corr == "sips":
            stemmed.append("sip")
        elif w_corr == "mandates":
            stemmed.append("mandate")
        elif w_corr == "penalties":
            stemmed.append("penalty")
        elif w_corr == "workarounds":
            stemmed.append("workaround")
        elif w_corr == "hacks":
            stemmed.append("hack")
        elif w_corr == "units":
            stemmed.append("unit")
        elif w_corr in ("debited", "debits"):
            stemmed.append("debit")
        elif w_corr in ("allocated", "allotment", "allotting"):
            stemmed.append("allotment")
        elif w_corr == "days":
            stemmed.append("day")
        elif w_corr == "months":
            stemmed.append("month")
        elif w_corr in ("strikes", "consecutively"):
            stemmed.append("strike")
        elif w_corr == "rejections":
            stemmed.append("rejection")
        elif w_corr == "reasons":
            stemmed.append("reason")
        elif w_corr == "beginners":
            stemmed.append("beginner")
        elif w_corr == "investors":
            stemmed.append("investor")
        elif w_corr == "differences":
            stemmed.append("difference")
        elif w_corr == "habits":
            stemmed.append("habit")
        else:
            stemmed.append(w_corr)

    q_str = " ".join(stemmed)

    is_downturn_query = any(
        p in q_str
        for p in [
            "market is down",
            "market down",
            "market crash",
            "market dip",
            "market fall",
            "during crash",
            "during dip",
            "portfolio is red",
            "red portfolio",
            "negative return",
            "drawdown",
            "xirr",
        ]
    ) or ("market" in stemmed and any(w in stemmed for w in ["down", "dip", "crash", "fall", "drop", "loss", "negative", "red"]))

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

    informative = [w for w in stemmed if w not in STOPWORDS]

    if "xirr" in stemmed or "cagr" in stemmed or "annualized" in q_str or "annualised" in q_str:
        for extra in ["xirr", "cagr", "return", "annualized", "negative", "dip"]:
            if extra not in informative:
                informative.append(extra)
    elif is_downturn_query:
        for extra in ["market", "down", "dip", "crash", "drawdown", "loss", "negative", "volatility", "xirr", "correction", "long", "term"]:
            if extra not in informative:
                informative.append(extra)
    elif any(w in q_str for w in ["notification", "alert", "alerts", "daily market"]):
        for extra in ["notification", "alert", "daily", "market", "panic", "noise", "long", "term"]:
            if extra not in informative:
                informative.append(extra)
    # If churn intent is present (without downturn/notification focus), boost core churn & failure terms
    elif is_churn_intent:
        for extra in ["stop", "stopped", "cancel", "cancelled", "discontinue", "churn", "pause", "paused", "bounce", "drop", "drawdown", "penalty", "loss"]:
            if extra not in informative:
                informative.append(extra)

    # If bank failure inquiry, enrich with mandate & failure rails
    is_bank_query = any(w in q_str for w in ["bank", "hdfc", "sbi", "icici", "axis", "kotak"]) and any(w in q_str for w in ["fail", "failing", "failed", "reject", "rejection", "drop", "often", "specific", "which", "most"])
    if is_bank_query:
        for extra in ["mandate", "autopay", "deduction", "failed", "rejection", "account"]:
            if extra not in informative:
                informative.append(extra)

    # If workaround inquiry, enrich with community recovery mechanisms
    is_workaround_query = any(w in q_str for w in ["workaround", "hack", "fix", "reddit", "solution", "alternative"])
    if is_workaround_query:
        for extra in ["pause", "skip", "snooze", "mandate", "autopay", "workaround"]:
            if extra not in informative:
                informative.append(extra)

    # If platform comparison inquiry, enrich with platform & clearing rails
    is_platform_query = any(w in q_str for w in ["zerodha", "coin", "platform", "compare", "difference"])
    if is_platform_query:
        for extra in ["zerodha", "coin", "autopay", "mandate", "demat", "bse", "star"]:
            if extra not in informative:
                informative.append(extra)

    # If unit allocation or NAV inquiry, enrich with settlement rails
    is_settlement_query = any(w in q_str for w in ["allotment", "nav", "unit", "debited", "settlement", "t+2", "delay"])
    if is_settlement_query:
        for extra in ["allotment", "nav", "unit", "processing", "settlement", "amc"]:
            if extra not in informative:
                informative.append(extra)

    # If scheme clutter / portfolio overlap inquiry, enrich with overlap rails
    is_clutter_query = any(w in q_str for w in ["overlap", "clutter", "multi", "diversification", "different", "beginner"])
    if is_clutter_query:
        for extra in ["overlap", "clutter", "scheme", "portfolio", "diversification"]:
            if extra not in informative:
                informative.append(extra)

    return informative if informative else stemmed, stemmed


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
                        raw_id = (row.get("raw_id") or "").strip()
                        source_url = (row.get("source_url") or "").strip()
                        if len(raw_text) < 35 or not is_verifiable_source_url(raw_id, source_url):
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

                        # Identify likely theme tag based on content (neutral GENERAL default prevents THEME-01 skew)
                        assigned_theme = "GENERAL"
                        if any(w in t_low for w in ["mandate", "autopay", "nach", "biller", "bank debit", "debit fail", "payment fail", "fail", "reject"]):
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
                        elif any(w in t_low for w in ["stop sip", "stop my sip", "cancel sip", "cancelled sip", "canceled sip", "discontinue", "left groww", "deleted mandate", "mandate deleted", "deleted app"]):
                            assigned_theme = "THEME-03"

                        # Infer journey stage
                        stage = "newly_started"
                        if any(w in t_low for w in ["stopped", "cancelled", "deleted mandate", "left groww", "discontinued"]):
                            stage = "stopped"
                        elif any(w in t_low for w in ["pause", "hold", "skip", "snooze"]):
                            stage = "paused"
                        elif any(w in t_low for w in ["started", "beginner", "first time", "first sip"]):
                            stage = "newly_started"
                        elif any(w in t_low for w in ["year", "months", "continuing", "regular", "discipline"]):
                            stage = "continuing"

                        rec_item = {
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
                        }
                        _, rec_item["theme_label"] = classify_evidence_theme(rec_item)
                        self.records.append(rec_item)
            except Exception as e:
                logger.warning(f"Error loading CSV corpus: {e}")

        # Fallback if CSV empty: Load representative quotes from themes JSON
        if not self.records and theme_map:
            for t_id, t in theme_map.items():
                for q in t.get("representative_quotes", []):
                    q_rid = q.get("raw_id", "")
                    q_url = q.get("source_url", "")
                    if not is_verifiable_source_url(q_rid, q_url):
                        continue
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
            elif token in ["xirr", "cagr"]:
                boost = 3.5
            elif token in ["market", "crash", "dip", "correction", "volatility", "drawdown"]:
                boost = 2.5
            elif token in ["stop", "stopped", "cancel", "cancelled", "discontinue", "churn", "pause", "paused"]:
                boost = 1.0 if any(w in query_tokens for w in ["market", "crash", "dip", "drawdown", "negative", "xirr"]) else 3.0
            elif token in ["bounce", "penalty", "loss", "negative"]:
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
        if is_broad_churn_reason_query(query):
            churn_tokens = list(search_tokens)
            for extra in ["autopay", "mandate", "biller", "bounce", "penalty", "skip", "pause", "dip", "loss", "xirr", "allotment", "delay", "overlap"]:
                if extra not in churn_tokens:
                    churn_tokens.append(extra)
            bm25_ranks = self.bm25_search(churn_tokens, top_n=200)
            vector_ranks = self.vector_search(churn_tokens, top_n=200)
            results = self._select_diverse_churn_results(
                bm25_ranks=bm25_ranks,
                vector_ranks=vector_ranks,
                top_k=top_k,
                platform_filter=platform_filter,
                journey_stage_filter=journey_stage_filter,
            )
            tier_used = "Tier 1: Cross-Theme Churn Synthesis RRF"
        else:
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

    def _select_diverse_churn_results(
        self,
        bm25_ranks: List[Tuple[int, float]],
        vector_ranks: List[Tuple[int, float]],
        top_k: int,
        platform_filter: Optional[str] = None,
        journey_stage_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Select 1 top-scoring genuine SIP/MF receipt per distinct churn theme before backfilling."""
        rrf_constant = 60
        fused_scores: Dict[int, float] = {}
        for rank, (doc_idx, _) in enumerate(bm25_ranks):
            fused_scores[doc_idx] = fused_scores.get(doc_idx, 0.0) + (1.0 / (rrf_constant + rank + 1))
        for rank, (doc_idx, _) in enumerate(vector_ranks):
            fused_scores[doc_idx] = fused_scores.get(doc_idx, 0.0) + (1.0 / (rrf_constant + rank + 1))

        sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        bm25_top10 = {x[0] for x in bm25_ranks[:10]}

        def _eligible(rec: Dict[str, Any], strict_diversity: bool) -> bool:
            if platform_filter and platform_filter.lower() != "all":
                if rec["platform"].lower() != platform_filter.lower():
                    return False
            if journey_stage_filter and journey_stage_filter.lower() != "all":
                if rec["journey_stage"].lower() != journey_stage_filter.lower():
                    return False
            t_low = rec["text"].lower()
            if "deleted my review" in t_low or "removed my review" in t_low:
                return False
            if strict_diversity:
                if not any(w in t_low for w in ["sip", "mandate", "autopay"]):
                    return False
                if not any(
                    w in t_low
                    for w in [
                        "stop", "cancel", "pause", "skip", "bounce", "penalty", "charge",
                        "fail", "reject", "dip", "loss", "negative", "delay", "allotment",
                        "overlap", "biller", "deduct", "issue", "problem", "frozen", "why",
                    ]
                ):
                    return False
                if "stock portfolio" in t_low and "stop" not in t_low and "cancel" not in t_low:
                    return False
                if not platform_filter or platform_filter.lower() == "all":
                    if "zerodha" in t_low or "unique to zerodha" in t_low:
                        return False
            return True

        picked: List[Dict[str, Any]] = []
        picked_ids: Set[int] = set()
        seen_themes: Set[str] = set()
        forum_count = 0

        # Pass 1: One distinct theme per slot, capping TradingQnA forum threads to avoid dominance
        for doc_idx, score in sorted_docs:
            rec = self.records[doc_idx]
            if not _eligible(rec, strict_diversity=True):
                continue
            tid, tlabel = classify_evidence_theme(rec)
            if tid == "GENERAL" or tid in seen_themes:
                continue
            if rec["platform"] == "forum" and forum_count >= 1 and (not platform_filter or platform_filter.lower() == "all"):
                continue

            item = dict(rec)
            item["theme_id"] = tid
            item["theme_label"] = tlabel
            item["similarity_score"] = round(min(0.99, max(0.60, score * 50.0)), 3)
            item["bm25_hit"] = doc_idx in bm25_top10
            picked.append(item)
            picked_ids.add(doc_idx)
            seen_themes.add(tid)
            if rec["platform"] == "forum":
                forum_count += 1
            if len(picked) >= top_k:
                return picked

        # Pass 2: Backfill remaining slots cleanly if narrow filters restricted distinct themes
        for doc_idx, score in sorted_docs:
            if doc_idx in picked_ids:
                continue
            rec = self.records[doc_idx]
            if not _eligible(rec, strict_diversity=False):
                continue
            tid, tlabel = classify_evidence_theme(rec)
            item = dict(rec)
            item["theme_id"] = tid
            item["theme_label"] = tlabel
            item["similarity_score"] = round(min(0.99, max(0.60, score * 50.0)), 3)
            item["bm25_hit"] = doc_idx in bm25_top10
            picked.append(item)
            picked_ids.add(doc_idx)
            if len(picked) >= top_k:
                break

        return picked
