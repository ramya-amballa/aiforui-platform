#!/usr/bin/env python3
"""
Delivery Intelligence — generator (AOS Sprint 17 — Consulting Delivery Engine)

Usage:
    python3 generate.py

For every pipeline.json entry with stage == "won" not yet processed,
generates a full Delivery Kit (10 artifacts, each rendered from
templates/delivery/) to output/delivery-kits/{slug}/ and records it in
processed-index.json.

Critical: once a kit is generated, its files are never regenerated or
overwritten. These are living delivery documents the founder edits by
hand during real delivery (attendee names, discovery answers, workbook
scores, actual status) — clobbering them on every run would destroy
real work. A re-run only backfills artifact files a processed
engagement is missing (e.g. a new artifact type added later), exactly
like sales-director/runtime/prepare.py's own backfill mechanism — it
never touches a file that already exists.

The feed's phase/status IS refreshed every run — that's a read-only
report of delivery-log.json (the founder's own log), never a rewrite
of a generated artifact.

If no engagement has reached stage == "won" yet, this prints a clear
message and writes nothing — never a fabricated kit.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import delivery_intelligence_engine as engine  # noqa: E402

TODAY = date.today().isoformat()

DEFAULT_PROCESSED_INDEX = {
    "schema": {
        "organisation": "string — key",
        "dateGenerated": "string — ISO 8601 date, when the kit was first generated",
        "kitPath": "string — path to the kit directory, relative to the repo root",
        "artifacts": "object — {suffix: path relative to the repo root}, one per generated file",
    },
    "processed": {},
}


def missing_artifacts(record, kit_dir):
    """True if a processed engagement is missing any of the current
    ARTIFACT_SPECS files — the same 'repair, never re-fabricate the
    rest' pattern sales-director/runtime/prepare.py's own
    missing_section_paths() uses."""
    artifacts = record.get("artifacts", {})
    for _template_filename, suffix, _label in engine.ARTIFACT_SPECS:
        if suffix not in artifacts or not (engine.REPO_ROOT / artifacts[suffix]).exists():
            return True
    return False


def write_kit_files(organisation, artifacts, existing_paths=None):
    """Writes only the artifact files not already present on disk —
    never overwrites a founder-edited file. Returns {suffix: path
    relative to REPO_ROOT} for every artifact, new or pre-existing."""
    existing_paths = existing_paths or {}
    slug = engine.slugify(organisation)
    kit_dir = engine.KITS_DIR / slug
    kit_dir.mkdir(parents=True, exist_ok=True)

    paths = {}
    for _template_filename, suffix, _label in engine.ARTIFACT_SPECS:
        if suffix in existing_paths and (engine.REPO_ROOT / existing_paths[suffix]).exists():
            paths[suffix] = existing_paths[suffix]
            continue
        artifact_path = kit_dir / f"{suffix}.md"
        artifact_path.write_text(artifacts[suffix], encoding="utf-8")
        paths[suffix] = str(artifact_path.relative_to(engine.REPO_ROOT))
    return paths, kit_dir


def main():
    pipeline_data = engine.load_json(engine.PIPELINE_PATH, {"pipeline": []})
    won = engine.won_engagements(pipeline_data)

    if not won:
        print("No engagements at stage 'won' yet in pipeline.json. Nothing to do.")
        return 0

    opportunity_schema = engine.load_json(engine.OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    ai_feed = engine.load_json(engine.ACCOUNT_INTELLIGENCE_FEED_PATH, {"briefs": []})
    service_recommendations = engine.load_json(
        engine.SERVICE_RECOMMENDATIONS_PATH, {"recommendations": {}}
    ).get("recommendations", {})
    bank = engine.load_json(engine.PRACTITIONER_BANK_PATH, {})
    # AOS Sprint 23 — Engagement Templates. Static, shared config; see
    # templates/delivery/regulatory-framework-annexes.json's own comment.
    framework_config = engine.load_json(engine.REGULATORY_FRAMEWORK_ANNEXES_PATH, {"frameworkPriority": [], "frameworks": {}})
    # Founder-maintained, read-only — see delivery_intelligence_engine.py's
    # own module docstring. This engine never writes to it.
    delivery_log = engine.load_json(engine.DELIVERY_LOG_PATH, {"engagements": {}})

    processed_index = engine.load_json(RUNTIME_DIR / "processed-index.json", DEFAULT_PROCESSED_INDEX)
    processed_index.setdefault("processed", {})

    engine.KITS_DIR.mkdir(parents=True, exist_ok=True)

    generated, backfilled = [], []
    entries = []
    for pipeline_entry in won:
        organisation = pipeline_entry["organisation"]
        opportunity = engine.find_opportunity(pipeline_entry.get("sourceRef"), opportunity_schema)
        ai_entry = engine.find_account_intelligence_entry(organisation, ai_feed)
        opportunity_id = opportunity["id"] if opportunity else None
        service_recommendation = engine.find_service_recommendation(opportunity_id, service_recommendations)

        artifacts, feed_entry = engine.build_delivery_kit(
            pipeline_entry, opportunity, ai_entry, service_recommendation, bank, delivery_log, framework_config,
        )

        record = processed_index["processed"].get(organisation)
        if record is None:
            paths, kit_dir = write_kit_files(organisation, artifacts)
            processed_index["processed"][organisation] = {
                "dateGenerated": TODAY,
                "kitPath": str(kit_dir.relative_to(engine.REPO_ROOT)),
                "artifacts": paths,
            }
            generated.append(organisation)
            print(f"  {organisation}: delivery kit generated -> {processed_index['processed'][organisation]['kitPath']}")
        else:
            kit_dir = engine.KITS_DIR / engine.slugify(organisation)
            if missing_artifacts(record, kit_dir):
                paths, kit_dir = write_kit_files(organisation, artifacts, record.get("artifacts", {}))
                record["artifacts"] = paths
                backfilled.append(organisation)
                print(f"  (backfill) {organisation}: regenerated missing artifact(s) only")
            record = processed_index["processed"][organisation]

        record = processed_index["processed"][organisation]
        feed_entry["kitPath"] = record["kitPath"]
        feed_entry["artifacts"] = record["artifacts"]
        entries.append(feed_entry)

    engine.save_json(RUNTIME_DIR / "processed-index.json", processed_index)

    feed = {
        "schema": {
            "organisation": "string", "engagementRef": "string", "primaryService": "string",
            "phase": "string — from delivery-log.json, refreshed every run",
            "kitPath": "string — relative to the repo root", "artifacts": "object — {suffix: path}",
        },
        "engagements": entries,
    }
    engine.save_json(engine.FEED_PATH, feed)

    report_path = RUNTIME_DIR / "output" / f"{TODAY}-delivery-intelligence-report.md"
    report_lines = [
        "# Delivery Intelligence — Daily Report",
        "",
        f"**Date:** {TODAY}",
        f"**Won engagements tracked:** {len(entries)}",
        f"**New delivery kits generated:** {len(generated)}",
        f"**Kits backfilled (missing artifacts only):** {len(backfilled)}",
        "",
    ]
    for e in entries:
        report_lines.append(f"- **{e['organisation']}** — phase: {e['phase']}, primary service: {e['primaryService']}")
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n{len(entries)} won engagement(s) tracked, {len(generated)} new kit(s) generated, "
          f"{len(backfilled)} backfilled. Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
