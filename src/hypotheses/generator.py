"""Multi-perspective hypothesis generator formulating competing causal explanations.

Produces dual, falsifiable hypotheses (Hypothesis A vs Hypothesis B) for each emergent
behavioral theme, highlighting missing evidence, continuation links, and primary interview questions.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

from src.database.connection import get_connection, get_db_path

logger = logging.getLogger("groww_discovery.hypotheses.generator")


class HypothesisGenerator:
    """Generates competing falsifiable hypotheses and research questions for thematic clusters."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = get_db_path(db_path)

    def generate_hypotheses_for_theme(
        self, theme: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Formulate at least 2 competing, falsifiable hypotheses for a thematic cluster.

        Args:
            theme: Dictionary representing a thematic cluster from thematic_clusters table.

        Returns:
            List of at least 2 hypothesis dictionaries ready for hypothesis_records insertion.
        """
        cluster_id = theme["cluster_id"]
        title = theme.get("title", "")
        desc = theme.get("description", "")
        item_count = theme.get("item_count", 0)
        quotes = theme.get("representative_quotes", [])
        combined_text = (title + " " + desc).lower()

        # 1. Early Drawdown / Negative XIRR Theme
        if any(w in combined_text for w in ["xirr", "negative", "loss", "drawdown", "red"]):
            hyp_a = {
                "hypothesis_id": f"hyp_{cluster_id}_A",
                "cluster_id": cluster_id,
                "perspective": "Hypothesis A: Loss Aversion & Psychological Churn",
                "observed_pattern": (
                    f"First-time investors checking portfolios within months 1–3 exhibit acute panic "
                    f"when encountering negative XIRR, actively contemplating pausing or terminating recurring SIPs."
                ),
                "hypothesis_text": (
                    "Users misinterpret early negative XIRR as direct permanent capital loss rather than temporary "
                    "volatility, triggering voluntary autopay cancellation due to loss aversion."
                ),
                "alternative_explanation": (
                    "Users check portfolio balances out of routine novelty and seek clarification online out of curiosity, "
                    "with no genuine intent to stop recurring contributions unless market decline exceeds 15%."
                ),
                "missing_evidence": (
                    "Unstated in public commentary: whether users who complained actually stopped their autopay in the app, "
                    "or if they continued investing after seeking reassurance."
                ),
                "connection_to_continuation": (
                    "Directly causes premature SIP attrition in months 1 to 3 before compounding benefits can materialize, "
                    "preventing investors from reaching the 12-month milestone."
                ),
                "validation_approach": "1:1 Semi-Structured User Interviews + Quantitative Cancellation Telemetry Analysis",
                "confidence_and_limitations": "High qualitative signal from multi-platform commentary, but lacks backend cancellation logs.",
                "research_questions": [
                    "Walk me through the last time you opened Groww and saw your portfolio returns in red. What went through your mind?",
                    "What did you expect your return or XIRR number to show during your first 90 days of investing?",
                    "Did you discuss the negative returns with anyone or seek advice online? What did you end up doing with your SIP?",
                    "What would make you feel comfortable letting your monthly investment run even when the market is falling?",
                ],
                "priority_score": 8.5,
            }

            hyp_b = {
                "hypothesis_id": f"hyp_{cluster_id}_B",
                "cluster_id": cluster_id,
                "perspective": "Hypothesis B: Metrics Confusion & Educational Gap",
                "observed_pattern": (
                    f"Investors report confusion over the discrepancy between absolute returns and XIRR, "
                    f"searching external forums for mathematical clarification."
                ),
                "hypothesis_text": (
                    "Users do not understand the annualized nature of XIRR calculations for multi-instalment cash flows, "
                    "leading to app mistrust and perceived calculation inaccuracy rather than market panic."
                ),
                "alternative_explanation": (
                    "Users fully understand equity risk but find Groww's visual dashboard presentation of XIRR "
                    "confusing compared to simple total invested vs current value."
                ),
                "missing_evidence": (
                    "Actual financial literacy background of users and whether contextual tooltips in the UI are viewed."
                ),
                "connection_to_continuation": (
                    "Undermines platform credibility; users may switch to competing brokers or traditional FDs "
                    "believing the platform is miscalculating their gains."
                ),
                "validation_approach": "Usability Testing with Prototype Dashboard + In-App Comprehension Survey",
                "confidence_and_limitations": "Strongly supported by Reddit clarification threads, but user cohort financial background unverified.",
                "research_questions": [
                    "How would you explain what XIRR means to a friend who has never invested before?",
                    "When you look at your Groww portfolio screen, which specific numbers do you look at first and why?",
                    "Have you ever noticed a difference between your Total Profit and your XIRR percentage? How did you make sense of it?",
                ],
                "priority_score": 7.8,
            }
            return [hyp_a, hyp_b]

        # 2. Autopay Mandate Execution Failure Theme
        if any(w in combined_text for w in ["autopay", "mandate", "failed", "pending", "deduct"]):
            hyp_a = {
                "hypothesis_id": f"hyp_{cluster_id}_A",
                "cluster_id": cluster_id,
                "perspective": "Hypothesis A: Involuntary Bank Friction & Inadvertent Churn",
                "observed_pattern": (
                    f"Recurring SIP deductions fail silently or linger in 'pending' status due to bank/eNACH/NPCI "
                    f"sync failures, leading to missed instalments."
                ),
                "hypothesis_text": (
                    "Mandate deduction failures represent the primary cause of involuntary SIP dropout; users who miss "
                    "one instalment due to technical bank sync delays are 60% more likely to abandon the SIP entirely."
                ),
                "alternative_explanation": (
                    "Users intentionally maintain insufficient bank balances on deduction day because of salary delays, "
                    "using mandate failure as a passive pause mechanism."
                ),
                "missing_evidence": (
                    "Bank rejection codes (e.g., technical failure vs. insufficient funds) and customer support ticket logs."
                ),
                "connection_to_continuation": (
                    "Direct structural break in recurring habit formation; investors who experience a failed autopay "
                    "rarely re-authorize mandates manually."
                ),
                "validation_approach": "Bank Error Telemetry Audit + Customer Support Call Shadowing",
                "confidence_and_limitations": "Multi-platform corroboration across Play Store and Reddit, but bank balance records unavailable.",
                "research_questions": [
                    "Tell me about the last time an automated SIP instalment did not go through as scheduled. How did you find out?",
                    "What was your experience trying to resolve the failed deduction with customer support?",
                    "Were you worried about bank bounce charges or missed investment dates when the status showed pending?",
                    "How do you prefer to handle investments when your salary is delayed past your scheduled SIP date?",
                ],
                "priority_score": 8.8,
            }

            hyp_b = {
                "hypothesis_id": f"hyp_{cluster_id}_B",
                "cluster_id": cluster_id,
                "perspective": "Hypothesis B: Notification Asymmetry & Anxiety Amplification",
                "observed_pattern": (
                    f"Investors report bank SMS debits occurring hours or days before Groww updates portfolio status, "
                    f"creating fear of lost funds."
                ),
                "hypothesis_text": (
                    "The operational communication gap between bank debit and Groww unit allocation creates "
                    "severe anxiety, causing users to distrust the platform and cancel active mandates."
                ),
                "alternative_explanation": (
                    "Users understand mutual fund NAV settlement takes T+1/T+2 days and are only frustrated by "
                    "lack of customer support responsiveness during market hours."
                ),
                "missing_evidence": (
                    "Average time taken for bank reconciliation notifications vs user expectation timelines."
                ),
                "connection_to_continuation": (
                    "Reduces platform trust, pushing first-time investors back to traditional bank-managed SIPs."
                ),
                "validation_approach": "Notification Funnel Timing Audit + User Perception Interviews",
                "confidence_and_limitations": "Frequent complaint in app reviews, but correlation with voluntary churn requires validation.",
                "research_questions": [
                    "Walk me through the timeline when your bank account gets debited: when do you expect to see units in your app?",
                    "What notifications or messages from Groww do you find most reassuring on your investment day?",
                    "Have you ever experienced a pending status for more than 24 hours? What action did you take?",
                ],
                "priority_score": 7.4,
            }
            return [hyp_a, hyp_b]

        # 3. SIP Pausing Discoverability Deficit Theme
        if any(w in combined_text for w in ["pause", "stop", "cancel", "temporary"]):
            hyp_a = {
                "hypothesis_id": f"hyp_{cluster_id}_A",
                "cluster_id": cluster_id,
                "perspective": "Hypothesis A: Pause Discoverability Deficit Inducing Full Churn",
                "observed_pattern": (
                    f"Investors needing temporary 1 to 2 month contribution halts due to liquidity needs "
                    f"resort to permanent cancellation because pausing controls are hidden."
                ),
                "hypothesis_text": (
                    "A majority of voluntary cancellations are unintended permanent terminations caused by the "
                    "low discoverability of temporary SIP pause options in the app UI."
                ),
                "alternative_explanation": (
                    "Users genuinely intend to exit mutual funds permanently due to life events, and would cancel "
                    "even if the pause toggle were prominently displayed."
                ),
                "missing_evidence": (
                    "Clickstream data on SIP management screen and user navigation paths prior to cancellation."
                ),
                "connection_to_continuation": (
                    "High-leverage product intervention: surfacing pause controls could directly retain 20–30% "
                    "of churned investors who resume contributions after 1–2 months."
                ),
                "validation_approach": "A/B Testing of Visible Pause Toggle + Churned User Exit Interviews",
                "confidence_and_limitations": "Clear review quotes citing missing pause option, but overall cancellation intent distribution unquantified.",
                "research_questions": [
                    "When you needed to pause or stop your SIP, walk me through how you searched for that option in the app.",
                    "If you had the option to pause your SIP for 2 months without any penalty, would you have chosen that instead of cancelling?",
                    "What was the specific financial situation that led you to want to pause your monthly contribution?",
                ],
                "priority_score": 8.2,
            }

            hyp_b = {
                "hypothesis_id": f"hyp_{cluster_id}_B",
                "cluster_id": cluster_id,
                "perspective": "Hypothesis B: Exit Load & Liquidity Anxiety",
                "observed_pattern": (
                    f"Conservative investors express surprise and concern regarding hidden exit loads and "
                    f"capital redemption delays."
                ),
                "hypothesis_text": (
                    "Fear of lock-in and unexpected exit loads prevents first-time investors from staying committed "
                    "past month 3, prompting premature total fund redemption."
                ),
                "alternative_explanation": (
                    "Users understand exit loads but cancel because their monthly cash flow stability deteriorated."
                ),
                "missing_evidence": (
                    "Income stability of the cohort and whether exit loads were actually deducted upon redemption."
                ),
                "connection_to_continuation": (
                    "Direct barrier to reaching 12 months; users redeem full capital early to ensure liquidity."
                ),
                "validation_approach": "Exit Survey Analysis + User Financial Fragility Interviews",
                "confidence_and_limitations": "Observed in conservative 1-star reviews, but prevalence across moderate investors uncertain.",
                "research_questions": [
                    "When you first invested, what was your understanding of when and how you could take your money out?",
                    "Did you encounter any exit loads or charges when stopping? How did that affect your trust in mutual funds?",
                    "How important was immediate access to emergency cash in your decision to cancel the SIP?",
                ],
                "priority_score": 7.0,
            }
            return [hyp_a, hyp_b]

        # 4. Disciplined Counter-Cyclical Accumulation Theme
        if any(w in combined_text for w in ["step up", "12 month", "discipline", "accumulat", "continuing"]):
            hyp_a = {
                "hypothesis_id": f"hyp_{cluster_id}_A",
                "cluster_id": cluster_id,
                "perspective": "Hypothesis A: Milestone Feedback & Reinvestment Momentum",
                "observed_pattern": (
                    f"Investors achieving 6 to 12 months of disciplined SIP contributions demonstrate high conviction "
                    f"and proactively increase instalment amounts during market dips."
                ),
                "hypothesis_text": (
                    "Celebrating contribution milestones (e.g., 6 months uninterrupted autopay) creates psychological "
                    "momentum that converts passive investors into active counter-cyclical compounders."
                ),
                "alternative_explanation": (
                    "These investors possess pre-existing high financial literacy and higher disposable incomes, "
                    "making their continuation independent of platform reinforcement."
                ),
                "missing_evidence": (
                    "Socio-economic profile and prior equity investing experience of this disciplined cohort."
                ),
                "connection_to_continuation": (
                    "Blueprint for success: identifying the habits of 12-month completers allows Groww to guide "
                    "at-risk beginners toward the same behavioral milestones."
                ),
                "validation_approach": "Cohort Comparison Study (12M Completers vs 3M Dropouts) + User Interviews",
                "confidence_and_limitations": "Rich qualitative narratives on Reddit, but potential survivor bias in voluntary forum posts.",
                "research_questions": [
                    "What helped you stay disciplined and keep your autopay running during months when returns were negative?",
                    "What prompted you to step up or increase your monthly investment amount? How did you decide on the increase?",
                    "How did reaching your 12-month milestone change how you think about long-term wealth building?",
                ],
                "priority_score": 8.0,
            }

            hyp_b = {
                "hypothesis_id": f"hyp_{cluster_id}_B",
                "cluster_id": cluster_id,
                "perspective": "Hypothesis B: Automated Hands-Off Habit Formation",
                "observed_pattern": (
                    f"Long-term continuing investors deliberately refrain from checking daily portfolio balances, "
                    f"relying strictly on hands-off autopay."
                ),
                "hypothesis_text": (
                    "Low dashboard engagement and 'set-and-forget' behavior correlates with higher 12-month retention, "
                    "whereas frequent daily balance monitoring increases anxiety and churn risk."
                ),
                "alternative_explanation": (
                    "Frequent checkers are simply more engaged users who are equally likely to continue if returns are positive."
                ),
                "missing_evidence": (
                    "App session frequency data correlated with voluntary SIP cancellation rates."
                ),
                "connection_to_continuation": (
                    "Could revolutionize growth engagement strategy: shifting from vanity daily active metrics to "
                    "promoting healthy long-term automated investing habits."
                ),
                "validation_approach": "Telemetry Correlation Analysis (Session Frequency vs 12M Churn Rate)",
                "confidence_and_limitations": "Evidenced by quotes from patient investors, needs quantitative telemetry validation.",
                "research_questions": [
                    "How often do you check your Groww app in a typical week or month?",
                    "Do you have notifications turned on for daily portfolio changes? How do those notifications make you feel?",
                    "What advice would you give to a friend who is obsessively checking their portfolio every day?",
                ],
                "priority_score": 8.6,
            }
            return [hyp_a, hyp_b]

        # 5. Generic Emergent Behavioral Theme Fallback
        hyp_a = {
            "hypothesis_id": f"hyp_{cluster_id}_A",
            "cluster_id": cluster_id,
            "perspective": "Hypothesis A: Operational Friction Driving Attrition",
            "observed_pattern": f"Recurring behavioral observations in {title} comprising {item_count} records.",
            "hypothesis_text": f"Operational friction in {title} degrades investor confidence, directly contributing to early SIP dropouts.",
            "alternative_explanation": f"The pattern in {title} represents transient cosmetic dissatisfaction without altering underlying contribution habits.",
            "missing_evidence": "User session replay data and post-interaction churn telemetry.",
            "connection_to_continuation": "Accumulated micro-frictions create inertia against renewing or continuing recurring autopay.",
            "validation_approach": "1:1 User Interviews + In-App Workflow Usability Testing",
            "confidence_and_limitations": f"Grounded in {item_count} empirical records, but long-term longitudinal causality unmeasured.",
            "research_questions": [
                f"Walk me through your experience regarding {title}.",
                "What did you expect to happen, and how did the app respond?",
                "How did this interaction affect your willingness to keep investing every month?",
            ],
            "priority_score": 7.0,
        }

        hyp_b = {
            "hypothesis_id": f"hyp_{cluster_id}_B",
            "cluster_id": cluster_id,
            "perspective": "Hypothesis B: Expectation Mismatch vs External Reality",
            "observed_pattern": f"Investors reporting unexpected friction during {title}.",
            "hypothesis_text": f"The root cause of friction in {title} stems from mismatched consumer expectations formed by instant UPI e-commerce apps.",
            "alternative_explanation": f"The friction is caused by banking and clearing house settlement infrastructure beyond app control.",
            "missing_evidence": "User expectations baseline measured at the point of onboarding.",
            "connection_to_continuation": "Setting transparent expectation timelines at onboarding could neutralize the friction.",
            "validation_approach": "Expectation Survey at Day 1 vs Day 30 + Concept Testing",
            "confidence_and_limitations": "Logical hypothesis supported by review tone, requires primary field testing.",
            "research_questions": [
                "What expectations did you have before starting this workflow on Groww?",
                "How does this experience compare to other financial apps you use regularly?",
                "What communication would have helped prevent confusion in this situation?",
            ],
            "priority_score": 6.8,
        }
        return [hyp_a, hyp_b]

    def persist_hypotheses(
        self, hypotheses: List[Dict[str, Any]]
    ) -> List[str]:
        """Save generated hypotheses into the SQLite hypothesis_records table."""
        conn = get_connection(self.db_path)
        inserted_ids = []
        try:
            now_utc = datetime.now(timezone.utc)
            for h in hypotheses:
                hid = h["hypothesis_id"]
                conn.execute(
                    """
                    INSERT OR REPLACE INTO hypothesis_records (
                        hypothesis_id,
                        cluster_id,
                        observed_pattern,
                        hypothesis_text,
                        alternative_explanation,
                        missing_evidence,
                        connection_to_continuation,
                        validation_approach,
                        research_questions,
                        priority_score,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        hid,
                        h["cluster_id"],
                        h["observed_pattern"],
                        h["hypothesis_text"],
                        h["alternative_explanation"],
                        h["missing_evidence"],
                        h["connection_to_continuation"],
                        h["validation_approach"],
                        json.dumps(h["research_questions"]),
                        float(h.get("priority_score", 0.0)),
                        now_utc,
                    ),
                )
                inserted_ids.append(hid)
            conn.commit()
            logger.info("Persisted %d hypothesis records to SQLite", len(inserted_ids))
            return inserted_ids
        finally:
            conn.close()

    def get_hypotheses_from_db(
        self, cluster_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve stored hypothesis records from SQLite."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            if cluster_id:
                cursor.execute(
                    """
                    SELECT hypothesis_id, cluster_id, observed_pattern, hypothesis_text,
                           alternative_explanation, missing_evidence, connection_to_continuation,
                           validation_approach, research_questions, priority_score, created_at
                    FROM hypothesis_records
                    WHERE cluster_id = ?
                    ORDER BY priority_score DESC;
                    """,
                    (cluster_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT hypothesis_id, cluster_id, observed_pattern, hypothesis_text,
                           alternative_explanation, missing_evidence, connection_to_continuation,
                           validation_approach, research_questions, priority_score, created_at
                    FROM hypothesis_records
                    ORDER BY priority_score DESC;
                    """
                )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                r = dict(row)
                r["research_questions"] = json.loads(r["research_questions"])
                results.append(r)
            return results
        finally:
            conn.close()
