"""Targeted Primary Research Interview Guide Generator.

Constructs non-leading, debiased qualitative interview protocols for 1:1 user sessions
to validate or falsify competing hypotheses regarding first-year SIP continuation.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("groww_discovery.hypotheses.interview_guides")


class InterviewGuideSynthesizer:
    """Synthesizes structured, non-leading user interview guides for discovery opportunities."""

    def generate_guide(
        self,
        cluster_id: str,
        theme_title: str,
        observed_pattern: str,
        hypothesis_a: str,
        hypothesis_b: str,
        core_questions: List[str],
        target_segment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Produce an operational, multi-stage 1:1 user interview protocol."""
        segment = target_segment or self._infer_target_segment(theme_title, observed_pattern)

        # Standard qualitative interview structure
        warmup = [
            "Tell me a little about when you first started thinking about investing in mutual funds.",
            "How did you decide on the monthly instalment amount for your initial SIP?",
            "What did you hope or expect mutual fund investing would do for you over the next 1 to 2 years?",
        ]

        # Alternative explanation debiasing probes
        debiasing_probes = [
            f"Some investors tell us: '{hypothesis_a[:120]}...'. Have you felt that way, or has your experience been different?",
            f"Other investors tell us: '{hypothesis_b[:120]}...'. Does that resonate with your situation at all?",
            "Can you recall a time when you saw or experienced this, but chose NOT to change or cancel your SIP? What kept you going?",
        ]

        wrapup = [
            "If you could wave a magic wand and change one thing about how your monthly SIP runs or shows information, what would it be?",
            "Is there anything else about managing your investments this past year that surprised or confused you?",
        ]

        return {
            "cluster_id": cluster_id,
            "theme_title": theme_title,
            "target_participant_screener": segment,
            "session_duration_minutes": 45,
            "interview_phases": {
                "1_warmup_and_context": warmup,
                "2_core_behavioral_inquiries": core_questions,
                "3_competing_hypotheses_probes": debiasing_probes,
                "4_wrap_up_and_ideal_state": wrapup,
            },
            "facilitator_notes": [
                "Do NOT explain XIRR, CAGR, or mandate mechanics during the session. Observe user language.",
                "Probe for specific retrospectives: 'Walk me through the last time...' rather than hypothetical answers.",
                "Look for behavioral workarounds (e.g. checking bank SMS, asking friends, watching YouTube).",
            ],
        }

    def _infer_target_segment(self, title: str, pattern: str) -> str:
        """Infer specific recruiting criteria based on the behavioral theme."""
        combined = (title + " " + pattern).lower()

        if any(w in combined for w in ["xirr", "negative", "loss", "red", "drawdown"]):
            return (
                "First-time mutual fund investors (tenure 1–6 months) who have experienced a negative "
                "portfolio return or monthly decline on Groww."
            )
        if any(w in combined for w in ["autopay", "mandate", "failed", "pending", "deduct"]):
            return (
                "Investors whose recurring SIP autopay instalment failed, delayed, or showed pending "
                "status within the past 90 days."
            )
        if any(w in combined for w in ["pause", "stop", "cancel"]):
            return (
                "Users who paused or cancelled a recurring mutual fund SIP within months 2 to 9 of starting."
            )
        if any(w in combined for w in ["kyc", "onboard", "start"]):
            return (
                "New Groww users who completed digital KYC within the past 30 days and initiated their first micro-SIP."
            )
        if any(w in combined for w in ["step up", "12 month", "discipline"]):
            return (
                "Disciplined investors who completed 9 to 12 consecutive months of SIP instalments without pause."
            )

        return "Active mutual fund SIP investors within their first 12 months of investing on Groww."
