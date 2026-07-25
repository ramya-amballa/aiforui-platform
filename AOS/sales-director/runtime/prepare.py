#!/usr/bin/env python3
"""
Sales Director — Proposal Preparation Engine (execution mode)

Usage:
    python3 prepare.py

Reads every opportunity in ../../opportunity-hunter/opportunity-schema.json
classified Immediate Proposal, Apply, Partnership or Follow Recruiter,
and — for any not already prepared — writes a full package to
output/packages/: cover letter, proposal, recruiter outreach, client
outreach, clarifying questions, recommended pricing and a proposal
confidence score. The model behind pricing and confidence is documented
in ../proposal-preparation-engine.md; read that first if a number here
looks wrong.

Every opportunity is enriched (never re-scored) from two files it may
already appear in: ../../08-Revenue-Hunter/pipeline.json (a real
revenue estimate, where Revenue Hunter or the founder already entered
one) and ../../06-CRM/company-intelligence.json (relationship context —
tailored positioning, outreach history, a named recruiter).

Each opportunity is also reduced to exactly one status — Proposal
Ready, Needs Review, or Ready To Send — written to
output/ceo-advisor-feed.json. That status is the only thing
09-CEO-Advisor ever reads from Sales Director; it never sees a draft.

This script prepares. It never sends. There is no code path in this
file that transmits anything anywhere — every output is a file on disk
for the founder to review.

Idempotent: processed-index.json records every opportunity id already
packaged, so a re-run only prepares opportunities that are new since
the last run.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
SALES_DIRECTOR_DIR = RUNTIME_DIR.parent
AOS_DIR = SALES_DIRECTOR_DIR.parent
REPO_ROOT = AOS_DIR.parent

OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "opportunity-hunter" / "opportunity-schema.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
SERVICE_RECOMMENDATIONS_PATH = AOS_DIR / "service-mapping" / "service-recommendations.json"

CONFIG_DIR = RUNTIME_DIR / "config"
OUTPUT_DIR = RUNTIME_DIR / "output"
PACKAGES_DIR = OUTPUT_DIR / "packages"
PROCESSED_INDEX_PATH = RUNTIME_DIR / "processed-index.json"
CEO_FEED_PATH = OUTPUT_DIR / "ceo-advisor-feed.json"

TODAY = date.today().isoformat()

# opportunity-hunter/opportunity-scoring-engine.md's eight classifications;
# these four are the ones an outbound package makes sense for.
TARGET_CLASSIFICATIONS = {"Immediate Proposal", "Apply", "Partnership", "Follow Recruiter"}

# proposal-preparation-engine.md, Proposal Confidence Score
CONFIDENCE_WEIGHTS = {
    "probabilityOfWinning": 0.30,
    "priorityScoreNormalised": 0.30,
    "dataCompleteness": 0.25,
    "scopedBonus": 0.15,
}

DEFAULT_PROCESSED_INDEX = {
    "schema": {
        "opportunityId": "string — matches opportunity-hunter/opportunity-schema.json's id",
        "datePrepared": "string — ISO 8601 date",
        "status": "string — Proposal Ready, Needs Review, or Ready To Send",
        "packagePath": "string — path to the generated package, relative to the repo root",
    },
    "processed": {},
}

DEFAULT_CEO_FEED = {
    "schema": {
        "opportunityId": "string",
        "title": "string",
        "organisation": "string",
        "status": "string — Proposal Ready, Needs Review, or Ready To Send — the only field 09-CEO-Advisor reads",
        "packagePath": "string — where the founder reviews the full package; CEO Advisor does not open this itself",
    },
    "feed": [],
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


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# --------------------------------------------------------------------------
# Content bank selection — proposal-preparation-engine.md, "The Content Bank"
# --------------------------------------------------------------------------

def select_bank_items(bank_items, domain_tags):
    domain_set = set(domain_tags or [])
    return [item for item in bank_items if domain_set & set(item.get("domainTags", []))]


# --------------------------------------------------------------------------
# Pricing — proposal-preparation-engine.md, "Recommended Pricing"
# --------------------------------------------------------------------------

def infer_engagement_type(opportunity, pipeline_entry):
    if pipeline_entry:
        return pipeline_entry.get("type", "Consulting Project")
    if opportunity["classification"] == "Partnership":
        return "Partnership"
    return "Consulting Project"


def recommend_pricing(opportunity, pipeline_entry, rate_card):
    if pipeline_entry and pipeline_entry.get("expectedRevenue") not in (None, "", "Not yet estimated"):
        return {"basis": "revenue-hunter-pipeline", "amount": str(pipeline_entry["expectedRevenue"]), "note": ""}

    engagement_type = infer_engagement_type(opportunity, pipeline_entry)
    card = rate_card["types"].get(engagement_type, {})
    if "dayRate" not in card:
        note = card.get("note", "No rate-card model for this engagement type yet.")
        return {"basis": "rate-card-note", "amount": note, "note": "Confirm actual terms before sending."}

    day_rate = card["dayRate"]
    low_days, high_days = card["typicalDays"]["min"], card["typicalDays"]["max"]
    low, high = day_rate * low_days, day_rate * high_days

    time_required = opportunity["scores"].get("timeRequired", 5)
    adj = rate_card["effortAdjustment"]
    if time_required >= adj["lowEffortThreshold"]:
        low, high = low * adj["highEffortDiscount"], high * adj["highEffortDiscount"]
    elif time_required < adj["highOverheadThreshold"]:
        low, high = low * adj["highOverheadUplift"], high * adj["highOverheadUplift"]

    currency = rate_card.get("defaultCurrency", "USD")
    unit = card.get("unit", "per day")
    amount = f"{currency} {round(low):,} - {currency} {round(high):,} ({engagement_type}, {unit})"
    return {
        "basis": "rate-card-estimate",
        "amount": amount,
        "note": "Confirm before sending — this is a starting-point estimate, not a quoted price.",
    }


# --------------------------------------------------------------------------
# Confidence + status — proposal-preparation-engine.md
# --------------------------------------------------------------------------

def data_completeness(opportunity, crm_entry, pricing):
    checks = [
        bool(opportunity.get("organisation")),
        bool(opportunity.get("description")),
        bool(opportunity.get("domainTags")),
        bool(crm_entry and (crm_entry.get("recruiter") or crm_entry.get("existingRelationship") not in (None, "none"))),
        pricing["basis"] == "revenue-hunter-pipeline",
    ]
    return sum(2 for c in checks if c)


def compute_confidence(opportunity, crm_entry, pricing):
    probability = opportunity["scores"].get("probabilityOfWinning", 0)
    priority_normalised = opportunity["priorityScore"] / 10
    completeness = data_completeness(opportunity, crm_entry, pricing)
    scoped_bonus = 10 if opportunity.get("scopedEngagement") else 4

    weighted = (
        probability * CONFIDENCE_WEIGHTS["probabilityOfWinning"]
        + priority_normalised * CONFIDENCE_WEIGHTS["priorityScoreNormalised"]
        + completeness * CONFIDENCE_WEIGHTS["dataCompleteness"]
        + scoped_bonus * CONFIDENCE_WEIGHTS["scopedBonus"]
    )
    return round(weighted * 10)


def determine_status(confidence, opportunity):
    if opportunity.get("autoScored") or confidence < 50:
        return "Needs Review"
    if confidence >= 75 and opportunity.get("scopedEngagement"):
        return "Ready To Send"
    return "Proposal Ready"


# --------------------------------------------------------------------------
# Document generation
# --------------------------------------------------------------------------

def clarifying_questions(opportunity, pricing):
    questions = []
    if not opportunity.get("scopedEngagement"):
        questions.append("Is this a fixed-scope engagement, an ongoing advisory arrangement, or still an open-ended lead?")
    if opportunity.get("location") in (None, "", "Not specified"):
        questions.append("Where is this based, and is remote delivery acceptable?")
    domain_tags = set(opportunity.get("domainTags", []))
    if domain_tags & {"ADGL", "AI Deployment Governance"}:
        questions.append("How many AI systems or use cases are currently in production or planned, and which ones are in scope?")
    if "AI Governance" in domain_tags:
        questions.append("Is there an existing governance owner or committee today, or would this be the first one?")
    if pricing["basis"] != "revenue-hunter-pipeline":
        questions.append("What budget range or rate has already been discussed, if any?")
    questions.append("What does success look like by the end of this engagement, from your side?")
    return questions


def opening_reference(opportunity, crm_entry):
    if crm_entry and crm_entry.get("outreachHistory"):
        last = crm_entry["outreachHistory"][-1]
        return f"Following up on our {last['channel']} conversation ({last['date']}) about {opportunity['title']}."
    return f"Reaching out regarding {opportunity['title']} at {opportunity['organisation']}."


def cover_letter(opportunity, crm_entry, bank):
    experience = select_bank_items(bank["practitionerExperience"], opportunity["domainTags"])
    lead_experience = experience[0]["text"] if experience else bank["practitionerExperience"][0]["text"]
    positioning = (crm_entry or {}).get("tailoredPositioning", "")

    lines = [
        f"Dear {opportunity['organisation']} team,",
        "",
        opening_reference(opportunity, crm_entry),
        "",
        f"I'm Ramya Amballa, founder of AI for U&I, an independent advisory practice in AI governance, "
        f"technology risk and GRC. {lead_experience}",
    ]
    if positioning:
        lines += ["", positioning]
    lines += [
        "",
        f"Based on what's been described, this looks like a strong fit for {opportunity['title']}, "
        f"and I'd welcome the chance to discuss it further.",
        "",
        "Ramya",
    ]
    return "\n".join(lines)


def proposal_document(opportunity, bank, pricing):
    products = select_bank_items(bank["products"], opportunity["domainTags"])
    experience = select_bank_items(bank["practitionerExperience"], opportunity["domainTags"])
    domain_tags = set(opportunity.get("domainTags", []))

    sections = [
        f"## Proposal — {opportunity['title']} ({opportunity['organisation']})",
        "",
        f"**Prepared by:** AI for U&I  ",
        f"**Date:** {TODAY}  ",
        f"**Reference:** {opportunity['id']}",
        "",
        "### Situation",
        opportunity.get("description") or "As discussed.",
        "",
        "### Relevant Experience",
    ]
    sections += [f"- {item['text']}" for item in experience] or [
        "- General AI governance and technology risk advisory background — see AI for U&I's About page."
    ]

    if domain_tags & {"ADGL", "AI Deployment Governance"}:
        sections += [
            "",
            "### Approach: AI Deployment Governance Lifecycle (ADGL)",
            "This engagement is scoped using ADGL's five phases: " + ", ".join(bank["adglPhases"]) + ".",
        ]
    if domain_tags & {"AI Governance", "GRC"}:
        sections += [
            "",
            "### Approach: OPERA",
            "Governance decisions are sequenced using the OPERA methodology: " + ", ".join(bank["operaPhases"]) + ".",
        ]

    if products:
        sections += ["", "### Relevant Prior Work"]
        sections += [f"- **{p['title']}** — {p['description']}" for p in products]

    sections += ["", "### Recommended Pricing", pricing["amount"]]
    if pricing["note"]:
        sections.append(f"*{pricing['note']}*")

    sections += [
        "",
        "### Next Steps",
        "A short scoping call to confirm the details below before any formal engagement begins.",
    ]
    return "\n".join(sections)


def recruiter_outreach(opportunity, crm_entry):
    has_recruiter = opportunity.get("sourceCategory") == "Recruiter Channel" or (crm_entry or {}).get("recruiter")
    if not has_recruiter:
        return "Not applicable — no recruiter channel identified for this opportunity."
    recruiter = (crm_entry or {}).get("recruiter") or opportunity.get("source")
    lines = [
        f"Hi {recruiter},",
        "",
        opening_reference(opportunity, crm_entry),
        "",
        f"I'd like to move forward on {opportunity['title']} at {opportunity['organisation']}. Could you share "
        f"the client's expected timeline and rate range, and what the next step in their process looks like?",
        "",
        "Ramya",
    ]
    return "\n".join(lines)


def client_outreach(opportunity, crm_entry):
    recruiter_only = opportunity.get("sourceCategory") == "Recruiter Channel" and (
        crm_entry or {}
    ).get("existingRelationship", "none") == "none"
    if recruiter_only:
        return "Not applicable — reaching this organisation directly bypasses the recruiter channel it came through."
    lines = [
        "Hello,",
        "",
        opening_reference(opportunity, crm_entry),
        "",
        f"I'm Ramya Amballa, founder of AI for U&I. I'd welcome a short call to understand "
        f"{opportunity['title']} in more detail and confirm whether there's a fit before anything formal.",
        "",
        "Ramya",
    ]
    return "\n".join(lines)


def build_package(opportunity, pipeline_entry, crm_entry, bank, rate_card, service_recommendation):
    pricing = recommend_pricing(opportunity, pipeline_entry, rate_card)
    confidence = compute_confidence(opportunity, crm_entry, pricing)
    status = determine_status(confidence, opportunity)

    return {
        "opportunityId": opportunity["id"],
        "title": opportunity["title"],
        "organisation": opportunity["organisation"],
        "classification": opportunity["classification"],
        "datePrepared": TODAY,
        "coverLetter": cover_letter(opportunity, crm_entry, bank),
        "proposal": proposal_document(opportunity, bank, pricing),
        "recruiterOutreach": recruiter_outreach(opportunity, crm_entry),
        "clientOutreach": client_outreach(opportunity, crm_entry),
        "clarifyingQuestions": clarifying_questions(opportunity, pricing),
        "recommendedPricing": pricing,
        "confidenceScore": confidence,
        "status": status,
        "serviceRecommendation": service_recommendation,
    }


def render_service_mapping_section(service_recommendation):
    """Additive only — service-mapping/'s own recommendation, surfaced
    read-only. Never affects cover letter, proposal text, pricing,
    confidence score or status above, all computed exactly as before
    this section existed."""
    if not service_recommendation:
        return ("## Service Mapping\n\n"
                "_Not yet mapped — the Service Mapping Engine has not processed this "
                "opportunity yet (it runs before Sales Director in the daily sequence; "
                "this can happen on the same day an opportunity is first discovered)._")
    if service_recommendation.get("notApplicable"):
        return f"## Service Mapping\n\n_Not applicable — {service_recommendation['notApplicableReason']}_"

    r = service_recommendation
    lines = [
        "## Service Mapping",
        "",
        f"**Primary Service:** {r['primaryService']}  ",
        f"**Recommended Engagement Type:** {r['recommendedEngagementType']}  ",
        f"**Estimated Project Size:** {r['estimatedProjectSize']} ({r['projectSizeBasis']})  ",
        f"**Recommended Proposal Template:** `templates/proposals/{r['recommendedProposalTemplate']}`",
        "",
        "**Secondary Services:** " + " → ".join(r["secondaryServices"]) if r["secondaryServices"] else
        "**Secondary Services:** _none_",
    ]
    if r["crossSellOpportunities"]:
        lines += ["", "**Cross-Sell Opportunities:** " + "; ".join(r["crossSellOpportunities"])]
    return "\n".join(lines)


def render_package_markdown(package):
    lines = [
        f"# Sales Director Package — {package['title']} ({package['organisation']})",
        "",
        f"**Opportunity:** {package['opportunityId']}  ",
        f"**Classification:** {package['classification']}  ",
        f"**Prepared:** {package['datePrepared']}  ",
        f"**Confidence score:** {package['confidenceScore']}/100  ",
        f"**Status:** {package['status']}",
        "",
        "---",
        "",
        render_service_mapping_section(package["serviceRecommendation"]),
        "",
        "---",
        "",
        "## Cover Letter",
        "",
        package["coverLetter"],
        "",
        "---",
        "",
        package["proposal"],
        "",
        "---",
        "",
        "## Recruiter Outreach",
        "",
        package["recruiterOutreach"],
        "",
        "---",
        "",
        "## Client Outreach",
        "",
        package["clientOutreach"],
        "",
        "---",
        "",
        "## Questions to Clarify Scope",
        "",
    ]
    lines += [f"- {q}" for q in package["clarifyingQuestions"]]
    lines += [
        "",
        "---",
        "",
        "*This package is preparation only. Review and send by hand — nothing here is sent automatically.*",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    schema_data = load_json(OPPORTUNITY_SCHEMA_PATH)
    pipeline_data = load_json(PIPELINE_PATH)
    crm_data = load_json(CRM_PATH)
    rate_card = load_json(CONFIG_DIR / "rate-card.json")
    bank = load_json(CONFIG_DIR / "practitioner-bank.json")
    # Read-only, optional — service-mapping/'s own output. Sales Director's
    # core logic (pricing, confidence, status) is unaffected either way;
    # this only fills in the additive Service Mapping section (see
    # render_service_mapping_section()).
    service_recommendations = load_json(
        SERVICE_RECOMMENDATIONS_PATH, {"recommendations": {}}
    ).get("recommendations", {})
    processed_index = load_json(PROCESSED_INDEX_PATH, DEFAULT_PROCESSED_INDEX)
    processed_index.setdefault("processed", {})

    candidates = [
        o for o in schema_data["opportunities"]
        if o.get("classification") in TARGET_CLASSIFICATIONS and o["id"] not in processed_index["processed"]
    ]

    if not candidates:
        print("No new classified opportunities to prepare. Nothing to do.")
        return 0

    pipeline_by_ref = {e["sourceRef"]: e for e in pipeline_data["pipeline"] if e.get("sourceRef")}
    crm_by_org = {c["companyName"]: c for c in crm_data["companies"]}

    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    ceo_feed = load_json(CEO_FEED_PATH, DEFAULT_CEO_FEED)
    ceo_feed.setdefault("feed", [])

    prepared = []
    for opportunity in candidates:
        pipeline_entry = pipeline_by_ref.get(opportunity["id"])
        crm_entry = crm_by_org.get(opportunity["organisation"])
        service_recommendation = service_recommendations.get(opportunity["id"])
        package = build_package(opportunity, pipeline_entry, crm_entry, bank, rate_card, service_recommendation)

        slug = slugify(f"{opportunity['id']}-{opportunity['organisation']}-{opportunity['title']}")[:80]
        package_path = PACKAGES_DIR / f"{slug}.md"
        package_path.write_text(render_package_markdown(package), encoding="utf-8")
        relative_path = str(package_path.relative_to(REPO_ROOT))

        ceo_feed["feed"].append({
            "opportunityId": opportunity["id"],
            "title": opportunity["title"],
            "organisation": opportunity["organisation"],
            "status": package["status"],
            "packagePath": relative_path,
        })
        processed_index["processed"][opportunity["id"]] = {
            "datePrepared": TODAY,
            "status": package["status"],
            "packagePath": relative_path,
        }
        prepared.append(package)
        print(f"  {opportunity['id']}: {opportunity['title']} -> confidence {package['confidenceScore']}/100 -> {package['status']}")

    save_json(CEO_FEED_PATH, ceo_feed)
    save_json(PROCESSED_INDEX_PATH, processed_index)

    report_path = OUTPUT_DIR / f"{TODAY}-sales-director-report.md"
    report_lines = [
        "# Sales Director — Daily Preparation Report",
        "",
        f"**Date:** {TODAY}",
        f"**Packages prepared:** {len(prepared)}",
        "",
    ]
    for p in prepared:
        report_lines.append(f"- **{p['title']}** ({p['organisation']}) — {p['confidenceScore']}/100 — {p['status']}")
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n{len(prepared)} packages prepared. Report: {report_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
