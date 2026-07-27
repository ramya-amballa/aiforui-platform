#!/usr/bin/env python3
"""
Account Intelligence — Executive Account Intelligence Brief generator
(AOS Sprint 8)

Usage:
    python3 generate.py

For every organisation already qualified by Demand Intelligence (every
key in demand-intelligence/organisation-profiles.json's "organisations"
dict — the same high-confidence gate collectors/demand_signals.py
already applies), (re)generates a ten-section Executive Account
Intelligence Brief and writes it to output/account-briefs/{slug}.md,
plus a compact, searchable record in output/account-intelligence-feed.json
the dashboard's Account Intelligence page reads directly.

Read-only with respect to every other employee's own data — never
writes to organisation-profiles.json, opportunity-schema.json,
company-intelligence.json or any other employee's output. This is a
purely additive, downstream capability; Demand Intelligence's own
collection/scoring pipeline is completely unaffected by whether this
script has ever run.

Every brief is regenerated in full on every run (not gated by a
processed-index the way Sales Director's one-time-per-opportunity
packages are) — a brief is meant to always reflect the latest signal
picture for that organisation, and regenerating is cheap (no model
call, no network access).

If no organisations are qualified yet, this prints a clear message and
writes nothing — never a fabricated placeholder brief.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import account_intelligence_engine as engine  # noqa: E402

TODAY = date.today().isoformat()


def main():
    profiles = engine.load_json(engine.PROFILES_PATH, {"organisations": {}})
    organisations = profiles.get("organisations", {})

    if not organisations:
        print("No organisations qualified by Demand Intelligence yet. Nothing to do.")
        return 0

    opportunity_schema = engine.load_json(engine.OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    demand_categories_config = engine.load_demand_categories_config()
    config = engine.load_config()
    assets = engine.load_supporting_assets()

    engine.BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    feed = {
        "schema": {
            "organisation": "string", "industry": "string", "region": "string",
            "buyingReadinessBand": "string", "outreachStrategy": "string",
            "overallPriority": "number", "lastSeen": "string ISO date",
            "briefPath": "string — relative to the repo root",
            "executiveSummary": "string — Section 10, <=300 words",
        },
        "briefs": [],
    }

    for organisation, profile in organisations.items():
        markdown, feed_entry = engine.build_brief(
            profile, opportunity_schema, demand_categories_config, config, assets)

        slug = engine.slugify(organisation)
        brief_path = engine.BRIEFS_DIR / f"{slug}.md"
        brief_path.write_text(markdown, encoding="utf-8")

        feed_entry["briefPath"] = str(brief_path.relative_to(engine.REPO_ROOT))
        feed["briefs"].append(feed_entry)
        print(f"  {organisation}: brief written -> {feed_entry['briefPath']}")

    engine.save_json(engine.FEED_PATH, feed)

    report_path = RUNTIME_DIR / "output" / f"{TODAY}-account-intelligence-report.md"
    report_lines = [
        "# Account Intelligence — Daily Report",
        "",
        f"**Date:** {TODAY}",
        f"**Briefs generated:** {len(feed['briefs'])}",
        "",
    ]
    for entry in feed["briefs"]:
        report_lines.append(
            f"- **{entry['organisation']}** ({entry['industry']}) — priority {entry['overallPriority']}, "
            f"{entry['buyingReadinessBand']} band, outreach: {entry['outreachStrategy']}"
        )
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n{len(feed['briefs'])} brief(s) generated. Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
