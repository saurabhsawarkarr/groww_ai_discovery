"""Unit tests for multi-source ingestion connectors and the RawRecord schema contract.

Validates:
- Strict Pydantic RawRecord validation
- Salted SHA-256 author privacy hashing
- Play Store connector normalization and error recovery
- App Store connector normalization
- Reddit connector fallback and authentication handling
- YouTube connector graceful degradation
- File importer flexibility across CSV and JSON
- SQLite idempotency via save_to_db
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.connectors.base import BaseSourceConnector, RawRecord
from src.connectors.play_store import PlayStoreConnector
from src.connectors.app_store import AppStoreConnector
from src.connectors.reddit import RedditConnector
from src.connectors.youtube import YouTubeConnector
from src.connectors.file_importer import FileImporterConnector
from src.database.connection import get_connection, init_db


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Fixture providing initialized SQLite test database."""
    db_file = tmp_path / "test_connectors.db"
    init_db(db_path=db_file)
    return db_file


def test_raw_record_schema_validation():
    """Verify that RawRecord strictly enforces required fields and types."""
    now = datetime.now(timezone.utc)
    rec = RawRecord(
        raw_id="playstore_com.groww_001",
        source_platform="play_store",
        source_url="https://play.google.com/store/apps/details?id=com.groww",
        author_id_hash="abc123def4567890",
        published_at=now,
        collected_at=now,
        raw_text="Simple SIP interface but returns took 2 days to reflect.",
        thread_context={"score": 4, "version": "14.2"},
        product_context="groww_specific",
    )

    assert rec.raw_id == "playstore_com.groww_001"
    assert rec.source_platform == "play_store"
    assert rec.product_context == "groww_specific"

    # Test database tuple conversion
    db_tuple = rec.to_db_tuple(is_qualified=1)
    assert len(db_tuple) == 10
    assert db_tuple[0] == rec.raw_id
    assert db_tuple[9] == 1

    # Test reconstruction from database row
    row_dict = {
        "raw_id": rec.raw_id,
        "source_platform": rec.source_platform,
        "source_url": rec.source_url,
        "author_id_hash": rec.author_id_hash,
        "published_at": rec.published_at.isoformat(),
        "collected_at": rec.collected_at.isoformat(),
        "raw_text": rec.raw_text,
        "thread_context": json.dumps(rec.thread_context),
        "product_context": rec.product_context,
        "is_qualified": 1,
    }
    reconstructed = RawRecord.from_db_row(row_dict)
    assert reconstructed.raw_id == rec.raw_id
    assert reconstructed.thread_context == rec.thread_context


def test_raw_record_validation_failures():
    """Verify that invalid records raise Pydantic validation errors."""
    with pytest.raises(Exception):
        # Missing raw_text
        RawRecord(
            raw_id="rec_001",
            source_platform="reddit",
        )

    with pytest.raises(Exception):
        # Empty text
        RawRecord(
            raw_id="rec_002",
            source_platform="reddit",
            raw_text="",
        )


def test_author_hashing():
    """Verify salted SHA-256 author privacy hashing."""
    connector = PlayStoreConnector(config={"salt": "test_salt_123"})
    h1 = connector.hash_author("investor_rahul")
    h2 = connector.hash_author("investor_rahul")
    h3 = connector.hash_author("INVESTOR_RAHUL ")  # Normalized case and whitespace

    assert h1 is not None
    assert len(h1) == 16
    assert h1 == h2
    assert h1 == h3

    # Different author must produce different hash
    h_other = connector.hash_author("investor_priya")
    assert h1 != h_other

    # None and empty strings should yield None
    assert connector.hash_author(None) is None
    assert connector.hash_author("") is None
    assert connector.hash_author("   ") is None


def test_play_store_connector_mock():
    """Verify PlayStoreConnector normalization with simulated review data."""
    fake_reviews = [
        {
            "reviewId": "rev_mock_001",
            "userName": "Amit Kumar",
            "content": "Negative returns on first SIP after 2 months. Uninstalled.",
            "score": 1,
            "thumbsUpCount": 14,
            "reviewCreatedVersion": "12.0.1",
            "at": datetime(2026, 3, 15, 10, 0, 0, tzinfo=timezone.utc),
            "replyContent": "Hi Amit, please note that mutual funds fluctuate in the short term.",
            "repliedAt": datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc),
        }
    ]

    with patch("src.connectors.play_store.reviews", return_value=(fake_reviews, None)):
        connector = PlayStoreConnector(config={"app_id": "com.nextbillion.groww"})
        records = connector.fetch_records(count=1)

        assert len(records) == 1
        rec = records[0]
        assert rec.raw_id == "playstore_com.nextbillion.groww_rev_mock_001"
        assert rec.source_platform == "play_store"
        assert rec.product_context == "groww_specific"
        assert rec.author_id_hash is not None
        assert rec.thread_context["score"] == 1
        assert "Negative returns" in rec.raw_text


def test_play_store_connector_error_handling():
    """Verify PlayStoreConnector gracefully recovers from network exceptions."""
    with patch("src.connectors.play_store.reviews", side_effect=ConnectionError("Simulated network timeout")):
        connector = PlayStoreConnector()
        records = connector.fetch_records(count=5)
        assert records == []


def test_app_store_connector_mock():
    """Verify AppStoreConnector normalization and deterministic ID generation."""
    fake_reviews = [
        {
            "review": "Autopay deduction on 5th failed without notification.",
            "date": datetime(2026, 4, 10, 8, 30, 0, tzinfo=timezone.utc),
            "userName": "VikramS",
            "rating": 2,
            "title": "Mandate deduction issue",
            "isEdited": False,
        }
    ]

    with patch("src.connectors.app_store.AppStore") as mock_app_store_cls:
        instance = mock_app_store_cls.return_value
        instance.reviews = fake_reviews

        connector = AppStoreConnector(config={"app_name": "groww", "app_id": 1404871703})
        records = connector.fetch_records(how_many=1)

        assert len(records) == 1
        rec = records[0]
        assert rec.source_platform == "app_store"
        assert rec.product_context == "groww_specific"
        assert rec.raw_id.startswith("appstore_1404871703_")
        assert rec.thread_context["rating"] == 2
        assert "Autopay deduction" in rec.raw_text


def test_reddit_connector_fallback_dataset():
    """Verify RedditConnector loads all 50 curated pilot samples when offline."""
    connector = RedditConnector(config={"salt": "pilot_test_salt"})
    records = connector.fetch_records()

    assert len(records) == 50
    for r in records:
        assert isinstance(r, RawRecord)
        assert r.source_platform == "reddit"
        assert r.raw_id.startswith("reddit_pilot_")
        assert len(r.raw_text.split()) >= 4
        assert r.thread_context is not None
        assert "parent_title" in r.thread_context
        assert "subreddit" in r.thread_context


def test_youtube_connector_graceful_missing_key():
    """Verify YouTubeConnector returns empty or fallback gracefully when API key is missing."""
    connector = YouTubeConnector(config={"api_key": None})
    records = connector.fetch_records()
    assert isinstance(records, list)


def test_file_importer_csv(tmp_path: Path):
    """Verify FileImporterConnector imports CSV with custom columns."""
    csv_file = tmp_path / "external_forum.csv"
    csv_content = """review_id,user,comment,rating,source_url
post_101,Suresh,Started my first Rs 1000 SIP today in Nifty 50,5,https://forum.tradingqna.com/t/101
post_102,Deepa,Why did my SIP deduction fail with code 05?,1,https://forum.tradingqna.com/t/102
"""
    csv_file.write_text(csv_content, encoding="utf-8")

    importer = FileImporterConnector(config={"default_platform": "forum"})
    records = importer.import_file(csv_file)

    assert len(records) == 2
    assert records[0].raw_id == "post_101"
    assert records[0].source_platform == "forum"
    assert records[0].source_url == "https://forum.tradingqna.com/t/101"
    assert "Started my first Rs 1000 SIP" in records[0].raw_text
    assert records[0].author_id_hash is not None
    assert records[0].thread_context["rating"] == 5


def test_file_importer_json(tmp_path: Path):
    """Verify FileImporterConnector imports JSON records."""
    json_file = tmp_path / "raw_dump.json"
    data = [
        {
            "id": "json_01",
            "text": "XIRR is confusing for new investors in year 1.",
            "author": "Ankit",
            "platform": "reddit",
            "url": "https://reddit.com/r/mutualfunds/comments/1",
        }
    ]
    json_file.write_text(json.dumps(data), encoding="utf-8")

    importer = FileImporterConnector()
    records = importer.import_file(json_file)

    assert len(records) == 1
    assert records[0].raw_id == "json_01"
    assert records[0].source_platform == "reddit"
    assert "XIRR is confusing" in records[0].raw_text


def test_save_to_db_idempotency(temp_db: Path):
    """Verify save_to_db stores records and handles duplicates idempotently."""
    connector = PlayStoreConnector()
    rec = RawRecord(
        raw_id="playstore_com.groww_dup_test",
        source_platform="play_store",
        raw_text="SIP investment completed cleanly.",
        product_context="groww_specific",
    )

    # First save
    saved_cnt = connector.save_to_db([rec], db_path=temp_db)
    assert saved_cnt == 1

    # Second save with same raw_id (should not throw IntegrityError, should update)
    rec.raw_text = "Updated comment text for idempotency check."
    saved_cnt_2 = connector.save_to_db([rec], db_path=temp_db)
    assert saved_cnt_2 == 1

    conn = get_connection(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT raw_text FROM raw_conversations WHERE raw_id = ?", (rec.raw_id,))
    row = cursor.fetchone()
    assert row["raw_text"] == "Updated comment text for idempotency check."
    conn.close()
