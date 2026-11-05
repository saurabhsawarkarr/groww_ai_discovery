# System Architecture Specification: Groww AI-Powered Discovery Engine

> **Document Type:** Technical & System Architecture Specification  
> **Product Context:** Groww · Growth Engineering  
> **Related Documents:** [context.md](file:///d:/SAURABH/Groww%20Discovery%20Engine/context.md) | [Problem Sataement.txt](file:///d:/SAURABH/Groww%20Discovery%20Engine/Problem%20Sataement.txt)  
> **Target Strategic Metric:** 12-Month First-Time Mutual Fund SIP Continuation Rate  

---

## 1. Architectural Philosophy & Design Principles

The Groww AI Discovery Engine is designed not as an autonomous decision-maker or speculative text generator, but as an **auditable, evidence-first research operating system**. Every technical decision is anchored by five fundamental architectural principles:

```mermaid
graph TD
    P1["1. Provenance & Traceability First<br/>Every claim maps deterministically to a verbatim quote & source ID"]
    P2["2. Epistemic Separation of Concerns<br/>Level 1 Evidence ➔ Level 2 Theme ➔ Level 3 Hypothesis ➔ Level 4 Problem"]
    P3["3. Model-Agnostic & Schema-Enforced<br/>Pydantic contracts, deterministic JSON schema & runtime validation"]
    P4["4. Continuous Human-in-the-Loop (HITL)<br/>20-item Golden Set benchmarking, failure logging & active review"]
    P5["5. Zero-PII & Ethical Safeguards<br/>Automated redaction of sensitive info, no advisory recommendations"]

    P1 --- P2 --- P3 --- P4 --- P5
```

1. **Deterministic Traceability:** Any insight presented on an executive dashboard or research summary must be traceable down to the raw public post, timestamp, and verbatim quote substring. Hallucinated quotes break the entire pipeline.
2. **Epistemic Layering:** The architecture strictly isolates *what was said* (evidence) from *how it clusters* (themes), *how it might be explained* (hypotheses), and *what is confirmed by 1:1 user research* (validated problems).
3. **Strict Schema Contracts:** LLMs are never prompted for free-form summaries. All extractions must conform to an immutable 21-field data contract validated via JSON Schema / Pydantic.
4. **Active Quality Auditing:** A built-in evaluation subsystem continuously benchmarks model output against a human-labelled golden dataset across 7 dimensions of agreement.
5. **Zero-PII & Ethical Compliance:** Ingestion pipelines automatically scrub personally identifiable information (PII) including phone numbers, email addresses, PAN cards, and bank account details.

---

## 2. End-to-End System Architecture

The Problem Statement defines exactly **7 pipeline stages** (Collect → Clean → Extract → Discover Patterns → Generate Hypotheses → Compare Opportunities → Evaluate Quality). The diagram below maps these 7 stages plus a **presentation layer** (the PM Research Dashboard) which is not a pipeline stage but the interface through which findings are inspected and reviewed:

```mermaid
flowchart TB
    subgraph INGESTION["1. Data Ingestion & Source Connectors"]
        direction TB
        C1["Google Play Store Adapter<br/>(google-play-scraper / RSS)"]
        C2["Apple App Store Adapter<br/>(app-store-scraper)"]
        C3["Reddit Adapter<br/>(Reddit API / Pushshift / JSON)"]
        C4["YouTube Comments Adapter<br/>(YouTube Data API v3)"]
        C5["Forums & Manual Importer<br/>(TradingQ&A HTML / CSV / JSON)"]
    end

    subgraph PREPROCESSING["2. Cleaning, Deduplication & Qualification Engine"]
        direction TB
        P1["Text Sanitizer & PII Redactor<br/>(Regex / Presidio / PII Scrubber)"]
        P2["Exact Deduplicator<br/>(SHA-256 Text Hashing)"]
        P3["Near-Duplicate Detector<br/>(MinHash LSH / Jaccard > 0.85)"]
        P4["Relevance Classifier<br/>(Zero-Shot / Keyword Rules)"]
        P5["Exclusion Logger<br/>(Logged Reason & Audit Metadata)"]
    end

    subgraph EXTRACTION["3. LLM Extraction & Validation Engine"]
        direction TB
        E1["Extraction Orchestrator<br/>(OpenAI / Claude / Gemini / Local)"]
        E2["Pydantic Schema Validator<br/>(21-Field Evidence Contract)"]
        E3["Verbatim Quote Verifier<br/>(Exact Substring Boundary Match)"]
        E4["Unknown-Value Enforcer<br/>(Strict No-Guess Fallback)"]
    end

    subgraph STORAGE["4. Unified Data & Provenance Layer (SQLite / DuckDB / Postgres)"]
        direction TB
        D1[("raw_conversations")]
        D2[("exclusion_logs")]
        D3[("extracted_evidence")]
        D4[("thematic_clusters")]
        D5[("hypotheses_records")]
        D6[("golden_set_benchmarks")]
        D7[("ai_failure_logs")]
    end

    subgraph PATTERN_ENGINE["5. Pattern Discovery & Semantic Clustering Engine"]
        direction TB
        CL1["Dense Embeddings Generator<br/>(text-embedding-3-small / MiniLM)"]
        CL2["Vector Similarity & Clustering<br/>(HDBSCAN / UMAP / Cosine Graph)"]
        CL3["Cluster Synthesizer LLM<br/>(Title, Description, Counter-Examples)"]
        CL4["Author & Source Aggregator<br/>(Item Count vs Distinct Author)"]
    end

    subgraph HYPOTHESIS_ENGINE["6. Hypothesis Generation & Opportunity Prioritization"]
        direction TB
        H1["Multi-Perspective Generator<br/>(Competing Causal Arguments)"]
        H2["Interview Guide Synthesizer<br/>(Primary Research Questions)"]
        H3["5-Pillar Opportunity Ranker<br/>(Prevalence, Impact, 12M Metric)"]
    end

    subgraph EVALUATION["7. Quality Assurance & Golden Set Benchmarking"]
        direction TB
        Q1["20-Item Golden Set Storage"]
        Q2["7-Dimension Agreement Evaluator"]
        Q3["Automated Failure Logger & Prompt Tuner"]
    end

    subgraph UI_AUDIT["8. Growth PM Research & Audit Dashboard"]
        direction TB
        UI1["Evidence & Verbatim Explorer"]
        UI2["Thematic Cluster & Trend Matrix"]
        UI3["Opportunity Prioritization View"]
        UI4["Golden Set Benchmark & Failure Audit"]
        UI5["Export Center (Deck Slide / CSV / JSON)"]
    end

    %% Pipeline Connections
    INGESTION --> PREPROCESSING
    PREPROCESSING -->|Qualified Raw Corpus| D1
    PREPROCESSING -->|Filtered Out Records| D2
    D1 --> EXTRACTION
    EXTRACTION -->|Validated Evidence Records| D3
    D3 --> PATTERN_ENGINE
    PATTERN_ENGINE -->|Clusters & Counter-Examples| D4
    D4 --> HYPOTHESIS_ENGINE
    HYPOTHESIS_ENGINE -->|Hypotheses & Ranked Opportunities| D5
    
    %% Benchmarking & Human-in-the-Loop
    D3 -.->|Sampling for Benchmarking| Q1
    Q1 --> Q2
    Q2 -->|Agreement Metrics & Deviations| D6
    Q2 -->|Real Model Failures| D7
    D7 -.->|Prompt Optimization Loop| E1

    %% UI Connections
    D3 --> UI1
    D4 --> UI2
    D5 --> UI3
    D6 & D7 --> UI4
    UI1 & UI2 & UI3 & UI4 --> UI5
    UI1 -.->|Human Re-Annotation / Edit| D3
```

---

## 3. Detailed Component Architecture

### 3.1 Data Ingestion Subsystem

The Ingestion Subsystem abstracts source variations into a uniform raw schema.

```mermaid
classDiagram
    class BaseSourceConnector {
        <<abstract>>
        +fetch_raw(query_params: dict) List~RawRecord~
        +validate_credentials() bool
        +get_source_metadata() dict
    }
    class PlayStoreConnector {
        +app_id: str
        +fetch_raw() List~RawRecord~
    }
    class AppStoreConnector {
        +app_id: str
        +fetch_raw() List~RawRecord~
    }
    class RedditConnector {
        +subreddits: List~str~
        +fetch_raw() List~RawRecord~
    }
    class YouTubeConnector {
        +video_ids: List~str~
        +fetch_raw() List~RawRecord~
    }
    class ForumFileConnector {
        +file_path: str
        +fetch_raw() List~RawRecord~
    }

    BaseSourceConnector <|-- PlayStoreConnector
    BaseSourceConnector <|-- AppStoreConnector
    BaseSourceConnector <|-- RedditConnector
    BaseSourceConnector <|-- YouTubeConnector
    BaseSourceConnector <|-- ForumFileConnector
```

#### Raw Record Schema (Ingestion Contract)
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime

class RawRecord(BaseModel):
    raw_id: str = Field(description="Unique deterministic ID (e.g. playstore_com.groww_12345)")
    source_platform: str = Field(description="play_store | app_store | reddit | youtube | forum | manual")
    source_url: Optional[str] = Field(default=None, description="Canonical public URL")
    author_id_hash: Optional[str] = Field(default=None, description="Salted SHA-256 hash of author username")
    published_at: Optional[datetime] = Field(default=None, description="Original publication timestamp")
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_text: str = Field(description="Unprocessed text verbatim from source")
    thread_context: Optional[Dict[str, Any]] = Field(default=None, description="Parent post title, video title, etc.")
    product_context: str = Field(default="unknown", description="groww_specific | category_level | other_product_specific | unknown")
```

---

### 3.2 Preprocessing, Deduplication & Qualification Engine

Raw text passes through a four-phase filter pipeline before reaching any LLM:

```mermaid
flowchart LR
    A["Raw Ingest"] --> B["1. PII Redaction<br/>(Regex / Presidio)"]
    B --> C["2. Exact Hash Deduplication<br/>(SHA-256)"]
    C --> D["3. Near-Duplicate Filter<br/>(MinHash Jaccard > 0.85)"]
    D --> E["4. Relevance Filter<br/>(Mutual Fund / SIP Domain Check)"]
    E -->|Passed| F["Qualified Ingestion Store"]
    E -->|Rejected| G["Exclusion Log Store"]
```

1. **PII Sanitization:**
   * Automated regex and NER masks replace sensitive data:
     * Indian Mobile Numbers: `(?:\+91|91|0)?[6-9]\d{9}` $\rightarrow$ `[REDACTED_PHONE]`
     * Permanent Account Number (PAN): `[A-Z]{5}[0-9]{4}[A-Z]{1}` $\rightarrow$ `[REDACTED_PAN]`
     * Email Addresses: `[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+` $\rightarrow$ `[REDACTED_EMAIL]`
     * Bank Account Numbers / IFSC Codes $\rightarrow$ `[REDACTED_BANK_INFO]`
2. **Deduplication Engine:**
   * **Exact Duplicates:** Normalized lowercase text passed through SHA-256. Exact duplicates are discarded with hit-counts incremented.
   * **Near-Duplicates / Reposts:** MinHash with Locality Sensitive Hashing (LSH) detecting duplicate bot reviews or syndicated cross-posts (Jaccard similarity threshold: $\ge 0.85$).
3. **Relevance Qualification:**
   * Rule-based keyword matching combined with an optional lightweight zero-shot classifier ensures only conversations relevant to **Mutual Funds, SIPs, Recurring Investments, Portfolio Tracking, NAV, and Rupee Cost Averaging** enter the extraction pipeline.
   * Unrelated discussions (e.g., F&O intraday options bugs, US stocks tax queries, general KYC camera crashes) are routed directly to `exclusion_logs` with a descriptive `exclusion_reason`.

---

### 3.3 LLM Extraction Engine & Guardrails

The extraction engine converts unstructured commentary into structured evidence. It guarantees schema conformance and eliminates hallucinations via programmatic guardrails.

```mermaid
sequenceDiagram
    participant Orch as Extraction Orchestrator
    participant LLM as Foundation Model
    participant Val as Pydantic Validator
    participant Sub as Substring Guardrail
    participant DB as Evidence Store

    Orch->>LLM: Send Qualified Record + Schema System Prompt
    LLM-->>Orch: Return Structured JSON
    Orch->>Val: Validate against 21-Field Evidence Schema
    alt Validation Error
        Val-->>Orch: Schema Exception
        Orch->>LLM: Retry with Error Feedback (Max 2 Retries)
    else Validation Success
        Val-->>Sub: Validate evidence_quote
        alt Substring NOT in raw_text
            Sub-->>Orch: Hallucination Flagged!
            Orch->>LLM: Re-prompt forcing exact quote
        else Substring Matches
            Sub-->>DB: Commit EvidenceRecord
        end
    end
```

#### Core Evidence Data Model (Pydantic Implementation)
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime
import uuid

class EvidenceRecord(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = Field(description="Foreign key to raw_conversations.raw_id")
    source_platform: Literal["play_store", "app_store", "reddit", "youtube", "forum", "other"]
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    product_context: Literal["groww_specific", "category_level", "other_product_specific", "unknown"]
    investor_context: Optional[str] = Field(default=None, description="Explicit stated background")
    journey_stage: Literal[
        "before_starting", "newly_started", "continuing", 
        "considering_change", "paused", "stopped", "unknown"
    ] = "unknown"
    motivation: Optional[str] = None
    expectation: Optional[str] = None
    trigger_or_situation: Optional[str] = None
    reported_behaviour: str = Field(description="Explicit action or habit described")
    friction_or_concern: Optional[str] = None
    monitoring_behaviour: Optional[str] = None
    workaround: Optional[str] = None
    reported_outcome: Optional[str] = None
    evidence_quote: str = Field(description="Shortest verbatim substring supporting the extraction")
    evidence_type: Literal["explicitly_stated", "inferred", "unknown"] = "explicitly_stated"
    missing_information: List[str] = Field(default_factory=list)
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    review_status: Literal["unreviewed", "accepted", "corrected", "rejected"] = "unreviewed"

    @validator("evidence_quote")
    def quote_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError("evidence_quote must be an explicit, non-empty excerpt")
        return v
```

#### Substring Verification Algorithm
```python
def verify_verbatim_quote(raw_text: str, evidence_quote: str) -> bool:
    """
    Guarantees zero model hallucination in evidence quotes.
    Normalizes whitespace and checks for exact substring existence.
    """
    clean_raw = " ".join(raw_text.split()).lower()
    clean_quote = " ".join(evidence_quote.split()).lower()
    return clean_quote in clean_raw
```

---

### 3.4 Pattern Discovery & Semantic Clustering Engine

The system uses an unsupervised bottom-up clustering pipeline to discover recurring behavioural patterns without pre-selecting themes:

```mermaid
flowchart TD
    E1["Extracted Evidence Records"] --> E2["Feature Vectorizer<br/>(Text: reported_behaviour + friction_or_concern)"]
    E2 --> E3["Embeddings Generation<br/>(e.g., text-embedding-3-small)"]
    E3 --> E4["Dimensionality Reduction<br/>(UMAP to 5-10 Dimensions)"]
    E4 --> E5["Density-Based Clustering<br/>(HDBSCAN / Cosine Clustering)"]
    E5 --> E6["Cluster Aggregation<br/>(Collect Members, Authors, Sources)"]
    E6 --> E7["Theme Synthesis LLM<br/>- Synthesizes Title & Summary<br/>- Identifies Outliers & Counter-Examples"]
    E7 --> E8["Thematic Cluster Record"]
```

#### Aggregation Metrics per Cluster
* **Dataset Prevalence ($P$):** $\frac{\text{Records in Cluster}}{\text{Total Qualified Records}} \times 100\%$
* **Unique Voice Ratio ($UVR$):** $\frac{\text{Distinct Authors in Cluster}}{\text{Total Records in Cluster}}$ (detects single-user review bombing)
* **Cross-Source Dispersion:** Entropy across source platforms ensuring patterns are not platform artifacts.
* **Counter-Evidence Identification:** Negative semantic distance queries identify users experiencing similar triggers who did *not* develop the friction.

---

### 3.5 Hypothesis Generation & Opportunity Prioritization Engine

To transition from observations to actionable research, the engine generates competing hypotheses and prioritizes opportunities using a transparent multi-dimensional rubric.

```mermaid
flowchart LR
    subgraph THEME["Validated Cluster"]
        T1["Theme: Confusion Interpreting Negative XIRR in M1-M3"]
    end

    subgraph DUAL_HYPOTHESIS["Multi-Perspective Generation"]
        H_A["Hypothesis A (Loss-Aversion):<br/>Users interpret early negative XIRR as capital loss, triggering voluntary autopay cancellation."]
        H_B["Hypothesis B (Information Curiosity):<br/>Users seek YouTube explanations out of curiosity without intending to alter contributions."]
    end

    subgraph INTERVIEW_GEN["Targeted Primary Inquiries"]
        Q1["'Walk me through the last time you checked your portfolio when returns were in red.'"]
        Q2["'What did you expect XIRR to show in your first 90 days?'"]
    end

    THEME --> H_A & H_B
    H_A & H_B --> INTERVIEW_GEN
```

#### The 5-Pillar Opportunity Prioritization Rubric
Each opportunity area $O_i$ receives a transparent qualitative & quantitative score:

$$S(O_i) = w_1 P(O_i) + w_2 I(O_i) + w_3 R_{12M}(O_i) + w_4 Q(O_i) + w_5 A(O_i)$$

Where:
* $P(O_i)$ (**Prevalence**): Proportion of unique authors reporting this pattern in the dataset.
* $I(O_i)$ (**User Impact Severity**): Degree of anxiety or friction expressed (scored from 1 to 5).
* $R_{12M}(O_i)$ (**Relevance to 12M Metric**): Plausible causal relationship with maintaining an active SIP (1 to 5).
* $Q(O_i)$ (**Evidence Quality & Diversity**): Multi-platform corroboration and presence of counter-evidence.
* $A(O_i)$ (**Product Addressability**): Feasibility of solving via Groww UX/Product mechanisms.

> **Important:** The Problem Statement (§10) explicitly states: *"Initially, the system should compare opportunities qualitatively and show the evidence behind each assessment. Avoid assigning arbitrary numerical scores until the criteria and scoring definitions are defensible."* The formula above is an **aspirational target** for later iterations. The V1 implementation must use **qualitative comparison with transparent evidence** rather than opaque numerical ranking.

---

### 3.6 Quality Assurance, Benchmarking & Golden Set Subsystem

This subsystem satisfies the core requirement for an auditable **AI Evidence Log** containing a human-labelled **Golden Set of ~20 items**.

```mermaid
flowchart TD
    subgraph GOLDEN_SET["Golden Dataset (20 Curated Items)"]
        G1["Item 01 (Short Review)"]
        G2["Item 02 (Long Context Post)"]
        G3["Item 03 (Ambiguous Intent)"]
        G4["..."]
        G20["Item 20 (Counter-Example)"]
    end

    subgraph DUAL_EVAL["Parallel Annotation Comparison"]
        H_ANN["Human Ground Truth Labels<br/>(Pre-annotated independently)"]
        M_ANN["Model Extraction Output<br/>(Live run against current prompt)"]
    end

    subgraph METRIC_ENGINE["7-Dimension Agreement Engine"]
        M1["Relevance Agreement %"]
        M2["Quote Exact-Match %"]
        M3["Behaviour & Friction Semantic %"]
        M4["Journey Stage Precision %"]
        M5["Workaround & Outcome Recall %"]
        M6["Zero-Hallucination Rate %"]
        M7["Source Traceability (100% Target)"]
    end

    subgraph FAILURE_LOG["AI Failure Logger"]
        F1["Log Discrepancy"]
        F2["Root-Cause Diagnostic"]
        F3["Prompt / Schema Remediation"]
    end

    GOLDEN_SET --> H_ANN & M_ANN
    H_ANN & M_ANN --> METRIC_ENGINE
    METRIC_ENGINE -->|Field Mismatches| FAILURE_LOG
```

---

## 4. Storage Architecture & Database Schema

The system uses an embedded, zero-maintenance relational engine (**SQLite / DuckDB**) for local execution and pilot testing, which cleanly scales to **PostgreSQL** for multi-user production deployments.

```mermaid
erDiagram
    RAW_CONVERSATIONS ||--o{ EXCLUSION_LOGS : "logs exclusions"
    RAW_CONVERSATIONS ||--o{ EXTRACTED_EVIDENCE : "yields"
    EXTRACTED_EVIDENCE }o--o{ CLUSTER_MAPPINGS : "belongs to"
    THEMATIC_CLUSTERS ||--o{ CLUSTER_MAPPINGS : "groups"
    THEMATIC_CLUSTERS ||--o{ HYPOTHESIS_RECORDS : "generates"
    RAW_CONVERSATIONS ||--o{ GOLDEN_SET_BENCHMARKS : "sampled in"
    GOLDEN_SET_BENCHMARKS ||--o{ AI_FAILURE_LOGS : "records failures"

    RAW_CONVERSATIONS {
        string raw_id PK
        string source_platform
        string source_url
        string author_id_hash
        timestamp published_at
        timestamp collected_at
        text raw_text
        json thread_context
        string product_context
        boolean is_qualified
    }

    EXCLUSION_LOGS {
        string exclusion_id PK
        string raw_id FK
        string reason
        timestamp excluded_at
    }

    EXTRACTED_EVIDENCE {
        string evidence_id PK
        string raw_id FK
        string journey_stage
        text motivation
        text expectation
        text trigger_or_situation
        text reported_behaviour
        text friction_or_concern
        text monitoring_behaviour
        text workaround
        text reported_outcome
        text evidence_quote
        string evidence_type
        json missing_information
        float extraction_confidence
        string review_status
        timestamp created_at
    }

    THEMATIC_CLUSTERS {
        string cluster_id PK
        string title
        text description
        int item_count
        int distinct_authors_count
        json source_distribution
        json counter_evidence_quotes
        timestamp created_at
    }

    CLUSTER_MAPPINGS {
        string mapping_id PK
        string cluster_id FK
        string evidence_id FK
        float similarity_score
    }

    HYPOTHESIS_RECORDS {
        string hypothesis_id PK
        string cluster_id FK
        text observed_pattern
        text hypothesis_text
        text alternative_explanation
        text missing_evidence
        text connection_to_continuation
        text validation_approach
        json research_questions
        float priority_score
        timestamp created_at
    }

    GOLDEN_SET_BENCHMARKS {
        string benchmark_id PK
        string raw_id FK
        json human_labels
        json model_labels
        float agreement_score
        timestamp evaluated_at
    }

    AI_FAILURE_LOGS {
        string failure_id PK
        string benchmark_id FK
        string failure_type
        text raw_input
        text erroneous_model_output
        text ground_truth_correction
        text remediation_applied
        timestamp logged_at
    }
```

---

## 5. PM Audit & Research Dashboard Architecture

The frontend provides the Growth PM with a clean, evidence-backed workspace for exploring findings, inspecting audits, and exporting deliverables.

```mermaid
graph TD
    subgraph UI_VIEWS["Research Dashboard UI Modules"]
        V1["1. Evidence Explorer<br/>- Filter by journey stage & platform<br/>- Clickable source URLs & quote highlights"]
        V2["2. Cluster & Theme Explorer<br/>- Semantic cluster visualization<br/>- Supporting vs. counter-evidence panels"]
        V3["3. Opportunity Matrix<br/>- 5-Pillar priority quadrant chart<br/>- Direct linkage to 12M SIP retention"]
        V4["4. Golden Set & Audit Center<br/>- 7-Dimension agreement gauges<br/>- Failure case analysis & prompt inspector"]
        V5["5. Export & Deliverable Generator<br/>- Single-slide executive summary deck<br/>- Comprehensive CSV / JSON Evidence Log"]
    end
```

### Dashboard Interaction Contract
1. **Auditable Click-Through:** Selecting any bar in a theme frequency chart immediately isolates the supporting records, showing original quotes alongside platform links.
2. **Interactive Review:** PMs can manually toggle `review_status` (`accepted`, `corrected`, `rejected`) directly within the UI, triggering real-time re-clustering.
3. **One-Slide Deck Generator:** Automates Deliverable 4 by generating a pre-formatted SVG / PDF slide summarizing the ingestion volumes, top 3 emergent themes, competing hypotheses, and next-step interview questions.

---

## 6. Security, Privacy & Advisory Safeguards

| Domain | Threat / Risk | Enforced Architectural Safeguard |
|---|---|---|
| **Privacy & PII** | Leakage of user phone numbers, emails, PAN cards, or portfolio values from public screenshots/text. | Ingestion-level regex sanitization and Presidio NER scrubbers strip all PII before database storage or LLM submission. |
| **Platform Compliance** | IP blocking or ToS violations from automated scraping. | Connectors adhere to rate limits, robots.txt directives, caching headers, and support local offline CSV/JSON imports. |
| **Investment Advice Boundary** | Engine outputs fund recommendations or stock picks. | System prompt system guards forbid financial advisory generation; system operates strictly as an analytical UX research tool. |
| **Dark Patterns** | Recommending FOMO, artificial urgency, or anxiety-inducing nudges. | Hardcoded prompt constraints reject any retention strategy involving artificial countdowns, deceptive cancellation flows, or guilt messaging. |

---

## 7. Directory & Project Structure

The project is structured modularly for maintainability and clear separation of concerns:

```text
Groww-Discovery-Engine/
├── context.md                          # Comprehensive problem context & specification
├── architecture.md                     # System architecture specification (this document)
├── Problem Sataement.txt               # Source assignment document
├── pyproject.toml / requirements.txt   # Python dependency specifications
├── configs/
│   ├── config.yaml                     # Pipeline parameters, model selection, thresholds
│   └── pii_patterns.json               # Regex patterns for phone, PAN, email sanitization
├── data/
│   ├── raw/                            # Ingested, unedited source files (JSON / CSV)
│   ├── processed/                      # Normalized, deduplicated, qualified datasets
│   ├── golden_set/                     # 20 human-labelled benchmark items
│   └── database/                       # Local SQLite / DuckDB storage files
├── src/
│   ├── __init__.py
│   ├── connectors/                     # Ingestion adapters
│   │   ├── base.py                     # BaseSourceConnector abstract class
│   │   ├── play_store.py               # Google Play Store scraper / adapter
│   │   ├── app_store.py                # Apple App Store adapter
│   │   ├── reddit.py                   # Reddit API / Pushshift connector
│   │   ├── youtube.py                  # YouTube Data API comments connector
│   │   └── file_importer.py            # Local CSV / JSON / Excel loader
│   ├── preprocessing/                  # Data cleaning & qualification
│   │   ├── sanitizer.py                # PII masking & text normalization
│   │   ├── deduplicator.py             # SHA-256 & MinHash LSH deduplication
│   │   └── qualifier.py                # Relevance classifier & exclusion logger
│   ├── extraction/                     # LLM evidence extraction
│   │   ├── models.py                   # Pydantic 21-Field EvidenceRecord schema
│   │   ├── prompts.py                  # Structured extraction prompt templates
│   │   ├── orchestrator.py             # LLM API caller with retry logic
│   │   └── guardrails.py               # Substring verbatim quote verification
│   ├── clustering/                     # Semantic pattern discovery
│   │   ├── embedder.py                 # Vector embedding generator
│   │   ├── clusterer.py                # HDBSCAN / UMAP clustering
│   │   └── synthesizer.py              # LLM theme naming & counter-evidence finder
│   ├── hypotheses/                     # Hypotheses & prioritization
│   │   ├── generator.py                # Multi-perspective hypothesis synthesizer
│   │   └── ranker.py                   # 5-Pillar opportunity scoring algorithm
│   ├── evaluation/                     # Golden set benchmarking
│   │   ├── benchmark.py                # 7-dimension agreement evaluator
│   │   └── failure_logger.py           # Automated failure recorder & report generator
│   └── ui/                             # PM audit & exploration interface
│       ├── app.py                      # Web application entry point (Streamlit / FastAPI)
│       ├── components/                 # UI views (Explorer, Clusters, Golden Set)
│       └── exporter.py                 # Findings & Evidence Log export utilities
└── tests/
    ├── test_connectors.py
    ├── test_deduplicator.py
    ├── test_guardrails.py
    ├── test_schema_validation.py
    └── test_evaluator.py
```

---

## 8. Phased Implementation Roadmap

```mermaid
gantt
    title Groww Discovery Engine: Implementation Roadmap
    dateFormat  YYYY-MM-DD
    section Phase 1: Core Engine
    Data Contracts & Pydantic Schemas       :done,    des1, 2026-10-23, 2d
    Connectors (Play Store & Reddit)       :active,  des2, after des1, 3d
    Preprocessing & PII Redaction Pipeline :         des3, after des2, 2d
    section Phase 2: AI Pipeline
    LLM Extraction & Quote Verification    :         des4, after des3, 3d
    20-Item Golden Set Curation & Eval     :         des5, after des4, 2d
    Failure Mode Logging & Prompt Tuning   :         des6, after des5, 2d
    section Phase 3: Analytics & PM UI
    Semantic Clustering & Theme Synthesis  :         des7, after des6, 3d
    Hypothesis Generator & 5-Pillar Ranker :         des8, after des7, 2d
    PM Audit Dashboard & Deck Exporter     :         des9, after des8, 3d
```

### Milestone Milestones
* **Milestone 1 (Data Foundation):** Ingest 100–200 pilot comments, run through PII redaction and deduplication, and export clean records.
* **Milestone 2 (Auditable Extraction):** Extract structured records using LLM with 100% passing substring verification on quotes.
* **Milestone 3 (Golden Set Benchmark):** Evaluate against 20 human-labelled items, document failure cases, and tune prompts.
* **Milestone 4 (End-to-End Synthesis):** Cluster verified records, generate competing hypotheses, rank opportunities, and generate Deliverables 1–4.
