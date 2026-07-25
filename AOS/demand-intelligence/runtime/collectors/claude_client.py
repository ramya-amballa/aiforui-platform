"""
Minimal, dependency-free Claude API client (urllib + json only, no
`anthropic` package) — used solely by demand_signals.py to read a news
item and decide whether it names a real organisation adopting an AI
tool at scale. This is AOS's first runtime with an external paid API
dependency; every other employee stays stdlib-only. Never called
unless ANTHROPIC_API_KEY is set — its absence is a clean skip, not an
error, matching every other connector's credential-missing behaviour.
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
        "Decide whether this news item describes a SPECIFIC, NAMED organisation "
        "(not the AI vendor itself) deploying, adopting, or rolling out an AI tool "
        "or system at meaningful scale (e.g. across many employees or a whole "
        "department) — the kind of event that signals that organisation will soon "
        "need AI governance, human oversight, deployment controls, or risk "
        "assessment. A generic product-feature announcement, a vendor's own "
        "roadmap post, or vague/speculative coverage with no named adopting "
        "organisation is NOT a demand signal."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "isDemandSignal": {
                "type": "boolean",
                "description": "true only if a specific, named organisation is described as adopting/deploying an AI tool at scale",
            },
            "organisation": {
                "type": "string",
                "description": "the named organisation adopting the AI tool; empty string if isDemandSignal is false",
            },
            "aiTool": {
                "type": "string",
                "description": "the AI tool/product being adopted, e.g. 'Microsoft Copilot'; empty string if unknown",
            },
            "scale": {
                "type": "string",
                "description": "the scale mentioned, verbatim if possible, e.g. '40,000 employees'; empty string if not stated",
            },
            "industry": {
                "type": "string",
                "description": "the organisation's industry, only if stated or unambiguous from the text; empty string otherwise",
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "high only if the organisation and the at-scale adoption are both stated plainly and unambiguously in the text",
            },
        },
        "required": ["isDemandSignal", "organisation", "aiTool", "scale", "industry", "confidence"],
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
