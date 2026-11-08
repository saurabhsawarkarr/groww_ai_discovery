"""Golden Set Benchmarking & AI Failure Audit Center Component (Tab 4 / Engine Info).

Matches the reference Google Photos Discovery Engine architecture design:
- Top Badge & Philosophy Quote Banner
- 4-Card Hero Metric Grid
- Horizontal 5-Stage Data Processing Pipeline Stepper with SVG icons & gradient track
- 2-Column Grid: Core Qualitative Capabilities (2x2 grid) & 5 Ingestion Sources (list with badges)
- 7-Dimension Agreement Benchmark Metrics & Curated Golden Set Inspection
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import streamlit as st

from src.database.connection import get_connection
from src.evaluation.benchmark import GoldenSetBenchmark
from src.evaluation.failure_logger import AIFailureLogger


ENGINE_TOP_HTML = """<div class="engine-header">
<div class="engine-badge">
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>
About the Discovery Platform
</div>
<h1 class="engine-title">Groww SIP Discovery Engine</h1>
<p class="engine-subtitle">An AI-powered qualitative customer intelligence system that transforms thousands of fragmented user conversations into structured, evidence-backed insights for product and growth teams.</p>
</div>
<div class="engine-quote-card">
<h2 class="engine-quote-text">&ldquo;From customer voices <span class="engine-quote-arrow">&rarr;</span> structured evidence <span class="engine-quote-arrow">&rarr;</span> behavioral understanding <span class="engine-quote-arrow">&rarr;</span> actionable insight.&rdquo;</h2>
</div>"""

ENGINE_STATS_HTML = """<div class="engine-stats-grid" style="margin-bottom: 1.5rem;">
<div class="engine-stat-card">
<div class="engine-stat-label">Total Records Ingested</div>
<div class="engine-stat-value">32,547</div>
<div class="engine-stat-subtext engine-subtext-green">Raw discourse from 5 sources</div>
</div>
<div class="engine-stat-card">
<div class="engine-stat-label">Cleaned &amp; Normalized</div>
<div class="engine-stat-value">~9,850</div>
<div class="engine-stat-subtext engine-subtext-green">Records after fuzzy deduplication</div>
</div>
<div class="engine-stat-card">
<div class="engine-stat-label">Relevance Filtered</div>
<div class="engine-stat-value">3,052</div>
<div class="engine-stat-subtext engine-subtext-green">100% relevant MF/SIP conversations</div>
</div>
<div class="engine-stat-card">
<div class="engine-stat-label">Structured Journeys</div>
<div class="engine-stat-value">111</div>
<div class="engine-stat-subtext engine-subtext-blue">Fully extracted failure journeys</div>
</div>
</div>"""

ENGINE_PIPELINE_HTML = """<div class="engine-section-card">
<div class="engine-section-header">
<h2 class="engine-section-title">
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A73E8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20v2"></path><path d="M12 2v2"></path><path d="M17 20v2"></path><path d="M17 2v2"></path><path d="M2 12h2"></path><path d="M2 17h2"></path><path d="M2 7h2"></path><path d="M20 12h2"></path><path d="M20 17h2"></path><path d="M20 7h2"></path><path d="M7 20v2"></path><path d="M7 2v2"></path><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="8" y="8" width="8" height="8" rx="1"></rect></svg>
Data Processing Pipeline
</h2>
</div>
<div class="engine-timeline-wrapper">
<div class="engine-timeline-line"></div>
<div class="engine-timeline-step">
<div class="engine-timeline-icon-wrap" style="border-color:#38BDF8; color:#38BDF8;">
<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 13v8l-4-4"></path><path d="m12 21 4-4"></path><path d="M4.393 15.269A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.436 8.284"></path></svg>
</div>
<span class="engine-timeline-name">1. Collection</span>
<span class="engine-timeline-desc">Scraping &amp; APIs</span>
</div>
<div class="engine-timeline-step">
<div class="engine-timeline-icon-wrap" style="border-color:#38BDF8; color:#38BDF8;">
<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 20a1 1 0 0 0 .553.895l2 1A1 1 0 0 0 14 21v-7a2 2 0 0 1 .517-1.341L21.74 4.67A1 1 0 0 0 21 3H3a1 1 0 0 0-.742 1.67l7.225 7.989A2 2 0 0 1 10 14z"></path></svg>
</div>
<span class="engine-timeline-name">2. Cleaning</span>
<span class="engine-timeline-desc">MinHash Deduplication</span>
</div>
<div class="engine-timeline-step">
<div class="engine-timeline-icon-wrap" style="border-color:#A78BFA; color:#A78BFA;">
<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 20a1 1 0 0 0 .553.895l2 1A1 1 0 0 0 14 21v-7a2 2 0 0 1 .517-1.341L21.74 4.67A1 1 0 0 0 21 3H3a1 1 0 0 0-.742 1.67l7.225 7.989A2 2 0 0 1 10 14z"></path></svg>
</div>
<span class="engine-timeline-name">3. Relevance</span>
<span class="engine-timeline-desc">2-Pass Filtering</span>
</div>
<div class="engine-timeline-step">
<div class="engine-timeline-icon-wrap" style="border-color:#00D09C; color:#00D09C;">
<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
</div>
<span class="engine-timeline-name">4. Extraction</span>
<span class="engine-timeline-desc">LLM JSON Schema</span>
</div>
<div class="engine-timeline-step">
<div class="engine-timeline-icon-wrap" style="border-color:#FBBF24; color:#FBBF24;">
<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
</div>
<span class="engine-timeline-name">5. Analytics</span>
<span class="engine-timeline-desc">Data-Driven Segments</span>
</div>
</div>
</div>"""

ENGINE_TWO_COL_HTML = """<div class="engine-two-col-grid">
<!-- Left: Core Qualitative Capabilities -->
<div class="engine-section-card" style="margin-bottom: 0;">
<div class="engine-section-header">
<h2 class="engine-section-title">
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20v2"></path><path d="M12 2v2"></path><path d="M17 20v2"></path><path d="M17 2v2"></path><path d="M2 12h2"></path><path d="M2 17h2"></path><path d="M2 7h2"></path><path d="M20 12h2"></path><path d="M20 17h2"></path><path d="M20 7h2"></path><path d="M7 20v2"></path><path d="M7 2v2"></path><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="8" y="8" width="8" height="8" rx="1"></rect></svg>
Core Qualitative Capabilities
</h2>
</div>
<div class="engine-caps-grid">
<div class="engine-cap-card">
<div class="engine-cap-icon" style="background:rgba(0, 208, 156, 0.15); color:#00D09C;">
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
</div>
<h3 class="engine-cap-title">Journey Extraction</h3>
<p class="engine-cap-desc">Extracts failure points (mandates, KYC, folio sync), behavioral triggers, and workarounds.</p>
</div>
<div class="engine-cap-card">
<div class="engine-cap-icon" style="background:rgba(251, 191, 36, 0.15); color:#FBBF24;">
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13.172 2a2 2 0 0 1 1.414.586l6.71 6.71a2.4 2.4 0 0 1 0 3.408l-4.592 4.592a2.4 2.4 0 0 1-3.408 0l-6.71-6.71A2 2 0 0 1 6 9.172V3a1 1 0 0 1 1-1z"></path><path d="M2 7v6.172a2 2 0 0 0 .586 1.414l6.71 6.71a2.4 2.4 0 0 0 3.191.193"></path><circle cx="10.5" cy="6.5" r=".5" fill="currentColor"></circle></svg>
</div>
<h3 class="engine-cap-title">Relevance Filtering</h3>
<p class="engine-cap-desc">Fast keyword filtering followed by LLM classification for ambiguous records.</p>
</div>
<div class="engine-cap-card">
<div class="engine-cap-icon" style="background:rgba(248, 113, 113, 0.15); color:#F87171;">
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 21a8 8 0 0 0-16 0"></path><circle cx="10" cy="8" r="5"></circle><path d="M22 20c0-3.37-2-6.5-4-8a5 5 0 0 0-.45-8.3"></path></svg>
</div>
<h3 class="engine-cap-title">Behavioral Segments</h3>
<p class="engine-cap-desc">Analyzes extracted data to discover emergent, data-driven user archetypes.</p>
</div>
<div class="engine-cap-card">
<div class="engine-cap-icon" style="background:rgba(56, 189, 248, 0.15); color:#38BDF8;">
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 10.656V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12.344"></path><path d="m9 11 3 3L22 4"></path></svg>
</div>
<h3 class="engine-cap-title">Fuzzy Deduplication</h3>
<p class="engine-cap-desc">MinHash algorithm used to find and link identical failure reports.</p>
</div>
</div>
</div>

<!-- Right: 5 Ingestion Sources -->
<div class="engine-section-card" style="margin-bottom: 0;">
<div class="engine-section-header">
<h2 class="engine-section-title">
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F29900" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg>
5 Ingestion Sources
</h2>
</div>
<div class="engine-sources-list">
<div class="engine-source-row">
<div class="engine-source-icon" style="background:#1A73E8;">P</div>
<div class="engine-source-info">
<h4 class="engine-source-title">Google Play Store</h4>
<p class="engine-source-desc">Android app reviews</p>
</div>
<div class="engine-source-stats">
<span class="engine-source-count">27,112</span>
<span class="engine-source-pct">83.3%</span>
</div>
</div>
<div class="engine-source-row">
<div class="engine-source-icon" style="background:#5F6368;">A</div>
<div class="engine-source-info">
<h4 class="engine-source-title">Apple App Store</h4>
<p class="engine-source-desc">iOS app reviews</p>
</div>
<div class="engine-source-stats">
<span class="engine-source-count">528</span>
<span class="engine-source-pct">1.6%</span>
</div>
</div>
<div class="engine-source-row">
<div class="engine-source-icon" style="background:#FF4500;">R</div>
<div class="engine-source-info">
<h4 class="engine-source-title">Reddit API</h4>
<p class="engine-source-desc">r/IndiaInvestments, r/MutualFunds</p>
</div>
<div class="engine-source-stats">
<span class="engine-source-count">574</span>
<span class="engine-source-pct">1.8%</span>
</div>
</div>
<div class="engine-source-row">
<div class="engine-source-icon" style="background:#D93025;">Y</div>
<div class="engine-source-info">
<h4 class="engine-source-title">YouTube Data API</h4>
<p class="engine-source-desc">MF educational comments</p>
</div>
<div class="engine-source-stats">
<span class="engine-source-count">3,745</span>
<span class="engine-source-pct">11.5%</span>
</div>
</div>
<div class="engine-source-row">
<div class="engine-source-icon" style="background:#188038;">F</div>
<div class="engine-source-info">
<h4 class="engine-source-title">Investor Forums</h4>
<p class="engine-source-desc">ValuePickr &amp; TradingQ&amp;A</p>
</div>
<div class="engine-source-stats">
<span class="engine-source-count">588</span>
<span class="engine-source-pct">1.8%</span>
</div>
</div>
</div>
</div>
</div>"""


def render_audit_center(db_path=None) -> None:
    """Render Tab 4: Golden Set Benchmarking & Engine Architecture View."""
    
    # 1. Top Philosophy Mission Banner & Header
    st.markdown(ENGINE_TOP_HTML, unsafe_allow_html=True)

    # 2. 4-Card Hero Metric Grid
    st.markdown(ENGINE_STATS_HTML, unsafe_allow_html=True)

    # 3. Data Processing Pipeline Card
    st.markdown(ENGINE_PIPELINE_HTML, unsafe_allow_html=True)

    # 4. Capabilities and Sources Row
    st.markdown(ENGINE_TWO_COL_HTML, unsafe_allow_html=True)

