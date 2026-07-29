#!/usr/bin/env python3
"""
Capacity Management — generator (AOS Sprint 22)

Usage:
    python3 generate.py

A pure read-only aggregator, regenerated in full every run — nothing
here is founder-edited by this engine (capacity-config.json is a
founder-tunable config the founder edits directly, like rate-card.json,
never written by this script). Reads Revenue Hunter's pipeline,
Delivery Intelligence's delivery-log.json, Sales Director's own feed,
and Service Mapping's recommendations to give an honest read on how
much delivery room is actually left.
"""

import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import capacity_management_engine as engine  # noqa: E402


def main():
    pipeline_data = engine.load_json(engine.PIPELINE_PATH, {"pipeline": []})
    delivery_log = engine.load_json(engine.DELIVERY_LOG_PATH, {"engagements": {}})
    ceo_feed = engine.load_json(engine.CEO_ADVISOR_FEED_PATH, {"feed": []})
    service_recommendations = engine.load_json(
        engine.SERVICE_RECOMMENDATIONS_PATH, {"recommendations": {}}
    ).get("recommendations", {})
    rate_card = engine.load_json(engine.RATE_CARD_PATH, {"types": {}})
    config = engine.load_json(engine.CONFIG_PATH, {"foundersAvailableDaysPerWeek": 4,
                                                     "weeksOfCommittedWorkThresholds": {}})

    active, active_min, active_max = engine.active_engagement_load(pipeline_data, delivery_log, rate_card)
    pending, pending_min, pending_max = engine.incoming_pipeline_load(ceo_feed, service_recommendations, rate_card)

    total_min, total_max = active_min + pending_min, active_max + pending_max
    available_days_per_week = config.get("foundersAvailableDaysPerWeek", 4)
    min_weeks, max_weeks = engine.weeks_of_committed_work(total_min, total_max, available_days_per_week)
    status = engine.capacity_status(min_weeks, config.get("weeksOfCommittedWorkThresholds", {}))

    feed = {
        "schema": {
            "capacityStatus": "string — Available Capacity | Near Capacity | Over Capacity | Not enough signal yet",
            "weeksOfCommittedWorkMin": "number or null", "weeksOfCommittedWorkMax": "number or null",
            "foundersAvailableDaysPerWeek": "number — from capacity-config.json, founder-tunable",
            "activeEngagements": "array — pipeline stage=='won' entries not yet Closed in delivery-log.json",
            "activeEstimatedDaysMin": "number", "activeEstimatedDaysMax": "number",
            "pendingProposals": "array — sales-director feed entries at Ready To Send/Proposal Ready",
            "pendingEstimatedDaysMin": "number", "pendingEstimatedDaysMax": "number",
        },
        "capacityStatus": status,
        "weeksOfCommittedWorkMin": min_weeks, "weeksOfCommittedWorkMax": max_weeks,
        "foundersAvailableDaysPerWeek": available_days_per_week,
        "activeEngagements": active, "activeEstimatedDaysMin": active_min, "activeEstimatedDaysMax": active_max,
        "pendingProposals": pending, "pendingEstimatedDaysMin": pending_min, "pendingEstimatedDaysMax": pending_max,
    }
    engine.save_json(engine.FEED_PATH, feed)

    report = engine.render_capacity_markdown(active, active_min, active_max, pending, pending_min, pending_max,
                                              min_weeks, max_weeks, status, available_days_per_week)
    report_path = RUNTIME_DIR / "output" / f"{engine.TODAY}-capacity-report.md"
    report_path.write_text(report, encoding="utf-8")
    (RUNTIME_DIR / "output" / "capacity-report.md").write_text(report, encoding="utf-8")

    print(f"Capacity status: {status}")
    print(f"Active engagements: {len(active)} ({active_min}-{active_max} days) | "
          f"Pending proposals: {len(pending)} ({pending_min}-{pending_max} days)")
    if min_weeks is not None:
        print(f"Weeks of committed work at {available_days_per_week} days/week: {min_weeks}-{max_weeks}")
    print(f"Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
