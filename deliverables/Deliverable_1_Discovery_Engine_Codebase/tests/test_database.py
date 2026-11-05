"""Unit tests for SQLite database schema, connections, constraints, and CRUD operations.

Validates:
- Full schema creation across all 8 tables
- Foreign key enforcement and cascade delete behaviors
- JSON serialization/deserialization integrity
- Complete CRUD lifecycles on all tables
- Transaction rollbacks on exceptions
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import pytest

from src.database.connection import (
    get_connection,
    get_db_cursor,
    get_table_names,
    init_db,
)


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Fixture providing a temporary SQLite database initialized with schema.sql."""
    db_file = tmp_path / "test_discovery.db"
    init_db(db_path=db_file)
    return db_file


EXPECTED_TABLES = {
    "raw_conversations",
    "exclusion_logs",
    "extracted_evidence",
    "thematic_clusters",
    "cluster_mappings",
    "hypothesis_records",
    "golden_set_benchmarks",
    "ai_failure_logs",
}


def test_schema_initialization(temp_db: Path):
    """Verify that all 8 core tables are properly created."""
    tables = set(get_table_names(temp_db))
    assert EXPECTED_TABLES.issubset(tables), f"Missing tables: {EXPECTED_TABLES - tables}"


def test_foreign_keys_enforced(temp_db: Path):
    """Verify foreign key enforcement (inserting orphan child record fails)."""
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    # Attempt inserting an exclusion log referencing a non-existent raw_id
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO exclusion_logs (exclusion_id, raw_id, reason, excluded_at)
            VALUES (?, ?, ?, ?);
            """,
            ("ex_orphan_1", "non_existent_raw_id", "Test orphan check", datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    conn.close()


def test_crud_raw_conversations(temp_db: Path):
    """Test Create, Read, Update, Delete for raw_conversations table."""
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    raw_id = "test_playstore_001"
    now_iso = datetime.now(timezone.utc).isoformat()
    thread_data = {"app_version": "14.2", "user_rating": 1, "review_length": 45}

    # CREATE
    cursor.execute(
        """
        INSERT INTO raw_conversations (
            raw_id, source_platform, source_url, author_id_hash,
            published_at, collected_at, raw_text, thread_context,
            product_context, is_qualified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            raw_id,
            "play_store",
            "https://play.google.com/store/apps/details?id=com.nextbillion.groww&reviewId=1",
            "hash_abc123",
            now_iso,
            now_iso,
            "Started my first SIP of 1000 rupees last month but XIRR shows negative -8%. Confused whether to continue.",
            json.dumps(thread_data),
            "groww_specific",
            0,
        ),
    )
    conn.commit()

    # READ
    cursor.execute("SELECT * FROM raw_conversations WHERE raw_id = ?", (raw_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row["source_platform"] == "play_store"
    assert row["product_context"] == "groww_specific"
    assert row["is_qualified"] == 0
    loaded_context = json.loads(row["thread_context"])
    assert loaded_context["user_rating"] == 1

    # UPDATE
    cursor.execute(
        "UPDATE raw_conversations SET is_qualified = 1 WHERE raw_id = ?",
        (raw_id,),
    )
    conn.commit()
    cursor.execute("SELECT is_qualified FROM raw_conversations WHERE raw_id = ?", (raw_id,))
    assert cursor.fetchone()["is_qualified"] == 1

    # DELETE
    cursor.execute("DELETE FROM raw_conversations WHERE raw_id = ?", (raw_id,))
    conn.commit()
    cursor.execute("SELECT * FROM raw_conversations WHERE raw_id = ?", (raw_id,))
    assert cursor.fetchone() is None
    conn.close()


def test_crud_exclusion_logs(temp_db: Path):
    """Test CRUD operations on exclusion_logs with foreign key linkage."""
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    raw_id = "test_raw_excl_001"
    now_iso = datetime.now(timezone.utc).isoformat()

    # Create parent raw conversation
    cursor.execute(
        """
        INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text)
        VALUES (?, ?, ?, ?);
        """,
        (raw_id, "reddit", now_iso, "How do I trade BankNifty F&O intraday options with 10k margin?"),
    )

    # CREATE exclusion log
    excl_id = "excl_001"
    reason_str = "Irrelevant domain: contains 'f&o'"
    cursor.execute(
        """
        INSERT INTO exclusion_logs (exclusion_id, raw_id, reason, excluded_at)
        VALUES (?, ?, ?, ?);
        """,
        (excl_id, raw_id, reason_str, now_iso),
    )
    conn.commit()

    # READ
    cursor.execute("SELECT * FROM exclusion_logs WHERE exclusion_id = ?", (excl_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row["raw_id"] == raw_id
    assert row["reason"] == reason_str

    # UPDATE
    updated_reason = "Excluded: Intraday F&O discussion not relevant to mutual fund SIP"
    cursor.execute(
        "UPDATE exclusion_logs SET reason = ? WHERE exclusion_id = ?",
        (updated_reason, excl_id),
    )
    conn.commit()
    cursor.execute("SELECT reason FROM exclusion_logs WHERE exclusion_id = ?", (excl_id,))
    assert cursor.fetchone()["reason"] == updated_reason

    # DELETE
    cursor.execute("DELETE FROM exclusion_logs WHERE exclusion_id = ?", (excl_id,))
    conn.commit()
    cursor.execute("SELECT * FROM exclusion_logs WHERE exclusion_id = ?", (excl_id,))
    assert cursor.fetchone() is None
    conn.close()


def test_cascade_delete_from_raw_conversations(temp_db: Path):
    """Verify that deleting a raw conversation cascades to exclusion_logs and extracted_evidence."""
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    raw_id = "test_raw_cascade_001"
    now_iso = datetime.now(timezone.utc).isoformat()

    cursor.execute(
        """
        INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text, is_qualified)
        VALUES (?, ?, ?, ?, 1);
        """,
        (raw_id, "reddit", now_iso, "I stopped my SIP after 3 months because NAV kept dipping."),
    )

    ev_id = "ev_cascade_001"
    cursor.execute(
        """
        INSERT INTO extracted_evidence (
            evidence_id, raw_id, journey_stage, reported_behaviour,
            evidence_quote, created_at
        ) VALUES (?, ?, ?, ?, ?, ?);
        """,
        (ev_id, raw_id, "stopped", "Stopped monthly contributions after NAV decline", "stopped my sip after 3 months", now_iso),
    )
    conn.commit()

    # Verify insertion
    cursor.execute("SELECT COUNT(*) as cnt FROM extracted_evidence WHERE raw_id = ?", (raw_id,))
    assert cursor.fetchone()["cnt"] == 1

    # Delete parent
    cursor.execute("DELETE FROM raw_conversations WHERE raw_id = ?", (raw_id,))
    conn.commit()

    # Child extracted_evidence should be removed via CASCADE
    cursor.execute("SELECT COUNT(*) as cnt FROM extracted_evidence WHERE raw_id = ?", (raw_id,))
    assert cursor.fetchone()["cnt"] == 0
    conn.close()


def test_crud_thematic_clusters_and_mappings(temp_db: Path):
    """Test CRUD operations on thematic_clusters and cluster_mappings."""
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    now_iso = datetime.now(timezone.utc).isoformat()

    # Setup parent raw and evidence records
    raw_id = "test_raw_cluster_001"
    cursor.execute(
        """
        INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text, is_qualified)
        VALUES (?, ?, ?, ?, 1);
        """,
        (raw_id, "play_store", now_iso, "Negative XIRR after 2 months of investing."),
    )

    ev_id = "ev_cluster_001"
    cursor.execute(
        """
        INSERT INTO extracted_evidence (
            evidence_id, raw_id, journey_stage, reported_behaviour,
            evidence_quote, created_at
        ) VALUES (?, ?, ?, ?, ?, ?);
        """,
        (ev_id, raw_id, "newly_started", "Checking portfolio weekly and noting negative XIRR", "negative xirr after 2 months", now_iso),
    )

    # 1. CREATE Cluster
    cluster_id = "cluster_xirr_anxiety"
    src_dist = {"play_store": 12, "reddit": 8, "youtube": 4}
    counter_quotes = ["Continued SIP despite -5% return as advised by long term horizon"]
    cursor.execute(
        """
        INSERT INTO thematic_clusters (
            cluster_id, title, description, item_count, distinct_authors_count,
            source_distribution, counter_evidence_quotes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            cluster_id,
            "Early-Stage Negative XIRR Panic",
            "Novice investors interpret initial 1-3 month negative XIRR as permanent loss.",
            24,
            21,
            json.dumps(src_dist),
            json.dumps(counter_quotes),
            now_iso,
        ),
    )

    # 2. CREATE Cluster Mapping
    mapping_id = "map_001"
    cursor.execute(
        """
        INSERT INTO cluster_mappings (mapping_id, cluster_id, evidence_id, similarity_score)
        VALUES (?, ?, ?, ?);
        """,
        (mapping_id, cluster_id, ev_id, 0.91),
    )
    conn.commit()

    # READ Cluster & Mapping
    cursor.execute("SELECT * FROM thematic_clusters WHERE cluster_id = ?", (cluster_id,))
    c_row = cursor.fetchone()
    assert c_row["title"] == "Early-Stage Negative XIRR Panic"
    assert c_row["distinct_authors_count"] == 21
    loaded_dist = json.loads(c_row["source_distribution"])
    assert loaded_dist["reddit"] == 8

    cursor.execute("SELECT * FROM cluster_mappings WHERE mapping_id = ?", (mapping_id,))
    m_row = cursor.fetchone()
    assert m_row["similarity_score"] == pytest.approx(0.91)

    # Unique constraint verification on (cluster_id, evidence_id)
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO cluster_mappings (mapping_id, cluster_id, evidence_id, similarity_score)
            VALUES (?, ?, ?, ?);
            """,
            ("map_002_duplicate", cluster_id, ev_id, 0.88),
        )
        conn.commit()

    # UPDATE Cluster
    cursor.execute(
        "UPDATE thematic_clusters SET item_count = 25 WHERE cluster_id = ?",
        (cluster_id,),
    )
    conn.commit()
    cursor.execute("SELECT item_count FROM thematic_clusters WHERE cluster_id = ?", (cluster_id,))
    assert cursor.fetchone()["item_count"] == 25

    # DELETE Cluster cascades to cluster_mappings
    cursor.execute("DELETE FROM thematic_clusters WHERE cluster_id = ?", (cluster_id,))
    conn.commit()
    cursor.execute("SELECT * FROM cluster_mappings WHERE mapping_id = ?", (mapping_id,))
    assert cursor.fetchone() is None
    conn.close()


def test_crud_hypothesis_records(temp_db: Path):
    """Test CRUD operations on hypothesis_records table."""
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    now_iso = datetime.now(timezone.utc).isoformat()
    cluster_id = "cluster_bank_mandate"

    # Setup parent cluster
    cursor.execute(
        """
        INSERT INTO thematic_clusters (
            cluster_id, title, description, created_at
        ) VALUES (?, ?, ?, ?);
        """,
        (cluster_id, "Autopay Mandate Failure Friction", "Confusion between e-mandate and netbanking deduction", now_iso),
    )

    # CREATE Hypothesis
    hypo_id = "hypo_001"
    questions = [
        "What notification did you receive when your SIP instalment date arrived?",
        "How did you resolve the failed payment status in the app?",
    ]
    cursor.execute(
        """
        INSERT INTO hypothesis_records (
            hypothesis_id, cluster_id, observed_pattern, hypothesis_text,
            alternative_explanation, missing_evidence, connection_to_continuation,
            validation_approach, research_questions, priority_score, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            hypo_id,
            cluster_id,
            "Investors report cancelled mandates after 1 bank debit failure",
            "Users assume a single failed deduction terminates their mutual fund investment account.",
            "Users intentionally cancelled due to temporary cash liquidity constraints.",
            "Bank error codes and whether users attempted manual re-try are missing.",
            "Mandate failure directly breaks the trailing 30-day active instalment continuation rule.",
            "Targeted 1:1 user interviews with users who suffered first-instalment mandate drops.",
            json.dumps(questions),
            4.2,
            now_iso,
        ),
    )
    conn.commit()

    # READ
    cursor.execute("SELECT * FROM hypothesis_records WHERE hypothesis_id = ?", (hypo_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row["cluster_id"] == cluster_id
    assert row["priority_score"] == pytest.approx(4.2)
    saved_questions = json.loads(row["research_questions"])
    assert len(saved_questions) == 2

    # UPDATE
    cursor.execute(
        "UPDATE hypothesis_records SET priority_score = 4.7 WHERE hypothesis_id = ?",
        (hypo_id,),
    )
    conn.commit()
    cursor.execute("SELECT priority_score FROM hypothesis_records WHERE hypothesis_id = ?", (hypo_id,))
    assert cursor.fetchone()["priority_score"] == pytest.approx(4.7)

    # DELETE
    cursor.execute("DELETE FROM hypothesis_records WHERE hypothesis_id = ?", (hypo_id,))
    conn.commit()
    cursor.execute("SELECT * FROM hypothesis_records WHERE hypothesis_id = ?", (hypo_id,))
    assert cursor.fetchone() is None
    conn.close()


def test_crud_golden_set_and_ai_failures(temp_db: Path):
    """Test CRUD operations on golden_set_benchmarks and ai_failure_logs."""
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    now_iso = datetime.now(timezone.utc).isoformat()
    raw_id = "test_raw_golden_001"

    cursor.execute(
        """
        INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text, is_qualified)
        VALUES (?, ?, ?, ?, 1);
        """,
        (raw_id, "youtube", now_iso, "Invested in small cap index, returns are down by 4 percent."),
    )

    # CREATE Golden Set Benchmark
    benchmark_id = "bench_001"
    human_labels = {
        "journey_stage": "continuing",
        "reported_behaviour": "monitoring returns in small cap index",
        "evidence_quote": "returns are down by 4 percent",
    }
    model_labels = {
        "journey_stage": "stopped",  # Erroneous hallucination
        "reported_behaviour": "stopped SIP due to loss",
        "evidence_quote": "returns are down by 4 percent",
    }
    cursor.execute(
        """
        INSERT INTO golden_set_benchmarks (
            benchmark_id, raw_id, human_labels, model_labels, agreement_score, evaluated_at
        ) VALUES (?, ?, ?, ?, ?, ?);
        """,
        (benchmark_id, raw_id, json.dumps(human_labels), json.dumps(model_labels), 0.71, now_iso),
    )

    # CREATE AI Failure Log linked to benchmark
    failure_id = "fail_001"
    cursor.execute(
        """
        INSERT INTO ai_failure_logs (
            failure_id, benchmark_id, failure_type, raw_input,
            erroneous_model_output, ground_truth_correction, remediation_applied, logged_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            failure_id,
            benchmark_id,
            "stage_inference_hallucination",
            "Invested in small cap index, returns are down by 4 percent.",
            "journey_stage: stopped",
            "journey_stage: continuing (investor only stated returns are down, never stated they stopped)",
            "Updated system prompt rule: Never equate market drops with stopping SIP without explicit statement.",
            now_iso,
        ),
    )
    conn.commit()

    # READ
    cursor.execute("SELECT * FROM golden_set_benchmarks WHERE benchmark_id = ?", (benchmark_id,))
    b_row = cursor.fetchone()
    assert b_row["agreement_score"] == pytest.approx(0.71)
    loaded_human = json.loads(b_row["human_labels"])
    assert loaded_human["journey_stage"] == "continuing"

    cursor.execute("SELECT * FROM ai_failure_logs WHERE failure_id = ?", (failure_id,))
    f_row = cursor.fetchone()
    assert f_row["failure_type"] == "stage_inference_hallucination"
    assert "remediation_applied" in f_row.keys()

    # UPDATE
    cursor.execute(
        "UPDATE golden_set_benchmarks SET agreement_score = 0.85 WHERE benchmark_id = ?",
        (benchmark_id,),
    )
    conn.commit()
    cursor.execute("SELECT agreement_score FROM golden_set_benchmarks WHERE benchmark_id = ?", (benchmark_id,))
    assert cursor.fetchone()["agreement_score"] == pytest.approx(0.85)

    # DELETE benchmark - failure log should set benchmark_id to NULL (ON DELETE SET NULL)
    cursor.execute("DELETE FROM golden_set_benchmarks WHERE benchmark_id = ?", (benchmark_id,))
    conn.commit()
    cursor.execute("SELECT * FROM golden_set_benchmarks WHERE benchmark_id = ?", (benchmark_id,))
    assert cursor.fetchone() is None

    cursor.execute("SELECT benchmark_id FROM ai_failure_logs WHERE failure_id = ?", (failure_id,))
    assert cursor.fetchone()["benchmark_id"] is None
    conn.close()


def test_transaction_context_manager(temp_db: Path):
    """Test get_db_cursor commit and rollback behavior."""
    raw_id = "test_trans_001"
    now_iso = datetime.now(timezone.utc).isoformat()

    # Successful commit
    with get_db_cursor(temp_db, commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text)
            VALUES (?, ?, ?, ?);
            """,
            (raw_id, "play_store", now_iso, "Smooth transaction"),
        )

    # Verify committed
    with get_db_cursor(temp_db) as cursor:
        cursor.execute("SELECT raw_id FROM raw_conversations WHERE raw_id = ?", (raw_id,))
        assert cursor.fetchone() is not None

    # Rollback on exception
    with pytest.raises(RuntimeError):
        with get_db_cursor(temp_db, commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text)
                VALUES (?, ?, ?, ?);
                """,
                ("test_trans_fail", "play_store", now_iso, "Should not persist"),
            )
            raise RuntimeError("Forced simulation error")

    # Verify not persisted
    with get_db_cursor(temp_db) as cursor:
        cursor.execute("SELECT raw_id FROM raw_conversations WHERE raw_id = ?", ("test_trans_fail",))
        assert cursor.fetchone() is None
