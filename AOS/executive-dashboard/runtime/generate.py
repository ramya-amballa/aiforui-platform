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
executive-dashboard.md (always overwritten in place), a dated copy in
runtime/output/ for history, an HTML rendering of the same content
(same two locations, plus below), and an immutable dated archive copy
of both formats under AOS/daily-briefs/YYYY/MM/DD/ — this is the one
Daily Executive Brief the Orchestrator's "Daily Brief" step produces.
"""

import html
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
STABLE_HTML_PATH = DASHBOARD_DIR / "executive-dashboard.html"
OUTPUT_DIR = RUNTIME_DIR / "output"
DAILY_BRIEFS_DIR = AOS_DIR / "daily-briefs"

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


def _inline_html(text):
    """Escape, then apply the small set of inline styles this report's
    own markdown actually uses: `code`, **bold**, *italic*. Escaping
    first means a literal & or < in a real company/opportunity name
    can never be interpreted as markup."""
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def _line_html(line):
    """Whole-line underscore italics — this generator's own empty-state
    lines (e.g. "_No open pipeline items yet._") always wrap the
    entire line, never mid-sentence, so this is anchored to the full
    line rather than a general inline substitution: a real company or
    opportunity title containing an underscore (e.g. "ACME_Corp") must
    never be partially italicised."""
    stripped = line.strip()
    if len(stripped) > 2 and stripped.startswith("_") and stripped.endswith("_"):
        return f"<em>{_inline_html(stripped[1:-1])}</em>"
    return _inline_html(line)


def markdown_to_html(report_md, title):
    """A small, deterministic renderer for exactly the markdown
    constructs generate() itself produces (headings, tables, bullet
    lists, bold/italic/code, horizontal rules, plain paragraphs) — not
    a general-purpose markdown parser, and not a second copy of the
    report's business logic: it renders the same lines generate()
    already computed, so there is exactly one place that decides what
    the Daily Executive Brief says."""
    lines = report_md.split("\n")
    html_parts = []
    i = 0
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]

        if line.startswith("|"):
            close_list()
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            header_cells = [c.strip() for c in table_lines[0].strip("|").split("|")]
            html_parts.append("<table>")
            html_parts.append("<thead><tr>" + "".join(f"<th>{_inline_html(c)}</th>" for c in header_cells) + "</tr></thead>")
            html_parts.append("<tbody>")
            for row_line in table_lines[2:]:
                cells = [c.strip() for c in row_line.strip("|").split("|")]
                html_parts.append("<tr>" + "".join(f"<td>{_inline_html(c)}</td>" for c in cells) + "</tr>")
            html_parts.append("</tbody></table>")
            continue

        if line.startswith("### "):
            close_list()
            html_parts.append(f"<h3>{_inline_html(line[4:])}</h3>")
        elif line.startswith("## "):
            close_list()
            html_parts.append(f"<h2>{_inline_html(line[3:])}</h2>")
        elif line.startswith("# "):
            close_list()
            html_parts.append(f"<h1>{_inline_html(line[2:])}</h1>")
        elif line.strip() == "---":
            close_list()
            html_parts.append("<hr>")
        elif line.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{_line_html(line[2:])}</li>")
        elif line.strip() == "":
            close_list()
        else:
            close_list()
            html_parts.append(f"<p>{_line_html(line)}</p>")
        i += 1

    close_list()
    body = "\n".join(html_parts)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title, quote=False)}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
          max-width: 960px; margin: 2rem auto; padding: 0 1.5rem;
          color: #1a1a1a; background: #fff; line-height: 1.5; }}
  h1 {{ font-size: 1.6rem; border-bottom: 2px solid #222; padding-bottom: 0.4rem; }}
  h2 {{ font-size: 1.25rem; margin-top: 2rem; border-bottom: 1px solid #ccc; padding-bottom: 0.3rem; }}
  h3 {{ font-size: 1.05rem; margin-top: 1.5rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: 0.75rem 0; }}
  th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; font-size: 0.92rem; }}
  th {{ background: #f2f2f2; }}
  code {{ background: #f2f2f2; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.9em; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 1.5rem 0; }}
  ul {{ margin: 0.5rem 0; }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #e6e6e6; background: #1a1a1a; }}
    h1 {{ border-color: #555; }}
    h2 {{ border-color: #444; }}
    th, td {{ border-color: #444; }}
    th {{ background: #2a2a2a; }}
    code {{ background: #2a2a2a; }}
    hr {{ border-top-color: #444; }}
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def archive_daily_brief(report_md, report_html, today):
    """AOS/daily-briefs/YYYY/MM/DD/ — an immutable dated archive of the
    one Daily Executive Brief this run produced, in both formats.
    Additive only: the stable executive-dashboard.md/.html and the
    dated runtime/output/ copies this script already wrote are
    untouched."""
    day_dir = DAILY_BRIEFS_DIR / f"{today.year:04d}" / f"{today.month:02d}" / f"{today.day:02d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    (day_dir / "executive-dashboard.md").write_text(report_md, encoding="utf-8")
    (day_dir / "executive-dashboard.html").write_text(report_html, encoding="utf-8")
    return day_dir


def main():
    try:
        opportunities = load_json(OPPORTUNITY_SCHEMA_PATH)["opportunities"]
        pipeline = load_json(PIPELINE_PATH)["pipeline"]
        crm = load_json(CRM_PATH)["companies"]
    except FileNotFoundError as exc:
        print(f"Cannot find a required source file: {exc}", file=sys.stderr)
        return 1

    report = generate(opportunities, pipeline, crm)
    report_html = markdown_to_html(report, "AOS Executive Dashboard")

    STABLE_OUTPUT_PATH.write_text(report, encoding="utf-8")
    STABLE_HTML_PATH.write_text(report_html, encoding="utf-8")
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / f"{TODAY.isoformat()}-executive-dashboard.md").write_text(report, encoding="utf-8")
    (OUTPUT_DIR / f"{TODAY.isoformat()}-executive-dashboard.html").write_text(report_html, encoding="utf-8")

    day_dir = archive_daily_brief(report, report_html, TODAY)

    print(f"Executive Dashboard written to {STABLE_OUTPUT_PATH} and {STABLE_HTML_PATH}")
    print(f"Daily Executive Brief archived to {day_dir.relative_to(AOS_DIR.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
