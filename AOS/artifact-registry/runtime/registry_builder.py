#!/usr/bin/env python3
"""
Artifact Registry — index builder (AOS Architecture Constitution, Phase 1)

Usage:
    python3 registry_builder.py

Scans AOS/output/ (nothing else) and writes one full index rebuilt
from scratch every run — artifact-index.json is a derived, disposable
view, never a second copy of the data it describes. Deleting it and
re-running this script reproduces it exactly; nothing is lost, because
nothing here is a system of record. Markdown and JSON files under
output/ remain the canonical, human-readable artifacts, exactly as the
Constitution requires.

This script changes no employee's code or behavior. It only reads
what employees already wrote.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import registry_model as model  # noqa: E402

# Lives under output/, alongside every other employee's generated
# artifacts, now that this runs as part of the daily Orchestrator
# cycle — it is real daily production data, committed the same way,
# not a disposable local-only test artifact anymore.
INDEX_PATH = model.AOS_DIR / "output" / "artifact-registry" / "artifact-index.json"

INDEX_SCHEMA = {
    "schemaVersion": "string — this index format's own version, bumped only if the top-level shape changes",
    "generatedAt": "string — ISO 8601 UTC timestamp of this build",
    "sourceRoot": "string — relative to AOS/, the directory tree this index was built from",
    "orchestratorConfigPath": "string — relative to AOS/, where the employee-level dependency graph used for lineage was read from",
    "artifactCount": "number — total artifacts indexed",
    "employeeCounts": "object — employee key -> number of artifacts indexed for that employee (platform artifacts under 'orchestrator'/'daily-briefs' excluded)",
    "validationSummary": "object — flaggedCount (artifacts with at least one Phase 3 structural flag, advisory only, never blocking) and flagCounts (flag name -> occurrence count)",
    "artifacts": "array of artifact records — see registry_model.py's build_artifact_record() for the exact per-record shape",
}


def scan_output_files(output_dir):
    """Every regular file under output/, in stable sorted order, with
    its path relative to AOS/ — the same relative-path convention every
    other employee already uses when citing a source file."""
    aos_dir = output_dir.parent
    files = sorted(p for p in output_dir.rglob("*") if p.is_file())
    return [(p, str(p.relative_to(aos_dir))) for p in files]


def build_index(output_dir=None, config_path=None):
    # Read module attributes dynamically (not as mutable default
    # arguments) so tests can patch model.OUTPUT_DIR / model.
    # ORCHESTRATOR_CONFIG_PATH and have main()'s no-argument call
    # actually observe the patched value.
    if output_dir is None:
        output_dir = model.OUTPUT_DIR
    if config_path is None:
        config_path = model.ORCHESTRATOR_CONFIG_PATH

    dependency_graph = model.load_dependency_graph(config_path)
    artifacts = []
    employee_counts = {}
    flag_counts = {}
    flagged_count = 0

    for absolute_path, relative_path in scan_output_files(output_dir):
        record = model.build_artifact_record(absolute_path, relative_path, dependency_graph)
        artifacts.append(record)
        if record["employee"]:
            employee_counts[record["employee"]] = employee_counts.get(record["employee"], 0) + 1
        if record["validationFlags"]:
            flagged_count += 1
            for flag in record["validationFlags"]:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1

    # AOS_DIR is derived from output_dir's own parent, not the module's
    # fixed constant, so this works whether output_dir is the real
    # AOS/output/ or a test fixture rooted somewhere else entirely.
    aos_dir = output_dir.parent

    try:
        orchestrator_config_relative = str(config_path.relative_to(aos_dir))
    except ValueError:
        orchestrator_config_relative = str(config_path)

    return {
        "schema": INDEX_SCHEMA,
        "schemaVersion": model.INDEX_SCHEMA_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceRoot": str(output_dir.relative_to(aos_dir)),
        "orchestratorConfigPath": orchestrator_config_relative,
        "artifactCount": len(artifacts),
        "employeeCounts": dict(sorted(employee_counts.items())),
        "validationSummary": {
            "flaggedCount": flagged_count,
            "flagCounts": dict(sorted(flag_counts.items())),
        },
        "artifacts": artifacts,
    }


def save_index(index, path=None):
    if path is None:
        path = INDEX_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        import json
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def main():
    index = build_index()
    written_path = save_index(index)
    print(f"Artifact Registry: {index['artifactCount']} artifact(s) indexed "
          f"across {len(index['employeeCounts'])} employee(s).")
    try:
        print(f"Index written to {written_path.relative_to(model.REPO_ROOT)}")
    except ValueError:
        print(f"Index written to {written_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
