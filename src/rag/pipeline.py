"""End-to-End Qualitative RAG Pipeline with Robust Fallback and Rule Enforcement.

Coordinates:
1. Hybrid BM25 + Vector Semantic Retrieval across 3,052 customer conversation corpus.
2. Structured prompt assembly adhering to SEBI Non-Advice Invariant.
3. Pluggable LLM execution with automatic Deterministic Grounded Synthesis fallback.
4. Regulatory compliance auditing (SEBI Non-Advice, Citation Density, Section Completeness).
"""

import time
from typing import Any, Dict, List, Optional

from src.rag.retriever import HybridEvidenceRetriever
from src.rag.prompt_builder import RAGPromptBuilder
from src.rag.llm_adapter import LLMAdapter
from src.rag.rules import RAGRulesEngine, RAG_SYSTEM_RULES_PROMPT


class RAGPipeline:
    """Orchestrator for qualitative evidence retrieval-augmented generation."""

    def __init__(self, retriever: Optional[HybridEvidenceRetriever] = None):
        self.retriever = retriever or HybridEvidenceRetriever()

    def query(
        self,
        query: str,
        top_k: int = 5,
        platform_filter: Optional[str] = None,
        journey_stage_filter: Optional[str] = None,
        llm_provider: str = "Deterministic Grounded Engine (No Key Required)",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Execute end-to-end RAG inquiry and return synthesized analysis with rule audits."""
        start_time = time.perf_counter()

        # 1. Retrieve top-K evidence chunks using hybrid BM25 + Vector RRF
        retrieved_evidence = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            platform_filter=platform_filter,
            journey_stage_filter=journey_stage_filter,
        )

        retrieval_time_ms = round((time.perf_counter() - start_time) * 1000, 1)

        # 2. Build structured user prompt with numbered evidence context blocks
        user_prompt = RAGPromptBuilder.build_user_prompt(query, retrieved_evidence)

        # 3. Generate synthesis via external LLM with automatic grounded fallback
        gen_start = time.perf_counter()
        synthesis, is_fallback, fallback_reason = LLMAdapter.generate_with_fallback(
            prompt=user_prompt,
            system_prompt=RAG_SYSTEM_RULES_PROMPT,
            retrieved_evidence=retrieved_evidence,
            provider=llm_provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            temperature=temperature,
        )
        generation_time_ms = round((time.perf_counter() - gen_start) * 1000, 1)
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 1)

        # 4. Enforce and Audit Rules Post-Generation
        sebi_compliant, sebi_violations = RAGRulesEngine.validate_sebi_compliance(synthesis)
        citation_audit = RAGRulesEngine.audit_citations(synthesis, len(retrieved_evidence))
        structure_audit = RAGRulesEngine.audit_structure(synthesis)

        # Determine readable execution mode label for UI display
        if is_fallback:
            execution_mode = "Deterministic Grounded Fallback (Active)"
        elif "Deterministic" in llm_provider:
            execution_mode = "Deterministic Grounded Engine"
        else:
            model_disp = model or ("Gemini" if "Gemini" in llm_provider else "Default Model")
            execution_mode = f"External LLM ({model_disp})"

        return {
            "query": query,
            "answer": synthesis,
            "retrieved_evidence": retrieved_evidence,
            "evidence_count": len(retrieved_evidence),
            "retrieval_time_ms": retrieval_time_ms,
            "generation_time_ms": generation_time_ms,
            "total_latency_ms": total_time_ms,
            "llm_provider": llm_provider,
            "llm_model": model or ("Grounded Engine" if "Deterministic" in llm_provider else "Default"),
            "is_fallback": is_fallback,
            "fallback_reason": fallback_reason,
            "execution_mode": execution_mode,
            "sebi_compliant": sebi_compliant,
            "sebi_violations": sebi_violations,
            "sebi_guardrail": "PASSED (100% Non-Advice Compliant)" if sebi_compliant else "FLAGGED (Review Required)",
            "citation_audit": citation_audit,
            "structure_audit": structure_audit,
        }
