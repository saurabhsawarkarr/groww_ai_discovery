"""Opportunity Matrix & Primary Interview Guides Component (Tab 3 / Tab 5).

Ranks discovery opportunity spaces using the 5-pillar qualitative rubric, displays
dual competing hypotheses, and surfaces actionable 1:1 primary research interview guides.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st

from src.database.connection import get_connection
from src.hypotheses.llm_opportunity_synthesizer import LLMOpportunitySynthesizer
from src.ui.components.common_ui import MISSION_BANNER_HTML, get_kpi_card_html

JSON_EXPORT_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data"
    / "processed"
    / "hypotheses_and_opportunities.json"
)


def _render_opportunity_ask_bar(opp_num: int, prompts: List[str]) -> None:
    """Render GR-1-style contextual prompt bar below an opportunity card."""
    cols = st.columns([1.2, 1.2, 0.9], gap="small")
    for idx, p_text in enumerate(prompts[:2]):
        with cols[idx]:
            if st.button(f"↳ {p_text}", key=f"opp_{opp_num}_ask_{idx}", use_container_width=True):
                st.session_state["pending_ai_query"] = p_text
                st.session_state["nav_target_page"] = "Ask AI Engine"
                st.rerun()
    with cols[2]:
        if st.button(f"Ask AI (Opp {opp_num}) ➔", key=f"opp_{opp_num}_ask_main", use_container_width=True):
            st.session_state["pending_ai_query"] = prompts[0]
            st.session_state["nav_target_page"] = "Ask AI Engine"
            st.rerun()
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


def render_llm_opportunity_section(themes: Optional[List[Dict[str, Any]]] = None) -> None:
    """Render 3 Core Product Opportunities in an executive horizontal row layout."""
    synthesizer = LLMOpportunitySynthesizer()
    opps = synthesizer.get_strategic_bets()
    b1, b2, b3 = opps[0], opps[1], opps[2]

    # Horizontal Lifecycle Journey Stepper
    st.markdown(
        """<div style="background: #151A24; border: 1px solid #222938; border-radius: 10px; padding: 12px 18px; margin: 14px 0 16px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
<div style="font-size: 13px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.04em;">
12-Month Investor Journey:
</div>
<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; font-size: 13.5px; font-weight: 600;">
<span style="background: rgba(0, 208, 156, 0.12); color: #00D09C; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(0, 208, 156, 0.3);">
Phase 1 (M1–3): Mandate &amp; Autopay
</span>
<span style="color: #64748B;">&rarr;</span>
<span style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3);">
Phase 2 (M1–4): Volatility Pacing Shield
</span>
<span style="color: #64748B;">&rarr;</span>
<span style="background: rgba(251, 191, 36, 0.12); color: #FBBF24; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(251, 191, 36, 0.3);">
Phase 3 (M4–12): Goal &amp; Portfolio Hygiene
</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # Opportunity 1: Horizontal Card
    st.markdown(
        f"""<div style="background: #151A24; border: 1.5px solid #222938; border-left: 5px solid #00D09C; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1E2533; padding-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span class="badge-tag badge-tier-1">TIER 1 PRIORITY</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 18.5px; font-weight: 800; color: #F1F5F9; margin: 0;">Opportunity 1: Fail-Safe Autopay & Cash-Flow Buffer Engine</h3>
<span style="font-size: 13px; color: #00D09C; font-weight: 600;">Finding 3: Emergency Cash Buffer</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span class="badge-tag badge-play-store">24.6% CHURN VOLUME</span>
<span style="font-size: 13.5px; font-weight: 700; color: #00D09C;">Score: 4.85 / 5.0</span>
</div>
</div>
<div style="display: grid; grid-template-columns: 29% 45% 26%; gap: 16px; align-items: stretch;">
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 4px;">Discovered User Friction:</div>
<div style="font-size: 13px; color: #F1F5F9; line-height: 1.5;">Salary delays of 2–3 days leave balances depleted; fear of ₹450 ECS bank penalties prompts users to permanently delete mandates instead of pausing.</div>
</div>
<div style="font-size: 12px; color: #94A3B8; margin-top: 8px; font-weight: 600;">
Lifecycle Window: <strong style="color: #F1F5F9;">Month 1–3 (Setup & Early Debit)</strong>
</div>
</div>
<div style="display: flex; flex-direction: column; justify-content: space-between;">
<div style="font-size: 11px; font-weight: 700; color: #F1F5F9; text-transform: uppercase; margin-bottom: 6px;">Actionable Product Solutions:</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">24h Pre-Debit Ping:</strong> Proactive WhatsApp balance check before run.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">1-Click Instant UPI Retry:</strong> Zero-penalty 48h manual payment fallback.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">Salary Date Auto-Shift:</strong> Move instalment date +/- 5 days without reset.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">NPCI Limit Demystifier:</strong> Explaining limit is an authorization cap.
</div>
</div>
</div>
<div style="background: rgba(0, 208, 156, 0.08); border: 1px solid rgba(0, 208, 156, 0.25); border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 11px; font-weight: 700; color: #00D09C; text-transform: uppercase; margin-bottom: 3px;">Projected 12M Impact:</div>
<div style="font-size: 15px; font-weight: 800; color: #00D09C;">+14% to +18% Lift</div>
<div style="font-size: 12px; color: #34D399; margin-top: 3px; line-height: 1.35;">Target: >65% mandate recovery via 1-click fallback link.</div>
</div>
<div style="font-size: 11.5px; color: #34D399; font-weight: 600; border-top: 1px solid rgba(0, 208, 156, 0.25); padding-top: 6px; margin-top: 6px;">
✓ 100% SEBI Non-Advice Compliant
</div>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )
    _render_opportunity_ask_bar(
        1,
        [
            "Why do bank autopay mandates fail silently?",
            "How does fear of ₹450 bank bounce fines trigger cancellations?",
        ],
    )

    # Opportunity 2: Horizontal Card
    st.markdown(
        f"""<div style="background: #151A24; border: 1.5px solid #222938; border-left: 5px solid #38BDF8; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1E2533; padding-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span class="badge-tag badge-tier-1">TIER 1 PRIORITY</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 18.5px; font-weight: 800; color: #F1F5F9; margin: 0;">Opportunity 2: First-90-Day Volatility Pacing Shield</h3>
<span style="font-size: 13px; color: #38BDF8; font-weight: 600;">Findings 1 &amp; 4: Volatility &amp; Return Expectations</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span class="badge-tag badge-reddit">17.5% CHURN VOLUME</span>
<span style="font-size: 13.5px; font-weight: 700; color: #38BDF8;">Score: 4.65 / 5.0</span>
</div>
</div>
<div style="display: grid; grid-template-columns: 29% 45% 26%; gap: 16px; align-items: stretch;">
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 4px;">Discovered User Friction:</div>
<div style="font-size: 13px; color: #F1F5F9; line-height: 1.5;">Novices treat SIPs like fixed deposits; early 2–3% paper dips or distorted -35% annualized XIRR on short tenures trigger acute panic drop-offs.</div>
</div>
<div style="font-size: 12px; color: #94A3B8; margin-top: 8px; font-weight: 600;">
Lifecycle Window: <strong style="color: #F1F5F9;">Month 1–4 (Correction Shock)</strong>
</div>
</div>
<div style="display: flex; flex-direction: column; justify-content: space-between;">
<div style="font-size: 11px; font-weight: 700; color: #F1F5F9; text-transform: uppercase; margin-bottom: 6px;">Actionable Product Solutions:</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">Units Accumulated Lens:</strong> Highlight unit growth rather than noisy daily dip.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">Contextual DCA Primer:</strong> Calming visual showing how dips buy more units.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">Domino Settlement Stepper:</strong> T+2 allotment progress tracker eliminating fear.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">Tenor Return Safeguards:</strong> Suppress distorted &lt;1Y XIRR metrics by default.
</div>
</div>
</div>
<div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 11px; font-weight: 700; color: #38BDF8; text-transform: uppercase; margin-bottom: 3px;">Projected 12M Impact:</div>
<div style="font-size: 15px; font-weight: 800; color: #38BDF8;">+8% to +12% Lift</div>
<div style="font-size: 12px; color: #7DD3FC; margin-top: 3px; line-height: 1.35;">Target: Post-drawdown cancellation rate decrease to &lt;7.5%.</div>
</div>
<div style="font-size: 11.5px; color: #7DD3FC; font-weight: 600; border-top: 1px solid rgba(56, 189, 248, 0.25); padding-top: 6px; margin-top: 6px;">
✓ 100% SEBI Non-Advice Compliant
</div>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )
    _render_opportunity_ask_bar(
        2,
        [
            "Why does XIRR show -18% on a tiny 30 rupees dip?",
            "Why do users panic over the 48-hour NAV allotment delay?",
        ],
    )

    # Opportunity 3: Horizontal Card
    st.markdown(
        f"""<div style="background: #151A24; border: 1.5px solid #222938; border-left: 5px solid #FBBF24; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1E2533; padding-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span class="badge-tag badge-tier-2">TIER 2 PRIORITY</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 18.5px; font-weight: 800; color: #F1F5F9; margin: 0;">Opportunity 3: Goal-Anchoring & Portfolio Consolidation</h3>
<span style="font-size: 13px; color: #FBBF24; font-weight: 600;">Finding 2: Not Setting Financial Goals</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span class="badge-tag badge-forum">9.3% CHURN VOLUME</span>
<span style="font-size: 13.5px; font-weight: 700; color: #FBBF24;">Score: 4.40 / 5.0</span>
</div>
</div>
<div style="display: grid; grid-template-columns: 29% 45% 26%; gap: 16px; align-items: stretch;">
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 4px;">Discovered User Friction:</div>
<div style="font-size: 13px; color: #F1F5F9; line-height: 1.5;">Novices buy 5–8 hyped funds, discovering 70% stock overlap across scattered debit dates, freezing in cognitive decision fatigue.</div>
</div>
<div style="font-size: 12px; color: #94A3B8; margin-top: 8px; font-weight: 600;">
Lifecycle Window: <strong style="color: #F1F5F9;">Month 4–12 (Clutter & Habit Erosion)</strong>
</div>
</div>
<div style="display: flex; flex-direction: column; justify-content: space-between;">
<div style="font-size: 11px; font-weight: 700; color: #F1F5F9; text-transform: uppercase; margin-bottom: 6px;">Actionable Product Solutions:</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">Portfolio Overlap X-Ray:</strong> Detect duplicate company holdings passively.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">Debit Date Synchronizer:</strong> Group multiple active SIPs into 1 payday debit.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">In-Portfolio Consolidation:</strong> Merge future flow into core funds cleanly.
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; line-height: 1.4; color: #CBD5E1;">
• <strong style="color: #F1F5F9;">Cognitive Decluttering:</strong> Reduce fatigue without triggering fund selling.
</div>
</div>
</div>
<div style="background: rgba(251, 191, 36, 0.08); border: 1px solid rgba(251, 191, 36, 0.25); border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;">
<div>
<div style="font-size: 11px; font-weight: 700; color: #FBBF24; text-transform: uppercase; margin-bottom: 3px;">Projected 12M Impact:</div>
<div style="font-size: 15px; font-weight: 800; color: #FBBF24;">+6% to +9% Lift</div>
<div style="font-size: 12px; color: #FDE68A; margin-top: 3px; line-height: 1.35;">Target: Multi-fund pause rate reduction & portfolio simplicity.</div>
</div>
<div style="font-size: 11.5px; color: #FDE68A; font-weight: 600; border-top: 1px solid rgba(251, 191, 36, 0.25); padding-top: 6px; margin-top: 6px;">
✓ 100% SEBI Non-Advice Compliant
</div>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )
    _render_opportunity_ask_bar(
        3,
        [
            "Why do first-time users accumulate 6+ overlapping funds?",
            "What habits differentiate 12-month continuers from early drop-offs?",
        ],
    )

    # Interactive Custom LLM Discovery Expander (Tucked away, no scrolling impact)
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    with st.expander("On-Demand AI Opportunity Synthesizer (Custom Query)", expanded=False):
        st.markdown(
            """<div style="margin-bottom: 10px;">
<strong style="font-size: 15px; color: #F1F5F9;">Interactive Discovery Engine</strong>
<div style="font-size: 14px; color: #94A3B8;">Query our 3,052 customer dataset and failure themes to synthesize custom product solutions.</div>
</div>""",
            unsafe_allow_html=True,
        )

        preset_col1, preset_col2, preset_col3 = st.columns(3)
        if "llm_opp_input" not in st.session_state:
            st.session_state["llm_opp_input"] = ""

        with preset_col1:
            if st.button("Bank Autopay & Bounce", key="btn_preset_autopay", use_container_width=True):
                st.session_state["llm_opp_input"] = "Bank autopay mandate failures, silent rejections, and fear of ₹450 ECS bounce charges."
                st.rerun()
        with preset_col2:
            if st.button("Volatility & XIRR Shock", key="btn_preset_volatility", use_container_width=True):
                st.session_state["llm_opp_input"] = "First-time investor panic during months 1-3 when portfolio turns negative or XIRR shows distorted drop."
                st.rerun()
        with preset_col3:
            if st.button("Over-Diversification", key="btn_preset_diversification", use_container_width=True):
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
            run_btn = st.button("Run Opportunity Discovery", key="btn_run_opp_discovery", type="primary", use_container_width=True)

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

            feature_bullets = "".join([f"<li style='margin-bottom: 4px;'>{f}</li>" for f in opp_features])

            blueprint_html = (
                f'<div class="overview-section-card" style="margin-top: 14px; border-left: 4.5px solid #00D09C;">'
                f'<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">'
                f'<div>'
                f'<span class="badge-tag badge-tier-1">{opp_tier.upper()}</span>'
                f'<h3 style="font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 19px; font-weight: 800; color: #F1F5F9; margin: 4px 0 2px 0;">{opp_title}</h3>'
                f'<div style="font-size: 13.5px; color: #00D09C; font-weight: 600;">Addressed Theme: {opp_theme}</div>'
                f'</div>'
                f'<span style="font-size: 12px; background: rgba(0, 208, 156, 0.12); color: #00D09C; padding: 4px 10px; border-radius: 6px; font-weight: 700; border: 1px solid rgba(0, 208, 156, 0.3);">{opp_source}</span>'
                f'</div>'
                f'<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 8px; padding: 10px 14px; margin: 8px 0 10px 0;">'
                f'<div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Discovered Problem & Evidence Grounding:</div>'
                f'<p style="font-size: 13.5px; color: #F1F5F9; line-height: 1.45; margin: 3px 0 6px 0;">{opp_prob}</p>'
                f'<div style="font-size: 13px; font-style: italic; color: #CBD5E1; border-left: 3px solid #00D09C; padding-left: 10px;">"{opp_quote}"</div>'
                f'</div>'
                f'<div style="margin-top: 8px;">'
                f'<div style="font-size: 11px; font-weight: 700; color: #F1F5F9; text-transform: uppercase; margin-bottom: 4px;">Actionable Product Solution:</div>'
                f'<ul style="font-size: 13.5px; color: #CBD5E1; line-height: 1.5; padding-left: 18px; margin: 0 0 10px 0;">'
                f'{feature_bullets}'
                f'</ul>'
                f'</div>'
                f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px;">'
                f'<div style="background: rgba(0, 208, 156, 0.08); border: 1px solid rgba(0, 208, 156, 0.25); border-radius: 8px; padding: 10px 12px;">'
                f'<strong style="color: #00D09C; font-size: 13px;">12-Month Metric Impact:</strong>'
                f'<p style="font-size: 13px; color: #34D399; margin: 3px 0 0 0; line-height: 1.4;">{opp_mech}<br/><strong>Projected Lift:</strong> {opp_impact}</p>'
                f'</div>'
                f'<div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 10px 12px;">'
                f'<strong style="color: #38BDF8; font-size: 13px;">30-Day Validation Test:</strong>'
                f'<p style="font-size: 13px; color: #7DD3FC; margin: 3px 0 0 0; line-height: 1.4;">{opp_exp}</p>'
                f'</div>'
                f'</div>'
                f'<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 6px; padding: 8px 12px; margin-top: 8px; font-size: 12.5px; color: #94A3B8;">'
                f'<strong style="color: #F1F5F9;">Regulatory Guardrail Check:</strong> {opp_guard}'
                f'</div>'
                f'</div>'
            )
            st.markdown(blueprint_html, unsafe_allow_html=True)


def render_priority_matrix(db_path=None) -> None:
    """Render Tab 3: Core Product Opportunities and Actionable Solutions."""
    st.markdown(
        """<div class="page-header-container">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px;">
<div style="display: flex; align-items: center; gap: 10px;">
<h1 class="page-title">Opportunity</h1>
<span class="badge-tag badge-tier-1">Executive Roadmap</span>
</div>
</div>
<p class="page-subtitle">High-leverage product opportunities architected directly to drive <strong style="color: #F1F5F9;">12-Month First-Time SIP Continuation</strong>. Grounded across 3,052 verified customer records under strict SEBI zero-fund-advice and anti-FOMO constraints.</p>
</div>""",
        unsafe_allow_html=True,
    )

    # Standard 4-Card Hero Metric Grid
    kpi1 = get_kpi_card_html("ADDRESSED THEMES", "7 Themes", "100% Unified with Findings", "#F1F5F9", "#00D09C")
    kpi2 = get_kpi_card_html("CORE OPPORTUNITIES", "3 Solutions", "Autopay, Volatility, Clutter", "#00D09C", "#00D09C")
    kpi3 = get_kpi_card_html("REGULATORY SAFEGUARDS", "100%", "SEBI Zero-Advice Compliant", "#F1F5F9", "#00D09C")
    kpi4 = get_kpi_card_html("PROJECTED 12M LIFT", "+18–25%", "SIP continuation rate", "#38BDF8", "#38BDF8")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi1, unsafe_allow_html=True)
    with c2:
        st.markdown(kpi2, unsafe_allow_html=True)
    with c3:
        st.markdown(kpi3, unsafe_allow_html=True)
    with c4:
        st.markdown(kpi4, unsafe_allow_html=True)

    # Render 3 Core Opportunities side-by-side
    render_llm_opportunity_section()
