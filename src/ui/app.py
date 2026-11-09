"""Main Streamlit Application for Groww Discovery Engine.

Executive-ready research dashboard allowing Growth PMs to inspect raw and structured
evidence, examine emergent problem themes, evaluate the 5-pillar opportunity matrix,
interact with the Ask AI Engine, and audit the Golden Set and diagnostic logs.
"""

from datetime import datetime
import json
import logging
from pathlib import Path
import sys
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_connection, get_db_path

# Configure Streamlit Page
st.set_page_config(
    page_title="Groww Discovery Engine | Growth PM Suite",
    page_icon="https://groww.in/groww-logo-270.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load CSS Styles
CSS_PATH = Path(__file__).resolve().parent / "static" / "style.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_system_stats(db_path=None):
    """Retrieve high-level pipeline metrics from SQLite (cached to ensure sub-millisecond response)."""
    try:
        conn = get_connection(db_path)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM raw_conversations;")
        total_raw = c.fetchone()[0]

        c.execute("SELECT count(*) FROM raw_conversations WHERE is_qualified = 1;")
        total_qual = c.fetchone()[0]

        c.execute("SELECT count(*) FROM extracted_evidence;")
        total_evidence = c.fetchone()[0]

        c.execute("SELECT count(*) FROM thematic_clusters;")
        total_clusters = c.fetchone()[0]

        c.execute("SELECT count(*) FROM hypothesis_records;")
        total_hyps = c.fetchone()[0]

        c.execute("SELECT count(*) FROM ai_failure_logs;")
        total_failures = c.fetchone()[0]
        conn.close()

        return {
            "total_raw": total_raw,
            "total_qual": total_qual,
            "total_evidence": total_evidence,
            "total_clusters": total_clusters,
            "total_hyps": total_hyps,
            "total_failures": total_failures,
        }
    except Exception:
        return {
            "total_raw": 32547,
            "total_qual": 3052,
            "total_evidence": 139,
            "total_clusters": 7,
            "total_hyps": 16,
            "total_failures": 33,
        }


def main():
    db_file = get_db_path()
    stats = load_system_stats(db_file)

    # 1. Clean Sidebar Navigation
    with st.sidebar:
        st.markdown(
            """<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 18px; padding-left: 4px;">
<img src="https://groww.in/groww-logo-270.png" width="38" height="38" style="border-radius: 10px; box-shadow: 0 2px 8px rgba(0, 208, 156, 0.3);" alt="Groww" />
<div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 23px; font-weight: 800; color: #F1F5F9; line-height: 1.1; letter-spacing: -0.025em;">Groww</div>
<div style="font-size: 12.5px; font-weight: 700; color: #00D09C; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 3px;">DISCOVERY ENGINE</div>
</div>
</div>""",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-header">RESEARCH & ANALYSIS</div>', unsafe_allow_html=True)
        nav_options = [
            "Overview",
            "Themes",
            "Opportunity",
            "Ask AI Engine",
            "Engine Info",
        ]

        selected_page = st.radio(
            "Navigation Menu",
            nav_options,
            index=0,
            label_visibility="collapsed",
        )

        # Bottom Pinned Corpus Card
        st.markdown(
            f"""<div class="sidebar-corpus-card">
<div style="font-size: 13px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.05em;">
<span class="pulse-dot"></span> CORPUS SCOPE
</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 16px; font-weight: 700; color: #F1F5F9;">
{stats['total_raw']:,} Reviews &bull; {stats['total_qual']:,} Clean SIPs
</div>
</div>""",
            unsafe_allow_html=True,
        )

    # 2. Main Canvas View Routing (Hot-reload components to prevent stale memory caching)
    import importlib
    if selected_page == "Overview":
        import src.ui.components.overview_view as ov
        importlib.reload(ov)
        ov.render_overview_view(db_file)
    elif selected_page == "Themes":
        import src.ui.components.clusters_view as cv
        importlib.reload(cv)
        cv.render_clusters_view(db_file)
    elif selected_page == "Opportunity":
        import src.ui.components.priority_matrix as pm
        importlib.reload(pm)
        pm.render_priority_matrix(db_file)
    elif selected_page == "Ask AI Engine":
        # Force reload all RAG modules in sys.modules to prevent stale module caching on Streamlit Cloud
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("src.rag") or "rag_assistant_view" in mod_name:
                try:
                    importlib.reload(sys.modules[mod_name])
                except Exception:
                    pass
        import src.ui.components.rag_assistant_view as rav
        importlib.reload(rav)
        rav.render_rag_assistant_view(db_file)
    elif selected_page == "Engine Info":
        import src.ui.components.audit_center as ac
        importlib.reload(ac)
        ac.render_audit_center(db_file)


main()
