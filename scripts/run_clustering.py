"""Script to execute Phase 5: Pattern Discovery, Semantic Clustering & Counter-Evidence Synthesis.

Loads qualified extracted evidence from the database (>= 100 records), generates
embeddings, applies UMAP + HDBSCAN, synthesizes emergent qualitative themes,
surfaces contradictory counter-examples, and persists to thematic_clusters and cluster_mappings.
"""

import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.clustering.analyzer import ClusteringAnalyzer
from src.clustering.clusterer import SemanticClusterer
from src.clustering.embedder import EvidenceEmbedder
from src.clustering.synthesizer import ThemeSynthesizer
from src.database.connection import get_connection, get_db_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("groww_discovery.scripts.run_clustering")


def print_ascii_header(title: str, width: int = 80) -> None:
    print("\n" + "=" * width)
    print(f" {title.upper()}")
    print("=" * width)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Semantic Clustering & Counter-Evidence Synthesis"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to discovery_engine.db",
    )
    parser.add_argument(
        "--min-cluster-size",
        type=int,
        default=3,
        help="HDBSCAN min_cluster_size parameter (default: 3)",
    )
    args = parser.parse_args()

    db_file = get_db_path(args.db_path)
    print_ascii_header("Groww Discovery Engine: Phase 5 Semantic Clustering")
    print(f"Database Target: {db_file}")
    print(f"Timestamp:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Initialize Clustering Analyzer
    embedder = EvidenceEmbedder()
    clusterer = SemanticClusterer(min_cluster_size=args.min_cluster_size, min_samples=2)
    synthesizer = ThemeSynthesizer()
    analyzer = ClusteringAnalyzer(
        db_path=db_file,
        embedder=embedder,
        clusterer=clusterer,
        synthesizer=synthesizer,
    )

    # 2. Load evidence records
    print("\n[INFO] Loading extracted evidence records from database...")
    evidence_records = analyzer.load_evidence_records()
    total_records = len(evidence_records)
    print(f"[OK] Loaded {total_records} evidence records for clustering (Requirement: >= 100)")

    if total_records < 100:
        print(f"[WARNING] Corpus has {total_records} records, which is fewer than 100.")
    else:
        print(f"[PASSED] Qualified corpus size condition verified: {total_records} >= 100 records")

    # 3. Execute Semantic Clustering
    print("\n[INFO] Generating dense embeddings and executing UMAP + HDBSCAN clustering...")
    results = analyzer.run_clustering(records=evidence_records, persist_to_db=True)

    clusters = results["clusters"]
    mappings_count = results["mappings_count"]
    noise_count = results["noise_count"]

    print_ascii_header("Emergent Thematic Clusters & Counter-Evidence Synthesis")
    print(f"Discovered Themes: {len(clusters)} | Total Mapped Items: {mappings_count} | Noise/Outliers: {noise_count}\n")

    for i, cl in enumerate(clusters, 1):
        print(f"[{i}] THEME: {cl['title']}")
        print(f"    Description:        {cl['description']}")
        print(f"    Item Count:         {cl['item_count']} ({cl['dataset_prevalence_pct']}% prevalence)")
        print(f"    Unique Voices:      {cl['distinct_authors_count']} authors (UVR: {cl['unique_voice_ratio']})")
        print(f"    Platform Spread:    {cl['source_distribution']} (Dispersion: {cl['cross_source_dispersion']})")
        
        print("\n    Representative Supporting Verbatim Quotes:")
        for q in cl.get("representative_quotes", [])[:2]:
            print(f"     * \"{q}\"")

        print("\n    Contradictory Counter-Evidence Quotes (Alternative Outcomes):")
        counter_quotes = cl.get("counter_evidence_quotes", [])
        if counter_quotes:
            for cq in counter_quotes[:2]:
                print(f"     <!> \"{cq}\"")
        else:
            print("     <!> No direct contradictory outlier detected in local sample.")
        print("-" * 80)

    # 4. Export JSON artifact for UI / downstream consumption
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    export_path = processed_dir / "thematic_clusters.json"

    export_data = {
        "generated_at": datetime.now().isoformat(),
        "total_records_clustered": total_records,
        "themes_count": len(clusters),
        "mappings_count": mappings_count,
        "noise_count": noise_count,
        "themes": [
            {
                "cluster_id": cl["cluster_id"],
                "title": cl["title"],
                "description": cl["description"],
                "item_count": cl["item_count"],
                "distinct_authors_count": cl["distinct_authors_count"],
                "unique_voice_ratio": cl["unique_voice_ratio"],
                "dataset_prevalence_pct": cl["dataset_prevalence_pct"],
                "source_distribution": cl["source_distribution"],
                "cross_source_dispersion": cl["cross_source_dispersion"],
                "representative_quotes": cl["representative_quotes"],
                "counter_evidence_quotes": cl["counter_evidence_quotes"],
            }
            for cl in clusters
        ],
    }

    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Thematic clusters exported to: {export_path}")

    # 5. Database Table Verification
    conn = get_connection(db_file)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM thematic_clusters;")
    db_clusters = c.fetchone()[0]
    c.execute("SELECT count(*) FROM cluster_mappings;")
    db_mappings = c.fetchone()[0]
    conn.close()

    print_ascii_header("Phase 5 Database State Verification")
    print(f"thematic_clusters rows committed: {db_clusters}")
    print(f"cluster_mappings rows committed:  {db_mappings}")
    print("\n[OK] Phase 5 Semantic Clustering & Counter-Evidence Synthesis completed successfully.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
