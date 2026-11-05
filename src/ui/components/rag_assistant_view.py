"""Interactive Qualitative RAG Assistant Component.

Enables Growth PMs to converse with the cleaned 3,052 customer conversation corpus,
retrieve hybrid BM25 + Vector evidence, and generate high-impact PM product strategies.
Architected with a pluggable adapter for user-provided separate LLMs (Gemini, OpenAI, Claude, Groq, Ollama).
"""

import os
from pathlib import Path
import streamlit as st

from src.rag.retriever import HybridEvidenceRetriever
from src.rag.llm_adapter import LLMAdapter
from src.rag.pipeline import RAGPipeline
from src.ui.components.common_ui import MISSION_BANNER_HTML, get_kpi_card_html


@st.cache_resource(show_spinner="Initializing Qualitative Evidence Index...")
def get_shared_pipeline() -> RAGPipeline:
    """Initialize and cache the hybrid BM25 + Vector retriever pipeline."""
    retriever = HybridEvidenceRetriever()
    return RAGPipeline(retriever=retriever)


def render_rag_assistant_view(db_path=None) -> None:
    """Render the complete interactive RAG Assistant view with separate LLM adapter."""
    
    # 0. Top Mission Philosophy Banner
    st.markdown(MISSION_BANNER_HTML, unsafe_allow_html=True)

    # Initialize session state for RAG configuration and chat
    if "rag_provider" not in st.session_state:
        st.session_state["rag_provider"] = os.getenv("RAG_LLM_PROVIDER") or "Google Gemini (Gemini 3.5 Flash)"
    if "rag_api_key" not in st.session_state:
        st.session_state["rag_api_key"] = os.getenv("RAG_LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    if "rag_model" not in st.session_state:
        st.session_state["rag_model"] = os.getenv("RAG_LLM_MODEL") or "gemini-3.5-flash"
    if "rag_base_url" not in st.session_state:
        st.session_state["rag_base_url"] = ""
    if "rag_top_k" not in st.session_state:
        st.session_state["rag_top_k"] = 5
    if "rag_temperature" not in st.session_state:
        st.session_state["rag_temperature"] = 0.2
    if "rag_history" not in st.session_state:
        st.session_state["rag_history"] = []
    if "rag_query_input" not in st.session_state:
        st.session_state["rag_query_input"] = ""

    active_provider_display = (
        st.session_state["rag_provider"].split(" (")[0]
        if "(" in st.session_state["rag_provider"]
        else st.session_state["rag_provider"]
    )
    active_model_display = st.session_state.get("rag_model", "gemini-3.5-flash")

    # 1. Sleek Sticky Header matching reference style
    st.markdown(
        f"""<div class="rag-sticky-header">
<div class="rag-header-left">
<div class="rag-header-icon">🔬</div>
<div>
<div class="rag-header-title">AI Qualitative Discovery Engine</div>
<div class="rag-header-subtitle">Groww Mutual Funds &bull; Conversing across 3,052 verified customer conversations</div>
</div>
</div>
<div class="rag-header-badge">
<span class="rag-pulse-dot"></span>
<span>{active_model_display} Active &bull; 7 Discovered Themes &bull; 3,052 Clean SIPs</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # 2. Executive 4-Card Hero Metric Grid matching inspiration design
    rkpi1 = get_kpi_card_html("INDEXED CORPUS", "3,052", "100% Traceable Clean SIPs", "#0F172A", "#008764")
    rkpi2 = get_kpi_card_html("RETRIEVAL ARCHITECTURE", "Hybrid RRF", "BM25 Lexical + Cosine Vectors", "#0F172A", "#008764")
    rkpi3 = get_kpi_card_html("SAFETY GUARDRAILS", "100%", "Strict SEBI Non-Advice Invariant", "#008764", "#008764")
    rkpi4 = get_kpi_card_html("ACTIVE LLM ENGINE", active_provider_display, f"Model: {active_model_display}", "#0284C7", "#0284C7")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(rkpi1, unsafe_allow_html=True)
    with c2:
        st.markdown(rkpi2, unsafe_allow_html=True)
    with c3:
        st.markdown(rkpi3, unsafe_allow_html=True)
    with c4:
        st.markdown(rkpi4, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # 3. Dedicated Separate LLM Configuration Panel (collapsible)
    with st.expander("⚙️ **LLM Model & Endpoint Settings (Plug-and-Play)**", expanded=False):
        st.markdown(
            """<p style="font-size: 14.5px; color: #475569; margin-bottom: 12px;">
            Configure your active LLM provider below. The Qualitative RAG pipeline routes prompt contexts and retrieved customer evidence chunks to your specified model.
            </p>""",
            unsafe_allow_html=True,
        )

        cfg_col1, cfg_col2 = st.columns(2)
        with cfg_col1:
            selected_provider = st.selectbox(
                "LLM Provider / Backend",
                LLMAdapter.PROVIDERS,
                index=LLMAdapter.PROVIDERS.index(st.session_state["rag_provider"])
                if st.session_state["rag_provider"] in LLMAdapter.PROVIDERS
                else 0,
                key="cfg_provider_select",
            )
            st.session_state["rag_provider"] = selected_provider

            # Dynamic model suggestions
            default_model = "gemini-3.5-flash"
            if "Gemini" in selected_provider:
                default_model = "gemini-3.5-flash"
            elif "OpenAI" in selected_provider:
                default_model = "gpt-4o"
            elif "Anthropic" in selected_provider:
                default_model = "claude-3-5-sonnet-20241022"
            elif "Groq" in selected_provider:
                default_model = "llama-3.3-70b-versatile"
            elif "Ollama" in selected_provider:
                default_model = "llama3"

            model_val = st.text_input(
                "Model Identifier",
                value=st.session_state.get("rag_model") or default_model,
                help="Model name (e.g. gemini-3.5-flash, gpt-4o, claude-3-5-sonnet, llama-3.3-70b-versatile)",
                key="cfg_model_input",
            )
            st.session_state["rag_model"] = model_val

        with cfg_col2:
            key_val = st.text_input(
                "API Key (Leave blank for Deterministic Engine or Local Ollama)",
                value=st.session_state.get("rag_api_key", ""),
                type="password",
                help="API key for your chosen provider. Kept strictly in local memory session.",
                key="cfg_api_key_input",
            )
            st.session_state["rag_api_key"] = key_val

            base_url_val = st.text_input(
                "Base URL / Custom Endpoint (Optional)",
                value=st.session_state.get("rag_base_url", ""),
                placeholder="e.g. http://localhost:11434 or https://your-proxy.com/v1",
                help="Specify custom host URL for Ollama, vLLM, or corporate proxies.",
                key="cfg_base_url_input",
            )
            st.session_state["rag_base_url"] = base_url_val

        col_param1, col_param2, col_btn = st.columns([1.5, 1.5, 1.2])
        with col_param1:
            st.session_state["rag_top_k"] = st.slider(
                "Evidence Chunks (Top-K)", min_value=3, max_value=10, value=st.session_state["rag_top_k"]
            )
        with col_param2:
            st.session_state["rag_temperature"] = st.slider(
                "Generation Temperature", min_value=0.0, max_value=1.0, value=st.session_state["rag_temperature"], step=0.05
            )
        with col_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔌 Test Connection", use_container_width=True):
                with st.spinner("Testing connection to separate LLM..."):
                    ok, msg = LLMAdapter.test_connection(
                        provider=st.session_state["rag_provider"],
                        api_key=st.session_state["rag_api_key"],
                        model=st.session_state["rag_model"],
                        base_url=st.session_state["rag_base_url"],
                    )
                if ok:
                    st.success(f"✓ {msg}")
                else:
                    st.error(f"✕ {msg}")

    # 4. "Try Asking" Quick Inquiries Grid (Refined Reference Style)
    st.markdown("<div class='rag-suggested-wrap'><div class='rag-suggested-label'>Try Asking</div></div>", unsafe_allow_html=True)

    q_row1 = st.columns(3)
    with q_row1[0]:
        if st.button("🚨 Why do bank autopay mandates fail silently?", use_container_width=True):
            st.session_state["rag_query_input"] = "Why do bank autopay mandates fail silently and cause involuntary churn?"
            st.rerun()
    with q_row1[1]:
        if st.button("📉 What causes Month 1–3 return panic?", use_container_width=True):
            st.session_state["rag_query_input"] = "What causes panic and SIP cancellations during Months 1 to 3 when portfolio shows negative returns?"
            st.rerun()
    with q_row1[2]:
        if st.button("🧩 Scheme overlap & over-diversification", use_container_width=True):
            st.session_state["rag_query_input"] = "Why do novice investors accumulate 6+ overlapping funds and what friction does it cause?"
            st.rerun()

    q_row2 = st.columns(3)
    with q_row2[0]:
        if st.button("💸 How does the ₹450 ECS penalty trigger churn?", use_container_width=True):
            st.session_state["rag_query_input"] = "How does the fear of ₹450 bank ECS bounce penalties push investors to cancel their entire SIP?"
            st.rerun()
    with q_row2[1]:
        if st.button("⏱️ Why does T+2 settlement delay cause fraud anxiety?", use_container_width=True):
            st.session_state["rag_query_input"] = "Why do users panic over the 48-hour AMC unit allotment delay and misinterpret processing states?"
            st.rerun()
    with q_row2[2]:
        if st.button("🛡️ What habits help investors continue 12+ months?", use_container_width=True):
            st.session_state["rag_query_input"] = "What mental models and product features help investors continue SIPs past 12 months?"
            st.rerun()

    # Filters Row
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    fcol1, fcol2, fcol3 = st.columns([1.5, 1.5, 3])
    with fcol1:
        platform_filter = st.selectbox(
            "Filter Platform Source",
            ["All", "Play Store", "Reddit", "App Store", "YouTube", "Forum"],
            index=0,
            key="rag_plat_filter",
        )
    with fcol2:
        stage_filter = st.selectbox(
            "Filter Journey Stage",
            ["All", "newly_started", "continuing", "paused", "stopped"],
            index=0,
            key="rag_stage_filter",
        )

    # 5. Inquiry Input Bar
    st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
    query_text = st.text_input(
        "Enter your strategic qualitative research inquiry:",
        value=st.session_state.get("rag_query_input", ""),
        placeholder="Ask anything about first-time SIP churn, investor psychology, or payment friction…",
        label_visibility="collapsed",
        key="main_rag_input",
    )

    action_c1, action_c2 = st.columns([4, 1])
    with action_c1:
        submit_clicked = st.button("🔍 Synthesize Qualitative Insight", type="primary", use_container_width=True)
    with action_c2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state["rag_history"] = []
            st.session_state["rag_query_input"] = ""
            st.rerun()

    st.markdown(
        "<div style='text-align: center; color: #64748B; font-size: 13.5px; margin-top: 6px;'>Answers synthesized via hybrid BM25 + Vector retrieval &bull; Strict SEBI Non-Advice compliant &bull; Verifiable quotes</div>",
        unsafe_allow_html=True,
    )

    # 6. Execute Query Pipeline
    if submit_clicked and query_text.strip():
        pipeline = get_shared_pipeline()
        
        with st.spinner("Retrieving evidence via hybrid BM25 + Vector RRF and synthesizing insight via Gemini..."):
            plat_arg = None if platform_filter == "All" else platform_filter.lower().replace(" ", "_")
            stage_arg = None if stage_filter == "All" else stage_filter.lower()

            result = pipeline.query(
                query=query_text.strip(),
                top_k=st.session_state["rag_top_k"],
                platform_filter=plat_arg,
                journey_stage_filter=stage_arg,
                llm_provider=st.session_state["rag_provider"],
                api_key=st.session_state["rag_api_key"],
                model=st.session_state["rag_model"],
                base_url=st.session_state["rag_base_url"],
                temperature=st.session_state["rag_temperature"],
            )

            # Prepend to history for chronological display
            st.session_state["rag_history"].insert(0, result)

    # 7. Render Conversation History (Refined Reference Style)
    if st.session_state["rag_history"]:
        st.markdown("<div class='rag-chat-container'>", unsafe_allow_html=True)
        
        for item in st.session_state["rag_history"]:
            q = item["query"]
            ans = item["answer"]
            evid_list = item.get("retrieved_evidence", [])
            lat = item.get("total_latency_ms", 18.5)
            engine_name = item.get("llm_model") or item.get("llm_provider", "Gemini").split(" (")[0]
            m_count = item.get("evidence_count", len(evid_list))

            # User Bubble
            user_msg_html = f"""<div class="rag-message-user">
<div class="rag-bubble-user">
<strong>PM Research Inquiry:</strong><br/>
{q}
</div>
</div>"""
            st.markdown(user_msg_html, unsafe_allow_html=True)

            # AI Avatar + Bubble
            ai_card_header = f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid #F1F5F9; padding-bottom: 8px;">
<span style="font-size: 13.5px; font-weight: 700; color: #008764; text-transform: uppercase; letter-spacing: 0.04em;">
Synthesized Qualitative Analysis &bull; Backed by {m_count} Evidence Chunks
</span>
<div style="display: flex; gap: 6px; flex-wrap: wrap;">
<span class="badge-tag badge-tier-1">✓ Verified Evidence</span>
<span class="badge-tag badge-platform">Engine: {engine_name}</span>
<span class="badge-tag badge-category">⏱ {lat}ms</span>
<span class="badge-tag badge-category">SEBI Compliant</span>
</div>
</div>"""

            st.markdown(
                f"""<div class="rag-message-ai">
<div class="rag-ai-avatar">🔬</div>
<div class="rag-bubble-ai">
{ai_card_header}
<div class="rag-content-markdown">
""",
                unsafe_allow_html=True,
            )

            # Render synthesized markdown directly
            st.markdown(ans, unsafe_allow_html=True)

            # Retrieved Evidence Chunks Accordion
            if evid_list:
                with st.expander(f"📂 **Inspect {len(evid_list)} Retrieved Customer Evidence Chunks (Click to Expand)**", expanded=False):
                    st.markdown(
                        "<p style='font-size: 14px; color: #64748B; margin-bottom: 10px;'>Exact customer quotes retrieved from the 3,052 verified corpus that substantiate this synthesis:</p>",
                        unsafe_allow_html=True,
                    )
                    
                    for idx, ev in enumerate(evid_list, 1):
                        plat = ev.get("platform", "source").lower().replace(" ", "-")
                        plat_upper = ev.get("platform", "source").upper()
                        pub_date = ev.get("published_at", "Recent")
                        stage = ev.get("journey_stage", "unknown").replace("_", " ").title()
                        sim = round(ev.get("similarity_score", 0.90) * 100, 1)
                        q_text = ev.get("quote", "").replace("<", "&lt;").replace(">", "&gt;")
                        src_url = ev.get("source_url", "")
                        
                        src_link_html = (
                            f'<a href="{src_url}" target="_blank" style="color: #008764; font-weight: 600; text-decoration: none;">[Original Source Link ↗]</a>'
                            if src_url else ''
                        )

                        chunk_html = f"""<div class="evidence-card" style="margin-bottom: 12px; padding: 14px 18px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 6px;">
<div style="display: flex; align-items: center; gap: 8px;">
<span style="font-weight: 800; color: #0F172A; font-size: 14px;">[EVID-{idx}]</span>
<span class="badge-tag badge-{plat}">{plat_upper}</span>
<span class="badge-tag badge-category">{stage}</span>
<span style="font-size: 13.5px; color: #64748B;">📅 {pub_date}</span>
</div>
<div style="font-size: 13.5px; font-weight: 700; color: #008764;">
Relevance Match: {sim}%
</div>
</div>
<div style="font-size: 16px; font-style: italic; color: #1E293B; line-height: 1.6; margin: 8px 0;">
"{q_text}"
</div>
<div style="font-size: 13.5px; margin-top: 6px;">
{src_link_html}
</div>
</div>"""
                        st.markdown(chunk_html, unsafe_allow_html=True)

            st.markdown("</div></div></div>", unsafe_allow_html=True)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Initial Empty State Card matching reference design
        st.markdown(
            """<div class="rag-empty-state">
<div class="rag-empty-icon">🔬</div>
<div class="rag-empty-title">Query 3,052 Customer Evidence Records</div>
<div class="rag-empty-desc">
Ask open-ended strategic inquiries regarding first-time mutual fund SIP churn, mandate drop-offs, return anxiety, or investor psychology. Powered by hybrid BM25 + Vector semantic retrieval and Google Gemini 3.5 Flash.
</div>
<div class="rag-doc-list">
<div class="rag-doc-chip">📱 Google Play Store (1,227)</div>
<div class="rag-doc-chip">▶️ YouTube (1,098)</div>
<div class="rag-doc-chip">💬 Reddit (357)</div>
<div class="rag-doc-chip">🌐 Investor Forums (302)</div>
<div class="rag-doc-chip">🍏 Apple App Store (68)</div>
</div>
</div>""",
            unsafe_allow_html=True,
        )
