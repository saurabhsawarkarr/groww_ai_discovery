"""Agreement metric calculation across the 7 evaluation dimensions.

Calculates exact and semantic agreement scores between LLM extractions and
human-labelled ground-truth benchmarks adhering to architecture specification 3.6.
"""

from collections import Counter
import re
from typing import Any, Dict, List, Optional, Tuple

from src.extraction.guardrails import validate_substring


def compute_token_f1(pred_text: Optional[str], gold_text: Optional[str]) -> float:
    """Compute token-level precision, recall, and F1 between two texts."""
    if not pred_text and not gold_text:
        return 1.0
    if not pred_text or not gold_text:
        return 0.0

    def tokenize(s: str) -> List[str]:
        return re.findall(r"\w+", s.lower())

    pred_tokens = tokenize(pred_text)
    gold_tokens = tokenize(gold_text)

    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0

    common = Counter(pred_tokens) & Counter(gold_tokens)
    overlap = sum(common.values())

    if overlap == 0:
        return 0.0

    precision = overlap / len(pred_tokens)
    recall = overlap / len(gold_tokens)
    return 2 * (precision * recall) / (precision + recall)


def compute_semantic_agreement(
    pred_behaviour: str,
    pred_friction: Optional[str],
    gold_behaviour: str,
    gold_friction: Optional[str],
    threshold: float = 0.50,
) -> float:
    """Compute semantic agreement score across behaviour and friction descriptions."""
    f1_behaviour = compute_token_f1(pred_behaviour, gold_behaviour)
    f1_friction = compute_token_f1(pred_friction, gold_friction)

    # Weighted combination: 60% behaviour, 40% friction
    if gold_friction is None and pred_friction is None:
        score = f1_behaviour
    else:
        score = (0.6 * f1_behaviour) + (0.4 * f1_friction)

    return score


class BenchmarkMetricsCalculator:
    """Calculates agreement scores across the 7 mandated evaluation dimensions."""

    def evaluate_item(
        self,
        raw_text: str,
        human_label: Dict[str, Any],
        model_output: Dict[str, Any],
    ) -> Dict[str, float]:
        """Compute the 7 agreement dimension scores for a single benchmark item.

        Returns:
            Dictionary with scores (0.0 to 1.0) for each dimension and overall average.
        """
        # 1. Relevance Agreement
        gold_rel = human_label.get("is_relevant", True)
        model_rel = model_output.get("is_relevant", True)
        m1_relevance = 1.0 if gold_rel == model_rel else 0.0

        # 2. Verbatim Quote Exactness
        quote = model_output.get("evidence_quote", "")
        m2_quote_exactness = 1.0 if validate_substring(raw_text, quote) else 0.0

        # 3. Behaviour & Friction Semantic Agreement
        m3_behaviour_friction = compute_semantic_agreement(
            pred_behaviour=model_output.get("reported_behaviour", ""),
            pred_friction=model_output.get("friction_or_concern"),
            gold_behaviour=human_label.get("reported_behaviour", ""),
            gold_friction=human_label.get("friction_or_concern"),
        )

        # 4. Journey Stage Accuracy (Exact enum match)
        gold_stage = human_label.get("journey_stage", "unknown")
        model_stage = model_output.get("journey_stage", "unknown")
        m4_journey_stage = 1.0 if gold_stage == model_stage else 0.0

        # 5. Workaround & Outcome Recall / Precision
        workaround_f1 = compute_token_f1(
            model_output.get("workaround"), human_label.get("workaround")
        )
        outcome_f1 = compute_token_f1(
            model_output.get("reported_outcome"), human_label.get("reported_outcome")
        )
        m5_workaround_outcome = (workaround_f1 + outcome_f1) / 2.0

        # 6. Zero-Hallucination Rate (verbatim quote verified + confidence score)
        # Penalizes quote failure heavily as hallucination
        m6_zero_hallucination = 1.0 if m2_quote_exactness == 1.0 else 0.0

        # 7. Source Traceability (100% requirement - raw_id linkage)
        gold_id = human_label.get("raw_id")
        model_id = model_output.get("source_id") or model_output.get("raw_id")
        m7_traceability = 1.0 if gold_id == model_id else 0.0

        overall_score = (
            m1_relevance
            + m2_quote_exactness
            + m3_behaviour_friction
            + m4_journey_stage
            + m5_workaround_outcome
            + m6_zero_hallucination
            + m7_traceability
        ) / 7.0

        return {
            "relevance_agreement": m1_relevance,
            "quote_exactness": m2_quote_exactness,
            "behaviour_friction_agreement": m3_behaviour_friction,
            "journey_stage_accuracy": m4_journey_stage,
            "workaround_outcome_agreement": m5_workaround_outcome,
            "zero_hallucination_rate": m6_zero_hallucination,
            "source_traceability": m7_traceability,
            "overall_agreement": round(overall_score, 4),
        }

    def aggregate_metrics(
        self, item_metrics: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """Compute mean percentage across all benchmark items for the 7 dimensions."""
        if not item_metrics:
            return {}

        keys = [
            "relevance_agreement",
            "quote_exactness",
            "behaviour_friction_agreement",
            "journey_stage_accuracy",
            "workaround_outcome_agreement",
            "zero_hallucination_rate",
            "source_traceability",
            "overall_agreement",
        ]

        summary = {}
        for k in keys:
            vals = [item[k] for item in item_metrics if k in item]
            summary[k] = round(sum(vals) / len(vals), 4) if vals else 0.0

        return summary
