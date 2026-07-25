#!/usr/bin/env python3
"""
Market Intelligence — Runtime v1.0

Usage:
    python3 monitor.py

Checks every source configured in config/sources.json (a source with
no feed URLs yet prints a skip message and is left alone — connector-
ready, not simulated, exactly like demand-intelligence's collectors).
Every entry not already in seen-index.json is substantive by
definition (see ../market-intelligence-classification-model.md) and is
run through six deterministic checks: consultingOpportunity,
linkedinContent, websiteUpdate, newProduct, affectsADGL, affectsOPERA.

Every substantive entry is logged to ../regulatory-log.json. Structured
(never drafted) records are then routed:
  - consultingOpportunity  -> demand-intelligence/runtime/inbox/
                              (scored/classified by the existing,
                              unmodified opportunity-scoring-engine.md
                              on the next Demand Intelligence run)
  - linkedinContent or
    websiteUpdate           -> 02-Content-Director/content-brief-queue.json
  - newProduct              -> 03-Product-Manager/product-backlog.json
                              (signalSource: "Market Intelligence",
                              left unscored for Product Manager's own
                              evaluation)
  - every substantive entry -> output/ceo-advisor-feed.json (the six
                              checks only, never a draft)

Also writes output/{date}-market-intelligence-report.md, a plain
summary of what ran today.

This script does not draft content, does not score or classify the
opportunities it hands to Demand Intelligence, and does not evaluate or
format the candidates it hands to Product Manager. See
../market-intelligence-classification-model.md, "What This Runtime
Does Not Do."
"""

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

import feeds

RUNTIME_DIR = Path(__file__).resolve().parent
MARKET_INTEL_DIR = RUNTIME_DIR.parent
AOS_DIR = MARKET_INTEL_DIR.parent
REPO_ROOT = AOS_DIR.parent

REGULATORY_LOG_PATH = MARKET_INTEL_DIR / "regulatory-log.json"
SOURCES_CONFIG_PATH = RUNTIME_DIR / "config" / "sources.json"
SEEN_INDEX_PATH = RUNTIME_DIR / "seen-index.json"
OUTPUT_DIR = RUNTIME_DIR / "output"
CEO_FEED_PATH = OUTPUT_DIR / "ceo-advisor-feed.json"

CONTENT_QUEUE_PATH = AOS_DIR / "02-Content-Director" / "content-brief-queue.json"
PRODUCT_BACKLOG_PATH = AOS_DIR / "03-Product-Manager" / "product-backlog.json"
OPPORTUNITY_INBOX_DIR = AOS_DIR / "demand-intelligence" / "runtime" / "inbox"

TODAY = date.today().isoformat()

# market-intelligence-classification-model.md, "The Six Checks"
CONSULTING_TERMS = ["enforcement action", "penalty", "fine", "compliance deadline", "mandatory",
                     "must comply", "audit requirement", "certification required"]
MINOR_UPDATE_TERMS = ["corrigendum", "typographical", "housekeeping", "minor amendment"]
WEBSITE_UPDATE_TERMS = ["supersedes", "replaces", "new version", "revises", "updated requirements"]
NEW_PRODUCT_TERMS = ["framework", "toolkit", "assessment", "certification", "mandatory", "requirement"]
ADGL_TERMS = ["ai deployment", "ai system", "ai lifecycle", "production ai"]
AI_NATIVE_SOURCES = {"Microsoft AI", "OpenAI Enterprise", "Anthropic"}

DEFAULT_SEEN_INDEX = {
    "schema": {
        "key": "string — sha256(link, or source|title when there's no link)[:16]",
        "firstSeen": "string — ISO 8601 date",
        "source": "string",
        "title": "string",
    },
    "seen": {},
}

DEFAULT_CONTENT_QUEUE = {
    "schema": {
        "id": "string — e.g. brief-0001",
        "dateFlagged": "string — ISO 8601 date",
        "regulatoryLogRef": "string — id in 05-Market-Intelligence/regulatory-log.json",
        "source": "string",
        "developmentSummary": "string — factual, from the source, not a drafted angle",
        "url": "string or null",
        "triggeredBy": "array of strings — linkedinContent and/or websiteUpdate",
        "affectsADGL": "boolean",
        "affectsOPERA": "boolean",
        "status": "string — queued, briefed, published, declined",
    },
    "queue": [],
}

DEFAULT_CEO_FEED = {
    "schema": {
        "id": "string",
        "source": "string",
        "title": "string",
        "url": "string or null",
        "checks": "object — the six booleans, never a draft",
        "routedTo": "array of strings",
    },
    "feed": [],
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
    # Trailing "s?" tolerates simple plurals ("ai deployment" also
    # matches "ai deployments") without reopening the substring-false-
    # positive problem word-boundary matching exists to avoid — the
    # leading \b still blocks a match inside an unrelated word.
    return re.search(r"\b" + re.escape(term) + r"s?\b", text) is not None


def dedupe_key(source_name, entry):
    basis = entry.get("link") or f"{source_name}|{entry.get('title', '')}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def classify(title, summary, source_name):
    text = f"{title} {summary}".lower()

    consulting_hits = [t for t in CONSULTING_TERMS if _matches(text, t)]
    minor_hits = [t for t in MINOR_UPDATE_TERMS if _matches(text, t)]
    website_hits = [t for t in WEBSITE_UPDATE_TERMS if _matches(text, t)]
    product_hits = [t for t in NEW_PRODUCT_TERMS if _matches(text, t)]
    adgl_hits = [t for t in ADGL_TERMS if _matches(text, t)]

    consulting = bool(consulting_hits)
    linkedin = not bool(minor_hits)
    website = bool(website_hits)
    new_product = len(product_hits) >= 2
    affects_adgl = source_name in AI_NATIVE_SOURCES or bool(adgl_hits)
    affects_opera = True

    reasons = {
        "consultingOpportunity": (f"Matched: {', '.join(consulting_hits)}" if consulting
                                   else "No enforcement/penalty/compliance-deadline language found."),
        "linkedinContent": (f"Flagged as a minor update: {', '.join(minor_hits)}" if minor_hits
                             else "Substantive development in a tracked source."),
        "websiteUpdate": (f"Matched: {', '.join(website_hits)}" if website
                           else "No supersedes/replaces/revises language found."),
        "newProduct": (f"Matched {len(product_hits)} of: {', '.join(product_hits)}" if new_product
                        else (f"Only {len(product_hits)} match(es) ({', '.join(product_hits)}); needs 2+" if product_hits
                              else "No framework/toolkit/assessment/certification/requirement language found.")),
        "affectsADGL": (f"Source '{source_name}' is an AI-deployment vendor" if source_name in AI_NATIVE_SOURCES
                         else (f"Matched: {', '.join(adgl_hits)}" if adgl_hits
                               else "No AI-deployment-specific language found, and source is not an AI-native vendor.")),
        "affectsOPERA": "Every substantive development from a tracked source is governance-relevant; "
                        "OPERA is the umbrella methodology.",
    }

    return {
        "consultingOpportunity": consulting, "linkedinContent": linkedin, "websiteUpdate": website,
        "newProduct": new_product, "affectsADGL": affects_adgl, "affectsOPERA": affects_opera,
        "reasons": reasons,
    }


def opportunity_scores(checks):
    """Heuristic 0-10 scores for a market-wide (not a specific named
    lead) consulting signal — same honesty convention as
    demand-intelligence/runtime/collectors/common.py's heuristic_scores:
    conservative, documented, and flagged autoScored so a human knows
    to verify rather than treat it as finished."""
    return {
        "expectedRevenue": 5, "probabilityOfWinning": 3,
        "strategicValue": 7 if checks["consultingOpportunity"] else 5,
        "relationshipValue": 2, "timeRequired": 6, "geography": 6, "remoteCompatibility": 8,
        "alignmentAIforUIServices": 8,
        "alignmentADGL": 8 if checks["affectsADGL"] else 4,
        "alignmentOPERA": 8, "longTermRelationshipPotential": 5,
    }


def route_to_demand_intelligence(source_name, source_config, entry, checks, inbox_batch):
    domain_tags = source_config.get("domainTags") or ["AI Governance"]
    raw_summary = entry.get("summary") or entry["title"]
    description = (
        f"{raw_summary} This {source_name} development creates a potential AI governance advisory "
        f"opportunity for organisations required to respond to it."
    )
    inbox_batch.append({
        "source": f"Market Intelligence: {source_name}",
        "sourceCategory": "Compliance Programme",
        "title": f"{source_name}: {entry['title']}",
        "organisation": f"Market-wide: organisations affected by {source_name}",
        "description": description,
        "url": entry.get("link"),
        "location": "Not specified",
        "remote": True,
        "domainTags": domain_tags,
        "scores": opportunity_scores(checks),
        "scopedEngagement": False,
        "recurrencePattern": "none",
        "autoCollected": True,
        "autoScored": True,
        "matchedKeywords": [source_name],
    })


def route_to_content_director(regulatory_log_id, source_name, entry, checks, content_queue):
    triggered_by = [k for k in ("linkedinContent", "websiteUpdate") if checks[k]]
    content_queue["queue"].append({
        "id": next_id(content_queue["queue"], "brief"),
        "dateFlagged": TODAY,
        "regulatoryLogRef": regulatory_log_id,
        "source": source_name,
        "developmentSummary": entry.get("summary") or entry["title"],
        "url": entry.get("link"),
        "triggeredBy": triggered_by,
        "affectsADGL": checks["affectsADGL"],
        "affectsOPERA": checks["affectsOPERA"],
        "status": "queued",
    })


def route_to_product_manager(regulatory_log_id, source_name, entry, product_backlog):
    product_backlog["backlog"].append({
        "id": next_id(product_backlog["backlog"], "prod"),
        "dateAdded": TODAY,
        "signalSource": "Market Intelligence",
        "signalDescription": f"{source_name}: {entry['title']}",
        "proposedFormat": None,
        "score": None,
        "status": "candidate",
        "revenueOrLeadPotential": "Not yet evaluated",
        "owner": "",
        "notes": f"Auto-flagged by Market Intelligence Runtime (regulatory-log.json {regulatory_log_id}) "
                 f"from {entry.get('link') or 'source feed'}. Awaiting Product Manager evaluation.",
    })


def main():
    sources_config = load_json(SOURCES_CONFIG_PATH, {"sources": []})
    seen_index = load_json(SEEN_INDEX_PATH, DEFAULT_SEEN_INDEX)
    seen_index.setdefault("seen", {})
    regulatory_log = load_json(REGULATORY_LOG_PATH)
    regulatory_log.setdefault("log", [])

    new_entries = []  # (source_name, source_config, entry)
    for source in sources_config.get("sources", []):
        name = source["name"]
        feed_urls = source.get("feedUrls") or []
        if not feed_urls:
            print(f"  {name}: no feed URLs configured, skipping")
            continue
        for url in feed_urls:
            entries = feeds.fetch_feed_entries(url)
            for entry in entries:
                key = dedupe_key(name, entry)
                if key in seen_index["seen"]:
                    continue
                seen_index["seen"][key] = {"firstSeen": TODAY, "source": name, "title": entry.get("title", "")}
                new_entries.append((name, source, entry))

    save_json(SEEN_INDEX_PATH, seen_index)

    if not new_entries:
        print("No new developments across any configured source. Nothing to do.")
        return 0

    content_queue = load_json(CONTENT_QUEUE_PATH, DEFAULT_CONTENT_QUEUE)
    content_queue.setdefault("queue", [])
    product_backlog = load_json(PRODUCT_BACKLOG_PATH, {"backlog": []})
    product_backlog.setdefault("backlog", [])
    ceo_feed = load_json(CEO_FEED_PATH, DEFAULT_CEO_FEED)
    ceo_feed.setdefault("feed", [])
    inbox_batch = []

    run_summary = []
    for source_name, source_config, entry in new_entries:
        checks = classify(entry.get("title", ""), entry.get("summary", ""), source_name)

        log_id = next_id(regulatory_log["log"], "reg")
        routed_to = []

        if checks["consultingOpportunity"]:
            route_to_demand_intelligence(source_name, source_config, entry, checks, inbox_batch)
            routed_to.append("demand-intelligence/runtime/inbox")
        if checks["linkedinContent"] or checks["websiteUpdate"]:
            route_to_content_director(log_id, source_name, entry, checks, content_queue)
            routed_to.append("02-Content-Director/content-brief-queue.json")
        if checks["newProduct"]:
            route_to_product_manager(log_id, source_name, entry, product_backlog)
            routed_to.append("03-Product-Manager/product-backlog.json")

        ceo_feed["feed"].append({
            "id": log_id, "source": source_name, "title": entry.get("title", ""),
            "url": entry.get("link"),
            "checks": {k: v for k, v in checks.items() if k != "reasons"},
            "routedTo": routed_to + ["09-CEO-Advisor (via runtime/output/ceo-advisor-feed.json)"],
        })

        regulatory_log["log"].append({
            "id": log_id,
            "date": TODAY,
            "source": source_name,
            "summary": entry.get("summary") or entry.get("title", ""),
            "url": entry.get("link"),
            "substantive": True,
            "triggers": {
                "linkedinIdea": "Queued to Content Director" if checks["linkedinContent"] else None,
                "newsletterIdea": None,
                "productUpdate": "Queued to Product Manager" if checks["newProduct"] else "not applicable — did not meet the new-product threshold",
                "consultingOpportunity": "Routed to Demand Intelligence" if checks["consultingOpportunity"] else "not applicable — no enforcement/compliance-deadline language found",
            },
            "checks": checks,
            "routedTo": routed_to + ["09-CEO-Advisor"],
        })
        run_summary.append((source_name, entry.get("title", ""), checks, routed_to))
        print(f"  {log_id}: [{source_name}] {entry.get('title', '')} -> routed: {', '.join(routed_to) or 'none (informational only)'}")

    save_json(REGULATORY_LOG_PATH, regulatory_log)
    save_json(CONTENT_QUEUE_PATH, content_queue)
    save_json(PRODUCT_BACKLOG_PATH, product_backlog)
    save_json(CEO_FEED_PATH, ceo_feed)

    if inbox_batch:
        inbox_path = OPPORTUNITY_INBOX_DIR / f"{TODAY}-market-intelligence.json"
        existing = load_json(inbox_path, []) if inbox_path.exists() else []
        save_json(inbox_path, existing + inbox_batch)

    OUTPUT_DIR.mkdir(exist_ok=True)
    report_lines = [
        "# Market Intelligence — Daily Report", "", f"**Date:** {TODAY}",
        f"**New developments:** {len(run_summary)}", "",
        "| Source | Title | Consulting | LinkedIn | Website | Product | ADGL | OPERA |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for source_name, title, checks, _ in run_summary:
        report_lines.append(
            f"| {source_name} | {title} | {checks['consultingOpportunity']} | {checks['linkedinContent']} | "
            f"{checks['websiteUpdate']} | {checks['newProduct']} | {checks['affectsADGL']} | {checks['affectsOPERA']} |"
        )
    (OUTPUT_DIR / f"{TODAY}-market-intelligence-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n{len(run_summary)} developments logged. Report: "
          f"{(OUTPUT_DIR / f'{TODAY}-market-intelligence-report.md').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
