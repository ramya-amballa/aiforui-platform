#!/usr/bin/env python3
"""
Reverse Job Hunt — Business Development Strategy generator (AOS Sprint 9)

Usage:
    python3 generate.py

For every organisation already qualified by Demand Intelligence (every
key in demand-intelligence/organisation-profiles.json's "organisations"
dict — the same population Account Intelligence, Sprint 8, already
briefs), (re)generates a Reverse Job Hunt Strategy and writes it to
output/strategies/{slug}.md, plus a compact, sortable-by-expected-ROI
record in output/reverse-job-hunt-feed.json the dashboard's Reverse Job
Hunt page reads directly.

Read-only with respect to every other employee's own data — never
writes to organisation-profiles.json, opportunity-schema.json,
company-intelligence.json, account-intelligence-feed.json, pipeline.json
or any other employee's output. Purely additive, downstream capability;
no existing scoring logic anywhere in AOS is touched or recomputed
differently than its own employee already computes it.

Every strategy is regenerated in full on every run (not gated by a
processed-index) — a strategy is meant to always reflect the latest
signal picture for that organisation, and regenerating is cheap (no
model call, no network access).

If no organisations are qualified yet, this prints a clear message and
writes nothing — never a fabricated placeholder strategy.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import reverse_job_hunt_engine as engine  # noqa: E402

TODAY = date.today().isoformat()


def main():
    profiles = engine.load_json(engine.PROFILES_PATH, {"organisations": {}})
    organisations = profiles.get("organisations", {})

    if not organisations:
        print("No organisations qualified by Demand Intelligence yet. Nothing to do.")
        return 0

    opportunity_schema = engine.load_json(engine.OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    pipeline_data = engine.load_json(engine.PIPELINE_PATH, {"pipeline": []})
    crm_data = engine.load_json(engine.CRM_PATH, {"companies": []})
    ai_feed = engine.load_json(engine.ACCOUNT_INTELLIGENCE_FEED_PATH, {"briefs": []})
    demand_categories_config = engine.load_demand_categories_config()
    config = engine.load_config()

    engine.STRATEGIES_DIR.mkdir(parents=True, exist_ok=True)
    feed = {
        "schema": {
            "organisation": "string", "industry": "string", "buyingReadinessBand": "string",
            "entryPoint": "string", "probabilityOfEngagement": "number 0-100",
            "recommendedTimeline": "string", "consultingPotentialEstimate": "string",
            "expectedConsultingRoi": "number 0-10 or null — dashboard sort key",
            "lastSeen": "string ISO date", "strategyPath": "string — relative to the repo root",
        },
        "strategies": [],
    }

    for organisation, profile in organisations.items():
        markdown, feed_entry = engine.build_strategy(
            profile, opportunity_schema, pipeline_data, crm_data, ai_feed,
            demand_categories_config, config)

        slug = engine.slugify(organisation)
        strategy_path = engine.STRATEGIES_DIR / f"{slug}.md"
        strategy_path.write_text(markdown, encoding="utf-8")

        feed_entry["strategyPath"] = str(strategy_path.relative_to(engine.REPO_ROOT))
        feed["strategies"].append(feed_entry)
        print(f"  {organisation}: strategy written -> {feed_entry['strategyPath']} "
              f"(entry point: {feed_entry['entryPoint']}, expected ROI: {feed_entry['expectedConsultingRoi']})")

    # Sorted by Expected Consulting ROI descending before writing — the
    # feed file itself satisfies "sort companies by expected consulting
    # ROI" for any reader (dashboard or otherwise), not just the report
    # below.
    feed["strategies"].sort(key=lambda e: e["expectedConsultingRoi"] if e["expectedConsultingRoi"] is not None else -1, reverse=True)
    engine.save_json(engine.FEED_PATH, feed)

    report_path = RUNTIME_DIR / "output" / f"{TODAY}-reverse-job-hunt-report.md"
    report_lines = [
        "# Reverse Job Hunt — Daily Report",
        "",
        f"**Date:** {TODAY}",
        f"**Strategies generated:** {len(feed['strategies'])}",
        "",
    ]
    ranked = sorted(feed["strategies"], key=lambda e: e["expectedConsultingRoi"] or 0, reverse=True)
    for entry in ranked:
        report_lines.append(
            f"- **{entry['organisation']}** ({entry['industry']}) — expected ROI {entry['expectedConsultingRoi']}, "
            f"entry point: {entry['entryPoint']}, timeline: {entry['recommendedTimeline']}"
        )
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n{len(feed['strategies'])} strategy(ies) generated. Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
