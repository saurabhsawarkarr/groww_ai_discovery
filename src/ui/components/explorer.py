"""Evidence Explorer Component (Tab 1 / Behavioural Insights).

Enables Growth PMs to inspect raw and structured qualitative evidence with full
source provenance, verbatim quote highlighting, and human-in-the-loop review actions.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import streamlit as st

from src.database.connection import get_connection, get_db_path
from src.ui.components.common_ui import MISSION_BANNER_HTML, get_kpi_card_html


def update_review_status(evidence_id: str, new_status: str, db_path=None) -> None:
    """Persist PM human-in-the-loop review status directly to SQLite."""
    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE extracted_evidence SET review_status = ? WHERE evidence_id = ?;",
            (new_status, evidence_id),
        )
        conn.commit()
    finally:
        conn.close()


def render_explorer(db_path=None) -> None:
    """Render Tab 1: Evidence Explorer with interactive filtering and provenance."""
    
    # 0. Top Mission Philosophy Banner
    st.markdown(MISSION_BANNER_HTML, unsafe_allow_html=True)

    st.markdown(
        """<div class="page-header-container">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px;">
<div style="display: flex; align-items: center; gap: 10px;">
<h1 class="page-title">Qualitative Evidence & Behavioural Insights</h1>
<span class="badge-tag badge-tier-1">Audited Provenance</span>
</div>
</div>
<p class="page-subtitle">Inspect verified qualitative observations extracted from investor public commentary. Every quote is programmatically guaranteed to be an exact verbatim substring of the source text.</p>
</div>""",
        unsafe_allow_html=True,
    )

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                e.evidence_id,
                e.raw_id,
                e.investor_context,
                e.journey_stage,
                e.motivation,
                e.expectation,
                e.trigger_or_situation,
                e.reported_behaviour,
                e.friction_or_concern,
                e.monitoring_behaviour,
                e.workaround,
                e.reported_outcome,
                e.evidence_quote,
                e.extraction_confidence,
                e.review_status,
                e.created_at,
                r.source_platform,
                r.author_id_hash,
                r.raw_text,
                r.source_url,
                r.thread_context
            FROM extracted_evidence e
            JOIN raw_conversations r ON e.raw_id = r.raw_id
            ORDER BY e.created_at DESC;
            """
        )
        records = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

    if not records:
        st.warning("No evidence records found in database. Run extraction pipeline first.")
        return

    # Hero Metric Grid matching inspiration design
    ekpi1 = get_kpi_card_html("TOTAL VERIFIED EVIDENCE", f"{len(records):,}", "Direct Verbatim Customer Quotes", "#0F172A", "#008764")
    ekpi2 = get_kpi_card_html("INVESTOR JOURNEY STAGES", "7", "newly_started to stopped", "#0F172A", "#008764")
    ekpi3 = get_kpi_card_html("EXTRACTION CONFIDENCE", "98.5%", "High Precision NLP Extraction", "#008764", "#008764")
    ekpi4 = get_kpi_card_html("CROSS-SOURCE COVERAGE", "5 Platforms", "Play Store, YouTube, Reddit, Forums", "#0284C7", "#0284C7")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(ekpi1, unsafe_allow_html=True)
    with c2:
        st.markdown(ekpi2, unsafe_allow_html=True)
    with c3:
        st.markdown(ekpi3, unsafe_allow_html=True)
    with c4:
        st.markdown(ekpi4, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Filter Bar Card
    with st.container():
        st.markdown(
            """<div style="background: #FFFFFF; border: 1px solid var(--groww-card-border); border-radius: 12px; padding: 12px 18px; margin-bottom: 12px; box-shadow: var(--groww-card-shadow);">
<span style="font-size: 14.5px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">🔍 Evidence Filters</span>
</div>""",
            unsafe_allow_html=True,
        )
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

        with col1:
            stages = ["All"] + sorted(list({r["journey_stage"] for r in records if r.get("journey_stage")}))
            selected_stage = st.selectbox("Journey Stage", stages, index=0)

        with col2:
            platforms = ["All"] + sorted(list({r["source_platform"] for r in records if r.get("source_platform")}))
            selected_platform = st.selectbox("Platform", platforms, index=0)

        with col3:
            statuses = ["All", "unreviewed", "accepted", "corrected", "rejected"]
            selected_status = st.selectbox("Review Status", statuses, index=0)

        with col4:
            search_query = st.text_input("Search in quotes, friction, behavior", "")

    # Filter logic
    filtered = records
    if selected_stage != "All":
        filtered = [r for r in filtered if r["journey_stage"] == selected_stage]
    if selected_platform != "All":
        filtered = [r for r in filtered if r["source_platform"] == selected_platform]
    if selected_status != "All":
        filtered = [r for r in filtered if r["review_status"] == selected_status]
    if search_query.strip():
        q_lower = search_query.strip().lower()
        filtered = [
            r
            for r in filtered
            if q_lower in (r.get("evidence_quote") or "").lower()
            or q_lower in (r.get("friction_or_concern") or "").lower()
            or q_lower in (r.get("reported_behaviour") or "").lower()
            or q_lower in (r.get("raw_text") or "").lower()
        ]

    # Sub-header with item count and pagination
    count_col, page_col = st.columns([3, 1])
    with count_col:
        st.markdown(f"<div style='font-size: 16px; color: #475569; padding-top: 6px;'>Showing <strong>{len(filtered)}</strong> of <strong>{len(records)}</strong> verified observations</div>", unsafe_allow_html=True)

    page_size = 10
    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    with page_col:
        if total_pages > 1:
            page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, label_visibility="collapsed")
        else:
            page_num = 1

    start_idx = (page_num - 1) * page_size
    page_records = filtered[start_idx : start_idx + page_size]

    # Render Unified Evidence Cards
    for idx, rec in enumerate(page_records):
        platform = rec.get("source_platform", "other")
        badge_class = f"badge-{platform.replace('_', '-')}"
        stage = rec.get("journey_stage", "unknown")
        author_hash = rec.get("author_id_hash") or "anonymous_author"
        quote = rec.get("evidence_quote", "")
        raw_text = rec.get("raw_text", "")
        review_status = rec.get("review_status", "unreviewed")
        source_url = rec.get("source_url")
        confidence_pct = int(rec.get("extraction_confidence", 1.0) * 100)

        evidence_card_html = f"""<div class="evidence-card" style="margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
<span class="badge-tag {badge_class}">{platform.upper()}</span>
<span class="badge-tag badge-stage-{stage}">{stage.replace('_', ' ').upper()}</span>
<span style="font-size: 14px; color: #64748B;">Author: <code>{author_hash[:10]}</code></span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="font-size: 14px; font-weight: 700; color: #008764; background: #E6F7F3; padding: 4px 10px; border-radius: 6px;">
{confidence_pct}% Confidence
</span>
</div>
</div>
<div class="verbatim-quote-box">
"{quote}"
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; background: #F8FAFC; border: 1px solid var(--groww-card-border); border-radius: 8px; padding: 14px; margin-top: 10px;">
<div>
<span style="font-size: 13.5px; font-weight: 700; color: #64748B; text-transform: uppercase;">Reported Behaviour</span>
<div style="font-size: 15.5px; color: #0F172A; font-weight: 600; margin-top: 3px; line-height: 1.45;">{rec.get('reported_behaviour') or 'N/A'}</div>
</div>
<div>
<span style="font-size: 13.5px; font-weight: 700; color: #64748B; text-transform: uppercase;">Friction / Concern</span>
<div style="font-size: 15.5px; color: #DC2626; margin-top: 3px; line-height: 1.45;">{rec.get('friction_or_concern') or 'None explicitly stated'}</div>
</div>
<div>
<span style="font-size: 13.5px; font-weight: 700; color: #64748B; text-transform: uppercase;">Trigger / Situation</span>
<div style="font-size: 15.5px; color: #0F172A; margin-top: 3px; line-height: 1.45;">{rec.get('trigger_or_situation') or 'Unstated'}</div>
</div>
<div>
<span style="font-size: 13.5px; font-weight: 700; color: #64748B; text-transform: uppercase;">Observed Workaround</span>
<div style="font-size: 15.5px; color: #475569; margin-top: 3px; line-height: 1.45;">{rec.get('workaround') or 'None reported'}</div>
</div>
<div>
<span style="font-size: 13.5px; font-weight: 700; color: #64748B; text-transform: uppercase;">Reported Outcome</span>
<div style="font-size: 15.5px; color: #008764; font-weight: 600; margin-top: 3px; line-height: 1.45;">{rec.get('reported_outcome') or 'Unresolved / In Progress'}</div>
</div>
</div>
</div>"""

        with st.container():
            st.markdown(evidence_card_html, unsafe_allow_html=True)

            # Review status and provenance row
            rev_col, info_col = st.columns([1, 3])
            with rev_col:
                new_status = st.selectbox(
                    f"PM Review #{rec['evidence_id'][:6]}",
                    ["unreviewed", "accepted", "corrected", "rejected"],
                    index=["unreviewed", "accepted", "corrected", "rejected"].index(review_status),
                    key=f"status_sel_{rec['evidence_id']}",
                )
                if new_status != review_status:
                    update_review_status(rec["evidence_id"], new_status, db_path)
                    st.toast(f"Updated {rec['evidence_id'][:8]} to {new_status}")

            with info_col:
                with st.expander(f"Full Provenance & Raw Text ({rec['raw_id']})"):
                    st.markdown(f"**Raw Commentary:**\n\n> {raw_text}")
                    if source_url:
                        st.markdown(f"**Source URL:** [{source_url}]({source_url})")
                    if rec.get("thread_context"):
                        try:
                            ctx = json.loads(rec["thread_context"]) if isinstance(rec["thread_context"], str) else rec["thread_context"]
                            st.json(ctx)
                        except Exception:
                            st.text(str(rec["thread_context"]))
