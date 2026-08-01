#!/usr/bin/env python3
"""
Relationship Intelligence — daily generator (AOS Sprint 13)

Usage:
    python3 generate.py

Reads relationship-profiles.json (founder-maintained, persistent —
see ../relationship-intelligence-engine.md) plus, read-only,
06-CRM/company-intelligence.json and
demand-intelligence/organisation-profiles.json for the Relationship
Opportunity cross-reference. Writes output/{date}-relationship-
intelligence-report.md and output/relationship-intelligence-feed.json.

Never writes to relationship-profiles.json, company-intelligence.json
or organisation-profiles.json. If no people are tracked yet, prints a
clear message and writes nothing — never a fabricated report.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import relationship_intelligence_engine as engine  # noqa: E402

TODAY = date.today().isoformat()


def render_report(feed):
    lines = [
        "# Relationship Intelligence — Daily Report",
        "",
        f"**Date:** {TODAY}",
        f"**People tracked:** {len(feed['people'])}",
        "",
    ]

    lines += ["## Reconnect Recommendations", ""]
    if feed["reconnectRecommendations"]:
        by_name = {e["person"]: e for e in feed["people"]}
        for name in feed["reconnectRecommendations"]:
            e = by_name[name]
            lines.append(f"- **{name}** ({e['company']}) — {e['reconnectReason']}")
    else:
        lines.append("_No reconnect recommendations today._")
    lines.append("")

    lines += ["## Birthday Reminders", ""]
    lines += [f"- **{n}**" for n in feed["birthdayReminders"]] or ["_None this window._"]
    lines.append("")

    lines += ["## Work Anniversary Reminders", ""]
    lines += [f"- **{n}**" for n in feed["workAnniversaryReminders"]] or ["_None this window._"]
    lines.append("")

    lines += ["## Conference Reminders", ""]
    lines += [f"- **{n}**" for n in feed["conferenceReminders"]] or ["_None this window._"]
    lines.append("")

    lines += ["## At-Risk Relationships", ""]
    lines += [f"- **{n}**" for n in feed["atRiskRelationships"]] or ["_None flagged High risk today._"]
    lines.append("")

    return "\n".join(lines)


def main():
    profiles = engine.load_profiles()
    people = profiles.get("people", {})

    if not people:
        print("No relationships tracked yet in relationship-profiles.json. Nothing to do.")
        return 0

    config = engine.load_config()
    crm_data = engine.load_json(engine.CRM_PATH, {"companies": []})
    org_profiles_data = engine.load_json(engine.ORGANISATION_PROFILES_PATH, {"organisations": {}})

    feed = engine.build_feed(profiles, config, crm_data, org_profiles_data)

    engine.FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine.save_json(engine.FEED_PATH, feed)

    report_path = engine.FEED_PATH.parent / f"{TODAY}-relationship-intelligence-report.md"
    report_path.write_text(render_report(feed), encoding="utf-8")

    print(f"{len(people)} relationship(s) processed. Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
