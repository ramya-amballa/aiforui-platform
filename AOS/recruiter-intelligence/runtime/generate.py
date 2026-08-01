#!/usr/bin/env python3
"""
Recruiter Intelligence — daily knowledge-base refresh (AOS Sprint 10)

Usage:
    python3 generate.py

Scans demand-intelligence/opportunity-schema.json (Recruiter/Consulting
Channel entries) and crm/company-intelligence.json (companies with a
recruiter attributed) to build/refresh recruiter-profiles.json, then
writes the four requested views (Weekly Follow-up List, Dormant
Relationships, Priority Recruiters, Recruiters hiring AI Governance/
GRC/Fractional Consultants) to a compact, dashboard-facing feed.

Read-only with respect to every other employee's data. If neither
source has any recruiter/consulting-channel data yet, this prints a
clear message and writes an empty (not fabricated) feed.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import recruiter_intelligence_engine as engine  # noqa: E402

TODAY = date.today().isoformat()


def main():
    opportunity_schema = engine.load_json(engine.OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    crm_data = engine.load_json(engine.CRM_PATH, {"companies": []})
    pipeline_data = engine.load_json(engine.PIPELINE_PATH, {"pipeline": []})
    config = engine.load_config()
    profiles = engine.load_profiles()

    engine.refresh_all_profiles(opportunity_schema, crm_data, pipeline_data, config, profiles)

    if not profiles["recruiters"]:
        print("No recruiter or consulting-channel contacts on record yet. Nothing to do.")
        engine.save_json(engine.PROFILES_PATH, profiles)
        return 0

    engine.save_json(engine.PROFILES_PATH, profiles)
    feed = engine.build_feed(profiles, config)
    engine.save_json(engine.FEED_PATH, feed)

    report_path = engine.FEED_PATH.parent / f"{TODAY}-recruiter-intelligence-report.md"
    lines = [
        "# Recruiter Intelligence — Daily Report", "", f"**Date:** {TODAY}",
        f"**Contacts tracked:** {len(feed['contacts'])}", "",
        "## Weekly Follow-up List", "",
    ]
    lines += [f"- {name}" for name in feed["weeklyFollowUpList"]] or ["- None due this week."]
    lines += ["", "## Dormant Relationships", ""]
    lines += [f"- {name}" for name in feed["dormantRelationships"]] or ["- None."]
    lines += ["", "## Priority Recruiters", ""]
    lines += [f"- {name}" for name in feed["priorityRecruiters"]] or ["- None yet."]
    lines += ["", "## Recruiters Hiring AI Governance", ""]
    lines += [f"- {name}" for name in feed["hiringAiGovernance"]] or ["- None yet."]
    lines += ["", "## Recruiters Hiring GRC", ""]
    lines += [f"- {name}" for name in feed["hiringGrc"]] or ["- None yet."]
    lines += ["", "## Recruiters Hiring Fractional Consultants", ""]
    lines += [f"- {name}" for name in feed["hiringFractionalConsultants"]] or ["- None yet."]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{len(feed['contacts'])} contact(s) tracked. Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
