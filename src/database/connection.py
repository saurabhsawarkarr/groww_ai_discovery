"""Database connection, initialization, and session management module.

Provides thread-safe connections to the local SQLite database, schema migration
execution, context managers for transactions, and configuration path resolution.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional, Union
import yaml


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "configs" / "config.yaml"
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
DEFAULT_DB_REL_PATH = "data/database/discovery_engine.db"


def _adapt_datetime_iso(dt: datetime) -> str:
    """Adapt python datetime to ISO8601 string for SQLite storage."""
    return dt.isoformat()


def _convert_timestamp_iso(val: bytes) -> datetime:
    """Convert SQLite stored timestamp bytes to python datetime."""
    text = val.decode("utf-8")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        # Fallback for standard space separator
        return datetime.fromisoformat(text.replace(" ", "T"))


sqlite3.register_adapter(datetime, _adapt_datetime_iso)
sqlite3.register_converter("timestamp", _convert_timestamp_iso)
sqlite3.register_converter("TIMESTAMP", _convert_timestamp_iso)


def get_db_path(custom_path: Optional[Union[str, Path]] = None) -> Path:
    """Resolve the absolute SQLite database path.

    Order of precedence:
    1. Explicit custom_path argument
    2. DATABASE_PATH environment variable
    3. configs/config.yaml database.path setting
    4. Default relative path (data/database/discovery_engine.db)
    """
    if custom_path:
        db_path = Path(custom_path)
    elif "DATABASE_PATH" in os.environ and os.environ["DATABASE_PATH"].strip():
        db_path = Path(os.environ["DATABASE_PATH"].strip())
    elif DEFAULT_CONFIG_PATH.exists():
        try:
            with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
            cfg_path = config_data.get("database", {}).get("path")
            if cfg_path:
                project_root = DEFAULT_CONFIG_PATH.parent.parent
                db_path = project_root / cfg_path
            else:
                project_root = DEFAULT_CONFIG_PATH.parent.parent
                db_path = project_root / DEFAULT_DB_REL_PATH
        except Exception:
            project_root = Path(__file__).resolve().parent.parent.parent
            db_path = project_root / DEFAULT_DB_REL_PATH
    else:
        project_root = Path(__file__).resolve().parent.parent.parent
        db_path = project_root / DEFAULT_DB_REL_PATH

    # Normalize and ensure directory exists
    db_path = db_path.resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """Create and return a configured SQLite database connection.

    Enforces foreign key constraints and configures row factory to sqlite3.Row
    for dict-like and index-based access.
    """
    resolved_path = get_db_path(db_path)
    conn = sqlite3.connect(
        str(resolved_path),
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")  # Write-Ahead Logging for high concurrency
    return conn


@contextmanager
def get_db_cursor(
    db_path: Optional[Union[str, Path]] = None, commit: bool = True
) -> Generator[sqlite3.Cursor, None, None]:
    """Context manager for acquiring a database cursor and managing transactions.

    Commits automatically on normal exit if commit=True, and rolls back on error.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def execute_script(
    script_sql: str, db_path: Optional[Union[str, Path]] = None
) -> None:
    """Execute a raw SQL script containing multiple statements."""
    conn = get_connection(db_path)
    try:
        conn.executescript(script_sql)
        conn.commit()
    finally:
        conn.close()


def get_table_names(db_path: Optional[Union[str, Path]] = None) -> list[str]:
    """Retrieve list of existing table names in the database."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def init_db(
    db_path: Optional[Union[str, Path]] = None,
    schema_path: Optional[Union[str, Path]] = None,
    drop_tables: bool = False,
) -> None:
    """Initialize database schema from schema.sql.

    Args:
        db_path: Path to SQLite DB file. Defaults to resolved config path.
        schema_path: Path to schema.sql file. Defaults to src/database/schema.sql.
        drop_tables: If True, drops all existing engine tables prior to recreation.
    """
    resolved_db_path = get_db_path(db_path)
    resolved_schema_path = (
        Path(schema_path).resolve() if schema_path else DEFAULT_SCHEMA_PATH
    )

    if not resolved_schema_path.exists():
        raise FileNotFoundError(
            f"Database schema file not found at: {resolved_schema_path}"
        )

    with open(resolved_schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection(resolved_db_path)
    try:
        if drop_tables:
            # Drop in reverse dependency order
            tables_to_drop = [
                "ai_failure_logs",
                "golden_set_benchmarks",
                "hypothesis_records",
                "cluster_mappings",
                "thematic_clusters",
                "extracted_evidence",
                "exclusion_logs",
                "raw_conversations",
            ]
            cursor = conn.cursor()
            for tbl in tables_to_drop:
                cursor.execute(f"DROP TABLE IF EXISTS {tbl};")
            conn.commit()

        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    db_file = get_db_path()
    print(f"Initializing database at: {db_file}")
    init_db()
    tables = get_table_names()
    print(f"Database initialized successfully with {len(tables)} tables:")
    for t in tables:
        print(f" - {t}")
