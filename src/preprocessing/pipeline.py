"""Complete preprocessing pipeline orchestrating sanitization, deduplication, and qualification.

Executes the four-stage cleaning engine, writes auditable exclusion entries to
the SQLite exclusion_logs table, and marks validated conversations in raw_conversations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

from src.connectors.base import RawRecord
from src.database.connection import get_connection, get_db_path
from src.preprocessing.sanitizer import PIISanitizer
from src.preprocessing.deduplicator import Deduplicator
from src.preprocessing.qualifier import RelevanceClassifier

logger = logging.getLogger("groww_discovery.preprocessing.pipeline")


@dataclass
class PreprocessingResult:
    """Summary metrics and artifact containers produced by a preprocessing pipeline run."""
    total_input: int = 0
    pii_redacted_count: int = 0
    exact_duplicates_dropped: int = 0
    near_duplicates_dropped: int = 0
    irrelevant_dropped: int = 0
    qualified_count: int = 0
    qualified_records: List[RawRecord] = field(default_factory=list)
    exclusion_entries: List[Dict[str, Any]] = field(default_factory=list)


class PreprocessingPipeline:
    """Orchestrates end-to-end data cleaning, privacy masking, and qualification."""

    def __init__(
        self,
        sanitizer: Optional[PIISanitizer] = None,
        deduplicator: Optional[Deduplicator] = None,
        qualifier: Optional[RelevanceClassifier] = None,
    ):
        self.sanitizer = sanitizer or PIISanitizer()
        self.deduplicator = deduplicator or Deduplicator(near_duplicate_threshold=0.85)
        self.qualifier = qualifier or RelevanceClassifier()

    def process_records(
        self,
        records: List[RawRecord],
        db_path: Optional[Union[str, Path]] = None,
        sync_db: bool = True,
    ) -> PreprocessingResult:
        """Run all records through sanitization, deduplication, and qualification.

        Args:
            records: List of raw harvested conversations.
            db_path: Path to target SQLite database.
            sync_db: If True, commits updates and exclusion logs to database.

        Returns:
            PreprocessingResult with counts, qualified records, and exclusion entries.
        """
        result = PreprocessingResult(total_input=len(records))
        if not records:
            return result

        now_iso = datetime.now(timezone.utc).isoformat()
        sanitized_records: List[RawRecord] = []

        # Stage 1: PII Masking and Sanitization
        for rec in records:
            cleaned_rec, applied = self.sanitizer.sanitize_record(rec)
            if applied:
                result.pii_redacted_count += 1
            sanitized_records.append(cleaned_rec)

        # Stage 2: Relevance Qualification (filter non-SIP noise, short texts, F&O/crypto)
        relevant_candidates, excluded_records = self.qualifier.batch_qualify(sanitized_records)
        result.irrelevant_dropped = len(excluded_records)
        for rec, reason in excluded_records:
            result.exclusion_entries.append({
                "exclusion_id": f"excl_rel_{uuid.uuid4().hex[:12]}",
                "raw_id": rec.raw_id,
                "reason": reason,
                "excluded_at": now_iso,
            })

        # Stage 3: Deduplication (Exact + Near) on relevant candidates
        qualified_records, duplicate_entries = self.deduplicator.filter_records(relevant_candidates)
        result.qualified_count = len(qualified_records)
        result.qualified_records = qualified_records

        for dup in duplicate_entries:
            if dup["duplicate_type"] == "exact":
                result.exact_duplicates_dropped += 1
            else:
                result.near_duplicates_dropped += 1

            result.exclusion_entries.append({
                "exclusion_id": f"excl_dup_{uuid.uuid4().hex[:12]}",
                "raw_id": dup["raw_id"],
                "reason": dup["reason"],
                "excluded_at": now_iso,
            })

        # Stage 4: Database Synchronization (Audit Logging and Qualification Flags)
        if sync_db:
            self._sync_to_database(
                qualified_records=qualified_records,
                exclusion_entries=result.exclusion_entries,
                all_sanitized_records=sanitized_records,
                db_path=db_path,
            )

        logger.info(
            "Pipeline finished: %d in -> %d qualified (%d PII scrubbed, %d exact dupes, %d near dupes, %d irrelevant)",
            result.total_input,
            result.qualified_count,
            result.pii_redacted_count,
            result.exact_duplicates_dropped,
            result.near_duplicates_dropped,
            result.irrelevant_dropped,
        )
        return result

    def _sync_to_database(
        self,
        qualified_records: List[RawRecord],
        exclusion_entries: List[Dict[str, Any]],
        all_sanitized_records: List[RawRecord],
        db_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Persist qualification flags, updated sanitized text, and exclusion logs."""
        resolved_db = get_db_path(db_path)
        conn = get_connection(resolved_db)
        try:
            cursor = conn.cursor()

            # 1. Update sanitized text and reset is_qualified for all input records
            update_query = """
            UPDATE raw_conversations
            SET raw_text = ?, thread_context = ?, is_qualified = ?
            WHERE raw_id = ?;
            """
            qualified_ids = {r.raw_id for r in qualified_records}

            update_tuples = []
            for r in all_sanitized_records:
                is_qual = 1 if r.raw_id in qualified_ids else 0
                import json
                ctx_json = json.dumps(r.thread_context) if r.thread_context else None
                update_tuples.append((r.raw_text, ctx_json, is_qual, r.raw_id))

            cursor.executemany(update_query, update_tuples)

            # 2. Insert exclusion logs for dropped records
            if exclusion_entries:
                excl_query = """
                INSERT OR REPLACE INTO exclusion_logs (exclusion_id, raw_id, reason, excluded_at)
                VALUES (?, ?, ?, ?);
                """
                excl_tuples = [
                    (e["exclusion_id"], e["raw_id"], e["reason"], e["excluded_at"])
                    for e in exclusion_entries
                ]
                cursor.executemany(excl_query, excl_tuples)

            conn.commit()
            logger.info("Successfully synchronized preprocessing results to %s", resolved_db.name)
        except Exception as e:
            conn.rollback()
            logger.error("Failed database sync in preprocessing pipeline: %s", str(e), exc_info=True)
            raise
        finally:
            conn.close()

    def process_database(self, db_path: Optional[Union[str, Path]] = None) -> PreprocessingResult:
        """Load all records from SQLite raw_conversations and run the pipeline."""
        resolved_db = get_db_path(db_path)
        conn = get_connection(resolved_db)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raw_conversations;")
            rows = cursor.fetchall()
            records = [RawRecord.from_db_row(row) for row in rows]
        finally:
            conn.close()

        logger.info("Loaded %d raw conversations from database for processing", len(records))
        return self.process_records(records, db_path=resolved_db, sync_db=True)
