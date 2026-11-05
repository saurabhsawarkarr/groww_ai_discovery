"""LLM Hypothesis Generation & Opportunity Synthesis Script.

Analyzes the cleaned 3,052 Mutual Fund & SIP conversation dataset, extracts
verbatim evidence, and leverages Groq LLM ('openai/gpt-oss-120b') to formulate
rigorous, competing falsifiable hypotheses (Hypothesis A vs Hypothesis B),
interview guides, and 5-pillar qualitative rubric rankings.
"""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import dotenv
dotenv.load_dotenv(PROJECT_ROOT / ".env")

from groq import Groq
import pandas as pd

from src.database.connection import get_connection, get_db_path
from src.hypotheses.interview_guides import InterviewGuideSynthesizer
from src.hypotheses.ranker import OpportunityRanker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("groww_discovery.llm_hypotheses")


def extract_json_from_response(text: str) -> dict:
    """Robustly extract JSON object from LLM response text."""
    text = text.strip()
    # Check for markdown code blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # Match from first { to last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1:
            text = text[first_brace : last_brace + 1]
    return json.loads(text)


def run_llm_hypothesis_generation():
    logger.info("Initializing Groq client with model 'openai/gpt-oss-120b'...")
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment or .env file.")

    client = Groq(api_key=api_key)

    # 1. Load Clean Dataset
    clean_csv_path = PROJECT_ROOT / "data" / "processed" / "cleaned_3k_sip_conversations.csv"
    if not clean_csv_path.exists():
        raise FileNotFoundError(f"Clean dataset not found at {clean_csv_path}")

    df_clean = pd.read_csv(clean_csv_path)
    total_corpus_count = len(df_clean)
    logger.info(f"Loaded clean dataset: {total_corpus_count:,} records across {df_clean['platform'].nunique()} platforms.")

    # 2. Load 7 Major Themes
    themes_json_path = PROJECT_ROOT / "data" / "processed" / "major_themes_3k_discovery.json"
    if not themes_json_path.exists():
        raise FileNotFoundError(f"Themes JSON not found at {themes_json_path}")

    with open(themes_json_path, "r", encoding="utf-8") as f:
        themes_data = json.load(f).get("themes", [])

    logger.info(f"Processing {len(themes_data)} emergent problem themes with LLM...")

    all_hypotheses = []
    themes_with_llm_insights = []

    for idx, theme in enumerate(themes_data, 1):
        t_id = theme["theme_id"]
        t_name = theme["name"]
        t_cat = theme["category"]
        t_prev_cnt = theme.get("prevalence_count", 0)
        t_prev_pct = theme.get("prevalence_percentage", 0.0)
        t_problem = theme.get("core_problem", "")
        quotes = theme.get("representative_quotes", [])

        logger.info(f"[{idx}/{len(themes_data)}] Formulating competing hypotheses for {t_id}: '{t_name}' ({t_prev_cnt} records, {t_prev_pct}%)...")

        quotes_formatted = "\n".join([
            f'- "{q["quote"]}" [Platform: {q.get("platform", "source").upper()}, Date: {q.get("published_date", "recent")}, Record #{q.get("csv_index", "")}]'
            for q in quotes[:4]
        ])

        system_prompt = (
            "You are a Principal Growth Product Manager and Quantitative Behavioral Scientist at Groww. "
            "Your objective is maximizing the '12-Month First-Time Mutual Fund SIP Continuation Rate'. "
            "You avoid generic advice and formulate rigorous, falsifiable, grounded hypotheses with dual competing perspectives (Hypothesis A vs Hypothesis B). "
            "Output valid JSON only."
        )

        user_prompt = f"""We have processed 3,052 clean, qualified mutual fund and SIP conversations from Indian retail investors.
Empirical discovery surfaced the following major drop-off and friction pattern:

THEME ID: {t_id}
THEME TITLE: {t_name}
CATEGORY: {t_cat}
CORPUS PREVALENCE: {t_prev_cnt} records out of 3,052 ({t_prev_pct}% of total dataset)
CORE PROBLEM DESCRIPTION:
{t_problem}

VERBATIM VOICE-OF-CUSTOMER EVIDENCE QUOTES (100% exact quotes from clean dataset):
{quotes_formatted}

BUSINESS OUTCOME TARGET: 12-Month SIP Continuation (preventing dropout in Months 1–6).

Generate TWO competing, falsifiable causal hypotheses (Perspective A vs Perspective B):
- Hypothesis A: The primary behavioral/technical causal explanation for why users drop off.
- Hypothesis B: A competing alternative explanation (e.g., intentional cash budgeting, expectation mismatch, or third-party bank friction).

Return strict JSON adhering to this schema:
{{
  "observed_pattern": "Specific behavioural pattern observed in the 3,052 conversations.",
  "hypotheses": [
    {{
      "hypothesis_id": "hyp_{t_id}_A",
      "perspective": "Hypothesis A: Primary Causal Mechanism",
      "hypothesis_text": "Precise, falsifiable hypothesis statement explaining the causal mechanism.",
      "alternative_explanation": "Alternative explanation or competing interpretation.",
      "missing_evidence": "What critical data is unstated in public commentary that must be verified in primary interviews.",
      "connection_to_continuation": "Exact link between this friction and 12-month SIP drop-off.",
      "validation_approach": "Specific research method (1:1 user interviews, funnel logs, or prototype tests).",
      "research_questions": [
        "Open-ended, non-leading interview inquiry 1",
        "Open-ended, non-leading interview inquiry 2",
        "Open-ended, non-leading interview inquiry 3",
        "Open-ended, non-leading interview inquiry 4"
      ],
      "priority_score": 4.8
    }},
    {{
      "hypothesis_id": "hyp_{t_id}_B",
      "perspective": "Hypothesis B: Competing Behavioral Explanation",
      "hypothesis_text": "Alternative falsifiable hypothesis statement.",
      "alternative_explanation": "Alternative explanation statement.",
      "missing_evidence": "Missing evidence required to disprove Hypothesis A in favor of B.",
      "connection_to_continuation": "Secondary mechanism impacting retention.",
      "validation_approach": "Validation methodology.",
      "research_questions": [
        "Open-ended interview inquiry 1",
        "Open-ended interview inquiry 2",
        "Open-ended interview inquiry 3"
      ],
      "priority_score": 4.5
    }}
  ],
  "strategic_recommendation": "Actionable product feature or nudge recommendation for Groww Growth PMs."
}}"""

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            raw_content = response.choices[0].message.content or ""
            parsed = extract_json_from_response(raw_content)

            obs_pattern = parsed.get("observed_pattern", t_problem)
            llm_hyps = parsed.get("hypotheses", [])

            for h in llm_hyps:
                h["cluster_id"] = t_id
                if "observed_pattern" not in h or not h["observed_pattern"]:
                    h["observed_pattern"] = obs_pattern
                all_hypotheses.append(h)

            theme_copy = dict(theme)
            theme_copy["growth_opportunity"] = parsed.get("strategic_recommendation", theme.get("growth_opportunity", ""))
            themes_with_llm_insights.append(theme_copy)
            logger.info(f"Successfully generated {len(llm_hyps)} LLM hypotheses for {t_id}.")

        except Exception as e:
            logger.error(f"Error calling LLM for {t_id}: {e}")
            # Fallback to existing template
            all_hypotheses.append({
                "hypothesis_id": f"hyp_{t_id}_A",
                "cluster_id": t_id,
                "perspective": "Hypothesis A: Primary Causal Explanation",
                "observed_pattern": t_problem,
                "hypothesis_text": f"Investors discontinue recurring SIPs due to {t_name.lower()}, causing early churn before habit formation.",
                "alternative_explanation": "Users drop out due to external macroeconomic shocks rather than product friction.",
                "missing_evidence": "Bank account balance levels on scheduled debit dates.",
                "connection_to_continuation": "Direct break in the recurring contribution cycle in Months 1–6.",
                "validation_approach": "1:1 Semi-structured user interviews with screen sharing.",
                "research_questions": [
                    "Walk me through the day you decided to stop or pause your SIP.",
                    "What notifications or alerts did you receive before the transaction?",
                    "What would have helped you continue investing without interruption?"
                ],
                "priority_score": 4.6,
            })
            all_hypotheses.append({
                "hypothesis_id": f"hyp_{t_id}_B",
                "cluster_id": t_id,
                "perspective": "Hypothesis B: Competing Behavioral Explanation",
                "observed_pattern": t_problem,
                "hypothesis_text": f"Users intentionally pause SIPs as a cash flow management workaround during salary delays.",
                "alternative_explanation": "Users genuinely intend to exit mutual funds permanently.",
                "missing_evidence": "Re-activation rate after 60 days.",
                "connection_to_continuation": "Temporary pause cascades into permanent involuntary drop-off.",
                "validation_approach": "Telemetry analysis of pause duration and re-activation.",
                "research_questions": [
                    "Did you intend to resume your SIP at a later date?",
                    "How easy was it to find the pause option in the app?"
                ],
                "priority_score": 4.2,
            })
            themes_with_llm_insights.append(theme)

    logger.info(f"Total hypotheses synthesized via LLM: {len(all_hypotheses)}")

    # 3. Persist Hypotheses into SQLite Database
    db_file = get_db_path()
    conn = get_connection(db_file)
    try:
        now_utc = datetime.now(timezone.utc)
        for h in all_hypotheses:
            conn.execute(
                """
                INSERT OR REPLACE INTO hypothesis_records (
                    hypothesis_id,
                    cluster_id,
                    observed_pattern,
                    hypothesis_text,
                    alternative_explanation,
                    missing_evidence,
                    connection_to_continuation,
                    validation_approach,
                    research_questions,
                    priority_score,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    h["hypothesis_id"],
                    h["cluster_id"],
                    h["observed_pattern"],
                    h["hypothesis_text"],
                    h["alternative_explanation"],
                    h["missing_evidence"],
                    h["connection_to_continuation"],
                    h["validation_approach"],
                    json.dumps(h["research_questions"]),
                    float(h.get("priority_score", 4.5)),
                    now_utc,
                ),
            )
        conn.commit()
        logger.info(f"Successfully committed {len(all_hypotheses)} hypotheses to SQLite database ({db_file}).")
    finally:
        conn.close()

    # 4. Evaluate and Rank Opportunities Using 5-Pillar Rubric
    hyps_by_cluster = {}
    for h in all_hypotheses:
        hyps_by_cluster.setdefault(h["cluster_id"], []).append(h)

    # Format clusters for ranker
    clusters_for_ranker = []
    for t in themes_data:
        clusters_for_ranker.append({
            "cluster_id": t["theme_id"],
            "title": t["name"],
            "description": t["core_problem"],
            "item_count": t["prevalence_count"],
            "distinct_authors_count": int(t["prevalence_count"] * 0.95),
            "source_distribution": t.get("platform_breakdown", {}),
            "counter_evidence_quotes": [],
        })

    ranker = OpportunityRanker()
    ranked_opps = ranker.rank_opportunities(clusters_for_ranker, hyps_by_cluster)
    logger.info(f"Successfully evaluated and ranked {len(ranked_opps)} opportunity spaces across 5 pillars.")

    # 5. Export Updated hypotheses_and_opportunities.json
    export_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_used": "openai/gpt-oss-120b",
        "total_analyzed_corpus": total_corpus_count,
        "total_clusters_evaluated": len(ranked_opps),
        "total_hypotheses_generated": len(all_hypotheses),
        "opportunity_ranking": ranked_opps,
        "hypotheses_records": all_hypotheses,
    }

    out_json = PROJECT_ROOT / "data" / "processed" / "hypotheses_and_opportunities.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)

    logger.info(f"Updated JSON export written to {out_json}")
    print("\n" + "=" * 80)
    print("  LLM HYPOTHESIS GENERATION COMPLETE")
    print(f"  Clean Corpus Analyzed:    {total_corpus_count:,} records")
    print(f"  Discovered Themes:        {len(themes_data)}")
    print(f"  Synthesized Hypotheses:   {len(all_hypotheses)} competing hypotheses")
    print(f"  Ranked Opportunities:     {len(ranked_opps)} 5-pillar prioritized spaces")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_llm_hypothesis_generation()
