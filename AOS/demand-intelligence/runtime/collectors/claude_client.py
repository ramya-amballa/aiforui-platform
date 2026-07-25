"""
Minimal, dependency-free Claude API client (urllib + json only, no
`anthropic` package) — used solely by demand_signals.py to confirm a
news item names a real, specific organisation and extract that name.
This is AOS's first runtime with an external paid API dependency;
every other employee stays stdlib-only. Never called unless
ANTHROPIC_API_KEY is set — its absence is a clean skip, not an error,
matching every other connector's credential-missing behaviour.

Sprint 6 (Demand Intelligence v2) widened what this extracts: it used
to be scoped narrowly to "AI tool adoption at scale" articles. Which
of the five demand-signal categories (AI Adoption, Governance Trigger,
Funding Trigger, Regulatory Trigger, Failure Trigger) an article
belongs to is now decided beforehand by demand_engine.classify_categories()
— pure deterministic keyword matching, no model call — and this
extraction only runs at all once that deterministic gate has already
matched something. Claude's job stays exactly the kind of task it
always did: given a passage of English text already flagged as
relevant, confirm there is a real, specific, named organisation in it
and pull out that name — never deciding the category itself.
"""

import json
import os
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

EXTRACTION_TOOL = {
    "name": "extract_demand_signal",
    "description": (
        "This news item's text already matched at least one deterministic "
        "keyword rule for a demand-signal category (AI adoption at scale, a "
        "governance trigger, a funding round, a regulatory trigger, or an AI "
        "failure/incident). Decide whether it genuinely names a SPECIFIC, "
        "REAL organisation experiencing that event — not the vendor being "
        "reported on, not a generic industry trend piece, not speculative or "
        "hypothetical coverage with no named organisation at all — and "
        "extract that organisation's name and a short factual summary of "
        "what was reported."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "isDemandSignal": {
                "type": "boolean",
                "description": "true only if a specific, real, named organisation is described experiencing the matched event",
            },
            "organisation": {
                "type": "string",
                "description": "the named organisation; empty string if isDemandSignal is false",
            },
            "eventSummary": {
                "type": "string",
                "description": "one factual sentence stating what was reported about this organisation, e.g. "
                                "'Acme Corp deployed Microsoft Copilot to 40,000 employees.' — no marketing "
                                "language, no speculation beyond what the text states; empty string if isDemandSignal is false",
            },
            "aiTool": {
                "type": "string",
                "description": "the AI tool/product named, if any (e.g. 'Microsoft Copilot'); empty string if not applicable to this event type",
            },
            "scale": {
                "type": "string",
                "description": "a scale figure mentioned, verbatim if possible, e.g. '40,000 employees'; empty string if not stated",
            },
            "industry": {
                "type": "string",
                "description": "the organisation's industry, only if stated or unambiguous from the text; empty string otherwise",
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "high only if the named organisation and the event are both stated plainly and unambiguously in the text",
            },
        },
        "required": ["isDemandSignal", "organisation", "eventSummary", "aiTool", "scale", "industry", "confidence"],
    },
}


def api_key_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def extract_demand_signal(title, summary, model=None, timeout=30):
    """Returns the tool-use input dict, or None if the API key is
    missing, the call fails, or the response isn't usable. Never
    raises — one article failing must never stop the rest of a run."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    body = {
        "model": model or DEFAULT_MODEL,
        "max_tokens": 512,
        "tools": [EXTRACTION_TOOL],
        "tool_choice": {"type": "tool", "name": "extract_demand_signal"},
        "messages": [{
            "role": "user",
            "content": f"Title: {title}\n\nSummary: {summary}",
        }],
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"    Claude API call failed: {exc}")
        return None

    for block in payload.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == "extract_demand_signal":
            return block.get("input")
    return None
