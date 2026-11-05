"""Script to execute the Phase 1 Pilot Ingestion.

Harvests 50 records from Google Play Store and 50 records from Reddit,
validates all records against the RawRecord contract, saves raw JSON copies,
and commits them to the SQLite database.
"""

import logging
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.table import Table

from src.connectors.play_store import PlayStoreConnector
from src.connectors.reddit import RedditConnector
from src.connectors.base import RawRecord
from src.database.connection import get_connection, get_db_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pilot_ingestion")
console = Console()


def run_pilot():
    console.print("\n[bold cyan]======================================================[/bold cyan]")
    console.print("[bold cyan] Groww Discovery Engine: Phase 1 Pilot Ingestion [/bold cyan]")
    console.print("[bold cyan]======================================================[/bold cyan]\n")

    db_path = get_db_path()
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ingest from Google Play Store
    console.print("[yellow]1. Harvesting 50 items from Google Play Store (com.nextbillion.groww)...[/yellow]")
    play_connector = PlayStoreConnector(config={"app_id": "com.nextbillion.groww", "country": "in", "lang": "en"})
    play_records = play_connector.fetch_records(count=50)
    console.print(f"   [green][OK] Fetched {len(play_records)} Play Store records[/green]")

    # Save Play Store raw JSON
    play_json_path = raw_dir / "play_store_pilot.json"
    play_connector.save_to_json(play_records, play_json_path)

    # 2. Ingest from Reddit
    console.print("[yellow]2. Harvesting 50 items from Reddit (r/IndiaInvestments, r/mutualfunds)...[/yellow]")
    reddit_connector = RedditConnector()
    reddit_records = reddit_connector.fetch_records()
    console.print(f"   [green][OK] Fetched {len(reddit_records)} Reddit records[/green]")

    # Save Reddit raw JSON
    reddit_json_path = raw_dir / "reddit_pilot.json"
    reddit_connector.save_to_json(reddit_records, reddit_json_path)

    all_records = play_records + reddit_records

    # 3. Validate Schema Conformance
    console.print("\n[yellow]3. Validating all records against RawRecord schema...[/yellow]")
    invalid_count = 0
    for idx, r in enumerate(all_records):
        try:
            assert isinstance(r, RawRecord)
            assert r.raw_id and len(r.raw_id) > 0
            assert r.source_platform in ["play_store", "reddit"]
            assert r.raw_text and len(r.raw_text.strip()) > 0
        except Exception as e:
            invalid_count += 1
            logger.error("Record %d failed validation: %s", idx, str(e))

    if invalid_count == 0:
        console.print(f"   [green][OK] 100% of records ({len(all_records)}/{len(all_records)}) passed strict RawRecord validation![/green]")
    else:
        console.print(f"   [red][FAILED] {invalid_count} records failed validation![/red]")
        return 1

    # 4. Commit to SQLite Database
    console.print(f"\n[yellow]4. Persisting records to SQLite database: {db_path.name}...[/yellow]")
    saved_play = play_connector.save_to_db(play_records, db_path=db_path)
    saved_reddit = reddit_connector.save_to_db(reddit_records, db_path=db_path)
    total_saved = saved_play + saved_reddit
    console.print(f"   [green][OK] Successfully committed {total_saved} records to 'raw_conversations'[/green]")

    # 5. Query and Display Summary Table
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source_platform, product_context, COUNT(*) as cnt
        FROM raw_conversations
        GROUP BY source_platform, product_context;
    """)
    rows = cursor.fetchall()
    conn.close()

    table = Table(title="Database 'raw_conversations' Status")
    table.add_column("Source Platform", style="cyan")
    table.add_column("Product Context", style="magenta")
    table.add_column("Record Count", style="green")

    for row in rows:
        table.add_row(row["source_platform"], row["product_context"], str(row["cnt"]))

    console.print()
    console.print(table)
    console.print(f"\n[bold green][OK] Phase 1 Pilot Ingestion Completed Successfully! Total items in DB: {total_saved}[/bold green]\n")
    return 0


if __name__ == "__main__":
    exit(run_pilot())
