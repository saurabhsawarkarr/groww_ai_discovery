"""Harvest expanded data from Google Play Store, App Store, Reddit, and YouTube,
and update the Groww Discovery Engine end-to-end.

Stages:
1. Multi-source harvesting (Google Play Store live, iOS App Store, Reddit, YouTube)
2. Ingest and persist raw records to raw_conversations table
3. 4-stage Cleaning & Qualification pipeline (PII redaction, deduplication, noise filtering)
4. Structured Evidence Extraction via Groq LLM with 100% verbatim quote verification
5. Unsupervised pattern clustering and thematic synthesis
6. Competing hypotheses generation and 5-pillar qualitative ranking
7. Re-synthesis of Deliverables 1 through 4
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from google_play_scraper import Sort

from src.connectors.play_store import PlayStoreConnector
from src.connectors.file_importer import FileImporterConnector
from src.connectors.base import RawRecord
from src.database.connection import get_connection, get_db_path
from src.preprocessing.pipeline import PreprocessingPipeline
from src.extraction.orchestrator import ExtractionOrchestrator
from src.clustering.analyzer import ClusteringAnalyzer
from src.hypotheses.generator import HypothesisGenerator
from src.hypotheses.ranker import OpportunityRanker
from src.exporter.export_all import export_all_deliverables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("groww_discovery.harvest_expanded")


def get_existing_raw_ids() -> set:
    """Fetch existing raw_id set from SQLite raw_conversations."""
    seen_ids = set()
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT raw_id FROM raw_conversations;")
        for r in c.fetchall():
            seen_ids.add(r[0])
    finally:
        conn.close()
    return seen_ids


def harvest_play_store_batches(seen_ids: set) -> list:
    """Fetch multiple batches of Google Play Store reviews across ratings and sorts."""
    connector = PlayStoreConnector()
    all_harvested = []

    batches = [
        {"name": "Most Relevant (Overall)", "count": 150, "sort": Sort.MOST_RELEVANT, "filter": None},
        {"name": "Newest Reviews (Overall)", "count": 150, "sort": Sort.NEWEST, "filter": None},
        {"name": "1-Star Reviews (High Churn / Failures)", "count": 120, "sort": Sort.NEWEST, "filter": 1},
        {"name": "2-Star Reviews (Friction / Cancellation)", "count": 100, "sort": Sort.NEWEST, "filter": 2},
        {"name": "3-Star Reviews (XIRR / Confusion)", "count": 100, "sort": Sort.NEWEST, "filter": 3},
        {"name": "4-Star Reviews (Feature Requests)", "count": 80, "sort": Sort.NEWEST, "filter": 4},
        {"name": "5-Star Reviews (Long-term Retention)", "count": 80, "sort": Sort.NEWEST, "filter": 5},
    ]

    for b in batches:
        logger.info("Harvesting Play Store batch: %s (target: %d)...", b["name"], b["count"])
        try:
            records = connector.fetch_records(
                count=b["count"],
                sort=b["sort"],
                filter_score_with=b["filter"],
            )
            new_in_batch = 0
            for r in records:
                if r.raw_id not in seen_ids:
                    seen_ids.add(r.raw_id)
                    all_harvested.append(r)
                    new_in_batch += 1
            logger.info("-> Added %d new records (total new Play Store: %d)", new_in_batch, len(all_harvested))
        except Exception as e:
            logger.error("Failed batch %s: %s", b["name"], str(e))

    return all_harvested


def harvest_file_batches(seen_ids: set) -> list:
    """Harvest new community discussions from expanded raw JSON datasets."""
    importer = FileImporterConnector()
    all_harvested = []

    raw_dir = PROJECT_ROOT / "data" / "raw"
    target_files = [
        raw_dir / "reddit_expanded.json",
        raw_dir / "app_store_expanded.json",
        raw_dir / "youtube_expanded.json",
    ]

    for fpath in target_files:
        if not fpath.exists():
            continue
        try:
            records = importer.import_file(fpath)
            new_in_batch = 0
            for r in records:
                if r.raw_id not in seen_ids:
                    seen_ids.add(r.raw_id)
                    all_harvested.append(r)
                    new_in_batch += 1
            logger.info("Harvested file %s: +%d new records", fpath.name, new_in_batch)
        except Exception as e:
            logger.error("Failed importing %s: %s", fpath.name, str(e))

    return all_harvested


def main():
    start_time = time.time()
    db_file = get_db_path()

    print("\n" + "=" * 80)
    print("  MULTI-SOURCE EXPANDED DATA COLLECTION & PIPELINE SYNTHESIS")
    print("=" * 80)
    print(f"Target Database: {db_file}")

    seen_ids = get_existing_raw_ids()
    print(f"[INFO] Existing database has {len(seen_ids)} raw records.")

    # 1. Harvest new raw records from all sources
    new_raw_records = []
    
    # 1a. Google Play Store (Live)
    play_records = harvest_play_store_batches(seen_ids)
    new_raw_records.extend(play_records)

    # 1b. Expanded files (Reddit, App Store, YouTube)
    file_records = harvest_file_batches(seen_ids)
    new_raw_records.extend(file_records)

    if new_raw_records:
        print(f"\n[OK] Harvested {len(new_raw_records)} brand new unique records across sources:")
        print(f"  - Play Store (Live):   {len(play_records)}")
        print(f"  - Community / Files:   {len(file_records)}")

        # 2. Persist newly harvested records into raw_conversations FIRST (satisfies foreign keys)
        logger.info("Persisting %d new records into raw_conversations table...", len(new_raw_records))
        connector = PlayStoreConnector()
        connector.save_to_db(new_raw_records, db_path=db_file, is_qualified=0)
        print(f"[OK] Persisted {len(new_raw_records)} raw records to SQLite raw_conversations.")

        # 3. Run Cleaning & Qualification Pipeline
        logger.info("Running 4-stage Cleaning & Qualification pipeline...")
        pipeline = PreprocessingPipeline()
        prep_result = pipeline.process_records(new_raw_records, db_path=db_file, sync_db=True)

        print(f"\n[OK] Preprocessing complete:")
        print(f"  - Total Ingested:      {prep_result.total_input}")
        print(f"  - PII Masked:          {prep_result.pii_redacted_count}")
        print(f"  - Duplicates Dropped:  {prep_result.exact_duplicates_dropped + prep_result.near_duplicates_dropped}")
        print(f"  - Irrelevant Dropped:  {prep_result.irrelevant_dropped}")
        print(f"  - Newly Qualified:     {prep_result.qualified_count}")
    else:
        print("[INFO] No brand new raw records fetched; checking for unextracted qualified records in database...")

    # 4. Extract Evidence for ANY qualified records missing from extracted_evidence
    conn = get_connection(db_file)
    try:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM raw_conversations r 
            WHERE r.is_qualified = 1 AND r.raw_id NOT IN (SELECT raw_id FROM extracted_evidence);
        """)
        rows = c.fetchall()
        unextracted_records = [RawRecord.from_db_row(r) for r in rows]
    finally:
        conn.close()

    if unextracted_records:
        logger.info(
            "Extracting structured evidence for %d qualified records without evidence...",
            len(unextracted_records)
        )
        orchestrator = ExtractionOrchestrator()
        new_evidence = orchestrator.extract_batch(
            unextracted_records, db_path=db_file, sync_db=True
        )
        print(f"[OK] Extracted and committed {len(new_evidence)} new structured evidence records!")
    else:
        print("[INFO] All qualified records already have extracted evidence in database.")

    # 5. Re-run Pattern Discovery & Clustering over full dataset
    logger.info("Re-running unsupervised clustering over updated corpus...")
    analyzer = ClusteringAnalyzer(db_path=db_file)
    clusters_result = analyzer.run_clustering(persist_to_db=True)
    active_clusters = analyzer.get_clusters_from_db()
    print(f"[OK] Pattern discovery updated: {len(active_clusters)} active thematic clusters.")

    # 6. Re-generate Competing Hypotheses & 5-Pillar Ranking
    logger.info("Updating competing hypotheses and 5-pillar qualitative ranking...")
    generator = HypothesisGenerator(db_path=db_file)
    all_hyps = []
    for thm in active_clusters:
        hyps = generator.generate_hypotheses_for_theme(thm)
        all_hyps.extend(hyps)
    generator.save_hypotheses_to_db(all_hyps)

    hyps_by_cluster = {}
    for h in all_hyps:
        hyps_by_cluster.setdefault(h["cluster_id"], []).append(h)
    ranker = OpportunityRanker()
    ranked_opps = ranker.rank_opportunities(active_clusters, hyps_by_cluster)
    print(f"[OK] Ranked {len(ranked_opps)} opportunity spaces across 5 qualitative pillars.")

    # 7. Re-export all deliverables
    logger.info("Re-synthesizing Deliverables 1 through 4...")
    export_all_deliverables(project_root=PROJECT_ROOT, db_path=db_file)
    print("[OK] Deliverables 1-4 regenerated with updated dataset numbers!")

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("  DATA COLLECTION & SYNTHESIS COMPLETE")
    print(f"  Total Duration: {elapsed:.2f}s")
    print("=" * 80 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
