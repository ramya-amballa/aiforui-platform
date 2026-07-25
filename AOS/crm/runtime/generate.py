#!/usr/bin/env python3
"""
CRM — Relationship Intelligence Runtime (v1.0)

Usage:
    python3 generate.py

Read-only. Never writes to 06-CRM/company-intelligence.json — see
../crm-runtime-notes.md's "The One Rule": relationshipTemperature,
nextFollowUpDue and outreachHistory belong to 04-Sales-Director
exclusively.

Generates three reports from company-intelligence.json enriched with
real, read-only history from three other employees:
  - opportunity-hunter/opportunity-schema.json (opportunity history per
    organisation)
  - sales-director/runtime/processed-index.json (proposal history per
    organisation)
  - 08-Revenue-Hunter/pipeline.json (open pipeline history per
    organisation, using the same currency parser Revenue Hunter and
    Executive Dashboard already ship)

Reports:
  - daily-follow-up-queue.md — due/overdue/cold-risk, using
    executive-dashboard/runtime/generate.py's own crm_follow_up_status()
    logic, copied verbatim rather than re-derived (see runtime notes)
  - relationship-health-report.md — one row per company: temperature,
    days since touch, opportunity/proposal/pipeline history, and a
    health flag derived from the same due/cold-risk signals above
  - stale-relationship-alerts.md — `cold` companies (the temperature
    executive-dashboard's own CRM section explicitly skips) whose
    lastTouch is 90+ days old, flagged for the monthly from-scratch
    review follow-up-priority-model.md itself calls for

Never drafts or sends outreach. Every output is a file for the founder
to read.
"""

import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
CRM_RUNTIME_OWNER_DIR = RUNTIME_DIR.parent
AOS_DIR = CRM_RUNTIME_OWNER_DIR.parent
REPO_ROOT = AOS_DIR.parent

CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "opportunity-hunter" / "opportunity-schema.json"
SALES_DIRECTOR_PROCESSED_PATH = AOS_DIR / "sales-director" / "runtime" / "processed-index.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"

OUTPUT_DIR = RUNTIME_DIR / "output"
LOGS_DIR = RUNTIME_DIR / "logs"

TODAY = date.today()
RUN_STARTED = datetime.now(timezone.utc)

# 04-Sales-Director/follow-up-priority-model.md, Step 1 — identical to
# executive-dashboard/runtime/generate.py's own constant, reused verbatim.
MAX_DAYS_BY_TEMPERATURE = {"hot": 3, "warm": 10, "cooling": 21}
STALE_COLD_THRESHOLD_DAYS = 90

# Reused verbatim from revenue-hunter/runtime/generate.py, which reused
# it verbatim from executive-dashboard/runtime/generate.py.
MULTIPLIERS = {"k": 1_000, "l": 100_000, "lakh": 100_000, "cr": 10_000_000, "crore": 10_000_000, "m": 1_000_000}
CURRENCY_SYMBOLS = {"$": "USD", "₹": "INR", "£": "GBP", "€": "EUR"}


def parse_currency(value):
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
    return sum(parsed) / len(parsed), currency


def format_amount(value):
    if not value:
        return "0"
    if value >= 10_000_000:
        return f"{value / 10_000_000:.2f}Cr"
    if value >= 100_000:
        return f"{value / 100_000:.2f}L"
    return f"{value:,.0f}"


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


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def table(rows, columns, empty_label="Nothing today"):
    if not rows:
        return f"_{empty_label}._"
    header = "| " + " | ".join(columns) + " |"
    divider = "|" + "|".join(["---"] * len(columns)) + "|"
    body = "\n".join("| " + " | ".join(str(r.get(c, "")) for c in columns) + " |" for r in rows)
    return f"{header}\n{divider}\n{body}"


# --------------------------------------------------------------------------
# Follow-up queue — reused verbatim from
# executive-dashboard/runtime/generate.py's crm_follow_up_status()
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
# Relationship categorisation — best-effort from existing fields only;
# see crm-runtime-notes.md for what's inferable and what isn't
# --------------------------------------------------------------------------

def categorise(company):
    if company.get("recruiter"):
        return "Recruiter"
    relationship = (company.get("existingRelationship") or "").lower()
    if relationship in ("prior client", "active client"):
        return "Client"
    industry = (company.get("industry") or "").lower()
    if "consulting" in industry or "advisory" in industry:
        return "Consulting Firm"
    return "Prospect"


# --------------------------------------------------------------------------
# History enrichment — read-only cross-reference
# --------------------------------------------------------------------------

def opportunity_history(opportunity_schema):
    history = {}
    for opp in opportunity_schema.get("opportunities", []):
        org = opp.get("organisation")
        if not org:
            continue
        history.setdefault(org, []).append(opp)
    return history


def proposal_history(sales_director_processed, opp_by_id):
    history = {}
    for opp_id, record in sales_director_processed.get("processed", {}).items():
        opp = opp_by_id.get(opp_id)
        if not opp:
            continue
        org = opp.get("organisation")
        history.setdefault(org, []).append({**record, "opportunityId": opp_id})
    return history


def pipeline_history(pipeline):
    history = {}
    for entry in pipeline.get("pipeline", []):
        org = entry.get("organisation")
        if not org:
            continue
        history.setdefault(org, []).append(entry)
    return history


# --------------------------------------------------------------------------
# Reports
# --------------------------------------------------------------------------

def generate_follow_up_queue(crm_status):
    lines = ["# CRM — Daily Follow-Up Queue", "", f"**Date:** {TODAY.isoformat()}", "",
              "## Due Today or Overdue", ""]
    lines.append(table(
        [{"Company": c["companyName"], "Temperature": c.get("relationshipTemperature"),
          "Days Since Touch": c.get("days_since_touch"), "Next Follow-Up Due": c.get("nextFollowUpDue")}
         for c in crm_status["due"]],
        ["Company", "Temperature", "Days Since Touch", "Next Follow-Up Due"],
        "Nothing due today"))
    lines += ["", "## Relationships Becoming Cold", ""]
    lines.append(table(
        [{"Company": c["companyName"], "Temperature": c.get("relationshipTemperature"),
          "Days Since Touch": c.get("days_since_touch")} for c in crm_status["cold_risk"]],
        ["Company", "Temperature", "Days Since Touch"], "None trending cold"))
    lines += ["", "## Escalated (Hot, Well Past Tolerance)", ""]
    lines.append(table(
        [{"Company": c["companyName"], "Days Since Touch": c.get("days_since_touch")} for c in crm_status["escalated"]],
        ["Company", "Days Since Touch"], "None escalated"))
    lines += ["", "---", "", "*Due/overdue logic reused verbatim from "
              "`executive-dashboard/runtime/generate.py`'s `crm_follow_up_status()` — "
              "see `../../crm-runtime-notes.md`. This runtime never drafts or sends outreach.*"]
    return "\n".join(lines) + "\n"


def generate_health_report(companies, opp_history, prop_history, pipe_history):
    rows = []
    for company in companies:
        org = company["companyName"]
        opps = opp_history.get(org, [])
        props = prop_history.get(org, [])
        pipe_items = pipe_history.get(org, [])

        pipe_weighted = 0.0
        for item in pipe_items:
            amount, _ = parse_currency(item.get("expectedRevenue"))
            if amount is not None:
                pipe_weighted += amount * (item.get("probabilityOfSuccess", 0) / 10)

        since_touch = days_since(company.get("lastTouch"))
        temperature = company.get("relationshipTemperature", "cold")
        max_days = MAX_DAYS_BY_TEMPERATURE.get(temperature)
        is_overdue = since_touch is not None and max_days is not None and since_touch > max_days
        is_cold_risk = temperature == "cooling" or (
            temperature in ("hot", "warm") and since_touch is not None and max_days and since_touch >= max_days
        )
        if temperature == "cold":
            health = "Dormant"
        elif is_cold_risk:
            health = "At Risk"
        elif is_overdue:
            health = "Needs Attention"
        else:
            health = "Healthy"

        rows.append({
            "Company": org, "Category": categorise(company), "Temperature": temperature,
            "Days Since Touch": since_touch if since_touch is not None else "?",
            "Health": health,
            "Opportunities": len(opps), "Proposals Prepared": len(props),
            "Open Pipeline": len(pipe_items), "Weighted Pipeline Value": format_amount(pipe_weighted),
        })

    lines = ["# CRM — Relationship Health Report", "", f"**Date:** {TODAY.isoformat()}", "",
              table(rows, ["Company", "Category", "Temperature", "Days Since Touch", "Health",
                            "Opportunities", "Proposals Prepared", "Open Pipeline", "Weighted Pipeline Value"],
                    "No companies on record yet"),
              "", "---", "",
              "*Category is inferred from existing fields only (see `../../crm-runtime-notes.md`) — "
              "\"Speaking Contact\" and \"Partner\" have no reliable signal in "
              "`company-intelligence.json` yet and are never guessed into a row above.*"]
    return "\n".join(lines) + "\n"


def generate_stale_alerts(companies):
    alerts = []
    for company in companies:
        if company.get("relationshipTemperature", "cold") != "cold":
            continue
        since_touch = days_since(company.get("lastTouch"))
        if since_touch is not None and since_touch > STALE_COLD_THRESHOLD_DAYS:
            alerts.append({"Company": company["companyName"], "Days Since Touch": since_touch,
                            "Recommendation": "Past the monthly review window — consider a from-scratch "
                                               "re-approach, not a chase."})
    lines = ["# CRM — Stale Relationship Alerts", "", f"**Date:** {TODAY.isoformat()}", "",
              f"Cold relationships untouched for {STALE_COLD_THRESHOLD_DAYS}+ days — a state "
              "`executive-dashboard`'s own CRM section never surfaces (it skips `cold` entirely) "
              "and `follow-up-priority-model.md` says should be reviewed monthly, not chased daily.",
              "", table(alerts, ["Company", "Days Since Touch", "Recommendation"], "No stale relationships"),
              "", "---", "", "*This runtime never drafts or sends outreach for these — it only flags "
              "that a human review is due.*"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{TODAY.isoformat()}-{RUN_STARTED.strftime('%H%M%S')}-crm.log"
    log_lines = [f"CRM Runtime v1.0 — run started {RUN_STARTED.isoformat()}"]

    def log(msg):
        print(msg)
        log_lines.append(msg)

    crm_data = load_json(CRM_PATH, {"companies": []})
    opportunity_schema = load_json(OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    sales_director_processed = load_json(SALES_DIRECTOR_PROCESSED_PATH, {"processed": {}})
    pipeline = load_json(PIPELINE_PATH, {"pipeline": []})

    companies = crm_data.get("companies", [])
    if not companies:
        log("No companies on record in company-intelligence.json yet. Nothing to report.")
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        return 0

    opp_by_id = {o["id"]: o for o in opportunity_schema.get("opportunities", [])}
    opp_history = opportunity_history(opportunity_schema)
    prop_history = proposal_history(sales_director_processed, opp_by_id)
    pipe_history = pipeline_history(pipeline)
    crm_status = crm_follow_up_status(companies)

    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "daily-follow-up-queue.md").write_text(generate_follow_up_queue(crm_status), encoding="utf-8")
    (OUTPUT_DIR / "relationship-health-report.md").write_text(
        generate_health_report(companies, opp_history, prop_history, pipe_history), encoding="utf-8")
    (OUTPUT_DIR / "stale-relationship-alerts.md").write_text(generate_stale_alerts(companies), encoding="utf-8")

    dated_prefix = TODAY.isoformat()
    for name in ("daily-follow-up-queue", "relationship-health-report", "stale-relationship-alerts"):
        content = (OUTPUT_DIR / f"{name}.md").read_text(encoding="utf-8")
        (OUTPUT_DIR / f"{dated_prefix}-{name}.md").write_text(content, encoding="utf-8")

    log(f"  {len(companies)} companies. Due: {len(crm_status['due'])}, cold-risk: {len(crm_status['cold_risk'])}, "
        f"escalated: {len(crm_status['escalated'])}, stale-cold: "
        f"{sum(1 for c in companies if c.get('relationshipTemperature') == 'cold' and (days_since(c.get('lastTouch')) or 0) > STALE_COLD_THRESHOLD_DAYS)}")
    log(f"\nReports written to {OUTPUT_DIR.relative_to(REPO_ROOT)}")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
