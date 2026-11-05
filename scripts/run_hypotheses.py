"""Script to execute Phase 6: Hypotheses Generation & 5-Pillar Opportunity Prioritization.

Loads thematic clusters from the database, formulates competing falsifiable hypotheses,
synthesizes targeted 1:1 primary research interview guides, evaluates opportunities
against the 5-pillar qualitative rubric, and commits records to hypothesis_records.
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
from src.database.connection import get_connection, get_db_path
from src.hypotheses.generator import HypothesisGenerator
from src.hypotheses.interview_guides import InterviewGuideSynthesizer
from src.hypotheses.ranker import OpportunityRanker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("groww_discovery.scripts.run_hypotheses")


def print_ascii_header(title: str, width: int = 80) -> None:
    print("\n" + "=" * width)
    print(f" {title.upper()}")
    print("=" * width)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Hypotheses Generation & 5-Pillar Opportunity Prioritization"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to discovery_engine.db",
    )
    args = parser.parse_args()

    db_file = get_db_path(args.db_path)
    print_ascii_header("Groww Discovery Engine: Phase 6 Opportunity Prioritization")
    print(f"Database Target: {db_file}")
    print(f"Timestamp:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Load clusters from database
    print("\n[INFO] Loading thematic clusters from database...")
    analyzer = ClusteringAnalyzer(db_path=db_file)
    themes = analyzer.get_clusters_from_db()
    print(f"[OK] Loaded {len(themes)} thematic clusters from SQLite")

    if not themes:
        print("[FAILED] No thematic clusters found in database. Run Phase 5 first.")
        return 1

    # 2. Formulate Competing Hypotheses & Primary Interview Guides
    generator = HypothesisGenerator(db_path=db_file)
    guide_synthesizer = InterviewGuideSynthesizer()
    ranker = OpportunityRanker()

    all_hypotheses = []
    hypotheses_by_cluster = {}
    interview_guides = []

    print("\n[INFO] Generating dual competing hypotheses and interview guides for each theme...")
    for theme in themes:
        cid = theme["cluster_id"]
        hyps = generator.generate_hypotheses_for_theme(theme)
        all_hypotheses.extend(hyps)
        hypotheses_by_cluster[cid] = hyps

        # Generate 1:1 primary user interview protocol
        guide = guide_synthesizer.generate_guide(
            cluster_id=cid,
            theme_title=theme["title"],
            observed_pattern=hyps[0]["observed_pattern"],
            hypothesis_a=hyps[0]["hypothesis_text"],
            hypothesis_b=hyps[1]["hypothesis_text"],
            core_questions=hyps[0]["research_questions"],
        )
        interview_guides.append(guide)

    guide_by_cluster = {g["cluster_id"]: g for g in interview_guides}

    # 3. Persist Hypotheses to SQLite
    print(f"[INFO] Committing {len(all_hypotheses)} hypothesis records to hypothesis_records...")
    inserted_ids = generator.persist_hypotheses(all_hypotheses)
    print(f"[OK] Persisted {len(inserted_ids)} records to hypothesis_records table")

    # 4. Rank Opportunities across the 5 Pillars
    print("\n[INFO] Evaluating and ranking opportunity spaces across 5 qualitative pillars...")
    ranked_opportunities = ranker.rank_opportunities(themes, hypotheses_by_cluster)

    # 5. Output Ranked Opportunity Matrix
    print_ascii_header("5-Pillar Ranked Opportunity Spaces (Growth PM Decision Matrix)")
    print(f"{'Rank':<5} | {'Cluster':<8} | {'Priority Tier':<32} | {'Score':>6} | {'Opportunity Title'}")
    print("-" * 5 + "-+-" + "-" * 8 + "-+-" + "-" * 32 + "-+-" + "-" * 6 + "-+-" + "-" * 35)

    for opp in ranked_opportunities:
        title_snippet = opp["title"][:45] + ("..." if len(opp["title"]) > 45 else "")
        print(f"#{opp['rank']:<4} | {opp['cluster_id']:<8} | {opp['priority_tier']:<32} | {opp['priority_score']:>6.2f} | {title_snippet}")

    # Detailed Opportunity Breakdown
    print_ascii_header("Detailed Opportunity Cards & Dual Competing Hypotheses")
    for opp in ranked_opportunities[:4]:
        cid = opp["cluster_id"]
        hyps = hypotheses_by_cluster.get(cid, [])
        p = opp["pillars"]

        print(f"\n[RANK #{opp['rank']}] {opp['title'].upper()} (Score: {opp['priority_score']}/5.0 - {opp['priority_tier']})")
        print(f"Cluster ID: {cid}")
        print(f"5-Pillar Qualitative Assessment:")
        print(f"  * Prevalence:              [{p['prevalence']['tier']}] {p['prevalence']['rationale']}")
        print(f"  * User Impact:             [{p['user_impact']['tier']}] {p['user_impact']['rationale']}")
        print(f"  * 12M Business Relevance:  [{p['business_relevance_12m']['tier']}] {p['business_relevance_12m']['rationale']}")
        print(f"  * Evidence Quality:        [{p['evidence_quality']['tier']}] {p['evidence_quality']['rationale']}")
        print(f"  * Product Addressability:  [{p['product_addressability']['tier']}] {p['product_addressability']['rationale']}")

        if len(hyps) >= 2:
            print(f"\nCompeting Falsifiable Hypotheses:")
            print(f"  [A] {hyps[0]['perspective']}:")
            print(f"      \"{hyps[0]['hypothesis_text']}\"")
            print(f"      Validation: {hyps[0]['validation_approach']}")
            print(f"  [B] {hyps[1]['perspective']}:")
            print(f"      \"{hyps[1]['hypothesis_text']}\"")
            print(f"      Validation: {hyps[1]['validation_approach']}")
            print(f"  Missing Evidence: {hyps[0]['missing_evidence']}")

            guide_obj = guide_by_cluster.get(cid, {})
            screener_snippet = guide_obj.get("target_participant_screener", "")[:80]
            print(f"\nTargeted Primary Interview Questions (Screener: {screener_snippet}...):")
            for q_idx, q in enumerate(hyps[0]["research_questions"][:3], 1):
                print(f"    {q_idx}. \"{q}\"")
        print("-" * 80)

    # 6. Export Full JSON Artifact
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    export_path = processed_dir / "hypotheses_and_opportunities.json"

    export_payload = {
        "generated_at": datetime.now().isoformat(),
        "total_clusters_evaluated": len(themes),
        "total_hypotheses_generated": len(all_hypotheses),
        "opportunity_ranking": ranked_opportunities,
        "interview_guides": interview_guides,
    }

    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Hypotheses and Opportunity Ranking exported to: {export_path}")

    # 7. Database State Verification
    conn = get_connection(db_file)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM hypothesis_records;")
    db_hyp_count = c.fetchone()[0]
    conn.close()

    print_ascii_header("Phase 6 Database State Verification")
    print(f"hypothesis_records rows committed: {db_hyp_count} (Requirement: >= 2 per theme)")
    print("\n[OK] Phase 6 Hypotheses Generation & Prioritization completed successfully.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
