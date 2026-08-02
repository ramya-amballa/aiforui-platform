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

Also wires in schema-contracts/runtime/'s schema_validator.py where a
real pilot Schema Contract exists for an artifact's exact path — a
deliberate, considered exception to "no cross-employee Python
imports": schema-contracts and artifact-registry are both shared
platform infrastructure, not employees with business logic, so there
is no isolation invariant being broken here, only the ordinary
software-engineering case of one shared library using another. See
schema-contracts/schema-contracts-model.md.
"""

import json
import re
import sys
from pathlib import Path

_SCHEMA_CONTRACTS_RUNTIME = Path(__file__).resolve().parent.parent.parent / "schema-contracts" / "runtime"
if str(_SCHEMA_CONTRACTS_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_SCHEMA_CONTRACTS_RUNTIME))

try:
    import schema_validator  # noqa: E402
except ImportError:
    schema_validator = None

_SCHEMAS_DIR = _SCHEMA_CONTRACTS_RUNTIME / "schemas"

# Path suffix -> schema filename. Deliberately a short, explicit,
# hand-maintained list of the real pilot Schema Contracts that exist
# today — extend only as new schemas are actually authored, never
# guess a mapping for a schema that doesn't exist yet.
_SCHEMA_CONTRACTS_BY_PATH_SUFFIX = {
    "output/account-intelligence/account-intelligence-feed.json": "account-intelligence-feed.schema.json",
    "output/artifact-registry/artifact-index.json": "artifact-index.schema.json",
}

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


def validate_artifact(absolute_path, relative_path, artifact_type):
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

    data = None
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

    schema_filename = _SCHEMA_CONTRACTS_BY_PATH_SUFFIX.get(relative_path)
    if schema_filename and schema_validator is not None and data is not None:
        schema = schema_validator.load_schema(_SCHEMAS_DIR / schema_filename)
        for violation in schema_validator.validate_against_schema(data, schema):
            flags.append(f"schema-contract:{violation}")

    return flags
