"""Unit tests for Phase 6: Hypotheses Generation & 5-Pillar Opportunity Prioritization."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import pytest

from src.database.connection import get_connection, init_db
from src.hypotheses.generator import HypothesisGenerator
from src.hypotheses.interview_guides import InterviewGuideSynthesizer
from src.hypotheses.ranker import OpportunityRanker


@pytest.fixture
def temp_db():
    """Create a temporary initialized SQLite database with schema."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    init_db(db_path=db_path)
    yield Path(db_path)

    try:
        os.remove(db_path)
    except OSError:
        pass


@pytest.fixture
def sample_themes():
    """Sample thematic clusters representing drawdowns, autopay failures, and milestone discipline."""
    return [
        {
            "cluster_id": "cl_001",
            "title": "Early Portfolio Drawdown Panic & Negative XIRR Confusion",
            "description": "First-time investors encountering portfolio declines within months 1-3 experience panic.",
            "item_count": 25,
            "distinct_authors_count": 25,
            "unique_voice_ratio": 1.0,
            "dataset_prevalence_pct": 16.13,
            "source_distribution": {"reddit": 15, "play_store": 10},
            "cross_source_dispersion": 0.97,
            "representative_quotes": ["Negative XIRR showing in my first month of SIP."],
            "counter_evidence_quotes": ["Instead of stopping my SIP, I stepped up my monthly contribution."],
            "created_at": datetime.now(timezone.utc),
        },
        {
            "cluster_id": "cl_002",
            "title": "Autopay Mandate Execution Failure & Asynchronous Notification Friction",
            "description": "Scheduled bank autopay deductions fail silently without real-time reconciliation.",
            "item_count": 35,
            "distinct_authors_count": 35,
            "unique_voice_ratio": 1.0,
            "dataset_prevalence_pct": 22.58,
            "source_distribution": {"play_store": 20, "reddit": 15},
            "cross_source_dispersion": 0.98,
            "representative_quotes": ["Bank autopay mandate deduction failed without notification."],
            "counter_evidence_quotes": ["Manually paid through UPI when mandate was delayed."],
            "created_at": datetime.now(timezone.utc),
        },
        {
            "cluster_id": "cl_003",
            "title": "Disciplined Counter-Cyclical Accumulation & Milestone Continuation",
            "description": "Disciplined investors step up contributions during dips and complete 12 months.",
            "item_count": 18,
            "distinct_authors_count": 18,
            "unique_voice_ratio": 1.0,
            "dataset_prevalence_pct": 11.61,
            "source_distribution": {"reddit": 12, "play_store": 6},
            "cross_source_dispersion": 0.92,
            "representative_quotes": ["Completed exactly 12 months of my first Nifty 50 Index SIP today."],
            "counter_evidence_quotes": [],
            "created_at": datetime.now(timezone.utc),
        },
    ]


class TestHypothesisGenerator:
    """Test multi-perspective hypothesis generation, question formulation, and persistence."""

    def test_generate_hypotheses_minimum_two_competing_perspectives(self, sample_themes):
        generator = HypothesisGenerator()
        for theme in sample_themes:
            hyps = generator.generate_hypotheses_for_theme(theme)
            # Mandatory requirement: each theme generates at least 2 competing hypotheses
            assert len(hyps) >= 2

            # Check that both perspectives are represented
            perspectives = [h["perspective"] for h in hyps]
            assert any("Hypothesis A" in p for p in perspectives)
            assert any("Hypothesis B" in p for p in perspectives)

            # Check required fields
            for h in hyps:
                assert h["cluster_id"] == theme["cluster_id"]
                assert len(h["observed_pattern"]) > 10
                assert len(h["hypothesis_text"]) > 10
                assert len(h["alternative_explanation"]) > 10
                assert len(h["missing_evidence"]) > 10
                assert len(h["connection_to_continuation"]) > 10
                assert len(h["validation_approach"]) > 5
                # Mandatory requirement: at least 3 interview questions
                assert isinstance(h["research_questions"], list)
                assert len(h["research_questions"]) >= 3

    def test_persist_and_retrieve_hypotheses(self, temp_db, sample_themes):
        # Seed thematic_clusters table first for foreign key integrity
        conn = get_connection(temp_db)
        now_iso = datetime.now(timezone.utc).isoformat()
        for t in sample_themes:
            conn.execute(
                """
                INSERT INTO thematic_clusters (cluster_id, title, description, item_count, created_at)
                VALUES (?, ?, ?, ?, ?);
                """,
                (t["cluster_id"], t["title"], t["description"], t["item_count"], now_iso),
            )
        conn.commit()
        conn.close()

        generator = HypothesisGenerator(db_path=temp_db)
        all_hyps = []
        for theme in sample_themes:
            all_hyps.extend(generator.generate_hypotheses_for_theme(theme))

        inserted_ids = generator.persist_hypotheses(all_hyps)
        assert len(inserted_ids) == len(all_hyps)
        assert len(inserted_ids) >= 6

        # Retrieve and verify stored records
        stored = generator.get_hypotheses_from_db()
        assert len(stored) == len(all_hyps)
        assert "research_questions" in stored[0]
        assert isinstance(stored[0]["research_questions"], list)

        # Filter by cluster
        cl_001_hyps = generator.get_hypotheses_from_db(cluster_id="cl_001")
        assert len(cl_001_hyps) >= 2


class TestOpportunityRanker:
    """Test 5-pillar qualitative rubric evaluation and prioritization ranking."""

    def test_evaluate_opportunity_all_five_pillars(self, sample_themes):
        ranker = OpportunityRanker()
        card = ranker.evaluate_opportunity(sample_themes[0])

        assert "priority_score" in card
        assert 1.0 <= card["priority_score"] <= 5.0
        assert "priority_tier" in card

        pillars = card["pillars"]
        assert "prevalence" in pillars
        assert "user_impact" in pillars
        assert "business_relevance_12m" in pillars
        assert "evidence_quality" in pillars
        assert "product_addressability" in pillars

        for p_name, p_data in pillars.items():
            assert "score" in p_data
            assert "tier" in p_data
            assert "rationale" in p_data
            assert 1.0 <= p_data["score"] <= 5.0

    def test_rank_opportunities_ordering(self, sample_themes):
        ranker = OpportunityRanker()
        ranked = ranker.rank_opportunities(sample_themes)

        assert len(ranked) == len(sample_themes)
        assert ranked[0]["rank"] == 1
        assert ranked[1]["rank"] == 2
        assert ranked[2]["rank"] == 3

        # Descending score verification
        scores = [r["priority_score"] for r in ranked]
        assert scores == sorted(scores, reverse=True)


class TestInterviewGuideSynthesizer:
    """Test generating 1:1 primary user interview protocols."""

    def test_generate_interview_guide(self, sample_themes):
        synthesizer = InterviewGuideSynthesizer()
        theme = sample_themes[0]
        questions = [
            "Walk me through when you first saw negative XIRR.",
            "What did you expect XIRR to show in month 1?",
            "Did you consider pausing or stopping?",
        ]

        guide = synthesizer.generate_guide(
            cluster_id=theme["cluster_id"],
            theme_title=theme["title"],
            observed_pattern="Panic over early portfolio drops.",
            hypothesis_a="Loss aversion triggers voluntary cancellation.",
            hypothesis_b="Educational gap regarding annualized metrics.",
            core_questions=questions,
        )

        assert guide["cluster_id"] == "cl_001"
        assert "target_participant_screener" in guide
        assert guide["session_duration_minutes"] == 45

        phases = guide["interview_phases"]
        assert len(phases["1_warmup_and_context"]) >= 2
        assert len(phases["2_core_behavioral_inquiries"]) == 3
        assert len(phases["3_competing_hypotheses_probes"]) >= 2
        assert len(phases["4_wrap_up_and_ideal_state"]) >= 2
        assert len(guide["facilitator_notes"]) >= 2
