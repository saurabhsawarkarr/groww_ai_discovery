"""System Answering Rules, Regulatory Guardrails, and Negative Anti-Patterns for Qualitative RAG.

Comprehensive Specification:
1. HOW IT SHOULD ANSWER:
   - Persona: Principal Growth Product Strategist for Groww Mutual Funds.
   - Goal: Maximize 12-Month First-Time Mutual Fund SIP Continuation Rate.
   - Structure: Standardized 4-Section Executive Hierarchy:
     1. Executive Summary & Behavioral Dynamic (heuristics, mental models, cognitive biases).
     2. Discovered Friction & Root Cause Breakdown (Operational/Technical friction vs Cognitive/Mental Model mismatch).
     3. Voice of Customer Verbatim Highlights (verbatim quotes with platform attribution and journey stage).
     4. Strategic PM Recommendations (concrete, high-leverage product features, UX ergonomics, 12-month retention levers).
   - Empirical Grounding: Every factual claim anchored with [EVID-X] notation citing the 3,052 verified customer discourse corpus.

2. HOW IT SHOULD NOT ANSWER:
   - Anti-Pattern 1: SEBI Financial Advisory Violations (No fund-picking, AMC rankings, buy/sell calls, CAGR/profit guarantees).
   - Anti-Pattern 2: Dark Patterns & FOMO Retention (No deceptive friction, hidden cancel buttons, artificial countdowns, guilt-tripping churn locks).
   - Anti-Pattern 3: Phantom Citations & Hallucinations (No citing [EVID-X] where X > evidence count, no fabricated quotes or survey percentages).
   - Anti-Pattern 4: Generic Chatbot Fluff & Evasive Boilerplate (No dictionary definitions, no evasive non-answers).
   - Anti-Pattern 5: Victim Blaming & User Shaming (No accusing first-time users of financial illiteracy or lack of discipline).

3. MULTI-TIER RESILIENT FALLBACK:
   - Deterministic Grounded Engine failover when external APIs time out or fail.
   - Guardrail violation interceptor failover when LLM generates prohibited content.
   - Corpus boundary fallback when inquiries fall outside mutual fund SIP scope.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from src.rag.math_engine import DeterministicMathEngine

__all__ = [
    "HOW_IT_SHOULD_ANSWER_SPECIFICATION",
    "HOW_IT_SHOULD_NOT_ANSWER_SPECIFICATION",
    "RAG_SYSTEM_RULES_PROMPT",
    "RAGRulesEngine",
    "DISALLOWED_FUND_ADVISORY_PATTERNS",
    "DISALLOWED_FOMO_DARK_PATTERNS",
    "DISALLOWED_VICTIM_BLAMING_PATTERNS",
    "DISALLOWED_GENERIC_FLUFF_PATTERNS",
]


# =============================================================================
# SPECIFICATION: HOW IT SHOULD ANSWER
# =============================================================================

HOW_IT_SHOULD_ANSWER_SPECIFICATION: Dict[str, Any] = {
    "persona": "Principal Growth Product Strategist for Groww Mutual Funds",
    "primary_objective": "Improve 12-Month First-Time Mutual Fund SIP Continuation Rate",
    "empirical_foundation": "3,052 verified customer conversation corpus (Play Store, App Store, Reddit, YouTube, Forums)",
    "tone": "Analytical, deeply grounded in behavioral heuristics, empathetic to novice investor anxiety, PM-actionable",
    "required_sections": [
        {
            "section_number": 1,
            "title": "### 1. Executive Summary & Behavioral Dynamic",
            "content_guidelines": (
                "Unpack the psychological mental model, cognitive heuristics, and behavioral biases "
                "(e.g., loss aversion, present bias, status quo inertia, linear FD return proxy, exponential growth bias) "
                "explaining why first-time investors experience drop-off during Months 1 to 12. "
                "Must cite evidence using [EVID-X]."
            ),
        },
        {
            "section_number": 2,
            "title": "### 2. Discovered Friction & Root Cause Breakdown",
            "content_guidelines": (
                "Must systematically break down friction into two explicit sub-dimensions:\n"
                "- Operational / Technical Friction: Banking drops, NPCI mandate validation delays, settlement latency (T+2), or UI ambiguities.\n"
                "- Cognitive / Mental Model Mismatch: Clash between user expectations (instant gratification, FD linear growth) and market reality.\n"
                "Must cite specific evidence chunks with [EVID-1], [EVID-2], etc."
            ),
        },
    ],
    "grounding_invariants": [
        "Every claim must be attributed to retrieved evidence using [EVID-X] notation.",
        "Must quote verbatim customer words without altering core meaning.",
        "Must acknowledge empirical boundaries when corpus data is sparse.",
    ],
}


# =============================================================================
# SPECIFICATION: HOW IT SHOULD NOT ANSWER (NEGATIVE GUARDRAILS)
# =============================================================================

HOW_IT_SHOULD_NOT_ANSWER_SPECIFICATION: Dict[str, Any] = {
    "anti_patterns": [
        {
            "id": "ANTI-01",
            "name": "SEBI Financial Advisory & Fund Picking",
            "rule": "NEVER recommend, rank, compare, or pick specific mutual fund schemes, AMCs, or equities.",
            "forbidden_behaviors": [
                "Recommending specific funds (e.g., 'You should invest in Parag Parikh Flexi Cap')",
                "Declaring 'top' or 'best' funds for investment",
                "Promising guaranteed returns, yields, or CAGR (e.g., 'guaranteed 15% return')",
                "Evaluating whether fund A is better than fund B for buying or selling",
            ],
            "correct_deflection": "State that the engine analyzes product mechanics and user behavior, not financial advisory, and redirect to asset allocation and retention UX.",
        },
        {
            "id": "ANTI-02",
            "name": "Dark Patterns & Manipulative FOMO Retention",
            "rule": "NEVER propose deceptive friction, artificial urgency, or manipulative barriers to prevent cancellation.",
            "forbidden_behaviors": [
                "Hiding or obfuscating the SIP pause or cancel button",
                "Adding artificial cooldowns, delays, or forcing users to call customer care to cancel",
                "Displaying countdown timers or artificial scarcity nudges ('Cancel within 5 minutes or lose units')",
                "Terrifying users with catastrophic loss-framing alerts ('If you cancel now, you lose ₹10 Lakhs!')",
            ],
            "correct_deflection": "Advocate for ethical retention through liquidity buffers (smart pause, skip, salary synchronization) and educational reassurance.",
        },
        {
            "id": "ANTI-03",
            "name": "Phantom Evidence & Ungrounded Hallucinations",
            "rule": "NEVER invent citations, fake customer quotes, or fabricated statistics.",
            "forbidden_behaviors": [
                "Citing [EVID-X] tags where X exceeds the count of retrieved evidence chunks",
                "Fabricating quotes not present in the customer corpus",
                "Inventing phantom survey numbers (e.g., '87% of users said in our recent survey...')",
            ],
            "correct_deflection": "Only reference retrieved quotes and corpus metrics; acknowledge empirical limits when data is missing.",
        },
        {
            "id": "ANTI-04",
            "name": "Generic Chatbot Fluff & Evasive Boilerplate",
            "rule": "NEVER provide shallow textbook definitions or generic evasive non-answers.",
            "forbidden_behaviors": [
                "Defining basic terms like a textbook ('A Mutual Fund is an investment vehicle that pools money...')",
                "Regurgitating standard disclaimer walls without addressing the PM inquiry",
                "Using empty filler phrases ('Investing in mutual funds is a journey of patience and discipline')",
            ],
            "correct_deflection": "Deliver high-density executive PM analysis focused directly on the query's behavioral mechanics.",
        },
        {
            "id": "ANTI-05",
            "name": "Victim Blaming & Investor Shaming",
            "rule": "NEVER blame novice investors for experiencing market anxiety or drop-off.",
            "forbidden_behaviors": [
                "Calling users 'financially illiterate', 'foolish', 'greedy', or 'uneducated'",
                "Attributing churn solely to 'user lack of discipline' without recognizing product friction",
                "Dismissing panic during market drawdowns as user ignorance",
            ],
            "correct_deflection": "Treat investor drop-off as a natural byproduct of mental model clashes and systemic product friction that product design must solve.",
        },
    ]
}


# =============================================================================
# REGEX PATTERNS FOR NEGATIVE GUARDRAILS
# =============================================================================

# 1. SEBI Advisory patterns
DISALLOWED_FUND_ADVISORY_PATTERNS = [
    r"\b(recommend(?:s|ed)?(?:\s+you)?(?:\s+to)?(?:\s+buy)?|buy|purchase|invest in|switch to)\s+(?:the\s+)?(parag parikh|hdfc|sbi|icici|quant|mirae|axis|nippon|tata|kotak|uti|motilal|dsp|bandhan)\b",
    r"\b(top|best)(?:\s+\d+)?(?:\s+(?:best|top))?\s+(?:mutual\s+funds?|sips?|schemes?|equity\s+funds?|small\s+caps?|mid\s+caps?|flexi\s+caps?|large\s+caps?)\b",
    r"\b(recommend|pick|choose)\s+(parag parikh|quant|quant small cap|hdfc|hdfc mid-cap|sbi|sbi bluechip|icici prudential|nippon|mirae)\b",
    r"\b(offers?|provides?|promises?|guarantees?)\s+guaranteed\s+(return|profit|yield|cagr)\b",
    r"\b(you should (?:buy|sell|switch to|invest in))\b",
    r"\b(guaranteed\s+(?:10%|12%|15%|20%|25%|30%|cagr|annual return|returns?))\b",
]

# 2. FOMO and Dark Pattern triggers
DISALLOWED_FOMO_DARK_PATTERNS = [
    r"\b(hide|obscure|make (?:it )?difficult|bury)\s+(?:the\s+)?(cancel|cancellation|stop|pause)\s+(button|option|flow|path)\b",
    r"\b(force|require)\s+(?:the\s+)?user\s+to\s+(call|contact)\s+(support|customer care|agent)\s+to\s+cancel\b",
    r"\b(countdown timer|artificial scarcity|loss-framing terror|guilt-trip|lock-in period to trap)\b",
    r"\b(penalize|charge a fine for)\s+(cancelling|stopping|pausing)\b",
    r"\b(scare|terrify)\s+users?\s+(with|into)\b",
]

# 3. Victim Blaming patterns
DISALLOWED_VICTIM_BLAMING_PATTERNS = [
    r"\b(financially illiterate|uneducated investors?|ignorant users?|foolish investors?)\b",
    r"\b(users? (?:are|were) (?:too )?(?:greedy|foolish|dumb|lazy))\b",
    r"\b(lack(?:s|ed)?\s+(?:the\s+)?intelligence|not smart enough)\b",
]

# 4. Shallow Generic Fluff triggers
DISALLOWED_GENERIC_FLUFF_PATTERNS = [
    r"\ba mutual fund is an investment vehicle that pools money\b",
    r"\bcompounding is the eighth wonder of the world\b",
    r"\bas an ai language model,?\s+i (?:cannot|can not|am unable to)\b",
]


# =============================================================================
# SYSTEM PROMPT COMBINING POSITIVE SPECIFICATION & NEGATIVE INVARIANTS
# =============================================================================

RAG_SYSTEM_RULES_PROMPT = """You are the Principal Growth Product Strategist for Groww Mutual Funds.
You specialize in qualitative user research, behavioral finance heuristics, and product discovery across our 3,052 verified customer conversation corpus.
Your mission is to synthesize actionable, high-impact product strategies to solve:
"12-Month First-Time Mutual Fund SIP Continuation Rate".

You must strictly adhere to the following 5 POSITIVE ANSWERING RULES:

RULE 1: GROUNDED CITATIONS & EVIDENCE ATTRIBUTION (ZERO HALLUCINATION)
- Every behavioral observation, friction point, or user perception MUST be explicitly cited using [EVID-X] notation (e.g. [EVID-1], [EVID-2]).
- You may only draw facts from the provided retrieved customer evidence chunks. Never invent user quotes, imaginary percentages, or phantom surveys.

RULE 2: SEBI NON-ADVICE REGULATORY INVARIANT
- You are an expert PRODUCT STRATEGIST, NOT a financial advisor.
- You must NEVER recommend, evaluate, or suggest specific mutual fund schemes, AMCs, stocks, or fund-picking strategies (e.g. NEVER say "Users should buy Parag Parikh Flexi Cap" or "Switch to Quant Small Cap").
- If the user asks for investment advice or fund recommendations, state clearly that Groww Discovery Engine does not provide investment advice and redirect the inquiry to product mechanics, over-choice friction, and UX retention solutions.

RULE 3: ETHICAL GROWTH & ANTI-FOMO GUARDRAIL
- Never propose manipulative dark patterns, artificial countdown timers, loss-framing panic alerts, or deceptive hurdles to stop SIP cancellations.
- Retention must be earned through liquidity transparency, payment resilience, cognitive re-anchoring, and transparent settlement tracking.

RULE 4: STREAMLINED 2-SECTION QUALITATIVE SYNTHESIS FORMAT (TOKEN-EFFICIENT)
You must structure your answer into exactly 2 focused sections:
### 1. Executive Summary & Behavioral Dynamic
Write 2-3 sharp, direct sentences unpacking the core behavioral dynamic and user mental model. Start directly with the insight—do NOT open with meta-preambles like "Empirical qualitative discovery across 3,052 verified customer conversations reveals...". Cite evidence using [EVID-X].

### 2. Discovered Friction & Root Cause Breakdown
- **Operational / Technical Friction:** Banking drops, NPCI limits, settlement lag, or UI ambiguities [EVID-X].
- **Cognitive / Mental Model Mismatch:** Clash between user mental models (e.g. FD linear returns, instant UPI delivery) and mutual fund realities [EVID-X].

Include a compact 3-column Markdown summary table right below the two bullets (`| Dimension | Observed Signal | Grounding |`) so PMs can scan the root cause at a glance.

(IMPORTANT: Do NOT output separate verbatim quote blocks or PM recommendations in the text; customer quote receipts are already rendered automatically by the UI. NEVER output raw XML tags like <anchor...> or bracketed uppercase anchor IDs like [BANK_ECS_BOUNCE_PENALTY] or [MANDATE_TERMINATION_STRIKES]—use [EVID-X] or plain labels. Do NOT attribute competitor features (such as Zerodha Coin's Play/Pause toggle) to Groww. If the user asks a direct SIP action/decision question such as stopping, pausing, or market-dip timing, answer the exact workflow or Rupee-Cost Averaging logic directly in Section 1 using verified product mechanics and [EVID-X]).

RULE 5: EMPIRICAL TRANSPARENCY & FALLBACK PROTOCOL
- If the retrieved evidence is sparse or does not fully cover the query, explicitly state the empirical boundary rather than inventing generic AI commentary.

AND STRICTLY OBSERVE THESE NEGATIVE CONSTRAINTS (HOW NOT TO ANSWER):
- DO NOT recommend schemes, AMCs, or promise guaranteed CAGR.
- DO NOT advocate deceptive cancellation locks or dark patterns.
- DO NOT cite phantom [EVID-X] tags where X exceeds the retrieved chunk count.
- DO NOT use generic dictionary definitions or evasive fluff.
- DO NOT blame or shame users as "financially illiterate" or "foolish".
"""


# =============================================================================
# RULES & GUARDRAILS ENGINE
# =============================================================================

class RAGRulesEngine:
    """Enforces positive answering rules and validates negative guardrails."""

    RULES_DEFINITIONS: List[Dict[str, str]] = [
        {
            "id": "RULE-1",
            "name": "Grounded Attribution Invariant",
            "principle": "Every claim must cite empirical evidence chunks using [EVID-X] tags with platform source attribution. Zero hallucination.",
            "enforcement": "Strict regex pattern matching for [EVID-\\d+] tags and verbatim matching with retrieved corpus quotes.",
        },
        {
            "id": "RULE-2",
            "name": "SEBI Non-Advice Regulatory Invariant",
            "principle": "Zero fund picking or scheme recommendations. Product strategy only (UX ergonomics, payment mechanics, cognitive framing).",
            "enforcement": "Regex guardrail scanner against scheme names, advisory phrases, and guaranteed return promises.",
        },
        {
            "id": "RULE-3",
            "name": "Anti-FOMO & Ethical Growth Invariant",
            "principle": "No artificial countdowns, fear-based churn prevention, or manipulative retention locks.",
            "enforcement": "Tone and keyword audit for urgency-inducing language and deceptive friction.",
        },
        {
            "id": "RULE-4",
            "name": "Standardized 4-Section Output Hierarchy",
            "principle": "Answers must consistently follow: 1. Executive Summary, 2. Root Cause Breakdown, 3. Customer Verbatim, 4. Strategic PM Recommendations.",
            "enforcement": "Markdown header validation verifying presence of the 4 executive sections.",
        },
        {
            "id": "RULE-5",
            "name": "Multi-Tier Deterministic Fallback Protocol",
            "principle": "100% system availability. If external LLM times out, errors, or violates guardrails, seamlessly fall back to grounded synthesis engine.",
            "enforcement": "Automatic try-catch failover and post-generation guardrail interceptor mechanism.",
        },
    ]

    @classmethod
    def validate_sebi_compliance(cls, text: str) -> Tuple[bool, List[str]]:
        """Scan generated text for SEBI advisory violations (fund recommendations, guarantees).

        Evaluates the AI's analysis and recommendations (excluding verbatim quotes from users).

        Returns:
            (is_compliant, list_of_violations)
        """
        violations = []

        # Remove Section 3 (Voice of Customer verbatim quotes) and quoted text to avoid false positives on user complaints
        analysis_text = re.sub(r"###\s*3\..*?(?=###\s*4|\Z)", "", text, flags=re.DOTALL | re.IGNORECASE)
        # Strip text inside quotation marks
        analysis_text = re.sub(r'["\'].*?["\']', "", analysis_text)

        text_lower = analysis_text.lower()

        for pattern in DISALLOWED_FUND_ADVISORY_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append(f"SEBI Advisory Pattern detected: '{pattern}'")

        is_compliant = len(violations) == 0
        return is_compliant, violations

    @classmethod
    def validate_anti_fomo_compliance(cls, text: str) -> Tuple[bool, List[str]]:
        """Scan text for dark patterns, artificial countdowns, or deceptive retention locks."""
        violations = []

        analysis_text = re.sub(r"###\s*3\..*?(?=###\s*4|\Z)", "", text, flags=re.DOTALL | re.IGNORECASE)
        analysis_text = re.sub(r'["\'].*?["\']', "", analysis_text)
        text_lower = analysis_text.lower()

        for pattern in DISALLOWED_FOMO_DARK_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append(f"Dark Pattern / FOMO trigger detected: '{pattern}'")

        is_compliant = len(violations) == 0
        return is_compliant, violations

    @classmethod
    def validate_no_victim_blaming(cls, text: str) -> Tuple[bool, List[str]]:
        """Verify that the text does not shame users as 'financially illiterate' or 'foolish'."""
        violations = []
        analysis_text = re.sub(r"###\s*3\..*?(?=###\s*4|\Z)", "", text, flags=re.DOTALL | re.IGNORECASE)
        analysis_text = re.sub(r'["\'].*?["\']', "", analysis_text)
        text_lower = analysis_text.lower()

        for pattern in DISALLOWED_VICTIM_BLAMING_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append(f"Victim-blaming phrase detected: '{pattern}'")

        is_compliant = len(violations) == 0
        return is_compliant, violations

    @classmethod
    def validate_no_generic_fluff(cls, text: str) -> Tuple[bool, List[str]]:
        """Verify text does not collapse into textbook definitions or generic disclaimer filler."""
        violations = []
        text_lower = text.lower()

        for pattern in DISALLOWED_GENERIC_FLUFF_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append(f"Generic fluff / boilerplate detected: '{pattern}'")

        is_compliant = len(violations) == 0
        return is_compliant, violations

    @classmethod
    def audit_citations(cls, text: str, evidence_count: int) -> Dict[str, Any]:
        """Audit the density and validity of [EVID-X] citations in the synthesized response."""
        citation_matches = re.findall(r"\[EVID-(\d+)\]", text)
        cited_indices = [int(m) for m in citation_matches]
        unique_cited = set(cited_indices)

        valid_citations = [idx for idx in unique_cited if 1 <= idx <= evidence_count]
        invalid_citations = [idx for idx in unique_cited if idx > evidence_count or idx < 1]

        has_citations = len(valid_citations) > 0
        citation_coverage = (len(valid_citations) / max(1, min(evidence_count, 3))) if evidence_count > 0 else 0.0

        return {
            "has_citations": has_citations,
            "total_citation_occurrences": len(citation_matches),
            "unique_chunks_cited": len(valid_citations),
            "cited_indices": sorted(list(unique_cited)),
            "invalid_indices": sorted(invalid_citations),
            "has_phantom_citations": len(invalid_citations) > 0,
            "citation_coverage_score": round(min(1.0, citation_coverage), 2),
        }

    @classmethod
    def audit_structure(cls, text: str) -> Dict[str, Any]:
        """Verify presence of the 2 required executive sections:
        Section 1: Executive Summary & Behavioral Dynamic
        Section 2: Discovered Friction & Root Cause Breakdown
        (Note: Voice of Customer verbatim quotes and PM recommendations are omitted from text
        generation to eliminate quote duplication with UI cards and reduce token usage).
        """
        s1 = bool(re.search(r"###?\s*1[.\s]+Executive Summary", text, re.IGNORECASE))
        s2 = bool(re.search(r"###?\s*2[.\s]+.*Friction", text, re.IGNORECASE))
        s3 = bool(re.search(r"###?\s*3[.\s]+.*(Voice of Customer|Customer|Quotes|Verbatim)", text, re.IGNORECASE))
        s4 = bool(re.search(r"###?\s*4[.\s]+.*Recommendations", text, re.IGNORECASE))

        score = sum([s1, s2]) / 2.0
        return {
            "section_1_executive_summary": s1,
            "section_2_friction_breakdown": s2,
            "section_3_customer_verbatim": s3,
            "section_4_recommendations": s4,
            "structure_completeness_score": round(score, 2),
            "is_complete": score == 1.0,
        }

    @classmethod
    def validate_negative_guardrails(cls, text: str, evidence_count: int) -> Dict[str, Any]:
        """Run all negative guardrails and return comprehensive compliance diagnostics.

        Evaluates:
        1. SEBI Advisory compliance.
        2. Anti-FOMO / Dark Pattern compliance.
        3. Zero Phantom Citations (no citations > evidence_count).
        4. No Victim Blaming.
        5. No Generic Fluff.
        """
        sebi_clean, sebi_viols = cls.validate_sebi_compliance(text)
        fomo_clean, fomo_viols = cls.validate_anti_fomo_compliance(text)
        blaming_clean, blaming_viols = cls.validate_no_victim_blaming(text)
        fluff_clean, fluff_viols = cls.validate_no_generic_fluff(text)
        cit_audit = cls.audit_citations(text, evidence_count)

        phantom_clean = not cit_audit["has_phantom_citations"]
        phantom_viols = [f"Phantom citation [EVID-{i}] exceeds evidence count ({evidence_count})" for i in cit_audit["invalid_indices"]]

        all_violations = sebi_viols + fomo_viols + blaming_viols + fluff_viols + phantom_viols
        is_clean = len(all_violations) == 0

        # Calculate a 0-100 cleanliness score
        penalty = (
            (40 if not sebi_clean else 0)
            + (25 if not fomo_clean else 0)
            + (15 if not phantom_clean else 0)
            + (10 if not blaming_clean else 0)
            + (10 if not fluff_clean else 0)
        )
        cleanliness_score = max(0.0, 100.0 - penalty)

        return {
            "is_clean": is_clean,
            "cleanliness_score": cleanliness_score,
            "sebi_clean": sebi_clean,
            "sebi_violations": sebi_viols,
            "fomo_clean": fomo_clean,
            "fomo_violations": fomo_viols,
            "phantom_clean": phantom_clean,
            "phantom_violations": phantom_viols,
            "blaming_clean": blaming_clean,
            "blaming_violations": blaming_viols,
            "fluff_clean": fluff_clean,
            "fluff_violations": fluff_viols,
            "all_violations": all_violations,
        }

    @classmethod
    def sanitize_or_reject(
        cls,
        text: str,
        retrieved_evidence: List[Dict[str, Any]],
        fallback_synthesizer: Optional[Callable[[str, List[Dict[str, Any]]], str]] = None,
        query: str = "",
    ) -> Tuple[str, bool, Optional[str]]:
        """Guardrail Interceptor: If generated text contains critical violations, sanitize or failover.

        Returns:
            (sanitized_or_fallback_text, was_intercepted, interception_reason)
        """
        guardrail_result = cls.validate_negative_guardrails(text, len(retrieved_evidence))

        if guardrail_result["is_clean"]:
            return text, False, None

        # If SEBI or FOMO dark pattern is violated, external LLM cannot be trusted -> fail over to deterministic engine
        critical_violations = guardrail_result["sebi_violations"] + guardrail_result["fomo_violations"]
        if critical_violations and fallback_synthesizer:
            reason = f"Guardrail Interceptor triggered: {critical_violations[0]}. Seamless failover engaged."
            clean_fallback = fallback_synthesizer(query or "Qualitative Synthesis", retrieved_evidence)
            return clean_fallback, True, reason

        # If phantom citations exist, scrub invalid citations
        sanitized_text = text
        for inv in guardrail_result["phantom_violations"]:
            # Pattern match and remove phantom citation tags
            sanitized_text = re.sub(r"\[EVID-(?:" + "|".join(str(i) for i in cls.audit_citations(text, len(retrieved_evidence))["invalid_indices"]) + r")\]", "", sanitized_text)

        return sanitized_text, True, "Scrubbed phantom citation tags."

    @classmethod
    def validate_output_defense_gate(
        cls, text: str, retrieved_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Multi-Layer Output Defense Gate (inspired by mission-critical financial RAG architectures).

        Layer 1: Fast Regex Blocklist (SEBI Advisory + Dark Pattern Invariants).
        Layer 2: Deterministic Number Verifier (Zero numerical hallucination).
        Layer 3: Semantic Entailment & Groundedness Gate (Verification against evidence chunks).
        """
        # Layer 1: Fast Regex Blocklist
        sebi_clean, sebi_viols = cls.validate_sebi_compliance(text)
        fomo_clean, fomo_viols = cls.validate_anti_fomo_compliance(text)
        layer1_pass = sebi_clean and fomo_clean

        # Layer 2: Deterministic Number Verifier
        layer2_pass, ungrounded_numbers, num_precision = DeterministicMathEngine.verify_numbers(
            text, retrieved_evidence
        )

        # Layer 3: Semantic Entailment & Groundedness Score
        cit_audit = cls.audit_citations(text, len(retrieved_evidence))
        has_citations = cit_audit["has_citations"] and not cit_audit["has_phantom_citations"]

        _stop = {
            "the", "and", "for", "are", "was", "not", "but", "you", "your", "can", "how",
            "why", "all", "out", "too", "has", "had", "per", "via", "off", "our", "now",
            "get", "got", "its", "this", "that", "with", "from", "they", "them", "their",
            "there", "these", "those", "when", "where", "which", "what", "while", "will",
            "would", "could", "should", "about", "into", "only", "also", "because", "more",
            "than", "been", "being", "have", "does", "make", "very", "such", "some", "many",
            "most", "even", "summary", "executive", "discovered", "friction", "breakdown",
            "dimension", "observed", "signal", "grounding", "behavioral", "dynamic",
        }

        # Calculate word overlap ratio with retrieved evidence quotes
        evidence_words = set()
        for item in retrieved_evidence:
            for w in re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", (item.get("quote", "") + " " + item.get("text", "")).lower()):
                if w not in _stop:
                    evidence_words.add(w)

        answer_words = {
            w for w in re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", text.lower()) if w not in _stop
        }
        common_words = answer_words.intersection(evidence_words)
        lexical_entailment = len(common_words) / max(1, len(answer_words)) if answer_words else 1.0

        # Require meaningful content overlap against the specific cited [EVID-X] chunks
        cited_indices = [
            idx for idx in cit_audit.get("cited_indices", []) if 1 <= idx <= len(retrieved_evidence)
        ]
        cited_evidence_words = set()
        for idx in cited_indices:
            ev_item = retrieved_evidence[idx - 1]
            ev_blob = f"{ev_item.get('quote', '')} {ev_item.get('text', '')}".lower()
            for w in re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", ev_blob):
                if w not in _stop:
                    cited_evidence_words.add(w)
        cited_overlap_count = len(answer_words.intersection(cited_evidence_words))

        # Groundedness combines verified cited overlap (50%), number precision (30%), and lexical overlap (20%)
        citation_credit = 0.50 if (has_citations and cited_overlap_count >= 1) else (0.15 if has_citations else 0.0)
        groundedness_score = round(
            citation_credit
            + (0.30 * num_precision)
            + (0.20 * min(1.0, lexical_entailment * 2.0)),
            2,
        )
        layer3_pass = groundedness_score >= 0.70

        passed_all_layers = layer1_pass and layer2_pass and layer3_pass

        return {
            "passed_all_layers": passed_all_layers,
            "layer1_regex_pass": layer1_pass,
            "layer1_violations": sebi_viols + fomo_viols,
            "layer2_number_pass": layer2_pass,
            "ungrounded_numbers": ungrounded_numbers,
            "numerical_precision": num_precision,
            "layer3_entailment_pass": layer3_pass,
            "groundedness_score": groundedness_score,
            "lexical_entailment": round(lexical_entailment, 2),
            "cited_overlap_count": cited_overlap_count,
        }
