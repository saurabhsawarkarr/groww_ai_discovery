"""Unit tests for Phase 4: Golden Set benchmarking, metrics calculation, and failure logging."""

import os
from pathlib import Path
import pytest
import sqlite3
import tempfile

from src.database.connection import init_db
from src.evaluation.benchmark import GoldenSetBenchmark
from src.evaluation.failure_logger import AIFailureLogger
from src.evaluation.metrics import (
    BenchmarkMetricsCalculator,
    compute_semantic_agreement,
    compute_token_f1,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary SQLite database initialized with schema."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    init_db(db_path=db_path)
    yield Path(db_path)

    try:
        os.remove(db_path)
    except OSError:
        pass


class TestMetricsCalculation:
    """Test token F1, semantic agreement, and 7-dimension metrics."""

    def test_compute_token_f1_exact_and_disjoint(self):
        assert compute_token_f1("monthly sip investment", "monthly sip investment") == 1.0
        assert compute_token_f1("apple orange", "banana grape") == 0.0
        assert compute_token_f1(None, None) == 1.0
        assert compute_token_f1("something", None) == 0.0
        assert compute_token_f1(None, "something") == 0.0

    def test_compute_token_f1_partial_overlap(self):
        f1 = compute_token_f1("monthly sip investment in index fund", "sip investment stopped")
        assert 0.0 < f1 < 1.0

    def test_compute_semantic_agreement(self):
        score = compute_semantic_agreement(
            pred_behaviour="Stopped recurring monthly SIP instalments",
            pred_friction="Negative XIRR panic in first month",
            gold_behaviour="Stopped recurring monthly SIP instalments",
            gold_friction="Negative XIRR panic in first month",
        )
        assert score == 1.0

        partial = compute_semantic_agreement(
            pred_behaviour="Stopped SIP due to market drop",
            pred_friction="Negative returns",
            gold_behaviour="Paused SIP temporarily",
            gold_friction="Negative returns in first month",
        )
        assert 0.0 < partial < 1.0

    def test_benchmark_metrics_calculator_all_dimensions(self):
        calc = BenchmarkMetricsCalculator()
        raw_text = "Negative XIRR showing in my first month of SIP. Very worried about losing my money."

        gold = {
            "raw_id": "test_001",
            "is_relevant": True,
            "journey_stage": "newly_started",
            "reported_behaviour": "Checking portfolio returns in first month",
            "friction_or_concern": "Anxiety and fear over negative XIRR",
            "workaround": None,
            "reported_outcome": None,
            "evidence_quote": "Negative XIRR showing in my first month of SIP",
        }

        # Perfect match
        pred_perfect = {
            "source_id": "test_001",
            "raw_id": "test_001",
            "is_relevant": True,
            "journey_stage": "newly_started",
            "reported_behaviour": "Checking portfolio returns in first month",
            "friction_or_concern": "Anxiety and fear over negative XIRR",
            "workaround": None,
            "reported_outcome": None,
            "evidence_quote": "Negative XIRR showing in my first month of SIP",
        }

        res = calc.evaluate_item(raw_text, gold, pred_perfect)
        assert res["relevance_agreement"] == 1.0
        assert res["quote_exactness"] == 1.0
        assert res["behaviour_friction_agreement"] == 1.0
        assert res["journey_stage_accuracy"] == 1.0
        assert res["workaround_outcome_agreement"] == 1.0
        assert res["zero_hallucination_rate"] == 1.0
        assert res["source_traceability"] == 1.0
        assert res["overall_agreement"] == 1.0

    def test_benchmark_metrics_calculator_hallucinated_quote(self):
        calc = BenchmarkMetricsCalculator()
        raw_text = "Negative XIRR showing in my first month of SIP."

        gold = {
            "raw_id": "test_002",
            "is_relevant": True,
            "journey_stage": "newly_started",
            "evidence_quote": "Negative XIRR showing in my first month of SIP",
        }

        pred_hallucinated = {
            "source_id": "test_002",
            "is_relevant": True,
            "journey_stage": "newly_started",
            "evidence_quote": "Completely made up quote not in text",
        }

        res = calc.evaluate_item(raw_text, gold, pred_hallucinated)
        assert res["quote_exactness"] == 0.0
        assert res["zero_hallucination_rate"] == 0.0


class TestAIFailureLogger:
    """Test AI failure tracking, discrepancy detection, and seeded cases."""

    def test_log_and_query_failure(self, temp_db_path):
        from datetime import datetime, timezone
        from src.database.connection import get_connection

        # Seed prerequisite raw_conversation and golden_set_benchmarks row for FK
        conn = get_connection(temp_db_path)
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text)
            VALUES ('raw_fk_001', 'test', ?, 'Test text');
            """,
            (now_iso,),
        )
        conn.execute(
            """
            INSERT INTO golden_set_benchmarks (benchmark_id, raw_id, human_labels, evaluated_at)
            VALUES ('bm_test_001', 'raw_fk_001', '{}', ?);
            """,
            (now_iso,),
        )
        conn.commit()
        conn.close()

        logger = AIFailureLogger(db_path=temp_db_path)
        fid = logger.log_failure(
            failure_type="stage_mismatch",
            raw_input="Returns dropped 4%",
            erroneous_model_output={"journey_stage": "stopped"},
            ground_truth_correction={"journey_stage": "continuing"},
            remediation_applied="Rule 4 enforced",
            benchmark_id="bm_test_001",
        )
        assert fid.startswith("fail_")
        assert logger.count_failures() == 1

        failures = logger.get_failures()
        assert len(failures) == 1
        assert failures[0]["failure_type"] == "stage_mismatch"
        assert failures[0]["benchmark_id"] == "bm_test_001"

        # Also test unlinked failure gracefully setting benchmark_id to None
        fid_unlinked = logger.log_failure(
            failure_type="unsupported_inference",
            raw_input="Some unlinked text",
            erroneous_model_output="err",
            ground_truth_correction="corr",
            remediation_applied="Rule 1 enforced",
            benchmark_id="bm_non_existent",
        )
        assert logger.count_failures() == 2
        f2 = [f for f in logger.get_failures() if f["failure_id"] == fid_unlinked][0]
        assert f2["benchmark_id"] is None

    def test_detect_discrepancies(self, temp_db_path):
        logger = AIFailureLogger(db_path=temp_db_path)
        raw_text = "Returns dropped 4 percent this month in small cap."

        gold = {
            "journey_stage": "continuing",
            "motivation": None,
            "evidence_quote": "Returns dropped 4 percent",
            "is_relevant": True,
        }

        # Model with stage mismatch and hallucinated quote
        pred = {
            "journey_stage": "stopped",
            "motivation": "Retirement goal",
            "evidence_quote": "I cancelled my SIP immediately",
            "is_relevant": True,
        }

        fids = logger.detect_and_log_discrepancies(raw_text, gold, pred, benchmark_id="bm_disc_001")
        assert len(fids) >= 2  # Hallucinated quote + stage mismatch + unsupported motivation
        assert logger.count_failures() >= 2

    def test_seed_documented_failures(self, temp_db_path):
        logger = AIFailureLogger(db_path=temp_db_path)
        seeded_ids = logger.seed_documented_failures()
        assert len(seeded_ids) == 3

        failures = logger.get_failures()
        types = {f["failure_type"] for f in failures}
        assert "stage_mismatch" in types
        assert "hallucinated_quote" in types
        assert "unsupported_inference" in types


class TestGoldenSetBenchmark:
    """Test end-to-end benchmark loading and execution."""

    def test_load_golden_set_files(self):
        benchmark = GoldenSetBenchmark()
        sources, labels_map = benchmark.load_golden_set()
        assert len(sources) == 20
        assert len(labels_map) == 20

        # Verify platform diversity: Play Store, Reddit, YouTube, Edge, Counter
        platforms = {s["source_platform"] for s in sources}
        assert "play_store" in platforms
        assert "reddit" in platforms
        assert "youtube" in platforms

    def test_run_benchmark_execution(self, temp_db_path):
        benchmark = GoldenSetBenchmark(db_path=temp_db_path)
        results = benchmark.run_benchmark(persist_to_db=True, seed_failure_cases=True)

        assert results["total_items"] == 20
        assert len(results["item_results"]) == 20
        assert results["failures_logged"] >= 3

        agg = results["aggregate_metrics"]
        assert "relevance_agreement" in agg
        assert "quote_exactness" in agg
        assert "behaviour_friction_agreement" in agg
        assert "journey_stage_accuracy" in agg
        assert "workaround_outcome_agreement" in agg
        assert "zero_hallucination_rate" in agg
        assert "source_traceability" in agg
        assert "overall_agreement" in agg

        # 100% Source Traceability requirement check
        assert agg["source_traceability"] == 1.0
        # 100% Quote Exactness / Zero Hallucination requirement check
        assert agg["quote_exactness"] == 1.0
        assert agg["zero_hallucination_rate"] == 1.0

        # Check records stored in SQLite database
        stored = benchmark.get_benchmark_results_from_db()
        assert len(stored) == 20
