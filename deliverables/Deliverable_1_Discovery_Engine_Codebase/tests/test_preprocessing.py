"""Comprehensive test suite for Phase 2: Cleaning, PII Masking & Relevance Qualification.

Validates:
- 100% PII scrubbing across Phone, PAN, Email, IFSC, Bank Account, UPI, and Aadhaar
- Unicode normalization and whitespace collapsing
- Exact SHA-256 duplicate dropping
- Near-duplicate character 3-gram MinHash/Jaccard filtering (threshold >= 0.85)
- Domain relevance classification and exclusion reason logging
- End-to-end pipeline execution and SQLite database synchronization
"""

from datetime import datetime, timezone
from pathlib import Path
import pytest

from src.connectors.base import RawRecord
from src.database.connection import get_connection, init_db
from src.preprocessing.sanitizer import PIISanitizer
from src.preprocessing.deduplicator import Deduplicator
from src.preprocessing.qualifier import RelevanceClassifier
from src.preprocessing.pipeline import PreprocessingPipeline


@pytest.fixture
def sanitizer() -> PIISanitizer:
    return PIISanitizer()


@pytest.fixture
def deduplicator() -> Deduplicator:
    return Deduplicator(near_duplicate_threshold=0.85)


@pytest.fixture
def qualifier() -> RelevanceClassifier:
    return RelevanceClassifier()


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Fixture providing an initialized SQLite test database."""
    db_file = tmp_path / "test_preprocessing.db"
    init_db(db_path=db_file)
    return db_file


# =====================================================================
# 1. PII Sanitization Tests
# =====================================================================

def test_pii_sanitization_mobile_numbers(sanitizer: PIISanitizer):
    """Verify Indian mobile numbers with varied prefixes are redacted."""
    test_cases = [
        ("My registered phone is +91 9876543210 please update it", "[REDACTED_PHONE]"),
        ("Call me on 919876543210 for KYC issue", "[REDACTED_PHONE]"),
        ("Send OTP to 09876543210 instead", "[REDACTED_PHONE]"),
        ("Contact number is 8765432109 immediately", "[REDACTED_PHONE]"),
    ]
    for raw_input, expected_token in test_cases:
        clean, applied = sanitizer.sanitize(raw_input)
        assert expected_token in clean
        assert "9876543210" not in clean
        assert "indian_phone" in applied


def test_pii_sanitization_pan_cards(sanitizer: PIISanitizer):
    """Verify Indian PAN card numbers are completely masked."""
    test_cases = [
        ("My PAN card is ABCDE1234F linked with Zerodha", "[REDACTED_PAN]"),
        ("Rejected due to invalid PAN BNZPK9876M details", "[REDACTED_PAN]"),
    ]
    for raw_input, expected_token in test_cases:
        clean, applied = sanitizer.sanitize(raw_input)
        assert expected_token in clean
        assert "ABCDE1234F" not in clean
        assert "BNZPK9876M" not in clean
        assert "pan_card" in applied


def test_pii_sanitization_emails(sanitizer: PIISanitizer):
    """Verify email addresses are redacted."""
    test_cases = [
        ("Send statement to rahul.investor@gmail.com please", "[REDACTED_EMAIL]"),
        ("Support contact: priya_99@yahoo.co.in for folio check", "[REDACTED_EMAIL]"),
    ]
    for raw_input, expected_token in test_cases:
        clean, applied = sanitizer.sanitize(raw_input)
        assert expected_token in clean
        assert "@gmail.com" not in clean
        assert "email_address" in applied


def test_pii_sanitization_banking_info(sanitizer: PIISanitizer):
    """Verify IFSC codes and bank account numbers are scrubbed."""
    text_ifsc = "My branch IFSC is HDFC0001234 and SBIN0005678"
    clean_ifsc, applied_ifsc = sanitizer.sanitize(text_ifsc)
    assert "[REDACTED_IFSC]" in clean_ifsc
    assert "HDFC0001234" not in clean_ifsc

    text_acc = "Autopay debited from a/c no: 1234567890123 without confirmation"
    clean_acc, applied_acc = sanitizer.sanitize(text_acc)
    assert "[REDACTED_BANK_INFO]" in clean_acc
    assert "1234567890123" not in clean_acc


def test_pii_sanitization_upi_and_aadhaar(sanitizer: PIISanitizer):
    """Verify UPI IDs and formatted Aadhaar numbers are redacted."""
    text_upi = "Paid instalment using UPI ID rahul.sharma@okhdfcbank successfully"
    clean_upi, applied_upi = sanitizer.sanitize(text_upi)
    assert "[REDACTED_UPI]" in clean_upi
    assert "rahul.sharma@okhdfcbank" not in clean_upi

    text_aadhaar = "Linked Aadhaar card 2345 6789 0123 for mutual fund KYC"
    clean_aadhaar, applied_aadhaar = sanitizer.sanitize(text_aadhaar)
    assert "[REDACTED_AADHAAR]" in clean_aadhaar
    assert "2345 6789 0123" not in clean_aadhaar


def test_sanitizer_unicode_normalization(sanitizer: PIISanitizer):
    """Verify non-printable control characters and excessive whitespaces are cleaned."""
    dirty_text = "Groww\x00\x08 SIP   instalment  \t\t debited\n\n\n\nsuccessfully!   "
    clean, _ = sanitizer.sanitize(dirty_text)
    assert clean == "Groww SIP instalment debited\n\nsuccessfully!"


# =====================================================================
# 2. Deduplication Tests
# =====================================================================

def test_exact_duplicate_dropping(deduplicator: Deduplicator):
    """Verify exact duplicate texts are dropped deterministically."""
    rec1 = RawRecord(
        raw_id="rec_001",
        source_platform="play_store",
        raw_text="Negative XIRR in first 3 months of mutual fund SIP.",
    )
    rec2 = RawRecord(
        raw_id="rec_002",
        source_platform="play_store",
        raw_text="NEGATIVE XIRR in first 3 months of mutual fund SIP.   ",  # Case/space variation
    )

    kept, dropped = deduplicator.filter_records([rec1, rec2])
    assert len(kept) == 1
    assert kept[0].raw_id == "rec_001"
    assert len(dropped) == 1
    assert dropped[0]["raw_id"] == "rec_002"
    assert dropped[0]["duplicate_type"] == "exact"
    assert dropped[0]["matched_id"] == "rec_001"


def test_near_duplicate_dropping(deduplicator: Deduplicator):
    """Verify near-duplicate reviews with high Jaccard similarity are dropped."""
    rec1 = RawRecord(
        raw_id="rec_bot_001",
        source_platform="play_store",
        raw_text="Groww app is very smooth and easy to invest in mutual funds for beginners.",
    )
    # 90%+ character overlap with minor typo/punctuation change
    rec2 = RawRecord(
        raw_id="rec_bot_002",
        source_platform="play_store",
        raw_text="Groww app is very smooth and easy to invest in mutual funds for beginner!",
    )

    kept, dropped = deduplicator.filter_records([rec1, rec2])
    assert len(kept) == 1
    assert kept[0].raw_id == "rec_bot_001"
    assert len(dropped) == 1
    assert dropped[0]["raw_id"] == "rec_bot_002"
    assert dropped[0]["duplicate_type"] == "near"
    assert dropped[0]["similarity"] >= 0.85


def test_distinct_records_not_dropped(deduplicator: Deduplicator):
    """Verify genuinely distinct records are kept."""
    rec1 = RawRecord(
        raw_id="rec_101",
        source_platform="reddit",
        raw_text="Started SIP in Parag Parikh Flexi Cap 3 months ago.",
    )
    rec2 = RawRecord(
        raw_id="rec_102",
        source_platform="reddit",
        raw_text="HDFC bank autopay mandate failed without warning.",
    )

    kept, dropped = deduplicator.filter_records([rec1, rec2])
    assert len(kept) == 2
    assert len(dropped) == 0


# =====================================================================
# 3. Relevance Qualification Tests
# =====================================================================

def test_qualification_valid_sip_discussions(qualifier: RelevanceClassifier):
    """Verify valid first-time mutual fund and SIP conversations pass qualification."""
    valid_samples = [
        "Started my first SIP of Rs 1000 last month and looking at portfolio daily.",
        "Why is XIRR showing negative -5% after 2 months of regular instalment?",
        "Groww autopay mandate deduction failed on 5th of this month.",
        "Decided to pause my SIP in small cap and step up Nifty 50 index fund.",
        "Completed 12 months of disciplined mutual fund investment with positive returns.",
    ]
    for text in valid_samples:
        is_qual, reason = qualifier.qualify_text(text)
        assert is_qual is True, f"Failed qualification for valid text: {text} (Reason: {reason})"
        assert reason is None


def test_qualification_rejection_exclusions(qualifier: RelevanceClassifier):
    """Verify discussions containing excluded domains (F&O, US stocks, crypto) are rejected."""
    excluded_samples = [
        ("Lost 50k in BankNifty intraday call options today, advice needed.", "intraday"),
        ("How to trade US stocks and Nasdaq 100 ETFs from India?", "us stocks"),
        ("Is Bitcoin and crypto trading better than mutual funds?", "crypto"),
        ("Bought BSE index option strike price 82000 expiring today.", "bse index option"),
    ]
    for text, expected_keyword in excluded_samples:
        is_qual, reason = qualifier.qualify_text(text)
        assert is_qual is False
        assert reason is not None
        assert "Irrelevant domain" in reason
        assert expected_keyword in reason


def test_qualification_insufficient_context(qualifier: RelevanceClassifier):
    """Verify short uninformative comments (< 4 words) are rejected."""
    short_samples = ["Nice app", "Bad", "Good SIP", "super"]
    for text in short_samples:
        is_qual, reason = qualifier.qualify_text(text)
        assert is_qual is False
        assert "Insufficient context" in reason


def test_qualification_no_sip_terminology(qualifier: RelevanceClassifier):
    """Verify general app reviews lacking SIP/Mutual Fund terminology are rejected."""
    general_samples = [
        "Login OTP was delayed by 5 minutes today morning.",
        "Camera permission is not working during Aadhaar verification step.",
        "The app crashed when opening dark mode settings.",
    ]
    for text in general_samples:
        is_qual, reason = qualifier.qualify_text(text)
        assert is_qual is False
        assert "No SIP/Mutual Fund terminology detected" in reason


# =====================================================================
# 4. End-to-End Pipeline & Database Synchronization Tests
# =====================================================================

def test_preprocessing_pipeline_end_to_end(temp_db: Path):
    """Verify the complete pipeline sanitizes, deduplicates, qualifies, and updates SQLite."""
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Seed raw_conversations table
    seed_records = [
        RawRecord(
            raw_id="rec_pii_001",
            source_platform="play_store",
            raw_text="My phone 9876543210 and PAN ABCDE1234F failed for first SIP verification.",
            product_context="groww_specific",
        ),
        RawRecord(
            raw_id="rec_pii_dup_002",
            source_platform="play_store",
            raw_text="My phone 9876543210 and PAN ABCDE1234F failed for first SIP verification.",  # Exact duplicate
            product_context="groww_specific",
        ),
        RawRecord(
            raw_id="rec_irrelevant_003",
            source_platform="reddit",
            raw_text="How to buy call option in Bank Nifty intraday for fast 100% profit?",
            product_context="category_level",
        ),
        RawRecord(
            raw_id="rec_short_004",
            source_platform="play_store",
            raw_text="Worst app ever",  # < 4 words
            product_context="groww_specific",
        ),
        RawRecord(
            raw_id="rec_valid_005",
            source_platform="reddit",
            raw_text="Started Rs 2000 monthly SIP in index fund, but negative XIRR is causing anxiety.",
            product_context="category_level",
        ),
    ]

    # Insert raw seed items
    conn = get_connection(temp_db)
    cursor = conn.cursor()
    insert_sql = """
    INSERT INTO raw_conversations (
        raw_id, source_platform, collected_at, raw_text, product_context, is_qualified
    ) VALUES (?, ?, ?, ?, ?, 0);
    """
    for r in seed_records:
        cursor.execute(insert_sql, (r.raw_id, r.source_platform, now_iso, r.raw_text, r.product_context))
    conn.commit()
    conn.close()

    # 2. Run Preprocessing Pipeline
    pipeline = PreprocessingPipeline()
    result = pipeline.process_database(db_path=temp_db)

    # 3. Verify Metrics
    assert result.total_input == 5
    assert result.pii_redacted_count == 2
    assert result.exact_duplicates_dropped == 1
    assert result.irrelevant_dropped == 2  # F&O and short text
    assert result.qualified_count == 2     # rec_pii_001 (sanitized & qualified) + rec_valid_005

    # 4. Verify Database State
    conn = get_connection(temp_db)
    cursor = conn.cursor()

    # Check is_qualified flags in raw_conversations
    cursor.execute("SELECT raw_id, raw_text, is_qualified FROM raw_conversations ORDER BY raw_id;")
    rows = {r["raw_id"]: r for r in cursor.fetchall()}

    # rec_pii_001 must have PII scrubbed and be marked qualified
    assert rows["rec_pii_001"]["is_qualified"] == 1
    assert "[REDACTED_PHONE]" in rows["rec_pii_001"]["raw_text"]
    assert "[REDACTED_PAN]" in rows["rec_pii_001"]["raw_text"]
    assert "9876543210" not in rows["rec_pii_001"]["raw_text"]

    # rec_pii_dup_002 must be unqualified (exact duplicate)
    assert rows["rec_pii_dup_002"]["is_qualified"] == 0

    # rec_irrelevant_003 must be unqualified (F&O)
    assert rows["rec_irrelevant_003"]["is_qualified"] == 0

    # rec_short_004 must be unqualified (< 4 words)
    assert rows["rec_short_004"]["is_qualified"] == 0

    # rec_valid_005 must be qualified
    assert rows["rec_valid_005"]["is_qualified"] == 1

    # Check exclusion_logs
    cursor.execute("SELECT raw_id, reason FROM exclusion_logs;")
    exclusions = {r["raw_id"]: r["reason"] for r in cursor.fetchall()}

    assert "rec_pii_dup_002" in exclusions
    assert "duplicate of rec_pii_001" in exclusions["rec_pii_dup_002"].lower()

    assert "rec_irrelevant_003" in exclusions
    assert "Irrelevant domain" in exclusions["rec_irrelevant_003"]
    assert any(term in exclusions["rec_irrelevant_003"] for term in ["call option", "intraday"])

    assert "rec_short_004" in exclusions
    assert "Insufficient context" in exclusions["rec_short_004"]

    conn.close()
