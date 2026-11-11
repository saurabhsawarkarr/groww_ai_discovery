"""Stage 1 Pre-LLM Fast Guardrails and Clarification Engine.

Executes ultra-fast (< 5ms, 0 Tokens) pre-retrieval evaluations:
1. Advisory Trap Detection (SEBI Non-Advice Invariant) -> Tier 1 Regulatory Refusal.
2. Dark Pattern & FOMO Trap Detection -> Tier 1 Ethical Growth Refusal.
3. Out-of-Scope Corpus Boundary Detection -> Tier 1 Empirical Scope Notice.
4. Ambiguous / Underspecified Query Detection -> Tier 2 Interactive Clarification Chips.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


# Common ambiguous or underspecified single-word or short prompts
AMBIGUOUS_KEYWORDS = {
    "help",
    "sip",
    "groww",
    "confused",
    "why",
    "what",
    "fund",
    "mutual fund",
    "invest",
    "money",
    "problem",
    "issue",
    "cancel",
    "stop",
    "hi",
    "hello",
    "hey",
}

DEFAULT_CLARIFICATION_CHIPS = [
    {
        "label": "📉 Why do people stop their first SIP?",
        "query": "why people are not contuning their SIP",
    },
    {
        "label": "💸 Bank ECS Bounce Penalty (₹450+)",
        "query": "Why did bank charge 500 penalty for missed SIP bounce?",
    },
    {
        "label": "⏸️ Pause SIP instead of Cancelling",
        "query": "Can users pause SIP for 2 months instead of cancelling mandate?",
    },
    {
        "label": "📊 Month 1 Negative Return Panic",
        "query": "Why do first-time users panic when portfolio shows negative return in month 1?",
    },
]

_WORKFLOW_EXCLUSION_RE = re.compile(
    r"\b(?:sip\s+(?:date|day|timing|time|schedule|pause|skip|cancel|stop|mode)|debit\s+(?:date|day|timing|schedule)|autopay|mandate|netbanking)\b",
    re.IGNORECASE,
)
_EXPLICIT_FUND_PICK_RE = re.compile(
    r"\b(?:which\s+fund|best\s+(?:mutual\s+)?fund|top\s+(?:mutual\s+)?fund|(?:small|mid|large|flexi|multi)\s*-?\s*cap|parag\s+parikh|ppfas|quant|hdfc\s+fund|scheme|guaranteed|cagr)\b",
    re.IGNORECASE,
)
_FUND_SCHEME_OR_CATEGORY_RE = re.compile(
    r"\b(?:(?:small|mid|large|flexi|multi)\s*-?\s*cap|elss|index\s+fund|"
    r"parag\s+parikh|ppfas|quant|hdfc\s+(?:mid|small|flexi|top|index|mutual)|"
    r"sbi\s+(?:small|contra|bluechip|nifty|mutual)|nippon|mirae|axis\s+(?:bluechip|small|mid|elss|mutual)|"
    r"kotak\s+(?:emerging|small|flexi|mutual)|motilal|icici\s+pru(?:dential)?)\b",
    re.IGNORECASE,
)

# Domain tokens keeping genuine Groww / MF / SIP / banking / UX inquiries in corpus scope
_IN_SCOPE_DOMAIN_RE = re.compile(
    r"\b(?:sip|sips|mutual\s*funds?|funds?|mf|amc|nav|xirr|cagr|irr|ltcg|stcg|tax|"
    r"groww|zerodha|coin|kuvera|paytm|mandates?|autopay|nach|ecs|upi|netbanking|"
    r"banks?|debit|credit|deduct(?:ed|ion)?|bounce[sd]?|penalt(?:y|ies)|fines?|charges?|"
    r"allotment|t\+2|units?|folio|kyc|pan|aadhaar|demat|redeem|redemption|"
    r"withdraw(?:al)?|pause|skip|snooze|cancel(?:lation|led)?|stop(?:ped)?|"
    r"continu(?:e|ing|ation)|retention|churn|drop\s*-?offs?|cohorts?|"
    r"invest(?:ing|ment|ed|ors?)?|beginners?|novice|portfolios?|returns?|loss(?:es)?|profit|dips?|crash|correction|"
    r"markets?|bull|bear|nifty|sensex|index|equity|debt|elss|lump\s*sum|lumpsum|step\s*-?up|"
    r"(?:flexi|small|mid|large|multi)\s*-?\s*cap|rupee\s*cost|compounding|fd|fixed\s*deposit|"
    r"volatility|drawdown|horizon|risk|exit\s+load|expense\s+ratio|"
    r"ui|ux|screen|button|badge|notifications?|nudge|trust|anxiety|panic|fear|fomo|"
    r"themes?|evidence|feedback|reviews?|customers?|users?|onboarding|install?ments?|"
    r"sav(?:e|ing|ings)|wealth|money|salary|cash\s*flow|rupees?|rs|inr|fail(?:ed|ure|ing)?|reject(?:ed|ion)?|"
    r"kaise|band|karu|kare|chalu|rok|paisa)\b",
    re.IGNORECASE,
)


def is_sebi_advisory_solicitation(query: str) -> bool:
    """Detect fund-picking, scheme comparison, or return-guarantee asks while sparing workflow & platform asks."""
    q_lower = (query or "").strip().lower()
    if not q_lower:
        return False

    # Do not block operational workflow questions (e.g., "which is best sip date", "best autopay mode")
    if _WORKFLOW_EXCLUSION_RE.search(q_lower) and not _EXPLICIT_FUND_PICK_RE.search(q_lower):
        return False

    if any(
        phrase in q_lower
        for phrase in [
            "which fund should i buy",
            "which specific mutual fund",
            "best fund to invest",
            "recommend a mutual fund",
            "recommend a fund",
            "give me top funds",
            "should i buy parag parikh",
            "which mutual fund is best",
            "buy parag parikh or quant",
            "which fund should i pick",
            "top mutual fund",
            "best mutual fund",
            "best small cap",
            "best mid cap",
            "best flexi cap",
            "best large cap",
            "top small cap",
            "top mid cap",
            "top flexi cap",
            "guaranteed 25% return",
            "guaranteed return",
            "sell my hdfc fund",
            "which fund to invest",
            "which fund to buy",
            "best fund to buy",
            "best fund to pick",
        ]
    ):
        return True

    if re.search(
        r"\b(which|what|recommend|suggest|give me|tell me|pick|buy)\b.*\b(best|top|good)\b.*\b(fund|mutual\s+fund|scheme|stocks?|amc|sip(?!\s+(?:date|day|timing|time|schedule|amount|pause|skip|cancel|stop|mode|autopay|mandate)))\b",
        q_lower,
    ):
        return True

    if re.search(
        r"\b(best|top)\b.*\b(small|mid|large|flexi|multi)\s*-?\s*cap\b.*\b(fund|buy|invest)\b",
        q_lower,
    ):
        return True

    # Direct buy/sell/hold solicitation for a named scheme, AMC, or market-cap category
    if re.search(
        r"\b(?:should\s+i|can\s+i|is\s+it\s+good\s+to|worth)\s+(?:to\s+)?(?:buy|sell|hold|invest\s+in|pick|choose|enter|exit|switch\s+to)\b",
        q_lower,
    ) and (_FUND_SCHEME_OR_CATEGORY_RE.search(q_lower) or re.search(r"\b(?:a\s+)?(?:mutual\s+fund|fund|scheme)\b", q_lower)):
        return True

    # Scheme-vs-scheme comparison (e.g. "compare Parag Parikh Flexi Cap with Quant Small Cap"),
    # while sparing platform comparisons ("Groww vs Zerodha Coin")
    if re.search(r"\b(?:compare|vs\.?|versus|better\s+than|difference\s+between)\b", q_lower) and _FUND_SCHEME_OR_CATEGORY_RE.search(q_lower):
        return True

    return False


def is_dark_pattern_request(query: str) -> bool:
    """Detect manipulative retention, hidden-cancel, or FOMO coercion requests."""
    q_lower = (query or "").strip().lower()
    return any(
        phrase in q_lower
        for phrase in [
            "trap user",
            "trick user",
            "hide cancel",
            "hide the cancel",
            "make cancel hard",
            "dark pattern",
            "scare user",
            "countdown timer",
            "force to stay",
            "block cancellation",
            "block sip cancellation",
            "prevent user from cancel",
            "penalize user for stopping",
        ]
    )


def is_out_of_scope_query(query: str) -> bool:
    """Detect speculative trading, general trivia, or non-finance/non-MF-SIP queries."""
    q_clean = (query or "").strip()
    q_lower = q_clean.lower()
    if not q_lower:
        return False

    explicit_oos = any(
        phrase in q_lower
        for phrase in [
            "bitcoin",
            "crypto",
            "ethereum",
            "forex",
            "100x leverage",
            "intraday futures",
            "option trading tip",
            "f&o strategy",
            "capital of france",
            "who is the president",
            "weather in",
            "cricket score",
        ]
    )
    if explicit_oos:
        return True

    # Catch general off-topic multi-word queries (e.g. "best laptop under 50k")
    # that lack any MF/SIP/investing/banking/UX domain token and are not advisory/FOMO probes.
    words = re.findall(r"[a-zA-Z0-9]+", q_lower)
    if len(words) >= 4 and not _IN_SCOPE_DOMAIN_RE.search(q_lower):
        if not is_sebi_advisory_solicitation(q_lower) and not is_dark_pattern_request(q_lower):
            return True

    return False


class PreLLMGuardrails:
    """Pre-retrieval, pre-generation guardrail inspector executing in < 5ms at 0 token cost."""

    @classmethod
    def inspect(cls, query: str) -> Optional[Dict[str, Any]]:
        """Evaluate incoming query before retrieval or LLM execution.

        Returns:
            Dict with 'action', 'answer', 'fallback_tier', 'clarification_chips' if intercepted,
            or None if query is safe to proceed to retrieval and generation.
        """
        q_clean = query.strip()
        q_lower = q_clean.lower()

        # ---------------------------------------------------------------------
        # 1. Ambiguous / Underspecified Query Probe (Tier 2 Clarification Chips)
        # ---------------------------------------------------------------------
        # If query is too brief (< 4 characters) or matches generic single keyword
        if len(q_clean) <= 3 or q_lower in AMBIGUOUS_KEYWORDS:
            answer = (
                "### 1. Executive Summary & Behavioral Dynamic\n"
                "Your inquiry appears brief or underspecified. The **Groww Qualitative Discovery Engine** "
                "is indexed on **3,052 verified customer conversations** analyzing first-time mutual fund SIP continuation, "
                "mandate failures, payment drop-offs, and early-tenure investor psychology.\n\n"
                "### 2. Discovered Friction & Root Cause Breakdown\n"
                "- **Operational / Technical Friction:** Narrow or generic keywords without clear context cannot be precisely matched against customer conversation receipts.\n"
                "- **Cognitive / Mental Model Mismatch:** Please select one of the verified research inquiry pathways below to explore grounded qualitative insights."
            )
            return {
                "intercepted": True,
                "skip_retrieval": True,
                "tier": "Tier 2: Interactive Clarification",
                "reason": "Query is underspecified or ambiguous. Providing structured clarification pathways.",
                "answer": answer,
                "clarification_chips": DEFAULT_CLARIFICATION_CHIPS,
                "sebi_clean": True,
                "fomo_clean": True,
            }

        # ---------------------------------------------------------------------
        # 2. SEBI Advisory Solicitation Probe (Tier 1 Regulatory Refusal)
        # ---------------------------------------------------------------------
        is_advisory_solicitation = is_sebi_advisory_solicitation(q_lower)

        if is_advisory_solicitation:
            answer = (
                "### 1. Executive Summary & Behavioral Dynamic\n"
                "**SEBI Regulatory Non-Advice Boundary Notice:** In strict compliance with **SEBI regulations**, the Groww Qualitative "
                "Discovery Engine **does not recommend, rate, rank, or pick specific mutual fund schemes, AMCs, or individual equities** [EVID-1]. "
                "First-time investors frequently seek 'the single star fund' due to decision paralysis and acute loss aversion. "
                "Long-term 12-month retention is determined by automated payment reliability and realistic "
                "compounding horizons, not by chasing top-quartile past performers [EVID-2].\n\n"
                "### 2. Discovered Friction & Root Cause Breakdown\n"
                "- **Operational / Technical Friction:** Novice users get overwhelmed by 2,500+ scheme options on onboarding interfaces, "
                "leading to abandoned registration flows or accidental creation of duplicate parallel SIPs.\n"
                "- **Cognitive / Mental Model Mismatch:** Novice investors treat mutual funds like consumer e-commerce products (hunting for '5-star ratings'), "
                "rather than anchoring their choice to a 3-to-5 year time horizon and risk tolerance [EVID-1]."
            )
            return {
                "intercepted": True,
                "skip_retrieval": False,
                "tier": "Tier 1: Regulatory Refusal (SEBI)",
                "reason": "SEBI non-advice guardrail engaged. Intercepted before external token consumption.",
                "answer": answer,
                "clarification_chips": [],
                "sebi_clean": True,
                "fomo_clean": True,
            }

        # ---------------------------------------------------------------------
        # 3. FOMO & Dark Pattern Probe (Tier 1 Ethical Growth Refusal)
        # ---------------------------------------------------------------------
        if is_dark_pattern_request(q_lower):
            answer = (
                "### 1. Executive Summary & Behavioral Dynamic\n"
                "**Ethical Growth & Anti-FOMO Principle:** Groww Discovery Engine strictly rejects deceptive dark patterns, hidden cancel buttons, "
                "and artificial friction to trap investors [EVID-1]. Behavioral finance research shows that artificial barriers to exit induce "
                "acute psychological reactance: when users feel trapped during a temporary month-end cashflow crunch, they permanently churn by deleting "
                "the app and terminating bank mandates at the bank branch.\n\n"
                "### 2. Discovered Friction & Root Cause Breakdown\n"
                "- **Operational / Technical Friction:** Lack of flexible, temporary cashflow controls (e.g. 1-tap pause or skip) forces users into an "
                "all-or-nothing binary cancellation decision [EVID-1].\n"
                "- **Cognitive / Mental Model Mismatch:** Deceptive hurdles destroy institutional trust. Long-term wealth creation requires high user agency "
                "and psychological safety, not coercive retention locks."
            )
            return {
                "intercepted": True,
                "skip_retrieval": False,
                "tier": "Tier 1: Ethical Refusal (Anti-FOMO)",
                "reason": "Dark pattern request intercepted. Guardrail enforced at 0 tokens.",
                "answer": answer,
                "clarification_chips": [],
                "sebi_clean": True,
                "fomo_clean": True,
            }

        # ---------------------------------------------------------------------
        # 4. Out-of-Scope Corpus Boundary Probe (Tier 1 Scope Notice)
        # ---------------------------------------------------------------------
        if is_out_of_scope_query(q_lower):
            answer = (
                "### 1. Executive Summary & Behavioral Dynamic\n"
                "**Corpus Empirical Scope Notice:** This Qualitative Discovery Engine is indexed strictly on **3,052 verified customer conversations** "
                "focused on first-time mutual fund investors, SIP payment rails, and 12-month retention heuristics. "
                "Speculative trading instruments, cryptocurrencies, high-leverage derivatives, and general knowledge fall outside this research engine's empirical corpus.\n\n"
                "### 2. Discovered Friction & Root Cause Breakdown\n"
                "- **Operational / Technical Friction:** The inquiry targets financial domains or topics outside our verified mutual fund SIP dataset.\n"
                "- **Cognitive / Mental Model Mismatch:** Novice investors who confuse long-term passive SIP compounding with speculative get-rich-quick trading "
                "suffer from severe hyper-volatility burnout and premature capital destruction."
            )
            return {
                "intercepted": True,
                "skip_retrieval": True,
                "tier": "Tier 1: Out-of-Scope Corpus Boundary",
                "reason": "Out of scope domain intercepted. Guardrail enforced at 0 tokens.",
                "answer": answer,
                "clarification_chips": [],
                "sebi_clean": True,
                "fomo_clean": True,
            }

        return None
