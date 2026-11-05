"""Prompt engineering and structured context assembly for Qualitative RAG.

Enforces:
1. Strict SEBI Non-Advice Guardrails (no specific fund recommendations).
2. Non-FOMO Guardrails (no urgency, countdowns, or manipulative nudges).
3. Verbatim customer quote citations using [EVID-X] format.
"""

from typing import Any, Dict, List


SEBI_SYSTEM_INSTRUCTIONS = """You are the Principal Growth Product Strategist for Groww Mutual Funds.
You specialize in qualitative user research, behavioral finance heuristics, and product discovery.
Your mission is to analyze customer feedback and synthesize actionable product strategies to improve:
"12-Month First-Time Mutual Fund SIP Continuation Rate".

STRICT EPISTEMIC & REGULATORY INVARIANTS:
1. SEBI COMPLIANCE: NEVER recommend specific mutual funds, AMC schemes, or stocks (no fund picking).
2. ETHICAL PRODUCT NUDGES: NEVER suggest artificial countdowns, FOMO, or fear-based messaging.
3. EMPIRICAL CITATIONS: Every claim about user friction or behavior MUST be substantiated with explicit citations
   referencing the retrieved evidence chunks using [EVID-1], [EVID-2], etc.
4. ACTIONABLE PRODUCT FOCUS: Solutions must focus on UX clarity, payment infrastructure resilience,
   transparent settlement tracking, and cognitive de-biasing.
"""


class RAGPromptBuilder:
    """Builds prompt contexts and messages for pluggable LLMs."""

    @staticmethod
    def build_evidence_context(retrieved_evidence: List[Dict[str, Any]]) -> str:
        """Format retrieved evidence records into numbered citation blocks."""
        if not retrieved_evidence:
            return "No matching customer evidence records found."

        chunks = []
        for idx, item in enumerate(retrieved_evidence, 1):
            plat = item.get("platform", "source").upper()
            date = item.get("published_at", "Recent")
            stage = item.get("journey_stage", "unknown").replace("_", " ").title()
            quote = item.get("quote", "").strip()
            theme = item.get("theme_id", "THEME-01")
            
            chunk = (
                f"--- [EVID-{idx}] ---\n"
                f"Platform: {plat} | Stage: {stage} | Date: {date} | Discovered Theme: {theme}\n"
                f"Verbatim Customer Discourse: \"{quote}\"\n"
            )
            chunks.append(chunk)

        return "\n".join(chunks)

    @classmethod
    def build_user_prompt(cls, query: str, retrieved_evidence: List[Dict[str, Any]]) -> str:
        """Construct the complete user prompt incorporating query and retrieved evidence."""
        context_str = cls.build_evidence_context(retrieved_evidence)
        
        prompt = f"""USER RESEARCH INQUIRY:
"{query}"

RETRIEVED EMPIRICAL EVIDENCE CHUNKS (Top {len(retrieved_evidence)}):
{context_str}

REQUIRED SYNTHESIS STRUCTURE:
Please synthesize a high-impact, executive-level qualitative analysis addressing the inquiry above based strictly on the retrieved customer evidence. Structure your response with the following markdown sections:

### 1. Executive Summary & Behavioral Dynamic
Synthesize the underlying investor psychology and user behavior demonstrated in the quotes. Explain why this happens to first-time investors.

### 2. Discovered Friction & Root Cause Breakdown
- **Operational / Technical Friction:** Breakdown of system drops, bank rejections, or delay ambiguities cited by users.
- **Cognitive / Mental Model Mismatch:** How user expectations clash with mutual fund realities (e.g. FD proxy, T+2 delay anxiety).
Cite specific evidence using [EVID-1], [EVID-2], etc.

### 3. Voice of Customer Verbatim Highlights
Highlight the 2-3 most compelling verbatim quotes from the retrieved evidence that reveal investor pain points.

### 4. Strategic PM Recommendations (12-Month Retention Impact)
Provide 2-3 concrete, high-leverage product features or UX ergonomics that resolve this friction without violating SEBI guidelines or using FOMO nudges.
"""
        return prompt

    @classmethod
    def get_messages(cls, query: str, retrieved_evidence: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Return chat-completion format messages."""
        return [
            {"role": "system", "content": SEBI_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": cls.build_user_prompt(query, retrieved_evidence)},
        ]

