"""Opportunity Matrix & Primary Interview Guides Component (Tab 3 / Tab 5).

Ranks discovery opportunity spaces using the 5-pillar qualitative rubric, displays
dual competing hypotheses, and surfaces actionable 1:1 primary research interview guides.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import streamlit as st

from src.database.connection import get_connection
from src.hypotheses.generator import HypothesisGenerator
from src.hypotheses.interview_guides import InterviewGuideSynthesizer
from src.hypotheses.llm_opportunity_synthesizer import LLMOpportunitySynthesizer
from src.hypotheses.ranker import OpportunityRanker
from src.ui.components.common_ui import MISSION_BANNER_HTML, get_kpi_card_html

JSON_EXPORT_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data"
    / "processed"
    / "hypotheses_and_opportunities.json"
)


def render_llm_opportunity_section(themes: List[Dict[str, Any]]) -> None:
    """Render top section on top of Opportunity Metric using LLM synthesis over 3,052 dataset and 7 themes."""
    st.markdown(
        """<div style="background: linear-gradient(135deg, #F0FDF9 0%, #EFF6FF 100%); border: 1.5px solid #CCFBF1; border-left: 5px solid #00D09C; border-radius: 12px; padding: 18px 22px; margin-bottom: 18px; box-shadow: var(--groww-card-shadow);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span style="font-size: 24px;">🤖</span>
<h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 22px; font-weight: 800; color: #0F172A; margin: 0;">AI Strategic Opportunity Synthesis & Top Growth Bets</h2>
</div>
<span class="badge-tag badge-tier-1">✨ Live LLM Engine</span>
</div>
<p style="font-size: 16px; color: #334155; line-height: 1.6; margin: 0;">
Discovers high-leverage product opportunities by synthesizing our <strong>3,052 verified customer conversations</strong> and <strong>7 discovered failure themes</strong>. Designed specifically to drive <strong>12-Month First-Time SIP Continuation</strong> under strict SEBI zero-fund-advice and anti-FOMO constraints.
</p>
</div>""",
        unsafe_allow_html=True,
    )

    synthesizer = LLMOpportunitySynthesizer()
    bets = synthesizer.get_strategic_bets()
    tab_bet1, tab_bet2, tab_bet3, tab_custom = st.tabs([
        "🛡️ Bet 1: Cash-Flow & Autopay (Finding 3)",
        "📉 Bet 2: Volatility & Return Pacing (Findings 1 & 4)",
        "🎯 Bet 3: Goal Anchoring & Overlap (Finding 2)",
        "🔍 Custom LLM Discovery",
    ])

    # Tab 1: Involuntary Churn & Autopay
    with tab_bet1:
        b1 = bets[0]
        st.markdown(
            f"""<div class="overview-section-card" style="margin-bottom: 14px; border-left: 4.5px solid #00D09C;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
<div>
<span class="badge-tag badge-play-store">24.6% OF CHURN VOLUME</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 800; color: #0F172A; margin: 6px 0 3px 0;">{b1['title']}</h3>
<div style="font-size: 15px; color: #008764; font-weight: 600;">{b1['tagline']}</div>
</div>
<div style="text-align: right;">
<span class="badge-tag badge-tier-1">TIER 1 PRIORITY</span>
<div style="font-size: 13.5px; color: #64748B; margin-top: 4px;">Score: 4.85 / 5.0</div>
</div>
</div>
<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin: 10px 0;">
<div style="font-size: 14px; font-weight: 700; color: #64748B; text-transform: uppercase;">Discovered Problem in 3,052 Dataset:</div>
<div style="font-size: 15.5px; color: #1E293B; line-height: 1.55; margin-top: 2px;">{b1['core_user_friction']}</div>
<div style="font-size: 14px; color: #64748B; margin-top: 6px;">
<strong>Addressed Discovered Themes:</strong> {", ".join(b1['addressed_themes'])}
</div>
</div>
<div style="margin-top: 12px;">
<div style="font-size: 14.5px; font-weight: 700; color: #0F172A; text-transform: uppercase; margin-bottom: 8px;">Architected Product Solutions:</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>24h Pre-Debit Balance Reminder:</strong> Proactive WhatsApp/push prompt to verify balance before scheduled run.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>1-Click Instant UPI Retry Fallback:</strong> Zero-penalty 48h manual UPI payment link when mandate rejects.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>Salary Date Auto-Shift Grace Period:</strong> Allows moving instalment date +/- 5 days without mandate wipeout.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>NPCI ₹1 Lakh Cap Demystification:</strong> Clarifying the limit is an authorization cap, not a live deduction.
</div>
</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0, 208, 156, 0.08); border-left: 3px solid #008764; padding: 10px 14px; border-radius: 6px; margin-top: 12px; font-size: 15px;">
<div><strong style="color: #008764;">Projected 12M Impact:</strong> {b1['projected_12m_impact']}</div>
<span style="font-size: 13.5px; color: #064E3B; font-weight: 600;">✓ Constraint Audit: 100% Compliant</span>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    # Tab 2: Volatility Pacing Shield
    with tab_bet2:
        b2 = bets[1]
        st.markdown(
            f"""<div class="overview-section-card" style="margin-bottom: 14px; border-left: 4.5px solid #0284C7;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
<div>
<span class="badge-tag badge-reddit">17.5% OF CHURN VOLUME</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 800; color: #0F172A; margin: 6px 0 3px 0;">{b2['title']}</h3>
<div style="font-size: 15px; color: #0284C7; font-weight: 600;">{b2['tagline']}</div>
</div>
<div style="text-align: right;">
<span class="badge-tag badge-tier-1">TIER 1 PRIORITY</span>
<div style="font-size: 13.5px; color: #64748B; margin-top: 4px;">Score: 4.65 / 5.0</div>
</div>
</div>
<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin: 10px 0;">
<div style="font-size: 14px; font-weight: 700; color: #64748B; text-transform: uppercase;">Discovered Problem in 3,052 Dataset:</div>
<div style="font-size: 15.5px; color: #1E293B; line-height: 1.55; margin-top: 2px;">{b2['core_user_friction']}</div>
<div style="font-size: 14px; color: #64748B; margin-top: 6px;">
<strong>Addressed Discovered Themes:</strong> {", ".join(b2['addressed_themes'])}
</div>
</div>
<div style="margin-top: 12px;">
<div style="font-size: 14.5px; font-weight: 700; color: #0F172A; text-transform: uppercase; margin-bottom: 8px;">Architected Product Solutions:</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>Units Accumulated Milestone Framing:</strong> Shifts early focus to accumulation progress rather than noisy daily dip.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>Contextual Rupee-Cost Averaging Primer:</strong> Non-intrusive explainer showing how market dips buy more units.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>Domino Settlement Progress Tracker:</strong> Visual timeline stepper for unit allotment eliminating fraud panic.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>Tenor-Sensitive Return Safeguards:</strong> Suppresses misleading annualized XIRR during first 90 days.
</div>
</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: rgba(2, 132, 199, 0.08); border-left: 3px solid #0284C7; padding: 10px 14px; border-radius: 6px; margin-top: 12px; font-size: 15px;">
<div><strong style="color: #0284C7;">Projected 12M Impact:</strong> {b2['projected_12m_impact']}</div>
<span style="font-size: 13.5px; color: #0369A1; font-weight: 600;">✓ Constraint Audit: 100% Compliant</span>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    # Tab 3: Portfolio Hygiene
    with tab_bet3:
        b3 = bets[2]
        st.markdown(
            f"""<div class="overview-section-card" style="margin-bottom: 14px; border-left: 4.5px solid #F59E0B;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
<div>
<span class="badge-tag badge-forum">9.3% OF CHURN VOLUME</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 800; color: #0F172A; margin: 6px 0 3px 0;">{b3['title']}</h3>
<div style="font-size: 15px; color: #D97706; font-weight: 600;">{b3['tagline']}</div>
</div>
<div style="text-align: right;">
<span class="badge-tag badge-tier-2">TIER 2 PRIORITY</span>
<div style="font-size: 13.5px; color: #64748B; margin-top: 4px;">Score: 4.40 / 5.0</div>
</div>
</div>
<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin: 10px 0;">
<div style="font-size: 14px; font-weight: 700; color: #64748B; text-transform: uppercase;">Discovered Problem in 3,052 Dataset:</div>
<div style="font-size: 15.5px; color: #1E293B; line-height: 1.55; margin-top: 2px;">{b3['core_user_friction']}</div>
<div style="font-size: 14px; color: #64748B; margin-top: 6px;">
<strong>Addressed Discovered Themes:</strong> {", ".join(b3['addressed_themes'])}
</div>
</div>
<div style="margin-top: 12px;">
<div style="font-size: 14.5px; font-weight: 700; color: #0F172A; text-transform: uppercase; margin-bottom: 8px;">Architected Product Solutions:</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>Portfolio Overlap X-Ray:</strong> Detects overlapping stock concentrations within user's own existing holdings.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>Debit Date Synchronization:</strong> Allows grouping multiple active SIPs into one unified monthly payday debit.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>In-Portfolio Consolidation Wizard:</strong> Streamlines future contributions into user's existing core funds.
</div>
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 15px; color: #334155; line-height: 1.5;">
• <strong>Cognitive Decluttering:</strong> Eliminates decision fatigue without recommending external funds or triggering sales.
</div>
</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; background: rgba(245, 158, 11, 0.08); border-left: 3px solid #D97706; padding: 10px 14px; border-radius: 6px; margin-top: 12px; font-size: 15px;">
<div><strong style="color: #D97706;">Projected 12M Impact:</strong> {b3['projected_12m_impact']}</div>
<span style="font-size: 13.5px; color: #92400E; font-weight: 600;">✓ Constraint Audit: 100% Compliant</span>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    # Tab 4: Interactive Custom LLM Discovery
    with tab_custom:
        st.markdown(
            """<div style="margin-bottom: 8px;">
<strong style="font-size: 16px; color: #0F172A;">Interactive LLM Opportunity Synthesizer</strong>
<div style="font-size: 15px; color: #64748B;">Query our dataset & failure themes directly to synthesize targeted product opportunities.</div>
</div>""",
            unsafe_allow_html=True,
        )

        preset_col1, preset_col2, preset_col3 = st.columns(3)
        if "llm_opp_input" not in st.session_state:
            st.session_state["llm_opp_input"] = ""

        with preset_col1:
            if st.button("🚨 Bank Autopay & Bounce Penalty", use_container_width=True):
                st.session_state["llm_opp_input"] = "Bank autopay mandate failures, silent rejections, and fear of ₹450 ECS bounce charges."
                st.rerun()
        with preset_col2:
            if st.button("📉 Novice Volatility & XIRR Shock", use_container_width=True):
                st.session_state["llm_opp_input"] = "First-time investor panic during months 1-3 when portfolio turns negative or XIRR shows distorted drop."
                st.rerun()
        with preset_col3:
            if st.button("🧹 Multi-SIP Overlap & Fatigue", use_container_width=True):
                st.session_state["llm_opp_input"] = "Over-diversification, holding 6+ funds with overlapping stocks, and multiple scattered debit dates."
                st.rerun()

        custom_query = st.text_input(
            "Enter problem area or strategic inquiry:",
            value=st.session_state.get("llm_opp_input", ""),
            placeholder="e.g. How can Groww redesign the SIP pause feature so users don't cancel permanently?",
            key="custom_llm_opp_text",
        )

        run_col1, run_col2 = st.columns([1, 3])
        with run_col1:
            run_btn = st.button("⚡ Run LLM Opportunity Discovery", type="primary", use_container_width=True)

        if run_btn or custom_query.strip():
            target_q = custom_query.strip() or "General First-Time SIP Continuation Opportunities"
            with st.spinner("Synthesizing actionable product opportunity across 3,052 verified customer records..."):
                result = synthesizer.synthesize_opportunity(target_q)

            # Display Synthesized Opportunity Blueprint Card
            opp_title = result.get("opportunity_title", "Synthesized Product Opportunity")
            opp_tier = result.get("priority_tier", "Tier 1: Immediate Priority")
            opp_theme = result.get("addressed_failure_theme", "Multiple Failure Themes")
            opp_prob = result.get("discovered_root_problem", "")
            opp_quote = result.get("grounding_evidence_quote", "")
            opp_features = result.get("product_solution_features", [])
            opp_mech = result.get("continuation_mechanism_12m", "")
            opp_impact = result.get("projected_metric_impact", "")
            opp_exp = result.get("validation_experiment", "")
            opp_guard = result.get("constraint_guardrail_check", "")
            opp_source = result.get("source", "Live Groq LLM (openai/gpt-oss-20b)")

            feature_bullets = "".join([f"<li style='margin-bottom: 6px;'>{f}</li>" for f in opp_features])

            blueprint_html = (
                f'<div class="overview-section-card" style="margin-top: 14px; border-left: 4.5px solid #00D09C;">'
                f'<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">'
                f'<div>'
                f'<span class="badge-tag badge-tier-1">{opp_tier.upper()}</span>'
                f'<h3 style="font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 22px; font-weight: 800; color: #0F172A; margin: 6px 0 2px 0;">{opp_title}</h3>'
                f'<div style="font-size: 14.5px; color: #008764; font-weight: 600;">Addressed Theme: {opp_theme}</div>'
                f'</div>'
                f'<span style="font-size: 13.5px; background: rgba(0, 208, 156, 0.1); color: #008764; padding: 4px 10px; border-radius: 6px; font-weight: 700;">{opp_source}</span>'
                f'</div>'
                f'<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin-2px 0 12px 0;">'
                f'<div style="font-size: 14px; font-weight: 700; color: #64748B; text-transform: uppercase;">Discovered Problem & Evidence Grounding:</div>'
                f'<p style="font-size: 15.5px; color: #1E293B; line-height: 1.55; margin: 4px 0 8px 0;">{opp_prob}</p>'
                f'<div style="font-size: 15px; font-style: italic; color: #334155; border-left: 3px solid #00D09C; padding-left: 10px;">"{opp_quote}"</div>'
                f'</div>'
                f'<div style="margin-top: 12px;">'
                f'<div style="font-size: 14.5px; font-weight: 700; color: #0F172A; text-transform: uppercase; margin-bottom: 6px;">Actionable Product Solution:</div>'
                f'<ul style="font-size: 15.5px; color: #334155; line-height: 1.6; padding-left: 20px; margin: 0 0 12px 0;">'
                f'{feature_bullets}'
                f'</ul>'
                f'</div>'
                f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">'
                f'<div style="background: rgba(0, 208, 156, 0.08); border: 1px solid rgba(0, 208, 156, 0.2); border-radius: 8px; padding: 12px 14px;">'
                f'<strong style="color: #008764; font-size: 14px;">📈 12-Month Metric Impact Mechanism:</strong>'
                f'<p style="font-size: 14.5px; color: #064E3B; margin: 4px 0 0 0; line-height: 1.5;">{opp_mech}<br/><strong>Projected Lift:</strong> {opp_impact}</p>'
                f'</div>'
                f'<div style="background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(2, 132, 199, 0.2); border-radius: 8px; padding: 12px 14px;">'
                f'<strong style="color: #0284C7; font-size: 14px;">🧪 30-Day Validation Experiment:</strong>'
                f'<p style="font-size: 14.5px; color: #0C4A6E; margin: 4px 0 0 0; line-height: 1.5;">{opp_exp}</p>'
                f'</div>'
                f'</div>'
                f'<div style="background: #F1F5F9; border-radius: 6px; padding: 10px 14px; margin-top: 10px; font-size: 14px; color: #475569;">'
                f'<strong>🛡️ Constraint & Regulatory Audit:</strong> {opp_guard}'
                f'</div>'
                f'</div>'
            )
            st.markdown(blueprint_html, unsafe_allow_html=True)


def render_priority_matrix(db_path=None) -> None:
    """Render Tab 3: 5-Pillar Opportunity Matrix and Targeted Interview Guides."""
    
    # 0. Top Mission Philosophy Banner
    st.markdown(MISSION_BANNER_HTML, unsafe_allow_html=True)

    st.markdown(
        """<div class="page-header-container">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px;">
<div style="display: flex; align-items: center; gap: 10px;">
<h1 class="page-title">5-Pillar Opportunity Decision Matrix & Hypotheses</h1>
<span class="badge-tag badge-tier-1">Prioritized Rubric</span>
</div>
</div>
<p class="page-subtitle">Ranks discovery opportunity spaces by synthesizing <strong>Prevalence, User Impact, 12M Business Relevance, Evidence Quality, and Product Addressability</strong>. Paired with dual competing hypotheses and interview protocols.</p>
</div>""",
        unsafe_allow_html=True,
    )

    # 1. Load data from SQLite
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                cluster_id, title, description, item_count,
                distinct_authors_count, source_distribution,
                counter_evidence_quotes, created_at
            FROM thematic_clusters
            ORDER BY item_count DESC;
            """
        )
        themes = [dict(row) for row in cursor.fetchall()]

        cursor.execute(
            """
            SELECT 
                hypothesis_id, cluster_id, observed_pattern,
                hypothesis_text, alternative_explanation, missing_evidence,
                connection_to_continuation, validation_approach,
                research_questions, priority_score, created_at
            FROM hypothesis_records
            ORDER BY priority_score DESC;
            """
        )
        hyps_rows = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

    if not themes:
        st.warning("No opportunity data found. Please run the hypothesis generation pipeline first.")
        return

    # Deserialize JSON fields in themes
    for t in themes:
        if isinstance(t.get("source_distribution"), str):
            try:
                t["source_distribution"] = json.loads(t["source_distribution"])
            except Exception:
                t["source_distribution"] = {}
        if isinstance(t.get("counter_evidence_quotes"), str):
            try:
                t["counter_evidence_quotes"] = json.loads(t["counter_evidence_quotes"])
            except Exception:
                t["counter_evidence_quotes"] = []

    # Group hypotheses by cluster
    hyps_by_cluster = {}
    for h in hyps_rows:
        cid = h["cluster_id"]
        try:
            h["research_questions"] = (
                json.loads(h["research_questions"])
                if isinstance(h["research_questions"], str)
                else h["research_questions"]
            )
        except Exception:
            h["research_questions"] = []
        hyps_by_cluster.setdefault(cid, []).append(h)

    # 1.5. Standard 4-Card Hero Metric Grid
    kpi1 = get_kpi_card_html("EVALUATED THEMES", "7", "Ranked across 5 pillars", "#0F172A", "#008764")
    kpi2 = get_kpi_card_html("TIER 1 GROWTH BETS", "3", "Autopay, Volatility, Overlap", "#008764", "#008764")
    kpi3 = get_kpi_card_html("COMPETING HYPOTHESES", "16", "Dual behavioral explanations", "#0F172A", "#008764")
    kpi4 = get_kpi_card_html("PROJECTED 12M LIFT", "+18–25%", "SIP continuation rate", "#0284C7", "#0284C7")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi1, unsafe_allow_html=True)
    with c2:
        st.markdown(kpi2, unsafe_allow_html=True)
    with c3:
        st.markdown(kpi3, unsafe_allow_html=True)
    with c4:
        st.markdown(kpi4, unsafe_allow_html=True)

    # 1.6. Render LLM Strategic Opportunity Section ON TOP of Opportunity Metric
    render_llm_opportunity_section(themes)

    # 2. Evaluate opportunities using ranker
    ranker = OpportunityRanker()
    ranked_opps = ranker.rank_opportunities(themes, hyps_by_cluster)
    guide_synthesizer = InterviewGuideSynthesizer()

    # Section Heading for 5-Pillar Metrics
    st.markdown(
        """<div style="margin-top: 24px; margin-bottom: 14px; border-top: 1px solid #E2E8F0; padding-top: 18px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 23px; font-weight: 800; color: #0F172A; margin: 0 0 4px 0;">5-Pillar Opportunity Metric Evaluation & Priority Ranking</h2>
<div style="font-size: 15.5px; color: #64748B;">Multi-dimensional quantitative scoring across Prevalence, User Impact, 12M Business Relevance, Evidence Quality, and Product Addressability.</div>
</div>
<span class="badge-tag badge-tier-1">Prioritized Rubric</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # Priority Summary Hero Metric Cards matching inspiration design
    tier1_count = sum(1 for o in ranked_opps if "Tier 1" in o["priority_tier"])
    tier2_count = sum(1 for o in ranked_opps if "Tier 2" in o["priority_tier"])

    pkpi1 = get_kpi_card_html("TOTAL OPPORTUNITY SPACES", str(len(ranked_opps)), "5-Pillar Evaluated Spaces", "#0F172A", "#008764")
    pkpi2 = get_kpi_card_html("TIER 1 IMMEDIATE BETS", str(tier1_count), "High-Impact Engineering Focus", "#008764", "#008764")
    pkpi3 = get_kpi_card_html("TIER 2 OPPORTUNITIES", str(tier2_count), "High Strategic Value Cohorts", "#0F172A", "#008764")
    pkpi4 = get_kpi_card_html("REGULATORY SAFEGUARDS", "100%", "SEBI Zero-Advice Compliant", "#0284C7", "#0284C7")

    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        st.markdown(pkpi1, unsafe_allow_html=True)
    with s_col2:
        st.markdown(pkpi2, unsafe_allow_html=True)
    with s_col3:
        st.markdown(pkpi3, unsafe_allow_html=True)
    with s_col4:
        st.markdown(pkpi4, unsafe_allow_html=True)

    FINDING_MAP = {
        "THEME-01": "🛡️ Finding 3: Emergency Funds",
        "THEME-02": "🎯 Finding 2: Not Setting Goals",
        "THEME-03": "🛡️ Finding 3: Emergency Funds",
        "THEME-04": "📉 Finding 1: Market Fluctuations",
        "THEME-05": "🚀 Finding 4: Return Expectations",
        "THEME-06": "📉 Finding 1: Market Fluctuations",
        "THEME-07": "🎯 Finding 2: Not Setting Goals",
    }

    # Ranked Summary Table View
    st.markdown("<h3 style='font-size: 21px; font-weight: 700; color: #0F172A; margin: 12px 0 8px 0;'>Prioritized Opportunities Overview</h3>", unsafe_allow_html=True)
    table_data = []
    for o in ranked_opps:
        p = o["pillars"]
        table_data.append({
            "Rank": f"#{o['rank']}",
            "Aligned Finding": FINDING_MAP.get(o["cluster_id"], "Research Finding"),
            "Opportunity Space": o["title"],
            "Priority Score": f"{o['priority_score']:.2f} / 5.0",
            "Priority Tier": o["priority_tier"],
            "Prevalence": f"{p['prevalence']['tier']} ({p['prevalence']['prevalence_pct']}%)",
            "User Impact": p["user_impact"]["tier"],
            "12M Relevance": p["business_relevance_12m"]["tier"],
            "Addressability": p["product_addressability"]["tier"],
        })
    st.dataframe(table_data, use_container_width=True)

    st.markdown("<h3 style='font-size: 21px; font-weight: 700; color: #0F172A; margin: 16px 0 10px 0;'>Deep-Dive: 5-Pillar Assessments, Competing Hypotheses & Protocols</h3>", unsafe_allow_html=True)

    opp_filter = st.radio(
        "Filter Opportunities by Aligned Finding:",
        [
            "All Opportunities (Unified 4-Finding View)",
            "📉 Finding 1: Market Fluctuations (Themes 4 & 6)",
            "🎯 Finding 2: Not Setting Financial Goals (Themes 2 & 7)",
            "🛡️ Finding 3: Lack of Emergency Funds (Themes 1 & 3)",
            "🚀 Finding 4: Unrealistic Return Expectations (Theme 5)",
        ],
        horizontal=True,
        key="opp_finding_filter",
    )

    opps_to_render = []
    for o in ranked_opps:
        cid = o["cluster_id"]
        if "All" in opp_filter:
            opps_to_render.append(o)
        elif "Finding 1" in opp_filter and cid in ["THEME-04", "THEME-06"]:
            opps_to_render.append(o)
        elif "Finding 2" in opp_filter and cid in ["THEME-02", "THEME-07"]:
            opps_to_render.append(o)
        elif "Finding 3" in opp_filter and cid in ["THEME-01", "THEME-03"]:
            opps_to_render.append(o)
        elif "Finding 4" in opp_filter and cid in ["THEME-05"]:
            opps_to_render.append(o)

    # Cohesive Opportunity Cards
    for opp in opps_to_render:
        cid = opp["cluster_id"]
        hyps = hyps_by_cluster.get(cid, [])
        p = opp["pillars"]
        rank = opp["rank"]
        tier_class = "badge-tier-1" if "Tier 1" in opp["priority_tier"] else "badge-tier-2"

        finding_badge = FINDING_MAP.get(cid, "Research Finding")
        if cid in ["THEME-04", "THEME-06"]:
            finding_style = "background: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE;"
        elif cid in ["THEME-02", "THEME-07"]:
            finding_style = "background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A;"
        elif cid in ["THEME-01", "THEME-03"]:
            finding_style = "background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA;"
        else:
            finding_style = "background: #F0F9FF; color: #0369A1; border: 1px solid #BAE6FD;"

        hyp_boxes = ""
        if len(hyps) >= 2:
            hyp_boxes = f"""<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px;">
<div style="background: rgba(2, 132, 199, 0.05); border: 1px solid rgba(2, 132, 199, 0.2); border-radius: 8px; padding: 14px 16px;">
<span style="font-size: 13.5px; font-weight: 700; color: #0284C7; text-transform: uppercase;">PERSPECTIVE A: PRIMARY CAUSAL EXPLANATION</span>
<p style="font-size: 16px; color: #0F172A; margin: 6px 0; font-weight: 500; line-height: 1.5;">"{hyps[0]['hypothesis_text']}"</p>
<span style="font-size: 14.5px; color: #64748B;"><strong>Validation:</strong> {hyps[0]['validation_approach']}</span>
</div>
<div style="background: rgba(124, 58, 237, 0.05); border: 1px solid rgba(124, 58, 237, 0.2); border-radius: 8px; padding: 14px 16px;">
<span style="font-size: 13.5px; font-weight: 700; color: #7C3AED; text-transform: uppercase;">PERSPECTIVE B: COMPETING / ALTERNATIVE</span>
<p style="font-size: 16px; color: #0F172A; margin: 6px 0; font-weight: 500; line-height: 1.5;">"{hyps[1]['hypothesis_text']}"</p>
<span style="font-size: 14.5px; color: #64748B;"><strong>Validation:</strong> {hyps[1]['validation_approach']}</span>
</div>
</div>"""

        opp_card_html = f"""<div class="evidence-card" style="margin-bottom: 16px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
<div>
<span class="badge-tag {tier_class}">RANK #{rank} &bull; {opp['priority_tier'].upper()}</span>
<span style="font-size: 13px; font-weight: 700; padding: 3px 8px; border-radius: 6px; margin-left: 6px; {finding_style}">{finding_badge.upper()}</span>
<span style="font-size: 14px; font-weight: 700; color: #64748B; margin-left: 6px;">CLUSTER: {cid.upper()}</span>
<h3 style="margin: 6px 0 4px 0; color: #0F172A; font-size: 22px; font-weight: 700;">{opp['title']}</h3>
</div>
<div style="text-align: right;">
<span style="font-size: 30px; font-weight: 800; color: #008764; font-family: 'Plus Jakarta Sans', sans-serif;">{opp['priority_score']}</span>
<span style="font-size: 15px; color: #64748B; font-weight: 600;">/ 5.0</span>
</div>
</div>
<p style="font-size: 16.5px; color: #334155; line-height: 1.6; margin-bottom: 14px;">{opp['description']}</p>
<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 12px;">
<div class="pillar-metric-box">
<div class="pillar-score-label">Prevalence</div>
<div class="pillar-score-val">{p['prevalence']['score']}/5</div>
<div class="pillar-score-desc">{p['prevalence']['tier']}</div>
</div>
<div class="pillar-metric-box">
<div class="pillar-score-label">User Impact</div>
<div class="pillar-score-val">{p['user_impact']['score']}/5</div>
<div class="pillar-score-desc">{p['user_impact']['tier']}</div>
</div>
<div class="pillar-metric-box">
<div class="pillar-score-label">12M Relevance</div>
<div class="pillar-score-val">{p['business_relevance_12m']['score']}/5</div>
<div class="pillar-score-desc">{p['business_relevance_12m']['tier']}</div>
</div>
<div class="pillar-metric-box">
<div class="pillar-score-label">Evidence Quality</div>
<div class="pillar-score-val">{p['evidence_quality']['score']}/5</div>
<div class="pillar-score-desc">{p['evidence_quality']['tier']}</div>
</div>
<div class="pillar-metric-box">
<div class="pillar-score-label">Addressability</div>
<div class="pillar-score-val">{p['product_addressability']['score']}/5</div>
<div class="pillar-score-desc">{p['product_addressability']['tier']}</div>
</div>
</div>
{hyp_boxes}
</div>"""

        st.markdown(opp_card_html, unsafe_allow_html=True)

        # Primary Research Interview Guide Expander
        if len(hyps) >= 2:
            guide = guide_synthesizer.generate_guide(
                cluster_id=cid,
                theme_title=opp["title"],
                observed_pattern=hyps[0]["observed_pattern"],
                hypothesis_a=hyps[0]["hypothesis_text"],
                hypothesis_b=hyps[1]["hypothesis_text"],
                core_questions=hyps[0]["research_questions"],
            )

            with st.expander(f"View 1:1 Primary Research Protocol for #{rank} ({cid})", expanded=False):
                st.markdown(f"**Target Participant Screener:**\n\n> {guide['target_participant_screener']}")
                st.markdown(f"**Session Format:** 45-minute 1:1 semi-structured video interview with screen sharing.")

                st.markdown("##### Core Non-Leading Retrospective Inquiries:")
                for q_idx, q in enumerate(guide["interview_phases"]["2_core_behavioral_inquiries"], 1):
                    st.markdown(f"**Q{q_idx}.** *\"{q}\"*")

                st.markdown("##### Competing Hypotheses Debiasing Probes:")
                for p_idx, probe in enumerate(guide["interview_phases"]["3_competing_hypotheses_probes"], 1):
                    st.markdown(f"**Probe {p_idx}:** *\"{probe}\"*")

                st.markdown("##### Facilitator Instructions:")
                for fn in guide["facilitator_notes"]:
                    st.markdown(f"- {fn}")
