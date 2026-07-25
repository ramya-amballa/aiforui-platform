#!/usr/bin/env python3
"""
Content Director — Draft Generation Engine (Runtime v1.0)

Usage:
    python3 generate.py

Reads four already-classified signal sources (never re-classifying any
of them — see ../content-generation-model.md):
  - 02-Content-Director/content-brief-queue.json (Market Intelligence's
    linkedinContent/websiteUpdate/affectsADGL/affectsOPERA triggers)
  - opportunity-hunter/opportunity-schema.json, filtered to
    classification == "Convert into Content" (Opportunity Hunter's own
    existing decision tree)
  - 03-Product-Manager/shipped-products-log.json (Product Manager's own
    "shipped" record)
  - executive-dashboard/executive-dashboard.md's "## Today's
    Priorities" section (CEO Advisor's own decision model, already
    executed there)

For every new signal, determines seven booleans by reusing whichever
upstream answer already exists (never re-deriving one), assembles
publish-ready drafts for up to four real formats (LinkedIn post,
newsletter article, website insight, product announcement) from
../../sales-director/runtime/config/practitioner-bank.json's real
practitioner-experience bullets and product catalogue — never
inventing a claim, a credential, or a result — and reports one of
three statuses per signal to output/ceo-advisor-feed.json: `Ready to
Publish`, `Needs Review`, or `Low Value`.

This script never publishes anything and never writes to any file
outside content-director/ except one lifecycle field it's meant to
own: it flips a consumed content-brief-queue.json entry's own `status`
from "queued" to "briefed" once a draft exists for it — the same
field Market Intelligence already defined for exactly this handoff,
not a new one. Every other input above is read-only.
"""

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
CONTENT_DIRECTOR_DIR = RUNTIME_DIR.parent
AOS_DIR = CONTENT_DIRECTOR_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONTENT_BRIEF_QUEUE_PATH = AOS_DIR / "02-Content-Director" / "content-brief-queue.json"
OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "opportunity-hunter" / "opportunity-schema.json"
SHIPPED_PRODUCTS_PATH = AOS_DIR / "03-Product-Manager" / "shipped-products-log.json"
EXECUTIVE_DASHBOARD_PATH = AOS_DIR / "executive-dashboard" / "executive-dashboard.md"
PRACTITIONER_BANK_PATH = AOS_DIR / "sales-director" / "runtime" / "config" / "practitioner-bank.json"
MARKET_INTELLIGENCE_SOURCES_PATH = AOS_DIR / "05-Market-Intelligence" / "runtime" / "config" / "sources.json"

TEMPLATES_DIR = RUNTIME_DIR / "templates"
QUEUE_DIR = RUNTIME_DIR / "queue"
CONTENT_QUEUE_LOG_PATH = QUEUE_DIR / "content-queue.json"
PROCESSED_INDEX_PATH = QUEUE_DIR / "processed-index.json"
OUTPUT_DIR = RUNTIME_DIR / "output"
DRAFTS_DIR = OUTPUT_DIR / "drafts"
CEO_FEED_PATH = OUTPUT_DIR / "ceo-advisor-feed.json"
LOGS_DIR = RUNTIME_DIR / "logs"

TODAY = date.today().isoformat()
RUN_STARTED = datetime.now(timezone.utc)

HASHTAG_MAP = {
    "AI Governance": "#AIGovernance", "ADGL": "#ADGL", "AI Deployment Governance": "#AIDeploymentGovernance",
    "GRC": "#GRC", "Technology Risk": "#TechnologyRisk", "Third-Party Risk": "#ThirdPartyRisk",
    "Security Governance": "#SecurityGovernance", "DORA": "#DORA", "EU AI Act": "#EUAIAct",
    "Fractional Advisory": "#FractionalAdvisory", "Government/FedRAMP-GovRAMP-CMMC": "#GovTech",
}

HERO_IMAGE_BY_SIGNAL_TYPE = {
    "regulatory": "A structured governance/framework diagram or blueprint-style graphic — no generic AI robot or brain imagery.",
    "product": "A screenshot or clean diagram of the resource itself.",
    "opportunity": "A founder portrait or the AI for U&I brand mark/wordmark.",
    "priority": "The AI for U&I brand mark/wordmark.",
}

CTA_BY_FORMAT = {
    "linkedin": "Comment with how your organisation is handling this, or send a direct message to discuss specifics.",
    "newsletter": "Subscribe to the AI for U&I newsletter for the full breakdown, or forward this to whoever owns AI governance at your organisation.",
    "website": "Download the related resource, or book a scoping call to discuss your organisation's specific exposure.",
    "product": "View the resource, or book a scoping call to see how it applies to your organisation.",
}

OBJECTIVE_BY_SIGNAL_TYPE = {
    "regulatory": "Generate consulting leads",
    "product": "Sell products",
    "opportunity": "Build authority",
    "priority": "Build authority",
}

SOURCE_STRENGTH = {"product": 9, "regulatory": 7, "opportunity": 6, "priority": 5}

DEFAULT_PROCESSED_INDEX = {
    "schema": {
        "processedOpportunities": "array of opportunity-hunter ids already drafted",
        "processedProducts": "array of shipped-products-log ids already drafted",
        "processedPriorities": "array of ceo-priority-{date} ids already drafted",
    },
    "processedOpportunities": [],
    "processedProducts": [],
    "processedPriorities": [],
}

DEFAULT_CONTENT_QUEUE_LOG = {
    "schema": {
        "id": "string — the candidate's naturalId",
        "dateQueued": "string — ISO 8601 date",
        "sourceType": "string — regulatory, opportunity, product, or priority",
        "title": "string",
        "determinations": "object — the seven booleans",
        "grounding": "number — 0 or 10, see content-generation-model.md",
        "score": "number — 0-100",
        "status": "string — Ready to Publish, Needs Review, or Low Value",
        "draftPaths": "array of strings",
    },
    "queue": [],
}

DEFAULT_CEO_FEED = {
    "schema": {
        "id": "string", "title": "string", "sourceType": "string",
        "status": "string — Ready to Publish, Needs Review, or Low Value — the only field 09-CEO-Advisor reads",
        "score": "number — 0-100", "draftPaths": "array of strings",
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


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


def load_source_domain_tags():
    """Reads Market Intelligence's own source->domainTags mapping
    (data, not logic) since content-brief-queue.json entries don't
    carry domainTags themselves — without this, every regulatory
    signal would have no domain to match against the content bank and
    would be forced Low Value regardless of real relevance."""
    config = load_json(MARKET_INTELLIGENCE_SOURCES_PATH, {"sources": []})
    return {source["name"]: source.get("domainTags", ["AI Governance"]) for source in config.get("sources", [])}


# --------------------------------------------------------------------------
# Signal collection — one function per source, each read-only
# --------------------------------------------------------------------------

def collect_regulatory_candidates(content_queue, source_domain_tags):
    candidates = []
    for item in content_queue.get("queue", []):
        if item.get("status") != "queued":
            continue
        triggered_by = item.get("triggeredBy", [])
        candidates.append({
            "sourceType": "regulatory",
            "naturalId": item["id"],
            "title": item["source"] + ": " + item.get("developmentSummary", ""),
            "summary": item.get("developmentSummary", ""),
            "url": item.get("url"),
            "domainTags": source_domain_tags.get(item["source"], ["AI Governance"]),
            "linkedin": "linkedinContent" in triggered_by,
            "newsletter": "linkedinContent" in triggered_by,
            "website": "websiteUpdate" in triggered_by,
            "github": False,
            "adgl": bool(item.get("affectsADGL")),
            "opera": bool(item.get("affectsOPERA")),
            "productAnnouncement": False,
            "sourceLabel": f"Market Intelligence ({item['source']})",
            "briefQueueItem": item,
        })
    return candidates


def collect_opportunity_candidates(opportunity_schema, processed_index):
    candidates = []
    for opp in opportunity_schema.get("opportunities", []):
        if opp.get("classification") != "Convert into Content":
            continue
        if opp["id"] in processed_index["processedOpportunities"]:
            continue
        domain_tags = opp.get("domainTags", [])
        candidates.append({
            "sourceType": "opportunity",
            "naturalId": opp["id"],
            "title": opp["title"],
            "summary": opp.get("description", ""),
            "url": opp.get("url"),
            "domainTags": domain_tags,
            "linkedin": True, "newsletter": True, "website": False, "github": False,
            "adgl": "ADGL" in domain_tags, "opera": True, "productAnnouncement": False,
            "sourceLabel": f"Opportunity Hunter (recurring theme: {opp['organisation']})",
        })
    return candidates


def collect_product_candidates(shipped_products, processed_index):
    candidates = []
    for prod in shipped_products.get("shippedProducts", []):
        if prod["id"] in processed_index["processedProducts"]:
            continue
        is_adgl = "adgl" in prod["title"].lower()
        # Inferred from the product's own real title, same as the adgl
        # boolean below — without this, a shipped product would have
        # nothing to match against the content bank and would be
        # forced Low Value regardless of how concrete it is.
        domain_tags = ["ADGL", "AI Deployment Governance"] if is_adgl else ["AI Governance"]
        candidates.append({
            "sourceType": "product",
            "naturalId": prod["id"],
            "title": prod["title"],
            "summary": prod.get("originSignal", ""),
            "url": None,
            "domainTags": domain_tags,
            "linkedin": True, "newsletter": True, "website": True, "github": True,
            "adgl": is_adgl, "opera": True, "productAnnouncement": True,
            "sourceLabel": f"Product Manager (shipped {prod.get('dateShipped', '')})",
            "productFormat": prod.get("format", ""),
        })
    return candidates


def collect_priority_candidate(processed_index):
    priority_id = f"ceo-priority-{TODAY}"
    if priority_id in processed_index["processedPriorities"]:
        return []
    if not EXECUTIVE_DASHBOARD_PATH.exists():
        return []
    text = EXECUTIVE_DASHBOARD_PATH.read_text(encoding="utf-8")
    if "## Today's Priorities" not in text:
        return []
    section = text.split("## Today's Priorities", 1)[1].split("## Opportunity Hunter", 1)[0]
    match = re.search(r"\*\*Highest-value action:\*\*\s*(.+)", section)
    if not match:
        return []
    reason_match = re.search(r"\*\*Reason:\*\*\s*(.+)", section)
    return [{
        "sourceType": "priority",
        "naturalId": priority_id,
        "title": match.group(1).strip(),
        "summary": reason_match.group(1).strip() if reason_match else "",
        "url": None,
        "domainTags": ["AI Governance"],
        "linkedin": True, "newsletter": False, "website": False, "github": False,
        "adgl": False, "opera": True, "productAnnouncement": False,
        "sourceLabel": "CEO Advisor (today's highest-value action)",
    }]


# --------------------------------------------------------------------------
# Content bank grounding — practitioner-bank.json, read-only
# --------------------------------------------------------------------------

def match_practitioner_bullet(candidate, bank):
    domain_set = set(candidate["domainTags"])
    if not domain_set:
        return None
    for item in bank.get("practitionerExperience", []):
        if domain_set & set(item.get("domainTags", [])):
            return item
    return None


def match_product(candidate, bank):
    products = bank.get("products", [])
    title_lower = candidate["title"].lower()
    for product in products:
        if product["title"].lower() in title_lower or title_lower in product["title"].lower():
            return product
    domain_set = set(candidate["domainTags"])
    if domain_set:
        for product in products:
            if domain_set & set(product.get("domainTags", [])):
                return product
    return None


# --------------------------------------------------------------------------
# Scoring and status — content-generation-model.md
# --------------------------------------------------------------------------

def compute_score(candidate, grounding):
    flags = [candidate["linkedin"], candidate["newsletter"], candidate["website"],
              candidate["github"], candidate["adgl"], candidate["opera"], candidate["productAnnouncement"]]
    flag_breadth = min(10, 2 * sum(flags))
    source_strength = SOURCE_STRENGTH[candidate["sourceType"]]
    weighted = (flag_breadth * 0.35) + (grounding * 0.35) + (source_strength * 0.30)
    return round(weighted * 10)


def determine_status(candidate, grounding, score):
    if grounding == 0 or score < 40:
        return "Low Value"
    if candidate["sourceType"] == "priority":
        return "Needs Review"
    if score >= 70:
        return "Ready to Publish"
    return "Needs Review"


# --------------------------------------------------------------------------
# Draft assembly
# --------------------------------------------------------------------------

def hook_line(candidate):
    if candidate["sourceType"] == "regulatory":
        return f"{candidate['title'].rstrip('.')}."
    if candidate["sourceType"] == "opportunity":
        return f"We keep seeing the same question from prospective clients: {candidate['title']}."
    if candidate["sourceType"] == "product":
        return f"AI for U&I has shipped a new resource: {candidate['title']}."
    return f"Today's focus at AI for U&I: {candidate['title']}."


def also_relevant_to(candidate):
    parts = []
    if candidate["adgl"]:
        parts.append("ADGL methodology")
    if candidate["opera"]:
        parts.append("OPERA methodology")
    if candidate["github"]:
        parts.append("GitHub resources update")
    return ", ".join(parts) if parts else "None"


def hashtags_for(candidate):
    tags = ["#AIforUandI"]
    for domain_tag in candidate["domainTags"]:
        tag = HASHTAG_MAP.get(domain_tag)
        if tag and tag not in tags:
            tags.append(tag)
    return " ".join(tags)


def build_tokens(candidate, bullet, product, status, fmt):
    objective = {
        "linkedin": OBJECTIVE_BY_SIGNAL_TYPE[candidate["sourceType"]],
        "newsletter": "Increase newsletter subscribers",
        "website": "Support website SEO",
        "product": "Sell products",
    }[fmt]
    practitioner_grounding = bullet["text"] if bullet else ""
    product_reference = f"**Related resource:** {product['title']} — {product['description']}" if product else ""
    return {
        "SOURCE_DESCRIPTION": candidate["sourceLabel"],
        "DATE": TODAY,
        "STATUS": status,
        "OBJECTIVE": objective,
        "ALSO_RELEVANT_TO": also_relevant_to(candidate),
        "HEADLINE": candidate["title"],
        "HOOK_LINE": hook_line(candidate),
        "BODY_PARAGRAPH": candidate["summary"] or candidate["title"],
        "PRACTITIONER_GROUNDING": practitioner_grounding,
        "PRODUCT_REFERENCE": product_reference,
        "CTA_LINE": CTA_BY_FORMAT[fmt],
        "HASHTAGS": hashtags_for(candidate),
        "HERO_IMAGE": HERO_IMAGE_BY_SIGNAL_TYPE[candidate["sourceType"]],
    }


def render_template(template_text, tokens):
    result = template_text
    for key, value in tokens.items():
        result = result.replace("{{" + key + "}}", value)
    return result


TEMPLATE_FILES = {
    "linkedin": "linkedin-post.md",
    "newsletter": "newsletter-article.md",
    "website": "website-insight.md",
    "product": "product-announcement.md",
}


def generate_drafts(candidate, bullet, product, status):
    slug = slugify(f"{candidate['naturalId']}-{candidate['title']}")
    draft_paths = []
    for fmt, flag_key in (("linkedin", "linkedin"), ("newsletter", "newsletter"),
                           ("website", "website"), ("product", "productAnnouncement")):
        if not candidate[flag_key]:
            continue
        template_text = (TEMPLATES_DIR / TEMPLATE_FILES[fmt]).read_text(encoding="utf-8")
        tokens = build_tokens(candidate, bullet, product, status, fmt)
        rendered = render_template(template_text, tokens)
        draft_path = DRAFTS_DIR / f"{slug}-{fmt}.md"
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(rendered, encoding="utf-8")
        draft_paths.append(str(draft_path.relative_to(REPO_ROOT)))
    return draft_paths


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{TODAY}-{RUN_STARTED.strftime('%H%M%S')}-content-director.log"
    log_lines = [f"Content Director Runtime v1.0 — run started {RUN_STARTED.isoformat()}"]

    def log(msg):
        print(msg)
        log_lines.append(msg)

    content_queue = load_json(CONTENT_BRIEF_QUEUE_PATH, {"queue": []})
    opportunity_schema = load_json(OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    shipped_products = load_json(SHIPPED_PRODUCTS_PATH, {"shippedProducts": []})
    practitioner_bank = load_json(PRACTITIONER_BANK_PATH, {"practitionerExperience": [], "products": []})
    processed_index = load_json(PROCESSED_INDEX_PATH, DEFAULT_PROCESSED_INDEX)
    for key in ("processedOpportunities", "processedProducts", "processedPriorities"):
        processed_index.setdefault(key, [])

    source_domain_tags = load_source_domain_tags()
    candidates = (
        collect_regulatory_candidates(content_queue, source_domain_tags)
        + collect_opportunity_candidates(opportunity_schema, processed_index)
        + collect_product_candidates(shipped_products, processed_index)
        + collect_priority_candidate(processed_index)
    )

    if not candidates:
        log("No new signals from any source. Nothing to do.")
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        return 0

    ceo_feed = load_json(CEO_FEED_PATH, DEFAULT_CEO_FEED)
    ceo_feed.setdefault("feed", [])
    content_queue_log = load_json(CONTENT_QUEUE_LOG_PATH, DEFAULT_CONTENT_QUEUE_LOG)
    content_queue_log.setdefault("queue", [])

    processed_count = 0
    for candidate in candidates:
        bullet = match_practitioner_bullet(candidate, practitioner_bank)
        product = match_product(candidate, practitioner_bank)
        grounding = 10 if (bullet or product) else 0
        score = compute_score(candidate, grounding)
        status = determine_status(candidate, grounding, score)

        draft_paths = generate_drafts(candidate, bullet, product, status)

        ceo_feed["feed"].append({
            "id": candidate["naturalId"], "title": candidate["title"], "sourceType": candidate["sourceType"],
            "status": status, "score": score, "draftPaths": draft_paths,
        })
        content_queue_log["queue"].append({
            "id": candidate["naturalId"], "dateQueued": TODAY, "sourceType": candidate["sourceType"],
            "title": candidate["title"],
            "determinations": {k: candidate[k] for k in
                                ("linkedin", "newsletter", "website", "github", "adgl", "opera", "productAnnouncement")},
            "grounding": grounding, "score": score, "status": status, "draftPaths": draft_paths,
        })

        if candidate["sourceType"] == "regulatory":
            candidate["briefQueueItem"]["status"] = "briefed"
        elif candidate["sourceType"] == "opportunity":
            processed_index["processedOpportunities"].append(candidate["naturalId"])
        elif candidate["sourceType"] == "product":
            processed_index["processedProducts"].append(candidate["naturalId"])
        elif candidate["sourceType"] == "priority":
            processed_index["processedPriorities"].append(candidate["naturalId"])

        processed_count += 1
        log(f"  {candidate['naturalId']}: [{candidate['sourceType']}] {candidate['title'][:60]} "
            f"-> score {score}/100 -> {status} ({len(draft_paths)} draft(s))")

    save_json(CONTENT_BRIEF_QUEUE_PATH, content_queue)
    save_json(PROCESSED_INDEX_PATH, processed_index)
    save_json(CEO_FEED_PATH, ceo_feed)
    save_json(CONTENT_QUEUE_LOG_PATH, content_queue_log)

    OUTPUT_DIR.mkdir(exist_ok=True)
    report_lines = [
        "# Content Director — Daily Report", "", f"**Date:** {TODAY}",
        f"**Signals processed:** {processed_count}", "",
        "| Signal | Type | Score | Status | Drafts |", "|---|---|---|---|---|",
    ]
    for entry in ceo_feed["feed"][-processed_count:]:
        report_lines.append(f"| {entry['title'][:60]} | {entry['sourceType']} | {entry['score']} | "
                             f"{entry['status']} | {len(entry['draftPaths'])} |")
    report_path = OUTPUT_DIR / f"{TODAY}-content-director-report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    log(f"\n{processed_count} signals processed. Report: {report_path.relative_to(REPO_ROOT)}")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
