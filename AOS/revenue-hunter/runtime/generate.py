#!/usr/bin/env python3
"""
Revenue Hunter — Financial Intelligence Runtime (v1.0)

Usage:
    python3 generate.py

Executes three existing, fully-specified models that had never run as
code — see ../revenue-hunter-runtime-notes.md for exactly which source
answers which question and what's reused versus new:

  - 08-Revenue-Hunter/lead-scoring.md — scores new pipeline entries
    this runtime adds (opportunities daily-workflow.md says should be
    admitted to the pipeline but ingest.py's routing rules don't cover,
    plus CRM upsell/renewal candidates), using the exact same weights
    ingest.py's own route_to_revenue_hunter already applies
  - 08-Revenue-Hunter/decision-tree.md — assigns stage/next-action to
    every new entry
  - 08-Revenue-Hunter/revenue-forecasting-engine.md — expected value,
    three-scenario monthly bucketing, and leverage ranking, exactly as
    documented, against the live pipeline

No financial assumption is ever fabricated: an item with no real
expectedRevenue is recorded "Not yet estimated" and excluded from every
dollar sum, never guessed. Currency parsing reuses
executive-dashboard/runtime/generate.py's parser verbatim rather than
re-deriving one.

Writes output/revenue-dashboard.md and output/revenue-forecast.md
(always overwritten, plus a dated copy each), and updates
08-Revenue-Hunter/pipeline.json — the only file this script writes to
outside revenue-hunter/.
"""

import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
REVENUE_HUNTER_DIR = RUNTIME_DIR.parent
AOS_DIR = REVENUE_HUNTER_DIR.parent
REPO_ROOT = AOS_DIR.parent

PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "demand-intelligence" / "opportunity-schema.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
SALES_DIRECTOR_PROCESSED_PATH = AOS_DIR / "sales-director" / "runtime" / "processed-index.json"
PRODUCT_BACKLOG_PATH = AOS_DIR / "03-Product-Manager" / "product-backlog.json"
SHIPPED_PRODUCTS_PATH = AOS_DIR / "03-Product-Manager" / "shipped-products-log.json"

QUEUE_DIR = RUNTIME_DIR / "queue"
PROCESSED_INDEX_PATH = QUEUE_DIR / "processed-index.json"
OUTPUT_DIR = AOS_DIR / "output" / "revenue-hunter"
LOGS_DIR = RUNTIME_DIR / "logs"

TODAY = date.today()
RUN_STARTED = datetime.now(timezone.utc)

# lead-scoring.md's table, identical to ingest.py's REVENUE_HUNTER_WEIGHTS —
# reused, not reinvented; see revenue-hunter-runtime-notes.md.
LEAD_SCORE_WEIGHTS = {"expectedRevenue": 0.35, "probabilityOfWinning": 0.30, "timeRequired": 0.20, "strategicValue": 0.15}

TEMPERATURE_PROBABILITY = {"hot": 7, "warm": 4}
CRM_DEFAULT_EFFORT = 6
CRM_DEFAULT_STRATEGIC = 6
CRM_UNCLEAR_EXPECTED_REVENUE = 3

DEFAULT_PROCESSED_INDEX = {
    "schema": {
        "addedFromOpportunities": "array of demand-intelligence ids already admitted to pipeline.json",
        "addedFromCrm": "array of CRM companyName values already admitted as upsell/renewal candidates",
    },
    "addedFromOpportunities": [],
    "addedFromCrm": [],
}

# --------------------------------------------------------------------------
# Currency parsing — reused verbatim from executive-dashboard/runtime/generate.py
# --------------------------------------------------------------------------

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
# I/O helpers
# --------------------------------------------------------------------------

def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def next_id(existing_items, prefix, field="id"):
    max_n = 0
    for item in existing_items:
        match = re.match(rf"{prefix}-(\d+)$", item.get(field, ""))
        if match:
            max_n = max(max_n, int(match.group(1)))
    return f"{prefix}-{max_n + 1:04d}"


# --------------------------------------------------------------------------
# Lead scoring — 08-Revenue-Hunter/lead-scoring.md
# --------------------------------------------------------------------------

def lead_score(scores):
    weighted = sum(scores.get(field, 0) * weight for field, weight in LEAD_SCORE_WEIGHTS.items())
    return round(weighted * 10)


def band_for(score):
    if score >= 80:
        return "Priority"
    if score >= 50:
        return "Active"
    return "Deferred"


# --------------------------------------------------------------------------
# Decision tree — 08-Revenue-Hunter/decision-tree.md, applied to a
# freshly-added entry only (never overwrites an existing item's own
# nextAction/nextActionDue, which may reflect real human judgement)
# --------------------------------------------------------------------------

def initial_action(band):
    if band == "Priority":
        return "Action now — hand to Sales Director / CEO Advisor today.", TODAY.isoformat()
    if band == "Active":
        return "Leave it, next scheduled touch stands.", (TODAY + timedelta(days=7)).isoformat()
    return "Leave in pipeline as Deferred. No action.", None


# --------------------------------------------------------------------------
# New pipeline entries
# --------------------------------------------------------------------------

def add_opportunity_entries(pipeline, opportunity_schema, processed_index, log):
    existing_refs = {e.get("sourceRef") for e in pipeline["pipeline"] if e.get("sourceRef")}
    added = []
    for opp in opportunity_schema.get("opportunities", []):
        if opp.get("band") not in ("Active", "Priority"):
            continue
        if opp["id"] in existing_refs or opp["id"] in processed_index["addedFromOpportunities"]:
            continue

        scores = opp.get("scores", {})
        score = lead_score(scores)
        band = band_for(score)
        next_action, next_action_due = initial_action(band)
        entry_type = "Partnership" if opp.get("classification") == "Partnership" else "Consulting Project"

        entry = {
            "id": next_id(pipeline["pipeline"], "rev"),
            "dateAdded": TODAY.isoformat(),
            "type": entry_type,
            "title": opp["title"],
            "organisation": opp["organisation"],
            "sourceRef": opp["id"],
            "expectedRevenue": "Not yet estimated",
            "probabilityOfSuccess": scores.get("probabilityOfWinning", 0),
            "effortRequired": scores.get("timeRequired", 0),
            "strategicValue": scores.get("strategicValue", 0),
            "score": score,
            "band": band,
            "stage": "identified",
            "owner": "Ramya",
            "lastTouch": TODAY.isoformat(),
            "nextAction": next_action,
            "nextActionDue": next_action_due,
            "expectedCloseDate": None,
        }
        pipeline["pipeline"].append(entry)
        processed_index["addedFromOpportunities"].append(opp["id"])
        added.append(entry)
        log(f"  + {entry['id']}: {entry['title']} ({opp['id']}) -> {score}/100 ({band})")
    return added


def add_crm_entries(pipeline, crm_data, processed_index, log):
    existing_orgs = {e.get("organisation") for e in pipeline["pipeline"]}
    added = []
    for company in crm_data.get("companies", []):
        temperature = company.get("relationshipTemperature")
        if temperature not in ("hot", "warm"):
            continue
        name = company["companyName"]
        if name in existing_orgs or name in processed_index["addedFromCrm"]:
            continue

        scores = {
            "expectedRevenue": CRM_UNCLEAR_EXPECTED_REVENUE,
            "probabilityOfWinning": TEMPERATURE_PROBABILITY[temperature],
            "timeRequired": CRM_DEFAULT_EFFORT,
            "strategicValue": CRM_DEFAULT_STRATEGIC,
        }
        score = lead_score(scores)
        band = band_for(score)
        next_action, next_action_due = initial_action(band)

        entry = {
            "id": next_id(pipeline["pipeline"], "rev"),
            "dateAdded": TODAY.isoformat(),
            "type": "Consulting Project",
            "title": f"Upsell/renewal — {name}",
            "organisation": name,
            "sourceRef": f"crm:{name}",
            "expectedRevenue": "Not yet estimated",
            "probabilityOfSuccess": scores["probabilityOfWinning"],
            "effortRequired": scores["timeRequired"],
            "strategicValue": scores["strategicValue"],
            "score": score,
            "band": band,
            "stage": "identified",
            "owner": "Ramya",
            "lastTouch": TODAY.isoformat(),
            "nextAction": next_action,
            "nextActionDue": next_action_due,
            "expectedCloseDate": None,
        }
        pipeline["pipeline"].append(entry)
        processed_index["addedFromCrm"].append(name)
        added.append(entry)
        log(f"  + {entry['id']}: {entry['title']} -> {score}/100 ({band}, {temperature} relationship)")
    return added


def advance_stage_for_prepared_proposals(pipeline, sales_director_processed, log):
    pipeline_by_ref = {e.get("sourceRef"): e for e in pipeline["pipeline"] if e.get("sourceRef")}
    advanced = []
    for opp_id in sales_director_processed.get("processed", {}):
        entry = pipeline_by_ref.get(opp_id)
        if entry and entry.get("stage") == "identified":
            entry["stage"] = "in-progress"
            advanced.append(entry["id"])
            log(f"  ~ {entry['id']}: stage -> in-progress (Sales Director has prepared a package)")
    return advanced


# --------------------------------------------------------------------------
# Revenue dashboard
# --------------------------------------------------------------------------

def open_items(pipeline):
    return [e for e in pipeline if e.get("stage") not in ("won", "lost")]


def business_days_ago(iso_date):
    if not iso_date:
        return None
    try:
        last_touch = datetime.strptime(iso_date, "%Y-%m-%d").date()
    except ValueError:
        return None
    days = 0
    current = last_touch
    while current < TODAY:
        current += timedelta(days=1)
        if current.weekday() < 5:
            days += 1
    return days


def render_table(rows, columns):
    header = "| " + " | ".join(columns) + " |"
    divider = "|" + "|".join(["---"] * len(columns)) + "|"
    lines = [header, divider]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join(lines) if rows else header + "\n" + divider + "\n| _none_ |" + " |" * (len(columns) - 1)


REVENUE_TYPES = ["Consulting Project", "Enterprise Contract", "Workshop", "Speaking Engagement",
                  "Paid Advisory Call", "Grant", "Partnership", "Product Idea", "Licensing"]


def generate_dashboard(pipeline, product_backlog, shipped_products):
    items = pipeline["pipeline"]
    unestimated_count = 0
    stage_rows = []
    for stage_label, stage_key in [("Identified", "identified"), ("Qualified", "qualified"),
                                     ("In Progress", "in-progress"), ("Won (this quarter)", "won"),
                                     ("Lost (this quarter)", "lost"), ("Deferred", "deferred")]:
        stage_items = [e for e in items if e.get("stage") == stage_key]
        weighted = 0.0
        for e in stage_items:
            amount, _ = parse_currency(e.get("expectedRevenue"))
            if amount is None:
                unestimated_count += 1
                continue
            weighted += amount * (e.get("probabilityOfSuccess", 0) / 10)
        stage_rows.append({"Stage": stage_label, "Count": len(stage_items), "Weighted Value": format_amount(weighted, None) if weighted else "0"})

    total_weighted = 0.0
    type_rows = []
    for revenue_type in REVENUE_TYPES:
        type_items = [e for e in open_items(items) if e.get("type") == revenue_type]
        weighted = 0.0
        for e in type_items:
            amount, _ = parse_currency(e.get("expectedRevenue"))
            if amount is not None:
                weighted += amount * (e.get("probabilityOfSuccess", 0) / 10)
        total_weighted += weighted
        type_rows.append({"Type": revenue_type, "Open Items": len(type_items), "Weighted Value": format_amount(weighted, None) if weighted else "0"})

    priority_rows = [{"Item": e["title"], "Organisation": e["organisation"], "Score": e["score"],
                       "Next Action": e.get("nextAction", ""), "Due": e.get("nextActionDue", "")}
                      for e in open_items(items) if e.get("band") == "Priority"]

    at_risk_rows = []
    for e in open_items(items):
        days = business_days_ago(e.get("lastTouch"))
        if days is not None and days >= 5:
            at_risk_rows.append({"Item": e["title"], "Organisation": e["organisation"],
                                   "Last Touch": e.get("lastTouch", ""), "Days Stalled": days})

    won_lost = [e for e in items if e.get("stage") in ("won", "lost")]
    won_lost_text = "\n".join(f"- {e['title']} ({e['organisation']}) — {e['stage']}" for e in won_lost) or "_None this week._"

    shipped_with_results = [p for p in shipped_products.get("shippedProducts", [])
                             if p.get("revenueOrLeadResult") not in (None, "", "Not yet measured")]
    in_development = [p for p in product_backlog.get("backlog", []) if p.get("status") == "in-development"]

    lines = [
        "# Revenue Dashboard", "", f"**Date:** {TODAY.isoformat()}", "",
        "## Pipeline at a Glance", "",
        render_table(stage_rows, ["Stage", "Count", "Weighted Value"]), "",
        f"**Total weighted pipeline value:** {format_amount(total_weighted, None) if total_weighted else '0'}  ",
        f"**Items pending a revenue estimate:** {unestimated_count}", "",
        "## By Revenue Type (Service Line Performance)", "",
        render_table(type_rows, ["Type", "Open Items", "Weighted Value"]), "",
        "## Priority Items Today", "",
        render_table(priority_rows, ["Item", "Organisation", "Score", "Next Action", "Due"]), "",
        "## At Risk (Stalled 5+ Business Days)", "",
        render_table(at_risk_rows, ["Item", "Organisation", "Last Touch", "Days Stalled"]), "",
        "## Won / Lost This Week", "", won_lost_text, "",
        "## Product Revenue Potential", "",
        "**Shipped, with a measured result:**",
    ]
    lines += [f"- {p['title']}: {p['revenueOrLeadResult']}" for p in shipped_with_results] or ["_None measured yet._"]
    lines += ["", "**In development (Product Manager's own score, no revenue projected here):**"]
    lines += [f"- {p['signalDescription']} — {p.get('proposedFormat', '?')}, {p.get('score', '?')}/40"
              for p in in_development] or ["_None in development._"]
    lines += ["", "---", "", "*Source: `pipeline.json`. Feeds `07-Daily-Brief` and `09-CEO-Advisor`.*"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Revenue forecast — 08-Revenue-Hunter/revenue-forecasting-engine.md
# --------------------------------------------------------------------------

def month_key(iso_date):
    if not iso_date:
        return "Unscheduled"
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d").date()
        return d.strftime("%Y-%m")
    except ValueError:
        return "Unscheduled"


def generate_forecast(pipeline):
    items = pipeline["pipeline"]
    months = {}
    for e in items:
        key = month_key(e.get("expectedCloseDate"))
        months.setdefault(key, {"committed": 0.0, "expected": 0.0, "best_case": 0.0, "items": []})

    for e in items:
        key = month_key(e.get("expectedCloseDate"))
        amount, currency = parse_currency(e.get("expectedRevenue"))
        if e.get("stage") == "won":
            if amount is not None:
                months[key]["committed"] += amount
            continue
        if e.get("stage") in ("lost", "deferred"):
            continue
        if amount is None:
            continue
        ev = amount * (e.get("probabilityOfSuccess", 0) / 10)
        months[key]["expected"] += ev
        months[key]["items"].append((e, ev, amount))
        if e.get("band") == "Priority":
            months[key]["best_case"] += amount

    for key in months:
        months[key]["expected"] += months[key]["committed"]
        months[key]["best_case"] += months[key]["committed"]

    ordered_months = sorted(k for k in months if k != "Unscheduled")
    this_month = TODAY.strftime("%Y-%m")

    lines = [
        "# Revenue Forecast", "", f"**Generated:** {TODAY.isoformat()}",
        "**Method:** `revenue-forecasting-engine.md`", "", "---", "", "## This Month", "",
    ]
    this = months.get(this_month, {"committed": 0.0, "expected": 0.0, "best_case": 0.0, "items": []})
    lines += [
        "| Scenario | Amount |", "|---|---|",
        f"| Committed (already won) | {format_amount(this['committed'], None) if this['committed'] else '0'} |",
        f"| Expected (probability-weighted) | {format_amount(this['expected'], None) if this['expected'] else '0'} |",
        f"| Best case (all Priority items close) | {format_amount(this['best_case'], None) if this['best_case'] else '0'} |",
        "", "---", "", "## Next 3 Months (Expected Scenario Only)", "",
        "| Month | Expected value | Concentration risk |", "|---|---|---|",
    ]
    upcoming = [m for m in ordered_months if m >= this_month][:3]
    for m in upcoming:
        data = months[m]
        concentration = ""
        if data["items"] and data["expected"] > 0:
            top_item, top_ev, _ = max(data["items"], key=lambda t: t[1])
            pct = round((top_ev / data["expected"]) * 100)
            concentration = f"{pct}% in {top_item['title']}"
        lines.append(f"| {m} | {format_amount(data['expected'], None) if data['expected'] else '0'} | {concentration} |")
    if not upcoming:
        lines.append("| _none scheduled_ | | |")

    lines += ["", "---", "", "## Highest-Leverage Actions This Month", "",
              "Ranked by leverage (expected-revenue impact of a realistic probability increase), "
              "not by deal size or urgency:", ""]
    leverage_candidates = []
    for e in open_items(items):
        amount, _ = parse_currency(e.get("expectedRevenue"))
        if amount is None:
            continue
        leverage = amount * (2 / 10)
        leverage_candidates.append((e, leverage))
    leverage_candidates.sort(key=lambda t: t[1], reverse=True)
    for i, (e, leverage) in enumerate(leverage_candidates[:3], start=1):
        lines.append(f"{i}. {e['title']} — leverage {format_amount(leverage, None)}, "
                      f"current probability {e.get('probabilityOfSuccess', 0)}/10")
    if not leverage_candidates:
        lines.append("_No items with a real expectedRevenue figure to rank yet._")

    lines += ["", "---", "", "*Feeds `kpi-dashboards/08-revenue-hunter.md` and "
              "`kpi-dashboards/ceo-dashboard.md`'s Pipeline Health read.*"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{TODAY.isoformat()}-{RUN_STARTED.strftime('%H%M%S')}-revenue-hunter.log"
    log_lines = [f"Revenue Hunter Runtime v1.0 — run started {RUN_STARTED.isoformat()}"]

    def log(msg):
        print(msg)
        log_lines.append(msg)

    pipeline = load_json(PIPELINE_PATH, {"pipeline": []})
    opportunity_schema = load_json(OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    crm_data = load_json(CRM_PATH, {"companies": []})
    sales_director_processed = load_json(SALES_DIRECTOR_PROCESSED_PATH, {"processed": {}})
    product_backlog = load_json(PRODUCT_BACKLOG_PATH, {"backlog": []})
    shipped_products = load_json(SHIPPED_PRODUCTS_PATH, {"shippedProducts": []})
    processed_index = load_json(PROCESSED_INDEX_PATH, DEFAULT_PROCESSED_INDEX)
    processed_index.setdefault("addedFromOpportunities", [])
    processed_index.setdefault("addedFromCrm", [])

    added_opp = add_opportunity_entries(pipeline, opportunity_schema, processed_index, log)
    added_crm = add_crm_entries(pipeline, crm_data, processed_index, log)
    advanced = advance_stage_for_prepared_proposals(pipeline, sales_director_processed, log)

    if added_opp or added_crm or advanced:
        save_json(PIPELINE_PATH, pipeline)
        save_json(PROCESSED_INDEX_PATH, processed_index)
    else:
        log("No new pipeline entries or stage changes this run.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dashboard = generate_dashboard(pipeline, product_backlog, shipped_products)
    (AOS_DIR / "output" / "revenue-hunter" / "revenue-dashboard.md").write_text(dashboard, encoding="utf-8")
    (OUTPUT_DIR / f"{TODAY.isoformat()}-revenue-dashboard.md").write_text(dashboard, encoding="utf-8")

    forecast = generate_forecast(pipeline)
    (OUTPUT_DIR / "revenue-forecast.md").write_text(forecast, encoding="utf-8")
    (OUTPUT_DIR / f"{TODAY.isoformat()}-revenue-forecast.md").write_text(forecast, encoding="utf-8")

    log(f"\n{len(added_opp)} opportunity-sourced entries added, {len(added_crm)} CRM-sourced entries added, "
        f"{len(advanced)} stage(s) advanced. Dashboard and forecast written to "
        f"{OUTPUT_DIR.relative_to(REPO_ROOT)}")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
