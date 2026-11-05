"""File importer connector for local CSV, JSON, and JSONL data files.

Enables reproducible offline testing, benchmark data loading, and ingestion
of external community dumps (e.g. TradingQ&A forums, Reddit archival exports).
"""

import csv
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from src.connectors.base import BaseSourceConnector, RawRecord

logger = logging.getLogger("groww_discovery.connectors.file_importer")

TEXT_ALIASES = ["raw_text", "text", "content", "comment", "review", "body", "message", "selftext"]
ID_ALIASES = ["raw_id", "id", "review_id", "comment_id", "post_id"]
PLATFORM_ALIASES = ["source_platform", "platform", "source"]
URL_ALIASES = ["source_url", "url", "link", "permalink"]
AUTHOR_ALIASES = ["author_id_hash", "author", "user", "username", "userName", "author_name"]
DATE_ALIASES = ["published_at", "date", "created_at", "timestamp", "time", "at"]
PRODUCT_ALIASES = ["product_context", "product", "context"]


class FileImporterConnector(BaseSourceConnector):
    """Ingestion connector for local files (CSV, JSON, JSONL, XLSX)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.default_platform = self.config.get("default_platform", "file_import")

    def _find_field_value(self, row: Dict[str, Any], aliases: List[str]) -> Optional[Any]:
        """Find value in row dictionary matching any alias (case-insensitive)."""
        lower_keys = {k.lower(): k for k in row.keys()}
        for alias in aliases:
            if alias.lower() in lower_keys:
                orig_key = lower_keys[alias.lower()]
                val = row[orig_key]
                if val is not None and not (isinstance(val, float) and pd.isna(val)):
                    return val
        return None

    def _normalize_dict_record(
        self,
        raw_dict: Dict[str, Any],
        file_path: Path,
        index: int
    ) -> Optional[RawRecord]:
        """Convert a raw dictionary from CSV/JSON into a validated RawRecord."""
        raw_text = self._find_field_value(raw_dict, TEXT_ALIASES)
        if not raw_text or not str(raw_text).strip():
            return None
        clean_text = str(raw_text).strip()

        platform = (
            self._find_field_value(raw_dict, PLATFORM_ALIASES)
            or self.default_platform
        )

        raw_id = self._find_field_value(raw_dict, ID_ALIASES)
        if not raw_id:
            digest = hashlib.sha256(f"{file_path.stem}_{index}_{clean_text[:64]}".encode()).hexdigest()[:12]
            raw_id = f"{platform}_{file_path.stem}_{digest}"
        else:
            raw_id = str(raw_id)

        source_url = self._find_field_value(raw_dict, URL_ALIASES)
        if source_url:
            source_url = str(source_url)

        author_val = self._find_field_value(raw_dict, AUTHOR_ALIASES)
        author_hash = None
        if author_val:
            author_str = str(author_val)
            # If already a 16-hex hash, preserve, else hash
            if len(author_str) == 16 and all(c in "0123456789abcdefABCDEF" for c in author_str):
                author_hash = author_str.lower()
            else:
                author_hash = self.hash_author(author_str)

        date_val = self._find_field_value(raw_dict, DATE_ALIASES)
        published_at = None
        if date_val:
            if isinstance(date_val, datetime):
                published_at = date_val if date_val.tzinfo else date_val.replace(tzinfo=timezone.utc)
            elif isinstance(date_val, str):
                try:
                    published_at = datetime.fromisoformat(date_val.replace("Z", "+00:00"))
                except Exception:
                    pass

        product_context = self._find_field_value(raw_dict, PRODUCT_ALIASES)
        if not product_context:
            product_context = "groww_specific" if "groww" in clean_text.lower() else "category_level"
        else:
            product_context = str(product_context)

        # Collect extra fields into thread_context
        mapped_keys = set()
        for alias_list in [TEXT_ALIASES, ID_ALIASES, PLATFORM_ALIASES, URL_ALIASES, AUTHOR_ALIASES, DATE_ALIASES, PRODUCT_ALIASES]:
            for a in alias_list:
                for k in raw_dict.keys():
                    if k.lower() == a.lower():
                        mapped_keys.add(k)

        thread_ctx = {
            k: v for k, v in raw_dict.items()
            if k not in mapped_keys and not (isinstance(v, float) and pd.isna(v))
        }
        thread_ctx["file_source"] = file_path.name

        return RawRecord(
            raw_id=raw_id,
            source_platform=platform,
            source_url=source_url,
            author_id_hash=author_hash,
            published_at=published_at,
            collected_at=datetime.now(timezone.utc),
            raw_text=clean_text,
            thread_context=thread_ctx if thread_ctx else None,
            product_context=product_context,
        )

    def import_file(self, file_path: Union[str, Path]) -> List[RawRecord]:
        """Read a single CSV, JSON, or JSONL file and convert to RawRecord list."""
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Input file does not exist: {path}")

        records: List[RawRecord] = []
        suffix = path.suffix.lower()

        logger.info("Importing records from %s (%s)", path.name, suffix)

        if suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for idx, item in enumerate(data):
                    if isinstance(item, dict):
                        rec = self._normalize_dict_record(item, path, idx)
                        if rec:
                            records.append(rec)
            elif isinstance(data, dict):
                # Might have a top-level key like "data" or "records"
                items = data.get("records") or data.get("data") or [data]
                for idx, item in enumerate(items):
                    if isinstance(item, dict):
                        rec = self._normalize_dict_record(item, path, idx)
                        if rec:
                            records.append(rec)

        elif suffix == ".jsonl":
            with open(path, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if line:
                        item = json.loads(line)
                        rec = self._normalize_dict_record(item, path, idx)
                        if rec:
                            records.append(rec)

        elif suffix in [".csv", ".tsv"]:
            delimiter = "\t" if suffix == ".tsv" else ","
            df = pd.read_csv(path, sep=delimiter)
            for idx, row in df.iterrows():
                rec = self._normalize_dict_record(row.to_dict(), path, idx)
                if rec:
                    records.append(rec)

        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
            for idx, row in df.iterrows():
                rec = self._normalize_dict_record(row.to_dict(), path, idx)
                if rec:
                    records.append(rec)

        else:
            raise ValueError(f"Unsupported file format: {suffix}")

        logger.info("Successfully parsed and validated %d records from %s", len(records), path.name)
        return records

    def fetch_records(self, file_path: Optional[Union[str, Path]] = None, **kwargs) -> List[RawRecord]:
        """Implement abstract method by delegating to import_file."""
        target_path = file_path or self.config.get("file_path")
        if not target_path:
            raise ValueError("file_path must be provided to FileImporterConnector.fetch_records")
        return self.import_file(target_path)
