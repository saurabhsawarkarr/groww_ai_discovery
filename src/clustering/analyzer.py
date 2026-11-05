"""End-to-end semantic clustering, counter-evidence synthesis, and database persistence.

Discovers emergent qualitative behavioral themes, pairs themes with contradictory
counter-examples, and commits clusters and mappings to SQLite.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from src.clustering.clusterer import SemanticClusterer
from src.clustering.embedder import EvidenceEmbedder
from src.clustering.synthesizer import ThemeSynthesizer
from src.database.connection import get_connection, get_db_path

logger = logging.getLogger("groww_discovery.clustering.analyzer")


class CounterEvidenceFinder:
    """Surfaces contradictory records sharing similar triggers but displaying opposite outcomes."""

    def find_counter_evidence(
        self,
        cluster_records: List[Dict[str, Any]],
        all_records: List[Dict[str, Any]],
        top_k: int = 3,
    ) -> List[str]:
        """Identify quotes from records with similar triggers but divergent behaviour.

        For instance, when a cluster exhibits churn due to negative returns, counter-evidence
        locates investors who experienced negative returns but stepped up or stayed invested.
        """
        cluster_ids = {r.get("evidence_id") for r in cluster_records}
        counter_candidates = []

        # Analyze cluster dominant triggers & frictions
        cluster_text = " ".join([
            (r.get("trigger_or_situation") or "") + " " + (r.get("friction_or_concern") or "")
            for r in cluster_records
        ]).lower()

        is_drawdown_cluster = any(w in cluster_text for w in ["negative", "xirr", "down", "loss", "red"])
        is_mandate_cluster = any(w in cluster_text for w in ["autopay", "mandate", "failed", "pending", "deduct"])
        is_pause_cluster = any(w in cluster_text for w in ["pause", "stop", "cancel"])

        for rec in all_records:
            if rec.get("evidence_id") in cluster_ids:
                continue

            r_text = (
                (rec.get("reported_behaviour") or "")
                + " "
                + (rec.get("workaround") or "")
                + " "
                + (rec.get("evidence_quote") or "")
            ).lower()
            stage = rec.get("journey_stage", "")
            quote = rec.get("evidence_quote")

            if not quote or len(quote.strip()) < 10:
                continue

            # Case 1: Drawdown churn vs Drawdown continuation / stepping up
            if is_drawdown_cluster:
                if stage == "continuing" or any(w in r_text for w in ["step up", "stepped up", "stayed", "ignored", "discipline", "accumulat", "+14%", "+16%"]):
                    counter_candidates.append(quote.strip())

            # Case 2: Autopay failure vs Proactive workaround
            elif is_mandate_cluster:
                if any(w in r_text for w in ["workaround", "manual", "upi", "scheduled", "salary"]):
                    counter_candidates.append(quote.strip())

            # Case 3: Cancellation vs Pausing or temporary adjustment
            elif is_pause_cluster:
                if stage == "continuing" or "reduced" in r_text or "paused" in stage:
                    counter_candidates.append(quote.strip())

        # If domain-specific counter-evidence found, return top_k
        if counter_candidates:
            # Deduplicate preserving order
            seen = set()
            deduped = []
            for c in counter_candidates:
                if c not in seen:
                    seen.add(c)
                    deduped.append(c)
            return deduped[:top_k]

        # General fallback: Return records from 'continuing' journey stage
        fallback_quotes = [
            r.get("evidence_quote")
            for r in all_records
            if r.get("evidence_id") not in cluster_ids
            and r.get("journey_stage") == "continuing"
            and r.get("evidence_quote")
        ]
        return fallback_quotes[:top_k]


class ClusteringAnalyzer:
    """Coordinates end-to-end unsupervised semantic clustering and database synchronization."""

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        embedder: Optional[EvidenceEmbedder] = None,
        clusterer: Optional[SemanticClusterer] = None,
        synthesizer: Optional[ThemeSynthesizer] = None,
    ):
        self.db_path = get_db_path(db_path)
        self.embedder = embedder or EvidenceEmbedder()
        self.clusterer = clusterer or SemanticClusterer()
        self.synthesizer = synthesizer or ThemeSynthesizer()
        self.counter_finder = CounterEvidenceFinder()

    def load_evidence_records(self) -> List[Dict[str, Any]]:
        """Load extracted evidence records joined with raw conversations for provenance."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    e.evidence_id,
                    e.raw_id,
                    e.investor_context,
                    e.journey_stage,
                    e.motivation,
                    e.expectation,
                    e.trigger_or_situation,
                    e.reported_behaviour,
                    e.friction_or_concern,
                    e.monitoring_behaviour,
                    e.workaround,
                    e.reported_outcome,
                    e.evidence_quote,
                    e.evidence_type,
                    e.extraction_confidence,
                    e.created_at,
                    r.source_platform,
                    r.author_id_hash,
                    r.raw_text,
                    r.product_context
                FROM extracted_evidence e
                JOIN raw_conversations r ON e.raw_id = r.raw_id
                ORDER BY e.created_at ASC;
                """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def run_clustering(
        self,
        records: Optional[List[Dict[str, Any]]] = None,
        persist_to_db: bool = True,
    ) -> Dict[str, Any]:
        """Execute semantic clustering over evidence records and persist results.

        Returns:
            Dictionary containing thematic clusters, prevalence statistics, and mappings.
        """
        all_records = records if records is not None else self.load_evidence_records()
        total_count = len(all_records)
        logger.info("Executing semantic clustering over %d evidence records", total_count)

        if total_count == 0:
            logger.warning("No evidence records available for clustering.")
            return {"total_records": 0, "clusters": [], "noise_count": 0}

        # 1. Generate Embeddings
        embeddings = self.embedder.embed_records(all_records)

        # 2. Density-Based Clustering
        labels, probabilities = self.clusterer.fit_predict(embeddings)

        # 3. Group records by cluster label
        clusters_by_label: Dict[int, List[Tuple[Dict[str, Any], np.ndarray]]] = {}
        noise_records: List[Dict[str, Any]] = []

        for idx, label in enumerate(labels):
            rec = all_records[idx]
            emb = embeddings[idx]
            if label == -1:
                noise_records.append(rec)
            else:
                clusters_by_label.setdefault(int(label), []).append((rec, emb))

        # 4. Synthesize themes and attach counter-evidence
        synthesized_clusters: List[Dict[str, Any]] = []
        cluster_mappings_to_save: List[Dict[str, Any]] = []

        for cl_idx, member_pairs in clusters_by_label.items():
            cluster_id = f"cl_{cl_idx:03d}"
            cluster_recs = [p[0] for p in member_pairs]
            cluster_embs = [p[1] for p in member_pairs]

            # Find contradictory counter-examples
            counter_quotes = self.counter_finder.find_counter_evidence(
                cluster_records=cluster_recs,
                all_records=all_records,
                top_k=3,
            )

            # Synthesize Theme
            theme = self.synthesizer.synthesize_theme(
                cluster_id=cluster_id,
                cluster_records=cluster_recs,
                total_qualified_records=total_count,
                counter_evidence_quotes=counter_quotes,
            )
            synthesized_clusters.append(theme)

            # Build Cluster Mappings
            for rec, emb in member_pairs:
                sim = self.clusterer.compute_similarity_to_centroid(emb, cl_idx)
                cluster_mappings_to_save.append({
                    "mapping_id": f"map_{cluster_id}_{rec['evidence_id']}",
                    "cluster_id": cluster_id,
                    "evidence_id": rec["evidence_id"],
                    "similarity_score": round(sim, 4),
                })

        # 5. Persist to Database
        if persist_to_db:
            self._save_to_db(synthesized_clusters, cluster_mappings_to_save)

        logger.info(
            "Clustering complete: %d themes formed, %d mappings saved, %d noise items",
            len(synthesized_clusters),
            len(cluster_mappings_to_save),
            len(noise_records),
        )

        return {
            "total_records": total_count,
            "clusters": synthesized_clusters,
            "mappings_count": len(cluster_mappings_to_save),
            "noise_count": len(noise_records),
        }

    def _save_to_db(
        self,
        clusters: List[Dict[str, Any]],
        mappings: List[Dict[str, Any]],
    ) -> None:
        """Persist thematic clusters and cluster mappings to SQLite tables."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()

            # Insert / Replace Thematic Clusters
            for cl in clusters:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO thematic_clusters (
                        cluster_id,
                        title,
                        description,
                        item_count,
                        distinct_authors_count,
                        source_distribution,
                        counter_evidence_quotes,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        cl["cluster_id"],
                        cl["title"],
                        cl["description"],
                        cl["item_count"],
                        cl["distinct_authors_count"],
                        json.dumps(cl["source_distribution"]),
                        json.dumps(cl["counter_evidence_quotes"]),
                        cl["created_at"],
                    ),
                )

            # Insert / Replace Cluster Mappings
            for m in mappings:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO cluster_mappings (
                        mapping_id,
                        cluster_id,
                        evidence_id,
                        similarity_score
                    ) VALUES (?, ?, ?, ?);
                    """,
                    (
                        m["mapping_id"],
                        m["cluster_id"],
                        m["evidence_id"],
                        m["similarity_score"],
                    ),
                )

            conn.commit()
            logger.info(
                "Persisted %d clusters and %d mappings to SQLite database",
                len(clusters),
                len(mappings),
            )
        finally:
            conn.close()

    def get_clusters_from_db(self) -> List[Dict[str, Any]]:
        """Retrieve stored thematic clusters from SQLite."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT cluster_id, title, description, item_count,
                       distinct_authors_count, source_distribution,
                       counter_evidence_quotes, created_at
                FROM thematic_clusters
                ORDER BY item_count DESC;
                """
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                r = dict(row)
                r["source_distribution"] = json.loads(r["source_distribution"])
                r["counter_evidence_quotes"] = json.loads(r["counter_evidence_quotes"])
                results.append(r)
            return results
        finally:
            conn.close()
