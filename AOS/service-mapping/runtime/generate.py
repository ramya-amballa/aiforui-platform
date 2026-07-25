#!/usr/bin/env python3
"""
Service Mapping Engine — execution mode

Usage:
    python3 generate.py

Reads every opportunity in ../../opportunity-hunter/opportunity-schema.json
(read-only) and, for every one not already mapped, deterministically
computes: Primary Service, Secondary Services, Recommended Engagement
Type, Estimated Project Size, Recommended Proposal Template, and
Cross-Sell Opportunities. Every rule is a lookup against
config/service-catalogue.json — no randomness, no LLM call, no
external service; the same opportunity always produces the same
recommendation.

Also reads, read-only, two files it never writes to:
  - 08-Revenue-Hunter/pipeline.json — a real expectedRevenue figure,
    when one already exists, is the only thing allowed to override the
    Primary-Service-implied default project size
  - 06-CRM/company-intelligence.json — an existingRelationship of
    "active client" is the only signal that overrides the engagement
    type to Retainer

Never re-scores, re-classifies, or re-routes an opportunity — those
stay Opportunity Hunter's (ingest.py) job alone, exactly as before this
engine existed. Never touches Revenue Hunter's pipeline.json or CRM's
company-intelligence.json.

Writes:
  - ../service-recommendations.json — one entry per opportunity,
    the persisted record Sales Director reads (read-only) to surface
    the recommended template/engagement type in its own packages
  - output/{date}-service-recommendation-report.md (dated) and
    output/service-recommendation-report.md (stable) — every newly
    mapped opportunity, plus summary counts
  - logs/{date}-{time}-service-mapping.log

Idempotent: processed-index.json records every opportunity id already
mapped, so a re-run only maps opportunities new since the last run —
the same convention every other AOS runtime already follows.
"""

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
SERVICE_MAPPING_DIR = RUNTIME_DIR.parent
AOS_DIR = SERVICE_MAPPING_DIR.parent
REPO_ROOT = AOS_DIR.parent

OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "opportunity-hunter" / "opportunity-schema.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"

CONFIG_DIR = RUNTIME_DIR / "config"
OUTPUT_DIR = RUNTIME_DIR / "output"
LOGS_DIR = RUNTIME_DIR / "logs"
PROCESSED_INDEX_PATH = RUNTIME_DIR / "processed-index.json"
RECOMMENDATIONS_PATH = SERVICE_MAPPING_DIR / "service-recommendations.json"

TODAY = date.today()
RUN_STARTED = datetime.now(timezone.utc)

DEFAULT_PROCESSED_INDEX = {
    "schema": {"opportunityId": "string — already mapped, this run and every prior run skips it"},
    "processed": {},
}

DEFAULT_RECOMMENDATIONS = {
    "schema": {
        "opportunityId": "string — matches opportunity-hunter/opportunity-schema.json's id",
        "title": "string", "organisation": "string",
        "dateMapped": "string — ISO 8601 date",
        "notApplicable": "boolean — true for Ignore/Convert into Content/Convert into Product Idea; every field below is null when true",
        "notApplicableReason": "string or null",
        "primaryService": "string or null — one of service-catalogue.json's primaryServices",
        "primaryServiceReason": "string or null — which rule matched, for transparency",
        "secondaryServices": "array of strings — natural follow-on services, ordered",
        "recommendedEngagementType": "string or null — one of service-catalogue.json's engagementTypes",
        "estimatedProjectSize": "string or null — Small, Medium, Large, or Enterprise",
        "projectSizeBasis": "string or null — 'pipeline-revenue' (a real expectedRevenue figure) or 'heuristic-estimate' (Primary-Service default adjusted by the 0-10 expectedRevenue score) — never fabricated, always labelled",
        "recommendedProposalTemplate": "string or null — a real filename in templates/proposals/",
        "crossSellOpportunities": "array of strings",
    },
    "recommendations": {},
}


def load_json(path, default=None):
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# --------------------------------------------------------------------------
# Currency parsing — reused verbatim from executive-dashboard/runtime/
# generate.py (also reused by revenue-hunter/ and crm/), so a figure in
# pipeline.json parses the same way everywhere it's read in AOS.
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
    return sum(parsed) / len(parsed), currency


def _matches(text, keyword):
    """Word-boundary, case-insensitive, plural-tolerant — same convention
    used across AOS (market-intelligence/runtime/monitor.py, etc.)."""
    pattern = r"\b" + re.escape(keyword.lower()) + r"s?\b"
    return re.search(pattern, (text or "").lower()) is not None


def any_keyword_matches(text, keywords):
    return any(_matches(text, kw) for kw in keywords)


# --------------------------------------------------------------------------
# 1. Primary Service — first matching rule wins (see service-mapping-model.md)
# --------------------------------------------------------------------------

def determine_primary_service(opportunity, catalogue):
    text = f"{opportunity.get('title', '')} {opportunity.get('description', '')}"
    domain_tags = set(opportunity.get("domainTags", []))
    scoped = bool(opportunity.get("scopedEngagement"))

    if any_keyword_matches(text, catalogue["fractionalKeywords"]) or "Fractional Advisory" in domain_tags:
        return "Fractional AI Governance Lead", "fractional keyword or Fractional Advisory domainTag"

    if domain_tags & {"ADGL", "AI Deployment Governance"}:
        return "AI Deployment Governance (ADGL)", "ADGL/AI Deployment Governance domainTag"

    if "Third-Party Risk" in domain_tags:
        return "AI Third-Party Risk Review", "Third-Party Risk domainTag"

    if domain_tags & {"DORA", "EU AI Act", "Government/FedRAMP-GovRAMP-CMMC"}:
        if scoped:
            return "AI Policy & Control Framework", "regulatory domainTag (DORA/EU AI Act/Government), scoped"
        return "AI Readiness Assessment", "regulatory domainTag (DORA/EU AI Act/Government), unscoped"

    if "GRC" in domain_tags:
        return "AI Governance Operating Model", "GRC domainTag"

    if domain_tags & {"Security Governance", "Technology Risk"}:
        return "AI Risk Assessment", "Security Governance/Technology Risk domainTag"

    if "AI Governance" in domain_tags:
        if scoped:
            return "Responsible AI Implementation", "AI Governance domainTag, scoped"
        return "AI Governance Advisory", "AI Governance domainTag, unscoped"

    if opportunity.get("sourceCategory") == "Consulting Channel":
        return "AI Governance Advisory", "Consulting Channel source, no more specific domainTag"

    if any_keyword_matches(text, catalogue["workshopKeywords"] + catalogue["trainingKeywords"]):
        return "Executive Workshop", "workshop/training keyword"

    return "AI Readiness Assessment", "no more specific signal — conservative default"


# --------------------------------------------------------------------------
# 2. Secondary Services — fixed chain per Primary Service
# --------------------------------------------------------------------------

def determine_secondary_services(primary_service, catalogue):
    return list(catalogue["secondaryServiceChains"].get(primary_service, []))


# --------------------------------------------------------------------------
# 3. Recommended Engagement Type
# --------------------------------------------------------------------------

def determine_engagement_type(opportunity, primary_service, crm_entry, catalogue):
    text = f"{opportunity.get('title', '')} {opportunity.get('description', '')}"

    if crm_entry and crm_entry.get("existingRelationship") == "active client":
        return "Retainer", "active client relationship in CRM"

    if primary_service == "Fractional AI Governance Lead":
        return "Fractional consulting", "Primary Service is Fractional AI Governance Lead"

    if primary_service == "Executive Workshop":
        if any_keyword_matches(text, catalogue["trainingKeywords"]):
            return "Training", "Executive Workshop primary service, training-specific keyword"
        return "Discovery workshop", "Executive Workshop primary service"

    if primary_service == "AI Readiness Assessment":
        return "Discovery workshop", "Primary Service is AI Readiness Assessment"

    if opportunity.get("scopedEngagement"):
        return "Fixed-price project", "scopedEngagement is true"

    if opportunity.get("classification") == "Relationship Building":
        return "Advisory engagement", "classification is Relationship Building"

    return "Advisory engagement", "default — unscoped, no more specific signal"


# --------------------------------------------------------------------------
# 4. Estimated Project Size
# --------------------------------------------------------------------------

def _band_from_amount(amount, thresholds):
    if amount <= thresholds["small_max"]:
        return "Small"
    if amount <= thresholds["medium_max"]:
        return "Medium"
    if amount <= thresholds["large_max"]:
        return "Large"
    return "Enterprise"


def determine_project_size(opportunity, primary_service, pipeline_entry, catalogue):
    if pipeline_entry:
        amount, _currency = parse_currency(pipeline_entry.get("expectedRevenue"))
        if amount is not None:
            return _band_from_amount(amount, catalogue["projectSizeRevenueThresholds"]), "pipeline-revenue"

    bands = catalogue["projectSizeBands"]
    default_band = catalogue["projectSizeDefaultByPrimaryService"].get(primary_service, "Medium")
    index = bands.index(default_band)

    revenue_score = opportunity.get("scores", {}).get("expectedRevenue", 5)
    if revenue_score >= 8:
        index = min(index + 1, len(bands) - 1)
    elif revenue_score <= 2:
        index = max(index - 1, 0)

    return bands[index], "heuristic-estimate"


# --------------------------------------------------------------------------
# 5. Recommended Proposal Template
# --------------------------------------------------------------------------

def determine_proposal_template(opportunity, primary_service, catalogue):
    domain_tags = opportunity.get("domainTags", [])
    for tag in domain_tags:
        if tag in catalogue["proposalTemplateByDomainTag"]:
            return catalogue["proposalTemplateByDomainTag"][tag]
    return catalogue["proposalTemplateByPrimaryService"].get(primary_service, "enterprise-consulting-proposal-template.md")


# --------------------------------------------------------------------------
# 6. Cross-Sell Opportunities
# --------------------------------------------------------------------------

def determine_cross_sell(opportunity, primary_service, bank_products, catalogue):
    cross_sell = []
    complement = catalogue["crossSellComplement"].get(primary_service)
    if complement:
        cross_sell.append(complement)

    domain_set = set(opportunity.get("domainTags", []))
    matched_products = [p["title"] for p in bank_products if domain_set & set(p.get("domainTags", []))]
    cross_sell.extend(matched_products[:2])
    return cross_sell


# --------------------------------------------------------------------------
# Per-opportunity recommendation
# --------------------------------------------------------------------------

def map_opportunity(opportunity, pipeline_entry, crm_entry, bank_products, catalogue):
    primary_service, reason = determine_primary_service(opportunity, catalogue)
    engagement_type, _engagement_reason = determine_engagement_type(opportunity, primary_service, crm_entry, catalogue)
    project_size, size_basis = determine_project_size(opportunity, primary_service, pipeline_entry, catalogue)

    return {
        "opportunityId": opportunity["id"],
        "title": opportunity["title"],
        "organisation": opportunity["organisation"],
        "dateMapped": TODAY.isoformat(),
        "notApplicable": False,
        "notApplicableReason": None,
        "primaryService": primary_service,
        "primaryServiceReason": reason,
        "secondaryServices": determine_secondary_services(primary_service, catalogue),
        "recommendedEngagementType": engagement_type,
        "estimatedProjectSize": project_size,
        "projectSizeBasis": size_basis,
        "recommendedProposalTemplate": determine_proposal_template(opportunity, primary_service, catalogue),
        "crossSellOpportunities": determine_cross_sell(opportunity, primary_service, bank_products, catalogue),
    }


def not_applicable_entry(opportunity, reason):
    return {
        "opportunityId": opportunity["id"],
        "title": opportunity["title"],
        "organisation": opportunity["organisation"],
        "dateMapped": TODAY.isoformat(),
        "notApplicable": True,
        "notApplicableReason": reason,
        "primaryService": None, "primaryServiceReason": None,
        "secondaryServices": [], "recommendedEngagementType": None,
        "estimatedProjectSize": None, "projectSizeBasis": None,
        "recommendedProposalTemplate": None, "crossSellOpportunities": [],
    }


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def render_report(new_entries):
    mapped = [e for e in new_entries if not e["notApplicable"]]
    skipped = [e for e in new_entries if e["notApplicable"]]

    lines = [
        "# Service Recommendation Report",
        "",
        f"**Date:** {TODAY.isoformat()}",
        f"**Opportunities mapped this run:** {len(mapped)}",
        f"**Not applicable this run:** {len(skipped)}",
        "",
        "## Recommendations",
        "",
    ]
    if mapped:
        lines.append("| Title | Organisation | Primary Service | Engagement Type | Size | Template | Secondary Services |")
        lines.append("|---|---|---|---|---|---|---|")
        for e in mapped:
            secondary = "; ".join(e["secondaryServices"])
            lines.append(f"| {e['title']} | {e['organisation']} | {e['primaryService']} | "
                          f"{e['recommendedEngagementType']} | {e['estimatedProjectSize']} "
                          f"({e['projectSizeBasis']}) | {e['recommendedProposalTemplate']} | {secondary} |")
    else:
        lines.append("_No new opportunities mapped this run._")

    lines += ["", "## Cross-Sell Opportunities", ""]
    for e in mapped:
        if e["crossSellOpportunities"]:
            lines.append(f"- **{e['title']}** ({e['organisation']}): " + "; ".join(e["crossSellOpportunities"]))
    if not any(e["crossSellOpportunities"] for e in mapped):
        lines.append("_None this run._")

    if skipped:
        lines += ["", "## Not Applicable", ""]
        for e in skipped:
            lines.append(f"- **{e['title']}** ({e['organisation']}) — {e['notApplicableReason']}")

    if mapped:
        lines += ["", "## Summary", ""]
        by_primary = {}
        by_type = {}
        by_size = {}
        for e in mapped:
            by_primary[e["primaryService"]] = by_primary.get(e["primaryService"], 0) + 1
            by_type[e["recommendedEngagementType"]] = by_type.get(e["recommendedEngagementType"], 0) + 1
            by_size[e["estimatedProjectSize"]] = by_size.get(e["estimatedProjectSize"], 0) + 1
        lines.append("**By Primary Service:** " + ", ".join(f"{k} ({v})" for k, v in sorted(by_primary.items())))
        lines.append("")
        lines.append("**By Engagement Type:** " + ", ".join(f"{k} ({v})" for k, v in sorted(by_type.items())))
        lines.append("")
        lines.append("**By Project Size:** " + ", ".join(f"{k} ({v})" for k, v in sorted(by_size.items())))

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    LOGS_DIR.mkdir(exist_ok=True)
    log_path = LOGS_DIR / f"{TODAY.isoformat()}-{RUN_STARTED.strftime('%H%M%S')}-service-mapping.log"
    log_lines = [f"Service Mapping Engine — run started {RUN_STARTED.isoformat()}"]

    try:
        schema_data = load_json(OPPORTUNITY_SCHEMA_PATH)
    except FileNotFoundError as exc:
        print(f"Cannot find opportunity-schema.json: {exc}", file=sys.stderr)
        return 1

    pipeline_data = load_json(PIPELINE_PATH, {"pipeline": []})
    crm_data = load_json(CRM_PATH, {"companies": []})
    catalogue = load_json(CONFIG_DIR / "service-catalogue.json")
    bank = load_json(AOS_DIR / "sales-director" / "runtime" / "config" / "practitioner-bank.json", {"products": []})

    processed_index = load_json(PROCESSED_INDEX_PATH, DEFAULT_PROCESSED_INDEX)
    processed_index.setdefault("processed", {})
    recommendations = load_json(RECOMMENDATIONS_PATH, DEFAULT_RECOMMENDATIONS)
    recommendations.setdefault("recommendations", {})

    pipeline_by_ref = {e["sourceRef"]: e for e in pipeline_data.get("pipeline", []) if e.get("sourceRef")}
    crm_by_org = {c["companyName"]: c for c in crm_data.get("companies", [])}

    candidates = [
        o for o in schema_data["opportunities"]
        if o["id"] not in processed_index["processed"]
    ]

    if not candidates:
        print("No new opportunities to map. Nothing to do.")
        log_lines.append("No new opportunities to map.")
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        return 0

    new_entries = []
    for opportunity in candidates:
        classification = opportunity.get("classification")
        if classification in catalogue["excludedClassifications"]:
            entry = not_applicable_entry(opportunity, catalogue["excludedClassifications"][classification])
        else:
            pipeline_entry = pipeline_by_ref.get(opportunity["id"])
            crm_entry = crm_by_org.get(opportunity["organisation"])
            entry = map_opportunity(opportunity, pipeline_entry, crm_entry, bank.get("products", []), catalogue)

        recommendations["recommendations"][opportunity["id"]] = entry
        processed_index["processed"][opportunity["id"]] = {"dateMapped": TODAY.isoformat()}
        new_entries.append(entry)

        if entry["notApplicable"]:
            line = f"  {opportunity['id']}: {opportunity['title']} -> not applicable ({entry['notApplicableReason']})"
        else:
            line = (f"  {opportunity['id']}: {opportunity['title']} -> {entry['primaryService']} / "
                    f"{entry['recommendedEngagementType']} / {entry['estimatedProjectSize']}")
        print(line)
        log_lines.append(line)

    save_json(RECOMMENDATIONS_PATH, recommendations)
    save_json(PROCESSED_INDEX_PATH, processed_index)

    OUTPUT_DIR.mkdir(exist_ok=True)
    report = render_report(new_entries)
    (OUTPUT_DIR / f"{TODAY.isoformat()}-service-recommendation-report.md").write_text(report, encoding="utf-8")
    (OUTPUT_DIR / "service-recommendation-report.md").write_text(report, encoding="utf-8")

    mapped_count = sum(1 for e in new_entries if not e["notApplicable"])
    summary = f"\n{mapped_count} opportunities mapped, {len(new_entries) - mapped_count} not applicable."
    print(summary)
    log_lines.append(summary)
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
