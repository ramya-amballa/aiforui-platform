"""
Artifact Registry — confidence metadata & structural verification
hooks (AOS Architecture Constitution, Phase 3)

Everything here is advisory only, per ARCHITECTURE-CONSTITUTION.md's
Decision Framework and the Gemini-roadmap critique's explicit guidance:
structural checks, logged, never blocking. Nothing here changes what
gets indexed or prevents an artifact from appearing in the registry —
a "flagged" artifact is still indexed, still queryable, just annotated
honestly with what looks structurally off about it.

Confidence extraction is opportunistic, never inferred: it only
surfaces a confidence value an employee's own output already states,
in a pattern that already exists in this codebase today (Sales
Director's own "**Confidence score:** N/100" line, and JSON feed
entries already named confidenceScore/qualificationScore). It never
computes, estimates, or guesses a confidence value for an artifact
that doesn't already carry one — that would be exactly the kind of
fabrication the Constitution forbids.
"""

import json
import re

_MARKDOWN_CONFIDENCE_PATTERN = re.compile(r"\*\*Confidence score:\*\*\s*(\d+(?:\.\d+)?)\s*/\s*100")

# The exact, already-real JSON field names this codebase uses for a
# 0-100 confidence-shaped number. Extend this list only when a new
# employee introduces a *genuinely equivalent* field — never add a
# name here speculatively.
_JSON_CONFIDENCE_FIELDS = ("confidenceScore", "qualificationScore")


def _read_text_safely(absolute_path):
    try:
        return absolute_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def extract_confidence(absolute_path, artifact_type):
    """Returns a 0-100 number if, and only if, the artifact's own
    content already states one via an existing, real convention.
    Returns None otherwise — never a guess, never a default."""
    text = _read_text_safely(absolute_path)
    if text is None:
        return None

    if str(absolute_path).endswith(".json"):
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return None
        if isinstance(data, dict):
            for field in _JSON_CONFIDENCE_FIELDS:
                value = data.get(field)
                if isinstance(value, (int, float)):
                    return value
        return None

    match = _MARKDOWN_CONFIDENCE_PATTERN.search(text)
    if match:
        return float(match.group(1))
    return None


def validate_artifact(absolute_path, artifact_type):
    """A short list of structural flags, empty when nothing looks
    wrong. Every check here is cheap, deterministic, and explainable —
    no semantic judgement about whether content is *true*, only
    whether its shape matches what this codebase's own conventions
    already promise. This is deliberately narrow: it is not, and is
    not meant to become, a claim-extraction or fact-checking layer —
    see architecture-v2/gemini-enterprise-roadmap-critique.md's
    explicit rejection of that as a general-purpose mechanism."""
    flags = []

    try:
        size = absolute_path.stat().st_size
    except OSError:
        return ["file-unreadable"]

    if size == 0 and absolute_path.name != ".gitkeep":
        flags.append("empty-file")
        return flags  # nothing further to check meaningfully

    if str(absolute_path).endswith(".json"):
        text = _read_text_safely(absolute_path)
        if text is None:
            flags.append("file-unreadable")
            return flags
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            flags.append("invalid-json")
            return flags
        if artifact_type == "feed" and isinstance(data, dict) and "schema" not in data:
            flags.append("feed-missing-schema-key")

    return flags
