#!/usr/bin/env python3
"""
Relevance Cleanup v1 — one-time historical migration.

Usage:
    python3 cleanup_relevance_v1.py

Not part of the daily pipeline and never invoked by ingest.py,
collect.py, or any scheduled workflow. Run by hand, once, to bring
opportunities that were scored and routed *before* relevance.py
existed into alignment with it.

Reprocesses every existing entry in ../opportunity-schema.json through
relevance.compute_relevance(). Anything scoring below
relevance.RELEVANCE_THRESHOLD is removed from:
  - opportunity-schema.json (the opportunity entry itself)
  - 08-Revenue-Hunter/pipeline.json (any entry whose sourceRef matches)
  - 06-CRM/company-intelligence.json (any outreachHistory entry that
    traces back to this opportunity via the exact marker string
    route_to_crm() writes; a company record is removed outright only
    if every one of its outreachHistory entries traces to a removed
    opportunity and it carries no other real content — no recruiter,
    no tailored positioning, no prior applications, no notes)

Nothing is deleted. Every removed opportunity — plus whatever pipeline
or CRM data was removed alongside it — is written to
archive/relevance-cleanup-v1/archive-manifest.json (queryable) and
summarised in archive/relevance-cleanup-v1/cleanup-report.md (for a
human to read).

Safe to re-run: a second run reprocesses whatever remains, and since
everything left already cleared the threshold the first time, it will
find nothing further to remove.
"""

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import relevance

RUNTIME_DIR = Path(__file__).resolve().parent
DEMAND_INTELLIGENCE_DIR = RUNTIME_DIR.parent
AOS_DIR = DEMAND_INTELLIGENCE_DIR.parent
REPO_ROOT = AOS_DIR.parent

OPPORTUNITY_SCHEMA_PATH = DEMAND_INTELLIGENCE_DIR / "opportunity-schema.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"

ARCHIVE_DIR = RUNTIME_DIR / "archive" / "relevance-cleanup-v1"
ARCHIVE_MANIFEST_PATH = ARCHIVE_DIR / "archive-manifest.json"
CLEANUP_REPORT_PATH = ARCHIVE_DIR / "cleanup-report.md"

CLEANUP_TIMESTAMP = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

DEFAULT_MANIFEST = {
    "schema": {
        "opportunityId": "string — the id this entry had in opportunity-schema.json before removal",
        "cleanupTimestamp": "string — ISO 8601 timestamp of the migration run that removed this record",
        "relevanceScore": "number — 0-100, recomputed by relevance.compute_relevance() against the stored record",
        "rejectionReason": "string — why it fell below relevance.RELEVANCE_THRESHOLD",
        "originalOpportunityRecord": "object — the complete, unmodified opportunity-schema.json entry",
        "removedPipelineEntries": "array of objects — any 08-Revenue-Hunter/pipeline.json entries removed alongside it (sourceRef match)",
        "removedCrm": "object or null — {companyName, outreachEntriesRemoved, companyRecordFullyRemoved, fullCompanyRecord} if this opportunity's organisation had any CRM record affected",
    },
    "runs": [],
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def outreach_marker(opportunity):
    return f"Demand Intelligence logged: {opportunity['title']} ("


def clean_pipeline(opportunity_id, pipeline_data):
    kept, removed = [], []
    for entry in pipeline_data["pipeline"]:
        if entry.get("sourceRef") == opportunity_id:
            removed.append(entry)
        else:
            kept.append(entry)
    pipeline_data["pipeline"] = kept
    return removed


def clean_crm(opportunity, crm_data):
    marker = outreach_marker(opportunity)
    for company in crm_data["companies"]:
        if company.get("companyName") != opportunity.get("organisation"):
            continue

        history = company.get("outreachHistory", [])
        keep_history = [h for h in history if marker not in h.get("summary", "")]
        removed_entries = [h for h in history if marker in h.get("summary", "")]
        if not removed_entries:
            continue

        has_other_content = bool(
            keep_history
            or company.get("recruiter")
            or company.get("tailoredPositioning")
            or company.get("previousApplications")
            or company.get("notes")
        )
        if not has_other_content:
            original_record = deepcopy(company)
            crm_data["companies"].remove(company)
            return {
                "companyName": company["companyName"],
                "outreachEntriesRemoved": removed_entries,
                "companyRecordFullyRemoved": True,
                "fullCompanyRecord": original_record,
            }
        company["outreachHistory"] = keep_history
        return {
            "companyName": company["companyName"],
            "outreachEntriesRemoved": removed_entries,
            "companyRecordFullyRemoved": False,
            "fullCompanyRecord": None,
        }
    return None


def generate_cleanup_report(entries):
    lines = [
        "# Relevance Cleanup v1 — One-Time Migration Report",
        "",
        f"**Run at:** {CLEANUP_TIMESTAMP}",
        f"**Opportunities removed:** {len(entries)}",
        "",
        "| Opportunity | Organisation | Relevance | Reason |",
        "|---|---|---|---|",
    ]
    for e in entries:
        title = e["originalOpportunityRecord"].get("title", "")
        org = e["originalOpportunityRecord"].get("organisation", "")
        lines.append(f"| {title} | {org} | {e['relevanceScore']} | {e['rejectionReason']} |")

    pipeline_removed = sum(len(e["removedPipelineEntries"]) for e in entries)
    crm_touched = [e for e in entries if e["removedCrm"]]
    lines += [
        "",
        f"**Pipeline entries removed from 08-Revenue-Hunter/pipeline.json:** {pipeline_removed}",
        f"**CRM records touched in 06-CRM/company-intelligence.json:** {len(crm_touched)}",
        "",
        "---",
        "",
        "*Nothing here was permanently deleted. The complete original record for every",
        "row above — plus any pipeline or CRM data removed alongside it — is in",
        "archive-manifest.json in this same folder.*",
    ]
    return "\n".join(lines)


def main():
    schema_data = load_json(OPPORTUNITY_SCHEMA_PATH)
    pipeline_data = load_json(PIPELINE_PATH)
    crm_data = load_json(CRM_PATH)

    kept_opportunities = []
    archive_entries = []

    for opportunity in schema_data["opportunities"]:
        result = relevance.compute_relevance(opportunity)
        if result["score"] >= relevance.RELEVANCE_THRESHOLD:
            kept_opportunities.append(opportunity)
            continue

        removed_pipeline = clean_pipeline(opportunity["id"], pipeline_data)
        removed_crm = clean_crm(opportunity, crm_data)

        archive_entries.append({
            "opportunityId": opportunity["id"],
            "cleanupTimestamp": CLEANUP_TIMESTAMP,
            "relevanceScore": result["score"],
            "rejectionReason": result["reason"] or "Below relevance threshold on reprocessing.",
            "originalOpportunityRecord": opportunity,
            "removedPipelineEntries": removed_pipeline,
            "removedCrm": removed_crm,
        })
        print(f"  removed {opportunity['id']}: {opportunity['title']} -> relevance {result['score']}/100 "
              f"({len(removed_pipeline)} pipeline entr{'y' if len(removed_pipeline) == 1 else 'ies'}, "
              f"crm {'touched' if removed_crm else 'unaffected'})")

    if not archive_entries:
        print("Every existing opportunity already clears the relevance threshold. Nothing to clean up.")
        return 0

    schema_data["opportunities"] = kept_opportunities
    save_json(OPPORTUNITY_SCHEMA_PATH, schema_data)
    save_json(PIPELINE_PATH, pipeline_data)
    save_json(CRM_PATH, crm_data)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_json(ARCHIVE_MANIFEST_PATH) if ARCHIVE_MANIFEST_PATH.exists() else DEFAULT_MANIFEST
    manifest.setdefault("runs", [])
    manifest["runs"].append({"cleanupTimestamp": CLEANUP_TIMESTAMP, "entries": archive_entries})
    save_json(ARCHIVE_MANIFEST_PATH, manifest)

    CLEANUP_REPORT_PATH.write_text(generate_cleanup_report(archive_entries), encoding="utf-8")

    print(f"\n{len(archive_entries)} opportunities removed and archived. "
          f"{len(kept_opportunities)} remain in opportunity-schema.json.")
    print(f"Archive: {ARCHIVE_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
