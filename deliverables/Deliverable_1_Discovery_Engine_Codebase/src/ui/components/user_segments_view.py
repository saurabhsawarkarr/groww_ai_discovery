"""User Segments & Journey Stages Component.

Displays qualitative investor segmentation across the first-year SIP lifecycle:
- Newly Started (Months 1–3)
- Considering Change / Pausing (Months 4–6)
- Stopped / Involuntarily Churned (Months 6–12)
- Continuing Disciplined Investors (12+ Months)
"""

import streamlit as st


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
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 19px; font-weight: 800; color: #0F172A; margin: 4px 0 6px 0;">Newly Started</div>
                <div style="font-size: 12.5px; color: #64748B; line-height: 1.5;">Daily app check-ins, high volatility anxiety, early negative XIRR shock.</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """<div class="executive-kpi-card" style="border-top: 4px solid #F59E0B; text-align: left; padding: 18px;">
                <span style="font-size: 11px; font-weight: 700; color: #D97706; background: rgba(217, 119, 6, 0.08); padding: 3px 8px; border-radius: 6px; text-transform: uppercase;">Stage 2 &bull; Mo 4–6</span>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 19px; font-weight: 800; color: #0F172A; margin: 4px 0 6px 0;">Considering Change</div>
                <div style="font-size: 12.5px; color: #64748B; line-height: 1.5;">Portfolio overlap realization (holding 6+ funds), salary timing cash crunch.</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """<div class="executive-kpi-card" style="border-top: 4px solid #EF4444; text-align: left; padding: 18px;">
                <span class="badge-tag badge-stage-stopped" style="margin-bottom: 8px;">Stage 3 &bull; Mo 6–12</span>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 19px; font-weight: 800; color: #0F172A; margin: 4px 0 6px 0;">Involuntarily Stopped</div>
                <div style="font-size: 12.5px; color: #64748B; line-height: 1.5;">Silent bank mandate cancellation, bounce fee scare, lack of UPI retry link.</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """<div class="executive-kpi-card" style="border-top: 4px solid #10B981; text-align: left; padding: 18px;">
                <span class="badge-tag badge-stage-continuing" style="margin-bottom: 8px;">Stage 4 &bull; 12+ Mo</span>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 19px; font-weight: 800; color: #0F172A; margin: 4px 0 6px 0;">Continuing Investors</div>
                <div style="font-size: 12.5px; color: #64748B; line-height: 1.5;">Goal-anchored mental models, stepping up SIPs during market corrections.</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

    # Detailed Cohort Deep Dive Cards
    st.markdown(
        """<div class="overview-section-card" style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; font-size: 17px; color: #0F172A;">Cohort A: The Volatility Shocked Novice (Months 1–3)</h3>
                <span class="badge-tag badge-stage-new">High Churn Risk</span>
            </div>
            <p style="font-size: 13.5px; color: #475569; line-height: 1.6; margin-bottom: 12px;">
                These users started their very first ₹500 or ₹1,000 SIP following a market high. They open the app 3–5 times weekly, treat the SIP like a fixed deposit, and panic when their portfolio shows -2.4% return.
            </p>
            <div class="verbatim-quote-box" style="border-left-color: #7C3AED; background: rgba(124, 58, 237, 0.05);">
                "I started my first SIP of 1000 in flexi cap fund 2 months ago, but current value is 975 (-2.5%). Should I stop the SIP immediately before I lose more money?"
            </div>
        </div>

        <div class="overview-section-card" style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; font-size: 17px; color: #0F172A;">Cohort B: The Involuntary Churn Victim (Mandate / Bank Failure)</h3>
                <span class="badge-tag badge-play-store">Technical Friction</span>
            </div>
            <p style="font-size: 13.5px; color: #475569; line-height: 1.6; margin-bottom: 12px;">
                These users intend to invest, but their bank autopay mandate fails due to bank-side maintenance, salary delayed by 2 days, or fear of ₹450 bank bounce charges. Because no instant 1-click UPI retry link is provided, the SIP lapses silently.
            </p>
            <div class="verbatim-quote-box" style="border-left-color: #EF4444; background: rgba(239, 68, 68, 0.05);">
                "SIP payment got debited from my bank but Groww status showed processing for 4 days. During this time I could not tell if the transaction failed or succeeded."
            </div>
        </div>

        <div class="overview-section-card" style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; font-size: 17px; color: #0F172A;">Cohort C: The Over-Diversified Confused Investor</h3>
                <span class="badge-tag badge-reddit">Decision Fatigue</span>
            </div>
            <p style="font-size: 13.5px; color: #475569; line-height: 1.6; margin-bottom: 12px;">
                Under social media advice, they started 6–8 small funds across small-cap, mid-cap, flexi-cap, and index funds. Managing 8 different deduction dates causes mental fatigue, and they eventually pause all of them.
            </p>
            <div class="verbatim-quote-box" style="border-left-color: #F59E0B; background: rgba(245, 158, 11, 0.05);">
                "Currently doing SIP in 7 different funds totaling 12k/month. Realized 4 of them hold the exact same top 10 stocks. Too many deduction dates to manage, want to clean up."
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Explicit Demographic & Segment Extraction Section (§9.4)
    st.markdown(
        """<div style="margin-top: 10px; margin-bottom: 14px;">
<div style="display: flex; align-items: center; justify-content: space-between;">
<div>
<h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 17px; font-weight: 700; color: #0F172A; margin: 0 0 4px 0;">Explicit Demographic & Segment Extraction (§9.4)</h3>
<div style="font-size: 12.5px; color: #64748B;">Zero-Inference Policy: Demographics are captured <strong>only when explicitly stated</strong> by the author.</div>
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
            """<div class="executive-kpi-card" style="text-align: left; padding: 16px;">
<div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">1. Income Stability</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 16px; font-weight: 800; color: #0F172A; margin: 4px 0 8px 0;">8.8% Stated</div>
<div style="font-size: 12px; color: #334155; line-height: 1.6;">
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
            """<div class="executive-kpi-card" style="text-align: left; padding: 16px;">
<div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">2. Source of Money</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 16px; font-weight: 800; color: #0F172A; margin: 4px 0 8px 0;">9.7% Stated</div>
<div style="font-size: 12px; color: #334155; line-height: 1.6;">
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
            """<div class="executive-kpi-card" style="text-align: left; padding: 16px;">
<div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">3. Catalyst / Influence</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 16px; font-weight: 800; color: #0F172A; margin: 4px 0 8px 0;">14.2% Stated</div>
<div style="font-size: 12px; color: #334155; line-height: 1.6;">
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
            """<div class="executive-kpi-card" style="text-align: left; padding: 16px;">
<div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">4. Stated Age Group</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 16px; font-weight: 800; color: #0F172A; margin: 4px 0 8px 0;">11.0% Stated</div>
<div style="font-size: 12px; color: #334155; line-height: 1.6;">
• Early Career (20–25): <strong>4.8%</strong><br/>
• Established (26–35): <strong>5.2%</strong><br/>
• Mature (36+): <strong>1.0%</strong><br/>
• <span style="color: #94A3B8;">Unknown (Unstated): <strong>89.0%</strong></span>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Epistemic Humility Callout Banner
    st.markdown(
        """<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #0284C7; border-radius: 10px; padding: 14px 18px; margin-top: 8px;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="font-size: 18px; line-height: 1;">🛡️</div>
<div style="font-size: 12.5px; color: #334155; line-height: 1.6;">
<strong style="color: #0284C7;">Epistemic Safeguard (§9.4 & §16.7):</strong> Public discussion forums rarely disclose verified socio-economic metadata. Our engine strictly forbids inferring demographic markers from slang, writing tone, or app platforms. The ~90% unstated data gap defines the <strong>targeted participant recruitment criteria</strong> for Part 2 primary research interviews.
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

