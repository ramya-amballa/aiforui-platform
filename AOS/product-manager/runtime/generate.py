#!/usr/bin/env python3
"""
Product Manager — Evaluation Runtime (v1.0)

Usage:
    python3 generate.py

Executes ../../03-Product-Manager/product-evaluation-framework.md
(Steps 2-4) against four real signal sources — see
../product-manager-runtime-notes.md for exactly which source answers
which question and why none of it re-decides another employee's work:

  - product-backlog.json entries Market Intelligence already wrote
    with score: null — evaluated in place (the only write this script
    makes outside product-manager/)
  - demand-intelligence/opportunity-schema.json entries classified
    "Convert into Product Idea" (Demand Intelligence's own decision
    tree, never re-derived here)
  - sales-director/runtime/processed-index.json, grouped by domainTags
    to detect a real recurring pattern (a count of real records, not
    an invented one)
  - content-director/runtime/queue/content-queue.json, as additional
    raw candidates for this framework's own, different four-dimension
    evaluation

Every new or updated backlog entry gets a real 0-40 score
(product-evaluation-framework.md's demand/build-effort/differentiation/
revenue dimensions, made deterministic in that file's "Runtime
Execution Notes" section) and a status: in-development (30+),
candidate (15-29), or parked (below 15). CEO Advisor already reads
product-backlog.json directly (decision-model.md's existing 0-40 ->
divide-by-4 row) — this script does not add a new feed file, it makes
that existing integration real.

This script never builds, ships, or announces a product. Every output
is a row in product-backlog.json for the founder to act on by hand.
"""

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
PRODUCT_MANAGER_DIR = RUNTIME_DIR.parent
AOS_DIR = PRODUCT_MANAGER_DIR.parent
REPO_ROOT = AOS_DIR.parent

PRODUCT_BACKLOG_PATH = AOS_DIR / "03-Product-Manager" / "product-backlog.json"
OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "demand-intelligence" / "opportunity-schema.json"
SALES_DIRECTOR_PROCESSED_PATH = AOS_DIR / "sales-director" / "runtime" / "processed-index.json"
CONTENT_QUEUE_LOG_PATH = AOS_DIR / "content-director" / "runtime" / "queue" / "content-queue.json"
PRACTITIONER_BANK_PATH = AOS_DIR / "sales-director" / "runtime" / "config" / "practitioner-bank.json"

QUEUE_DIR = RUNTIME_DIR / "queue"
PROCESSED_INDEX_PATH = QUEUE_DIR / "processed-index.json"
OUTPUT_DIR = RUNTIME_DIR / "output"
LOGS_DIR = RUNTIME_DIR / "logs"

TODAY = date.today().isoformat()
RUN_STARTED = datetime.now(timezone.utc)

FORMAT_KEYWORDS = [
    ("Toolkit", ["toolkit", "bundle", "template pack"]),
    ("Checklist", ["checklist", "verification", "single check"]),
    ("Executive Guide", ["executive", "board", "overview", "briefing"]),
    ("Assessment", ["assessment", "self-score", "diagnostic", "maturity"]),
    ("Course", ["course", "curriculum", "multi-part"]),
    ("Workshop", ["workshop", "live session", "facilitated", "cohort"]),
    ("Subscription", ["subscription", "ongoing access", "recurring access"]),
]
BUILD_EFFORT_KEYWORDS = ["toolkit", "checklist", "template", "framework"]

DEFAULT_PROCESSED_INDEX = {
    "schema": {
        "processedOpportunities": "array of demand-intelligence ids already evaluated",
        "processedPatterns": "array of domainTag pattern keys already evaluated",
        "processedContentSignals": "array of content-director content-queue ids already evaluated",
    },
    "processedOpportunities": [],
    "processedPatterns": [],
    "processedContentSignals": [],
}


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


def _matches(text, term):
    return re.search(r"\b" + re.escape(term) + r"s?\b", text) is not None


# --------------------------------------------------------------------------
# Signal collection
# --------------------------------------------------------------------------

def collect_unscored_backlog_signals(product_backlog):
    return [entry for entry in product_backlog.get("backlog", []) if entry.get("score") is None]


def collect_opportunity_signals(opportunity_schema, processed_index):
    signals = []
    for opp in opportunity_schema.get("opportunities", []):
        if opp.get("classification") != "Convert into Product Idea":
            continue
        if opp["id"] in processed_index["processedOpportunities"]:
            continue
        signals.append({
            "signalType": "opportunity", "naturalId": opp["id"],
            "signalDescription": f"{opp['title']} ({opp['organisation']})",
            "domainTags": opp.get("domainTags", []), "occurrenceCount": 1,
        })
    return signals


def collect_sales_director_patterns(sales_director_processed, opportunity_schema, processed_index):
    opp_by_id = {o["id"]: o for o in opportunity_schema.get("opportunities", [])}
    tag_counts = {}
    for opp_id in sales_director_processed.get("processed", {}):
        opp = opp_by_id.get(opp_id)
        if not opp:
            continue
        for tag in opp.get("domainTags", []):
            tag_counts.setdefault(tag, set()).add(opp_id)

    signals = []
    for tag, opp_ids in tag_counts.items():
        if len(opp_ids) < 2:
            continue
        pattern_key = f"sd-pattern-{tag}"
        if pattern_key in processed_index["processedPatterns"]:
            continue
        signals.append({
            "signalType": "sales-director-pattern", "naturalId": pattern_key,
            "signalDescription": f"Recurring demand pattern: {len(opp_ids)} prepared proposals share the '{tag}' domain",
            "domainTags": [tag], "occurrenceCount": len(opp_ids),
        })
    return signals


def collect_content_director_signals(content_queue_log, processed_index):
    signals = []
    for entry in content_queue_log.get("queue", []):
        if entry["id"] in processed_index["processedContentSignals"]:
            continue
        domain_tags = ["ADGL"] if "adgl" in entry["title"].lower() else ["AI Governance"]
        signals.append({
            "signalType": "content-director", "naturalId": entry["id"],
            "signalDescription": entry["title"], "domainTags": domain_tags, "occurrenceCount": 1,
        })
    return signals


# --------------------------------------------------------------------------
# Format matching — product-evaluation-framework.md, Step 2
# --------------------------------------------------------------------------

def match_format(signal_description, domain_tags):
    text = signal_description.lower()
    if "ADGL" in domain_tags or _matches(text, "adgl"):
        return "ADGL Extension"
    for format_name, terms in FORMAT_KEYWORDS:
        if any(_matches(text, term) for term in terms):
            return format_name
    return "OPERA Module"


# --------------------------------------------------------------------------
# Content bank grounding (differentiation dimension) — reused, not
# re-collected, same bank Sales Director and Content Director already use
# --------------------------------------------------------------------------

def has_bank_grounding(domain_tags, bank):
    domain_set = set(domain_tags)
    if not domain_set:
        return False
    for item in bank.get("practitionerExperience", []) + bank.get("products", []):
        if domain_set & set(item.get("domainTags", [])):
            return True
    return False


# --------------------------------------------------------------------------
# Scoring — product-evaluation-framework.md Step 3, made deterministic
# in its "Runtime Execution Notes" section
# --------------------------------------------------------------------------

def score_signal(signal_description, domain_tags, occurrence_count, signal_type, matched_format, bank):
    text = signal_description.lower()

    demand = min(10, 4 + 2 * occurrence_count)

    if matched_format in ("ADGL Extension", "OPERA Module"):
        build_effort = 8
    elif sum(1 for t in BUILD_EFFORT_KEYWORDS if _matches(text, t)) >= 2:
        build_effort = 7
    else:
        build_effort = 5

    differentiation = 6 if has_bank_grounding(domain_tags, bank) else 3

    revenue = 7 if signal_type in ("opportunity", "sales-director-pattern") else 5

    return demand, build_effort, differentiation, revenue


def status_for_score(score):
    if score >= 30:
        return "in-development"
    if score >= 15:
        return "candidate"
    return "parked"


def revenue_note(revenue):
    if revenue >= 7:
        return "Clear lead-gen or revenue role (grounded in a real qualified signal)."
    return "Not yet confirmed — revisit if the signal repeats."


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{TODAY}-{RUN_STARTED.strftime('%H%M%S')}-product-manager.log"
    log_lines = [f"Product Manager Runtime v1.0 — run started {RUN_STARTED.isoformat()}"]

    def log(msg):
        print(msg)
        log_lines.append(msg)

    product_backlog = load_json(PRODUCT_BACKLOG_PATH, {"backlog": []})
    opportunity_schema = load_json(OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    sales_director_processed = load_json(SALES_DIRECTOR_PROCESSED_PATH, {"processed": {}})
    content_queue_log = load_json(CONTENT_QUEUE_LOG_PATH, {"queue": []})
    practitioner_bank = load_json(PRACTITIONER_BANK_PATH, {"practitionerExperience": [], "products": []})
    processed_index = load_json(PROCESSED_INDEX_PATH, DEFAULT_PROCESSED_INDEX)
    for key in ("processedOpportunities", "processedPatterns", "processedContentSignals"):
        processed_index.setdefault(key, [])

    unscored_entries = collect_unscored_backlog_signals(product_backlog)
    new_signals = (
        collect_opportunity_signals(opportunity_schema, processed_index)
        + collect_sales_director_patterns(sales_director_processed, opportunity_schema, processed_index)
        + collect_content_director_signals(content_queue_log, processed_index)
    )

    if not unscored_entries and not new_signals:
        log("No new or unscored signals from any source. Nothing to do.")
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        return 0

    evaluated = []

    for entry in unscored_entries:
        domain_tags = []  # product-backlog.json entries don't carry domainTags; match on description text only
        matched_format = match_format(entry["signalDescription"], domain_tags)
        demand, build_effort, differentiation, revenue = score_signal(
            entry["signalDescription"], domain_tags, 1, "market-intelligence", matched_format, practitioner_bank)
        score = demand + build_effort + differentiation + revenue
        status = status_for_score(score)

        entry["proposedFormat"] = matched_format
        entry["score"] = score
        entry["status"] = status
        entry["revenueOrLeadPotential"] = revenue_note(revenue)
        entry["notes"] = (entry.get("notes", "") + " " +
                          f"Evaluated by Product Manager Runtime v1.0 on {TODAY}. "
                          f"Demand {demand}/10, Build effort {build_effort}/10, "
                          f"Differentiation {differentiation}/10, Revenue {revenue}/10 = {score}/40.").strip()

        evaluated.append((entry["id"], entry["signalDescription"], matched_format, score, status))
        log(f"  {entry['id']}: {entry['signalDescription'][:60]} -> {matched_format}, {score}/40 -> {status}")

    for signal in new_signals:
        matched_format = match_format(signal["signalDescription"], signal["domainTags"])
        demand, build_effort, differentiation, revenue = score_signal(
            signal["signalDescription"], signal["domainTags"], signal["occurrenceCount"],
            signal["signalType"], matched_format, practitioner_bank)
        score = demand + build_effort + differentiation + revenue
        status = status_for_score(score)

        new_entry = {
            "id": next_id(product_backlog["backlog"], "prod"),
            "dateAdded": TODAY,
            "signalSource": {"opportunity": "Demand Intelligence", "sales-director-pattern": "Sales Director",
                              "content-director": "Content Director"}[signal["signalType"]],
            "signalDescription": signal["signalDescription"],
            "proposedFormat": matched_format,
            "score": score,
            "status": status,
            "revenueOrLeadPotential": revenue_note(revenue),
            "owner": "",
            "notes": f"Evaluated by Product Manager Runtime v1.0 on {TODAY}. "
                     f"Demand {demand}/10, Build effort {build_effort}/10, "
                     f"Differentiation {differentiation}/10, Revenue {revenue}/10 = {score}/40.",
        }
        product_backlog["backlog"].append(new_entry)

        if signal["signalType"] == "opportunity":
            processed_index["processedOpportunities"].append(signal["naturalId"])
        elif signal["signalType"] == "sales-director-pattern":
            processed_index["processedPatterns"].append(signal["naturalId"])
        elif signal["signalType"] == "content-director":
            processed_index["processedContentSignals"].append(signal["naturalId"])

        evaluated.append((new_entry["id"], signal["signalDescription"], matched_format, score, status))
        log(f"  {new_entry['id']}: [{signal['signalType']}] {signal['signalDescription'][:60]} "
            f"-> {matched_format}, {score}/40 -> {status}")

    save_json(PRODUCT_BACKLOG_PATH, product_backlog)
    save_json(PROCESSED_INDEX_PATH, processed_index)

    OUTPUT_DIR.mkdir(exist_ok=True)
    report_lines = [
        "# Product Manager — Daily Report", "", f"**Date:** {TODAY}",
        f"**Signals evaluated:** {len(evaluated)}", "",
        "| ID | Signal | Format | Score | Status |", "|---|---|---|---|---|",
    ]
    for entry_id, description, fmt, score, status in evaluated:
        report_lines.append(f"| {entry_id} | {description[:60]} | {fmt} | {score}/40 | {status} |")
    report_path = OUTPUT_DIR / f"{TODAY}-product-manager-report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    log(f"\n{len(evaluated)} signals evaluated. Report: {report_path.relative_to(REPO_ROOT)}")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
