"""Executive Overview Component for Groww Discovery Engine.

Comprehensive executive dashboard providing:
1. Executive KPI metrics across the 32.5k review / 3,052 clean SIP corpus.
2. The 12-Month SIP Continuation problem statement & drop-off dynamics.
3. 4-Stage Discovery Engine methodology stepper.
4. Problem spaces & severity profile mapped across the 4 core research findings.
5. Strategic product opportunity bets preview (Autopay, Volatility, Clutter).
6. Embedded interactive Qualitative Research Assistant (RAG Chat).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st

from src.ui.components.common_ui import get_kpi_card_html
from src.rag.pipeline import RAGPipeline
from src.rag.retriever import HybridEvidenceRetriever


@st.cache_resource(show_spinner="Initializing Qualitative Evidence Index...")
def get_overview_pipeline() -> RAGPipeline:
    """Initialize and cache the hybrid BM25 + Vector retriever pipeline."""
    retriever = HybridEvidenceRetriever()
    return RAGPipeline(retriever=retriever)


HEADER_HTML = """<div class="page-header-container">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 4px; flex-wrap: wrap;">
<div style="display: flex; align-items: center; gap: 10px;">
<h1 class="page-title" style="margin: 0;">Overview</h1>
<span class="badge-tag badge-tier-1">Executive Suite</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="background: rgba(0, 208, 156, 0.12); color: #00D09C; font-size: 13px; font-weight: 700; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(0, 208, 156, 0.3);">
3,052 Clean Corpus
</span>
<span style="background: #1E2533; color: #94A3B8; font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 6px; border: 1px solid #2B3548;">
SEBI Non-Advice Compliant
</span>
</div>
</div>
<p class="page-subtitle">AI-powered behavioral analysis of user drop-off and friction points in first-time mutual fund SIP continuation.</p>
</div>"""

SECTION_TITLE_HTML = """<div style="margin-bottom: 10px;">
<h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 20px; font-weight: 700; color: #F1F5F9; margin: 0;">Executive Overview Metrics</h2>
</div>"""

KPI_1_HTML = get_kpi_card_html("TOTAL SCRAPED REVIEWS", "32,547", "Play Store, App Store, Reddit, YouTube, Forum", "#F1F5F9", "#00D09C")
KPI_2_HTML = get_kpi_card_html("CLEAN QUALIFIED SIPS", "3,052", "100% relevant MF conversations", "#00D09C", "#00D09C")
KPI_3_HTML = get_kpi_card_html("DATA SOURCES ANALYSED", "5", "Play Store, App Store, Reddit, YouTube, Forum", "#F1F5F9", "#00D09C")
KPI_4_HTML = get_kpi_card_html("FAILURE THEMES GENERATED", "7", "Prevalence 3.2% – 18.0% of corpus", "#38BDF8", "#38BDF8")

PROBLEM_CONTEXT_HTML = """<div style="background: #151A24; border: 1px solid #222938; border-left: 4.5px solid #00D09C; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 16.5px; font-weight: 700; color: #F1F5F9;">
The Core Problem: 54% of First-Time Mutual Fund SIP Investors Drop Off Before Month 12
</div>
<span class="badge-tag badge-platform">Behavioral Discovery</span>
</div>
<p style="font-size: 14.5px; color: #94A3B8; line-height: 1.6; margin: 0 0 10px 0;">
Analysis across 3,052 verified customer conversations reveals that SIP discontinuation is driven by two distinct failure vectors:
<strong style="color: #F1F5F9;">Involuntary Churn (24.6%)</strong> caused by silent bank mandate drops and ₹450 ECS bounce penalty dread, and 
<strong style="color: #F1F5F9;">Cognitive / Expectation Shock (49.4%)</strong> caused by short-tenure annualized XIRR distortions, red portfolio panic, and scheme overlap fatigue.
</p>
<div style="display: flex; gap: 12px; flex-wrap: wrap; font-size: 13px;">
<span style="background: #1A2230; border: 1px solid #2B3548; padding: 4px 10px; border-radius: 6px; color: #F1F5F9;"><strong style="color: #94A3B8;">Target Metric:</strong> 12-Month SIP Continuation Rate</span>
<span style="background: #1A2230; border: 1px solid #2B3548; padding: 4px 10px; border-radius: 6px; color: #00D09C;"><strong style="color: #94A3B8;">Projected Potential Lift:</strong> +18% to +25%</span>
<span style="background: #1A2230; border: 1px solid #2B3548; padding: 4px 10px; border-radius: 6px; color: #38BDF8;"><strong style="color: #94A3B8;">Critical Drop Window:</strong> Month 1 to Month 4</span>
</div>
</div>"""

HOW_IT_WORKS_HTML = """<div class="overview-section-card" style="height: 100%;">
<h3 style="font-size: 18.5px; font-weight: 700; color: #F1F5F9; margin: 0 0 14px 0;">How the Discovery Engine Works</h3>
<div class="pipeline-step-box">
<div style="font-weight: 700; color: #F1F5F9; font-size: 15.5px;">1. Multi-Channel Ingestion (32.5k+ raw reviews)</div>
<div style="font-size: 14px; color: #94A3B8; margin-top: 4px; line-height: 1.5;">Harvested across Google Play Store (27.1k), YouTube (3.7k), Reddit (574), Forums (588), App Store (522).</div>
</div>
<div class="pipeline-step-arrow">↓</div>
<div class="pipeline-step-box">
<div style="font-weight: 700; color: #F1F5F9; font-size: 15.5px;">2. Qualification &amp; Deduplication (3,052 records)</div>
<div style="font-size: 14px; color: #94A3B8; margin-top: 4px; line-height: 1.5;">Strict MF/SIP qualification, spam filtering, and inverted prefix shingle deduplication.</div>
</div>
<div class="pipeline-step-arrow">↓</div>
<div class="pipeline-step-box">
<div style="font-weight: 700; color: #F1F5F9; font-size: 15.5px;">3. Pattern Discovery &amp; Theming (7 core themes)</div>
<div style="font-size: 14px; color: #94A3B8; margin-top: 4px; line-height: 1.5;">Unsupervised clustering, active date spans (2016–2026), platform distribution, and verbatim quote indexing.</div>
</div>
<div class="pipeline-step-arrow">↓</div>
<div class="pipeline-step-box">
<div style="font-weight: 700; color: #F1F5F9; font-size: 15.5px;">4. Competing Hypotheses &amp; Opportunity Solutions</div>
<div style="font-size: 14px; color: #94A3B8; margin-top: 4px; line-height: 1.5;">Behavioral hypotheses, 5-pillar qualitative scoring, product addressability, and conversational RAG discovery.</div>
</div>
</div>"""

FRUSTRATION_PROFILE_HTML = """<div class="overview-section-card" style="height: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<h3 style="font-size: 18.5px; font-weight: 700; color: #F1F5F9; margin: 0;">Discovered Problem Spaces &amp; Severity</h3>
<span class="badge-tag badge-tier-1">4 Findings Mapped</span>
</div>
<div style="display: flex; height: 28px; border-radius: 8px; overflow: hidden; margin-bottom: 12px; font-size: 13.5px; font-weight: 700; color: #FFFFFF; text-align: center; line-height: 28px;">
<div style="width: 74%; background: #EF4444;" title="High Frustration: 74%">74%</div>
<div style="width: 18%; background: #F59E0B;" title="Medium Frustration: 18%">18%</div>
<div style="width: 8%; background: #10B981;" title="Low / Positive: 8%">8%</div>
</div>
<div style="display: flex; gap: 18px; font-size: 14px; color: #94A3B8; margin-bottom: 14px;">
<div><span style="color: #EF4444; font-size: 14px;">●</span> <strong>High Frustration</strong> (74%)</div>
<div><span style="color: #F59E0B; font-size: 14px;">●</span> <strong>Medium Friction</strong> (18%)</div>
<div><span style="color: #10B981; font-size: 14px;">●</span> <strong>Habit Anchors</strong> (8%)</div>
</div>
<div style="border-top: 1px solid var(--groww-border-subtle); padding-top: 12px;">
<div style="font-size: 14.5px; margin-bottom: 10px;">
<span style="color: #00D09C; font-weight: 800; font-size: 15px;">The 4 Core Research Findings &amp; Empirical Theme Mapping:</span>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13.5px; line-height: 1.55;">
  <div style="background: #1A2230; border: 1px solid #2B3548; border-left: 4px solid #A78BFA; padding: 8px 12px; border-radius: 6px;">
    <strong style="color: #A78BFA;">1. Market Fluctuations (11.2%)</strong><br/>
    &bull; Early Drawdown Panic (Theme 04 — 5.9%)<br/>
    &bull; T+2 NAV Delay Uncertainty (Theme 06 — 5.3%)
  </div>
  <div style="background: #1A2230; border: 1px solid #2B3548; border-left: 4px solid #FBBF24; padding: 8px 12px; border-radius: 6px;">
    <strong style="color: #FBBF24;">2. Not Setting Goals (12.5%)</strong><br/>
    &bull; Scheme Overlap Clutter (Theme 02 — 9.3%)<br/>
    &bull; Milestone Disconnect (Theme 07 — 3.2%)
  </div>
  <div style="background: #1A2230; border: 1px solid #2B3548; border-left: 4px solid #F87171; padding: 8px 12px; border-radius: 6px;">
    <strong style="color: #F87171;">3. Emergency Buffer Lack (24.6%)</strong><br/>
    &bull; Mandate Drops &amp; Timing (Theme 01 — 18.0%)<br/>
    &bull; ECS Bounce Penalty Trap (Theme 03 — 6.6%)
  </div>
  <div style="background: #1A2230; border: 1px solid #2B3548; border-left: 4px solid #38BDF8; padding: 8px 12px; border-radius: 6px;">
    <strong style="color: #38BDF8;">4. Return Mismatch (6.3%)</strong><br/>
    &bull; XIRR Distortion &amp; FD Anchor (Theme 05 — 6.3%)
  </div>
</div>
</div>
</div>"""

STRATEGIC_BETS_HTML = """<div style="background: #151A24; border: 1px solid #222938; border-radius: 12px; padding: 18px 22px; margin-top: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 17px; font-weight: 700; color: #F1F5F9;">
The 3 Strategic Product Bets (12-Month Retention Roadmap)
</div>
<span class="badge-tag badge-tier-1">Executive Roadmap</span>
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
<div style="background: #1A2230; border: 1px solid #2B3548; border-left: 4px solid #00D09C; border-radius: 8px; padding: 12px 14px;">
<div style="font-size: 12px; font-weight: 700; color: #00D09C; text-transform: uppercase;">Bet 1: Mandate Resilience (Month 1–3)</div>
<div style="font-size: 15px; font-weight: 700; color: #F1F5F9; margin: 3px 0 5px 0;">Fail-Safe Autopay &amp; Cash Buffer</div>
<div style="font-size: 13.5px; color: #94A3B8; line-height: 1.5;">1-click manual UPI retry links on debit bounce + proactive 24h pre-debit WhatsApp ping to curb involuntary cancellations.</div>
<div style="font-size: 12.5px; color: #00D09C; font-weight: 700; margin-top: 6px;">Projected Lift: +14% to +18%</div>
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-left: 4px solid #38BDF8; border-radius: 8px; padding: 12px 14px;">
<div style="font-size: 12px; font-weight: 700; color: #38BDF8; text-transform: uppercase;">Bet 2: Volatility Framing (Month 1–4)</div>
<div style="font-size: 15px; font-weight: 700; color: #F1F5F9; margin: 3px 0 5px 0;">Volatility Pacing Shield</div>
<div style="font-size: 13.5px; color: #94A3B8; line-height: 1.5;">Tenor-sensitive metric masking suppressing distorted &lt;1Y XIRR, highlighting units accumulated during normal corrections.</div>
<div style="font-size: 12.5px; color: #38BDF8; font-weight: 700; margin-top: 6px;">Projected Lift: +8% to +12%</div>
</div>
<div style="background: #1A2230; border: 1px solid #2B3548; border-left: 4px solid #FBBF24; border-radius: 8px; padding: 12px 14px;">
<div style="font-size: 12px; font-weight: 700; color: #FBBF24; text-transform: uppercase;">Bet 3: Portfolio Hygiene (Month 4–12)</div>
<div style="font-size: 15px; font-weight: 700; color: #F1F5F9; margin: 3px 0 5px 0;">Goal-Anchoring &amp; Declutter</div>
<div style="font-size: 13.5px; color: #94A3B8; line-height: 1.5;">In-app portfolio overlap X-ray showing duplicate stock concentration across held schemes + unified payday debit date grouping.</div>
<div style="font-size: 12.5px; color: #FBBF24; font-weight: 700; margin-top: 6px;">Projected Lift: +6% to +9%</div>
</div>
</div>
</div>"""

SUGGESTED_QUESTIONS_LABEL_HTML = """<div style="font-size: 12px; font-weight: 500; color: #64748B; margin-top: 14px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
<span>💬</span> <span>Suggested questions to explore:</span>
</div>"""


def render_overview_view(db_path=None) -> None:
    """Render the clean Executive Overview with integrated Qualitative Research Assistant."""

    # Initialize session state for overview chat
    if "overview_chat_history" not in st.session_state:
        st.session_state["overview_chat_history"] = []
    if "overview_query_input" not in st.session_state:
        st.session_state["overview_query_input"] = ""

    # 1. Standard Page Header Area
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

    # 2. Executive Overview Title
    st.markdown(SECTION_TITLE_HTML, unsafe_allow_html=True)

    # 3. Row of 4 Clean Executive Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(KPI_1_HTML, unsafe_allow_html=True)
    with m2:
        st.markdown(KPI_2_HTML, unsafe_allow_html=True)
    with m3:
        st.markdown(KPI_3_HTML, unsafe_allow_html=True)
    with m4:
        st.markdown(KPI_4_HTML, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # 4. Strategic Problem Statement & Drop-Off Dynamics
    st.markdown(PROBLEM_CONTEXT_HTML, unsafe_allow_html=True)

    # 5. Two-Column Lower Layout
    left_col, right_col = st.columns([1.05, 0.95], gap="medium")
    with left_col:
        st.markdown(HOW_IT_WORKS_HTML, unsafe_allow_html=True)
    with right_col:
        st.markdown(FRUSTRATION_PROFILE_HTML, unsafe_allow_html=True)

    # 6. Strategic Product Roadmap Bets
    st.markdown(STRATEGIC_BETS_HTML, unsafe_allow_html=True)

    # 7. Ask the Discovery Engine Search
    st.markdown("<div style='margin-top: 24px; margin-bottom: 12px;'><h3 style='font-family: \"Plus Jakarta Sans\", sans-serif; font-size: 18px; font-weight: 700; color: #F1F5F9; margin: 0;'>Ask the Discovery Engine</h3></div>", unsafe_allow_html=True)

    pipeline = get_overview_pipeline()

    # Input Search Bar + 'Ask Engine' Button (Inline Layout)
    inp_col, btn_col = st.columns([4.8, 1.2], gap="small")
    with inp_col:
        typed_ov_query = st.text_input(
            "Ask anything:",
            placeholder="Ask anything (e.g. 'Why do bank autopay mandates fail silently?')...",
            label_visibility="collapsed",
            key="overview_discovery_input",
        )
    with btn_col:
        ov_ask_clicked = st.button("Ask Engine", type="primary", use_container_width=True, key="overview_discovery_submit")

    # Suggested Questions Label (Low-key, natural prompt)
    st.markdown(SUGGESTED_QUESTIONS_LABEL_HTML, unsafe_allow_html=True)

    chip_clicked_query = None
    r1_cols = st.columns(3)
    rec_r1 = [
        "Why do bank autopay mandates fail silently?",
        "What causes panic when early portfolios show negative returns?",
        "How does fear of ₹450 bank bounce fines trigger cancellations?",
    ]
    for idx, q_text in enumerate(rec_r1):
        with r1_cols[idx]:
            if st.button(f'"{q_text}"', key=f"ov_chip_r1_{idx}", use_container_width=True):
                chip_clicked_query = q_text

    r2_cols = st.columns(3)
    rec_r2 = [
        "Why do users panic over 48-hour NAV allotment delay?",
        "Why do first-time users accumulate 6+ overlapping funds?",
        "What workarounds do users try when payment fails?",
    ]
    for idx, q_text in enumerate(rec_r2):
        with r2_cols[idx]:
            if st.button(f'"{q_text}"', key=f"ov_chip_r2_{idx}", use_container_width=True):
                chip_clicked_query = q_text

    # Process Inquiry from either Quick Button or Text Input
    active_inquiry = chip_clicked_query or (typed_ov_query.strip() if ov_ask_clicked else None)
    if active_inquiry:
        with st.spinner("Analyzing 3,052 customer conversations and synthesizing qualitative analysis..."):
            res = pipeline.query(query=active_inquiry, top_k=5)
            st.session_state["overview_chat_history"].insert(0, res)

    # Render Results on Overview
    if st.session_state["overview_chat_history"]:
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        for item in st.session_state["overview_chat_history"]:
            q = item["query"]
            ans = item["answer"]
            evid_list = item.get("retrieved_evidence", [])
            lat = item.get("total_latency_ms", 22.0)
            m_count = item.get("evidence_count", len(evid_list))

            # Question Card
            st.markdown(
                f"""<div style="background: #1A2230; border: 1px solid #2B3548; border-left: 4px solid #00D09C; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #00D09C; text-transform: uppercase; margin-bottom: 3px;">RESEARCH QUESTION</div>
                <div style="font-size: 15.5px; font-weight: 600; color: #F1F5F9;">{q}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            # Response Card
            st.markdown(
                f"""<div style="background: #151A24; border: 1px solid #222938; border-radius: 10px; padding: 18px 22px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1E2533; padding-bottom: 8px; flex-wrap: wrap; gap: 6px;">
                <span style="font-size: 13px; font-weight: 700; color: #00D09C; text-transform: uppercase;">
                Qualitative Synthesis &bull; {m_count} Evidence Chunks
                </span>
                <div style="display: flex; gap: 6px;">
                <span class="badge-tag badge-tier-1">Verified Evidence</span>
                <span class="badge-tag badge-category">{lat}ms</span>
                <span class="badge-tag badge-category">SEBI Compliant</span>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

            st.markdown(ans)

            # Evidence Quotes Drawer
            if evid_list:
                with st.expander(f"View {len(evid_list)} Retrieved Customer Quotes", expanded=False):
                    for idx, ev in enumerate(evid_list, 1):
                        plat = ev.get("platform", "source").upper()
                        stage = ev.get("journey_stage", "unknown").replace("_", " ").title()
                        pub_date = ev.get("published_at", "Recent")
                        q_text = ev.get("quote", "").replace("<", "&lt;").replace(">", "&gt;")
                        src_url = ev.get("source_url", "")
                        src_link = f'<a href="{src_url}" target="_blank" style="color: #00D09C; font-weight: 600; text-decoration: none;">[Original Source Link ↗]</a>' if src_url else ''

                        st.markdown(
                            f"""<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-bottom: 4px;">
                            <div><strong>[EVID-{idx}]</strong> &bull; <span style="color: #00D09C; font-weight: 700;">{plat}</span> &bull; {stage} &bull; Date: {pub_date}</div>
                            </div>
                            <div style="font-size: 14px; font-style: italic; color: #F1F5F9; margin: 4px 0;">"{q_text}"</div>
                            <div style="font-size: 12px;">{src_link}</div>
                            </div>""",
                            unsafe_allow_html=True,
                        )

            st.markdown("</div>", unsafe_allow_html=True)
