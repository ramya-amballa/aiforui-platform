#!/usr/bin/env python3
"""
Fractional Advisory Radar — daily refresh (AOS Sprint 11)

Usage:
    python3 generate.py

Reads demand-intelligence/organisation-profiles.json (required) plus
opportunity-schema.json and pipeline.json (optional, read-only
cross-references) to classify every already-qualified organisation
into a stage (Emerging/Growing/Enterprise/Urgent), estimate Fractional
Advisory Potential, recommend an engagement model, and estimate
expected consulting revenue — writing a feed sorted by that revenue
estimate for the dashboard.

Read-only, purely additive. Reuses Demand Intelligence's own signal
classification rather than re-scanning the same public signals a
second time.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import fractional_advisory_radar_engine as engine  # noqa: E402

TODAY = date.today().isoformat()


def main():
    profiles = engine.load_json(engine.PROFILES_PATH, {"organisations": {}})
    if not profiles.get("organisations"):
        print("No organisations qualified by Demand Intelligence yet. Nothing to do.")
        return 0

    opportunity_schema = engine.load_json(engine.OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    pipeline_data = engine.load_json(engine.PIPELINE_PATH, {"pipeline": []})
    demand_categories_config = engine.load_demand_categories_config()
    config = engine.load_config()

    feed = engine.build_feed(profiles, demand_categories_config, config, opportunity_schema, pipeline_data)
    engine.save_json(engine.FEED_PATH, feed)

    report_path = engine.FEED_PATH.parent / f"{TODAY}-fractional-advisory-radar-report.md"
    lines = [
        "# Fractional Advisory Radar — Daily Report", "", f"**Date:** {TODAY}",
        f"**Organisations tracked:** {len(feed['organisations'])}", "",
        "| Organisation | Stage | Potential | Engagement Model | Expected Revenue |",
        "|---|---|---|---|---|",
    ]
    for e in feed["organisations"]:
        lines.append(
            f"| {e['organisation']} | {e['stage']} | {e['fractionalAdvisoryPotential']}/100 | "
            f"{e['recommendedEngagementModel']} | {e['expectedConsultingRevenue']['estimate']} |"
        )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{len(feed['organisations'])} organisation(s) classified. Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
