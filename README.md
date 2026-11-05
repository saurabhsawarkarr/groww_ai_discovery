# 🌱 Groww Discovery Engine

> **AI-Powered Qualitative Research Operating System for Mutual Fund SIP Continuation**  
> **Strategic Metric:** 12-Month Active SIP Retention Rate among First-Time Investors  
> **Corpus Scope:** 32,547 Harvested Conversations &bull; 3,052 Clean Qualified Records &bull; 7 Discovered Themes &bull; 16 Competing Hypotheses &bull; 3 Tier-1 Growth Bets  
> **Repository:** [https://github.com/saurabhsawarkarr/groww_ai_discovery](https://github.com/saurabhsawarkarr/groww_ai_discovery)

---

## 📌 Executive Overview

The **Groww Discovery Engine** is an auditable, evidence-first qualitative customer intelligence platform built for Growth Product Managers and Engineering leaders. It addresses the core problem of **first-time mutual fund investor drop-off within the first 12 months** by transforming fragmented public discourse across 5 distinct channels into structured, decision-ready behavioral insights.

### 🎯 Key Performance Indicators (Corpus & Performance)
* **Total Harvested Records:** 32,547 conversations (Google Play Store, Apple App Store, Reddit, YouTube, Investing Forums)
* **Clean Qualified Dataset:** 3,052 verified mutual fund & SIP conversations
* **Emergent Problem Themes:** 7 empirical failure modes (prevalence ranging from 3.2% to 18.0%)
* **Strategic Growth Bets:** 3 Tier-1 high-leverage product bets (+18% to +25% projected 12M SIP continuation lift)
* **AI Agreement Benchmark:** 7-dimension Golden Set evaluation with automated failure logging

---

## 🏛️ System Architecture

The engine operates across 7 deterministic pipeline stages plus an executive dashboard:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        GROWW DISCOVERY ENGINE ARCHITECTURE                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  1. Multi-Channel Ingestion (32.5k+ Discourse Records)                                │
│     ├── Google Play Store (27.1k) &bull; Apple App Store (522)                         │
│     └── YouTube Comments (3.7k) &bull; Reddit (574) &bull; ValuePickr/Forums (588)     │
│                                                                                        │
│  2. Qualification, Normalization & Zero-PII Scrubber                                   │
│     ├── Inverted prefix shingle deduplication &bull; Strict MF/SIP qualification       │
│     └── Automated PII redaction (PAN, account numbers, phone, email)                   │
│                                                                                        │
│  3. Structured Evidence Extraction (21-Field Pydantic Contracts)                       │
│     └── Exact verbatim quote spans, sentiment, emotional polarity, channel lineage    │
│                                                                                        │
│  4. Unsupervised Thematic Clustering & Pattern Discovery                               │
│     └── 7 empirical clusters mapped across the 4 Secondary Research Findings           │
│                                                                                        │
│  5. Dual Competing Hypotheses & Opportunity Synthesis                                 │
│     └── 5-pillar prioritization rubric & 1:1 primary user interview protocols          │
│                                                                                        │
│  6. Interactive Qualitative RAG Assistant                                              │
│     └── Hybrid BM25 + dense vector retrieval with pluggable LLM adapters (Gemini/Groq) │
│                                                                                        │
│  7. Golden Set Quality Auditing & AI Failure Center                                    │
│     └── 20-item expert benchmark across 7 agreement dimensions                         │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Discovered Themes & The 4 Secondary Research Findings

All 7 discovered empirical themes map cleanly under the 4 initial secondary research assumptions:

| # | Discovered Theme Title | Corpus Count | Share | Aligned Secondary Finding |
|:---:|:---|:---:|:---:|:---|
| **1** | **Cash-Flow Timing Mismatches & Autopay Deduction Drops** | 548 | **18.0%** | **Finding #3:** Lack of Emergency Funds |
| **2** | **Goal-Deficient Over-Diversification & Portfolio Clutter** | 284 | **9.3%** | **Finding #2:** Not Setting Financial Goals |
| **3** | **Emergency Buffer Deficit & The ECS Bounce Penalty Trap** | 200 | **6.6%** | **Finding #3:** Lack of Emergency Funds |
| **4** | **Early Drawdown Panic & Volatility Shock (Months 1–3)** | 181 | **5.9%** | **Finding #1:** Market Fluctuations |
| **5** | **Unrealistic Growth Expectations & XIRR Distortion** | 193 | **6.3%** | **Finding #4:** Unrealistic Return Expectations |
| **6** | **Price-Fluctuation Uncertainty during NAV Settlement Lag** | 163 | **5.3%** | **Finding #1:** Market Fluctuations |
| **7** | **Milestone Disconnect vs. Goal-Anchored Discipline** | 98 | **3.2%** | **Finding #2:** Not Setting Financial Goals |

---

## 🚀 The 3 Tier-1 Growth Bets

1. **🛡️ Bet 1: Autopay Mandate Resilience & Bounce Shield** (Addressing Finding #3)
   * 24h Pre-debit balance check prompts & 1-click zero-penalty manual UPI retry fallback.
   * Projected 12-Month Lift: **+8.5% to +11.0%** continuation rate.
2. **📉 Bet 2: Novice Volatility Pacing Shield & Accumulation Framing** (Addressing Findings #1 & #4)
   * Units Accumulated milestone view, tenor-sensitive annualized XIRR suppression in first 90 days.
   * Projected 12-Month Lift: **+5.5% to +7.2%** continuation rate.
3. **🎯 Bet 3: Portfolio Hygiene & Multi-SIP Decluttering X-Ray** (Addressing Finding #2)
   * Overlap detector for user's existing funds & payday-synchronized unified SIP debit.
   * Projected 12-Month Lift: **+4.0% to +6.5%** continuation rate.

---

## 📸 Screenshots & Master PDF Deliverable

A single comprehensive PDF deliverable containing ultra-crisp screenshots of all views is available in the root repository:
* 📄 **[Download Master PDF: `ss of all page.pdf`](./ss%20of%20all%20page.pdf)**

### Captured Views:
* `page_screenshots/01_overview.png` — Executive KPI Suite & Discovery Pipeline
* `page_screenshots/02_failure_themes.png` — 7 Discovered Thematic Clusters
* `page_screenshots/03_user_segments.png` — 4 First-Year Investor Journey Cohorts
* `page_screenshots/04_opportunity_matrix_bet1.png` — 5-Pillar Rubric & Bet 1 (Autopay)
* `page_screenshots/05_opportunity_matrix_bet2.png` — 5-Pillar Rubric & Bet 2 (Volatility)
* `page_screenshots/06_opportunity_matrix_bet3.png` — 5-Pillar Rubric & Bet 3 (Portfolio Hygiene)
* `page_screenshots/07_rag_assistant.png` — Qualitative RAG Research Assistant
* `page_screenshots/08_engine_info.png` — Architecture Stepper & Golden Set Benchmark Audit
* `page_screenshots/09_solution_1_accumulation_lens.png` — Solution 1 UI Slide
* `page_screenshots/10_solution_2_milestone_shield.png` — Solution 2 UI Slide
* `page_screenshots/11_solution_3_cycle_time_machine.png` — Solution 3 UI Slide
* `page_screenshots/12_solution_4_volatility_buffer.png` — Solution 4 UI Slide
* `page_screenshots/13_solution_5_confidence_checkin.png` — Solution 5 UI Slide

---

## 🛠️ Quickstart & Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/saurabhsawarkarr/groww_ai_discovery.git
cd groww_ai_discovery
```

### 2. Set Up Python Virtual Environment
```bash
# Recommended Python version: 3.11
python -m venv .venv

# Activate on Windows:
.\.venv\Scripts\activate

# Activate on macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and insert your API keys:
```bash
cp .env.example .env
```
*(Optional LLM Keys: `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`)*

### 5. Launch the Local Application
```bash
python run_app.py
```
Open your browser at **`http://127.0.0.1:8501`** to access the live dashboard.

---

## 📂 Project Directory Structure

```
groww_ai_discovery/
├── configs/                     # System & pipeline YAML configuration
├── data/                        # Datasets, SQLite DB, processed JSON
│   ├── database/discovery_engine.db
│   ├── processed/               # Extracted themes & hypotheses
│   └── raw/                     # Raw harvested multi-source conversations
├── deliverables/                # Executive findings, logs & slide presentations
├── page_screenshots/            # High-resolution 4K captures of all UI views
├── scripts/                     # Data harvesting, clustering & analysis scripts
├── src/
│   ├── clustering/              # Unsupervised theme clustering
│   ├── database/                # SQLite connection & schema management
│   ├── evaluation/              # Golden set benchmark & failure logging
│   ├── extraction/              # Pydantic structured evidence extractors
│   ├── hypotheses/              # 5-pillar opportunity ranker & LLM synthesis
│   ├── ingestion/               # Multi-source scraper connectors
│   ├── rag/                     # Hybrid BM25 + Vector evidence retriever
│   └── ui/                      # Streamlit application & interactive components
│       ├── app.py               # Main navigation router
│       └── components/          # Views: Overview, Themes, Segments, Matrix, RAG, Info
├── tests/                       # Unit and integration test suite
├── .env.example                 # Environment template
├── .gitignore                   # Version control ignore rules
├── requirements.txt             # Project dependencies
├── run_app.py                   # Streamlit server launcher
├── ss of all page.pdf           # Master PDF with all page screenshots
└── README.md                    # Documentation
```

---

## ⚖️ Regulatory & Ethical Guardrails

* **Zero-PII Compliance:** Automated regex & scrubber pipeline strips all PAN numbers, account numbers, phone numbers, and full names before database insertion.
* **SEBI Zero-Advice Mandate:** The engine enforces strict neutrality guardrails. It never recommends specific mutual fund schemes, fund houses, or asset allocation tips.
* **Deterministic Traceability:** Every hypothesis and synthesized opportunity directly links back to genuine, verbatim customer statements stored in the SQLite evidence repository.

---

**Developed for the Groww Growth Engineering & Product Strategy Team.**
