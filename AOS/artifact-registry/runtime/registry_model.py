"""
Artifact Registry — data model (AOS Architecture Constitution, Phase 1)

Per ARCHITECTURE-CONSTITUTION.md Section 3 and
architecture-v2/aos-v2-architecture.md: this is an additive metadata
index over AOS/output/, never a replacement for it. Every function
here is read-only with respect to the artifacts it describes — it
never writes into any employee's own output, and no employee imports
this module to change its own behavior. Building the index is entirely
a Phase 1 concern (see registry_builder.py); this module only defines
what a record looks like and how it is derived.

Deliberately excluded from this model, per the phased plan:
  - Confidence scoring (Phase 3)
  - Structural verification / validation flags (Phase 3)
  - A query API (Phase 2 — see registry_query.py once it exists)
  - Any lifecycle transition beyond the constant "published" (Phase 1
    only ever reads files an employee has already finished writing;
    there is no "draft" stage upstream of this index yet)
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import registry_validation  # noqa: E402

RUNTIME_DIR = Path(__file__).resolve().parent
ARTIFACT_REGISTRY_DIR = RUNTIME_DIR.parent
AOS_DIR = ARTIFACT_REGISTRY_DIR.parent
REPO_ROOT = AOS_DIR.parent

OUTPUT_DIR = AOS_DIR / "output"
ORCHESTRATOR_CONFIG_PATH = AOS_DIR / "orchestrator" / "runtime" / "config" / "orchestrator-config.json"

INDEX_SCHEMA_VERSION = "1"

# Fixed, deterministic vocabulary — a human or another employee reading
# this field never has to guess what it means. Extend this list rather
# than inventing an ad hoc string at a call site.
ARTIFACT_TYPES = (
    "daily-report",
    "feed",
    "stable-snapshot",
    "delivery-kit-component",
    "account-brief",
    "strategy-document",
    "company-profile",
    "orchestrator-report",
    "orchestrator-log",
    "orchestrator-status",
    "daily-brief-archive",
    "other",
)

_DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")


def slugify(text):
    """Identical to company-360/reverse-job-hunt/account-intelligence's
    own slugify() — reused verbatim, not re-derived, so an organisation
    lookup against the registry matches the exact same path segment
    those employees already write (delivery-kits/<slug>/,
    account-briefs/<slug>.md, strategies/<slug>.md,
    company-profiles/<slug>.md)."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_json(path, default=None):
    if not Path(path).exists():
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def stable_artifact_id(relative_path):
    """Deterministic across rebuilds: the same file path always gets
    the same ID, independent of its content. Identifies a *slot* in
    the output tree, not a specific version of what's in it — that's
    what contentHash is for. Rebuilding the index from a clean scan
    reproduces every existing ID exactly."""
    digest = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()
    return f"art_{digest[:16]}"


def content_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def extract_produced_date(relative_path):
    """A date embedded in the filename itself — already this codebase's
    own convention (YYYY-MM-DD-employee-report.md) — is far more
    reliable than filesystem mtime, which git checkout does not
    preserve. Returns None honestly when no date is present, rather
    than guessing one from mtime."""
    match = _DATE_PATTERN.search(Path(relative_path).name)
    return match.group(1) if match else None


def classify_artifact(relative_path):
    """Rule-based, deterministic, explainable — matches this whole
    project's convention of never using an opaque model where a fixed
    rule works. Every rule below is derived from a real path pattern
    that exists in AOS's own employee code, not guessed."""
    parts = Path(relative_path).parts
    name = Path(relative_path).name

    if len(parts) >= 2 and parts[0] == "output" and parts[1] == "orchestrator":
        if len(parts) >= 3 and parts[2] == "logs":
            return "orchestrator-log"
        if len(parts) >= 3 and parts[2] == "reports":
            return "orchestrator-report"
        if name == "status.json":
            return "orchestrator-status"
        return "other"

    if len(parts) >= 2 and parts[0] == "output" and parts[1] == "daily-briefs":
        return "daily-brief-archive"

    if len(parts) < 3 or parts[0] != "output":
        return "other"

    # parts[1] is the employee folder from here on
    rest = parts[2:]

    if "delivery-kits" in rest:
        return "delivery-kit-component"
    if "account-briefs" in rest:
        return "account-brief"
    if "strategies" in rest:
        return "strategy-document"
    if "company-profiles" in rest:
        return "company-profile"

    if name.endswith("-feed.json"):
        return "feed"

    if _DATE_PATTERN.search(name):
        return "daily-report"

    if name.endswith(".md") or name.endswith(".json") or name.endswith(".html"):
        return "stable-snapshot"

    return "other"


def employee_for_path(relative_path):
    """The employee folder is always the segment right after output/,
    for anything that isn't a system artifact (orchestrator, daily
    briefs). Returns None for those — they belong to the platform, not
    to any one employee."""
    parts = Path(relative_path).parts
    if len(parts) < 3 or parts[0] != "output":
        return None
    if parts[1] in ("orchestrator", "daily-briefs"):
        return None
    return parts[1]


def load_dependency_graph(config_path=ORCHESTRATOR_CONFIG_PATH):
    """Reads the orchestrator's own, already-real dependsOn graph —
    no new data entry, no employee change. This is coarse-grained,
    employee-level lineage: which employees a given employee's own
    code is allowed to have read from, per the same dependency graph
    the Orchestrator itself validates before running. It is not
    per-instance data lineage (which specific upstream artifact
    version fed this exact file) — that would require an employee to
    declare it at write time, which Phase 1 deliberately does not
    require of any employee, per the Constitution's "existing
    employees continue to function unchanged" requirement."""
    config = load_json(config_path, {"employees": []})
    return {e["key"]: list(e.get("dependsOn", [])) for e in config.get("employees", [])}


def lineage_for_employee(employee, dependency_graph):
    if employee is None:
        return {
            "employee": None,
            "dependsOnEmployees": [],
            "note": "Platform artifact (orchestrator or daily-briefs archive) — not owned by a single employee.",
        }
    return {
        "employee": employee,
        "dependsOnEmployees": dependency_graph.get(employee, []),
        "note": ("Coarse-grained, derived from orchestrator-config.json's dependsOn graph at build "
                 "time — names which employees this one is allowed to have read from, not which "
                 "specific upstream artifact version it actually read for this exact file."),
    }


def build_artifact_record(absolute_path, relative_path, dependency_graph):
    stat = absolute_path.stat()
    employee = employee_for_path(relative_path)
    artifact_type = classify_artifact(relative_path)
    return {
        "id": stable_artifact_id(relative_path),
        "employee": employee,
        "path": relative_path,
        "artifactType": artifact_type,
        "producedDate": extract_produced_date(relative_path),
        "contentHash": content_hash(absolute_path),
        "sizeBytes": stat.st_size,
        "fileModifiedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "schemaVersion": "unversioned",
        # Phase 3 — opportunistic only, never inferred. See
        # registry_validation.extract_confidence()'s own docstring for
        # exactly which real, pre-existing patterns this surfaces.
        "confidence": registry_validation.extract_confidence(absolute_path, artifact_type),
        "lifecycle": "published",
        "lineage": lineage_for_employee(employee, dependency_graph),
        # Phase 3 — advisory only. A non-empty list never blocks this
        # artifact from being indexed; it only annotates a structural
        # anomaly for a human (or a future enforcing verification
        # layer, per ARCHITECTURE-CONSTITUTION.md) to look at.
        "validationFlags": registry_validation.validate_artifact(absolute_path, relative_path, artifact_type),
    }
