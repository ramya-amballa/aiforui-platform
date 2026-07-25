#!/usr/bin/env python3
"""
Opportunity Hunter — Integration Status Dashboard & Collection
Verification Report

Usage:
    python3 integration_status.py

Called automatically at the end of collect.py's main(), so both
outputs regenerate every day as a side effect of the normal collection
run — no separate schedule, no Orchestrator change needed. Also
runnable standalone for a status check between runs.

Reads only (never writes to any of these):
  - config/sources.json         — per-connector config/status
  - snapshots/{date}-collection-snapshot.json — today's real counts
    and errors, if collect.py has already run today

Writes:
  - integration-status-dashboard.md (stable, overwritten every run) —
    is each connector Connected / Awaiting credentials / Awaiting API
    access / Disabled, and exactly what input it's waiting on
  - output/{date}-collection-verification-report.md (dated) — what
    actually happened on today's specific run: did each source run,
    how many postings it found, any error

This script computes status only from what config/sources.json and
the collection snapshot already say — it does not re-implement or
second-guess any connector's own collection logic, and it never scores,
classifies, or routes an opportunity; that stays ingest.py's job
alone, unchanged.
"""

import json
import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
OPPORTUNITY_HUNTER_DIR = RUNTIME_DIR.parent
AOS_DIR = OPPORTUNITY_HUNTER_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_DIR = RUNTIME_DIR / "config"
SNAPSHOTS_DIR = RUNTIME_DIR / "snapshots"
OUTPUT_DIR = RUNTIME_DIR / "output"
STABLE_DASHBOARD_PATH = RUNTIME_DIR / "integration-status-dashboard.md"

TODAY = date.today().isoformat()

CONNECTED = "Connected"
AWAITING_CREDENTIALS = "Awaiting credentials"
AWAITING_API_ACCESS = "Awaiting API access"
DISABLED = "Disabled"

# Phase 1 sources, in the order given in the Production Sprint request.
# "requiredInputKeys" are the sources.json fields that must be non-empty
# for the connector to actually return data; "credentialNature"
# distinguishes a real secret from a public target identifier, since
# both are bucketed under "Awaiting credentials" but mean different
# things to whoever is activating this.
PHASE_1_SOURCES = [
    {
        "key": "upwork", "name": "Upwork",
        "requiredInputKeys": ["apiKey", "apiSecret", "refreshToken"],
        "credentialNature": "real OAuth2 secrets (client ID, client secret, refresh token)",
        "accessPath": "credentials",
    },
    {
        "key": "linkedinJobs", "name": "LinkedIn Jobs",
        "requiredInputKeys": ["apiKey"],
        "credentialNature": "a Talent Solutions/Jobs API partner access token",
        "accessPath": "api_access",
    },
    {
        "key": "wellfound", "name": "Wellfound",
        "requiredInputKeys": ["apiKey"],
        "credentialNature": "no known public/partner API exists yet to authenticate against",
        "accessPath": "api_access",
    },
    {
        "key": "remoteok", "name": "RemoteOK",
        "requiredInputKeys": [],
        "credentialNature": "none — single public global feed",
        "accessPath": "none",
    },
    {
        "key": "greenhouse", "name": "Greenhouse",
        "requiredInputKeys": ["boardTokens"],
        "credentialNature": "public company board tokens (not secret) — one per company to monitor",
        "accessPath": "credentials",
    },
    {
        "key": "lever", "name": "Lever",
        "requiredInputKeys": ["companies"],
        "credentialNature": "public company slugs (not secret) — one per company to monitor",
        "accessPath": "credentials",
    },
    {
        "key": "ashby", "name": "Ashby",
        "requiredInputKeys": ["jobBoardNames"],
        "credentialNature": "public job board names (not secret) — one per organisation to monitor",
        "accessPath": "credentials",
    },
]


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_input_present(config, key):
    value = config.get(key)
    if isinstance(value, list):
        return len(value) > 0
    return bool(value)


def compute_status(source_def, config):
    missing = [k for k in source_def["requiredInputKeys"] if not is_input_present(config, k)]
    if not missing:
        return CONNECTED, []
    if source_def["accessPath"] == "api_access":
        return AWAITING_API_ACCESS, missing
    if source_def["accessPath"] == "credentials":
        return AWAITING_CREDENTIALS, missing
    return CONNECTED, []


def render_dashboard(sources_config, snapshot):
    per_source_counts = (snapshot or {}).get("perSource", {})
    rows = []
    for source_def in PHASE_1_SOURCES:
        config = sources_config.get(source_def["key"], {})
        status, missing = compute_status(source_def, config)
        count_note = ""
        if source_def["key"] in per_source_counts:
            count_note = f" ({per_source_counts[source_def['key']]} found in last run)"
        rows.append({
            "name": source_def["name"],
            "status": status,
            "requires": source_def["credentialNature"] if missing or status != CONNECTED
                        else "already configured",
            "note": count_note,
        })

    connected = [r for r in rows if r["status"] == CONNECTED]
    awaiting_creds = [r for r in rows if r["status"] == AWAITING_CREDENTIALS]
    awaiting_access = [r for r in rows if r["status"] == AWAITING_API_ACCESS]

    lines = [
        "# Opportunity Hunter — Integration Status Dashboard",
        "",
        f"**Generated:** {TODAY}",
        "",
        "*Regenerated automatically at the end of every collection run "
        "(`collect.py` calls `integration_status.py`). Reflects "
        "`config/sources.json`'s current configuration and the most "
        "recent collection snapshot; regenerate by re-running collection, "
        "do not hand-edit.*",
        "",
        "## Phase 1 Sources",
        "",
        "| Source | Status | Requires | Last Run |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['name']} | {r['status']} | {r['requires']} |{r['note']} |")

    lines += [
        "",
        f"**Summary:** {len(connected)} of 7 Phase 1 sources Connected, "
        f"{len(awaiting_creds)} Awaiting credentials, {len(awaiting_access)} Awaiting API access, "
        f"0 Disabled.",
        "",
        "## Disabled",
        "",
        "No Phase 1 source is disabled — every one has a real, compliant "
        "path forward (a working API today, or a documented API/partner "
        "path to activate later).",
        "",
        "## Approaches Deliberately Not Built",
        "",
        "Per instruction, brittle scraping that would violate a "
        "platform's Terms of Service was considered and rejected, not "
        "built, for the two sources with no compliant API path today:",
        "",
        "- **LinkedIn Jobs** — LinkedIn's Terms of Service explicitly "
        "prohibit scraping job listings; no scraping fallback was built. "
        "The only path is Talent Solutions/Jobs API partner access.",
        "- **Wellfound** — no documented public API or partner access "
        "path exists today; no scraping fallback was built. If Wellfound "
        "introduces one, `wellfound.py` is already wired to receive it.",
        "",
        "## Configuration",
        "",
        "See `../CONNECTOR-CONFIGURATION-GUIDE.md` for exactly how to "
        "activate each connector above, and "
        "`config/credentials.template.env` for the environment variable "
        "names real secrets should be set as — never commit a real "
        "secret into `config/sources.json`.",
        "",
    ]
    return "\n".join(lines)


def render_verification_report(sources_config, snapshot):
    per_source_counts = (snapshot or {}).get("perSource", {})
    per_source_errors = (snapshot or {}).get("perSourceErrors", {})
    total = (snapshot or {}).get("totalDiscovered")

    lines = [
        "# Daily Collection Verification Report",
        "",
        f"**Date:** {TODAY}",
        "",
    ]
    if snapshot is None:
        lines.append("_No collection snapshot found for today — `collect.py` has not "
                      "run yet today._")
        return "\n".join(lines) + "\n"

    lines.append(f"**Total postings discovered today (before dedup):** {total}")
    lines.append("")
    lines.append("| Source | Ran | Postings Found | Error |")
    lines.append("|---|---|---|---|")
    for source_def in PHASE_1_SOURCES:
        key = source_def["key"]
        count = per_source_counts.get(key)
        error = per_source_errors.get(key)
        ran = "Yes" if count is not None else "Not in this run"
        lines.append(f"| {source_def['name']} | {ran} | {count if count is not None else '-'} "
                      f"| {error or '-'} |")
    lines.append("")
    lines.append("A count of 0 with no error usually means the connector ran cleanly and "
                  "found nothing matching this run — not a failure. It can also mean the "
                  "underlying HTTP request itself failed (unreachable network, rate limit, "
                  "5xx): `common.http_get_json()` catches that internally and returns no "
                  "data so one source's outage never stops the rest of the run, which means "
                  "it doesn't reach this report's Error column either. Check the run's own "
                  "log/console output for a `fetch failed (...)` line for the authoritative "
                  "picture of *why* a count is 0. The Error column here only reflects an "
                  "exception that escaped all the way to collect.py's own per-source handler "
                  "(a bug in a connector, not a network condition).")
    lines.append("")
    lines.append("See `integration-status-dashboard.md` for whether a source is Connected, "
                  "still awaiting credentials/API access, or disabled.")
    lines.append("")
    return "\n".join(lines)


def main():
    sources_config = load_json(CONFIG_DIR / "sources.json", {})
    snapshot = load_json(SNAPSHOTS_DIR / f"{TODAY}-collection-snapshot.json", None)

    STABLE_DASHBOARD_PATH.write_text(render_dashboard(sources_config, snapshot), encoding="utf-8")

    OUTPUT_DIR.mkdir(exist_ok=True)
    verification_report = render_verification_report(sources_config, snapshot)
    (OUTPUT_DIR / f"{TODAY}-collection-verification-report.md").write_text(
        verification_report, encoding="utf-8"
    )

    print(f"Integration Status Dashboard written to {STABLE_DASHBOARD_PATH.relative_to(REPO_ROOT)}")
    print(f"Collection Verification Report written to "
          f"{(OUTPUT_DIR / f'{TODAY}-collection-verification-report.md').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
