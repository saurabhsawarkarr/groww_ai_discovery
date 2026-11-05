"""Pydantic data models for structured qualitative evidence extraction.

Implements the 21-field EvidenceRecord specification adhering to architecture.md
Section 3.3 and ensures unknown attributes strictly default to None or 'unknown'.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Literal, Optional, Union
import uuid
from pydantic import BaseModel, Field, field_validator

JourneyStage = Literal[
    "before_starting",
    "newly_started",
    "continuing",
    "considering_change",
    "paused",
    "stopped",
    "unknown",
]

ProductContext = Literal[
    "groww_specific",
    "category_level",
    "other_product_specific",
    "unknown",
]

SourcePlatform = Literal[
    "play_store",
    "app_store",
    "reddit",
    "youtube",
    "forum",
    "other",
]

EvidenceType = Literal[
    "explicitly_stated",
    "inferred",
    "unknown",
]

ReviewStatus = Literal[
    "unreviewed",
    "accepted",
    "corrected",
    "rejected",
]


class LLMExtractionPayload(BaseModel):
    """Structured extraction contract returned directly by the LLM."""
    investor_context: Optional[str] = Field(
        default=None,
        description="Explicit stated investor background (e.g. '22yo first job', 'earning 30k/mo'). Set null if not stated."
    )
    journey_stage: JourneyStage = Field(
        default="unknown",
        description="One of: before_starting, newly_started, continuing, considering_change, paused, stopped, unknown."
    )
    motivation: Optional[str] = Field(
        default=None,
        description="Explicitly stated reason for starting or wanting to invest. Set null if not stated."
    )
    expectation: Optional[str] = Field(
        default=None,
        description="Explicitly stated return, timeline, or habit expectation. Set null if not stated."
    )
    trigger_or_situation: Optional[str] = Field(
        default=None,
        description="Circumstance preceding action (e.g. 'salary delayed', 'market down 3%', 'bank mandate failed')."
    )
    reported_behaviour: str = Field(
        ...,
        min_length=3,
        description="Explicit action or habit described (e.g. 'paused SIP', 'checked NAV daily', 'stepped up Rs 1000')."
    )
    friction_or_concern: Optional[str] = Field(
        default=None,
        description="Explicit anxiety, confusion, or obstacle (e.g. 'negative XIRR confusion', 'fear of bounce fee')."
    )
    monitoring_behaviour: Optional[str] = Field(
        default=None,
        description="Explicit tracking habit or cadence (e.g. 'checking Groww app every 2 hours', 'never checks balance')."
    )
    workaround: Optional[str] = Field(
        default=None,
        description="External solution attempted (e.g. 'watched YouTube video', 'asked on Reddit', 'switched to monthly')."
    )
    reported_outcome: Optional[str] = Field(
        default=None,
        description="Explicit result described by author (e.g. 'sitting at +14% XIRR', 'lost 80% capital')."
    )
    evidence_quote: str = Field(
        ...,
        min_length=5,
        description="Shortest contiguous verbatim substring copied directly from the input text supporting the extraction."
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="List of core dimensions not explicitly mentioned in the text (e.g. ['income_stability', 'motivation'])."
    )
    extraction_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 reflecting how explicitly stated the observations were."
    )

    @field_validator("evidence_quote")
    @classmethod
    def quote_must_not_be_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 5:
            raise ValueError("evidence_quote must be an explicit, non-empty excerpt of at least 5 characters.")
        return v.strip()


class EvidenceRecord(BaseModel):
    """The complete 21-field qualitative evidence data contract."""
    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    source_id: str = Field(description="Foreign key referencing raw_conversations.raw_id")
    source_platform: SourcePlatform = "other"
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    product_context: ProductContext = "unknown"
    investor_context: Optional[str] = None
    journey_stage: JourneyStage = "unknown"
    motivation: Optional[str] = None
    expectation: Optional[str] = None
    trigger_or_situation: Optional[str] = None
    reported_behaviour: str = Field(..., min_length=3)
    friction_or_concern: Optional[str] = None
    monitoring_behaviour: Optional[str] = None
    workaround: Optional[str] = None
    reported_outcome: Optional[str] = None
    evidence_quote: str = Field(..., min_length=5)
    evidence_type: EvidenceType = "explicitly_stated"
    missing_information: List[str] = Field(default_factory=list)
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    review_status: ReviewStatus = "unreviewed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("evidence_quote")
    @classmethod
    def quote_must_be_substantial(cls, v: str) -> str:
        if not v or len(v.strip()) < 5:
            raise ValueError("evidence_quote must be a non-empty excerpt of at least 5 characters.")
        return v.strip()

    def to_db_tuple(self) -> tuple:
        """Convert to tuple for SQLite extracted_evidence table insertion."""
        missing_json = json.dumps(self.missing_information) if self.missing_information else "[]"
        return (
            self.evidence_id,
            self.source_id,
            self.investor_context,
            self.journey_stage,
            self.motivation,
            self.expectation,
            self.trigger_or_situation,
            self.reported_behaviour,
            self.friction_or_concern,
            self.monitoring_behaviour,
            self.workaround,
            self.reported_outcome,
            self.evidence_quote,
            self.evidence_type,
            missing_json,
            self.extraction_confidence,
            self.review_status,
            self.created_at.isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with ISO formatted timestamps."""
        data = self.model_dump()
        if self.published_at:
            data["published_at"] = self.published_at.isoformat()
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_db_row(cls, row: Any, parent_row: Optional[Any] = None) -> "EvidenceRecord":
        """Instantiate EvidenceRecord from an SQLite row."""
        missing_info = row["missing_information"]
        if isinstance(missing_info, str):
            try:
                missing_info = json.loads(missing_info)
            except Exception:
                missing_info = []

        pub_at = None
        platform = "other"
        url = None
        prod_ctx = "unknown"

        if parent_row:
            platform = parent_row["source_platform"]
            url = parent_row["source_url"]
            prod_ctx = parent_row["product_context"]
            if parent_row["published_at"]:
                if isinstance(parent_row["published_at"], str):
                    try:
                        pub_at = datetime.fromisoformat(parent_row["published_at"])
                    except Exception:
                        pub_at = None
                elif isinstance(parent_row["published_at"], datetime):
                    pub_at = parent_row["published_at"]

        created_dt = row["created_at"]
        if isinstance(created_dt, str):
            try:
                created_dt = datetime.fromisoformat(created_dt)
            except Exception:
                created_dt = datetime.now(timezone.utc)
        elif not isinstance(created_dt, datetime):
            created_dt = datetime.now(timezone.utc)

        # investor_context might be in row
        investor_ctx = row["investor_context"] if "investor_context" in row.keys() else None

        return cls(
            evidence_id=row["evidence_id"],
            source_id=row["raw_id"],
            source_platform=platform,
            source_url=url,
            published_at=pub_at,
            product_context=prod_ctx,
            investor_context=investor_ctx,
            journey_stage=row["journey_stage"] or "unknown",
            motivation=row["motivation"],
            expectation=row["expectation"],
            trigger_or_situation=row["trigger_or_situation"],
            reported_behaviour=row["reported_behaviour"],
            friction_or_concern=row["friction_or_concern"],
            monitoring_behaviour=row["monitoring_behaviour"],
            workaround=row["workaround"],
            reported_outcome=row["reported_outcome"],
            evidence_quote=row["evidence_quote"],
            evidence_type=row["evidence_type"] or "explicitly_stated",
            missing_information=missing_info,
            extraction_confidence=row["extraction_confidence"] or 1.0,
            review_status=row["review_status"] or "unreviewed",
            created_at=created_dt,
        )
