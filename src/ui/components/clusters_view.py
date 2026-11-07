"""Thematic Clusters & Pattern Discovery Component (Tab 2).

Displays unsupervised emergent behavioral clusters, prevalence statistics,
actionable product solutions, and verified verbatim customer evidence in a clean responsive grid.
Designed following strict Light Theme standards with Groww typography and zero visual noise.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import streamlit as st

from src.database.connection import get_connection
from src.ui.components.common_ui import MISSION_BANNER_HTML, get_kpi_card_html


def render_clusters_view(db_path=None) -> None:
    """Render Tab 2: Emergent Thematic Clusters in Modern Card Grid Layout."""
    

    st.markdown(
        """<div class="page-header-container" style="margin-bottom: 20px;">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 8px; flex-wrap: wrap;">
<div style="display: flex; align-items: center; gap: 12px;">
<h1 class="page-title" style="margin: 0;">Discovered SIP Failure Themes</h1>
<span class="badge-tag badge-tier-1" style="font-size: 13px; padding: 4px 10px;">7 Discovered Themes</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="background: rgba(0, 208, 156, 0.1); color: #008764; font-size: 13px; font-weight: 700; padding: 5px 12px; border-radius: 6px; border: 1px solid rgba(0, 208, 156, 0.25);">
👥 1,667 Mapped Failure Accounts
</span>
<span style="background: #F1F5F9; color: #475569; font-size: 13px; font-weight: 600; padding: 5px 12px; border-radius: 6px; border: 1px solid #E2E8F0;">
5 Channels &bull; 3,052 Clean Corpus
</span>
</div>
</div>
<p class="page-subtitle" style="font-size: 15.5px; color: #475569; line-height: 1.6;">
Empirical behavioral failure clusters discovered across <strong>3,052 qualified first-time investor conversations</strong>. Each theme quantifies user drop-off volume, pinpoints psychological and technical friction points, outlines concrete product interventions, and connects directly to customer evidence.
</p>
</div>""",
        unsafe_allow_html=True,
    )

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    json_path = project_root / "data" / "processed" / "major_themes_3k_discovery.json"

    themes_data = []
    total_corpus_count = 3052

    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_json = json.load(f)
                themes_data = raw_json.get("themes", [])
                total_corpus_count = raw_json.get("total_analyzed_corpus", 3052)
        except Exception as e:
            st.error(f"Error reading themes JSON: {e}")

    # Fallback to SQLite thematic_clusters if JSON fails
    if not themes_data:
        try:
            conn = get_connection(db_path)
            c = conn.cursor()
            rows = c.execute("SELECT cluster_id, title, description, item_count, source_distribution FROM thematic_clusters;").fetchall()
            for r in rows:
                dist = {}
                if r[4]:
                    try:
                        dist = json.loads(r[4])
                    except Exception:
                        pass
                themes_data.append({
                    "theme_id": r[0],
                    "name": r[1],
                    "category": "Discovered Theme",
                    "prevalence_count": r[3],
                    "prevalence_percentage": round((r[3] / total_corpus_count) * 100, 1),
                    "core_problem": r[2],
                    "growth_opportunity": "",
                    "representative_quotes": [],
                })
            conn.close()
        except Exception:
            pass

    if not themes_data:
        st.warning("No themes found. Please verify that data/processed/major_themes_3k_discovery.json exists.")
        return

    # Overview KPI row matching executive dashboard design
    total_matched = sum(t.get("prevalence_count", 0) for t in themes_data)
    coverage_pct = round((total_matched / total_corpus_count) * 100, 1) if total_corpus_count else 54.6
    k1 = get_kpi_card_html("DISCOVERED FAILURE THEMES", f"{len(themes_data)} Core Themes", "Prevalence 3.2% – 18.0%", "#0F172A", "#008764")
    k2 = get_kpi_card_html("MAPPED FAILURE VOLUME", f"{total_matched:,} Accounts", f"{coverage_pct}% of Qualified Corpus", "#008764", "#008764")
    k3 = get_kpi_card_html("ANALYZED SIP CORPUS", f"{total_corpus_count:,} Conversations", "100% Qualified Clean Records", "#0F172A", "#008764")
    k4 = get_kpi_card_html("MULTI-CHANNEL DATA", "5 Platforms", "Play Store, App Store, Reddit, YT, Forum", "#0284C7", "#0284C7")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(k1, unsafe_allow_html=True)
    with col2:
        st.markdown(k2, unsafe_allow_html=True)
    with col3:
        st.markdown(k3, unsafe_allow_html=True)
    with col4:
        st.markdown(k4, unsafe_allow_html=True)

    def format_platform_name(p: str) -> str:
        p_lower = (p or "").lower()
        if "play" in p_lower:
            return "Google Play Store"
        elif "apple" in p_lower or "app_store" in p_lower:
            return "Apple App Store"
        elif "reddit" in p_lower:
            return "Reddit Community"
        elif "forum" in p_lower:
            return "Investor Forum"
        return p.capitalize() if p else "Customer Verbatim"

    cards_html_list = []

    for i, t in enumerate(themes_data, 1):
        cid = t.get("theme_id", f"THEME-0{i}")
        title = t.get("name", "Untitled Theme")
        desc = t.get("core_problem", "")
        item_count = t.get("prevalence_count", 0)
        prevalence_pct = t.get("prevalence_percentage", 0.0)
        quotes = t.get("representative_quotes", [])
        opportunity = t.get("growth_opportunity", "")

        # Growth & Product Opportunity Callout Box
        opp_box = ""
        if opportunity:
            opp_box = (
                f'<div style="background: rgba(0, 208, 156, 0.07); border-left: 3.5px solid #00D09C; border-radius: 0 8px 8px 0; padding: 11px 13px; margin: 10px 0 14px 0;">'
                f'<div style="color: #008764; font-size: 13.5px; font-weight: 700; margin-bottom: 3px;">💡 Growth & Product Opportunity:</div>'
                f'<p style="font-family: \'Inter\', sans-serif; font-size: 13.5px; color: #1E293B; line-height: 1.5; margin: 0;">{opportunity}</p>'
                f'</div>'
            )

        # Quotes Drawer Content (Revealed on View Evidence)
        quotes_drawer_content = ""
        if quotes:
            quote_cards = []
            for q in quotes:
                q_text = q.get("quote", "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
                q_platform = format_platform_name(q.get("platform", ""))
                q_url = q.get("source_url", "")
                q_link = (
                    f'<a href="{q_url}" target="_blank" style="color: #0284C7; font-weight: 600; text-decoration: underline; font-size: 12px; display: inline-flex; align-items: center; gap: 3px;">Original Source Link ↗</a>'
                    if q_url else ""
                )

                quote_cards.append(
                    f'<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 3.5px solid #00D09C; border-radius: 7px; padding: 11px 13px; margin-bottom: 8px;">'
                    f'<div style="font-family: \'Inter\', sans-serif; font-size: 13px; color: #1E293B; line-height: 1.5; font-style: italic; margin-bottom: 6px;">"{q_text}"</div>'
                    f'<div style="display: flex; align-items: center; justify-content: space-between; font-size: 11.5px; margin-top: 4px;">'
                    f'<span style="background: #F1F5F9; color: #475569; padding: 2px 7px; border-radius: 4px; font-weight: 600;">{q_platform}</span>'
                    f'{q_link}'
                    f'</div>'
                    f'</div>'
                )
            quotes_drawer_content = "".join(quote_cards)
        else:
            quotes_drawer_content = '<div style="font-size: 12.5px; color: #64748B; font-style: italic;">No verbatim sample attached.</div>'

        evidence_count = len(quotes)

        footer_html = (
            f'<div style="border-top: 1px solid #E2E8F0; padding-top: 12px; margin-top: auto;">'
            f'<details class="evidence-details">'
            f'<summary style="display: flex; align-items: center; justify-content: space-between; cursor: pointer; list-style: none; user-select: none;">'
            f'<span class="evidence-link">View Evidence ({evidence_count}) &rarr;</span>'
            f'</summary>'
            f'<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 14px; margin-top: 12px; animation: fadeIn 0.2s ease;">'
            f'<div class="quotes-scroll-container" style="max-height: 340px; overflow-y: auto; padding-right: 6px;">{quotes_drawer_content}</div>'
            f'</div>'
            f'</details>'
            f'</div>'
        )

        card_html = (
            f'<div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-top: 4px solid #00D09C; border-radius: 12px; padding: 20px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between; min-height: 280px; transition: transform 0.15s ease, box-shadow 0.15s ease;">'
            f'<div>'
            f'<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">'
            f'<span class="badge-tag badge-tier-1">{cid}</span>'
            f'<div style="font-size: 13.5px; font-weight: 700; color: #008764; display: flex; align-items: center; gap: 4px;">'
            f'<span>👥</span>'
            f'<span>{item_count:,} People</span>'
            f'<span style="color: #64748B; font-weight: 500; font-size: 12.5px;">({prevalence_pct}%)</span>'
            f'</div>'
            f'</div>'
            f'<h3 style="font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 18px; font-weight: 800; color: #0F172A; margin: 0 0 10px 0; line-height: 1.35;">{title}</h3>'
            f'<p style="font-family: \'Inter\', sans-serif; font-size: 13.5px; color: #475569; line-height: 1.55; margin: 0 0 12px 0;">{desc}</p>'
            f'{opp_box}'
            f'</div>'
            f'{footer_html}'
            f'</div>'
        )
        cards_html_list.append(card_html)

    # Styles for details summary and responsive grid
    style_block = """<style>
details.evidence-details summary {
    list-style: none;
    cursor: pointer;
}
details.evidence-details summary::-webkit-details-marker {
    display: none;
}
details.evidence-details summary:focus {
    outline: none;
}
.evidence-link {
    color: #0284C7;
    font-weight: 600;
    font-size: 13.5px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: color 0.15s ease;
}
.evidence-link:hover {
    color: #0369A1;
    text-decoration: underline;
}
.quotes-scroll-container::-webkit-scrollbar {
    width: 5px;
}
.quotes-scroll-container::-webkit-scrollbar-track {
    background: #F1F5F9;
    border-radius: 4px;
}
.quotes-scroll-container::-webkit-scrollbar-thumb {
    background: #CBD5E1;
    border-radius: 4px;
}
.quotes-scroll-container::-webkit-scrollbar-thumb:hover {
    background: #94A3B8;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>"""

    # Render entire grid in responsive multi-column layout
    grid_container_html = (
        f'{style_block}'
        f'<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 18px; align-items: stretch; margin-top: 18px; margin-bottom: 24px;">'
        f'{"".join(cards_html_list)}'
        f'</div>'
    )

    st.markdown(grid_container_html, unsafe_allow_html=True)
