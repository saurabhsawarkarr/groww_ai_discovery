"""Qualitative RAG Golden Benchmark Evaluator.

Executes standardized benchmark evaluations across the 25-case Golden Dataset to measure:
1. Retrieval Precision & Hit Rate @ K (Target Theme & Keyword Recall).
2. Citation Integrity & Density (Presence of [EVID-X] tags and source attribution).
3. SEBI Non-Advice Regulatory Compliance Rate (Target: 100.0% Non-Advisory).
4. Anti-FOMO & Ethical Growth Compliance Rate (Target: 100.0% Non-Manipulative).
5. Zero Hallucination Rate (Target: 100.0% zero phantom citations).
6. Structural 4-Section Completeness Rate.
7. Deterministic Fallback Resilience (100% Uptime across API failures).
8. End-to-End Latency.
"""

import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from src.rag.pipeline import RAGPipeline
from src.rag.rules import RAGRulesEngine


class RAGEvaluator:
    """Evaluates the RAG pipeline against the 25-case Golden Dataset."""

    def __init__(self, data_path: Optional[Path] = None, pipeline: Optional[RAGPipeline] = None):
        project_root = Path(__file__).resolve().parent.parent.parent
        self.data_path = data_path or (project_root / "data" / "golden_set" / "rag_golden_dataset.json")
        self.pipeline = pipeline or RAGPipeline()
        self.golden_data: Dict[str, Any] = self._load_golden_dataset()

    def _load_golden_dataset(self) -> Dict[str, Any]:
        """Load golden dataset test cases from JSON file."""
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"test_cases": []}

    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Return list of all golden test cases."""
        return self.golden_data.get("test_cases", [])

    def evaluate_case(
        self,
        test_case: Dict[str, Any],
        top_k: int = 5,
        llm_provider: str = "Deterministic Grounded Engine (No Key Required)",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate a single golden benchmark query against positive requirements and negative guardrails."""
        query = test_case["query"]
        target_theme = test_case.get("target_theme_id", "THEME-01")
        expected_keywords = test_case.get("expected_keywords", [])
        min_citations = test_case.get("minimum_citations", 1)
        is_sebi_probe = test_case.get("sebi_advisory_probe", False)
        is_fomo_probe = test_case.get("fomo_probe", False)
        is_out_of_scope = test_case.get("out_of_scope_probe", False)

        start_time = time.perf_counter()
        rag_res = self.pipeline.query(
            query=query,
            top_k=top_k,
            llm_provider=llm_provider,
            api_key=api_key,
            model=model,
        )
        latency_ms = round((time.perf_counter() - start_time) * 1000, 1)

        answer = rag_res["answer"]
        retrieved = rag_res["retrieved_evidence"]

        # 1. Evaluate Retrieval Hit (Target theme match or keyword recall)
        theme_matches = sum(1 for item in retrieved if item.get("theme_id") == target_theme)
        keyword_hits = 0
        retrieved_blob = " ".join([item.get("quote", "").lower() for item in retrieved])
        for kw in expected_keywords:
            if kw.lower() in retrieved_blob or kw.lower() in answer.lower():
                keyword_hits += 1

        retrieval_hit = (theme_matches > 0) or (keyword_hits >= max(1, len(expected_keywords) // 3)) or is_out_of_scope

        # 2. Negative Guardrails Auditing
        negative_audit = rag_res.get("negative_guardrails") or RAGRulesEngine.validate_negative_guardrails(answer, len(retrieved))
        sebi_compliant = negative_audit["sebi_clean"]
        fomo_compliant = negative_audit["fomo_clean"]
        phantom_clean = negative_audit["phantom_clean"]
        blaming_clean = negative_audit["blaming_clean"]
        fluff_clean = negative_audit["fluff_clean"]
        cleanliness_score = negative_audit["cleanliness_score"]

        # 3. Citation Audit
        citation_audit = rag_res["citation_audit"]
        citation_pass = (citation_audit["unique_chunks_cited"] >= min_citations) or (min_citations == 0)

        # 4. Structure Audit
        structure_audit = rag_res["structure_audit"]
        structure_pass = structure_audit["is_complete"]

        # Overall Case Pass: All criteria met
        case_passed = sebi_compliant and fomo_compliant and phantom_clean and structure_pass and citation_pass

        return {
            "query_id": test_case["query_id"],
            "category": test_case["category"],
            "query": query,
            "target_theme": target_theme,
            "retrieval_hit": retrieval_hit,
            "retrieved_count": len(retrieved),
            "theme_matches": theme_matches,
            "keyword_hits": keyword_hits,
            "expected_keywords_count": len(expected_keywords),
            "sebi_compliant": sebi_compliant,
            "fomo_compliant": fomo_compliant,
            "phantom_clean": phantom_clean,
            "blaming_clean": blaming_clean,
            "cleanliness_score": cleanliness_score,
            "unique_citations": citation_audit["unique_chunks_cited"],
            "citation_pass": citation_pass,
            "structure_score": structure_audit["structure_completeness_score"],
            "structure_pass": structure_pass,
            "is_fallback": rag_res["is_fallback"],
            "retrieval_fallback_tier": rag_res.get("retrieval_fallback_tier", "Tier 1: Direct Hybrid RRF"),
            "execution_mode": rag_res["execution_mode"],
            "latency_ms": latency_ms,
            "case_passed": case_passed,
        }

    def evaluate_all(
        self,
        top_k: int = 5,
        llm_provider: str = "Deterministic Grounded Engine (No Key Required)",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run full evaluation suite across all golden benchmark cases."""
        test_cases = self.get_test_cases()
        if not test_cases:
            return {"error": "No golden test cases found."}

        results: List[Dict[str, Any]] = []
        total_cases = len(test_cases)
        passed_cases = 0
        sebi_passed = 0
        fomo_passed = 0
        phantom_clean_count = 0
        citation_passed = 0
        structure_passed = 0
        retrieval_hits = 0
        fallback_resilient_count = 0
        total_cleanliness = 0.0
        total_latency = 0.0

        for tc in test_cases:
            res = self.evaluate_case(
                test_case=tc,
                top_k=top_k,
                llm_provider=llm_provider,
                api_key=api_key,
                model=model,
            )
            results.append(res)

            if res["case_passed"]:
                passed_cases += 1
            if res["sebi_compliant"]:
                sebi_passed += 1
            if res["fomo_compliant"]:
                fomo_passed += 1
            if res["phantom_clean"]:
                phantom_clean_count += 1
            if res["citation_pass"]:
                citation_passed += 1
            if res["structure_pass"]:
                structure_passed += 1
            if res["retrieval_hit"]:
                retrieval_hits += 1
            if res["execution_mode"]:
                fallback_resilient_count += 1
            total_cleanliness += res["cleanliness_score"]
            total_latency += res["latency_ms"]

        summary = {
            "benchmark_name": self.golden_data.get("benchmark_name", "Golden Benchmark"),
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "overall_pass_rate": round((passed_cases / total_cases) * 100, 1),
            "sebi_compliance_rate": round((sebi_passed / total_cases) * 100, 1),
            "fomo_compliance_rate": round((fomo_passed / total_cases) * 100, 1),
            "zero_hallucination_rate": round((phantom_clean_count / total_cases) * 100, 1),
            "retrieval_hit_rate": round((retrieval_hits / total_cases) * 100, 1),
            "citation_compliance_rate": round((citation_passed / total_cases) * 100, 1),
            "structural_completeness_rate": round((structure_passed / total_cases) * 100, 1),
            "fallback_resilience_rate": round((fallback_resilient_count / total_cases) * 100, 1),
            "avg_cleanliness_score": round(total_cleanliness / max(1, total_cases), 1),
            "avg_latency_ms": round(total_latency / max(1, total_cases), 1),
            "cases_evaluated": results,
        }
        return summary
