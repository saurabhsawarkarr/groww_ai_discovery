"""Script to execute Phase 2: Cleaning, PII Masking & Relevance Qualification.

Runs the PreprocessingPipeline across raw conversations stored in the database,
logs exclusions into exclusion_logs, marks qualified records with is_qualified=1,
and exports the clean qualified dataset to data/processed/qualified_conversations.json.
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.table import Table

from src.database.connection import get_connection, get_db_path
from src.preprocessing.pipeline import PreprocessingPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("preprocessing_runner")
console = Console()


def run_preprocessing():
    console.print("\n[bold cyan]============================================================[/bold cyan]")
    console.print("[bold cyan] Groww Discovery Engine: Phase 2 Preprocessing Pipeline [/bold cyan]")
    console.print("[bold cyan]============================================================[/bold cyan]\n")

    db_path = get_db_path()
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[yellow]Connecting to database at: {db_path.name}...[/yellow]")
    pipeline = PreprocessingPipeline()
    result = pipeline.process_database(db_path=db_path)

    # Export qualified records to data/processed/
    qualified_export_path = processed_dir / "qualified_conversations.json"
    exported_data = [r.to_dict() for r in result.qualified_records]
    with open(qualified_export_path, "w", encoding="utf-8") as f:
        json.dump(exported_data, f, indent=2, ensure_ascii=False)

    console.print(f"[green][OK] Exported {len(exported_data)} qualified records to {qualified_export_path}[/green]\n")

    # Display Metrics Table
    summary_table = Table(title="Phase 2 Preprocessing & Qualification Results")
    summary_table.add_column("Pipeline Metric", style="cyan")
    summary_table.add_column("Count", style="green", justify="right")

    summary_table.add_row("Total Raw Records Ingested", str(result.total_input))
    summary_table.add_row("PII Tokens Redacted", str(result.pii_redacted_count))
    summary_table.add_row("Exact Duplicates Dropped", str(result.exact_duplicates_dropped))
    summary_table.add_row("Near Duplicates Dropped (>= 0.85)", str(result.near_duplicates_dropped))
    summary_table.add_row("Irrelevant Domains / Noise Dropped", str(result.irrelevant_dropped))
    summary_table.add_row("[bold]Qualified Conversations Committed[/bold]", f"[bold green]{result.qualified_count}[/bold green]")

    console.print(summary_table)

    # Display Database Audit
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM exclusion_logs;")
    excl_cnt = cursor.fetchone()["cnt"]

    cursor.execute("""
        SELECT is_qualified, COUNT(*) as cnt
        FROM raw_conversations
        GROUP BY is_qualified;
    """)
    qual_rows = cursor.fetchall()
    conn.close()

    db_table = Table(title="Database Table State Verification")
    db_table.add_column("Status / Flag", style="magenta")
    db_table.add_column("Count in DB", style="yellow", justify="right")

    for r in qual_rows:
        label = "Qualified (is_qualified = 1)" if r["is_qualified"] == 1 else "Excluded (is_qualified = 0)"
        db_table.add_row(label, str(r["cnt"]))
    db_table.add_row("Total Exclusion Log Entries", str(excl_cnt))

    console.print()
    console.print(db_table)
    console.print(f"\n[bold green][OK] Phase 2 Preprocessing Pipeline Completed Successfully![/bold green]\n")
    return 0


if __name__ == "__main__":
    exit(run_preprocessing())
