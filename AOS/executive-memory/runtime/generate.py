#!/usr/bin/env python3
"""
Executive Memory — generator (AOS Sprint 20)

Usage:
    python3 generate.py

A pure read-only aggregator, regenerated in full every run — like
Company 360, nothing here is founder-edited by this engine, so there
is nothing to protect from being overwritten. Reads CEO Advisor's own
daily-priorities-log.json (recurring priorities/alerts), Delivery
Intelligence's completed project-closure-report.md files (a real
Lessons Learned Library), Account Intelligence's already-fixed
governance risk vocabulary (recurring risk patterns across
organisations), and the founder-maintained decision-log.json.

If none of the four sources have any data yet, still writes an honest,
mostly-empty feed and report — never silently does nothing, since an
empty Executive Memory is itself informative (nothing has repeated
yet).
"""

import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import executive_memory_engine as engine  # noqa: E402


def main():
    priorities_log = engine.load_json(engine.CEO_ADVISOR_PRIORITIES_LOG_PATH, {"log": []})
    delivery_feed = engine.load_json(engine.DELIVERY_INTELLIGENCE_FEED_PATH, {"engagements": []})
    ai_feed = engine.load_json(engine.ACCOUNT_INTELLIGENCE_FEED_PATH, {"briefs": []})
    # Founder-maintained, read-only — see executive_memory_engine.py's
    # own module docstring and delivery_intelligence_engine.py's
    # precedent. This engine never writes it.
    decision_log = engine.load_json(engine.DECISION_LOG_PATH, {"decisions": []})

    recurring_orgs, recurring_alerts, days_tracked = engine.recurring_priorities(priorities_log)
    lessons_library = engine.build_lessons_learned_library(delivery_feed)
    recurring_risks = engine.recurring_governance_risks(ai_feed)
    decisions = decision_log.get("decisions", [])

    feed = {
        "schema": {
            "recurringPriorities": "array of {organisation, daysInTop3}",
            "recurringAlerts": "array of {alertType, daysFired}",
            "daysTracked": "number — total days in ceo-advisor's daily-priorities-log.json",
            "lessonsLearnedLibrary": "array of {organisation, lessons, closureReportPath}",
            "recurringGovernanceRisks": "array of {risk, organisations, occurrenceCount}",
            "founderDecisions": "array — decision-log.json's own decisions, read-only",
        },
        "recurringPriorities": recurring_orgs,
        "recurringAlerts": recurring_alerts,
        "daysTracked": days_tracked,
        "lessonsLearnedLibrary": lessons_library,
        "recurringGovernanceRisks": recurring_risks,
        "founderDecisions": decisions,
    }
    engine.save_json(engine.FEED_PATH, feed)

    report = engine.render_executive_memory_markdown(
        recurring_orgs, recurring_alerts, days_tracked, lessons_library, recurring_risks, decisions,
    )
    report_path = RUNTIME_DIR / "output" / f"{engine.TODAY}-executive-memory-report.md"
    report_path.write_text(report, encoding="utf-8")
    (RUNTIME_DIR / "output" / "executive-memory-report.md").write_text(report, encoding="utf-8")

    print(f"Days of CEO Advisor priority history: {days_tracked}")
    print(f"Recurring priorities: {len(recurring_orgs)} | Recurring alerts: {len(recurring_alerts)}")
    print(f"Lessons Learned entries: {len(lessons_library)} | Recurring governance risks: {len(recurring_risks)}")
    print(f"Founder-recorded decisions: {len(decisions)}")
    print(f"Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
