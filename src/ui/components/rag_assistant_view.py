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
from src.rag.evaluator import RAGEvaluator
from src.rag.llm_adapter import LLMAdapter


@st.cache_resource(show_spinner="Initializing Evidence Index...")
def get_shared_pipeline(version: str = "v4.1_invest_more_fix") -> RAGPipeline:
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

    # Resolve runtime hybrid LLM vs instant deterministic grounded mode
    use_hybrid = st.session_state.get("rag_engine_mode", "Auto Hybrid (Live LLM + Fallback)") == "Auto Hybrid (Live LLM + Fallback)"
    if use_hybrid:
        llm_cfg = LLMAdapter.resolve_runtime_llm(getattr(st, "secrets", None))
    else:
        llm_cfg = {
            "provider": "Deterministic Grounded Engine (No Key Required)",
            "api_key": None,
            "model": None,
        }

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

    if "rag_engine_mode" not in st.session_state:
        st.session_state["rag_engine_mode"] = "Auto Hybrid (Live LLM + Fallback)"

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
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            if has_messages:
                if st.button("New Chat", key="ai_eng_new_chat", use_container_width=True):
                    st.session_state["chat_messages"] = []
                    st.cache_resource.clear()
                    st.rerun()
            else:
                if st.button("Reset Engine", key="ai_eng_reset_cache", use_container_width=True, help="Flush in-memory engine cache"):
                    st.cache_resource.clear()
                    st.rerun()
        with btn_c2:
            st.markdown(
                """<div style="background: rgba(0, 208, 156, 0.12); color: #00D09C; font-size: 12px; font-weight: 700; padding: 7px 10px; border-radius: 8px; border: 1px solid rgba(0, 208, 156, 0.3); text-align: center;">
                3,052 Reviews
                </div>""",
                unsafe_allow_html=True,
            )
        st.selectbox(
            "Synthesis Mode",
            ["Auto Hybrid (Live LLM + Fallback)", "Instant Grounded Engine"],
            key="rag_engine_mode",
            label_visibility="collapsed",
        )

    # 2. Expandable Architectural Guide: How AI Answers vs How It Must NOT Answer
    with st.expander("🛡️ RAG AI Answering Guardrails & Fallback Architecture (How It Answers vs How It Must NOT Answer)", expanded=False):
        g_tab1, g_tab2, g_tab3, g_tab4 = st.tabs([
            "✅ How It Answers",
            "🚫 How It Must NOT Answer",
            "🔄 Multi-Tier Fallback",
            "🧪 Golden Benchmark Runner (25 Cases)",
        ])

        with g_tab1:
            st.markdown(
                """
                ### Streamlined 2-Section Qualitative Synthesis Hierarchy (Token-Optimized)
                Every generated response adheres to the following positive answering specification:
                
                - **1. Executive Summary & Behavioral Dynamic:** Unpacks investor mental models (e.g. loss aversion, linear FD return proxy, present bias, decision paralysis) explaining why first-time investors experience drop-off during Months 1–12. Must cite evidence with `[EVID-X]`.
                - **2. Discovered Friction & Root Cause Breakdown:**
                  - *Operational / Technical Friction:* Banking drops, NPCI limits, settlement lag (T+2), or UI ambiguities.
                  - *Cognitive / Mental Model Mismatch:* Clash between expectations (FD linear returns, instant UPI confirmation) and market reality.
                  - Explicitly cites evidence with `[EVID-1]`, `[EVID-2]`, etc.
                - **Token-Efficient Grounding Design:** Customer quote receipts are rendered directly in the visual evidence cards below to eliminate quote duplication and minimize token consumption.
                - **Empirical Grounding Invariant:** Zero hallucination. Every assertion must be anchored in verified evidence.
                """
            )

        with g_tab2:
            st.markdown(
                """
                ### Strict Negative Guardrails (Zero Tolerance Anti-Patterns)
                The AI is actively monitored and strictly forbidden from outputting the following:
                
                1. **🚫 SEBI Financial Advisory Violations:**
                   - NEVER recommend, pick, or rank specific mutual fund schemes, AMCs, or equities (e.g., *NEVER* say "You should buy Parag Parikh Flexi Cap" or "Switch to Quant Small Cap").
                   - NEVER promise or project guaranteed returns, yields, or CAGR.
                   - Redirection: Clearly explains that the engine provides UX/product discovery, not financial advice, and redirects to asset allocation frameworks.
                2. **🚫 Dark Patterns & Manipulative FOMO Retention:**
                   - NEVER propose deceptive friction (e.g. hiding the cancel button, artificial countdown timers, forcing phone calls to cancel, or guilt-tripping churn locks).
                   - Retention must be earned ethically through liquidity flexibility (1-tap smart pause, salary synchronization, pre-debit notifications).
                3. **🚫 Phantom Citations & Ungrounded Hallucinations:**
                   - NEVER cite phantom tags (e.g. citing `[EVID-7]` when only 3 chunks exist).
                   - NEVER fabricate user quotes, imaginary percentages, or phantom surveys.
                4. **🚫 Generic Chatbot Fluff & Evasive Boilerplate:**
                   - NEVER provide generic textbook definitions ("A mutual fund is an investment vehicle...") or empty non-answers.
                5. **🚫 Victim Blaming & User Shaming:**
                   - NEVER blame novice investors as "financially illiterate" or "foolish". Anxiety is treated as a natural signal of mental model clashes and system friction.
                """
            )

        with g_tab3:
            st.markdown(
                """
                ### Multi-Tier Resilient Fallback Architecture (100% Availability)
                The system provides seamless failover across 4 layers of infrastructure:
                
                - **Tier 1: Direct Hybrid BM25 + Vector RRF:** Combines lexical BM25 token matching with semantic TF-IDF cosine similarity across 3,052 conversations.
                - **Tier 2: Synonym & Lemmatized Query Expansion Fallback:** If initial hits are sparse, queries are automatically expanded using financial domain synonym mappings (e.g. *mandate* ↔ *autopay* ↔ *nach*, *bounce* ↔ *penalty* ↔ *ecs*).
                - **Tier 3: Thematic Cluster Centroid Fallback:** If zero keyword matches exist, the inquiry is dynamically routed to the nearest of the 7 discovered failure themes, pulling top representative quotes.
                - **Tier 4: Universal Deterministic Failover (Zero API Dependency):** If external LLMs timeout, quota-out (HTTP 429), or fail, the Deterministic Grounded Engine takes over with 0ms downtime.
                - **Tier 5: Post-Generation Guardrail Interceptor:** If external LLM output violates SEBI non-advice or anti-FOMO rules, the interceptor catches and replaces it with safe behavioral synthesis.
                """
            )

        with g_tab4:
            st.markdown("### Golden Benchmark Suite (25 Test Cases)")
            st.write("Execute standardized benchmark evaluations across all 25 test cases to verify retrieval precision, SEBI compliance, anti-FOMO guardrails, citation integrity, and fallback resilience.")

            if st.button("Run Full Golden Benchmark Evaluation 🚀", key="btn_run_golden_benchmark", use_container_width=True):
                with st.spinner("Evaluating 25 golden test cases across all criteria..."):
                    evaluator = RAGEvaluator()
                    bench_summary = evaluator.evaluate_all(top_k=5)

                st.success(f"Benchmark Complete! {bench_summary['passed_cases']}/{bench_summary['total_cases']} cases passed ({bench_summary['overall_pass_rate']}%).")
                
                b_m1, b_m2, b_m3, b_m4, b_m5 = st.columns(5)
                b_m1.metric("Overall Pass Rate", f"{bench_summary['overall_pass_rate']}%")
                b_m2.metric("SEBI Compliance", f"{bench_summary['sebi_compliance_rate']}%")
                b_m3.metric("Anti-FOMO Guardrail", f"{bench_summary['fomo_compliance_rate']}%")
                b_m4.metric("Zero Hallucination", f"{bench_summary['zero_hallucination_rate']}%")
                b_m5.metric("Avg Latency", f"{bench_summary['avg_latency_ms']} ms")

                with st.expander("View Case-by-Case Diagnostic Results", expanded=False):
                    for c_idx, c_res in enumerate(bench_summary["cases_evaluated"], 1):
                        status_emoji = "✅" if c_res["case_passed"] else "❌"
                        st.markdown(
                            f"**{status_emoji} [{c_res['query_id']}]** `{c_res['category']}`: *\"{c_res['query']}\"*  \n"
                            f"• Citations: {c_res['unique_citations']} | SEBI: {'PASS' if c_res['sebi_compliant'] else 'FAIL'} | "
                            f"Anti-FOMO: {'PASS' if c_res['fomo_compliant'] else 'FAIL'} | "
                            f"Structure: {c_res['structure_score']*100:.0f}% | "
                            f"Retrieval: {c_res['retrieval_fallback_tier']} | Latency: {c_res['latency_ms']}ms"
                        )

    st.markdown("<div style='border-bottom: 1px solid #1E2533; margin-bottom: 18px;'></div>", unsafe_allow_html=True)

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
                            src_link = f'<a href="{src_url}" target="_blank" style="color: #00D09C; font-weight: 600; text-decoration: none; font-size: 11px;">[Source Link ↗]</a>' if src_url else ""

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
