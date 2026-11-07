"""Executive Overview Component (matches modern clean Discovery Engine inspiration design).

Displays:
- Core Hypothesis callout banner with lightbulb icon
- 4 Executive Overview KPI cards
- 'How the Discovery Engine Works' pipeline step flow
- 'Frustration Profile' stacked severity bar and key friction drivers
"""

import streamlit as st
from src.ui.components.common_ui import MISSION_BANNER_HTML, get_kpi_card_html

HEADER_HTML = """<div class="page-header-container">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 4px;">
<div style="display: flex; align-items: center; gap: 10px;">
<h1 class="page-title">Groww Discovery Engine</h1>
<span class="badge-tag badge-tier-1">Executive Suite</span>
</div>
</div>
<p class="page-subtitle">AI-powered behavioral analysis of user drop-off and friction points in first-time mutual fund SIP continuation.</p>
</div>"""

SECTION_TITLE_HTML = """<div style="margin-bottom: 10px;">
<h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 22px; font-weight: 700; color: #0F172A; margin: 0;">Executive Overview Metrics</h2>
</div>"""

KPI_1_HTML = get_kpi_card_html("TOTAL SCRAPED REVIEWS", "32,547", "Play Store, App Store, Reddit, YouTube, Forum", "#0F172A", "#008764")
KPI_2_HTML = get_kpi_card_html("CLEAN QUALIFIED SIPS", "3,052", "100% relevant MF conversations", "#008764", "#008764")
KPI_3_HTML = get_kpi_card_html("DATA SOURCES ANALYSED", "5", "Play Store, App Store, Reddit, YouTube, Forum", "#0F172A", "#008764")
KPI_4_HTML = get_kpi_card_html("FAILURE THEMES GENERATED", "7", "Prevalence 3.2% – 18.0% of corpus", "#0284C7", "#0284C7")

HOW_IT_WORKS_HTML = """<div class="overview-section-card" style="height: 100%;">
<h3 style="font-size: 20px; font-weight: 700; color: #0F172A; margin: 0 0 14px 0;">How the Discovery Engine Works</h3>
<div class="pipeline-step-box">
<div style="font-weight: 700; color: #0F172A; font-size: 16.5px;">1. Multi-Channel Ingestion (32.5k+ raw reviews)</div>
<div style="font-size: 15px; color: #64748B; margin-top: 4px; line-height: 1.55;">Harvested across Google Play Store (27.1k), YouTube (3.7k), Reddit (574), Forums (588), App Store (522).</div>
</div>
<div class="pipeline-step-arrow">↓</div>
<div class="pipeline-step-box">
<div style="font-weight: 700; color: #0F172A; font-size: 16.5px;">2. Qualification & Deduplication (3,052 records)</div>
<div style="font-size: 15px; color: #64748B; margin-top: 4px; line-height: 1.55;">Strict MF/SIP qualification, spam filtering, and inverted prefix shingle deduplication.</div>
</div>
<div class="pipeline-step-arrow">↓</div>
<div class="pipeline-step-box">
<div style="font-weight: 700; color: #0F172A; font-size: 16.5px;">3. Pattern Discovery & Problem Theming (7 core themes)</div>
<div style="font-size: 15px; color: #64748B; margin-top: 4px; line-height: 1.55;">Unsupervised clustering, active date spans (2016–2026), platform distribution, and verbatim quote indexing.</div>
</div>
<div class="pipeline-step-arrow">↓</div>
<div class="pipeline-step-box">
<div style="font-weight: 700; color: #0F172A; font-size: 16.5px;">4. Competing Hypotheses & Opportunity Matrix (5-pillar rubric)</div>
<div style="font-size: 15px; color: #64748B; margin-top: 4px; line-height: 1.55;">Competing behavioral hypotheses, user impact scoring, product addressability, and primary interview guides.</div>
</div>
</div>"""

FRUSTRATION_PROFILE_HTML = """<div class="overview-section-card" style="height: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<h3 style="font-size: 20px; font-weight: 700; color: #0F172A; margin: 0;">Discovered Problem Spaces & Severity</h3>
<span class="badge-tag badge-tier-1">4 Findings Mapped</span>
</div>
<div style="display: flex; height: 30px; border-radius: 8px; overflow: hidden; margin-bottom: 12px; font-size: 14.5px; font-weight: 700; color: #FFFFFF; text-align: center; line-height: 30px;">
<div style="width: 74%; background: #EF4444;" title="High Frustration: 74%">74%</div>
<div style="width: 18%; background: #F59E0B;" title="Medium Frustration: 18%">18%</div>
<div style="width: 8%; background: #10B981;" title="Low / Positive: 8%">8%</div>
</div>
<div style="display: flex; gap: 18px; font-size: 15px; color: #64748B; margin-bottom: 14px;">
<div><span style="color: #EF4444; font-size: 16px;">●</span> <strong>High Frustration</strong> (74%)</div>
<div><span style="color: #F59E0B; font-size: 16px;">●</span> <strong>Medium Friction</strong> (18%)</div>
<div><span style="color: #10B981; font-size: 16px;">●</span> <strong>Habit Anchors</strong> (8%)</div>
</div>
<div style="border-top: 1px solid var(--groww-border-subtle); padding-top: 14px;">
<div style="font-size: 15.5px; margin-bottom: 10px;">
<span style="color: #008764; font-weight: 800; font-size: 16px;">🎯 The 4 Core Research Findings & Empirical Theme Mapping:</span>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 14px; line-height: 1.6;">
  <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #7C3AED; padding: 10px 14px; border-radius: 8px;">
    <strong style="color: #7C3AED;">1. Market Fluctuations (11.2%)</strong><br/>
    • Early Drawdown Panic (Theme 04 — 5.9%)<br/>
    • Price Uncertainty in T+2 NAV Delay (Theme 06 — 5.3%)
  </div>
  <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #D97706; padding: 10px 14px; border-radius: 8px;">
    <strong style="color: #D97706;">2. Not Setting Financial Goals (12.5%)</strong><br/>
    • Goal-Deficient Over-Diversification (Theme 02 — 9.3%)<br/>
    • Milestone Disconnect vs Discipline (Theme 07 — 3.2%)
  </div>
  <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #EF4444; padding: 10px 14px; border-radius: 8px;">
    <strong style="color: #EF4444;">3. Lack of Emergency Funds (24.6%)</strong><br/>
    • Cash-Flow Timing & Mandate Drops (Theme 01 — 18.0%)<br/>
    • ECS Bounce Penalty Trap (Theme 03 — 6.6%)
  </div>
  <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #0284C7; padding: 10px 14px; border-radius: 8px;">
    <strong style="color: #0284C7;">4. Unrealistic Return Expectations (6.3%)</strong><br/>
    • XIRR Distortion & Linear Growth Gap (Theme 05 — 6.3%)
  </div>
</div>
</div>
</div>"""


def render_overview_view(db_path=None) -> None:
    """Render the clean Executive Overview matching the modern Discovery Engine design."""
    

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

    # 4. Two-Column Lower Layout
    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        st.markdown(HOW_IT_WORKS_HTML, unsafe_allow_html=True)

    with right_col:
        st.markdown(FRUSTRATION_PROFILE_HTML, unsafe_allow_html=True)
