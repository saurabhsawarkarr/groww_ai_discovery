"""Groww AI-Powered Discovery Engine - Qualitative RAG Subsystem.

Provides hybrid BM25 + Vector retrieval over the 3,052 investor conversation corpus,
with a pluggable multi-provider LLM adapter architecture for separate LLMs.
"""

from src.rag.retriever import HybridEvidenceRetriever
from src.rag.prompt_builder import RAGPromptBuilder
from src.rag.llm_adapter import LLMAdapter
from src.rag.pipeline import RAGPipeline

__all__ = [
    "HybridEvidenceRetriever",
    "RAGPromptBuilder",
    "LLMAdapter",
    "RAGPipeline",
]

