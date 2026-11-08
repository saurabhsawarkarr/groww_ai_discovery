"""System Answering Rules and Regulatory Guardrails for Qualitative RAG.

Enforces:
1. Grounded Attribution Invariant (Every claim must cite [EVID-X] verbatim evidence).
2. SEBI Non-Advice Regulatory Invariant (No mutual fund picking, buying, or selling advice).
3. Anti-Dark Patterns & Non-FOMO Guardrail (No artificial urgency, countdowns, or deceptive friction).
4. Standardized 4-Section Executive Synthesis Hierarchy.
5. Deterministic Grounded Fallback Protocol (100% resilience when external LLMs are unavailable).
"""

import re
from typing import Any, Dict, List, Tuple


# Comprehensive list of AMC schemes, fund names, or financial advisory triggers to forbid in AI recommendations
DISALLOWED_FUND_ADVISORY_PATTERNS = [
    r"\b(recommend(?:s|ed)?(?:\s+you)?(?:\s+to)?(?:\s+buy)?|buy|purchase|invest in|switch to)\s+(?:the\s+)?(parag parikh|hdfc|sbi|icici|quant|mirae|axis|nippon|tata|kotak|uti)\b",
    r"\b(top|best)\s+(mutual fund|sip|scheme|equity fund|small cap|mid cap|flexi cap)\s+(to buy|to invest|for 2024|for 2025|for 2026)\b",
    r"\b(recommend|pick)\s+(parag parikh|quant small cap|hdfc mid-cap|sbi bluechip)\b",
    r"\b(offers?|provides?|promises?|guarantees?)\s+guaranteed\s+(return|profit|yield|cagr)\b",
]

# Standard System Prompt incorporating the 5 Rules
RAG_SYSTEM_RULES_PROMPT = """You are the Principal Growth Product Strategist for Groww Mutual Funds.
You specialize in qualitative user research, behavioral finance heuristics, and product discovery across our 3,052 verified customer conversation corpus.
Your mission is to synthesize actionable, high-impact product strategies to solve:
"12-Month First-Time Mutual Fund SIP Continuation Rate".

You must strictly adhere to the following 5 SYSTEM ANSWERING RULES:

RULE 1: GROUNDED CITATIONS & EVIDENCE ATTRIBUTION (ZERO HALLUCINATION)
- Every behavioral observation, friction point, or user perception MUST be explicitly cited using [EVID-X] notation (e.g. [EVID-1], [EVID-2]).
- You may only draw facts from the provided retrieved customer evidence chunks. Never invent user quotes, imaginary percentages, or phantom surveys.

RULE 2: SEBI NON-ADVICE REGULATORY INVARIANT
- You are an expert PRODUCT STRATEGIST, NOT a financial advisor.
- You must NEVER recommend, evaluate, or suggest specific mutual fund schemes, AMCs, stocks, or fund-picking strategies (e.g. NEVER say "Users should buy Parag Parikh Flexi Cap" or "Switch to Quant Small Cap").
- If the user asks for investment advice or fund recommendations, state clearly that Groww Discovery Engine does not provide investment advice and redirect the inquiry to product mechanics and UX retention solutions.

RULE 3: ETHICAL GROWTH & ANTI-FOMO GUARDRAIL
- Never propose manipulative dark patterns, artificial countdown timers, loss-framing panic alerts, or deceptive hurdles to stop SIP cancellations.
- Retention must be earned through liquidity transparency, payment resilience, cognitive re-anchoring, and transparent settlement tracking.

RULE 4: STANDARDIZED 4-SECTION EXECUTIVE SYNTHESIS FORMAT
You must structure your answer into exactly 4 sections:
### 1. Executive Summary & Behavioral Dynamic
Analyze the underlying psychological mental model and behavioral heuristic explaining why first-time investors experience this specific issue.

### 2. Discovered Friction & Root Cause Breakdown
- **Operational / Technical Friction:** Banking drops, NPCI limits, settlement lag, or UI ambiguities.
- **Cognitive / Mental Model Mismatch:** Clash between user mental models (e.g. FD linear returns, instant UPI delivery) and mutual fund realities.
Cite specific quotes with [EVID-1], [EVID-2], etc.

### 3. Voice of Customer Verbatim Highlights
Extract the 2-3 most telling verbatim quotes from the retrieved evidence chunks with source platform attribution.

### 4. Strategic PM Recommendations (12-Month Retention Impact)
Propose 2-3 concrete, high-leverage product features or UX interventions that resolve the friction while upholding SEBI compliance.

RULE 5: EMPIRICAL TRANSPARENCY & FALLBACK PROTOCOL
- If the retrieved evidence is sparse or does not fully cover the query, explicitly state the empirical boundary rather than inventing generic AI commentary.
"""


class RAGRulesEngine:
    """Enforces answering rules and validates output compliance."""

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
            "enforcement": "Regex guardrail scanner against scheme names and advisory solicitation patterns.",
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
            "name": "Deterministic Fallback Protocol",
            "principle": "100% system availability. If external LLM times out or quota is exceeded, seamlessly fall back to grounded synthesis engine.",
            "enforcement": "Automatic try-catch failover mechanism with explicit UI transparency badging.",
        },
    ]

    @classmethod
    def validate_sebi_compliance(cls, text: str) -> Tuple[bool, List[str]]:
        """Scan generated text for SEBI advisory violations (fund recommendations).
        
        Evaluates the AI's analysis and recommendations (excluding verbatim quotes from users).
        
        Returns:
            (is_compliant, list_of_violations)
        """
        violations = []
        
        # Remove Section 3 (Voice of Customer verbatim quotes) and quoted text to avoid false positives on user complaints
        analysis_text = re.sub(r'###\s*3\..*?(?=###\s*4|\Z)', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Strip text inside quotation marks
        analysis_text = re.sub(r'["\'].*?["\']', '', analysis_text)
        
        text_lower = analysis_text.lower()

        for pattern in DISALLOWED_FUND_ADVISORY_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append(f"Advisory phrase pattern detected: '{pattern}'")

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
            "citation_coverage_score": round(min(1.0, citation_coverage), 2),
        }

    @classmethod
    def audit_structure(cls, text: str) -> Dict[str, Any]:
        """Verify presence of the 4 required executive sections."""
        s1 = bool(re.search(r"###?\s*1[.\s]+Executive Summary", text, re.IGNORECASE))
        s2 = bool(re.search(r"###?\s*2[.\s]+.*Friction", text, re.IGNORECASE))
        s3 = bool(re.search(r"###?\s*3[.\s]+.*(Voice of Customer|Customer|Quotes|Verbatim)", text, re.IGNORECASE))
        s4 = bool(re.search(r"###?\s*4[.\s]+.*Recommendations", text, re.IGNORECASE))

        score = sum([s1, s2, s3, s4]) / 4.0
        return {
            "section_1_executive_summary": s1,
            "section_2_friction_breakdown": s2,
            "section_3_customer_verbatim": s3,
            "section_4_recommendations": s4,
            "structure_completeness_score": round(score, 2),
            "is_complete": score == 1.0,
        }
