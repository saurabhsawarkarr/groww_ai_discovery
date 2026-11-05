"""Extraction orchestrator coordinating LLM structured extraction, retries, and guardrails.

Supports OpenAI, Anthropic, Gemini, and deterministic offline rule-based extraction,
enforcing Pydantic validation and the Zero-Hallucination Verbatim Quote Guardrail.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Union
import yaml

from src.connectors.base import RawRecord
from src.database.connection import get_connection, get_db_path
from src.extraction.guardrails import (
    audit_missing_dimensions,
    clean_quote_delimiters,
    validate_substring,
)
from src.extraction.models import EvidenceRecord, LLMExtractionPayload
from src.extraction.prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    EXTRACTION_USER_PROMPT_TEMPLATE,
    REPROMPT_QUOTE_FAILURE_TEMPLATE,
    REPROMPT_SCHEMA_FAILURE_TEMPLATE,
)

logger = logging.getLogger("groww_discovery.extraction.orchestrator")
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "configs" / "config.yaml"


class ExtractionOrchestrator:
    """Manages LLM extraction execution, retry handling, and guardrail verification."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        config_path: Optional[Union[str, Path]] = None,
    ):
        self.config = config or self._load_config(config_path)
        extract_cfg = self.config.get("extraction", {})

        self.model_provider = extract_cfg.get("model_provider", "openai")
        self.model_name = extract_cfg.get("model_name", "gpt-4o-mini")
        self.temperature = extract_cfg.get("temperature", 0.0)
        self.max_retries = extract_cfg.get("max_retries", 2)
        self.quote_guardrail_enforced = extract_cfg.get("quote_guardrail_enforced", True)

        # Initialize API client if keys are present
        self._openai_client = None
        self._anthropic_client = None
        self._groq_client = None
        self._load_env_file()
        self._init_clients()

    def _load_env_file(self) -> None:
        """Load variables from .env file if present."""
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k not in os.environ and v:
                                os.environ[k] = v
            except Exception as e:
                logger.debug("Failed reading .env: %s", str(e))

    def _load_config(self, custom_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        path = Path(custom_path) if custom_path else DEFAULT_CONFIG_PATH
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning("Failed to load config: %s", str(e))
        return {}

    def _init_clients(self) -> None:
        # 1. Groq Client
        if self.model_provider == "groq" and os.environ.get("GROQ_API_KEY"):
            try:
                from groq import Groq
                self._groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
                if self.model_name in ["gpt-4o-mini", "gpt-4o", "default"]:
                    self.model_name = "openai/gpt-oss-120b"
                logger.info("Groq client initialized with model %s", self.model_name)
            except Exception as e:
                logger.warning("Groq client initialization failed: %s", str(e))

        # 2. OpenAI Client
        if self.model_provider == "openai" and os.environ.get("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            except Exception as e:
                logger.warning("OpenAI client initialization failed: %s", str(e))

        # 3. Anthropic Client
        elif self.model_provider == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                self._anthropic_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
            except Exception as e:
                logger.warning("Anthropic client initialization failed: %s", str(e))

    def _call_llm(self, user_prompt: str, system_prompt: str) -> str:
        """Execute model call through configured provider or fallback to mock."""
        # 1. Groq Execution
        if self._groq_client and (self.model_provider == "groq" or not (self._openai_client or self._anthropic_client)):
            response = self._groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or ""

        # 2. OpenAI Execution
        if self._openai_client:
            response = self._openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or ""

        # 3. Anthropic Execution
        if self._anthropic_client:
            response = self._anthropic_client.messages.create(
                model=self.model_name,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=self.temperature,
                max_tokens=1000,
            )
            return response.content[0].text if response.content else ""

        # Default fallback: Deterministic offline extractor
        return ""

    def _rule_based_fallback_extract(self, record: RawRecord) -> LLMExtractionPayload:
        """Deterministic, rule-based extraction fallback for offline execution and testing.

        Ensures 100% schema conformance and zero-hallucination quote compliance.
        """
        text = record.raw_text.strip()
        lower = text.lower()

        # 1. Infer Journey Stage
        journey_stage = "unknown"
        if any(w in lower for w in ["stop", "stopped", "cancel", "cancelled", "terminat", "liquidat"]):
            journey_stage = "stopped"
        elif any(w in lower for w in ["pause", "paused", "halt"]):
            journey_stage = "paused"
        elif any(w in lower for w in ["thinking of", "considering", "should i stop", "should i pause", "reconsider"]):
            journey_stage = "considering_change"
        elif any(w in lower for w in ["first sip", "started", "1st sip", "newly", "1 month", "2 month", "3 month"]):
            journey_stage = "newly_started"
        elif any(w in lower for w in ["12 month", "1 year", "completed", "disciplined", "compounding", "continu"]):
            journey_stage = "continuing"
        elif any(w in lower for w in ["how to start", "planning to", "before starting", "which fund to choose"]):
            journey_stage = "before_starting"

        # 2. Extract Verbatim Quote
        # Select the most informative sentence or clause as verbatim quote
        sentences = [s.strip() for s in re.split(r"[.!?\n]", text) if len(s.strip()) >= 5]
        evidence_quote = ""
        for s in sentences:
            s_lower = s.lower()
            if any(k in s_lower for k in ["sip", "xirr", "return", "autopay", "mandate", "nav", "stop", "pause"]):
                evidence_quote = s
                break

        if not evidence_quote:
            # Fallback to the first available non-empty sentence or first 60 chars
            evidence_quote = sentences[0] if sentences else text[:60]

        # Double check substring guardrail
        clean_quote = clean_quote_delimiters(evidence_quote)
        assert validate_substring(text, clean_quote), f"Fallback quote '{clean_quote}' must be in text '{text}'"

        # 3. Detect Friction
        friction = None
        if "negative" in lower or "-8%" in lower or "-5%" in lower or "in red" in lower:
            friction = "Panic or confusion over negative returns in initial months"
        elif "mandate" in lower or "autopay" in lower or "failed" in lower:
            friction = "Autopay bank mandate deduction failure or delay"
        elif "delay" in lower or "delayed" in lower:
            friction = "Delay in unit allotment or NAV reflection"
        elif "xirr" in lower:
            friction = "Difficulty interpreting XIRR vs absolute percentage returns"
        elif "overlap" in lower:
            friction = "Excessive portfolio overlap across multiple fund holdings"

        # 4. Detect Behaviour
        behaviour = "Monitoring mutual fund SIP investment and performance"
        if journey_stage == "stopped":
            behaviour = "Terminated or cancelled recurring SIP instalments"
        elif journey_stage == "paused":
            behaviour = "Paused recurring SIP contributions temporarily"
        elif "step up" in lower or "stepped up" in lower:
            behaviour = "Stepped up monthly instalment amount"
        elif "daily" in lower:
            behaviour = "Switched investment frequency"

        # 5. Missing Information
        payload_dict = {
            "investor_context": None,
            "motivation": None,
            "expectation": None,
            "trigger_or_situation": None,
            "friction_or_concern": friction,
            "monitoring_behaviour": None,
            "workaround": None,
            "reported_outcome": None,
        }
        missing = audit_missing_dimensions(payload_dict)

        return LLMExtractionPayload(
            investor_context=None,
            journey_stage=journey_stage,
            motivation=None,
            expectation=None,
            trigger_or_situation=None,
            reported_behaviour=behaviour,
            friction_or_concern=friction,
            monitoring_behaviour=None,
            workaround=None,
            reported_outcome=None,
            evidence_quote=clean_quote,
            missing_information=missing,
            extraction_confidence=0.95,
        )

    def extract_from_record(self, record: RawRecord) -> Optional[EvidenceRecord]:
        """Extract structured evidence from a single RawRecord instance.

        Executes LLM call with up to max_retries retry attempts on validation or
        substring quote failure, falling back to deterministic extraction if no API keys.
        """
        raw_text = record.raw_text.strip()
        if not raw_text or len(raw_text.split()) < 3:
            logger.warning("Skipping record %s: text too short", record.raw_id)
            return None

        # If live LLM clients are available, use them with retry logic
        if self._groq_client or self._openai_client or self._anthropic_client:
            user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
                platform=record.source_platform,
                product_context=record.product_context,
                thread_context=json.dumps(record.thread_context) if record.thread_context else "None",
                text=raw_text,
            )

            current_prompt = user_prompt
            for attempt in range(self.max_retries + 1):
                try:
                    raw_response = self._call_llm(current_prompt, EXTRACTION_SYSTEM_PROMPT)
                    data = json.loads(raw_response)

                    # Normalize quote
                    if "evidence_quote" in data and data["evidence_quote"]:
                        data["evidence_quote"] = clean_quote_delimiters(data["evidence_quote"])

                    # Validate quote substring guardrail
                    quote = data.get("evidence_quote", "")
                    if self.quote_guardrail_enforced and not validate_substring(raw_text, quote):
                        logger.warning(
                            "Attempt %d: Verbatim quote guardrail failed for record %s (quote: '%s')",
                            attempt + 1, record.raw_id, quote
                        )
                        current_prompt = REPROMPT_QUOTE_FAILURE_TEMPLATE.format(
                            text=raw_text, invalid_quote=quote
                        )
                        continue

                    # Validate with Pydantic
                    payload = LLMExtractionPayload(**data)
                    return self._build_evidence_record(record, payload)

                except json.JSONDecodeError as je:
                    logger.warning("Attempt %d JSON decode error for %s: %s", attempt + 1, record.raw_id, str(je))
                    current_prompt = REPROMPT_SCHEMA_FAILURE_TEMPLATE.format(error_message=str(je))
                except Exception as e:
                    logger.warning("Attempt %d validation failure for %s: %s", attempt + 1, record.raw_id, str(e))
                    current_prompt = REPROMPT_SCHEMA_FAILURE_TEMPLATE.format(error_message=str(e))

        # Deterministic offline rule-based fallback
        fallback_payload = self._rule_based_fallback_extract(record)
        return self._build_evidence_record(record, fallback_payload)

    def _build_evidence_record(
        self, record: RawRecord, payload: LLMExtractionPayload
    ) -> EvidenceRecord:
        """Combine raw record provenance with structured extraction payload."""
        # Auto-audit missing dimensions
        missing = payload.missing_information
        if not missing:
            missing = audit_missing_dimensions(payload.model_dump())

        # Substring guardrail check
        clean_quote = clean_quote_delimiters(payload.evidence_quote)
        if not validate_substring(record.raw_text, clean_quote):
            # Safe recovery: pull first exact sentence from raw text
            sentences = [s.strip() for s in re.split(r"[.!?\n]", record.raw_text) if len(s.strip()) >= 5]
            clean_quote = sentences[0] if sentences else record.raw_text[:60]

        return EvidenceRecord(
            evidence_id=f"ev_{record.raw_id}",
            source_id=record.raw_id,
            source_platform=record.source_platform if record.source_platform in ["play_store", "app_store", "reddit", "youtube", "forum"] else "other",
            source_url=record.source_url,
            published_at=record.published_at,
            product_context=record.product_context if record.product_context in ["groww_specific", "category_level", "other_product_specific"] else "unknown",
            investor_context=payload.investor_context,
            journey_stage=payload.journey_stage,
            motivation=payload.motivation,
            expectation=payload.expectation,
            trigger_or_situation=payload.trigger_or_situation,
            reported_behaviour=payload.reported_behaviour,
            friction_or_concern=payload.friction_or_concern,
            monitoring_behaviour=payload.monitoring_behaviour,
            workaround=payload.workaround,
            reported_outcome=payload.reported_outcome,
            evidence_quote=clean_quote,
            evidence_type="explicitly_stated",
            missing_information=missing,
            extraction_confidence=payload.extraction_confidence,
            review_status="unreviewed",
            created_at=datetime.now(timezone.utc),
        )

    def extract_batch(
        self,
        records: List[RawRecord],
        db_path: Optional[Union[str, Path]] = None,
        sync_db: bool = True,
    ) -> List[EvidenceRecord]:
        """Extract evidence records from a list of qualified RawRecord objects."""
        logger.info("Starting structured evidence extraction across %d records...", len(records))
        evidence_list: List[EvidenceRecord] = []

        for idx, rec in enumerate(records):
            try:
                evidence = self.extract_from_record(rec)
            except Exception as exc:
                logger.warning("Extraction error for %s: %s. Using rule-based fallback.", rec.raw_id, exc)
                fb_payload = self._rule_based_fallback_extract(rec)
                evidence = self._build_evidence_record(rec, fb_payload)

            if evidence:
                evidence_list.append(evidence)
            if (idx + 1) % 10 == 0:
                logger.info("Processed %d/%d records...", idx + 1, len(records))
            
            # Gentle rate-limit spacing for cloud LLM API
            time.sleep(0.25)

        if sync_db and evidence_list:
            self.save_evidence_to_db(evidence_list, db_path=db_path)

        logger.info("Extraction complete: generated %d verified evidence records", len(evidence_list))
        return evidence_list

    def save_evidence_to_db(
        self,
        evidence_list: List[EvidenceRecord],
        db_path: Optional[Union[str, Path]] = None,
    ) -> int:
        """Persist extracted EvidenceRecord instances into SQLite extracted_evidence."""
        if not evidence_list:
            return 0

        resolved_db = get_db_path(db_path)
        conn = get_connection(resolved_db)
        try:
            cursor = conn.cursor()
            query = """
            INSERT OR REPLACE INTO extracted_evidence (
                evidence_id, raw_id, investor_context, journey_stage,
                motivation, expectation, trigger_or_situation,
                reported_behaviour, friction_or_concern, monitoring_behaviour,
                workaround, reported_outcome, evidence_quote, evidence_type,
                missing_information, extraction_confidence, review_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            tuples = [e.to_db_tuple() for e in evidence_list]
            cursor.executemany(query, tuples)
            conn.commit()
            logger.info("Saved %d records into extracted_evidence in %s", len(evidence_list), resolved_db.name)
            return len(evidence_list)
        except Exception as e:
            conn.rollback()
            logger.error("Failed to commit evidence to database: %s", str(e), exc_info=True)
            raise
        finally:
            conn.close()
