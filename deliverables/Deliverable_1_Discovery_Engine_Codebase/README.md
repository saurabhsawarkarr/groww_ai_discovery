# Deliverable 1: Groww AI-Powered Discovery Engine

> **Project:** Senior PM Discovery Assignment — Mutual Fund SIP 12-Month Retention  
> **Strategic Metric:** 12-Month First-Time Mutual Fund SIP Continuation Rate  
> **Architecture Standard:** 7-Stage Pipeline with Zero-Hallucination Extraction & TDD Benchmark Gate  
> **Package Date:** October 26, 2026

---

## 1. Executive Summary & Engine Overview

The **Groww AI-Powered Discovery Engine** is an enterprise-grade qualitative research platform that systematically harvests, sanitizes, extracts, clusters, and prioritizes user friction and behavioral patterns from public discourse (Play Store, App Store, Reddit, YouTube) without anchoring on preconceived biases.

Built to address the strategic challenge of improving **12-month mutual fund SIP continuation**, the engine operates under strict epistemic guardrails:
1. **100% Verbatim Quote Exactness:** Rejects any hallucinated or paraphrased text. Every evidence quote is verified as an exact contiguous substring of the raw post.
2. **Epistemic Humility (§9.4):** Explicitly marks unstated demographics as `unknown`. Never fabricates investor segments.
3. **Contradictory Counter-Evidence:** Uncovers resilient investors who continued their SIP despite experiencing the same friction.
4. **Transparent 5-Pillar Prioritization:** Qualitatively evaluates candidate opportunities across Prevalence, User Impact, 12M SIP Relevance, Evidence Quality, and Product Addressability.

---

## 2. Quickstart & Single CLI Execution

### 2.1 Prerequisites & Installation
Ensure Python 3.10+ is installed:

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

### 2.2 End-to-End Pipeline Execution (Single Command)
Execute the complete 7-stage workflow — from ingestion and sanitization through clustering, hypothesis synthesis, and deliverables export:

```bash
python run_pipeline.py
```

Optional CLI flags:
```bash
python run_pipeline.py --help
# Options:
#   --skip-ingestion   Use existing SQLite dataset without re-harvesting
#   --db-path PATH     Custom SQLite database location
#   --output-dir DIR   Output folder for generated deliverables (default: deliverables/)
#   --verbose          Enable verbose debug logging
```

### 2.3 Interactive Streamlit Research Dashboard
Launch the Growth PM research workspace for quote inspection and human-in-the-loop review:

```bash
streamlit run src/ui/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser:
- **Tab 1 (Evidence Explorer):** Search and filter 155+ qualified records by platform and journey stage with 1-click quote traceability to raw URLs.
- **Tab 2 (Thematic Clusters):** Interactive radar and prevalence distribution across 8 emergent behavioral themes with counter-evidence quotes.
- **Tab 3 (Opportunity Matrix):** 5-pillar qualitative evaluation matrix and semi-structured 1:1 user interview protocol generators.
- **Tab 4 (Golden Set & Audit):** 7-dimension agreement benchmark, live Golden Set inspection, and diagnostic AI failure logs.

---

## 3. Test Suite Verification

Run the automated test suite covering all 8 pipeline modules:

```bash
pytest -v
```
All tests enforce strict data contracts, Pydantic validation schemas, exact substring guardrails, and deterministic scoring.

---

## 4. Repository Structure & Module Architecture

```text
Deliverable_1_Discovery_Engine_Codebase/
├── run_pipeline.py                 # Single root CLI entry point
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project packaging specifications
├── configs/
│   ├── config.yaml                 # Pipeline hyperparameters & weights
│   └── pii_patterns.json           # Regex patterns for PII scrubbing
├── data/
│   └── golden_set/                 # 20-item human ground-truth benchmark
├── src/
│   ├── connectors/                 # Play Store, App Store, Reddit, YouTube, CSV
│   ├── preprocessing/              # PII masking, SHA-256 deduplication, qualification
│   ├── extraction/                 # 21-field Pydantic schema & substring guardrail
│   ├── evaluation/                 # 7 agreement metrics & diagnostic failure logger
│   ├── clustering/                 # Embeddings, UMAP projection & HDBSCAN themes
│   ├── hypotheses/                 # Competing hypotheses (A/B) & 5-pillar ranker
│   ├── ui/                         # Streamlit Growth PM dashboard
│   ├── database/                   # SQLite connection & 8-table relational schema
│   └── exporter/                   # Deliverables synthesis & export center
└── tests/                          # 65+ unit & integration test suite
```

---

## 5. Artifact Manifest & Verification

| Deliverable | File Path | Format | Description |
|---|---|:---:|---|
| **Deliverable 1** | `Deliverable_1_Discovery_Engine_Codebase/` | Package | Fully runnable discovery engine with root CLI |
| **Deliverable 2** | `Deliverable_2_Discovery_Findings.md` | Markdown | Comprehensive findings, 8 themes, hypotheses |
| **Deliverable 3** | `Deliverable_3_AI_Evidence_Log.md` | Markdown | Golden Set audit, 7 agreement metrics, failure logs |
| **Deliverable 4** | `Deliverable_4_One_Slide_Workflow.pdf` | PDF / SVG | 16:9 executive workflow slide for final presentation |

---
*Developed for Groww Growth Engineering & Product Teams.*
