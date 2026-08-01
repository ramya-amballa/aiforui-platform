#!/usr/bin/env python3
"""
Executive Brand Intelligence — weekly generator (AOS Sprint 15)

Usage:
    python3 generate.py

Reads, read-only: demand-intelligence/organisation-profiles.json,
output/account-intelligence/account-intelligence-feed.json,
relationship-intelligence/relationship-profiles.json, and the shared
supporting-assets.json/account-intelligence-config.json. Never writes
to any of them.

Appends this run's plan to a persistent brand-plan-history.json (so the
Monthly Authority Report can roll up trailing weeks), and writes
output/{date}-executive-brand-intelligence-report.md plus
output/executive-brand-intelligence-feed.json (the Weekly Brand Plan
plus a Monthly Authority Report rollup) for the dashboard.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import executive_brand_intelligence_engine as engine  # noqa: E402

TODAY = date.today().isoformat()


def render_report(plan, monthly):
    lines = [
        "# Executive Brand Intelligence — Weekly Brand Plan",
        "",
        f"**Week of:** {plan['weekOf']}",
        f"**Companies this week:** {plan['companiesThisWeek']}",
        f"**Trending domain:** {plan['trendingDomain'] or 'Not enough signal yet'}",
        f"**Trending governance risk:** {plan['trendingGovernanceRisk'] or 'Not enough signal yet'}",
        "",
        "## Estimates",
        "",
        f"- **Visibility Impact:** {plan['visibilityImpact']}",
        f"- **Lead Generation Potential:** {plan['leadGenerationPotential']}",
        f"- **Expected Consulting Influence:** {plan['expectedConsultingInfluence']}",
        "",
        "## Companies to Engage", "",
    ]
    lines += [f"- **{c['organisation']}** ({c['industry']}) — {c['buyingReadinessBand']} readiness "
              f"({c['buyingReadinessScore']}/100)" for c in plan["companiesToEngage"]] or ["_None this week._"]

    lines += ["", "## Executives to Follow", ""]
    lines += [f"- **{e['person']}** — {e['role'] or 'Not specified'} at {e['company']}"
              for e in plan["executivesToFollow"]] or ["_No executives tracked yet in relationship-profiles.json._"]

    lines += ["", "## Topics to Write", ""]
    lines += [f"- {t}" for t in plan["topicsToWrite"]] or ["_Not enough signal yet._"]

    lines += ["", "## Products to Update", ""]
    lines += [f"- **{a['title']}** ({a['type']})" for a in plan["productsToUpdate"]] or ["_None ranked this week._"]

    lines += ["", "## Whitepapers to Publish", ""]
    lines += [f"- **{a['title']}**" for a in plan["whitepapersToPublish"]] or ["_None in the catalogue yet._"]

    lines += ["", "## Conferences to Monitor", ""]
    lines += [f"- **{c['name']}** — {c['date'] or 'date not specified'}"
              for c in plan["conferencesToMonitor"]] or ["_None tracked yet in relationship-profiles.json._"]

    lines += ["", "## Newsletter Themes", ""]
    lines += [f"- {t}" for t in plan["newsletterThemes"]] or ["_Not enough signal yet._"]

    lines += ["", "## GitHub Improvements", "", plan["githubImprovements"]]
    lines += ["", "## LinkedIn Strategy", "", plan["linkedinStrategy"]]

    lines += ["", "## Monthly Authority Report (trailing window)", ""]
    if monthly["weeksIncluded"] == 0:
        lines.append("_Not enough weekly history yet — this rolls up as more weeks run._")
    else:
        lines += [
            f"- **Weeks included:** {monthly['weeksIncluded']}",
            f"- **Most common domain:** {monthly['topDomain'] or 'Not enough signal'}",
            f"- **Most common governance risk:** {monthly['topRisk'] or 'Not enough signal'}",
            f"- **Companies engaged (deduped):** {monthly['totalCompaniesEngaged']}",
        ]
    lines.append("")
    return "\n".join(lines)


def main():
    config = engine.load_config()
    org_profiles = engine.load_json(engine.ORGANISATION_PROFILES_PATH, {"organisations": {}})
    account_feed = engine.load_json(engine.ACCOUNT_INTELLIGENCE_FEED_PATH, {"briefs": []})
    relationship_profiles = engine.load_json(engine.RELATIONSHIP_PROFILES_PATH, {"people": {}})
    assets = engine.load_json(engine.SUPPORTING_ASSETS_PATH, {"products": [], "websitePages": [], "channels": []})
    demand_categories_config = engine.load_json(engine.DEMAND_CATEGORIES_PATH, {"categories": {}})
    account_intelligence_config = engine.load_json(engine.ACCOUNT_INTELLIGENCE_CONFIG_PATH, {})

    if not org_profiles.get("organisations"):
        print("No organisations qualified by Demand Intelligence yet. Nothing to do.")
        return 0

    plan = engine.build_weekly_plan(
        org_profiles, account_feed, relationship_profiles, assets,
        demand_categories_config, account_intelligence_config, config,
    )

    history = engine.load_json(engine.HISTORY_PATH, engine.DEFAULT_HISTORY)
    history.setdefault("weeks", [])
    history["weeks"] = [w for w in history["weeks"] if w.get("weekOf") != plan["weekOf"]]
    history["weeks"].append(plan)
    engine.save_json(engine.HISTORY_PATH, history)

    monthly = engine.build_monthly_authority_report(history, config)

    feed = {"weeklyPlan": plan, "monthlyAuthorityReport": monthly}
    engine.FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine.save_json(engine.FEED_PATH, feed)

    report_path = engine.FEED_PATH.parent / f"{TODAY}-executive-brand-intelligence-report.md"
    report_path.write_text(render_report(plan, monthly), encoding="utf-8")

    print(f"Weekly Brand Plan built for {plan['companiesThisWeek']} companies this week. "
          f"Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
