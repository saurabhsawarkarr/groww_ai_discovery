"""Feature vectorizer and embedding generator for qualitative evidence records.

Transforms structured behavioral observations (reported_behaviour + friction_or_concern)
into dense semantic representations using sentence-transformers/all-MiniLM-L6-v2.
"""

import logging
from typing import Any, Dict, List, Optional, Union
import numpy as np

logger = logging.getLogger("groww_discovery.clustering.embedder")

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


class EvidenceEmbedder:
    """Generates normalized dense embeddings from structured evidence observations."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: Optional[str] = None,
        normalize_embeddings: bool = True,
    ):
        self.model_name = model_name
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self._model = None
        self._init_model()

    def _init_model(self) -> None:
        """Load the SentenceTransformer model with graceful fallback."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Loaded SentenceTransformer model: %s", self.model_name)
        except Exception as e:
            logger.warning(
                "Could not load SentenceTransformer (%s): %s. Fallback to lightweight vectorizer.",
                self.model_name,
                str(e),
            )
            self._model = None

    def construct_feature_text(self, record: Union[Dict[str, Any], Any]) -> str:
        """Combine behavioral fields into an informative semantic feature text.

        Adheres to architecture specification 3.4: reported_behaviour + friction_or_concern,
        with situational trigger and stage context if available.
        """
        if isinstance(record, dict):
            behaviour = record.get("reported_behaviour", "") or ""
            friction = record.get("friction_or_concern", "") or ""
            trigger = record.get("trigger_or_situation", "") or ""
            stage = record.get("journey_stage", "") or ""
        else:
            behaviour = getattr(record, "reported_behaviour", "") or ""
            friction = getattr(record, "friction_or_concern", "") or ""
            trigger = getattr(record, "trigger_or_situation", "") or ""
            stage = getattr(record, "journey_stage", "") or ""

        parts = []
        if stage and stage != "unknown":
            parts.append(f"Stage: {stage.replace('_', ' ')}")
        if trigger:
            parts.append(f"Trigger: {trigger}")
        if behaviour:
            parts.append(f"Action: {behaviour}")
        if friction:
            parts.append(f"Friction: {friction}")

        if not parts:
            # Fallback to evidence quote if available
            quote = record.get("evidence_quote", "") if isinstance(record, dict) else getattr(record, "evidence_quote", "")
            return quote or "Mutual fund SIP investment behaviour"

        return ". ".join(parts) + "."

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate dense embeddings for a list of text strings."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        if self._model is not None:
            embeddings = self._model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                normalize_embeddings=self.normalize_embeddings,
            )
            return np.asarray(embeddings, dtype=np.float32)

        # Deterministic lightweight fallback: Bag-of-words / character n-gram hashing
        logger.info("Using deterministic hash-based fallback embedding")
        dim = 384
        vectors = []
        for text in texts:
            vec = np.zeros(dim, dtype=np.float32)
            words = text.lower().split()
            for w in words:
                idx = hash(w) % dim
                vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)
        return np.array(vectors, dtype=np.float32)

    def embed_records(
        self, records: List[Union[Dict[str, Any], Any]]
    ) -> np.ndarray:
        """Construct feature texts and generate embeddings for evidence records."""
        texts = [self.construct_feature_text(r) for r in records]
        return self.embed_texts(texts)
