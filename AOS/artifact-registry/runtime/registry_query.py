"""
Artifact Registry — read-only query API (AOS Architecture Constitution, Phase 2)

Every function here is a pure read over an already-loaded index dict
(as built by registry_builder.py) — nothing here writes to the index,
to the filesystem, or to any employee's own output. An employee that
wants registry metadata calls load_index() once, then queries the
returned dict as many times as it likes in the same run.

Availability is always optional: if the registry hasn't been built
yet, load_index() returns a valid, empty-shaped index rather than
raising — matching this project's own "no data yet" convention rather
than treating a missing registry as an error. No employee's own
behavior may depend on the registry existing; every caller must
degrade to exactly its pre-registry behavior when it doesn't.
"""

import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import registry_model as model  # noqa: E402

DEFAULT_INDEX_PATH = RUNTIME_DIR / "index" / "artifact-index.json"

EMPTY_INDEX = {
    "schemaVersion": model.INDEX_SCHEMA_VERSION,
    "generatedAt": None,
    "artifactCount": 0,
    "employeeCounts": {},
    "artifacts": [],
}


def load_index(index_path=None):
    if index_path is None:
        index_path = DEFAULT_INDEX_PATH
    if not Path(index_path).exists():
        return dict(EMPTY_INDEX)
    return model.load_json(index_path, dict(EMPTY_INDEX))


def is_available(index):
    """True only if the index was actually built at least once and has
    something in it — an empty-but-present index (a real build of a
    genuinely empty output/ tree) is distinct from "never built"."""
    return bool(index.get("generatedAt"))


def all_artifacts(index, employee=None, artifact_type=None):
    artifacts = index.get("artifacts", [])
    if employee is not None:
        artifacts = [a for a in artifacts if a.get("employee") == employee]
    if artifact_type is not None:
        artifacts = [a for a in artifacts if a.get("artifactType") == artifact_type]
    return artifacts


def _sort_key(artifact):
    # Prefer the date embedded in the filename (this project's own
    # convention, immune to git checkout resetting mtimes); fall back
    # to filesystem mtime only when no date is present.
    return (artifact.get("producedDate") or "", artifact.get("fileModifiedAt") or "")


def latest_for_employee(index, employee, artifact_type=None):
    candidates = all_artifacts(index, employee=employee, artifact_type=artifact_type)
    if not candidates:
        return None
    return max(candidates, key=_sort_key)


def get_by_id(index, artifact_id):
    for artifact in index.get("artifacts", []):
        if artifact.get("id") == artifact_id:
            return artifact
    return None


def artifacts_for_organisation(index, organisation, employee=None):
    """Every artifact whose path names this organisation as a path
    segment — delivery-kits/<slug>/, account-briefs/<slug>.md,
    strategies/<slug>.md, company-profiles/<slug>.md. This only finds
    artifacts whose *filename convention already encodes* the
    organisation; it is not a general full-text search, and it is
    silent (returns an empty list) rather than guessing when an
    employee's own convention doesn't name the organisation in the
    path at all."""
    slug = model.slugify(organisation)
    matches = []
    for artifact in all_artifacts(index, employee=employee):
        path = artifact.get("path", "")
        stem = Path(path).stem
        parts = Path(path).parts
        if stem == slug or slug in parts:
            matches.append(artifact)
    return matches


def lineage_for(index, artifact_id):
    artifact = get_by_id(index, artifact_id)
    if artifact is None:
        return None
    return artifact.get("lineage")


def flagged_artifacts(index):
    """Every artifact carrying at least one Phase 3 structural
    validation flag — advisory only. These are still fully valid,
    fully indexed artifacts; this is a worklist for a human to glance
    at, never a filter that hides anything."""
    return [a for a in index.get("artifacts", []) if a.get("validationFlags")]


def summary(index):
    """A short, human-readable status line — exactly the shape an
    employee like CEO Advisor would append as one line of context,
    never as a claim about data it doesn't actually have."""
    if not is_available(index):
        return "Not available yet — the Artifact Registry has not been built."
    return (f"{index.get('artifactCount', 0)} artifact(s) indexed across "
            f"{len(index.get('employeeCounts', {}))} employee(s), "
            f"last built {index.get('generatedAt')}.")
