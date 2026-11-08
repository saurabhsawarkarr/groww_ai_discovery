"""Thematic Clusters & Pattern Discovery Component (Tab 2).

Displays unsupervised emergent behavioral clusters, prevalence statistics,
actionable product solutions, and verified verbatim customer evidence in a clean responsive grid.
Designed following strict Dark Theme standards with Groww typography and zero visual noise.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import streamlit as st

from src.database.connection import get_connection
from src.ui.components.common_ui import MISSION_BANNER_HTML, get_kpi_card_html


THEME_METADATA_MAP: Dict[str, Dict[str, Any]] = {
    "THEME-01": {
        "root_trigger": "Salary delay of 2–3 days leaves bank account empty on auto-debit day, causing silent mandate cancellation with zero fallback recovery link.",
        "critical_window": "Month 3–6 • Early Mandate Phase",
        "product_levers": [
            "1-Click Fallback UPI Retry",
            "WhatsApp T-24h Pre-Debit Ping",
            "5-Day Smart Salary Flex Buffer",
        ],
    },
    "THEME-02": {
        "root_trigger": "Chasing trending YouTube fund picks leads to 6+ overlapping funds with >70% stock redundancy, causing decision fatigue and premature liquidation.",
        "critical_window": "Month 4–8 • Portfolio Clutter Phase",
        "product_levers": [
            "1-Click Portfolio Overlap Cleaner",
            "3-Fund Core Foundation Bundle",
            "Duplicate Category Warning Modal",
        ],
    },
    "THEME-03": {
        "root_trigger": "Retail bank ₹450–₹590 auto-debit bounce penalty scares first-time investors into permanently cancelling their mandate to avoid recurring bank charges.",
        "critical_window": "Month 2–5 • Early Cash Crunch",
        "product_levers": [
            "Pre-Flight Bank Balance Verification",
            "1-Click 7-Day Auto-Pause / Skip",
            "Emergency Cash Buffer Setup Flow",
        ],
    },
    "THEME-04": {
        "root_trigger": "Normal 2–5% short-term market corrections trigger loss aversion and red-portfolio shock, prompting panic cancellations at the bottom of the cycle.",
        "critical_window": "Month 1–3 • First Correction Shock",
        "product_levers": [
            "Accumulation Lens (Unit Growth View)",
            "Volatility Reassurance Crash Context",
            "5-Year Market Cycle Time Machine",
        ],
    },
    "THEME-05": {
        "root_trigger": "Anchored to 15–20% bull-run marketing calculators, users interpret normal Year 1 flat/low XIRR as fund failure and prematurely stop disciplined investing.",
        "critical_window": "Month 6–12 • Horizon Mismatch",
        "product_levers": [
            "Hide <1Y Annualized XIRR by Default",
            "Absolute Rupee Wealth Accumulated",
            "Visual Compounding Horizon Simulator",
        ],
    },
    "THEME-06": {
        "root_trigger": "2-to-3 business day lag between bank debit and mutual fund unit allotment causes anxiety that money is lost or debited at unfavorable NAV rates.",
        "critical_window": "Month 1–4 • Settlement Anxiety",
        "product_levers": [
            "Real-Time In-App Settlement Tracker",
            "NAV Cutoff Lock-In Guarantee Badge",
            "Automated Unit Allotment Push Ping",
        ],
    },
    "THEME-07": {
        "root_trigger": "Investing without a concrete life milestone makes SIP deductions feel like discretionary monthly costs rather than disciplined wealth building.",
        "critical_window": "Month 6–12 • Habit Erosion",
        "product_levers": [
            "Mandatory Goal-Anchored SIP Setup",
            "Milestone Progress Bar (e.g. 15% to Car)",
            "Milestone Horizon Shield Visualizer",
        ],
    },
}


def render_clusters_view(db_path=None) -> None:
    """Render Tab 2: Emergent Thematic Clusters in Modern Card Grid Layout."""

    st.markdown(
        """<div class="page-header-container" style="margin-bottom: 20px;">
<div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 8px; flex-wrap: wrap;">
<div style="display: flex; align-items: center; gap: 12px;">
<h1 class="page-title" style="margin: 0;">Themes</h1>
<span class="badge-tag badge-tier-1" style="font-size: 13px; padding: 4px 10px;">7 Discovered Themes</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="background: rgba(0, 208, 156, 0.12); color: #00D09C; font-size: 13px; font-weight: 700; padding: 5px 12px; border-radius: 6px; border: 1px solid rgba(0, 208, 156, 0.3);">
1,667 Mapped Failure Accounts
</span>
<span style="background: #1E2533; color: #94A3B8; font-size: 13px; font-weight: 600; padding: 5px 12px; border-radius: 6px; border: 1px solid #2B3548;">
5 Channels &bull; 3,052 Clean Corpus
</span>
</div>
</div>
<p class="page-subtitle" style="font-size: 15.5px; color: #94A3B8; line-height: 1.6;">
Empirical behavioral failure clusters discovered across <strong style="color: #F1F5F9;">3,052 qualified first-time investor conversations</strong>. Each theme quantifies user drop-off volume, pinpoints psychological and technical friction points, outlines concrete product interventions, and connects directly to customer evidence.
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
    k1 = get_kpi_card_html("DISCOVERED FAILURE THEMES", f"{len(themes_data)} Core Themes", "Prevalence 3.2% – 18.0%", "#F1F5F9", "#00D09C")
    k2 = get_kpi_card_html("MAPPED FAILURE VOLUME", f"{total_matched:,} Accounts", f"{coverage_pct}% of Qualified Corpus", "#00D09C", "#00D09C")
    k3 = get_kpi_card_html("ANALYZED SIP CORPUS", f"{total_corpus_count:,} Conversations", "100% Qualified Clean Records", "#F1F5F9", "#00D09C")
    k4 = get_kpi_card_html("MULTI-CHANNEL DATA", "5 Platforms", "Play Store, App Store, Reddit, YT, Forum", "#38BDF8", "#38BDF8")

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
        item_count = t.get("prevalence_count", 0)
        prevalence_pct = t.get("prevalence_percentage", 0.0)
        quotes = t.get("representative_quotes", [])
        platform_breakdown = t.get("platform_breakdown", {})

        meta = THEME_METADATA_MAP.get(cid, {
            "root_trigger": t.get("core_problem", ""),
            "critical_window": "First-Year Journey",
            "product_levers": [
                "Product Intervention"
            ],
        })

        # Product lever pills in clean unified Groww mint tint
        levers_html_list = []
        for item in meta.get("product_levers", []):
            label = item[0] if isinstance(item, (list, tuple)) else str(item)
            levers_html_list.append(
                f'<span style="font-family: \'Inter\', sans-serif; font-size: 11.5px; font-weight: 600; color: #00D09C; background: rgba(0, 208, 156, 0.12); border: 1px solid rgba(0, 208, 156, 0.28); padding: 4px 8px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;">{label}</span>'
            )
        product_levers_html = "".join(levers_html_list)

        # Quotes Drawer Content (Revealed on View Evidence)
        quotes_drawer_content = ""
        if quotes:
            quote_cards = []
            for q in quotes:
                q_text = q.get("quote", "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
                q_platform = format_platform_name(q.get("platform", ""))
                q_url = q.get("source_url", "")
                q_link = (
                    f'<a href="{q_url}" target="_blank" style="color: #38BDF8; font-weight: 600; text-decoration: underline; font-size: 12px; display: inline-flex; align-items: center; gap: 3px;">Original Source Link ↗</a>'
                    if q_url else ""
                )

                quote_cards.append(
                    f'<div style="background: #1A2230; border: 1px solid #2B3548; border-left: 3.5px solid #00D09C; border-radius: 7px; padding: 11px 13px; margin-bottom: 8px;">'
                    f'<div style="font-family: \'Inter\', sans-serif; font-size: 13px; color: #F1F5F9; line-height: 1.5; font-style: italic; margin-bottom: 6px;">"{q_text}"</div>'
                    f'<div style="display: flex; align-items: center; justify-content: space-between; font-size: 11.5px; margin-top: 4px;">'
                    f'<span style="background: #242D3D; color: #94A3B8; padding: 2px 7px; border-radius: 4px; font-weight: 600;">{q_platform}</span>'
                    f'{q_link}'
                    f'</div>'
                    f'</div>'
                )
            quotes_drawer_content = "".join(quote_cards)
        else:
            quotes_drawer_content = '<div style="font-size: 12.5px; color: #94A3B8; font-style: italic;">No verbatim sample attached.</div>'

        evidence_count = len(quotes)

        footer_html = (
            f'<div style="border-top: 1px solid #222938; padding-top: 12px; margin-top: auto;">'
            f'<details class="evidence-details">'
            f'<summary style="display: flex; align-items: center; justify-content: space-between; cursor: pointer; list-style: none; user-select: none;">'
            f'<span class="evidence-link">View Evidence ({evidence_count}) &rarr;</span>'
            f'</summary>'
            f'<div style="background: #151A24; border: 1px solid #2B3548; border-radius: 8px; padding: 12px 14px; margin-top: 12px; animation: fadeIn 0.2s ease;">'
            f'<div class="quotes-scroll-container" style="max-height: 340px; overflow-y: auto; padding-right: 6px;">{quotes_drawer_content}</div>'
            f'</div>'
            f'</details>'
            f'</div>'
        )

        card_html = (
            f'<div style="background: #151A24; border: 1.5px solid #222938; border-top: 4px solid #00D09C; border-radius: 12px; padding: 20px 22px; box-shadow: 0 4px 14px rgba(0,0,0,0.3); display: flex; flex-direction: column; justify-content: space-between; min-height: 340px; transition: transform 0.15s ease, box-shadow 0.15s ease;">'
            f'<div>'
            f'<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">'
            f'<span class="badge-tag badge-tier-1">{cid}</span>'
            f'<div style="font-size: 13.5px; font-weight: 700; color: #00D09C; display: flex; align-items: center; gap: 4px;">'
            f'<span>{item_count:,} People</span>'
            f'<span style="color: #94A3B8; font-weight: 500; font-size: 12.5px;">({prevalence_pct}%)</span>'
            f'</div>'
            f'</div>'
            f'<h3 style="font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 18px; font-weight: 800; color: #F1F5F9; margin: 0 0 12px 0; line-height: 1.35;">{title}</h3>'
            f'<div style="background: #1A2230; border: 1px solid #2B3548; border-left: 3.5px solid #00D09C; border-radius: 0 8px 8px 0; padding: 9px 12px; margin-bottom: 11px;">'
            f'<div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 3px;">Root Friction Trigger</div>'
            f'<div style="font-family: \'Inter\', sans-serif; font-size: 13px; color: #F1F5F9; line-height: 1.45;">{meta["root_trigger"]}</div>'
            f'</div>'
            f'<div style="display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: #94A3B8; margin-bottom: 12px;">'
            f'<span style="font-weight: 700; color: #F1F5F9;">Critical Window:</span>'
            f'<span style="background: #1E2533; color: #CBD5E1; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; border: 1px solid #2B3548;">{meta["critical_window"]}</span>'
            f'</div>'
            f'<div style="margin-bottom: 8px;">'
            f'<div style="font-size: 11px; font-weight: 700; color: #00D09C; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; display: flex; align-items: center; gap: 4px;">'
            f'High-Leverage Product Levers'
            f'</div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 6px;">'
            f'{product_levers_html}'
            f'</div>'
            f'</div>'
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
    color: #38BDF8;
    font-weight: 600;
    font-size: 13.5px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: color 0.15s ease;
}
.evidence-link:hover {
    color: #0284C7;
    text-decoration: underline;
}
.quotes-scroll-container::-webkit-scrollbar {
    width: 5px;
}
.quotes-scroll-container::-webkit-scrollbar-track {
    background: #1E2533;
    border-radius: 4px;
}
.quotes-scroll-container::-webkit-scrollbar-thumb {
    background: #333F54;
    border-radius: 4px;
}
.quotes-scroll-container::-webkit-scrollbar-thumb:hover {
    background: #00D09C;
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
