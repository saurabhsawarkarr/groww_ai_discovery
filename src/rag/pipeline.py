"""End-to-End Qualitative RAG Pipeline with Robust Multi-Tier Fallback and Guardrail Enforcement.

Coordinates:
1. Hybrid BM25 + Vector Semantic Retrieval across 3,052 customer conversation corpus
   with multi-tier fallback (Direct RRF -> Synonym Query Expansion -> Thematic Centroid).
2. Structured prompt assembly adhering to SEBI Non-Advice Invariant & Anti-FOMO Guardrail.
3. Pluggable LLM execution with automatic Deterministic Grounded Synthesis fallback
   and post-generation negative guardrail interceptor.
4. Comprehensive compliance auditing:
   - Positive Requirements: 4-Tier Structure, [EVID-X] Grounding, Behavioral Heuristics, PM Levers.
   - Negative Invariants: SEBI Non-Advice, Anti-FOMO / Dark Patterns, Zero Phantom Citations, Zero Fluff, Zero Victim Blaming.
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
        """Execute end-to-end RAG inquiry and return synthesized analysis with multi-tier fallback
        and positive + negative rule audits.
        """
        start_time = time.perf_counter()

        # 1. Retrieve top-K evidence chunks with multi-tier retrieval fallback
        retrieved_evidence = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            platform_filter=platform_filter,
            journey_stage_filter=journey_stage_filter,
        )
        retrieval_meta = dict(getattr(self.retriever, "last_retrieval_meta", {}))
        retrieval_time_ms = round((time.perf_counter() - start_time) * 1000, 1)

        # 2. Build structured user prompt with numbered evidence context blocks
        user_prompt = RAGPromptBuilder.build_user_prompt(query, retrieved_evidence)

        # 3. Generate synthesis via external LLM with automatic grounded fallback & interceptor
        gen_start = time.perf_counter()
        synthesis, is_llm_fallback, fallback_reason = LLMAdapter.generate_with_fallback(
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

        # 4. Enforce and Audit Rules Post-Generation (Positive & Negative)
        negative_audit = RAGRulesEngine.validate_negative_guardrails(synthesis, len(retrieved_evidence))
        citation_audit = RAGRulesEngine.audit_citations(synthesis, len(retrieved_evidence))
        structure_audit = RAGRulesEngine.audit_structure(synthesis)

        is_overall_fallback = is_llm_fallback or retrieval_meta.get("is_fallback", False)

        # Determine readable execution mode label for UI display
        if is_llm_fallback:
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
            "is_fallback": is_overall_fallback,
            "is_llm_fallback": is_llm_fallback,
            "fallback_reason": fallback_reason,
            "retrieval_meta": retrieval_meta,
            "retrieval_fallback_tier": retrieval_meta.get("fallback_tier", "Tier 1: Direct Hybrid RRF"),
            "execution_mode": execution_mode,
            "sebi_compliant": negative_audit["sebi_clean"],
            "sebi_violations": negative_audit["sebi_violations"],
            "sebi_guardrail": "PASSED (100% Non-Advice Compliant)" if negative_audit["sebi_clean"] else "FLAGGED (Review Required)",
            "fomo_compliant": negative_audit["fomo_clean"],
            "fomo_violations": negative_audit["fomo_violations"],
            "citation_audit": citation_audit,
            "structure_audit": structure_audit,
            "negative_guardrails": negative_audit,
        }
