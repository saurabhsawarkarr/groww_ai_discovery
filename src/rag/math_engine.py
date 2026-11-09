"""Deterministic Domain Anchors & Number Verifier Engine.

Inspired by mission-critical financial RAG architectures:
"Never let the LLM do arithmetic. All numbers are computed or verified against ground truth."

Freezes regulatory, banking, and mathematical constants so the LLM cannot hallucinate
digits, interest rates, penalty amounts, or clearing cycles.
"""

import re
from typing import Any, Dict, List, Set, Tuple


# =============================================================================
# FROZEN DOMAIN CONSTANTS (IMMUTABLE REGULATORY & FINANCIAL ANCHORS)
# =============================================================================

FROZEN_DOMAIN_ANCHORS: Dict[str, Any] = {
    "NPCI_MANDATE_MAX_BUFFER": 100000,           # ₹1,00,000 regulatory authorization ceiling
    "BANK_ECS_BOUNCE_PENALTY_MIN": 450,         # ₹450 minimum bank bounce charge
    "BANK_ECS_BOUNCE_PENALTY_MAX": 590,         # ₹590 maximum bank bounce charge (with 18% GST)
    "CONSECUTIVE_REJECTION_THRESHOLD": 3,       # 3 strikes before mandatory mandate revocation
    "XIRR_30_DAY_EXAMPLE_LOSS": 30,             # ₹30 paper loss
    "XIRR_30_DAY_EXAMPLE_INSTALMENT": 1000,     # ₹1,000 initial instalment
    "XIRR_30_DAY_EXAMPLE_PERCENTAGE": -18.5,    # -18.5% annualized XIRR
    "PORTFOLIO_OVERLAP_MIN_PERCENT": 65,        # 65% underlying stock overlap
    "PORTFOLIO_OVERLAP_MAX_PERCENT": 75,        # 75% underlying stock overlap
    "EQUITY_SETTLEMENT_DAYS": 2,                # T+2 business days for equity NAV unit allotment
    "DEBT_SETTLEMENT_DAYS": 1,                  # T+1 business days for liquid/debt funds
    "NAV_CUTOFF_HOUR_EQUITY": 15,               # 3:00 PM equity NAV cut-off
    "NAV_CUTOFF_HOUR_DEBT": 14,                 # 2:00 PM liquid/debt NAV cut-off
    "SALARY_BUFFER_START_DAY": 5,               # 5th of the month
    "SALARY_BUFFER_END_DAY": 7,                 # 7th of the month
    "FIRST_YEAR_RETENTION_HORIZON_MONTHS": 12,  # 12-month retention milestone
    "CORPUS_SIZE": 3052,                        # 3,052 verified customer conversations
}


class DeterministicMathEngine:
    """Verifies that all numerical values, rupee amounts, and percentages cited in
    synthesized answers match verified empirical evidence or frozen domain constants.
    """

    @classmethod
    def get_frozen_anchors_xml(cls) -> str:
        """Serialize frozen domain anchors into structured XML for prompt injection."""
        return (
            "<frozen_domain_anchors>\n"
            f"  <anchor name=\"NPCI_MANDATE_LIMIT\">₹1,00,000 regulatory authorization buffer</anchor>\n"
            f"  <anchor name=\"BANK_ECS_BOUNCE_PENALTY\">₹450 to ₹590 per missed debit (with GST)</anchor>\n"
            f"  <anchor name=\"MANDATE_TERMINATION_STRIKES\">3 consecutive partner bank rejections</anchor>\n"
            f"  <anchor name=\"XIRR_DISTORTION_EXAMPLE\">₹30 dip on ₹1,000 in 30 days displays as -18.5% XIRR</anchor>\n"
            f"  <anchor name=\"PORTFOLIO_OVERLAP_RANGE\">65% to 75% identical stocks between Large Cap & Flexi Cap</anchor>\n"
            f"  <anchor name=\"EQUITY_NAV_SETTLEMENT\">T+2 business days for unit allotment</anchor>\n"
            f"  <anchor name=\"DEBT_NAV_SETTLEMENT\">T+1 business days</anchor>\n"
            f"  <anchor name=\"SALARY_BUFFER_WINDOW\">5th to 7th of the month</anchor>\n"
            f"  <anchor name=\"CORPUS_SIZE\">3,052 verified customer conversations</anchor>\n"
            "</frozen_domain_anchors>"
        )

    @classmethod
    def extract_numbers_from_text(cls, text: str) -> List[str]:
        """Extract all numbers, rupee values, and percentages from text."""
        # Find ₹ amounts, percentages, and standalone numbers
        raw_tokens = re.findall(r"(?:₹\s*[\d,]+(?:\.\d+)?|[\+\-]?\d+(?:\.\d+)?%|\b\d+(?:,\d+)*(?:\.\d+)?\b)", text)
        cleaned = []
        for tok in raw_tokens:
            c = tok.replace("₹", "").replace("%", "").replace(",", "").strip()
            try:
                # normalize to string representation of float or int
                val = float(c)
                if val.is_integer():
                    cleaned.append(str(int(val)))
                else:
                    cleaned.append(str(val))
            except ValueError:
                continue
        return cleaned

    @classmethod
    def build_allowed_number_set(cls, retrieved_evidence: List[Dict[str, Any]]) -> Set[str]:
        """Build the universe of allowable numbers from evidence chunks and frozen anchors."""
        allowed: Set[str] = set()

        # Add all frozen domain constants
        for val in FROZEN_DOMAIN_ANCHORS.values():
            if isinstance(val, (int, float)):
                if float(val).is_integer():
                    allowed.add(str(int(val)))
                    allowed.add(str(abs(int(val))))
                else:
                    allowed.add(str(val))
                    allowed.add(str(abs(val)))

        # Also add common small integer structural numbers (1, 2, 3, 4, 5, 10, 30, 48, 90, 180, 365)
        for structural_num in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 24, 30, 48, 60, 90, 100, 180, 365, 2500]:
            allowed.add(str(structural_num))

        # Extract all numbers from retrieved evidence quotes
        for item in retrieved_evidence:
            quote = item.get("quote", "") + " " + item.get("text", "")
            for num in cls.extract_numbers_from_text(quote):
                allowed.add(num)

        return allowed

    @classmethod
    def verify_numbers(
        cls, synthesis: str, retrieved_evidence: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str], float]:
        """Verify that numbers cited in the synthesized text are grounded.

        Returns:
            (is_clean, ungrounded_numbers_list, numerical_precision_score)
        """
        cited_numbers = cls.extract_numbers_from_text(synthesis)
        if not cited_numbers:
            return True, [], 1.0

        allowed = cls.build_allowed_number_set(retrieved_evidence)
        ungrounded = [n for n in cited_numbers if n not in allowed]

        precision = (len(cited_numbers) - len(ungrounded)) / len(cited_numbers) if cited_numbers else 1.0
        is_clean = len(ungrounded) == 0

        return is_clean, ungrounded, round(precision, 3)
