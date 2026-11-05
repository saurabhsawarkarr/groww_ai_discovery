"""Unit tests for Phase 3: Structured LLM Evidence Extraction Engine & Guardrails.

Validates:
- Strict Pydantic enforcement of the 21-field EvidenceRecord contract
- Verbatim quote substring guardrail (exact, case-insensitive, whitespace-normalized)
- Hallucination detection and reprompt loop
- Accurate quote span character index locating
- Batch extraction and SQLite database persistence
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.connectors.base import RawRecord
from src.database.connection import get_connection, init_db
from src.extraction.guardrails import (
    audit_missing_dimensions,
    find_quote_span,
    validate_substring,
)
from src.extraction.models import EvidenceRecord, LLMExtractionPayload
from src.extraction.orchestrator import ExtractionOrchestrator


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Fixture providing an initialized SQLite test database."""
    db_file = tmp_path / "test_extraction.db"
    init_db(db_path=db_file)
    return db_file


@pytest.fixture
def orchestrator() -> ExtractionOrchestrator:
    return ExtractionOrchestrator(config={"extraction": {"max_retries": 1}})


# =====================================================================
# 1. 21-Field Data Contract Tests
# =====================================================================

def test_evidence_record_schema_and_unknowns():
    """Verify that EvidenceRecord conforms to the 21-field specification."""
    now = datetime.now(timezone.utc)
    ev = EvidenceRecord(
        evidence_id="ev_test_001",
        source_id="reddit_pilot_001",
        source_platform="reddit",
        source_url="https://reddit.com/r/IndiaInvestments/1",
        published_at=now,
        product_context="category_level",
        investor_context="24yo beginner earning 40k",
        journey_stage="newly_started",
        motivation="Wealth creation",
        expectation="12% positive returns from day one",
        trigger_or_situation="Portfolio shows -4% return in month 2",
        reported_behaviour="Checking NAV daily on mobile app",
        friction_or_concern="Negative XIRR anxiety",
        monitoring_behaviour="Daily evening check",
        workaround="Asked for advice on Reddit",
        reported_outcome="Still invested but anxious",
        evidence_quote="Current value shows -4.5% returns and negative XIRR",
        evidence_type="explicitly_stated",
        missing_information=[],
        extraction_confidence=0.95,
        review_status="unreviewed",
        created_at=now,
    )

    assert ev.evidence_id == "ev_test_001"
    assert ev.journey_stage == "newly_started"
    assert ev.extraction_confidence == 0.95

    # Test database tuple conversion
    db_tuple = ev.to_db_tuple()
    assert len(db_tuple) == 18
    assert db_tuple[0] == ev.evidence_id
    assert db_tuple[1] == "reddit_pilot_001"
    assert db_tuple[2] == "24yo beginner earning 40k"


def test_evidence_record_validation_failures():
    """Verify that missing mandatory fields or empty quotes fail validation."""
    with pytest.raises(Exception):
        # Empty evidence_quote
        EvidenceRecord(
            source_id="rec_1",
            reported_behaviour="stopped SIP",
            evidence_quote="",
        )

    with pytest.raises(Exception):
        # Evidence quote shorter than 5 chars
        EvidenceRecord(
            source_id="rec_2",
            reported_behaviour="stopped SIP",
            evidence_quote="bad",
        )


# =====================================================================
# 2. Zero-Hallucination Verbatim Quote Guardrail Tests
# =====================================================================

def test_verbatim_quote_guardrail_pass():
    """Verify exact and whitespace-normalized substring matching."""
    raw_text = "Started my first SIP of Rs 2000 in Parag Parikh Flexi Cap 3 months ago. Current value shows -4.5% returns."
    
    # Exact match
    assert validate_substring(raw_text, "Current value shows -4.5% returns") is True

    # Whitespace and case variations
    assert validate_substring(raw_text, "current   value   shows  -4.5%  returns") is True

    # Multi-line match
    multi_line = "Company delayed salary.\nHad to stop my monthly SIP in Quant Small Cap."
    assert validate_substring(multi_line, "Had to stop my monthly SIP in Quant Small Cap.") is True


def test_verbatim_quote_guardrail_rejects_hallucinations():
    """Verify that hallucinated or altered quotes fail validation."""
    raw_text = "I stopped my SIP after 3 months because returns were in red."

    # Paraphrased / altered quote
    hallucinated_quote = "The investor cancelled their recurring SIP due to capital loss."
    assert validate_substring(raw_text, hallucinated_quote) is False

    # Single word altered
    almost_match = "I stopped my SIP after 4 months because returns were in red."
    assert validate_substring(raw_text, almost_match) is False


def test_quote_span_indexing():
    """Verify character index localization for UI quote highlighting."""
    raw_text = "Started my first SIP. Current value shows -4.5% returns. Very worried."
    quote = "Current value shows -4.5% returns"
    span = find_quote_span(raw_text, quote)

    assert span is not None
    start, end = span
    assert raw_text[start:end] == quote


def test_missing_dimension_auditing():
    """Verify unstated dimensions are accurately logged in missing_information."""
    partial_payload = {
        "investor_context": None,
        "motivation": None,
        "reported_behaviour": "Checked portfolio",
        "friction_or_concern": "Negative return panic",
    }
    missing = audit_missing_dimensions(partial_payload)
    assert "investor_context" in missing
    assert "motivation" in missing
    assert "friction_or_concern" not in missing


# =====================================================================
# 3. Extraction Orchestrator & Recovery Tests
# =====================================================================

def test_orchestrator_deterministic_extraction(orchestrator: ExtractionOrchestrator):
    """Verify deterministic extraction produces 100% compliant evidence records."""
    rec = RawRecord(
        raw_id="test_rec_001",
        source_platform="reddit",
        raw_text="Started my first SIP of Rs 1000 last month. Current value shows -8% returns and negative XIRR.",
        product_context="category_level",
    )

    evidence = orchestrator.extract_from_record(rec)
    assert evidence is not None
    assert evidence.source_id == rec.raw_id
    assert evidence.journey_stage in ["newly_started", "continuing", "unknown"]
    assert "negative" in evidence.friction_or_concern.lower()

    # Quote must be confirmed substring of raw text
    assert validate_substring(rec.raw_text, evidence.evidence_quote) is True


def test_orchestrator_reprompt_loop_on_hallucinated_quote(orchestrator: ExtractionOrchestrator):
    """Verify orchestrator reprompts when LLM provides a hallucinated quote."""
    raw_text = "I paused my SIP for 2 months because of job transition."
    rec = RawRecord(
        raw_id="test_rec_hallucinate",
        source_platform="reddit",
        raw_text=raw_text,
    )

    # Simulate: Attempt 1 returns hallucinated quote, Attempt 2 returns valid verbatim quote
    invalid_resp = json.dumps({
        "journey_stage": "paused",
        "reported_behaviour": "Paused SIP",
        "evidence_quote": "User stopped investment due to unemployment",  # Hallucination!
        "extraction_confidence": 0.9,
    })
    valid_resp = json.dumps({
        "journey_stage": "paused",
        "reported_behaviour": "Paused SIP for 2 months",
        "evidence_quote": "I paused my SIP for 2 months",  # Verbatim substring!
        "extraction_confidence": 0.95,
    })

    with patch.object(orchestrator, "_call_llm", side_effect=[invalid_resp, valid_resp]):
        orchestrator._openai_client = MagicMock()
        evidence = orchestrator.extract_from_record(rec)

        assert evidence is not None
        assert evidence.evidence_quote == "I paused my SIP for 2 months"
        assert validate_substring(raw_text, evidence.evidence_quote) is True


def test_save_evidence_to_db(temp_db: Path, orchestrator: ExtractionOrchestrator):
    """Verify extracted evidence commits cleanly to SQLite extracted_evidence table."""
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    now_iso = datetime.now(timezone.utc).isoformat()
    raw_id = "rec_db_test_001"
    raw_text = "Groww autopay mandate deduction failed on 5th of this month."

    cursor.execute(
        """
        INSERT INTO raw_conversations (raw_id, source_platform, collected_at, raw_text, is_qualified)
        VALUES (?, ?, ?, ?, 1);
        """,
        (raw_id, "play_store", now_iso, raw_text),
    )
    conn.commit()
    conn.close()

    raw_rec = RawRecord(
        raw_id=raw_id,
        source_platform="play_store",
        raw_text=raw_text,
        product_context="groww_specific",
    )

    evidence_list = orchestrator.extract_batch([raw_rec], db_path=temp_db, sync_db=True)
    assert len(evidence_list) == 1
    ev = evidence_list[0]

    # Query from database
    conn = get_connection(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM extracted_evidence WHERE raw_id = ?", (raw_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row["raw_id"] == raw_id
    assert row["evidence_quote"] == ev.evidence_quote
    assert validate_substring(raw_text, row["evidence_quote"]) is True
    conn.close()
