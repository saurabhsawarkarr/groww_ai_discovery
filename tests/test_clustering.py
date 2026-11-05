"""Unit tests for Phase 5: Pattern Discovery, Semantic Clustering & Counter-Evidence Synthesis."""

import os
from pathlib import Path
import tempfile
import pytest
import numpy as np

from src.clustering.analyzer import ClusteringAnalyzer, CounterEvidenceFinder
from src.clustering.clusterer import SemanticClusterer
from src.clustering.embedder import EvidenceEmbedder
from src.clustering.synthesizer import ThemeSynthesizer, compute_entropy
from src.database.connection import get_connection, init_db


@pytest.fixture
def temp_db():
    """Create a temporary initialized SQLite database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    init_db(db_path=db_path)
    yield Path(db_path)

    try:
        os.remove(db_path)
    except OSError:
        pass


@pytest.fixture
def sample_evidence_records():
    """Sample diverse evidence records spanning drawdown panic, mandate failure, and counter-discipline."""
    return [
        {
            "evidence_id": "ev_001",
            "raw_id": "raw_001",
            "journey_stage": "newly_started",
            "reported_behaviour": "Checking portfolio balance daily in first month",
            "friction_or_concern": "Anxiety over negative XIRR in month 1",
            "trigger_or_situation": "Negative returns in first month",
            "workaround": None,
            "evidence_quote": "Negative XIRR showing in my first month of SIP",
            "source_platform": "play_store",
            "author_id_hash": "author_111",
            "product_context": "groww_specific",
        },
        {
            "evidence_id": "ev_002",
            "raw_id": "raw_002",
            "journey_stage": "newly_started",
            "reported_behaviour": "Checking returns after market dip",
            "friction_or_concern": "Negative returns panic and fear of capital loss",
            "trigger_or_situation": "Portfolio in red",
            "workaround": None,
            "evidence_quote": "My returns are negative and I am losing money",
            "source_platform": "reddit",
            "author_id_hash": "author_222",
            "product_context": "category_level",
        },
        {
            "evidence_id": "ev_003",
            "raw_id": "raw_003",
            "journey_stage": "considering_change",
            "reported_behaviour": "Contemplating stopping SIP due to negative returns",
            "friction_or_concern": "Negative XIRR and market dip panic",
            "trigger_or_situation": "Market correction",
            "workaround": None,
            "evidence_quote": "Thinking of stopping my SIP because returns are down",
            "source_platform": "play_store",
            "author_id_hash": "author_333",
            "product_context": "groww_specific",
        },
        {
            "evidence_id": "ev_004",
            "raw_id": "raw_004",
            "journey_stage": "considering_change",
            "reported_behaviour": "Contacted customer care after autopay mandate failed",
            "friction_or_concern": "Autopay bank mandate deduction failure without notification",
            "trigger_or_situation": "Bank autopay failed",
            "workaround": None,
            "evidence_quote": "Autopay mandate deduction failed without notification",
            "source_platform": "play_store",
            "author_id_hash": "author_444",
            "product_context": "groww_specific",
        },
        {
            "evidence_id": "ev_005",
            "raw_id": "raw_005",
            "journey_stage": "paused",
            "reported_behaviour": "Checked bank account after instalment pending",
            "friction_or_concern": "Bank deduction delay and pending status",
            "trigger_or_situation": "Money debited but app shows pending status",
            "workaround": "Contacted bank branch",
            "evidence_quote": "Bank debited 1000 rupees but app shows pending status",
            "source_platform": "youtube",
            "author_id_hash": "author_555",
            "product_context": "category_level",
        },
        {
            "evidence_id": "ev_006",
            "raw_id": "raw_006",
            "journey_stage": "continuing",
            "reported_behaviour": "Waiting for support response on failed instalment",
            "friction_or_concern": "Autopay deduction failure and 4 day support delay",
            "trigger_or_situation": "Mandate deduction missed",
            "workaround": None,
            "evidence_quote": "Groww support took 4 days to respond to failed autopay",
            "source_platform": "play_store",
            "author_id_hash": "author_666",
            "product_context": "groww_specific",
        },
        {
            "evidence_id": "ev_007",
            "raw_id": "raw_007",
            "journey_stage": "continuing",
            "reported_behaviour": "Stepped up monthly contribution by Rs 1500 during dip",
            "friction_or_concern": None,
            "trigger_or_situation": "Nifty dropped 4% and portfolio in red",
            "workaround": "Bought discounted NAV units",
            "evidence_quote": "Instead of stopping my SIP, I stepped up my monthly contribution by Rs 1500",
            "source_platform": "reddit",
            "author_id_hash": "author_777",
            "product_context": "category_level",
        },
        {
            "evidence_id": "ev_008",
            "raw_id": "raw_008",
            "journey_stage": "continuing",
            "reported_behaviour": "Never checked balance and let autopay run for 12 months",
            "friction_or_concern": None,
            "trigger_or_situation": "Experienced months with negative 8 percent return",
            "workaround": "Ignored short term fluctuations completely",
            "evidence_quote": "Completed exactly 12 months of my first Nifty 50 Index SIP today",
            "source_platform": "reddit",
            "author_id_hash": "author_888",
            "product_context": "category_level",
        },
    ]


class TestEvidenceEmbedder:
    """Test feature text construction and embedding generation."""

    def test_construct_feature_text(self):
        embedder = EvidenceEmbedder()
        record = {
            "journey_stage": "newly_started",
            "trigger_or_situation": "Negative XIRR in first month",
            "reported_behaviour": "Checking portfolio returns",
            "friction_or_concern": "Anxiety over losses",
        }
        text = embedder.construct_feature_text(record)
        assert "Stage: newly started" in text
        assert "Trigger: Negative XIRR in first month" in text
        assert "Action: Checking portfolio returns" in text
        assert "Friction: Anxiety over losses" in text

    def test_embed_records_shape_and_normalization(self, sample_evidence_records):
        embedder = EvidenceEmbedder()
        embeddings = embedder.embed_records(sample_evidence_records)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (len(sample_evidence_records), 384)

        # Check normalization (norm ≈ 1.0)
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_allclose(norms, 1.0, atol=1e-4)


class TestSemanticClusterer:
    """Test clustering execution and centroid computation."""

    def test_fit_predict_clustering(self):
        clusterer = SemanticClusterer(min_cluster_size=2, min_samples=1)
        # Create two distinct clusters in 384D
        cluster_a = np.ones((5, 384), dtype=np.float32) + np.random.randn(5, 384) * 0.05
        cluster_b = -np.ones((5, 384), dtype=np.float32) + np.random.randn(5, 384) * 0.05
        X = np.vstack([cluster_a, cluster_b])

        labels, probabilities = clusterer.fit_predict(X)
        assert len(labels) == 10
        assert len(clusterer.cluster_centroids) >= 1

        # Check similarity to centroid
        sim = clusterer.compute_similarity_to_centroid(cluster_a[0], 0)
        assert -1.0 <= sim <= 1.0


class TestThemeSynthesizer:
    """Test metrics calculation, UVR, entropy, and theme synthesis."""

    def test_compute_entropy(self):
        # Single platform -> entropy 0
        assert compute_entropy({"play_store": 10}) == 0.0
        # Equal distribution across 2 platforms -> entropy 1.0
        assert compute_entropy({"play_store": 5, "reddit": 5}) == 1.0

    def test_synthesize_theme_metrics(self, sample_evidence_records):
        synthesizer = ThemeSynthesizer()
        theme = synthesizer.synthesize_theme(
            cluster_id="cl_001",
            cluster_records=sample_evidence_records[:3],
            total_qualified_records=len(sample_evidence_records),
            counter_evidence_quotes=["Counter quote 1"],
        )

        assert theme["cluster_id"] == "cl_001"
        assert theme["item_count"] == 3
        assert theme["distinct_authors_count"] == 3
        assert theme["unique_voice_ratio"] == 1.0
        assert theme["dataset_prevalence_pct"] > 0
        assert "title" in theme and len(theme["title"]) > 5
        assert "description" in theme and len(theme["description"]) > 20
        assert len(theme["counter_evidence_quotes"]) == 1


class TestCounterEvidenceFinder:
    """Test identifying opposing behavior during market drops."""

    def test_find_counter_evidence_for_drawdown(self, sample_evidence_records):
        finder = CounterEvidenceFinder()
        # Cluster with drawdown anxiety (records 0, 1, 2)
        drawdown_cluster = sample_evidence_records[:3]
        counter_quotes = finder.find_counter_evidence(
            cluster_records=drawdown_cluster,
            all_records=sample_evidence_records,
            top_k=2,
        )

        assert len(counter_quotes) >= 1
        # Should surface the counter-cyclical stepping up quote
        assert any("stepped up" in q.lower() or "12 month" in q.lower() for q in counter_quotes)


class TestClusteringAnalyzer:
    """Test end-to-end clustering and SQLite synchronization."""

    def test_run_clustering_end_to_end(self, temp_db, sample_evidence_records):
        # Seed records in SQLite database to satisfy foreign keys
        conn = get_connection(temp_db)
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()

        for rec in sample_evidence_records:
            conn.execute(
                """
                INSERT INTO raw_conversations (raw_id, source_platform, author_id_hash, collected_at, raw_text, is_qualified)
                VALUES (?, ?, ?, ?, ?, 1);
                """,
                (rec["raw_id"], rec["source_platform"], rec["author_id_hash"], now_iso, rec["evidence_quote"]),
            )
            conn.execute(
                """
                INSERT INTO extracted_evidence (evidence_id, raw_id, journey_stage, reported_behaviour, friction_or_concern, evidence_quote, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (rec["evidence_id"], rec["raw_id"], rec["journey_stage"], rec["reported_behaviour"], rec["friction_or_concern"], rec["evidence_quote"], now_iso),
            )
        conn.commit()
        conn.close()

        analyzer = ClusteringAnalyzer(
            db_path=temp_db,
            clusterer=SemanticClusterer(min_cluster_size=2, min_samples=1),
        )
        result = analyzer.run_clustering(records=sample_evidence_records, persist_to_db=True)

        assert result["total_records"] == 8
        assert len(result["clusters"]) >= 1
        assert result["mappings_count"] >= 1

        # Verify database tables populated
        stored_clusters = analyzer.get_clusters_from_db()
        assert len(stored_clusters) >= 1

        first_cl = stored_clusters[0]
        assert "title" in first_cl
        assert "description" in first_cl
        assert first_cl["item_count"] >= 2
        assert first_cl["distinct_authors_count"] >= 1
        assert isinstance(first_cl["source_distribution"], dict)
        assert isinstance(first_cl["counter_evidence_quotes"], list)
