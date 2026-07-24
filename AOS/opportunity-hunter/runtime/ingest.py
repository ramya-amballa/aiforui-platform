#!/usr/bin/env python3
"""
Opportunity Hunter — Daily Ingestion Workflow (execution mode)

Usage:
    python3 ingest.py

Reads every file in runtime/inbox/ (Markdown or JSON), scores each
opportunity with the exact model in ../opportunity-scoring-engine.md,
classifies it with the same decision tree, appends it to
../opportunity-schema.json, and routes it downstream with no manual
reformatting into:
  - 08-Revenue-Hunter/pipeline.json   (Immediate Proposal, Partnership)
  - 06-CRM/company-intelligence.json (Follow Recruiter, Relationship
    Building, Partnership, Immediate Proposal)
  - 09-CEO-Advisor reads opportunity-schema.json directly, so any
    Priority-band entry is already in its feed once this script exits.

Then writes today's report to runtime/output/ with the six required
views (Top 10, Highest Revenue, Highest ADGL, Highest AI Deployment
Governance, Immediate Application, Relationship Building), and moves
processed inbox files into runtime/processed/ so a re-run never
double-ingests the same file.

INPUT FORMAT

JSON: a single object, or a list of objects, with these fields
(camelCase, matching opportunity-schema.json directly):

    source, sourceCategory, title, organisation, description, url,
    location, remote, domainTags,
    scores: {
        expectedRevenue, probabilityOfWinning, strategicValue,
        relationshipValue, timeRequired, geography, remoteCompatibility,
        alignmentAIforUIServices, alignmentADGL, alignmentOPERA,
        longTermRelationshipPotential
    },
    expectedRevenueAmount   (string, e.g. "AED 45,000" — the actual
                             monetary estimate; distinct from the 0-10
                             scores.expectedRevenue dimension used for
                             scoring),
    scopedEngagement        (bool — is this a named, scoped engagement
                             rather than a general lead?),
    recurrencePattern       ("none" | "content" | "product" — set this
                             when the same theme has appeared more than
                             once; see opportunity-scoring-engine.md's
                             Step 3 for why this overrides the score)

Markdown: one or more records in a single file, separated by a line
containing only "---". Each record is a list of "Key: Value" lines
using the same field names as above (case-insensitive, spaces or
underscores instead of camelCase are both fine, e.g. "Expected Revenue"
or "expected_revenue" both match "expectedRevenue"). Description and
Notes may span multiple lines; everything after the field's line, up
to the next recognised "Key:" line or the "---" separator, belongs to
that field.
"""

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
OPPORTUNITY_HUNTER_DIR = RUNTIME_DIR.parent
AOS_DIR = OPPORTUNITY_HUNTER_DIR.parent

INBOX_DIR = RUNTIME_DIR / "inbox"
PROCESSED_DIR = RUNTIME_DIR / "processed"
OUTPUT_DIR = RUNTIME_DIR / "output"

OPPORTUNITY_SCHEMA_PATH = OPPORTUNITY_HUNTER_DIR / "opportunity-schema.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"

TODAY = date.today().isoformat()

# opportunity-scoring-engine.md, Step 1
SCORE_WEIGHTS = {
    "expectedRevenue": 0.20,
    "probabilityOfWinning": 0.15,
    "strategicValue": 0.10,
    "relationshipValue": 0.10,
    "timeRequired": 0.10,
    "geography": 0.05,
    "remoteCompatibility": 0.05,
    "alignmentAIforUIServices": 0.10,
    "alignmentADGL": 0.05,
    "alignmentOPERA": 0.05,
    "longTermRelationshipPotential": 0.05,
}
SCORE_FIELDS = list(SCORE_WEIGHTS.keys())

# 08-Revenue-Hunter/lead-scoring.md, reusing Opportunity Hunter's
# already-scored 0-10 dimensions rather than asking for a second
# manual judgement on the same underlying facts.
REVENUE_HUNTER_WEIGHTS = {
    "expectedRevenue": 0.35,
    "probabilityOfWinning": 0.30,
    "timeRequired": 0.20,
    "strategicValue": 0.15,
}

REQUIRED_FIELDS = ["title", "organisation", "source"]

# Canonical field name -> accepted aliases, for the Markdown parser.
FIELD_ALIASES = {
    "source": ["source"],
    "sourceCategory": ["sourcecategory", "source category"],
    "title": ["title"],
    "organisation": ["organisation", "organization"],
    "description": ["description"],
    "url": ["url", "link"],
    "location": ["location"],
    "remote": ["remote"],
    "domainTags": ["domaintags", "domain tags"],
    "expectedRevenueAmount": ["expectedrevenueamount", "expected revenue amount"],
    "scopedEngagement": ["scopedengagement", "scoped engagement"],
    "recurrencePattern": ["recurrencepattern", "recurrence pattern"],
    "notes": ["notes"],
    "expectedRevenue": ["expectedrevenue", "expected revenue"],
    "probabilityOfWinning": ["probabilityofwinning", "probability of winning"],
    "strategicValue": ["strategicvalue", "strategic value"],
    "relationshipValue": ["relationshipvalue", "relationship value"],
    "timeRequired": ["timerequired", "time required"],
    "geography": ["geography"],
    "remoteCompatibility": ["remotecompatibility", "remote compatibility"],
    "alignmentAIforUIServices": ["alignmentaiforuiservices", "alignment ai for u&i services", "alignment with ai for u&i services"],
    "alignmentADGL": ["alignmentadgl", "alignment adgl", "alignment with adgl"],
    "alignmentOPERA": ["alignmentopera", "alignment opera", "alignment with opera"],
    "longTermRelationshipPotential": ["longtermrelationshippotential", "long term relationship potential", "long-term relationship potential"],
}
ALIAS_TO_FIELD = {alias: field for field, aliases in FIELD_ALIASES.items() for alias in aliases}
MULTILINE_FIELDS = {"description", "notes"}


# --------------------------------------------------------------------------
# I/O helpers
# --------------------------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
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
# Parsing manually collected input
# --------------------------------------------------------------------------

def parse_markdown(text):
    records = []
    for block in re.split(r"^---\s*$", text, flags=re.MULTILINE):
        block = block.strip()
        if not block:
            continue
        record = {}
        current_field = None
        for line in block.splitlines():
            match = re.match(r"^([A-Za-z][A-Za-z _&-]*):\s*(.*)$", line)
            if match and match.group(1).strip().lower() in ALIAS_TO_FIELD:
                field = ALIAS_TO_FIELD[match.group(1).strip().lower()]
                record[field] = match.group(2).strip()
                current_field = field if field in MULTILINE_FIELDS else None
            elif current_field and line.strip():
                record[current_field] = (record.get(current_field, "") + " " + line.strip()).strip()
        if record:
            records.append(normalise_record(record))
    return records


def normalise_record(record):
    """Flatten a Markdown-parsed record (score fields at top level) into
    the same shape JSON input already uses (score fields under `scores`)."""
    scores = {}
    flat = {}
    for key, value in record.items():
        if key in SCORE_FIELDS:
            scores[key] = _to_number(value)
        else:
            flat[key] = value
    flat["scores"] = scores
    if "remote" in flat:
        flat["remote"] = str(flat["remote"]).strip().lower() in ("true", "yes", "1")
    if "scopedEngagement" in flat:
        flat["scopedEngagement"] = str(flat["scopedEngagement"]).strip().lower() in ("true", "yes", "1")
    if "domainTags" in flat and isinstance(flat["domainTags"], str):
        flat["domainTags"] = [t.strip() for t in flat["domainTags"].split(",") if t.strip()]
    return flat


def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def load_inbox_records():
    records, sources = [], []
    for path in sorted(INBOX_DIR.iterdir()):
        if path.name == ".gitkeep" or path.is_dir():
            continue
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix.lower() == ".json":
                data = json.loads(text)
                items = data if isinstance(data, list) else [data]
            elif path.suffix.lower() in (".md", ".markdown"):
                items = parse_markdown(text)
            else:
                print(f"  skip {path.name}: unsupported extension", file=sys.stderr)
                continue
            for item in items:
                records.append(item)
                sources.append(path)
        except Exception as exc:  # a malformed file must never stop the run
            print(f"  skip {path.name}: {exc}", file=sys.stderr)
    return records, sources


# --------------------------------------------------------------------------
# Scoring and classification — opportunity-scoring-engine.md
# --------------------------------------------------------------------------

def compute_priority_score(scores):
    weighted = sum(scores.get(field, 0) * weight for field, weight in SCORE_WEIGHTS.items())
    return round(weighted * 10)


def band_for(score):
    if score >= 80:
        return "Priority"
    if score >= 50:
        return "Active"
    return "Archived"


def classify(score, scores, source_category, scoped_engagement, recurrence_pattern):
    if recurrence_pattern == "content":
        return "Convert into Content"
    if recurrence_pattern == "product":
        return "Convert into Product Idea"
    if score < 30:
        return "Ignore"
    if source_category == "Recruiter Channel":
        return "Follow Recruiter"
    if score >= 80 and scoped_engagement:
        return "Immediate Proposal"
    if 50 <= score <= 79 and scores.get("relationshipValue", 0) >= 7 and not scoped_engagement:
        return "Relationship Building"
    if source_category == "Consulting Channel" and scores.get("strategicValue", 0) >= 6:
        return "Partnership"
    if 30 <= score <= 49:
        return "Relationship Building"
    return "Apply"


def process_record(record, existing_opportunities):
    missing = [f for f in REQUIRED_FIELDS if not record.get(f)]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")

    scores = {field: _to_number(record.get("scores", {}).get(field, 0)) for field in SCORE_FIELDS}
    priority_score = compute_priority_score(scores)
    band = band_for(priority_score)
    source_category = record.get("sourceCategory", "")
    scoped_engagement = bool(record.get("scopedEngagement", False))
    recurrence_pattern = str(record.get("recurrencePattern", "none")).strip().lower()
    classification = classify(priority_score, scores, source_category, scoped_engagement, recurrence_pattern)

    opportunity = {
        "id": next_id(existing_opportunities, "opp"),
        "dateFound": record.get("dateFound", TODAY),
        "source": record.get("source", ""),
        "sourceCategory": source_category,
        "title": record["title"],
        "organisation": record["organisation"],
        "description": record.get("description", ""),
        "url": record.get("url"),
        "location": record.get("location", "Not specified"),
        "remote": bool(record.get("remote", False)),
        "domainTags": record.get("domainTags", []),
        "scores": scores,
        "priorityScore": priority_score,
        "band": band,
        "classification": classification,
        "routedTo": [],
        "status": "archived" if classification == "Ignore" else "routed",
        "lastTouch": TODAY,
        "nextAction": "",
        "nextActionDue": "",
        "notes": record.get("notes", ""),
        "_expectedRevenueAmount": record.get("expectedRevenueAmount", ""),
    }
    existing_opportunities.append(opportunity)
    return opportunity


# --------------------------------------------------------------------------
# Routing — no manual reformatting, per the routing table in
# opportunity-scoring-engine.md
# --------------------------------------------------------------------------

def route_to_revenue_hunter(opportunity, pipeline_data):
    scores = opportunity["scores"]
    rh_weighted = sum(scores.get(field, 0) * weight for field, weight in REVENUE_HUNTER_WEIGHTS.items())
    rh_score = round(rh_weighted * 10)
    rh_band = "Priority" if rh_score >= 80 else "Active" if rh_score >= 50 else "Deferred"
    due_days = 1 if opportunity["classification"] == "Immediate Proposal" else 3

    entry = {
        "id": next_id(pipeline_data["pipeline"], "rev"),
        "dateAdded": TODAY,
        "type": "Partnership" if opportunity["classification"] == "Partnership" else "Consulting Project",
        "title": opportunity["title"],
        "organisation": opportunity["organisation"],
        "sourceRef": opportunity["id"],
        "expectedRevenue": opportunity["_expectedRevenueAmount"] or "Not yet estimated",
        "probabilityOfSuccess": scores.get("probabilityOfWinning", 0),
        "effortRequired": scores.get("timeRequired", 0),
        "strategicValue": scores.get("strategicValue", 0),
        "score": rh_score,
        "band": rh_band,
        "stage": "identified",
        "owner": "Ramya",
        "lastTouch": TODAY,
        "nextAction": "Send first-touch proposal" if opportunity["classification"] == "Immediate Proposal" else "Explore partnership terms",
        "nextActionDue": (date.today() + timedelta(days=due_days)).isoformat(),
        "expectedCloseDate": None,
    }
    pipeline_data["pipeline"].append(entry)
    return entry


TEMPERATURE_RANK = {"cold": 0, "cooling": 1, "warm": 2, "hot": 3}
FOLLOW_UP_DAYS = {"hot": 3, "warm": 10}


def route_to_crm(opportunity, crm_data):
    target_temperature = "hot" if opportunity["classification"] == "Immediate Proposal" else "warm"
    existing = next((c for c in crm_data["companies"] if c.get("companyName") == opportunity["organisation"]), None)

    outreach_entry = {
        "date": TODAY,
        "channel": opportunity["source"],
        "summary": f"Opportunity Hunter logged: {opportunity['title']} ({opportunity['classification']})",
    }

    if existing is None:
        existing = {
            "companyName": opportunity["organisation"],
            "industry": "Not specified",
            "aiMaturity": "Unknown",
            "regulations": opportunity["domainTags"],
            "existingRelationship": "none",
            "recruiter": opportunity["source"] if opportunity["sourceCategory"] == "Recruiter Channel" else None,
            "previousApplications": [],
            "tailoredPositioning": "",
            "lastTouch": TODAY,
            "relationshipTemperature": target_temperature,
            "nextFollowUpDue": (date.today() + timedelta(days=FOLLOW_UP_DAYS.get(target_temperature, 10))).isoformat(),
            "outreachHistory": [outreach_entry],
            "notes": "",
        }
        crm_data["companies"].append(existing)
    else:
        existing["lastTouch"] = TODAY
        if TEMPERATURE_RANK.get(target_temperature, 0) > TEMPERATURE_RANK.get(existing.get("relationshipTemperature", "cold"), 0):
            existing["relationshipTemperature"] = target_temperature
            existing["nextFollowUpDue"] = (date.today() + timedelta(days=FOLLOW_UP_DAYS.get(target_temperature, 10))).isoformat()
        existing.setdefault("outreachHistory", []).append(outreach_entry)
        if opportunity["sourceCategory"] == "Recruiter Channel" and not existing.get("recruiter"):
            existing["recruiter"] = opportunity["source"]

    if opportunity["classification"] in ("Apply", "Immediate Proposal"):
        existing.setdefault("previousApplications", []).append({
            "date": TODAY,
            "role": opportunity["title"],
            "outcome": "applied",
        })

    return existing


def route(opportunity, pipeline_data, crm_data):
    routed_to = []
    classification = opportunity["classification"]

    if classification in ("Immediate Proposal", "Partnership"):
        route_to_revenue_hunter(opportunity, pipeline_data)
        routed_to.append("08-Revenue-Hunter/pipeline.json")

    if classification in ("Follow Recruiter", "Relationship Building", "Partnership", "Immediate Proposal"):
        route_to_crm(opportunity, crm_data)
        routed_to.append("06-CRM/company-intelligence.json")

    if opportunity["band"] == "Priority":
        routed_to.append("09-CEO-Advisor (reads opportunity-schema.json directly)")

    opportunity["routedTo"] = routed_to


# --------------------------------------------------------------------------
# Daily report — the six required views
# --------------------------------------------------------------------------

def render_table(rows, columns):
    header = "| " + " | ".join(columns) + " |"
    divider = "|" + "|".join(["---"] * len(columns)) + "|"
    lines = [header, divider]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join(lines) if rows else header + "\n" + divider + "\n| _none today_ |" + " |" * (len(columns) - 1)


def generate_report(processed):
    top_10 = sorted(processed, key=lambda o: o["priorityScore"], reverse=True)[:10]
    highest_revenue = sorted(processed, key=lambda o: o["scores"].get("expectedRevenue", 0), reverse=True)[:10]
    adgl = [o for o in processed if "ADGL" in o["domainTags"]]
    deployment_governance = [o for o in processed if "AI Deployment Governance" in o["domainTags"]]
    immediate_application = [o for o in processed if o["classification"] in ("Immediate Proposal", "Apply")]
    relationship_building = [o for o in processed if o["classification"] in ("Relationship Building", "Follow Recruiter")]

    def rows(items, extra_col=None):
        out = []
        for o in items:
            row = {"Title": o["title"], "Organisation": o["organisation"], "Score": o["priorityScore"], "Classification": o["classification"]}
            if extra_col:
                row[extra_col[0]] = extra_col[1](o)
            out.append(row)
        return out

    report = f"""# Daily Opportunity Report — Execution Mode

**Date:** {TODAY}
**Opportunities processed today:** {len(processed)}

## Today's Top 10 Opportunities

{render_table(rows(top_10), ["Title", "Organisation", "Score", "Classification"])}

## Highest Revenue Opportunities

{render_table(rows(highest_revenue, ("Expected Revenue Score", lambda o: o["scores"].get("expectedRevenue", 0))), ["Title", "Organisation", "Expected Revenue Score", "Score"])}

## Highest ADGL Opportunities

{render_table(rows(adgl), ["Title", "Organisation", "Score", "Classification"])}

## Highest AI Deployment Governance Opportunities

{render_table(rows(deployment_governance), ["Title", "Organisation", "Score", "Classification"])}

## Opportunities Requiring Immediate Application

{render_table(rows(immediate_application), ["Title", "Organisation", "Score", "Classification"])}

## Opportunities Requiring Relationship Building

{render_table(rows(relationship_building), ["Title", "Organisation", "Score", "Classification"])}

---

*Routed today: {sum(1 for o in processed if o['routedTo'])} of {len(processed)} opportunities written
to at least one downstream file. See each opportunity's `routedTo` in
`opportunity-schema.json` for exactly where.*
"""
    return report


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    records, source_files = load_inbox_records()
    if not records:
        print("No new opportunities in runtime/inbox/. Nothing to do.")
        return 0

    schema_data = load_json(OPPORTUNITY_SCHEMA_PATH)
    pipeline_data = load_json(PIPELINE_PATH)
    crm_data = load_json(CRM_PATH)

    processed = []
    for record in records:
        try:
            opportunity = process_record(record, schema_data["opportunities"])
            route(opportunity, pipeline_data, crm_data)
            opportunity.pop("_expectedRevenueAmount", None)
            processed.append(opportunity)
            print(f"  {opportunity['id']}: {opportunity['title']} -> {opportunity['priorityScore']}/100 "
                  f"({opportunity['band']}) -> {opportunity['classification']}")
        except ValueError as exc:
            print(f"  skip record ({record.get('title', 'untitled')}): {exc}", file=sys.stderr)

    if not processed:
        print("Every record in the inbox failed validation. Nothing was written.", file=sys.stderr)
        return 1

    save_json(OPPORTUNITY_SCHEMA_PATH, schema_data)
    save_json(PIPELINE_PATH, pipeline_data)
    save_json(CRM_PATH, crm_data)

    OUTPUT_DIR.mkdir(exist_ok=True)
    report_path = OUTPUT_DIR / f"{TODAY}-daily-report.md"
    report_path.write_text(generate_report(processed), encoding="utf-8")

    PROCESSED_DIR.mkdir(exist_ok=True)
    for path in sorted(set(source_files)):
        path.rename(PROCESSED_DIR / path.name)

    print(f"\n{len(processed)} opportunities processed. Report: {report_path.relative_to(AOS_DIR.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
