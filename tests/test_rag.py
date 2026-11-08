"""Unit and integration tests for Qualitative RAG Pipeline, Rules, Fallback, and Evaluation."""

from pathlib import Path
import pytest

from src.rag.retriever import HybridEvidenceRetriever
from src.rag.rules import RAGRulesEngine
from src.rag.prompt_builder import RAGPromptBuilder
from src.rag.llm_adapter import LLMAdapter
from src.rag.pipeline import RAGPipeline
from src.rag.evaluator import RAGEvaluator


class TestRAGRetriever:
    """Test BM25 + Vector hybrid retrieval and reciprocal rank fusion."""

    def test_retriever_initialization_and_corpus_load(self):
        retriever = HybridEvidenceRetriever()
        assert len(retriever.records) > 0, "Corpus should load records"
        assert len(retriever.doc_tokens) == len(retriever.records)
        assert len(retriever.inverted_index) > 0

    def test_retriever_queries(self):
        retriever = HybridEvidenceRetriever()
        results = retriever.retrieve("autopay mandate failure", top_k=3)
        assert len(results) > 0
        assert len(results) <= 3
        assert "quote" in results[0]
        assert "similarity_score" in results[0]

    def test_retriever_platform_filter(self):
        retriever = HybridEvidenceRetriever()
        results = retriever.retrieve("delay nav allotment", top_k=5, platform_filter="play_store")
        for item in results:
            assert "play" in item["platform"].lower()


class TestRAGRulesEngine:
    """Test the 5 system answering rules and SEBI non-advice guardrails."""

    def test_sebi_non_advice_compliance(self):
        # Non-compliant advisory recommendation
        bad_text = "We recommend you buy Parag Parikh Flexi Cap for your portfolio."
        is_comp, viols = RAGRulesEngine.validate_sebi_compliance(bad_text)
        assert not is_comp
        assert len(viols) > 0

        # Compliant product recommendation
        good_text = (
            "We recommend adding an automated 1-click UPI recovery fallback link "
            "and a pre-debit WhatsApp ping to reduce involuntary churn."
        )
        is_comp, viols = RAGRulesEngine.validate_sebi_compliance(good_text)
        assert is_comp
        assert len(viols) == 0

    def test_citation_auditing(self):
        text = (
            "Users experience involuntary mandate drops [EVID-1]. "
            "Additionally, users report scheme overlap confusion [EVID-2]."
        )
        audit = RAGRulesEngine.audit_citations(text, evidence_count=3)
        assert audit["has_citations"] is True
        assert audit["unique_chunks_cited"] == 2
        assert 1 in audit["cited_indices"]
        assert 2 in audit["cited_indices"]

    def test_structure_auditing(self):
        text = """### 1. Executive Summary & Behavioral Dynamic
Novice investors experience churn.

### 2. Discovered Friction & Root Cause Breakdown
- Operational: Bank drops.
- Cognitive: FD anchor.

### 3. Voice of Customer Verbatim Highlights
- [EVID-1]: "Quote here"

### 4. Strategic PM Recommendations (12-Month Retention Impact)
1. Add UPI retry.
"""
        audit = RAGRulesEngine.audit_structure(text)
        assert audit["is_complete"] is True
        assert audit["structure_completeness_score"] == 1.0


class TestLLMAdapterAndFallback:
    """Test pluggable LLM connection tests and automatic deterministic fallback."""

    def test_deterministic_provider_connection(self):
        ok, msg = LLMAdapter.test_connection("Deterministic Grounded Engine (No Key Required)")
        assert ok is True
        assert "active" in msg.lower()

    def test_missing_api_key_failover(self):
        # When external provider is called without key, must gracefully fallback to deterministic engine
        prompt = "Why do bank autopay mandates fail silently?"
        evidence = [{"quote": "Bank autopay failed silently without any SMS.", "platform": "play_store", "theme_id": "THEME-01", "journey_stage": "stopped"}]
        
        text, is_fallback, reason = LLMAdapter.generate_with_fallback(
            prompt=prompt,
            system_prompt="Test system prompt",
            retrieved_evidence=evidence,
            provider="Google Gemini (Gemini 3.5 Flash)",
            api_key=None,
        )
        assert is_fallback is True
        assert "Automatic failover" in reason
        assert "Executive Summary" in text
        assert "[EVID-1]" in text

    def test_invalid_api_key_http_error_fallback(self):
        # When external provider throws HTTP error (e.g. 400 or 401), must catch and fallback
        prompt = "Why do investors panic over negative returns in month 1?"
        evidence = [{"quote": "My returns are negative in month 1, I want to cancel.", "platform": "reddit", "theme_id": "THEME-04", "journey_stage": "newly_started"}]

        text, is_fallback, reason = LLMAdapter.generate_with_fallback(
            prompt=prompt,
            system_prompt="Test system prompt",
            retrieved_evidence=evidence,
            provider="Google Gemini (Gemini 3.5 Flash)",
            api_key="invalid_fake_key_12345",
        )
        assert is_fallback is True
        assert "Activated Deterministic Grounded Synthesis Fallback" in reason
        assert "Executive Summary" in text
        assert "[EVID-1]" in text


class TestRAGPipelineEndToEnd:
    """Test full RAG pipeline integration."""

    def test_end_to_end_query_execution(self):
        pipeline = RAGPipeline()
        res = pipeline.query("Why do bank autopay mandates fail silently?", top_k=3)

        assert res["query"] == "Why do bank autopay mandates fail silently?"
        assert res["evidence_count"] > 0
        assert len(res["retrieved_evidence"]) <= 3
        assert res["sebi_compliant"] is True
        assert res["citation_audit"]["has_citations"] is True
        assert res["structure_audit"]["is_complete"] is True
        assert res["total_latency_ms"] > 0

    def test_golden_dataset_evaluation(self):
        evaluator = RAGEvaluator()
        cases = evaluator.get_test_cases()
        assert len(cases) >= 15

        # Evaluate first 3 cases
        for tc in cases[:3]:
            res = evaluator.evaluate_case(tc, top_k=3)
            assert res["sebi_compliant"] is True
            assert res["structure_pass"] is True
            assert res["case_passed"] is True

