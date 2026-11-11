"""Ask AI Engine Component (Discovery Engine Query Center).

Modeled after Groww's Executive Discovery Suite & Customer Voice Grounding:
1. Focused, clean State 1 (Unified Interactive Starter Question Cards).
2. Direct question-to-answer loop: Ask a question -> Get empirical, data-backed synthesis.
3. In-stream Verbatim Customer Evidence receipts in a compact 2-column grid.
4. Active conversational thread with persistent follow-up composer & 2x2 follow-up pills.
5. Strict SEBI non-advice compliance & resilient multi-tier deterministic fallback.
6. Real-time Positive Answering & Negative Guardrails compliance auditing.
"""

import re
from typing import Any, Dict, List, Optional
import streamlit as st

from src.rag.retriever import HybridEvidenceRetriever
from src.rag.pipeline import RAGPipeline
from src.rag.llm_adapter import LLMAdapter
from src.ui.components.common_ui import format_source_link_html


@st.cache_resource(show_spinner="Initializing Evidence Index...")
def get_shared_pipeline(version: str = "v4.5_hide_engineering_plumbing") -> RAGPipeline:
    """Initialize and cache the hybrid BM25 + Vector retriever pipeline."""
    retriever = HybridEvidenceRetriever()
    return RAGPipeline(retriever=retriever)


# 4 Curated High-Impact Starter Questions Aligned with Research Findings
STARTER_CARDS = [
    {
        "id": "autopay",
        "category": "AUTOPAY & ECS PENALTIES",
        "category_color": "#00D09C",
        "question": "Why do bank autopay mandates fail silently and trigger cancellations?",
        "corpus_stat": "18.0% Corpus Share • 548 Reviews",
        "finding": "Finding #3: Lack of Emergency Funds",
    },
    {
        "id": "drawdown",
        "category": "FIRST-MONTH DRAWDOWN PANIC",
        "category_color": "#F87171",
        "question": "Why do users panic when their early portfolio shows negative returns?",
        "corpus_stat": "5.9% Corpus Share • Months 1–3 Drop",
        "finding": "Finding #1: Market Fluctuations",
    },
    {
        "id": "overlap",
        "category": "PORTFOLIO OVER-DIVERSIFICATION",
        "category_color": "#38BDF8",
        "question": "Why do first-time users accumulate 6+ overlapping funds?",
        "corpus_stat": "9.3% Corpus Share • 284 Reviews",
        "finding": "Finding #2: Not Setting Financial Goals",
    },
    {
        "id": "nav_delay",
        "category": "NAV SETTLEMENT DELAYS",
        "category_color": "#FBBF24",
        "question": "Why do users panic over the 48-hour NAV allotment delay?",
        "corpus_stat": "5.3% Corpus Share • 163 Reviews",
        "finding": "Finding #1: Market Fluctuations",
    },
]

# Quick follow-up prompts for active conversation
FOLLOW_UP_SUGGESTIONS = [
    "Which specific banks (HDFC, SBI, etc.) fail most often?",
    "What workarounds do users discuss on Reddit?",
    "What habits differentiate 12-month continuers from early drop-offs?",
    "How does fear of ₹450 bank bounce fines trigger cancellations?",
]


AI_DISCLAIMER_HTML = (
    '<div style="text-align: center; font-size: 11.5px; color: #64748B; margin-top: 6px; margin-bottom: 4px;">'
    'Ask AI Engine is grounded on 3,052 verified customer reviews and can make mistakes &bull; Research discovery only, not SEBI financial advice.'
    '</div>'
)


def execute_inquiry(pipeline: RAGPipeline, query_text: str) -> None:
    """Execute inquiry immediately and record into conversation history."""
    clean_query = query_text.strip()
    if not clean_query:
        return

    # Append user question
    st.session_state["chat_messages"].append({
        "role": "user",
        "content": clean_query,
    })

    # Silently resolve runtime LLM with automatic grounded failover on the backend
    llm_cfg = LLMAdapter.resolve_runtime_llm(getattr(st, "secrets", None))

    # Execute RAG query through pipeline with GR-1-style Thinking state
    with st.spinner("Thinking across 3,052 verified customer reviews..."):
        res = pipeline.query(
            query=clean_query,
            top_k=5,
            llm_provider=llm_cfg["provider"] or "Deterministic Grounded Engine (No Key Required)",
            api_key=llm_cfg["api_key"],
            model=llm_cfg["model"],
        )

    synthesis = res["answer"]
    evid = res.get("retrieved_evidence", [])
    latency = res.get("total_latency_ms", 22.0)
    sebi_ok = res.get("sebi_compliant", True)
    fomo_ok = res.get("fomo_compliant", True)
    is_fallback = res.get("is_fallback", False)
    retrieval_tier = res.get("retrieval_fallback_tier", "Tier 1: Direct Hybrid RRF")
    exec_mode = res.get("execution_mode", "Deterministic Grounded Engine")
    clarification_chips = res.get("clarification_chips", [])
    follow_ups = res.get("follow_up_suggestions", FOLLOW_UP_SUGGESTIONS)

    # Append assistant synthesis
    st.session_state["chat_messages"].append({
        "role": "assistant",
        "content": synthesis,
        "evidence": evid,
        "evidence_count": len(evid),
        "latency_ms": latency,
        "query": clean_query,
        "sebi_ok": sebi_ok,
        "fomo_ok": fomo_ok,
        "is_fallback": is_fallback,
        "retrieval_tier": retrieval_tier,
        "exec_mode": exec_mode,
        "clarification_chips": clarification_chips,
        "follow_up_suggestions": follow_ups,
    })


def render_rag_assistant_view(db_path=None) -> None:
    """Render the Ask AI Engine interface focused on Question -> Answer."""
    pipeline = get_shared_pipeline()

    # Initialize session state for conversation history
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    else:
        # Automatically clean any legacy cached messages in session state that still contain Sections 3 or 4
        for msg in st.session_state["chat_messages"]:
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if "### 3. Voice of Customer" in content:
                    content = content.split("### 3. Voice of Customer")[0].strip()
                if "### 4. Strategic PM" in content:
                    content = content.split("### 4. Strategic PM")[0].strip()
                msg["content"] = content

    # Auto-execute contextual inquiry launched from Themes / Opportunity cards
    pending_query = st.session_state.pop("pending_ai_query", None)
    if pending_query and pending_query.strip():
        execute_inquiry(pipeline, pending_query.strip())

    has_messages = bool(st.session_state["chat_messages"])

    # 1. Page Header Bar
    h_col1, h_col2 = st.columns([3.4, 1.6])
    with h_col1:
        st.markdown(
            """<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
            <div style="width: 40px; height: 40px; border-radius: 10px; background: #00D09C; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; color: #0B0E14; letter-spacing: -0.02em; flex-shrink: 0; box-shadow: 0 2px 8px rgba(0, 208, 156, 0.3);">
            AI
            </div>
            <div>
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <h1 class="page-title" style="margin: 0; font-size: 22px; font-weight: 800; color: #F1F5F9;">Ask AI Engine</h1>
            <span class="badge-tag badge-tier-1">Direct Discovery</span>
            <span class="badge-tag badge-category">SEBI Non-Advice</span>
            <span class="badge-tag badge-category">Anti-FOMO Guardrail</span>
            </div>
            <p class="page-subtitle" style="margin: 2px 0 0 0; font-size: 13px; color: #94A3B8;">
            Direct answers grounded across 3,052 verified customer reviews &bull; Structured Behavioral Synthesis &bull; Hybrid Guarded Fallback
            </p>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with h_col2:
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            if has_messages and st.button("New Chat", key="ai_eng_new_chat", use_container_width=True):
                st.session_state["chat_messages"] = []
                st.rerun()
        with btn_c2:
            st.markdown(
                """<div style="background: rgba(0, 208, 156, 0.12); color: #00D09C; font-size: 12px; font-weight: 700; padding: 7px 10px; border-radius: 8px; border: 1px solid rgba(0, 208, 156, 0.3); text-align: center;">
                3,052 Reviews
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='border-bottom: 1px solid #1E2533; margin-top: 8px; margin-bottom: 18px;'></div>", unsafe_allow_html=True)

    active_prompt_to_run = None

    # =========================================================================
    # STATE 1: CLEAN, FOCUSED STARTING STATE (Empty Chat)
    # =========================================================================
    if not has_messages:
        # Primary Query Input Bar + Submit Button inside a Form
        with st.form("ask_ai_starter_form", clear_on_submit=False):
            inp_col, btn_col = st.columns([5.2, 1.3], gap="small")
            with inp_col:
                starter_query_input = st.text_input(
                    "Ask anything:",
                    placeholder="Ask about autopay failures, market panic, fund clutter, or NAV delays...",
                    label_visibility="collapsed",
                    key="starter_query_input",
                )
            with btn_col:
                starter_ask_clicked = st.form_submit_button("Ask Engine 🚀", type="primary", use_container_width=True)

        if starter_ask_clicked and starter_query_input.strip():
            active_prompt_to_run = starter_query_input.strip()

        st.markdown(AI_DISCLAIMER_HTML, unsafe_allow_html=True)

        # Section Label for Starter Cards with subtle gradient divider
        st.markdown(
            """<div style="display: flex; align-items: center; justify-content: center; gap: 16px; margin: 26px 0 18px 0;">
            <div style="flex: 1; height: 1px; background: linear-gradient(90deg, transparent, #2B3548);"></div>
            <span style="font-size: 11.5px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em;">
                Or explore frequent investor drop-off questions
            </span>
            <div style="flex: 1; height: 1px; background: linear-gradient(90deg, #2B3548, transparent);"></div>
            </div>""",
            unsafe_allow_html=True,
        )

        # 4 High-Impact Starter Cards in 2x2 Grid (Unified Card Tiles)
        grid_col1, grid_col2 = st.columns(2, gap="medium")
        for idx, card in enumerate(STARTER_CARDS):
            target_col = grid_col1 if idx % 2 == 0 else grid_col2
            with target_col:
                card_top_html = f"""<div class="starter-card-top">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11.5px; font-weight: 800; color: {card['category_color']}; letter-spacing: 0.06em; text-transform: uppercase;">
                        {card['category']}
                    </span>
                    <span style="background: rgba(255, 255, 255, 0.04); color: #94A3B8; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; border: 1px solid #2B3548;">
                        {card['corpus_stat']}
                    </span>
                </div>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 14.5px; font-weight: 700; color: #F1F5F9; line-height: 1.45; min-height: 44px; margin-bottom: 8px;">
                    "{card['question']}"
                </div>
                <div style="font-size: 12px; color: #64748B;">
                    Aligned with <strong style="color: #94A3B8;">{card['finding']}</strong>
                </div>
                </div>"""
                st.markdown(card_top_html, unsafe_allow_html=True)
                if st.button("Explore Question ➔", key=f"btn_starter_{card['id']}", use_container_width=True):
                    active_prompt_to_run = card["question"]

    # =========================================================================
    # STATE 2: ACTIVE CONVERSATION THREAD
    # =========================================================================
    else:
        turn_to_delete = None
        for idx, msg in enumerate(st.session_state["chat_messages"]):
            if msg["role"] == "user":
                u_col1, u_col2 = st.columns([0.93, 0.07], gap="small")
                with u_col1:
                    st.markdown(
                        f"""<div style="display: flex; justify-content: flex-end; margin-top: 18px; margin-bottom: 14px;">
                        <div style="background: #1A2230; border: 1px solid #2B3548; border-left: 3.5px solid #00D09C; border-radius: 10px; padding: 14px 20px; max-width: 88%; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);">
                        <div style="font-size: 11px; font-weight: 700; color: #00D09C; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.05em;">YOUR INQUIRY</div>
                        <div style="font-size: 16px; font-weight: 600; color: #F1F5F9; line-height: 1.45;">{msg['content']}</div>
                        </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with u_col2:
                    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)
                    if st.button("✕", key=f"del_turn_{idx}", help="Remove this Q&A turn from history"):
                        turn_to_delete = idx
            else:
                evidence_list = msg.get("evidence", [])

                with st.container(border=True):
                    # Core Synthesized Executive Answer (with highlighted citation badges)
                    content_to_render = msg["content"]
                    if "### 3. Voice of Customer" in content_to_render:
                        content_to_render = content_to_render.split("### 3. Voice of Customer")[0].strip()
                    if "### 4. Strategic PM" in content_to_render:
                        content_to_render = content_to_render.split("### 4. Strategic PM")[0].strip()

                    formatted_content = re.sub(r"\[EVID-(\d+)\]", r'<span class="evid-tag">[EVID-\1]</span>', content_to_render)
                    st.markdown(formatted_content, unsafe_allow_html=True)

                    # Render Interactive Clarification Chips if returned
                    chips = msg.get("clarification_chips", [])
                    if chips:
                        st.markdown("<div style='margin-top: 14px; margin-bottom: 8px; font-size: 12px; font-weight: 700; color: #00D09C; text-transform: uppercase; letter-spacing: 0.05em;'>👉 Suggested Research Pathways:</div>", unsafe_allow_html=True)
                        chip_c1, chip_c2 = st.columns(2, gap="small")
                        for c_idx, chip in enumerate(chips):
                            target_chip_col = chip_c1 if c_idx % 2 == 0 else chip_c2
                            with target_chip_col:
                                if st.button(chip["label"], key=f"chip_msg_{idx}_{c_idx}", use_container_width=True):
                                    active_prompt_to_run = chip["query"]

                    # Verbatim Customer Evidence Receipts (in a compact 2-column grid to prevent scroll bloat)
                    if evidence_list:
                        st.markdown(
                            f"""<div style="margin-top: 22px; padding-top: 16px; border-top: 1px solid #1E2533;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 6px;">
                            <span style="font-size: 12.5px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">
                            💬 Verified Customer Evidence ({len(evidence_list)} Grounded Receipts):
                            </span>
                            <span style="font-size: 11.5px; color: #00D09C; font-weight: 600;">100% Verbatim Customer Reviews</span>
                            </div>
                            </div>""",
                            unsafe_allow_html=True,
                        )

                        ev_col1, ev_col2 = st.columns(2, gap="small")
                        for e_idx, ev in enumerate(evidence_list, 1):
                            target_ev_col = ev_col1 if (e_idx % 2 != 0) else ev_col2
                            plat = ev.get("platform", "source").upper()
                            stage = ev.get("journey_stage", "unknown").replace("_", " ").title()
                            pub_date = ev.get("published_at", "Recent")
                            q_text = ev.get("quote", "").replace("<", "&lt;").replace(">", "&gt;")
                            src_url = ev.get("source_url", "")
                            src_link = format_source_link_html(src_url, label="[Source Link ↗]", color="#00D09C", font_size="11px")

                            # Distinct badge color per platform
                            plat_bg = "rgba(0, 208, 156, 0.12)"
                            plat_color = "#00D09C"
                            if "REDDIT" in plat:
                                plat_bg = "rgba(251, 146, 60, 0.12)"
                                plat_color = "#FB923C"
                            elif "APP STORE" in plat or "IOS" in plat:
                                plat_bg = "rgba(56, 189, 248, 0.12)"
                                plat_color = "#38BDF8"
                            elif "YOUTUBE" in plat:
                                plat_bg = "rgba(248, 113, 113, 0.12)"
                                plat_color = "#F87171"

                            with target_ev_col:
                                st.markdown(
                                    f"""<div style="background: #1A2230; border: 1px solid #2B3548; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px; min-height: 125px; display: flex; flex-direction: column; justify-content: space-between;">
                                    <div>
                                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; margin-bottom: 6px;">
                                    <div><strong style="color: #00D09C;">[EVID-{e_idx}]</strong> &bull; <span style="background: {plat_bg}; color: {plat_color}; padding: 1px 6px; border-radius: 4px; font-weight: 700; font-size: 10.5px;">{plat}</span></div>
                                    <span style="color: #64748B; font-size: 11px;">{pub_date}</span>
                                    </div>
                                    <div style="font-size: 13px; font-style: italic; color: #E2E8F0; line-height: 1.45; margin: 4px 0;">"{q_text}"</div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font-size: 11px; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 4px;">
                                    <span style="color: #94A3B8;">Stage: {stage}</span>
                                    {src_link}
                                </div>
                                </div>""",
                                    unsafe_allow_html=True,
                                )

        if turn_to_delete is not None:
            msgs = st.session_state["chat_messages"]
            end_idx = turn_to_delete + 2 if (turn_to_delete + 1 < len(msgs) and msgs[turn_to_delete + 1].get("role") == "assistant") else turn_to_delete + 1
            del msgs[turn_to_delete:end_idx]
            st.rerun()

        # Persistent Follow-up Chat Composer
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        with st.form("ask_ai_followup_form", clear_on_submit=True):
            f_inp, f_btn = st.columns([5.2, 1.3], gap="small")
            with f_inp:
                followup_query_input = st.text_input(
                    "Follow-up inquiry:",
                    placeholder="Ask a follow-up or explore another topic (e.g. 'Which specific banks fail most often?')...",
                    label_visibility="collapsed",
                    key="followup_query_input",
                )
            with f_btn:
                followup_ask_clicked = st.form_submit_button("Send / Ask 🚀", type="primary", use_container_width=True)

        if followup_ask_clicked and followup_query_input.strip():
            active_prompt_to_run = followup_query_input.strip()

        st.markdown(AI_DISCLAIMER_HTML, unsafe_allow_html=True)

        # Dynamic GR-1-style Follow-Up Question Chips aligned with the last reply
        dynamic_followups = FOLLOW_UP_SUGGESTIONS
        for m in reversed(st.session_state["chat_messages"]):
            if m.get("role") == "assistant" and m.get("follow_up_suggestions"):
                dynamic_followups = m["follow_up_suggestions"]
                break

        st.markdown(
            """<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; margin-bottom: 8px;">
            <span style="font-size: 11.5px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em;">
            Suggested Follow-up Inquiries:
            </span>
            </div>""",
            unsafe_allow_html=True,
        )
        for row_start in range(0, min(4, len(dynamic_followups)), 2):
            f_c1, f_c2 = st.columns(2, gap="small")
            with f_c1:
                q_item = dynamic_followups[row_start]
                if st.button(f"↳ {q_item}", key=f"fup_chip_{row_start}", use_container_width=True):
                    active_prompt_to_run = q_item
            if row_start + 1 < len(dynamic_followups):
                with f_c2:
                    q_item_2 = dynamic_followups[row_start + 1]
                    if st.button(f"↳ {q_item_2}", key=f"fup_chip_{row_start + 1}", use_container_width=True):
                        active_prompt_to_run = q_item_2

    # Execute inquiry if submitted from form or buttons
    if active_prompt_to_run:
        execute_inquiry(pipeline, active_prompt_to_run)
        st.rerun()
