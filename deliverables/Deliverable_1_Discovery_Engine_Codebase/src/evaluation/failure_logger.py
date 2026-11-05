"""AI Failure Logger for tracking, diagnosing, and remediating LLM extraction defects.

Maintains auditable records in the SQLite ai_failure_logs table for hallucinated quotes,
stage mismatches, unsupported teleological inferences, and relevance drift.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

from src.database.connection import get_connection, get_db_path
from src.extraction.guardrails import validate_substring

logger = logging.getLogger("groww_discovery.evaluation.failure_logger")


class AIFailureLogger:
    """Manages recording, auditing, and seeding of LLM extraction failure cases."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = get_db_path(db_path)

    def log_failure(
        self,
        failure_type: str,
        raw_input: str,
        erroneous_model_output: Union[str, Dict[str, Any]],
        ground_truth_correction: Union[str, Dict[str, Any]],
        remediation_applied: str,
        benchmark_id: Optional[str] = None,
        failure_id: Optional[str] = None,
    ) -> str:
        """Log a detected AI extraction defect into the ai_failure_logs table.

        Args:
            failure_type: Classification (e.g. stage_mismatch, hallucinated_quote, unsupported_inference)
            raw_input: Verbatim input text that triggered the failure
            erroneous_model_output: Model output string or JSON payload containing the error
            ground_truth_correction: Verified ground-truth correction or expected string
            remediation_applied: Prompt rule, guardrail, or code fix deployed to eliminate the defect
            benchmark_id: Optional reference to golden_set_benchmarks.benchmark_id
            failure_id: Optional custom ID; auto-generates if omitted

        Returns:
            The failure_id recorded in the database.
        """
        fid = failure_id or f"fail_{uuid.uuid4().hex[:12]}"
        err_str = (
            json.dumps(erroneous_model_output)
            if isinstance(erroneous_model_output, (dict, list))
            else str(erroneous_model_output)
        )
        gt_str = (
            json.dumps(ground_truth_correction)
            if isinstance(ground_truth_correction, (dict, list))
            else str(ground_truth_correction)
        )
        now_utc = datetime.now(timezone.utc)

        conn = get_connection(self.db_path)
        try:
            effective_bm_id = benchmark_id
            if effective_bm_id:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM golden_set_benchmarks WHERE benchmark_id = ?",
                    (effective_bm_id,),
                )
                if not cursor.fetchone():
                    effective_bm_id = None

            conn.execute(
                """
                INSERT OR REPLACE INTO ai_failure_logs (
                    failure_id,
                    benchmark_id,
                    failure_type,
                    raw_input,
                    erroneous_model_output,
                    ground_truth_correction,
                    remediation_applied,
                    logged_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    fid,
                    effective_bm_id,
                    failure_type,
                    raw_input,
                    err_str,
                    gt_str,
                    remediation_applied,
                    now_utc,
                ),
            )
            conn.commit()
            logger.info("Logged AI failure [%s] ID=%s for benchmark=%s", failure_type, fid, effective_bm_id)
            return fid
        finally:
            conn.close()

    def detect_and_log_discrepancies(
        self,
        raw_input: str,
        human_label: Dict[str, Any],
        model_output: Dict[str, Any],
        benchmark_id: Optional[str] = None,
    ) -> List[str]:
        """Inspect model extraction against human ground truth and record any defects found."""
        logged_failure_ids = []

        # 1. Hallucinated Quote Check
        model_quote = model_output.get("evidence_quote", "")
        if model_quote and not validate_substring(raw_input, model_quote):
            fid = self.log_failure(
                failure_type="hallucinated_quote",
                raw_input=raw_input,
                erroneous_model_output={"evidence_quote": model_quote},
                ground_truth_correction={"evidence_quote": human_label.get("evidence_quote")},
                remediation_applied=(
                    "Enforced programmatic validate_substring() guardrail and automated reprompting template "
                    "with strict contiguous substring requirement."
                ),
                benchmark_id=benchmark_id,
            )
            logged_failure_ids.append(fid)

        # 2. Journey Stage Mismatch
        gold_stage = human_label.get("journey_stage", "unknown")
        model_stage = model_output.get("journey_stage", "unknown")
        if gold_stage != "unknown" and model_stage != gold_stage:
            fid = self.log_failure(
                failure_type="stage_mismatch",
                raw_input=raw_input,
                erroneous_model_output={"journey_stage": model_stage},
                ground_truth_correction={"journey_stage": gold_stage},
                remediation_applied=(
                    "Enforced Prompt Rule #4: Do NOT conflate mentions of market drops with stopping "
                    "a SIP unless author explicitly states they stopped or paused."
                ),
                benchmark_id=benchmark_id,
            )
            logged_failure_ids.append(fid)

        # 3. Unsupported Teleological Inference (Invention of motivation or context)
        model_motivation = model_output.get("motivation")
        gold_motivation = human_label.get("motivation")
        if model_motivation and gold_motivation is None:
            fid = self.log_failure(
                failure_type="unsupported_inference",
                raw_input=raw_input,
                erroneous_model_output={"motivation": model_motivation},
                ground_truth_correction={"motivation": None},
                remediation_applied=(
                    "Enforced Prompt Rule #1 & #2: ONLY extract what the author EXPLICITLY states, "
                    "strictly defaulting unstated attributes to null."
                ),
                benchmark_id=benchmark_id,
            )
            logged_failure_ids.append(fid)

        # 4. Relevance Drift
        gold_rel = human_label.get("is_relevant", True)
        model_rel = model_output.get("is_relevant", True)
        if gold_rel != model_rel:
            fid = self.log_failure(
                failure_type="relevance_mismatch",
                raw_input=raw_input,
                erroneous_model_output={"is_relevant": model_rel},
                ground_truth_correction={"is_relevant": gold_rel},
                remediation_applied=(
                    "Enforced two-stage domain qualification filtering before LLM extraction to isolate "
                    "general app performance discussions from mutual fund SIP continuation evidence."
                ),
                benchmark_id=benchmark_id,
            )
            logged_failure_ids.append(fid)

        return logged_failure_ids

    def seed_documented_failures(
        self, benchmark_id_map: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """Seed the 3 genuine, documented AI failure cases identified during prompt development.

        Provides traceable diagnostic records for Deliverable 3 (AI Evidence Log) illustrating
        real hallucination modes and the prompt refinements that resolved them.
        """
        bm_map = benchmark_id_map or {}
        documented_cases = [
            {
                "failure_id": "fail_doc_001_stage_conflation",
                "raw_id": "golden_amb_017",
                "benchmark_id": bm_map.get("golden_amb_017", "bm_golden_amb_017"),
                "failure_type": "stage_mismatch",
                "raw_input": "Invested in small cap index, returns are down by 4 percent.",
                "erroneous_model_output": {
                    "journey_stage": "stopped",
                    "friction_or_concern": "Lost 4% on small cap index investment and stopped contributing",
                    "reported_behaviour": "Stopped recurring SIP contributions due to negative returns",
                },
                "ground_truth_correction": {
                    "journey_stage": "continuing",
                    "friction_or_concern": "Returns down by 4 percent in small cap fund",
                    "reported_behaviour": "Monitoring small cap index portfolio returns",
                },
                "remediation_applied": (
                    "Prompt Refinement: Added Critical Rule #4: 'Do NOT conflate mentions of market drops "
                    "with stopping a SIP unless the author explicitly states they stopped or paused.' "
                    "Enforced conservative defaulting to 'continuing' or 'unknown' when stopping is not explicit."
                ),
            },
            {
                "failure_id": "fail_doc_002_paraphrased_quote",
                "raw_id": "golden_rd_006",
                "benchmark_id": bm_map.get("golden_rd_006", "bm_golden_rd_006"),
                "failure_type": "hallucinated_quote",
                "raw_input": (
                    "Started Rs 3000 monthly SIP in Parag Parikh Flexi Cap 4 months ago. Current value is down by -6%. "
                    "Checked Reddit for workarounds and senior investors advised ignoring short-term NAV dips."
                ),
                "erroneous_model_output": {
                    "evidence_quote": "Senior investors told me to ignore short term NAV dips in Parag Parikh Flexi Cap",
                    "reported_behaviour": "Consulted Reddit community for investment advice",
                },
                "ground_truth_correction": {
                    "evidence_quote": "senior investors advised ignoring short-term NAV dips",
                    "reported_behaviour": "Checked Reddit for workarounds after portfolio value declined",
                },
                "remediation_applied": (
                    "Guardrail Architecture: Implemented deterministic validate_substring() pre-commit gate. "
                    "If the LLM returns synthesized or paraphrased quotes that are not exact contiguous substrings, "
                    "the orchestrator automatically triggers a targeted reprompt with REPROMPT_QUOTE_FAILURE_TEMPLATE."
                ),
            },
            {
                "failure_id": "fail_doc_003_motivation_attribution",
                "raw_id": "golden_ps_001",
                "benchmark_id": bm_map.get("golden_ps_001", "bm_golden_ps_001"),
                "failure_type": "unsupported_inference",
                "raw_input": (
                    "Negative XIRR showing in my first month of SIP. Very worried about losing my money. "
                    "UI is easy to navigate but returns are terrifying."
                ),
                "erroneous_model_output": {
                    "motivation": "Long term wealth accumulation and financial security for retirement",
                    "investor_context": "Conservative beginner investor looking for steady growth",
                },
                "ground_truth_correction": {
                    "motivation": None,
                    "investor_context": None,
                },
                "remediation_applied": (
                    "Prompt Refinement & Schema Gate: Enforced Critical Rule #1 & #2: 'ONLY extract what the author "
                    "EXPLICITLY states. If an attribute (e.g. motivation, context) is not stated, mark it strictly as null.' "
                    "Backed by Pydantic validation requiring missing fields to default to None."
                ),
            },
        ]

        inserted_ids = []
        for case in documented_cases:
            fid = self.log_failure(
                failure_type=case["failure_type"],
                raw_input=case["raw_input"],
                erroneous_model_output=case["erroneous_model_output"],
                ground_truth_correction=case["ground_truth_correction"],
                remediation_applied=case["remediation_applied"],
                benchmark_id=case["benchmark_id"],
                failure_id=case["failure_id"],
            )
            inserted_ids.append(fid)

        return inserted_ids

    def get_failures(
        self, failure_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve logged failures from SQLite, optionally filtered by failure_type."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            if failure_type:
                cursor.execute(
                    """
                    SELECT failure_id, benchmark_id, failure_type, raw_input,
                           erroneous_model_output, ground_truth_correction,
                           remediation_applied, logged_at
                    FROM ai_failure_logs
                    WHERE failure_type = ?
                    ORDER BY logged_at DESC
                    LIMIT ?;
                    """,
                    (failure_type, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT failure_id, benchmark_id, failure_type, raw_input,
                           erroneous_model_output, ground_truth_correction,
                           remediation_applied, logged_at
                    FROM ai_failure_logs
                    ORDER BY logged_at DESC
                    LIMIT ?;
                    """,
                    (limit,),
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def count_failures(self) -> int:
        """Count total logged failures in the database."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ai_failure_logs;")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def clear_failures(self) -> None:
        """Clear all failure logs (used in clean test resets)."""
        conn = get_connection(self.db_path)
        try:
            conn.execute("DELETE FROM ai_failure_logs;")
            conn.commit()
        finally:
            conn.close()
