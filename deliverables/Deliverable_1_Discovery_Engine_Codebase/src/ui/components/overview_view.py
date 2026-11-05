"""Executive Overview Component (matches modern clean Discovery Engine inspiration design).

Displays:
- Core Hypothesis callout banner with lightbulb icon
- 4 Executive Overview KPI cards
- 'How the Discovery Engine Works' pipeline step flow
- 'Frustration Profile' stacked severity bar and key friction drivers
"""

import streamlit as st

HEADER_HTML = """<div class="page-header-container">
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <h1 class="page-title">Groww Discovery Engine</h1>
            <span class="badge-tag badge-tier-1">Executive Suite</span>
        </div>
    </div>
    <p class="page-subtitle">AI-powered behavioral analysis of user drop-off and friction points in first-time mutual fund SIP continuation.</p>
</div>"""

HYPOTHESIS_HTML = """<div style="background: linear-gradient(135deg, #F0FDF9 0%, #EFF6FF 100%); border: 1px solid #CCFBF1; border-left: 4.5px solid #00D09C; border-radius: 12px; padding: 18px 22px; margin-bottom: 24px; box-shadow: var(--groww-card-shadow); display: flex; align-items: flex-start; gap: 16px;">
    <div style="font-size: 24px; line-height: 1; padding-top: 2px;">💡</div>
    <div style="font-size: 13.5px; color: #1E293B; line-height: 1.65;">
        <strong style="color: #008764; font-size: 14px; font-weight: 700;">Core Hypothesis:</strong> First-time SIP investors discontinue within 3–6 months not because of lack of wealth-building intent, but because friction compounds across <strong>technical mandate failures</strong> (₹1L NPCI authorization limit shock, silent bank bounces), <strong>cognitive return shock</strong> (early negative XIRR panic), and <strong>over-diversification overlap confusion</strong>.
    </div>
</div>"""

SECTION_TITLE_HTML = """<div style="margin-bottom: 14px;">
    <h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 17px; font-weight: 700; color: #0F172A; margin: 0;">Executive Overview Metrics</h2>
</div>"""

KPI_1_HTML = """<div class="executive-kpi-card">
    <div class="kpi-value">32,547</div>
    <div class="kpi-title">TOTAL SCRAPED REVIEWS</div>
    <div class="kpi-subtitle">Play Store, App Store, Reddit, YouTube, Forum</div>
</div>"""

KPI_2_HTML = """<div class="executive-kpi-card">
    <div class="kpi-value" style="color: #008764;">3,052</div>
    <div class="kpi-title">CLEAN QUALIFIED SIPS</div>
    <div class="kpi-subtitle">100% relevant MF conversations</div>
</div>"""

KPI_3_HTML = """<div class="executive-kpi-card">
    <div class="kpi-value">5</div>
    <div class="kpi-title">DATA SOURCES ANALYSED</div>
    <div class="kpi-subtitle">Play Store, App Store, Reddit, YouTube, Forum</div>
</div>"""

KPI_4_HTML = """<div class="executive-kpi-card">
    <div class="kpi-value" style="color: #0284C7;">7</div>
    <div class="kpi-title">FAILURE THEMES GENERATED</div>
    <div class="kpi-subtitle">Prevalence 3.2% – 18.0% of corpus</div>
</div>"""

HOW_IT_WORKS_HTML = """<div class="overview-section-card" style="height: 100%;">
    <h3 style="font-size: 16px; font-weight: 700; color: #0F172A; margin: 0 0 16px 0;">How the Discovery Engine Works</h3>
    <div class="pipeline-step-box">
        <div style="font-weight: 700; color: #0F172A; font-size: 13.5px;">1. Multi-Channel Ingestion (32.5k+ raw reviews)</div>
        <div style="font-size: 12px; color: #64748B; margin-top: 3px;">Harvested across Google Play Store (27.1k), YouTube (3.7k), Reddit (574), Forums (588), App Store (522).</div>
    </div>
    <div class="pipeline-step-arrow">↓</div>
    <div class="pipeline-step-box">
        <div style="font-weight: 700; color: #0F172A; font-size: 13.5px;">2. Qualification & Deduplication (3,052 records)</div>
        <div style="font-size: 12px; color: #64748B; margin-top: 3px;">Strict MF/SIP qualification, spam filtering, and inverted prefix shingle deduplication.</div>
    </div>
    <div class="pipeline-step-arrow">↓</div>
    <div class="pipeline-step-box">
        <div style="font-weight: 700; color: #0F172A; font-size: 13.5px;">3. Pattern Discovery & Problem Theming (7 core themes)</div>
        <div style="font-size: 12px; color: #64748B; margin-top: 3px;">Unsupervised clustering, active date spans (2016–2026), platform distribution, and verbatim quote indexing.</div>
    </div>
    <div class="pipeline-step-arrow">↓</div>
    <div class="pipeline-step-box">
        <div style="font-weight: 700; color: #0F172A; font-size: 13.5px;">4. Competing Hypotheses & Opportunity Matrix (5-pillar rubric)</div>
        <div style="font-size: 12px; color: #64748B; margin-top: 3px;">Competing behavioral hypotheses, user impact scoring, product addressability, and primary interview guides.</div>
    </div>
</div>"""

FRUSTRATION_PROFILE_HTML = """<div class="overview-section-card" style="height: 100%;">
    <h3 style="font-size: 16px; font-weight: 700; color: #0F172A; margin: 0 0 16px 0;">Frustration Profile & Drop-off Severity</h3>
    <div style="display: flex; height: 26px; border-radius: 8px; overflow: hidden; margin-bottom: 12px; font-size: 11px; font-weight: 700; color: #FFFFFF; text-align: center; line-height: 26px;">
        <div style="width: 74%; background: #EF4444;" title="High Frustration: 74%">74%</div>
        <div style="width: 18%; background: #F59E0B;" title="Medium Frustration: 18%">18%</div>
        <div style="width: 8%; background: #10B981;" title="Low / Positive: 8%">8%</div>
    </div>
    <div style="display: flex; gap: 16px; font-size: 12px; color: #64748B; margin-bottom: 18px;">
        <div><span style="color: #EF4444; font-size: 14px;">●</span> <strong>High</strong> (74%)</div>
        <div><span style="color: #F59E0B; font-size: 14px;">●</span> <strong>Medium</strong> (18%)</div>
        <div><span style="color: #10B981; font-size: 14px;">●</span> <strong>Low / Anchors</strong> (8%)</div>
    </div>
    <div style="border-top: 1px solid var(--groww-border-subtle); padding-top: 14px;">
        <div style="font-size: 12.5px; margin-bottom: 12px;">
            <span style="color: #DC2626; font-weight: 700;">● High Severity (Action Required):</span><br/>
            <span style="color: #475569; font-size: 12px; line-height: 1.6;">
                • Bank Autopay Mandate & Deduction Failures (18.0% prevalence)<br/>
                • Fear of Bank ECS Bounce Penalties during salary delay (6.6%)<br/>
                • Early-Tenure Negative Return Panic in Months 1–3 (5.9%)
            </span>
        </div>
        <div style="font-size: 12.5px; margin-bottom: 12px;">
            <span style="color: #D97706; font-weight: 700;">● Medium Severity (Decision Fatigue):</span><br/>
            <span style="color: #475569; font-size: 12px; line-height: 1.6;">
                • Over-Diversification & Portfolio Overlap (9.3% prevalence)<br/>
                • Cognitive Return Confusion: XIRR vs Absolute Return (6.3%)<br/>
                • Settlement Anxiety: NAV Timing & Unit Allotment Lag (5.3%)
            </span>
        </div>
        <div style="font-size: 12.5px;">
            <span style="color: #059669; font-weight: 700;">● Positive Habit Anchors (Retention Clues):</span><br/>
            <span style="color: #475569; font-size: 12px; line-height: 1.6;">
                • Goal-linked SIPs, stepping up during market dips, long-term horizon (3.2%)
            </span>
        </div>
    </div>
</div>"""


def render_overview_view(db_path=None) -> None:
    """Render the clean Executive Overview matching the modern Discovery Engine design."""
    
    # 1. Standard Page Header Area
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

    # 2. Core Hypothesis Callout Banner
    st.markdown(HYPOTHESIS_HTML, unsafe_allow_html=True)

    # 3. Executive Overview Title
    st.markdown(SECTION_TITLE_HTML, unsafe_allow_html=True)

    # 4. Row of 4 Clean Executive Metric Cards
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(KPI_1_HTML, unsafe_allow_html=True)
    with m2:
        st.markdown(KPI_2_HTML, unsafe_allow_html=True)
    with m3:
        st.markdown(KPI_3_HTML, unsafe_allow_html=True)
    with m4:
        st.markdown(KPI_4_HTML, unsafe_allow_html=True)

    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

    # 5. Two-Column Lower Layout
    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        st.markdown(HOW_IT_WORKS_HTML, unsafe_allow_html=True)

    with right_col:
        st.markdown(FRUSTRATION_PROFILE_HTML, unsafe_allow_html=True)
