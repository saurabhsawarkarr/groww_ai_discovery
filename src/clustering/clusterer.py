"""Dimensionality reduction and unsupervised density-based semantic clustering.

Applies UMAP manifold learning to project high-dimensional embeddings into a
latent space and HDBSCAN to discover emergent behavioural archetypes.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger("groww_discovery.clustering.clusterer")


class SemanticClusterer:
    """Manages UMAP dimensionality reduction and HDBSCAN density clustering."""

    def __init__(
        self,
        min_cluster_size: int = 3,
        min_samples: int = 2,
        n_components: int = 5,
        metric: str = "cosine",
        random_state: int = 42,
    ):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.n_components = n_components
        self.metric = metric
        self.random_state = random_state

        self.reduced_embeddings: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.probabilities: Optional[np.ndarray] = None
        self.cluster_centroids: Dict[int, np.ndarray] = {}

    def fit_predict(
        self, embeddings: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Execute dimensionality reduction and unsupervised clustering.

        Args:
            embeddings: 2D numpy array of shape (N, D).

        Returns:
            Tuple of (cluster_labels, cluster_probabilities).
            cluster_labels: Integer array where -1 indicates noise/outliers.
        """
        n_samples, n_features = embeddings.shape
        if n_samples == 0:
            return np.empty(0, dtype=int), np.empty(0, dtype=float)

        if n_samples < 4:
            # Degenerate case: insufficient samples for density estimation
            self.labels = np.zeros(n_samples, dtype=int)
            self.probabilities = np.ones(n_samples, dtype=float)
            self.cluster_centroids = {0: np.mean(embeddings, axis=0)}
            return self.labels, self.probabilities

        # 1. Dimensionality Reduction via UMAP
        try:
            import umap

            adaptive_components = min(self.n_components, max(2, n_samples - 2))
            adaptive_neighbors = min(15, max(2, n_samples - 1))

            reducer = umap.UMAP(
                n_components=adaptive_components,
                n_neighbors=adaptive_neighbors,
                metric=self.metric,
                min_dist=0.0,
                random_state=self.random_state,
            )
            self.reduced_embeddings = reducer.fit_transform(embeddings)
        except Exception as e:
            logger.warning("UMAP reduction failed (%s); using direct embeddings.", str(e))
            self.reduced_embeddings = embeddings

        # 2. Density-Based Clustering via HDBSCAN
        try:
            import hdbscan

            adaptive_min_cluster = min(self.min_cluster_size, max(2, n_samples // 4))
            adaptive_min_samples = min(self.min_samples, adaptive_min_cluster)

            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=adaptive_min_cluster,
                min_samples=adaptive_min_samples,
                metric="euclidean",
                cluster_selection_epsilon=0.0,
            )
            self.labels = clusterer.fit_predict(self.reduced_embeddings)
            self.probabilities = clusterer.probabilities_
        except Exception as e:
            logger.warning("HDBSCAN failed (%s); fallback to cosine AgglomerativeClustering.", str(e))
            from sklearn.cluster import AgglomerativeClustering

            n_clusters = max(2, min(5, n_samples // 3))
            agg = AgglomerativeClustering(n_clusters=n_clusters, metric="cosine", linkage="average")
            self.labels = agg.fit_predict(embeddings)
            self.probabilities = np.ones(n_samples, dtype=float)

        # 3. Calculate Centroids in original embedding space
        self._compute_centroids(embeddings)

        unique_clusters = set(self.labels) - {-1}
        logger.info(
            "Discovered %d dense behavioural clusters (Noise count: %d)",
            len(unique_clusters),
            int(np.sum(self.labels == -1)),
        )

        return self.labels, self.probabilities

    def _compute_centroids(self, embeddings: np.ndarray) -> None:
        """Compute the centroid vector for each identified cluster."""
        self.cluster_centroids.clear()
        if self.labels is None:
            return

        unique_labels = set(self.labels)
        for cl in unique_labels:
            if cl == -1:
                continue
            mask = self.labels == cl
            members = embeddings[mask]
            centroid = np.mean(members, axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 0:
                centroid = centroid / norm
            self.cluster_centroids[cl] = centroid

    def compute_similarity_to_centroid(
        self, embedding: np.ndarray, cluster_id: int
    ) -> float:
        """Compute cosine similarity of a vector to its cluster centroid."""
        if cluster_id not in self.cluster_centroids:
            return 0.0
        centroid = self.cluster_centroids[cluster_id]
        norm_v = np.linalg.norm(embedding)
        norm_c = np.linalg.norm(centroid)
        if norm_v == 0 or norm_c == 0:
            return 0.0
        return float(np.dot(embedding, centroid) / (norm_v * norm_c))
