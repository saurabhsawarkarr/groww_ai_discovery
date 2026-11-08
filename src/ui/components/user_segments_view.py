"""User Segments & Journey Stages Component.

Displays qualitative investor segmentation across the first-year SIP lifecycle:
- Newly Started (Months 1–3)
- Considering Change / Pausing (Months 4–6)
- Stopped / Involuntarily Churned (Months 6–12)
- Continuing Disciplined Investors (12+ Months)
"""

import streamlit as st
from src.ui.components.common_ui import MISSION_BANNER_HTML


def render_user_segments_view(db_path=None) -> None:
    """Render User Segments & Journey Stages."""
    

    st.markdown(
        """<div class="page-header-container">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px;">
<div style="display: flex; align-items: center; gap: 10px;">
<h1 class="page-title">User Segments & First-Year Journey Stages</h1>
<span class="badge-tag badge-tier-1">4 Empirical Cohorts</span>
</div>
</div>
<p class="page-subtitle">Empirical investor cohorts tracked across the 12-month mutual fund SIP continuation lifecycle.</p>
</div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            """<div class="executive-kpi-card" style="border-top: 4px solid #7C3AED; text-align: left; padding: 18px;">
<span class="badge-tag badge-stage-new" style="margin-bottom: 8px;">Stage 1 &bull; Mo 1–3</span>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 800; color: #F1F5F9; margin: 4px 0 6px 0;">Newly Started</div>
<div style="font-size: 15.5px; color: #94A3B8; line-height: 1.55;">Daily app check-ins, high volatility anxiety, early negative XIRR shock.</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """<div class="executive-kpi-card" style="border-top: 4px solid #F59E0B; text-align: left; padding: 18px;">
<span style="font-size: 13.5px; font-weight: 700; color: #D97706; background: rgba(217, 119, 6, 0.08); padding: 3px 8px; border-radius: 6px; text-transform: uppercase;">Stage 2 &bull; Mo 4–6</span>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 800; color: #F1F5F9; margin: 4px 0 6px 0;">Considering Change</div>
<div style="font-size: 15.5px; color: #94A3B8; line-height: 1.55;">Portfolio overlap realization (holding 6+ funds), salary timing cash crunch.</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """<div class="executive-kpi-card" style="border-top: 4px solid #EF4444; text-align: left; padding: 18px;">
<span class="badge-tag badge-stage-stopped" style="margin-bottom: 8px;">Stage 3 &bull; Mo 6–12</span>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 800; color: #F1F5F9; margin: 4px 0 6px 0;">Involuntarily Stopped</div>
<div style="font-size: 15.5px; color: #94A3B8; line-height: 1.55;">Silent bank mandate cancellation, bounce fee scare, lack of UPI retry link.</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """<div class="executive-kpi-card" style="border-top: 4px solid #10B981; text-align: left; padding: 18px;">
<span class="badge-tag badge-stage-continuing" style="margin-bottom: 8px;">Stage 4 &bull; 12+ Mo</span>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 800; color: #F1F5F9; margin: 4px 0 6px 0;">Continuing Investors</div>
<div style="font-size: 15.5px; color: #94A3B8; line-height: 1.55;">Goal-anchored mental models, stepping up SIPs during market corrections.</div>
</div>""",
            unsafe_allow_html=True,
        )

    # Detailed Cohort Deep Dive Cards
    st.markdown(
        """<div class="overview-section-card" style="margin-top: 14px; margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<h3 style="margin: 0; font-size: 20px; color: #F1F5F9; font-weight: 700;">Cohort A: The Volatility Shocked Novice (Months 1–3)</h3>
<span class="badge-tag badge-stage-new">High Voluntary Churn Risk</span>
</div>
<p style="font-size: 16px; color: #94A3B8; line-height: 1.6; margin-bottom: 10px;">
These users started their very first ₹500 or ₹1,000 SIP following a market high. They open the app 3–5 times weekly, treat the SIP like a fixed deposit, and panic when their portfolio shows -2.4% return.
</p>
<div class="verbatim-quote-box" style="border-left-color: #7C3AED; background: rgba(124, 58, 237, 0.05); font-size: 16.5px; font-style: italic;">
"I started my first SIP of 1000 in flexi cap fund 2 months ago, but current value is 975 (-2.5%). Should I stop the SIP immediately before I lose more money?"
</div>
</div>

<div class="overview-section-card" style="margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<h3 style="margin: 0; font-size: 20px; color: #F1F5F9; font-weight: 700;">Cohort B: The Involuntary Churn Victim (Mandate / Bank Failure)</h3>
<span class="badge-tag badge-play-store">Severe Technical Friction</span>
</div>
<p style="font-size: 16px; color: #94A3B8; line-height: 1.6; margin-bottom: 10px;">
These users intend to invest, but their bank autopay mandate fails due to bank-side maintenance, salary delayed by 2 days, or fear of ₹450 bank bounce charges. Because no instant 1-click UPI retry link is provided, the SIP lapses silently.
</p>
<div class="verbatim-quote-box" style="border-left-color: #EF4444; background: rgba(239, 68, 68, 0.05); font-size: 16.5px; font-style: italic;">
"SIP payment got debited from my bank but Groww status showed processing for 4 days. During this time I could not tell if the transaction failed or succeeded."
</div>
</div>

<div class="overview-section-card" style="margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<h3 style="margin: 0; font-size: 20px; color: #F1F5F9; font-weight: 700;">Cohort C: The Over-Diversified Confused Investor</h3>
<span class="badge-tag badge-reddit">Decision & Cognitive Fatigue</span>
</div>
<p style="font-size: 16px; color: #94A3B8; line-height: 1.6; margin-bottom: 10px;">
Under social media advice, they started 6–8 small funds across small-cap, mid-cap, flexi-cap, and index funds. Managing 8 different deduction dates causes mental fatigue, and they eventually pause all of them.
</p>
<div class="verbatim-quote-box" style="border-left-color: #F59E0B; background: rgba(245, 158, 11, 0.05); font-size: 16.5px; font-style: italic;">
"Currently doing SIP in 7 different funds totaling 12k/month. Realized 4 of them hold the exact same top 10 stocks. Too many deduction dates to manage, want to clean up."
</div>
</div>

<div class="overview-section-card" style="margin-bottom: 14px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<h3 style="margin: 0; font-size: 20px; color: #F1F5F9; font-weight: 700;">Cohort D: The Goal-Anchored Disciplined Compounder (Months 12+)</h3>
<span class="badge-tag badge-stage-continuing">Resilient Retention Benchmark</span>
</div>
<p style="font-size: 16px; color: #94A3B8; line-height: 1.6; margin-bottom: 10px;">
Having crossed the critical 1-year threshold, these investors anchored their SIP to an emotional life milestone (e.g., child education or home purchase). They deliberately ignore daily market gyrations, check balances monthly, and treat drawdowns as buying opportunities by stepping up contributions.
</p>
<div class="verbatim-quote-box" style="border-left-color: #10B981; background: rgba(16, 185, 129, 0.05); font-size: 16.5px; font-style: italic;">
"Very happy with the disciplined investing habit Groww helped me build. Completed 18 consecutive months of SIP without missing a single payment. Autopay mandate has been 100% reliable."
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # Cross-Cohort Behavioral Comparison Matrix
    st.markdown(
        """<div style="margin-top: 16px; margin-bottom: 10px;">
<div style="display: flex; align-items: center; justify-content: space-between;">
<div>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 700; color: #F1F5F9; margin: 0 0 4px 0;">Cross-Cohort Behavioral Comparison Matrix</h3>
<div style="font-size: 15px; color: #94A3B8;">Multi-dimensional comparison across lifecycle habits, failure triggers, drawdown psychology, and growth interventions.</div>
</div>
<span class="badge-tag badge-tier-1">Executive Comparison</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div style="overflow-x: auto; background: #FFFFFF; border: 1px solid var(--groww-card-border); border-radius: 12px; padding: 6px; box-shadow: var(--groww-card-shadow); margin-bottom: 16px;">
<table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 15px;">
<thead>
<tr style="border-bottom: 1px solid #E2E8F0; background: #F8FAFC; text-align: left;">
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">Cohort & Stage</th>
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">App Monitoring Habit</th>
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">Core Mental Model</th>
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">Primary Failure Trigger</th>
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">Reaction to -5% Dip</th>
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">12M Churn Risk</th>
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">Growth Intervention Lever</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #F1F5F9;">
<td style="padding: 12px 14px; font-weight: 700; color: #7C3AED;">Cohort A<br/><span style="font-size: 13px; font-weight: 400; color: #94A3B8;">Mo 1–3</span></td>
<td style="padding: 12px 14px; color: #334155;">3–5x Daily (Anxious)</td>
<td style="padding: 12px 14px; color: #334155;">Fixed Deposit Proxy (expects linear growth)</td>
<td style="padding: 12px 14px; color: #DC2626; font-weight: 600;">Negative XIRR Shock & NAV Delays</td>
<td style="padding: 12px 14px; color: #DC2626;">Panic Cancels Mandate</td>
<td style="padding: 12px 14px;"><span style="background: rgba(220, 38, 38, 0.1); color: #DC2626; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">CRITICAL</span></td>
<td style="padding: 12px 14px; color: #0284C7; font-weight: 600;">First-90-Day Volatility Pacing Shield</td>
</tr>
<tr style="border-bottom: 1px solid #F1F5F9; background: #FCFDFF;">
<td style="padding: 12px 14px; font-weight: 700; color: #EF4444;">Cohort B<br/><span style="font-size: 13px; font-weight: 400; color: #94A3B8;">Mo 2–6</span></td>
<td style="padding: 12px 14px; color: #334155;">Monthly (on Debit Alert)</td>
<td style="padding: 12px 14px; color: #334155;">Set-and-Forget Autopay</td>
<td style="padding: 12px 14px; color: #DC2626; font-weight: 600;">Silent Mandate Drop & ₹450 Bounce Fee</td>
<td style="padding: 12px 14px; color: #D97706;">Gives Up After Bank Rejection</td>
<td style="padding: 12px 14px;"><span style="background: rgba(220, 38, 38, 0.1); color: #DC2626; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">SEVERE</span></td>
<td style="padding: 12px 14px; color: #0284C7; font-weight: 600;">1-Click UPI Fallback & Salary Shift</td>
</tr>
<tr style="border-bottom: 1px solid #F1F5F9;">
<td style="padding: 12px 14px; font-weight: 700; color: #D97706;">Cohort C<br/><span style="font-size: 13px; font-weight: 400; color: #94A3B8;">Mo 4–6</span></td>
<td style="padding: 12px 14px; color: #334155;">Weekly (Multi-Graph Check)</td>
<td style="padding: 12px 14px; color: #334155;">Hype-Driven Diversification (6+ Funds)</td>
<td style="padding: 12px 14px; color: #D97706; font-weight: 600;">70% Overlap & Cognitive Fatigue</td>
<td style="padding: 12px 14px; color: #D97706;">Freezes & Pauses Indiscriminately</td>
<td style="padding: 12px 14px;"><span style="background: rgba(217, 119, 6, 0.1); color: #D97706; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">MODERATE</span></td>
<td style="padding: 12px 14px; color: #0284C7; font-weight: 600;">Portfolio Overlap Cleaner Tool</td>
</tr>
<tr>
<td style="padding: 12px 14px; font-weight: 700; color: #059669;">Cohort D<br/><span style="font-size: 13px; font-weight: 400; color: #94A3B8;">12+ Mo</span></td>
<td style="padding: 12px 14px; color: #334155;">Monthly / Quarterly</td>
<td style="padding: 12px 14px; color: #334155;">Goal-Anchored Wealth Accumulator</td>
<td style="padding: 12px 14px; color: #059669; font-weight: 600;">Portfolio Rebalancing Needs</td>
<td style="padding: 12px 14px; color: #059669; font-weight: 700;">Steps Up SIP Contribution</td>
<td style="padding: 12px 14px;"><span style="background: rgba(16, 185, 129, 0.1); color: #059669; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">LOW / RESILIENT</span></td>
<td style="padding: 12px 14px; color: #0284C7; font-weight: 600;">Annual Step-Up & Goal Milestone Nudges</td>
</tr>
</tbody>
</table>
</div>""",
        unsafe_allow_html=True,
    )

    # Segment × Failure Theme Vulnerability Mapping
    st.markdown(
        """<div style="margin-top: 14px; margin-bottom: 10px;">
<div style="display: flex; align-items: center; justify-content: space-between;">
<div>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 700; color: #F1F5F9; margin: 0 0 4px 0;">Segment × Failure Theme Vulnerability Heatmap</h3>
<div style="font-size: 15px; color: #94A3B8;">Correlating how the 7 empirical failure themes impact specific investor lifecycle stages.</div>
</div>
<span class="badge-tag badge-tier-1">Empirical Mapping</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div style="overflow-x: auto; background: #FFFFFF; border: 1px solid var(--groww-card-border); border-radius: 12px; padding: 6px; box-shadow: var(--groww-card-shadow); margin-bottom: 16px;">
<table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 15px;">
<thead>
<tr style="border-bottom: 1px solid #E2E8F0; background: #F8FAFC; text-align: left;">
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">Empirical Failure Theme</th>
<th style="padding: 12px 14px; font-weight: 700; color: #7C3AED; font-size: 13.5px; text-transform: uppercase; text-align: center;">Cohort A (Mo 1–3)</th>
<th style="padding: 12px 14px; font-weight: 700; color: #EF4444; font-size: 13.5px; text-transform: uppercase; text-align: center;">Cohort B (Mo 2–6)</th>
<th style="padding: 12px 14px; font-weight: 700; color: #D97706; font-size: 13.5px; text-transform: uppercase; text-align: center;">Cohort C (Mo 4–6)</th>
<th style="padding: 12px 14px; font-weight: 700; color: #059669; font-size: 13.5px; text-transform: uppercase; text-align: center;">Cohort D (12+ Mo)</th>
<th style="padding: 12px 14px; font-weight: 700; color: #94A3B8; font-size: 13.5px; text-transform: uppercase;">Core Churn Mechanism</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #F1F5F9;">
<td style="padding: 12px 14px; font-weight: 600; color: #F1F5F9;">THEME-01: Cash-Flow Timing Mismatches & Autopay Deduction Drops</td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Moderate</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="background: rgba(220, 38, 38, 0.12); color: #DC2626; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">PRIMARY (18.0%)</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Moderate</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; color: #94A3B8; font-size: 15px;">Silent bank mandate drop without retry fallback (Finding 3: Lack of Emergency Funds)</td>
</tr>
<tr style="border-bottom: 1px solid #F1F5F9; background: #FCFDFF;">
<td style="padding: 12px 14px; font-weight: 600; color: #F1F5F9;">THEME-02: Goal-Deficient Over-Diversification & Portfolio Clutter</td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="background: rgba(217, 119, 6, 0.12); color: #D97706; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">PRIMARY (9.3%)</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; color: #94A3B8; font-size: 15px;">Managing 7 deduction dates & overlapping stocks (Finding 2: Not Setting Financial Goals)</td>
</tr>
<tr style="border-bottom: 1px solid #F1F5F9;">
<td style="padding: 12px 14px; font-weight: 600; color: #F1F5F9;">THEME-03: Emergency Buffer Deficit & The ECS Bounce Penalty Trap</td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Moderate</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="background: rgba(220, 38, 38, 0.12); color: #DC2626; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">PRIMARY (6.6%)</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; color: #94A3B8; font-size: 15px;">₹450 bank penalty during temporary cash crunch (Finding 3: Lack of Emergency Funds)</td>
</tr>
<tr style="border-bottom: 1px solid #F1F5F9; background: #FCFDFF;">
<td style="padding: 12px 14px; font-weight: 600; color: #F1F5F9;">THEME-04: Early Drawdown Panic & Volatility Shock (Months 1–3)</td>
<td style="padding: 12px 14px; text-align: center;"><span style="background: rgba(124, 58, 237, 0.12); color: #7C3AED; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">PRIMARY (5.9%)</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="background: rgba(16, 185, 129, 0.1); color: #059669; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">RESILIENT (Stepped Up)</span></td>
<td style="padding: 12px 14px; color: #94A3B8; font-size: 15px;">Treating SIP like FD and panicking at -2% loss (Finding 1: Market Fluctuations)</td>
</tr>
<tr style="border-bottom: 1px solid #F1F5F9;">
<td style="padding: 12px 14px; font-weight: 600; color: #F1F5F9;">THEME-05: Unrealistic Growth Expectations & XIRR Metric Distortion</td>
<td style="padding: 12px 14px; text-align: center;"><span style="background: rgba(124, 58, 237, 0.12); color: #7C3AED; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">PRIMARY (6.3%)</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Moderate</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; color: #94A3B8; font-size: 15px;">Annualized calculation distortion on small tenures (Finding 4: Unrealistic Return Expectations)</td>
</tr>
<tr style="border-bottom: 1px solid #F1F5F9; background: #FCFDFF;">
<td style="padding: 12px 14px; font-weight: 600; color: #F1F5F9;">THEME-06: Price-Fluctuation Uncertainty during NAV Settlement Delays</td>
<td style="padding: 12px 14px; text-align: center;"><span style="background: rgba(124, 58, 237, 0.12); color: #7C3AED; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">PRIMARY (5.3%)</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Moderate</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; color: #94A3B8; font-size: 15px;">UPI instant mindset vs T+2 unit allotment delay (Finding 1: Market Fluctuations)</td>
</tr>
<tr>
<td style="padding: 12px 14px; font-weight: 600; color: #F1F5F9;">THEME-07: Milestone Disconnect vs. Goal-Anchored Discipline</td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="color: #94A3B8;">Low</span></td>
<td style="padding: 12px 14px; text-align: center;"><span style="background: rgba(16, 185, 129, 0.12); color: #059669; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 13px;">BENCHMARK (3.2%)</span></td>
<td style="padding: 12px 14px; color: #94A3B8; font-size: 15px;">Anchored to 10-year goal; ignores day-to-day noise (Finding 2: Not Setting Financial Goals)</td>
</tr>
</tbody>
</table>
</div>""",
        unsafe_allow_html=True,
    )

    # Explicit Demographic & Segment Extraction Section (§9.4)
    st.markdown(
        """<div style="margin-top: 14px; margin-bottom: 10px;">
<div style="display: flex; align-items: center; justify-content: space-between;">
<div>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 700; color: #F1F5F9; margin: 0 0 4px 0;">Explicit Demographic & Segment Extraction (§9.4)</h3>
<div style="font-size: 15px; color: #94A3B8;">Zero-Inference Policy: Demographics are captured <strong>only when explicitly stated</strong> by the author.</div>
</div>
<span class="badge-tag badge-tier-1">Audited Zero-Inference</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # 4 Demographic Dimension Cards
    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        st.markdown(
            """<div class="executive-kpi-card" style="text-align: left; padding: 18px;">
<div style="font-size: 14px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">1. Income Stability</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 20px; font-weight: 800; color: #F1F5F9; margin: 4px 0 8px 0;">8.8% Stated</div>
<div style="font-size: 15px; color: #334155; line-height: 1.6;">
• Stable / Salaried: <strong>6.8%</strong><br/>
• Variable / Freelance: <strong>1.6%</strong><br/>
• Explicitly Unstable: <strong>0.4%</strong><br/>
• <span style="color: #94A3B8;">Unknown (Unstated): <strong>91.2%</strong></span>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    with d_col2:
        st.markdown(
            """<div class="executive-kpi-card" style="text-align: left; padding: 18px;">
<div style="font-size: 14px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">2. Source of Money</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 20px; font-weight: 800; color: #F1F5F9; margin: 4px 0 8px 0;">9.7% Stated</div>
<div style="font-size: 15px; color: #334155; line-height: 1.6;">
• Monthly Salary: <strong>7.2%</strong><br/>
• Business / Trade: <strong>1.1%</strong><br/>
• Family / Savings: <strong>1.4%</strong><br/>
• <span style="color: #94A3B8;">Unknown (Unstated): <strong>90.3%</strong></span>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    with d_col3:
        st.markdown(
            """<div class="executive-kpi-card" style="text-align: left; padding: 18px;">
<div style="font-size: 14px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">3. Catalyst / Influence</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 20px; font-weight: 800; color: #F1F5F9; margin: 4px 0 8px 0;">14.2% Stated</div>
<div style="font-size: 15px; color: #334155; line-height: 1.6;">
• YouTube / Finfluencer: <strong>7.8%</strong><br/>
• Colleague / Friend: <strong>4.1%</strong><br/>
• Self-Directed: <strong>2.3%</strong><br/>
• <span style="color: #94A3B8;">Unknown (Unstated): <strong>85.8%</strong></span>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    with d_col4:
        st.markdown(
            """<div class="executive-kpi-card" style="text-align: left; padding: 18px;">
<div style="font-size: 14px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">4. Stated Age Group</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 20px; font-weight: 800; color: #F1F5F9; margin: 4px 0 8px 0;">11.0% Stated</div>
<div style="font-size: 15px; color: #334155; line-height: 1.6;">
• Early Career (20–25): <strong>4.8%</strong><br/>
• Established (26–35): <strong>5.2%</strong><br/>
• Mature (36+): <strong>1.0%</strong><br/>
• <span style="color: #94A3B8;">Unknown (Unstated): <strong>89.0%</strong></span>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    # Epistemic Humility Callout Banner & Primary Research Conversion
    st.markdown(
        """<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #0284C7; border-radius: 10px; padding: 14px 18px; margin-top: 14px; margin-bottom: 16px;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="font-size: 13px; font-weight: 700; color: #0284C7; border: 1.5px solid #0284C7; border-radius: 4px; padding: 2px 6px; line-height: 1.2;">SAFEGUARD</div>
<div style="font-size: 15.5px; color: #334155; line-height: 1.6;">
<strong style="color: #0284C7;">Epistemic Safeguard (§9.4 & §16.7):</strong> Public discussion forums rarely disclose verified socio-economic metadata. Our engine strictly forbids inferring demographic markers from slang, writing tone, or app platforms. The ~90% unstated demographic gap is <strong>not a defect</strong>—it defines the exact <strong>targeted recruitment screeners</strong> for Part 2 primary user research.
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # Primary Research Participant Recruitment Criteria by Segment
    st.markdown(
        """<div style="margin-top: 14px; margin-bottom: 10px;">
<div style="display: flex; align-items: center; justify-content: space-between;">
<div>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 21px; font-weight: 700; color: #F1F5F9; margin: 0 0 4px 0;">Primary Research Recruitment Protocols by Segment</h3>
<div style="font-size: 15px; color: #94A3B8;">Translating the qualitative cohorts into exact 1:1 user interview screener quotas for Part 2 validation.</div>
</div>
<span class="badge-tag badge-tier-1">Research Field Guide</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown(
            """<div class="overview-section-card" style="margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<strong style="font-size: 16.5px; color: #7C3AED;">Screener Profile A: Volatility Shocked Novice</strong>
<span style="font-size: 13.5px; background: rgba(124, 58, 237, 0.1); color: #7C3AED; font-weight: 700; padding: 2px 8px; border-radius: 4px;">Quota: n = 6</span>
</div>
<div style="font-size: 15px; color: #94A3B8; line-height: 1.55;">
• <strong>Screening Rule:</strong> First mutual fund SIP started within the last 60–90 days; app opened &ge; 4 times/week; portfolio experienced -1% to -5% paper loss.<br/>
• <strong>Core Interview Probe:</strong> <em>"Walk me through what you felt the first time you opened the app and saw a red number. What did you think was happening to your money?"</em>
</div>
</div>

<div class="overview-section-card" style="margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<strong style="font-size: 16.5px; color: #EF4444;">Screener Profile B: Involuntary Mandate Drop-off</strong>
<span style="font-size: 13.5px; background: rgba(220, 38, 38, 0.1); color: #DC2626; font-weight: 700; padding: 2px 8px; border-radius: 4px;">Quota: n = 6</span>
</div>
<div style="font-size: 15px; color: #94A3B8; line-height: 1.55;">
• <strong>Screening Rule:</strong> Had at least 1 failed autopay debit in the last 90 days or experienced a bank ECS bounce charge; did not resume the SIP within 14 days.<br/>
• <strong>Core Interview Probe:</strong> <em>"When your instalment didn't debit, what message did you see? Did you contact support, attempt a manual payment, or just leave it?"</em>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    with r_col2:
        st.markdown(
            """<div class="overview-section-card" style="margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<strong style="font-size: 16.5px; color: #D97706;">Screener Profile C: Over-Diversified Burnout</strong>
<span style="font-size: 13.5px; background: rgba(217, 119, 6, 0.1); color: #D97706; font-weight: 700; padding: 2px 8px; border-radius: 4px;">Quota: n = 5</span>
</div>
<div style="font-size: 15px; color: #94A3B8; line-height: 1.55;">
• <strong>Screening Rule:</strong> Holding &ge; 5 active funds simultaneously with total monthly SIP &le; ₹10,000; at least 2 funds in identical market-cap categories.<br/>
• <strong>Core Interview Probe:</strong> <em>"How did you choose these specific funds? When was the last time you checked whether they hold the same underlying stocks?"</em>
</div>
</div>

<div class="overview-section-card" style="margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<strong style="font-size: 16.5px; color: #059669;">Screener Profile D: Disciplined Long-Term Continuer</strong>
<span style="font-size: 13.5px; background: rgba(16, 185, 129, 0.1); color: #059669; font-weight: 700; padding: 2px 8px; border-radius: 4px;">Quota: n = 5</span>
</div>
<div style="font-size: 15px; color: #94A3B8; line-height: 1.55;">
• <strong>Screening Rule:</strong> Completed 12+ consecutive monthly SIP instalments without a pause; stepped up contribution at least once in the trailing 12 months.<br/>
• <strong>Core Interview Probe:</strong> <em>"What keeps you continuing your SIP when markets crash 10%? What specific mental model or goal do you anchor your investments to?"</em>
</div>
</div>""",
            unsafe_allow_html=True,
        )


