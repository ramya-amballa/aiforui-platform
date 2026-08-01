"""
Capacity Management Engine (AOS Sprint 22)

AI for U&I is one person. A full-codebase search before this employee
was designed confirmed CEO Advisor ranks priorities and recommends
pursuing new opportunities with zero regard for how much delivery work
is already committed — every day is treated as if the founder has
unlimited bandwidth. There is also no concept anywhere in AOS of the
founder's own available days per week, or how much effort an active
engagement actually consumes. This closes both gaps, honestly:

- **Active Engagement Load** — every Revenue Hunter pipeline entry at
  `stage == "won"` whose Delivery Intelligence phase (from
  `delivery-intelligence/delivery-log.json`, read-only) isn't yet
  `"Closed"`, mapped through Sales Director's own `rate-card.json`
  `typicalDays.{min,max}` for that entry's real `type` field — never a
  second, independently-invented effort estimate.
- **Incoming Pipeline Load** — every Sales Director package at status
  `"Ready To Send"` or `"Proposal Ready"` (from
  `output/sales-director/ceo-advisor-feed.json`), mapped
  through Service Mapping's own `recommendedEngagementType` for that
  opportunity, then the same rate-card lookup. An opportunity with no
  service-mapping recommendation yet is reported as honestly
  unestimated, never guessed.
- **Capacity Status** — the one number AOS cannot observe automatically
  is the founder's own available days per week, so
  `capacity-config.json` is a founder-tunable config (the same pattern
  as `rate-card.json`/`practitioner-bank.json`, not a founder-maintained
  log) shipping with a clearly labelled starting assumption. Total
  committed days (active + incoming) divided by that figure gives
  "weeks of committed work at your available pace," banded into
  Available Capacity / Near Capacity / Over Capacity by
  `capacity-config.json`'s own configurable thresholds.

Advisory only — never blocks a proposal from being prepared or a
priority from being ranked. It only gives the founder (and, one cycle
behind, CEO Advisor) an honest read on how much room is actually left.
"""

import copy
import json
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
CAPACITY_MANAGEMENT_DIR = RUNTIME_DIR.parent
AOS_DIR = CAPACITY_MANAGEMENT_DIR.parent
REPO_ROOT = AOS_DIR.parent

PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
DELIVERY_LOG_PATH = AOS_DIR / "delivery-intelligence" / "delivery-log.json"
CEO_ADVISOR_FEED_PATH = AOS_DIR / "output" / "sales-director" / "ceo-advisor-feed.json"
SERVICE_RECOMMENDATIONS_PATH = AOS_DIR / "service-mapping" / "service-recommendations.json"
RATE_CARD_PATH = AOS_DIR / "sales-director" / "runtime" / "config" / "rate-card.json"
CONFIG_PATH = RUNTIME_DIR / "config" / "capacity-config.json"

FEED_PATH = AOS_DIR / "output" / "capacity-management" / "capacity-feed.json"

TODAY = date.today().isoformat()

PENDING_STATUSES = ("Ready To Send", "Proposal Ready")


def load_json(path, default=None):
    if not path.exists():
        if default is not None:
            return copy.deepcopy(default)
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def typical_days_for(engagement_type, rate_card):
    """None when the rate card has no typicalDays for this type (e.g.
    Grant, Partnership) — never a guessed range."""
    card = rate_card.get("types", {}).get(engagement_type, {})
    typical = card.get("typicalDays")
    if not typical:
        return None
    return typical["min"], typical["max"]


def delivery_phase_for(organisation, delivery_log):
    entry = delivery_log.get("engagements", {}).get(organisation)
    return entry.get("phase", "Not started") if entry else "Not started"


# --------------------------------------------------------------------------
# Active Engagement Load
# --------------------------------------------------------------------------

def active_engagement_load(pipeline_data, delivery_log, rate_card):
    engagements = []
    min_total, max_total = 0, 0
    for entry in pipeline_data.get("pipeline", []):
        if entry.get("stage") != "won":
            continue
        organisation = entry.get("organisation")
        phase = delivery_phase_for(organisation, delivery_log)
        if phase == "Closed":
            continue
        typical = typical_days_for(entry.get("type"), rate_card)
        item = {"organisation": organisation, "title": entry.get("title"), "type": entry.get("type"), "phase": phase}
        if typical:
            item["estimatedDaysMin"], item["estimatedDaysMax"] = typical
            min_total += typical[0]
            max_total += typical[1]
        else:
            item["estimatedDaysMin"], item["estimatedDaysMax"] = None, None
        engagements.append(item)
    return engagements, min_total, max_total


# --------------------------------------------------------------------------
# Incoming Pipeline Load
# --------------------------------------------------------------------------

def incoming_pipeline_load(ceo_feed, service_recommendations, rate_card):
    pending = []
    min_total, max_total = 0, 0
    for entry in ceo_feed.get("feed", []):
        if entry.get("status") not in PENDING_STATUSES:
            continue
        recommendation = service_recommendations.get(entry.get("opportunityId"))
        item = {"organisation": entry.get("organisation"), "title": entry.get("title"), "status": entry.get("status")}
        engagement_type = None
        if recommendation and not recommendation.get("notApplicable"):
            engagement_type = recommendation.get("recommendedEngagementType")
        item["engagementType"] = engagement_type
        typical = typical_days_for(engagement_type, rate_card) if engagement_type else None
        if typical:
            item["estimatedDaysMin"], item["estimatedDaysMax"] = typical
            min_total += typical[0]
            max_total += typical[1]
        else:
            item["estimatedDaysMin"], item["estimatedDaysMax"] = None, None
        pending.append(item)
    return pending, min_total, max_total


# --------------------------------------------------------------------------
# Capacity Status
# --------------------------------------------------------------------------

def weeks_of_committed_work(min_days, max_days, available_days_per_week):
    if not available_days_per_week:
        return None, None
    return round(min_days / available_days_per_week, 1), round(max_days / available_days_per_week, 1)


def capacity_status(min_weeks, thresholds):
    if min_weeks is None:
        return "Not enough signal yet"
    if min_weeks >= thresholds.get("overCapacity", 10):
        return "Over Capacity"
    if min_weeks >= thresholds.get("nearCapacity", 6):
        return "Near Capacity"
    return "Available Capacity"


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_capacity_markdown(active, active_min, active_max, pending, pending_min, pending_max,
                              min_weeks, max_weeks, status, available_days_per_week):
    lines = [
        "# Capacity Management",
        "",
        f"**Generated:** {TODAY}",
        f"**Founder's available days/week (config):** {available_days_per_week}",
        "",
        "*Advisory only — never blocks a proposal from being prepared or changes a priority ranking. "
        "Every effort estimate below is Sales Director's own rate-card typicalDays range, reused verbatim.*",
        "",
        "---",
        "",
        f"## Capacity Status: {status}",
        "",
    ]
    if min_weeks is not None:
        lines.append(f"**Weeks of committed work at your available pace:** {min_weeks}-{max_weeks}")
    else:
        lines.append("_Not enough signal yet — no active or incoming engagement has an estimable effort._")

    lines += ["", "---", "", f"## Active Engagement Load ({len(active)} engagement(s))", "",
              f"**Estimated days:** {active_min}-{active_max}", ""]
    if active:
        for e in active:
            days = f"{e['estimatedDaysMin']}-{e['estimatedDaysMax']} days" if e["estimatedDaysMin"] is not None else "not estimated (no rate-card entry for this type)"
            lines.append(f"- **{e['organisation']}** — {e['title']} ({e['type']}), phase: {e['phase']} — {days}")
    else:
        lines.append("_No active engagements on record._")

    lines += ["", "---", "", f"## Incoming Pipeline Load ({len(pending)} pending proposal(s))", "",
              f"**Estimated days:** {pending_min}-{pending_max}", ""]
    if pending:
        for p in pending:
            days = f"{p['estimatedDaysMin']}-{p['estimatedDaysMax']} days" if p["estimatedDaysMin"] is not None else "not estimated (no service-mapping recommendation yet)"
            lines.append(f"- **{p['organisation']}** — {p['title']} ({p['status']}) — {days}")
    else:
        lines.append("_No pending proposals on record._")

    return "\n".join(lines)
