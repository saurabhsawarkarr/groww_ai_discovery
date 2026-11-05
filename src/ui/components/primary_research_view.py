"""Primary Research Component: User Survey & 1:1 Interview Guides.

Provides ready-to-deploy user survey instruments and qualitative 1:1 interview protocols
derived from the 7 discovered problem themes.
"""

import streamlit as st
from src.ui.components.common_ui import MISSION_BANNER_HTML, get_kpi_card_html


def render_primary_research_view(db_path=None) -> None:
    """Render Primary Research tools (Surveys and 1:1 Interview Protocols)."""
    
    # 0. Top Mission Philosophy Banner
    st.markdown(MISSION_BANNER_HTML, unsafe_allow_html=True)

    st.markdown(
        """<div class="page-header-container">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px;">
<div style="display: flex; align-items: center; gap: 10px;">
<h1 class="page-title">Primary Research: Survey & 1:1 Interview Protocols</h1>
<span class="badge-tag badge-tier-1">Ready to Deploy</span>
</div>
</div>
<p class="page-subtitle">Pre-formulated qualitative interview guides and quantitative survey instruments ready for deployment to Groww user cohorts.</p>
</div>""",
        unsafe_allow_html=True,
    )

    # 4-Card Hero Metric Grid matching inspiration design
    pkpi1 = get_kpi_card_html("RESEARCH INSTRUMENTS", "2", "Micro-Survey & 1:1 Guide", "#0F172A", "#008764")
    pkpi2 = get_kpi_card_html("TARGET USER COHORTS", "4", "Novice, Salary-Delay, Overlap, Churned", "#0F172A", "#008764")
    pkpi3 = get_kpi_card_html("QUESTION BATTERY", "25+", "Non-Leading Behavioral Probes", "#008764", "#008764")
    pkpi4 = get_kpi_card_html("ETHICAL COMPLIANCE", "100%", "Strict SEBI Non-Advice Guardrails", "#0284C7", "#0284C7")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(pkpi1, unsafe_allow_html=True)
    with c2:
        st.markdown(pkpi2, unsafe_allow_html=True)
    with c3:
        st.markdown(pkpi3, unsafe_allow_html=True)
    with c4:
        st.markdown(pkpi4, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    tab_survey, tab_interviews = st.tabs(["📋 In-App Micro-Survey Instrument", "🎙️ 1:1 Primary User Interview Protocol"])

    with tab_survey:
        st.markdown(
            """<div class="overview-section-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<div>
<span class="badge-tag badge-play-store" style="margin-bottom: 6px;">Trigger: Cancel / Pause SIP Flow</span>
<h3 style="font-size: 20px; font-weight: 700; color: #0F172A; margin: 4px 0 0 0;">
30-Second Micro-Survey (In-App Cancellation Intercept)
</h3>
</div>
<span style="font-size: 14px; color: #64748B; background: #F1F5F9; padding: 4px 10px; border-radius: 6px; font-weight: 600;">Target: 2nd Consecutive Failure or Manual Pause</span>
</div>
<p style="font-size: 16px; color: #475569; line-height: 1.6; margin-bottom: 14px;">
Deploy this 2-question micro-survey immediately when an investor initiates a SIP pause or when an autopay mandate experiences two consecutive bank-side rejections.
</p>
</div>""",
            unsafe_allow_html=True,
        )

        # Interactive Simulation of Survey Questions
        survey_col1, survey_col2 = st.columns(2, gap="medium")

        with survey_col1:
            st.markdown(
                """<div class="evidence-card" style="border-top: 3px solid #00D09C; margin-bottom: 0;">
<span style="font-size: 13.5px; font-weight: 700; color: #008764; text-transform: uppercase;">QUESTION 1 OF 2</span>
<h4 style="font-size: 18px; font-weight: 700; color: #0F172A; margin: 6px 0 12px 0;">What is the primary reason for stopping your SIP today?</h4>
</div>""",
                unsafe_allow_html=True,
            )
            q1_choice = st.radio(
                "Select primary drop-off driver:",
                [
                    "⏳ Temporary cash flow delay (salary delay or urgent expense)",
                    "🏦 Bank / Autopay issue (mandate failed, afraid of ₹450 bounce fees)",
                    "📉 Market / Returns concern (portfolio in red / early drawdown panic)",
                    "🧹 Portfolio cleanup (too many funds, consolidating portfolio)",
                    "❓ App / Settlement confusion (unclear NAV timing or XIRR calculation)",
                ],
                key="survey_q1",
                label_visibility="collapsed",
            )

        with survey_col2:
            st.markdown(
                """<div class="evidence-card" style="border-top: 3px solid #0284C7; margin-bottom: 0;">
<span style="font-size: 13.5px; font-weight: 700; color: #0284C7; text-transform: uppercase;">QUESTION 2 OF 2</span>
<h4 style="font-size: 18px; font-weight: 700; color: #0F172A; margin: 6px 0 12px 0;">If Groww offered 1-click instant UPI retry with zero bounce penalties, would you continue?</h4>
</div>""",
                unsafe_allow_html=True,
            )
            q2_choice = st.radio(
                "Select retention propensity:",
                [
                    "✅ Yes, definitely (removes payment friction completely)",
                    "🤔 Maybe, depending on next month's cash flow",
                    "❌ No, I want to exit mutual funds entirely",
                ],
                key="survey_q2",
                label_visibility="collapsed",
            )

        if st.button("Simulate In-App Response Submission"):
            st.success("✅ Survey response recorded! Diagnostic analytics updated in real-time.")

    with tab_interviews:
        st.markdown(
            """<div class="overview-section-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<div>
<span class="badge-tag badge-tier-1">Protocol Format</span>
<h3 style="font-size: 20px; font-weight: 700; color: #0F172A; margin: 4px 0 0 0;">
30-Minute Qualitative 1:1 Semi-Structured Interview Guide
</h3>
</div>
<span style="font-size: 14px; color: #64748B; background: #F1F5F9; padding: 4px 10px; border-radius: 6px; font-weight: 600;">Target Cohort: Churned Month 2–4 Users</span>
</div>
<p style="font-size: 16px; color: #475569; line-height: 1.6; margin-bottom: 14px;">
Designed to uncover subconscious mental models and friction triggers without introducing researcher confirmation bias.
</p>
</div>""",
            unsafe_allow_html=True,
        )

        # 4 Structured Interview Phases in Clean Cards
        phases = [
            {
                "phase": "Phase 1: Onboarding Mental Model & Initial Expectations",
                "duration": "5 minutes",
                "color": "#7C3AED",
                "questions": [
                    "Take me back to the exact day you decided to start your first SIP on Groww. What prompted you to invest?",
                    "What return, timeline, or financial milestone were you picturing in your head when you set up the mandate?",
                ],
            },
            {
                "phase": "Phase 2: First Drawdown Reaction & Monitoring Habits",
                "duration": "10 minutes",
                "color": "#0284C7",
                "questions": [
                    "How often did you check your mutual fund balance during your first 60 days of investing?",
                    "Walk me through the very first time you opened the app and saw your portfolio showing negative numbers (red). What thoughts crossed your mind?",
                    "Did you discuss the negative returns with anyone (friends, family, Reddit, YouTube) before making a decision?",
                ],
            },
            {
                "phase": "Phase 3: The Breaking Point (Churn Friction Event)",
                "duration": "10 minutes",
                "color": "#EF4444",
                "questions": [
                    "Describe the exact week or event that led to your SIP stopping. Was it a deliberate choice, or did a bank payment fail?",
                    "Did your bank charge an ECS bounce fee, or did you receive warning alerts before the scheduled debit date?",
                    "Did you try to resume the SIP through any alternative payment method like instant UPI?",
                ],
            },
            {
                "phase": "Phase 4: Counter-Factual Resolution & Product Nudges",
                "duration": "5 minutes",
                "color": "#10B981",
                "questions": [
                    "If Groww had sent you an alert 48 hours prior offering a flexible 1-month pause button, what would you have done?",
                    "What is the single most important change in the app that would give you the confidence to restart and continue for 3+ years?",
                ],
            },
        ]

        for p in phases:
            questions_html = "".join([f'<div style="font-size: 16px; color: #334155; margin-bottom: 8px; line-height: 1.6;">• <em>"{q}"</em></div>' for q in p['questions']])
            phase_card_html = (
                f'<div class="evidence-card" style="border-left: 4px solid {p["color"]}; margin-bottom: 12px;">'
                f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
                f'<h4 style="font-size: 18px; font-weight: 700; color: #0F172A; margin: 0;">{p["phase"]}</h4>'
                f'<span style="font-size: 13.5px; font-weight: 700; color: {p["color"]}; background: #F8FAFC; padding: 3px 8px; border-radius: 4px; border: 1px solid #E2E8F0;">⏱️ {p["duration"]}</span>'
                f'</div>'
                f'<div style="margin-top: 8px;">{questions_html}</div>'
                f'</div>'
            )
            st.markdown(phase_card_html, unsafe_allow_html=True)
