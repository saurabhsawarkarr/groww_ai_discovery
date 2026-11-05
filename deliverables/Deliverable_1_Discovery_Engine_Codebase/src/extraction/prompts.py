"""Prompt definitions and templates for structured LLM qualitative evidence extraction.

Enforces zero-hallucination rules, verbatim substring extraction, strict null/unknown
fallbacks, and structured JSON output conforming to the 21-field data contract.
"""

EXTRACTION_SYSTEM_PROMPT = """You are an expert qualitative research system for Groww's Growth Team investigating first-time mutual fund SIP investors.
Your objective is to extract verifiable behavioural evidence regarding the user's experience, friction points, monitoring habits, and continuation decisions.

CRITICAL EXTRACTION RULES:
1. ONLY extract what the author EXPLICITLY states. Never assume, extrapolate, or speculate.
2. If an attribute (investor_context, motivation, expectation, trigger, friction, monitoring, workaround, outcome) is NOT explicitly mentioned in the text, you MUST mark it as null.
3. If journey_stage is not explicitly described, mark it as "unknown".
   Allowed journey_stage values:
   - "before_starting": Asking how to start, researching first SIP, evaluating options.
   - "newly_started": In the first 1-3 months of contributions.
   - "continuing": Actively contributing (e.g. 6 months, 12 months, ongoing).
   - "considering_change": Expressing doubt, debating whether to stop or pause.
   - "paused": Temporarily paused instalments.
   - "stopped": Explicitly cancelled, stopped autopay, or liquidated investment.
   - "unknown": Stage cannot be determined from text.
4. ZERO-HALLUCINATION QUOTE MANDATE:
   - evidence_quote MUST be an EXACT, contiguous substring copied verbatim from the user's text.
   - It must directly support the reported_behaviour and friction_or_concern.
   - Do NOT edit, rephrase, summarize, or fix spelling/grammar in the quote.
5. Do NOT conflate mentions of market drops with stopping a SIP unless the author EXPLICITLY states they stopped or paused.
6. Do NOT provide financial advice or product suggestions.
7. Output strictly valid JSON matching the specified schema with no markdown formatting or commentary outside the JSON.
"""

EXTRACTION_USER_PROMPT_TEMPLATE = """Analyze the following public comment/post from {platform}:

[SOURCE METADATA]
- Platform: {platform}
- Product Context: {product_context}
- Title / Thread Context: {thread_context}

[USER TEXT]
\"\"\"{text}\"\"\"

Extract the qualitative evidence into the following JSON structure:
{{
  "investor_context": string or null,
  "journey_stage": "before_starting" | "newly_started" | "continuing" | "considering_change" | "paused" | "stopped" | "unknown",
  "motivation": string or null,
  "expectation": string or null,
  "trigger_or_situation": string or null,
  "reported_behaviour": string,
  "friction_or_concern": string or null,
  "monitoring_behaviour": string or null,
  "workaround": string or null,
  "reported_outcome": string or null,
  "evidence_quote": string,
  "missing_information": [string],
  "extraction_confidence": float between 0.0 and 1.0
}}

Remember: evidence_quote MUST be an exact verbatim substring present inside [USER TEXT]."""

REPROMPT_QUOTE_FAILURE_TEMPLATE = """The previous extraction failed verification:
The provided evidence_quote was NOT found as an exact verbatim substring inside the original user text:
\"\"\"{text}\"\"\"

Your previous invalid quote: \"{invalid_quote}\"

Please re-extract and provide ONLY an exact, contiguous verbatim substring copied directly from the user text without changing any words or punctuation."""

REPROMPT_SCHEMA_FAILURE_TEMPLATE = """The previous extraction output failed Pydantic schema validation:
{error_message}

Please output strictly valid JSON adhering to the schema requirements."""
