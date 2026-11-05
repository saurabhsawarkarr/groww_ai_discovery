"""Opportunity Ranker implementing the 5-Pillar Qualitative Comparison Rubric.

Evaluates and ranks behavioral opportunities across Prevalence, User Impact,
12-Month Business Relevance, Evidence Quality, and Product Addressability adhering
to Problem Statement §10 and Architecture Specification 3.5.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("groww_discovery.hypotheses.ranker")

# Aspirational weights defined in Architecture Specification 3.5
DEFAULT_WEIGHTS = {
    "prevalence": 0.20,
    "user_impact": 0.25,
    "relevance_12m": 0.25,
    "evidence_quality": 0.15,
    "product_addressability": 0.15,
}


class OpportunityRanker:
    """Ranks discovery opportunity spaces using transparent 5-pillar qualitative & quantitative evidence."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def evaluate_opportunity(
        self,
        theme: Dict[str, Any],
        hypotheses: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Evaluate a thematic cluster across the 5 qualitative pillars.

        Returns:
            Structured Opportunity Card with qualitative assessments, evidence rationales,
            defensible pillar scores (1-5), and overall weighted priority score.
        """
        cluster_id = theme["cluster_id"]
        title = theme.get("title", "")
        desc = theme.get("description", "")
        item_count = theme.get("item_count", 0)
        prevalence = theme.get("dataset_prevalence_pct")
        if prevalence is None or prevalence == 0.0:
            total_recs = theme.get("total_qualified_records", 155)
            prevalence = round((item_count / total_recs) * 100, 2) if total_recs > 0 else 0.0

        uvr = theme.get("unique_voice_ratio")
        if uvr is None:
            distinct = theme.get("distinct_authors_count", item_count)
            uvr = round(distinct / item_count, 4) if item_count > 0 else 1.0

        dispersion = theme.get("cross_source_dispersion")
        if dispersion is None or dispersion == 0.0:
            from src.clustering.synthesizer import compute_entropy
            dispersion = compute_entropy(theme.get("source_distribution", {}))

        counter_quotes = theme.get("counter_evidence_quotes", [])
        if isinstance(counter_quotes, str):
            try:
                counter_quotes = json.loads(counter_quotes)
            except Exception:
                counter_quotes = []
        combined_text = (title + " " + desc).lower()

        # -------------------------------------------------------------
        # Pillar 1: Prevalence (Dataset frequency & unique voices)
        # -------------------------------------------------------------
        if prevalence >= 20.0:
            p_tier, p_score = "Very High", 5.0
            p_desc = f"Dominant pattern comprising {prevalence}% of qualified dataset across {uvr * 100:.0f}% unique voices."
        elif prevalence >= 10.0:
            p_tier, p_score = "High", 4.0
            p_desc = f"Substantial representation ({prevalence}% prevalence) with healthy author diversity."
        elif prevalence >= 4.0:
            p_tier, p_score = "Moderate", 3.0
            p_desc = f"Measurable recurring pattern ({prevalence}% prevalence) corroborated across multiple users."
        else:
            p_tier, p_score = "Focused", 2.0
            p_desc = f"Niche or emergent signal ({prevalence}% prevalence) observed in specific cohorts."

        # -------------------------------------------------------------
        # Pillar 2: User Impact Severity (Anxiety, frustration, churn)
        # -------------------------------------------------------------
        if any(w in combined_text for w in ["loss", "negative", "xirr", "panic", "terrifying"]):
            i_tier, i_score = "Critical", 5.0
            i_desc = "Severe psychological anxiety regarding perceived permanent capital erosion during early investing."
        elif any(w in combined_text for w in ["failed", "pending", "bounce", "mandate", "deduct"]):
            i_tier, i_score = "High", 4.5
            i_desc = "Direct operational disruption; silent deduction failures trigger fear of penalties and missed SIP dates."
        elif any(w in combined_text for w in ["pause", "stop", "cancel", "hidden", "exit load"]):
            i_tier, i_score = "High", 4.0
            i_desc = "High friction in liquidity management forcing permanent cancellation over temporary pausing."
        elif any(w in combined_text for w in ["step up", "accumulat", "discipline"]):
            i_tier, i_score = "Positive Impact", 4.0
            i_desc = "High empowering impact; active habit formation and confidence through counter-cyclical investing."
        else:
            i_tier, i_score = "Moderate", 3.0
            i_desc = "Moderate friction or procedural confusion during routine account monitoring."

        # -------------------------------------------------------------
        # Pillar 3: Business Relevance to 12M SIP Continuation
        # -------------------------------------------------------------
        if any(w in combined_text for w in ["stop", "cancel", "dropout", "churn", "mandate", "failed"]):
            r_tier, r_score = "Direct Causal Driver", 5.0
            r_desc = "Direct, unmediated connection to SIP abandonment and premature mandate termination in Year 1."
        elif any(w in combined_text for w in ["negative", "xirr", "drawdown", "pause"]):
            r_tier, r_score = "High Causal Risk", 4.5
            r_desc = "Key behavioral bottleneck leading to voluntary cancellation within months 1 to 3."
        elif any(w in combined_text for w in ["step up", "12 month", "discipline"]):
            r_tier, r_score = "Retention Engine", 4.5
            r_desc = "Core blueprint for achieving the 12-month milestone; represents desired target behavior."
        else:
            r_tier, r_score = "Indirect Contributor", 3.0
            r_desc = "Secondary influence on investor sentiment, moderately impacting long-term engagement."

        # -------------------------------------------------------------
        # Pillar 4: Evidence Quality & Diversity
        # -------------------------------------------------------------
        has_counter = len(counter_quotes) > 0
        if dispersion >= 0.70 and has_counter:
            q_tier, q_score = "Multi-Platform Robust", 5.0
            q_desc = f"Corroborated across Reddit/PlayStore/YouTube (dispersion {dispersion}) with {len(counter_quotes)} counter-examples."
        elif dispersion >= 0.40 or has_counter:
            q_tier, q_score = "Strong", 4.0
            q_desc = f"Cross-platform evidence (dispersion {dispersion}) grounded in verbatim user quotes."
        else:
            q_tier, q_score = "Platform Specific", 3.0
            q_desc = "Primarily observed on a single channel; requires multi-channel validation."

        # -------------------------------------------------------------
        # Pillar 5: Product Addressability via Groww UX
        # -------------------------------------------------------------
        if any(w in combined_text for w in ["pause", "toggle", "discover"]):
            a_tier, a_score = "Highly Addressable", 5.0
            a_desc = "Direct UX intervention: making SIP pause and date adjustment prominent in app navigation."
        elif any(w in combined_text for w in ["xirr", "negative", "drawdown"]):
            a_tier, a_score = "Highly Addressable", 4.5
            a_desc = "High product leverage: proactive contextual volatility coaching and XIRR vs profit tooltips."
        elif any(w in combined_text for w in ["autopay", "mandate", "notification", "pending"]):
            a_tier, a_score = "Substantially Addressable", 4.0
            a_desc = "Transparent status tracking and automated fallback retry via UPI AutoPay."
        elif any(w in combined_text for w in ["step up", "milestone"]):
            a_tier, a_score = "Addressable", 4.0
            a_desc = "Milestone celebration cards and automated annual step-up contribution prompts."
        else:
            a_tier, a_score = "Moderate", 3.0
            a_desc = "Partially addressable via in-app FAQ and automated status messaging."

        # -------------------------------------------------------------
        # Composite Weighted Scoring & Prioritization Tier
        # -------------------------------------------------------------
        composite_score = (
            self.weights["prevalence"] * p_score
            + self.weights["user_impact"] * i_score
            + self.weights["relevance_12m"] * r_score
            + self.weights["evidence_quality"] * q_score
            + self.weights["product_addressability"] * a_score
        )
        composite_score = round(composite_score, 2)

        if composite_score >= 4.30:
            priority_tier = "Tier 1: Immediate Research Priority"
        elif composite_score >= 3.60:
            priority_tier = "Tier 2: High Value Opportunity"
        else:
            priority_tier = "Tier 3: Secondary Investigation"

        return {
            "cluster_id": cluster_id,
            "title": title,
            "description": desc,
            "priority_score": composite_score,
            "priority_tier": priority_tier,
            "pillars": {
                "prevalence": {
                    "score": p_score,
                    "tier": p_tier,
                    "prevalence_pct": prevalence,
                    "rationale": p_desc,
                },
                "user_impact": {
                    "score": i_score,
                    "tier": i_tier,
                    "rationale": i_desc,
                },
                "business_relevance_12m": {
                    "score": r_score,
                    "tier": r_tier,
                    "rationale": r_desc,
                },
                "evidence_quality": {
                    "score": q_score,
                    "tier": q_tier,
                    "dispersion": dispersion,
                    "counter_evidence_count": len(counter_quotes),
                    "rationale": q_desc,
                },
                "product_addressability": {
                    "score": a_score,
                    "tier": a_tier,
                    "rationale": a_desc,
                },
            },
            "hypotheses_count": len(hypotheses) if hypotheses else 0,
        }

    def rank_opportunities(
        self,
        themes: List[Dict[str, Any]],
        hypotheses_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> List[Dict[str, Any]]:
        """Rank all discovery opportunity spaces by transparent 5-pillar composite score."""
        h_map = hypotheses_map or {}
        evaluated = []

        for theme in themes:
            cid = theme["cluster_id"]
            hyps = h_map.get(cid, [])
            card = self.evaluate_opportunity(theme, hyps)
            evaluated.append(card)

        # Sort descending by priority score
        evaluated.sort(key=lambda x: x["priority_score"], reverse=True)

        for rank, opp in enumerate(evaluated, 1):
            opp["rank"] = rank

        logger.info("Ranked %d discovery opportunity spaces", len(evaluated))
        return evaluated
