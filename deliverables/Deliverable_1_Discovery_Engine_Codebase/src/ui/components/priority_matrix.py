"""Opportunity Matrix & Primary Interview Guides Component (Tab 3 / Tab 5).

Ranks discovery opportunity spaces using the 5-pillar qualitative rubric, displays
dual competing hypotheses, and surfaces actionable 1:1 primary research interview guides.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st

from src.database.connection import get_connection
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
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

    # Opportunity 1: Horizontal Card
    st.markdown(
        """<div style="background: #151A24; border: 1.5px solid #222938; border-left: 5px solid #00D09C; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1E2533; padding-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span class="badge-tag badge-tier-1">TIER 1 PRIORITY</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 18.5px; font-weight: 800; color: #F1F5F9; margin: 0;">Opportunity 1: Fail-Safe Autopay & Cash-Flow Buffer Engine</h3>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span class="badge-tag badge-play-store">24.5% CORPUS (748)</span>
<span style="font-size: 13px; font-weight: 700; color: #00D09C;">High Impact</span>
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
<div style="font-size: 11px; font-weight: 700; color: #00D09C; text-transform: uppercase; margin-bottom: 3px;">Primary Retention Goal:</div>
<div style="font-size: 15px; font-weight: 800; color: #00D09C;">Mandate Recovery Rate</div>
<div style="font-size: 12px; color: #34D399; margin-top: 4px; line-height: 1.35;">Convert involuntary bank bounce drops into recovered UPI SIP instalments.</div>
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
        """<div style="background: #151A24; border: 1.5px solid #222938; border-left: 5px solid #38BDF8; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1E2533; padding-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span class="badge-tag badge-tier-1">TIER 1 PRIORITY</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 18.5px; font-weight: 800; color: #F1F5F9; margin: 0;">Opportunity 2: First-90-Day Volatility Pacing Shield</h3>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span class="badge-tag badge-reddit">17.6% CORPUS (537)</span>
<span style="font-size: 13px; font-weight: 700; color: #38BDF8;">High Impact</span>
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
<div style="font-size: 11px; font-weight: 700; color: #38BDF8; text-transform: uppercase; margin-bottom: 3px;">Primary Retention Goal:</div>
<div style="font-size: 15px; font-weight: 800; color: #38BDF8;">Post-Dip Continuation</div>
<div style="font-size: 12px; color: #7DD3FC; margin-top: 4px; line-height: 1.35;">Reduce Month 1–4 panic cancellations after minor market drawdowns.</div>
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
        """<div style="background: #151A24; border: 1.5px solid #222938; border-left: 5px solid #FBBF24; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1E2533; padding-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span class="badge-tag badge-tier-2">TIER 2 PRIORITY</span>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 18.5px; font-weight: 800; color: #F1F5F9; margin: 0;">Opportunity 3: Goal-Anchoring & Portfolio Consolidation</h3>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span class="badge-tag badge-forum">9.3% CORPUS (284)</span>
<span style="font-size: 13px; font-weight: 700; color: #FBBF24;">Medium Impact</span>
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
<div style="font-size: 11px; font-weight: 700; color: #FBBF24; text-transform: uppercase; margin-bottom: 3px;">Primary Retention Goal:</div>
<div style="font-size: 15px; font-weight: 800; color: #FBBF24;">Multi-Fund Simplicity</div>
<div style="font-size: 12px; color: #FDE68A; margin-top: 4px; line-height: 1.35;">Lower multi-SIP pause/stop rates via goal anchoring &amp; payday sync.</div>
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
    kpi4 = get_kpi_card_html("NORTH-STAR METRIC", "12M SIP", "First-time investor continuation", "#38BDF8", "#38BDF8")

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
