-- ====================================================================
-- Groww AI-Powered Discovery Engine: SQLite Schema Specification
-- Corresponds to Architecture Specification Section 4
-- ====================================================================

PRAGMA foreign_keys = ON;

-- 1. RAW CONVERSATIONS (Ingested, normalized public discussions)
CREATE TABLE IF NOT EXISTS raw_conversations (
    raw_id TEXT PRIMARY KEY,
    source_platform TEXT NOT NULL,
    source_url TEXT,
    author_id_hash TEXT,
    published_at TIMESTAMP,
    collected_at TIMESTAMP NOT NULL,
    raw_text TEXT NOT NULL,
    thread_context TEXT,  -- JSON string containing parent post, thread title, video metadata
    product_context TEXT DEFAULT 'unknown',  -- groww_specific | category_level | other_product_specific | unknown
    is_qualified INTEGER DEFAULT 0  -- Boolean flag: 0 = excluded / unqualified, 1 = qualified
);

CREATE INDEX IF NOT EXISTS idx_raw_conv_platform ON raw_conversations(source_platform);
CREATE INDEX IF NOT EXISTS idx_raw_conv_qualified ON raw_conversations(is_qualified);
CREATE INDEX IF NOT EXISTS idx_raw_conv_author ON raw_conversations(author_id_hash);

-- 2. EXCLUSION LOGS (Auditable drop record for non-SIP or spam discussions)
CREATE TABLE IF NOT EXISTS exclusion_logs (
    exclusion_id TEXT PRIMARY KEY,
    raw_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    excluded_at TIMESTAMP NOT NULL,
    FOREIGN KEY (raw_id) REFERENCES raw_conversations(raw_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exclusion_raw_id ON exclusion_logs(raw_id);

-- 3. EXTRACTED EVIDENCE (21-field structured behavioral observations)
CREATE TABLE IF NOT EXISTS extracted_evidence (
    evidence_id TEXT PRIMARY KEY,
    raw_id TEXT NOT NULL,
    investor_context TEXT,  -- Explicit stated background (e.g. 22yo engineer, first job)
    journey_stage TEXT DEFAULT 'unknown',  -- before_starting | newly_started | continuing | considering_change | paused | stopped | unknown
    motivation TEXT,
    expectation TEXT,
    trigger_or_situation TEXT,
    reported_behaviour TEXT NOT NULL,
    friction_or_concern TEXT,
    monitoring_behaviour TEXT,
    workaround TEXT,
    reported_outcome TEXT,
    evidence_quote TEXT NOT NULL,
    evidence_type TEXT DEFAULT 'explicitly_stated',  -- explicitly_stated | inferred | unknown
    missing_information TEXT,  -- JSON array of attributes not explicitly mentioned
    extraction_confidence REAL NOT NULL DEFAULT 1.0,
    review_status TEXT DEFAULT 'unreviewed',  -- unreviewed | accepted | corrected | rejected
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (raw_id) REFERENCES raw_conversations(raw_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evidence_raw_id ON extracted_evidence(raw_id);
CREATE INDEX IF NOT EXISTS idx_evidence_stage ON extracted_evidence(journey_stage);
CREATE INDEX IF NOT EXISTS idx_evidence_review ON extracted_evidence(review_status);

-- 4. THEMATIC CLUSTERS (Unsupervised emergent behavioral clusters)
CREATE TABLE IF NOT EXISTS thematic_clusters (
    cluster_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    item_count INTEGER DEFAULT 0,
    distinct_authors_count INTEGER DEFAULT 0,
    source_distribution TEXT,  -- JSON object mapping source_platform -> item count
    counter_evidence_quotes TEXT,  -- JSON array of counter-example verbatim strings
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_clusters_created ON thematic_clusters(created_at);

-- 5. CLUSTER MAPPINGS (Evidence items mapped to thematic clusters)
CREATE TABLE IF NOT EXISTS cluster_mappings (
    mapping_id TEXT PRIMARY KEY,
    cluster_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    similarity_score REAL,
    FOREIGN KEY (cluster_id) REFERENCES thematic_clusters(cluster_id) ON DELETE CASCADE,
    FOREIGN KEY (evidence_id) REFERENCES extracted_evidence(evidence_id) ON DELETE CASCADE,
    UNIQUE(cluster_id, evidence_id)
);

CREATE INDEX IF NOT EXISTS idx_mappings_cluster ON cluster_mappings(cluster_id);
CREATE INDEX IF NOT EXISTS idx_mappings_evidence ON cluster_mappings(evidence_id);

-- 6. HYPOTHESIS RECORDS (Competing falsifiable causal explanations & interview guides)
CREATE TABLE IF NOT EXISTS hypothesis_records (
    hypothesis_id TEXT PRIMARY KEY,
    cluster_id TEXT NOT NULL,
    observed_pattern TEXT NOT NULL,
    hypothesis_text TEXT NOT NULL,
    alternative_explanation TEXT,
    missing_evidence TEXT,
    connection_to_continuation TEXT,
    validation_approach TEXT,
    research_questions TEXT,  -- JSON array of targeted primary research interview questions
    priority_score REAL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (cluster_id) REFERENCES thematic_clusters(cluster_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hypotheses_cluster ON hypothesis_records(cluster_id);
CREATE INDEX IF NOT EXISTS idx_hypotheses_priority ON hypothesis_records(priority_score);

-- 7. GOLDEN SET BENCHMARKS (Human-labelled ground truth evaluation dataset)
CREATE TABLE IF NOT EXISTS golden_set_benchmarks (
    benchmark_id TEXT PRIMARY KEY,
    raw_id TEXT NOT NULL,
    human_labels TEXT NOT NULL,  -- JSON object representing human ground truth extraction
    model_labels TEXT,  -- JSON object representing LLM extraction output
    agreement_score REAL,
    evaluated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (raw_id) REFERENCES raw_conversations(raw_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_golden_set_raw ON golden_set_benchmarks(raw_id);

-- 8. AI FAILURE LOGS (Diagnostic tracking of LLM hallucinations & extraction defects)
CREATE TABLE IF NOT EXISTS ai_failure_logs (
    failure_id TEXT PRIMARY KEY,
    benchmark_id TEXT,
    failure_type TEXT NOT NULL,  -- hallucinated_quote | category_drift | stage_mismatch | unsupported_inference | etc.
    raw_input TEXT NOT NULL,
    erroneous_model_output TEXT,
    ground_truth_correction TEXT,
    remediation_applied TEXT,
    logged_at TIMESTAMP NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES golden_set_benchmarks(benchmark_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_failure_benchmark ON ai_failure_logs(benchmark_id);
CREATE INDEX IF NOT EXISTS idx_failure_type ON ai_failure_logs(failure_type);
