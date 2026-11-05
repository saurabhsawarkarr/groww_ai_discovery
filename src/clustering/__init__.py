"""Unsupervised semantic clustering, pattern discovery, and counter-evidence synthesis."""

from src.clustering.analyzer import ClusteringAnalyzer, CounterEvidenceFinder
from src.clustering.clusterer import SemanticClusterer
from src.clustering.embedder import EvidenceEmbedder
from src.clustering.synthesizer import ThemeSynthesizer, compute_entropy

__all__ = [
    "EvidenceEmbedder",
    "SemanticClusterer",
    "ThemeSynthesizer",
    "CounterEvidenceFinder",
    "ClusteringAnalyzer",
    "compute_entropy",
]
