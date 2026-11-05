"""Golden Set Benchmark Runner evaluating extraction quality across the 7 agreement dimensions.

Executes end-to-end evaluation comparing LLM/rule-based model extractions against
the human-annotated Golden Set (20 items) and logs results to SQLite.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.connectors.base import RawRecord
from src.database.connection import get_connection, get_db_path
from src.evaluation.failure_logger import AIFailureLogger
from src.evaluation.metrics import BenchmarkMetricsCalculator
from src.extraction.orchestrator import ExtractionOrchestrator
from src.preprocessing.qualifier import RelevanceClassifier

logger = logging.getLogger("groww_discovery.evaluation.benchmark")

DEFAULT_SOURCE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "golden_set"
    / "golden_set_source.json"
)
DEFAULT_HUMAN_LABELS_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "golden_set"
    / "golden_set_human_labels.json"
)


class GoldenSetBenchmark:
    """Orchestrates Golden Set evaluation across the 7 mandated agreement dimensions."""

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        config: Optional[Dict[str, Any]] = None,
        source_path: Optional[Union[str, Path]] = None,
        human_labels_path: Optional[Union[str, Path]] = None,
    ):
        self.db_path = get_db_path(db_path)
        self.source_path = Path(source_path) if source_path else DEFAULT_SOURCE_PATH
        self.human_labels_path = (
            Path(human_labels_path) if human_labels_path else DEFAULT_HUMAN_LABELS_PATH
        )
        self.config = config

        self.metrics_calculator = BenchmarkMetricsCalculator()
        self.failure_logger = AIFailureLogger(db_path=self.db_path)
        self.orchestrator = ExtractionOrchestrator(config=self.config)
        self.qualifier = RelevanceClassifier()

    def load_golden_set(
        self,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """Load the 20 Golden Set source items and human ground-truth labels.

        Returns:
            Tuple of (source_items_list, human_labels_dict_keyed_by_raw_id)
        """
        if not self.source_path.exists():
            raise FileNotFoundError(
                f"Golden set source file not found at: {self.source_path}"
            )
        if not self.human_labels_path.exists():
            raise FileNotFoundError(
                f"Golden set human labels file not found at: {self.human_labels_path}"
            )

        with open(self.source_path, "r", encoding="utf-8") as f:
            sources: List[Dict[str, Any]] = json.load(f)

        with open(self.human_labels_path, "r", encoding="utf-8") as f:
            labels_list: List[Dict[str, Any]] = json.load(f)

        labels_map = {lbl["raw_id"]: lbl for lbl in labels_list}
        return sources, labels_map

    def ensure_sources_in_db(self, sources: List[Dict[str, Any]]) -> None:
        """Register Golden Set records in raw_conversations to satisfy foreign keys."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            now_iso = datetime.now(timezone.utc).isoformat()
            for s in sources:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO raw_conversations (
                        raw_id,
                        source_platform,
                        source_url,
                        author_id_hash,
                        published_at,
                        collected_at,
                        raw_text,
                        thread_context,
                        product_context,
                        is_qualified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        s["raw_id"],
                        s.get("source_platform", "other"),
                        s.get("source_url"),
                        s.get("author_id_hash"),
                        s.get("published_at", now_iso),
                        now_iso,
                        s["raw_text"],
                        json.dumps(s.get("thread_context", {})),
                        s.get("product_context", "unknown"),
                        s.get("is_qualified", 1),
                    ),
                )
            conn.commit()
            logger.info("Ensured %d Golden Set source items in raw_conversations", len(sources))
        finally:
            conn.close()

    def evaluate_single_item(
        self,
        raw_item: Dict[str, Any],
        human_label: Dict[str, Any],
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Run extraction and evaluate against human label across the 7 dimensions."""
        raw_id = raw_item["raw_id"]
        raw_text = raw_item["raw_text"]

        # 1. Qualification / Relevance Check
        is_relevant_pred, _ = self.qualifier.qualify_text(raw_text)

        # 2. Extract Evidence Record
        record = RawRecord(
            raw_id=raw_id,
            source_platform=raw_item.get("source_platform", "other"),
            source_url=raw_item.get("source_url"),
            author_id_hash=raw_item.get("author_id_hash"),
            raw_text=raw_text,
            thread_context=raw_item.get("thread_context"),
            product_context=raw_item.get("product_context", "unknown"),
        )

        evidence = self.orchestrator.extract_from_record(record)
        if evidence:
            model_dict = evidence.model_dump()
            model_dict["raw_id"] = raw_id
            model_dict["is_relevant"] = is_relevant_pred
        else:
            model_dict = {
                "raw_id": raw_id,
                "source_id": raw_id,
                "is_relevant": is_relevant_pred,
                "journey_stage": "unknown",
                "evidence_quote": raw_text[:50] if raw_text else "",
                "reported_behaviour": "",
                "friction_or_concern": None,
                "workaround": None,
                "reported_outcome": None,
            }

        # 3. Calculate 7-dimension agreement scores
        metrics = self.metrics_calculator.evaluate_item(
            raw_text=raw_text,
            human_label=human_label,
            model_output=model_dict,
        )

        return metrics, model_dict

    def run_benchmark(
        self,
        persist_to_db: bool = True,
        seed_failure_cases: bool = True,
    ) -> Dict[str, Any]:
        """Execute evaluation across all 20 Golden Set items.

        Returns:
            Dictionary containing aggregate metrics across 7 dimensions, item results,
            and total failure logs count.
        """
        sources, labels_map = self.load_golden_set()
        logger.info("Loaded %d Golden Set items for evaluation", len(sources))

        if persist_to_db:
            self.ensure_sources_in_db(sources)

        item_metrics_list: List[Dict[str, float]] = []
        item_results: List[Dict[str, Any]] = []
        benchmark_id_map: Dict[str, str] = {}

        now_utc = datetime.now(timezone.utc)

        for src in sources:
            raw_id = src["raw_id"]
            human_label = labels_map.get(raw_id, {})
            benchmark_id = f"bm_{raw_id}"
            benchmark_id_map[raw_id] = benchmark_id

            metrics, model_output = self.evaluate_single_item(src, human_label)
            item_metrics_list.append(metrics)

            item_results.append({
                "benchmark_id": benchmark_id,
                "raw_id": raw_id,
                "metrics": metrics,
                "human_label": human_label,
                "model_output": model_output,
            })

            # Persist benchmark result to database
            if persist_to_db:
                conn = get_connection(self.db_path)
                try:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO golden_set_benchmarks (
                            benchmark_id,
                            raw_id,
                            human_labels,
                            model_labels,
                            agreement_score,
                            evaluated_at
                        ) VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        (
                            benchmark_id,
                            raw_id,
                            json.dumps(human_label),
                            json.dumps(model_output, default=str),
                            metrics["overall_agreement"],
                            now_utc,
                        ),
                    )
                    conn.commit()
                finally:
                    conn.close()

            # Check and log any live discrepancies
            self.failure_logger.detect_and_log_discrepancies(
                raw_input=src["raw_text"],
                human_label=human_label,
                model_output=model_output,
                benchmark_id=benchmark_id,
            )

        # Seed documented historical development failure modes
        if seed_failure_cases and persist_to_db:
            self.failure_logger.seed_documented_failures(benchmark_id_map=benchmark_id_map)

        aggregate = self.metrics_calculator.aggregate_metrics(item_metrics_list)
        total_failures = self.failure_logger.count_failures()

        logger.info(
            "Benchmark completed: %d items evaluated, Overall Agreement: %.2f%%, Failures Logged: %d",
            len(sources),
            aggregate.get("overall_agreement", 0.0) * 100,
            total_failures,
        )

        return {
            "total_items": len(sources),
            "aggregate_metrics": aggregate,
            "item_results": item_results,
            "failures_logged": total_failures,
            "evaluated_at": now_utc.isoformat(),
        }

    def get_benchmark_results_from_db(self) -> List[Dict[str, Any]]:
        """Retrieve stored benchmark evaluations from golden_set_benchmarks."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT benchmark_id, raw_id, human_labels, model_labels,
                       agreement_score, evaluated_at
                FROM golden_set_benchmarks
                ORDER BY benchmark_id ASC;
                """
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                r = dict(row)
                r["human_labels"] = json.loads(r["human_labels"])
                r["model_labels"] = json.loads(r["model_labels"]) if r["model_labels"] else {}
                results.append(r)
            return results
        finally:
            conn.close()
