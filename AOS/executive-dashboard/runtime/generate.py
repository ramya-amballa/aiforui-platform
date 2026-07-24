#!/usr/bin/env python3
"""
AOS Executive Dashboard — generator

Usage:
    python3 generate.py

Reads the three live outputs that already exist — nothing new is
computed or stored as a separate source of truth:
  - opportunity-hunter/opportunity-schema.json
  - 08-Revenue-Hunter/pipeline.json
  - 06-CRM/company-intelligence.json

...and renders one executive-dashboard.md, applying two pieces of
logic that are already fully specified elsewhere in AOS but have no
other executable home yet:
  - 09-CEO-Advisor/decision-model.md (normalise -> urgency overlay ->
    effort tie-break -> top 3), so "Today's Priorities" is CEO
    Advisor's own documented method, run against live data
  - 04-Sales-Director/follow-up-priority-model.md (max days between
    touches by temperature), so the CRM section reflects the same
    due/overdue/escalation logic Sales Director is specified to use

This script does not write to any of the three source files. It is a
read-only view, safe to re-run at any time; the only output is
executive-dashboard.md (always overwritten in place) and a dated copy
in runtime/output/ for history.
"""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = RUNTIME_DIR.parent
AOS_DIR = DASHBOARD_DIR.parent

OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "opportunity-hunter" / "opportunity-schema.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"

STABLE_OUTPUT_PATH = DASHBOARD_DIR / "executive-dashboard.md"
OUTPUT_DIR = RUNTIME_DIR / "output"

TODAY = date.today()

# 04-Sales-Director/follow-up-priority-model.md, Step 1
MAX_DAYS_BY_TEMPERATURE = {"hot": 3, "warm": 10, "cooling": 21}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def days_since(iso_date):
    if not iso_date:
        return None
    try:
        return (TODAY - datetime.strptime(iso_date, "%Y-%m-%d").date()).days
    except ValueError:
        return None


def days_until(iso_date):
    if not iso_date:
        return None
    try:
        return (datetime.strptime(iso_date, "%Y-%m-%d").date() - TODAY).days
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Currency parsing — pipeline.json's expectedRevenue is "number or string,
# amount or range, with currency," so summing it means parsing it first.
# Best-effort: unparseable or unestimated entries are counted, not guessed.
# --------------------------------------------------------------------------

MULTIPLIERS = {"k": 1_000, "l": 100_000, "lakh": 100_000, "cr": 10_000_000, "crore": 10_000_000, "m": 1_000_000}
CURRENCY_SYMBOLS = {"$": "USD", "₹": "INR", "£": "GBP", "€": "EUR"}


def parse_currency(value):
    """Returns (numeric_value, currency_code) or (None, None) if unparseable."""
    if isinstance(value, (int, float)):
        return float(value), None
    if not isinstance(value, str):
        return None, None

    text = value.strip()
    currency = None
    for symbol, code in CURRENCY_SYMBOLS.items():
        if symbol in text:
            currency = code
            break
    match = re.search(r"[A-Za-z]{3}", text)
    if not currency and match:
        currency = match.group(0).upper()

    numbers = re.findall(r"(\d[\d,]*\.?\d*)\s*(k|l|lakh|cr|crore|m)?", text, flags=re.IGNORECASE)
    numbers = [(n, s) for n, s in numbers if n]
    if not numbers:
        return None, currency

    parsed = []
    for num, suffix in numbers:
        try:
            n = float(num.replace(",", ""))
        except ValueError:
            continue
        n *= MULTIPLIERS.get(suffix.lower(), 1) if suffix else 1
        parsed.append(n)

    if not parsed:
        return None, currency
    # A range ("10,000-15,000") averages; a single figure is used as-is.
    return sum(parsed) / len(parsed), currency


def format_amount(value, currency):
    if value is None:
        return "unestimated"
    label = currency or ""
    if value >= 10_000_000:
        return f"{label} {value / 10_000_000:.2f}Cr".strip()
    if value >= 100_000:
        return f"{label} {value / 100_000:.2f}L".strip()
    return f"{label} {value:,.0f}".strip()


# --------------------------------------------------------------------------
# Revenue
# --------------------------------------------------------------------------

def open_pipeline_items(pipeline):
    return [p for p in pipeline if p.get("stage") not in ("won", "lost")]


def revenue_section(pipeline):
    open_items = open_pipeline_items(pipeline)
    total_value = 0.0
    weighted_value = 0.0
    unestimated = 0
    currencies_seen = set()

    for item in open_items:
        amount, currency = parse_currency(item.get("expectedRevenue"))
        if amount is None:
            unestimated += 1
            continue
        if currency:
            currencies_seen.add(currency)
        total_value += amount
        weighted_value += amount * (item.get("probabilityOfSuccess", 0) / 10)

    mixed_currency_note = ""
    if len(currencies_seen) > 1:
        mixed_currency_note = f" (mixed currencies: {', '.join(sorted(currencies_seen))} — directional, not FX-adjusted)"
    currency_label = next(iter(currencies_seen), "") if len(currencies_seen) == 1 else ""

    return {
        "total_value": total_value,
        "weighted_value": weighted_value,
        "currency_label": currency_label,
        "mixed_currency_note": mixed_currency_note,
        "unestimated": unestimated,
        "active_count": len(open_items),
    }


# --------------------------------------------------------------------------
# Today's Priorities — 09-CEO-Advisor/decision-model.md, executed
# --------------------------------------------------------------------------

def urgency_factor(due_in_days):
    if due_in_days is None:
        return 0.8
    if due_in_days <= 2:
        return 1.5
    if due_in_days <= 7:
        return 1.2
    if due_in_days <= 30:
        return 1.0
    return 0.8


def ceo_advisor_candidates(opportunities, pipeline, crm_status):
    candidates = []

    for item in open_pipeline_items(pipeline):
        if item.get("band") != "Priority":
            continue
        due_in = days_until(item.get("nextActionDue"))
        value = (item.get("score", 0) / 10) * urgency_factor(due_in)
        candidates.append({
            "label": f"{item.get('nextAction') or 'Advance'} — {item.get('organisation')} ({item.get('title')})",
            "value": value,
            "effort": item.get("effortRequired", 5),
            "reason": f"Revenue Hunter Priority band (score {item.get('score')}/100)"
                      + (f", due in {due_in}d" if due_in is not None else ", no due date set"),
            "estimated_value": item.get("expectedRevenue"),
        })

    for opp in opportunities:
        if opp.get("band") != "Priority" or opp.get("status") == "archived":
            continue
        due_in = days_until(opp.get("nextActionDue"))
        value = (opp.get("priorityScore", 0) / 10) * urgency_factor(due_in)
        candidates.append({
            "label": f"Act on {opp.get('classification', 'opportunity').lower()} — {opp.get('organisation')} ({opp.get('title')})",
            "value": value,
            "effort": opp.get("scores", {}).get("timeRequired", 5),
            "reason": f"Opportunity Hunter Priority band (score {opp.get('priorityScore')}/100), "
                      f"classified {opp.get('classification')}",
            "estimated_value": None,
        })

    for company in crm_status["escalated"]:
        candidates.append({
            "label": f"Re-engage {company['companyName']} before the relationship goes cold",
            "value": 9 * 1.5,  # Hot+overdue per decision-model.md's normalisation table, escalation = urgent
            "effort": 3,
            "reason": f"Sales Director escalation: {company['relationshipTemperature']} and "
                      f"{company['days_since_touch']} days since last touch",
            "estimated_value": None,
            "is_escalation": True,
        })

    candidates.sort(key=lambda c: (c["value"], c["effort"]), reverse=True)
    return candidates


# --------------------------------------------------------------------------
# CRM — 04-Sales-Director/follow-up-priority-model.md, executed
# --------------------------------------------------------------------------

def crm_follow_up_status(companies):
    due, cold_risk, escalated = [], [], []

    for company in companies:
        temperature = company.get("relationshipTemperature", "cold")
        if temperature == "cold":
            continue
        max_days = MAX_DAYS_BY_TEMPERATURE.get(temperature)
        since_touch = days_since(company.get("lastTouch"))
        until_due = days_until(company.get("nextFollowUpDue"))
        is_overdue = (until_due is not None and until_due <= 0) or (
            since_touch is not None and max_days is not None and since_touch > max_days
        )

        record = {**company, "days_since_touch": since_touch}

        if is_overdue:
            due.append(record)
        if temperature == "cooling" or (
            temperature in ("hot", "warm") and since_touch is not None and max_days and since_touch >= max_days
        ):
            cold_risk.append(record)
        if temperature == "hot" and since_touch is not None and since_touch > 3 + 3:
            escalated.append(record)

    due.sort(key=lambda c: ({"hot": 0, "warm": 1, "cooling": 2}.get(c.get("relationshipTemperature"), 3),
                             -(c["days_since_touch"] or 0)))
    return {"due": due, "cold_risk": cold_risk, "escalated": escalated}


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def table(rows, columns, empty_label="Nothing today"):
    if not rows:
        return f"_{empty_label}._"
    header = "| " + " | ".join(columns) + " |"
    divider = "|" + "|".join(["---"] * len(columns)) + "|"
    body = "\n".join("| " + " | ".join(str(r.get(c, "")) for c in columns) + " |" for r in rows)
    return f"{header}\n{divider}\n{body}"


def generate(opportunities, pipeline, crm):
    rev = revenue_section(pipeline)
    crm_status = crm_follow_up_status(crm)
    priorities = ceo_advisor_candidates(opportunities, pipeline, crm_status)

    open_opps = [o for o in opportunities if o.get("status") not in ("won", "lost", "archived")]
    top_10 = sorted(open_opps, key=lambda o: o.get("priorityScore", 0), reverse=True)[:10]
    adgl_opps = sorted([o for o in open_opps if "ADGL" in o.get("domainTags", [])],
                        key=lambda o: o.get("priorityScore", 0), reverse=True)
    adg_opps = sorted([o for o in open_opps if "AI Deployment Governance" in o.get("domainTags", [])],
                       key=lambda o: o.get("priorityScore", 0), reverse=True)

    open_pipe = open_pipeline_items(pipeline)
    opp_by_id = {o["id"]: o for o in opportunities}
    immediate_proposals = [p for p in open_pipe
                            if opp_by_id.get(p.get("sourceRef"), {}).get("classification") == "Immediate Proposal"]
    partnerships = [p for p in open_pipe if p.get("type") == "Partnership"]

    def roi(item):
        amount, _ = parse_currency(item.get("expectedRevenue"))
        amount = amount or 0
        return amount * (item.get("probabilityOfSuccess", 0) / 10) * (item.get("effortRequired", 0) / 10)

    highest_roi = max(open_pipe, key=roi, default=None)

    top_priority = priorities[0] if priorities else None
    runners_up = priorities[1:4]

    lines = []
    lines.append("# AOS Executive Dashboard")
    lines.append("")
    lines.append(f"**Generated:** {TODAY.isoformat()}")
    lines.append("")
    lines.append("*Read-only view over `opportunity-hunter/opportunity-schema.json`, "
                  "`08-Revenue-Hunter/pipeline.json` and `06-CRM/company-intelligence.json`. "
                  "Regenerate with `python3 runtime/generate.py`; do not hand-edit.*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Revenue
    lines.append("## Revenue")
    lines.append("")
    currency_suffix = f" {rev['currency_label']}" if rev["currency_label"] else ""
    lines.append(f"- **Total pipeline value:** {format_amount(rev['total_value'], rev['currency_label'])}"
                  f"{rev['mixed_currency_note']}"
                  + (f" ({rev['unestimated']} item(s) not yet estimated, excluded)" if rev["unestimated"] else ""))
    lines.append(f"- **Expected revenue (probability-weighted):** {format_amount(rev['weighted_value'], rev['currency_label'])}")
    lines.append(f"- **Active opportunities:** {rev['active_count']}")
    lines.append("")

    # Today's Priorities
    lines.append("## Today's Priorities")
    lines.append("")
    if top_priority:
        lines.append(f"**Highest-value action:** {top_priority['label']}")
        lines.append(f"**Reason:** {top_priority['reason']}")
        if top_priority.get("estimated_value"):
            lines.append(f"**Estimated value:** {top_priority['estimated_value']}")
        lines.append("")
        if runners_up:
            lines.append("**Runners-up (not co-priorities):**")
            for r in runners_up:
                lines.append(f"- {r['label']} — {r['reason']}")
    else:
        lines.append("_No Priority-band candidates yet. Run Opportunity Hunter's ingestion "
                      "workflow to populate live data._")
    lines.append("")

    # Opportunity Hunter
    lines.append("## Opportunity Hunter")
    lines.append("")
    lines.append("### Top 10 Opportunities")
    lines.append(table([{"Title": o["title"], "Organisation": o["organisation"], "Score": o["priorityScore"],
                          "Classification": o["classification"]} for o in top_10],
                        ["Title", "Organisation", "Score", "Classification"], "No open opportunities logged yet"))
    lines.append("")
    lines.append("### Highest ADGL Opportunities")
    lines.append(table([{"Title": o["title"], "Organisation": o["organisation"], "Score": o["priorityScore"]}
                         for o in adgl_opps], ["Title", "Organisation", "Score"], "No ADGL-tagged opportunities yet"))
    lines.append("")
    lines.append("### Highest AI Deployment Governance Opportunities")
    lines.append(table([{"Title": o["title"], "Organisation": o["organisation"], "Score": o["priorityScore"]}
                         for o in adg_opps], ["Title", "Organisation", "Score"],
                        "No AI Deployment Governance-tagged opportunities yet"))
    lines.append("")

    # CRM
    lines.append("## CRM")
    lines.append("")
    recruiters_due = [c for c in crm_status["due"] if c.get("recruiter")]
    companies_due = [c for c in crm_status["due"] if not c.get("recruiter")]
    lines.append("### Recruiters Requiring Follow-Up")
    lines.append(table([{"Recruiter": c["recruiter"], "Company": c["companyName"], "Temperature": c["relationshipTemperature"],
                          "Days Since Touch": c["days_since_touch"]} for c in recruiters_due],
                        ["Recruiter", "Company", "Temperature", "Days Since Touch"], "No recruiter follow-ups due"))
    lines.append("")
    lines.append("### Companies Requiring Follow-Up")
    lines.append(table([{"Company": c["companyName"], "Temperature": c["relationshipTemperature"],
                          "Days Since Touch": c["days_since_touch"]} for c in companies_due],
                        ["Company", "Temperature", "Days Since Touch"], "No company follow-ups due"))
    lines.append("")
    lines.append("### Relationships Becoming Cold")
    lines.append(table([{"Company": c["companyName"], "Temperature": c["relationshipTemperature"],
                          "Days Since Touch": c["days_since_touch"]} for c in crm_status["cold_risk"]],
                        ["Company", "Temperature", "Days Since Touch"], "No relationships trending cold"))
    lines.append("")

    # Revenue Hunter
    lines.append("## Revenue Hunter")
    lines.append("")
    lines.append("### Immediate Proposals")
    lines.append(table([{"Title": p["title"], "Organisation": p["organisation"], "Score": p["score"],
                          "Due": p.get("nextActionDue")} for p in immediate_proposals],
                        ["Title", "Organisation", "Score", "Due"], "No immediate proposals pending"))
    lines.append("")
    lines.append("### Partnership Opportunities")
    lines.append(table([{"Title": p["title"], "Organisation": p["organisation"], "Score": p["score"]}
                         for p in partnerships], ["Title", "Organisation", "Score"], "No partnership opportunities open"))
    lines.append("")
    lines.append("### Highest ROI Opportunity")
    if highest_roi:
        lines.append(f"**{highest_roi['title']}** — {highest_roi['organisation']} "
                      f"(expected {highest_roi.get('expectedRevenue')}, "
                      f"probability {highest_roi.get('probabilityOfSuccess')}/10, "
                      f"effort {highest_roi.get('effortRequired')}/10)")
    else:
        lines.append("_No open pipeline items yet._")
    lines.append("")

    # Daily Summary
    lines.append("## Daily Summary")
    lines.append("")
    lines.append(daily_summary(rev, priorities, crm_status, open_opps, open_pipe))
    lines.append("")

    return "\n".join(lines)


def daily_summary(rev, priorities, crm_status, open_opps, open_pipe):
    if not open_opps and not open_pipe:
        return ("AI for U&I's pipeline is currently empty — no opportunities have been logged yet. "
                "Run Opportunity Hunter's ingestion workflow (`opportunity-hunter/runtime/ingest.py`) "
                "to begin populating live data before this summary reflects real activity.")

    parts = [
        f"AI for U&I is tracking {rev['active_count']} active pipeline item(s) worth an estimated "
        f"{format_amount(rev['total_value'], rev['currency_label'])} "
        f"({format_amount(rev['weighted_value'], rev['currency_label'])} probability-weighted), "
        f"alongside {len(open_opps)} open opportunit{'y' if len(open_opps) == 1 else 'ies'} in the funnel."
    ]
    if priorities:
        parts.append(f"Today's highest-value action is: {priorities[0]['label']}.")
    if crm_status["due"]:
        parts.append(f"{len(crm_status['due'])} relationship(s) need a follow-up today.")
    if crm_status["cold_risk"]:
        parts.append(f"{len(crm_status['cold_risk'])} relationship(s) are trending cold and need attention "
                      f"before they're lost.")
    return " ".join(parts)


def main():
    try:
        opportunities = load_json(OPPORTUNITY_SCHEMA_PATH)["opportunities"]
        pipeline = load_json(PIPELINE_PATH)["pipeline"]
        crm = load_json(CRM_PATH)["companies"]
    except FileNotFoundError as exc:
        print(f"Cannot find a required source file: {exc}", file=sys.stderr)
        return 1

    report = generate(opportunities, pipeline, crm)

    STABLE_OUTPUT_PATH.write_text(report, encoding="utf-8")
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / f"{TODAY.isoformat()}-executive-dashboard.md").write_text(report, encoding="utf-8")

    print(f"Executive Dashboard written to {STABLE_OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
