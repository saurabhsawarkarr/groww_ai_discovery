"""Script to run the Golden Set benchmark (20 items) and log evaluation metrics.

Evaluates model extractions against independent human ground truth across
the 7 agreement dimensions and outputs an ASCII formatted report.
"""

import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_db_path, init_db
from src.evaluation.benchmark import GoldenSetBenchmark
from src.evaluation.failure_logger import AIFailureLogger

# Configure basic logging to stdout with safe encoding
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("groww_discovery.scripts.run_benchmark")


def print_ascii_header(title: str, width: int = 78) -> None:
    print("\n" + "=" * width)
    print(f" {title.upper()}")
    print("=" * width)


def print_metrics_table(metrics: dict) -> None:
    dimension_names = [
        ("relevance_agreement", "1. Relevance Agreement Rate"),
        ("quote_exactness", "2. Verbatim Quote Exactness"),
        ("behaviour_friction_agreement", "3. Behaviour & Friction Agreement"),
        ("journey_stage_accuracy", "4. Journey Stage Accuracy"),
        ("workaround_outcome_agreement", "5. Workaround & Outcome Recall"),
        ("zero_hallucination_rate", "6. Zero-Hallucination Rate"),
        ("source_traceability", "7. Source Traceability Rate"),
        ("overall_agreement", "OVERALL COMPOSITE AGREEMENT"),
    ]

    print(f"{'Dimension':<45} | {'Agreement %':>12} | {'Status':>10}")
    print("-" * 45 + "-+-" + "-" * 12 + "-+-" + "-" * 10)

    for key, display_name in dimension_names:
        score = metrics.get(key, 0.0)
        pct_str = f"{score * 100:.2f}%"
        status = "[PASSED]" if score >= 0.70 else "[REVIEW]"
        if key == "source_traceability":
            status = "[PASSED]" if score == 1.0 else "[FAILED]"
        if key == "zero_hallucination_rate" or key == "quote_exactness":
            status = "[PASSED]" if score >= 0.95 else "[REVIEW]"

        prefix = ">> " if key == "overall_agreement" else "   "
        print(f"{prefix}{display_name:<42} | {pct_str:>12} | {status:>10}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Golden Set Benchmark across 7 Agreement Dimensions"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to discovery_engine.db (defaults to configured path)",
    )
    parser.add_argument(
        "--no-persist",
        action="store_true",
        help="Run evaluation in-memory without updating golden_set_benchmarks in SQLite",
    )
    args = parser.parse_args()

    db_file = get_db_path(args.db_path)
    print_ascii_header("Groww Discovery Engine: Golden Set Benchmark Execution")
    print(f"Database Target: {db_file}")
    print(f"Timestamp:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    benchmark = GoldenSetBenchmark(db_path=db_file)
    persist = not args.no_persist

    print("\n[INFO] Loading 20 Golden Set items and human ground-truth labels...")
    results = benchmark.run_benchmark(persist_to_db=persist, seed_failure_cases=persist)

    print_ascii_header("Golden Set 7-Dimension Agreement Summary")
    print_metrics_table(results["aggregate_metrics"])

    print_ascii_header("Curated Golden Set Platform Breakdown (20 Items)")
    sources, _ = benchmark.load_golden_set()
    platform_counts = {}
    for s in sources:
        p = s.get("source_platform", "other")
        platform_counts[p] = platform_counts.get(p, 0) + 1

    for platform, count in sorted(platform_counts.items()):
        print(f" - {platform.replace('_', ' ').title():<25}: {count:>3} items")

    print_ascii_header("Documented AI Failure Cases & Prompt Refinements (Deliverable 3 Preview)")
    failure_logger = AIFailureLogger(db_path=db_file)
    failures = failure_logger.get_failures(limit=10)

    print(f"Total AI Failure Cases Registered: {len(failures)}\n")
    for i, fail in enumerate(failures[:3], 1):
        print(f"[{i}] FAILURE TYPE: {fail['failure_type'].upper()}")
        print(f"    Raw Input:        \"{fail['raw_input'][:80]}...\"")
        print(f"    Erroneous Output: {fail['erroneous_model_output']}")
        print(f"    Ground Truth:     {fail['ground_truth_correction']}")
        print(f"    Remediation:      {fail['remediation_applied']}")
        print("-" * 78)

    print("\n[OK] Phase 4 Golden Set Benchmarking completed successfully.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
