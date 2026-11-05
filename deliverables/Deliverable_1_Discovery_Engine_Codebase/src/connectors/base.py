"""Base abstractions and schemas for multi-source data ingestion connectors.

Implements the immutable RawRecord data contract and the BaseSourceConnector
class with author anonymization, SQLite persistence, and JSON export utilities.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from src.database.connection import get_connection

logger = logging.getLogger("groww_discovery.connectors")


class RawRecord(BaseModel):
    """Immutable data contract for ingested public conversations.

    Conforms to architecture specification Section 3.1 & Section 4.
    """
    raw_id: str = Field(..., description="Unique deterministic ID (e.g. playstore_com.groww_12345)")
    source_platform: str = Field(..., description="play_store | app_store | reddit | youtube | forum | file_import")
    source_url: Optional[str] = Field(default=None, description="Canonical public URL")
    author_id_hash: Optional[str] = Field(default=None, description="Salted SHA-256 hash of author username for privacy")
    published_at: Optional[datetime] = Field(default=None, description="Original publication timestamp")
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when record was harvested"
    )
    raw_text: str = Field(..., min_length=1, description="Unprocessed verbatim text from source")
    thread_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parent post title, video title, upvotes, ratings, etc."
    )
    product_context: str = Field(
        default="unknown",
        description="groww_specific | category_level | other_product_specific | unknown"
    )

    def to_db_tuple(self, is_qualified: int = 0) -> tuple:
        """Convert record to a tuple for SQLite raw_conversations insertion."""
        thread_json = json.dumps(self.thread_context) if self.thread_context is not None else None
        return (
            self.raw_id,
            self.source_platform,
            self.source_url,
            self.author_id_hash,
            self.published_at.isoformat() if self.published_at else None,
            self.collected_at.isoformat(),
            self.raw_text,
            thread_json,
            self.product_context,
            is_qualified,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict with ISO formatted datetimes."""
        data = self.model_dump()
        if self.published_at:
            data["published_at"] = self.published_at.isoformat()
        if self.collected_at:
            data["collected_at"] = self.collected_at.isoformat()
        return data

    @classmethod
    def from_db_row(cls, row: Any) -> "RawRecord":
        """Instantiate RawRecord from an SQLite sqlite3.Row object or dict."""
        thread_context = row["thread_context"]
        if isinstance(thread_context, str):
            try:
                thread_context = json.loads(thread_context)
            except Exception:
                thread_context = None

        pub_at = row["published_at"]
        if isinstance(pub_at, str):
            try:
                pub_at = datetime.fromisoformat(pub_at)
            except Exception:
                pub_at = None

        coll_at = row["collected_at"]
        if isinstance(coll_at, str):
            try:
                coll_at = datetime.fromisoformat(coll_at)
            except Exception:
                coll_at = datetime.now(timezone.utc)
        elif not isinstance(coll_at, datetime):
            coll_at = datetime.now(timezone.utc)

        return cls(
            raw_id=row["raw_id"],
            source_platform=row["source_platform"],
            source_url=row["source_url"],
            author_id_hash=row["author_id_hash"],
            published_at=pub_at,
            collected_at=coll_at,
            raw_text=row["raw_text"],
            thread_context=thread_context,
            product_context=row["product_context"] or "unknown",
        )


class BaseSourceConnector(ABC):
    """Abstract base class for all platform-specific ingestion adapters."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.salt = self.config.get("salt", "groww_discovery_salt_v1")

    @abstractmethod
    def fetch_records(self, **kwargs) -> List[RawRecord]:
        """Fetch raw items from external source and normalize to RawRecord objects.

        Must handle timeouts, rate-limits, and network anomalies gracefully.
        """
        pass

    def hash_author(self, author_name: Optional[str]) -> Optional[str]:
        """Generate a 16-character salted SHA-256 hash of the author's public handle.

        Ensures zero storage of raw usernames while preserving author uniqueness
        for distinct-author metrics in clustering.
        """
        if not author_name or not str(author_name).strip():
            return None
        normalized = str(author_name).strip().lower()
        salted_str = f"{self.salt}_{normalized}"
        return hashlib.sha256(salted_str.encode("utf-8")).hexdigest()[:16]

    def save_to_db(
        self,
        records: List[RawRecord],
        db_path: Optional[Union[str, Path]] = None,
        is_qualified: int = 0
    ) -> int:
        """Persist a list of RawRecord items into SQLite raw_conversations.

        Uses INSERT OR REPLACE to ensure idempotency. Returns count of rows affected.
        """
        if not records:
            return 0

        conn = get_connection(db_path)
        try:
            cursor = conn.cursor()
            query = """
            INSERT OR REPLACE INTO raw_conversations (
                raw_id, source_platform, source_url, author_id_hash,
                published_at, collected_at, raw_text, thread_context,
                product_context, is_qualified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            data_tuples = [r.to_db_tuple(is_qualified=is_qualified) for r in records]
            cursor.executemany(query, data_tuples)
            conn.commit()
            logger.info("Saved %d records to raw_conversations table", len(records))
            return len(records)
        except Exception as e:
            conn.rollback()
            logger.error("Failed to persist records to database: %s", str(e))
            raise
        finally:
            conn.close()

    def save_to_json(
        self,
        records: List[RawRecord],
        output_path: Union[str, Path]
    ) -> Path:
        """Export raw records to a JSON file for archival and debugging."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        serialized = [r.to_dict() for r in records]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)
        logger.info("Exported %d records to JSON at %s", len(records), path)
        return path
