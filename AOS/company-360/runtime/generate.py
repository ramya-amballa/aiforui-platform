#!/usr/bin/env python3
"""
Company 360 — generator (AOS Sprint 19)

Usage:
    python3 generate.py

For every organisation in demand-intelligence/organisation-profiles.json
(the broadest, canonical per-organisation store), joins in whatever
already exists across Account Intelligence, CRM, Relationship
Intelligence, Reverse Job Hunt, Revenue Hunter's pipeline, Service
Mapping and Delivery Intelligence — read-only throughout, computing no
new fact. Writes one company-360-feed.json (for the dashboard table)
and one printable company-profiles/{slug}.md per organisation.

Regenerated in full every run — unlike Sales Director's proposals or
Delivery Intelligence's kits, nothing here is founder-edited, so there
is nothing to protect from being overwritten.

If no organisation has been profiled yet by Demand Intelligence, this
prints a clear message and writes nothing — never a fabricated view.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import company_360_engine as engine  # noqa: E402

TODAY = date.today().isoformat()


def main():
    profiles_data = engine.load_json(engine.ORGANISATION_PROFILES_PATH, {"organisations": {}})
    organisations = profiles_data.get("organisations", {})

    if not organisations:
        print("No organisations profiled yet by Demand Intelligence. Nothing to do.")
        return 0

    opportunity_schema = engine.load_json(engine.OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    ai_feed = engine.load_json(engine.ACCOUNT_INTELLIGENCE_FEED_PATH, {"briefs": []})
    crm_data = engine.load_json(engine.CRM_PATH, {"companies": []})
    relationship_feed = engine.load_json(engine.RELATIONSHIP_FEED_PATH, {"people": []})
    rjh_feed = engine.load_json(engine.REVERSE_JOB_HUNT_FEED_PATH, {"strategies": []})
    pipeline_data = engine.load_json(engine.PIPELINE_PATH, {"pipeline": []})
    service_recommendations = engine.load_json(
        engine.SERVICE_RECOMMENDATIONS_PATH, {"recommendations": {}}
    ).get("recommendations", {})
    # Founder-maintained, read-only — see company_360_engine.py's own
    # module docstring and delivery_intelligence_engine.py's precedent.
    delivery_log = engine.load_json(engine.DELIVERY_LOG_PATH, {"engagements": {}})
    delivery_feed = engine.load_json(engine.DELIVERY_INTELLIGENCE_FEED_PATH, {"engagements": []})

    engine.PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    entries = []
    for organisation, profile in organisations.items():
        company_360 = engine.build_company_360(
            organisation, profile, ai_feed, crm_data, relationship_feed, rjh_feed,
            pipeline_data, opportunity_schema, service_recommendations, delivery_log, delivery_feed,
        )
        slug = engine.slugify(organisation)
        profile_path = engine.PROFILES_DIR / f"{slug}.md"
        profile_path.write_text(engine.render_company_360_markdown(company_360), encoding="utf-8")

        entries.append({
            "organisation": organisation,
            "industry": company_360["industry"],
            "buyingReadinessBand": company_360["demandIntelligence"]["buyingReadinessBand"],
            "existingRelationship": (company_360["crm"] or {}).get("existingRelationship", "none"),
            "deliveryPhase": company_360["deliveryIntelligence"]["phase"],
            "pipelineEntryCount": len(company_360["pipeline"]),
            "profilePath": str(profile_path.relative_to(engine.REPO_ROOT)),
        })
        print(f"  {organisation}: 360 profile written -> {profile_path.relative_to(engine.REPO_ROOT)}")

    feed = {
        "schema": {
            "organisation": "string", "industry": "string", "buyingReadinessBand": "string",
            "existingRelationship": "string", "deliveryPhase": "string", "pipelineEntryCount": "number",
            "profilePath": "string — relative to the repo root",
        },
        "companies": entries,
    }
    engine.save_json(engine.FEED_PATH, feed)

    report_path = RUNTIME_DIR / "output" / f"{TODAY}-company-360-report.md"
    report_lines = [
        "# Company 360 — Daily Report",
        "",
        f"**Date:** {TODAY}",
        f"**Organisations profiled:** {len(entries)}",
        "",
    ]
    for e in entries:
        report_lines.append(f"- **{e['organisation']}** — {e['buyingReadinessBand']} buying readiness, "
                             f"relationship: {e['existingRelationship']}, delivery phase: {e['deliveryPhase']}")
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n{len(entries)} organisation(s) profiled. Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
