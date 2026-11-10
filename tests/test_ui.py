"""Unit tests for Phase 7: Growth PM Research & Audit Dashboard UI."""

from datetime import datetime, timezone
import os
from pathlib import Path
import tempfile
import pytest

from src.database.connection import get_connection, init_db
from src.ui.app import load_system_stats
from src.ui.components.explorer import update_review_status


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


class TestUIDashboard:
    """Test dashboard stats loading and human-in-the-loop review updates."""

    def test_load_system_stats_empty_and_seeded(self, temp_db):
        # Empty DB stats
        stats = load_system_stats(temp_db)
        assert stats["total_raw"] == 0
        assert stats["total_evidence"] == 0
        assert stats["total_clusters"] == 0

        # Seed rows
        conn = get_connection(temp_db)
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text, is_qualified)
            VALUES ('raw_001', 'play_store', ?, 'Review text', 1);
            """,
            (now_iso,),
        )
        conn.execute(
            """
            INSERT INTO extracted_evidence (evidence_id, raw_id, journey_stage, reported_behaviour, evidence_quote, created_at)
            VALUES ('ev_001', 'raw_001', 'newly_started', 'Started SIP', 'Started SIP quote', ?);
            """,
            (now_iso,),
        )
        conn.commit()
        conn.close()

        load_system_stats.clear()
        updated_stats = load_system_stats(temp_db)
        assert updated_stats["total_raw"] == 1
        assert updated_stats["total_qual"] == 1
        assert updated_stats["total_evidence"] == 1

    def test_update_review_status_human_in_the_loop(self, temp_db):
        conn = get_connection(temp_db)
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text, is_qualified)
            VALUES ('raw_hil_001', 'reddit', ?, 'Reddit post', 1);
            """,
            (now_iso,),
        )
        conn.execute(
            """
            INSERT INTO extracted_evidence (evidence_id, raw_id, journey_stage, reported_behaviour, evidence_quote, review_status, created_at)
            VALUES ('ev_hil_001', 'raw_hil_001', 'continuing', 'Continuing SIP', 'Continuing SIP quote', 'unreviewed', ?);
            """,
            (now_iso,),
        )
        conn.commit()
        conn.close()

        # Update to accepted
        update_review_status("ev_hil_001", "accepted", db_path=temp_db)

        conn = get_connection(temp_db)
        c = conn.cursor()
        c.execute("SELECT review_status FROM extracted_evidence WHERE evidence_id = 'ev_hil_001';")
        status = c.fetchone()[0]
        conn.close()

        assert status == "accepted"

        # Update to rejected
        update_review_status("ev_hil_001", "rejected", db_path=temp_db)

        conn = get_connection(temp_db)
        c = conn.cursor()
        c.execute("SELECT review_status FROM extracted_evidence WHERE evidence_id = 'ev_hil_001';")
        status = c.fetchone()[0]
        conn.close()

        assert status == "rejected"

    def test_format_source_link_html_safety_and_external_target(self):
        from src.ui.components.common_ui import format_source_link_html

        valid_html = format_source_link_html("https://tradingqna.com/t/penalty-over-missed-sip/120657")
        assert 'href="https://tradingqna.com/t/penalty-over-missed-sip/120657"' in valid_html
        assert 'target="_blank"' in valid_html
        assert 'rel="noopener noreferrer"' in valid_html

        assert format_source_link_html("https://www.reddit.com/r/mutualfunds/comments/142_pause_feature_missing_in_amc") == ""
        assert format_source_link_html("javascript:alert(1)") == ""
        assert format_source_link_html("") == ""
