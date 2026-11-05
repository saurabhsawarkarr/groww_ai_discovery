"""Evaluation, benchmarking, and AI failure diagnostics module."""

from src.evaluation.benchmark import GoldenSetBenchmark
from src.evaluation.failure_logger import AIFailureLogger
from src.evaluation.metrics import (
    BenchmarkMetricsCalculator,
    compute_semantic_agreement,
    compute_token_f1,
)

__all__ = [
    "GoldenSetBenchmark",
    "AIFailureLogger",
    "BenchmarkMetricsCalculator",
    "compute_semantic_agreement",
    "compute_token_f1",
]
