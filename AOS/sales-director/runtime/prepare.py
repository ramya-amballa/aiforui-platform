#!/usr/bin/env python3
"""
Sales Director — Proposal Preparation Engine (execution mode)

Usage:
    python3 prepare.py

Reads every opportunity in ../../demand-intelligence/opportunity-schema.json
classified Immediate Proposal, Apply, Partnership or Follow Recruiter,
and — for any not already prepared — writes to output/packages/: one
combined package file (cover letter, proposal, recruiter outreach,
client outreach, clarifying questions, recommended pricing and a
proposal confidence score, all in one document) plus one standalone
file per artifact (-proposal.md, -cover-letter.md, -recruiter-message.md,
-client-outreach.md) so the dashboard can preview/copy/download each
piece on its own. write_package_files() is the one place any of these
five files gets written — every prepared package always gets all five;
there is no code path that records a path without writing the file it
points to. The model behind pricing and confidence is documented in
../proposal-preparation-engine.md; read that first if a number here
looks wrong.

Also repairs (backfills) any already-processed opportunity whose
recorded paths predate the four standalone files above — regenerates
just the missing files and adds the missing path keys, without
duplicating its feed entry or changing a status already recorded.

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

import copy
import json
import re
import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
SALES_DIRECTOR_DIR = RUNTIME_DIR.parent
AOS_DIR = SALES_DIRECTOR_DIR.parent
REPO_ROOT = AOS_DIR.parent

OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "demand-intelligence" / "opportunity-schema.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
SERVICE_RECOMMENDATIONS_PATH = AOS_DIR / "service-mapping" / "service-recommendations.json"
ACCOUNT_INTELLIGENCE_FEED_PATH = AOS_DIR / "account-intelligence" / "runtime" / "output" / "account-intelligence-feed.json"
PROPOSAL_CONTENT_LIBRARY_PATH = AOS_DIR / "templates" / "proposals" / "proposal-content-library.json"

CONFIG_DIR = RUNTIME_DIR / "config"
OUTPUT_DIR = RUNTIME_DIR / "output"
PACKAGES_DIR = OUTPUT_DIR / "packages"
PROCESSED_INDEX_PATH = RUNTIME_DIR / "processed-index.json"
CEO_FEED_PATH = OUTPUT_DIR / "ceo-advisor-feed.json"

TODAY = date.today().isoformat()

# demand-intelligence/opportunity-scoring-engine.md's eight classifications;
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
        "opportunityId": "string — matches demand-intelligence/opportunity-schema.json's id",
        "datePrepared": "string — ISO 8601 date",
        "status": "string — Proposal Ready, Needs Review, or Ready To Send",
        "packagePath": "string — path to the combined package (all sections in one file), relative to the repo root",
        "proposalPath": "string — path to just the proposal document, relative to the repo root",
        "coverLetterPath": "string — path to just the cover letter, relative to the repo root",
        "recruiterMessagePath": "string — path to just the recruiter outreach message, relative to the repo root",
        "clientOutreachPath": "string — path to just the client outreach message, relative to the repo root",
    },
    "processed": {},
}

DEFAULT_CEO_FEED = {
    "schema": {
        "opportunityId": "string",
        "title": "string",
        "organisation": "string",
        "status": "string — Proposal Ready, Needs Review, or Ready To Send — the only field 09-CEO-Advisor reads",
        "packagePath": "string — the combined package (all sections in one file); CEO Advisor does not open this itself",
        "proposalPath": "string — standalone proposal document, so the dashboard can preview/copy/download it alone",
        "coverLetterPath": "string — standalone cover letter",
        "recruiterMessagePath": "string — standalone recruiter outreach message",
        "clientOutreachPath": "string — standalone client outreach message",
    },
    "feed": [],
}

# (path_key, package content key, human label, filename suffix) for each
# standalone artifact file written alongside the combined package.md —
# lets the dashboard preview/copy/download each piece independently
# instead of only the combined file.
SECTION_SPECS = [
    ("proposalPath", "proposal", "Proposal", "proposal"),
    ("coverLetterPath", "coverLetter", "Cover Letter", "cover-letter"),
    ("recruiterMessagePath", "recruiterOutreach", "Recruiter Message", "recruiter-message"),
    ("clientOutreachPath", "clientOutreach", "Client Outreach", "client-outreach"),
]


def load_json(path, default=None):
    if not path.exists():
        if default is not None:
            # Deep-copy, never the caller's own object - DEFAULT_PROCESSED_INDEX
            # and DEFAULT_CEO_FEED are module-level constants callers reuse on
            # every invocation; returning them directly would let main()'s own
            # in-place mutations (processed_index["processed"][...] = ...,
            # ceo_feed["feed"].append(...)) silently corrupt that shared
            # constant for every later call in the same process.
            return copy.deepcopy(default)
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
# Opportunity Qualification Engine (AOS Sprint 18) — "is this worth my
# time?" Every input below is a real, already-computed score from
# opportunity-schema.json (per opportunity-scoring-engine.md) or a real
# cross-reference to Account Intelligence/CRM — never a second,
# independently-invented number. This is advisory only: it never
# changes whether a package gets prepared (that's classification's
# job, upstream, untouched here); it only tells the founder, up front,
# whether this opportunity is worth pursuing.
# --------------------------------------------------------------------------

def brand_value(ai_entry, crm_entry):
    if ai_entry and ai_entry.get("buyingReadinessBand") in ("High", "Very High"):
        return f"High — Account Intelligence records {ai_entry['buyingReadinessBand']} buying readiness"
    if crm_entry and (crm_entry.get("existingRelationship") or "none").lower() != "none":
        return f"Medium — CRM records an existing relationship ({crm_entry['existingRelationship']})"
    return "Not enough signal yet"


def repeat_business_potential(opportunity, crm_entry):
    score = opportunity.get("scores", {}).get("longTermRelationshipPotential", 0)
    prior_count = len((crm_entry or {}).get("previousApplications", []))
    detail = (
        f"{prior_count} prior application(s) on record in CRM" if prior_count
        else "No prior applications on record in CRM"
    )
    return {"score": score, "detail": detail}


def time_investment_label(opportunity):
    # timeRequired is already inverted per opportunity-scoring-engine.md — 10 = least time.
    score = opportunity.get("scores", {}).get("timeRequired", 5)
    if score >= 7:
        label = "Low — quick to deliver"
    elif score >= 4:
        label = "Medium"
    else:
        label = "High — a longer engagement"
    return score, label


def competition_level():
    # Always honest: AOS has no data source for competing bids on any opportunity.
    return "Not tracked — AOS has no data source for competitor activity on this opportunity."


def qualification_verdict(opportunity, pricing, ai_entry, crm_entry, config):
    scores = opportunity.get("scores", {})
    probability = scores.get("probabilityOfWinning", 0)
    strategic = scores.get("strategicValue", 0)
    repeat = repeat_business_potential(opportunity, crm_entry)
    time_score, time_label = time_investment_label(opportunity)
    expected_revenue_score = scores.get("expectedRevenue", 0)

    weights = config.get("weights", {})
    weighted = (
        probability * weights.get("probabilityOfWinning", 0)
        + strategic * weights.get("strategicValue", 0)
        + repeat["score"] * weights.get("repeatBusinessPotential", 0)
        + time_score * weights.get("timeInvestment", 0)
        + expected_revenue_score * weights.get("estimatedValue", 0)
    )

    thresholds = config.get("verdictThresholds", {})
    if weighted >= thresholds.get("pursue", 7.0):
        verdict = "Pursue"
    elif weighted >= thresholds.get("consider", 4.5):
        verdict = "Consider"
    else:
        verdict = "Ignore"

    return {
        "verdict": verdict,
        "weightedScore": round(weighted, 1),
        "estimatedProjectValue": pricing["amount"],
        "probabilityOfWinning": probability,
        "strategicValue": strategic,
        "brandValue": brand_value(ai_entry, crm_entry),
        "repeatBusinessPotential": repeat["score"],
        "repeatBusinessDetail": repeat["detail"],
        "timeInvestment": time_label,
        "competitionLevel": competition_level(),
    }


def render_qualification_section(qualification):
    return "\n".join([
        f"## Opportunity Qualification — {qualification['verdict']} ({qualification['weightedScore']}/10)",
        "",
        f"- **Estimated project value:** {qualification['estimatedProjectValue']}",
        f"- **Probability of winning:** {qualification['probabilityOfWinning']}/10",
        f"- **Strategic value:** {qualification['strategicValue']}/10",
        f"- **Brand value:** {qualification['brandValue']}",
        f"- **Repeat business potential:** {qualification['repeatBusinessPotential']}/10 — {qualification['repeatBusinessDetail']}",
        f"- **Time investment:** {qualification['timeInvestment']}",
        f"- **Competition level:** {qualification['competitionLevel']}",
        "",
        "*Advisory only — this verdict never changes whether a package is prepared; "
        "it's a starting judgement for the founder, not a filter.*",
    ])


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


def find_account_intelligence_entry(organisation, ai_feed):
    for entry in ai_feed.get("briefs", []):
        if entry.get("organisation") == organisation:
            return entry
    return None


def commercial_options(pricing, rate_card):
    """AOS Sprint 12 — the four Commercial Options every Executive
    Proposal offers, each grounded in rate-card.json's own real,
    already-existing figures (never a fabricated number). Discovery
    and Assessment/Implementation reuse the same day-rate types
    recommend_pricing() already draws from; Retainer uses the new
    'Fractional Retainer' rate-card entry (same day rate as Consulting
    Project, framed as an ongoing monthly commitment)."""
    types = rate_card.get("types", {})
    currency = rate_card.get("defaultCurrency", "USD")

    def describe(type_name, label):
        card = types.get(type_name, {})
        if "dayRate" not in card:
            return f"{label}: see rate-card note — {card.get('note', 'pricing to be confirmed')}."
        rate = card["dayRate"]
        low, high = card["typicalDays"]["min"], card["typicalDays"]["max"]
        unit = card.get("unit", "per day")
        return f"{label}: {currency} {rate:,} {unit}, typically {low}-{high} {'days' if 'day' in unit else 'units'}."

    return {
        "Discovery": describe("Workshop", "Discovery Workshop"),
        "Assessment": describe("Consulting Project", "Assessment"),
        "Implementation": describe("Enterprise Contract", "Implementation"),
        "Retainer": describe("Fractional Retainer", "Retainer"),
    }


def regulatory_deliverables(service_recommendation, proposal_content_library):
    """AOS Sprint 23 — Engagement Templates. Reuses templates/proposals/'s
    own already-authored, framework-specific deliverable list — via
    service-mapping's own already-computed recommendedProposalTemplate,
    never a second, independent template selection — instead of the
    generic three-bullet fallback. None when no service recommendation
    exists yet, or its template isn't in the library, so the caller can
    fall back to the generic list rather than fabricate one."""
    if not service_recommendation or service_recommendation.get("notApplicable"):
        return None
    template_filename = service_recommendation.get("recommendedProposalTemplate")
    if not template_filename:
        return None
    entry = proposal_content_library.get(template_filename)
    return entry.get("keyDeliverables") if entry else None


def executive_proposal_document(opportunity, ai_entry, service_recommendation, pricing, bank, rate_card,
                                 proposal_content_library=None):
    """AOS Sprint 12 — the Executive Proposal Generator. Every fact-
    bearing section traces back to Account Intelligence's own already-
    computed brief data (ai_entry) — company profile, AI initiatives,
    governance risks, service fit, supporting assets — never a second,
    independent guess at the same facts, and nothing here is invented
    beyond what that brief already established. Returns None when no
    Account Intelligence brief exists yet for this organisation, so the
    caller can fall back to the pre-Sprint-12 generic proposal rather
    than fabricate these sections from nothing."""
    if not ai_entry:
        return None

    company = ai_entry.get("companyProfile", {})
    risks = ai_entry.get("governanceRisks", [])
    services = ai_entry.get("serviceFit", [])
    assets = ai_entry.get("supportingAssets", [])
    initiatives = ai_entry.get("aiInitiatives", [])
    experience = select_bank_items(bank["practitionerExperience"], opportunity.get("domainTags", []))

    lines = [
        f"# Executive Proposal — {opportunity['organisation']}",
        "",
        f"**Prepared by:** AI for U&I  ",
        f"**Date:** {TODAY}  ",
        f"**Reference:** {opportunity['id']}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        ai_entry.get("executiveSummary", "Not yet available."),
        "",
        "---",
        "",
        "## Business Context",
        "",
        f"- **Industry:** {company.get('industry', 'Not specified')}",
        f"- **Geographic footprint:** {company.get('geographicFootprint', 'Not specified')}",
        f"- **Approximate size:** {company.get('approximateSize', 'Not specified')}",
        f"- **Regulatory environment:** {company.get('regulatoryEnvironment', 'Not specified')}",
        f"- **Deployment stage:** {ai_entry.get('deploymentStage', 'Not specified')}",
        "",
        "---",
        "",
        "## Observed AI Initiatives",
        "",
    ]
    lines += [f"- {i}" for i in initiatives] or ["- None recorded yet."]

    lines += ["", "---", "", "## Likely Governance Challenges", ""]
    lines += [f"- **{r['risk']}** — {r['why']}" for r in risks] or ["- Not enough signal yet to assess."]

    lines += ["", "---", "", "## Recommended Engagement", ""]
    lines += [f"- **{s['service']}** — {s['confidence']} confidence" for s in services] or ["- Not enough signal yet to rank service fit."]

    tailored_deliverables = regulatory_deliverables(service_recommendation, proposal_content_library or {})
    lines += ["", "---", "", "## Deliverables", ""]
    if tailored_deliverables:
        lines += [f"- {d}" for d in tailored_deliverables]
    else:
        lines += [
            "- A findings report scoped to the governance challenges above",
            "- A prioritised remediation/implementation roadmap",
            "- Executive briefing session to walk through findings and recommendations",
        ]

    lines += [
        "", "---", "", "## Timeline", "",
        "A short scoping call to confirm scope and sequencing before any formal engagement begins.",
    ]

    lines += [
        "", "---", "", "## Success Metrics", "",
        "- Governance gaps identified above have a named owner and a documented remediation plan",
        "- Recommended service(s) above are scoped into a signed statement of work",
        "- No material governance gap remains undocumented at engagement close",
    ]

    options = commercial_options(pricing, rate_card)
    lines += ["", "---", "", "## Commercial Options", ""]
    for label in ("Discovery", "Assessment", "Implementation", "Retainer"):
        lines.append(f"- **{label}:** {options[label]}")
    if pricing.get("note"):
        lines.append(f"\n*{pricing['note']}*")

    lines += ["", "---", "", "## Appendices — Relevant AI for U&I Resources", ""]
    lines += [f"- **{a['title']}** ({a['type']}) — {a['url']}" for a in assets] or ["- None specifically relevant identified yet."]

    if experience:
        lines += ["", "---", "", "## Practitioner Experience", ""]
        lines += [f"- {item['text']}" for item in experience]

    lines += ["", "---", "", "*This proposal is preparation only. Review and send by hand — nothing here is sent automatically.*"]
    return "\n".join(lines)


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


def build_package(opportunity, pipeline_entry, crm_entry, bank, rate_card, service_recommendation, ai_entry=None,
                   qualification_config=None, proposal_content_library=None):
    pricing = recommend_pricing(opportunity, pipeline_entry, rate_card)
    confidence = compute_confidence(opportunity, crm_entry, pricing)
    status = determine_status(confidence, opportunity)
    qualification = qualification_verdict(opportunity, pricing, ai_entry, crm_entry, qualification_config or {})

    # AOS Sprint 12 — an Executive Proposal (traced back to Account
    # Intelligence's own brief) whenever one exists for this organisation;
    # otherwise the original generic proposal_document(), never a blank.
    proposal = executive_proposal_document(
        opportunity, ai_entry, service_recommendation, pricing, bank, rate_card, proposal_content_library
    ) or proposal_document(opportunity, bank, pricing)

    return {
        "opportunityId": opportunity["id"],
        "title": opportunity["title"],
        "organisation": opportunity["organisation"],
        "classification": opportunity["classification"],
        "datePrepared": TODAY,
        "coverLetter": cover_letter(opportunity, crm_entry, bank),
        "proposal": proposal,
        "recruiterOutreach": recruiter_outreach(opportunity, crm_entry),
        "clientOutreach": client_outreach(opportunity, crm_entry),
        "clarifyingQuestions": clarifying_questions(opportunity, pricing),
        "recommendedPricing": pricing,
        "confidenceScore": confidence,
        "status": status,
        "serviceRecommendation": service_recommendation,
        "qualification": qualification,
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
        render_qualification_section(package["qualification"]),
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


def write_package_files(package, slug):
    """Writes the combined package.md (unchanged - full package review) plus
    one standalone file per artifact (proposal, cover letter, recruiter
    message, client outreach), so the dashboard can preview/copy/download
    each piece on its own instead of only the combined file. Every prepared
    package always gets all five files - there is no code path that records
    a path without writing the file it points to. Returns every path
    (relative to REPO_ROOT) to store in the feed/processed-index record."""
    package_path = PACKAGES_DIR / f"{slug}.md"
    package_path.write_text(render_package_markdown(package), encoding="utf-8")
    paths = {"packagePath": str(package_path.relative_to(REPO_ROOT))}

    for path_key, content_key, label, file_suffix in SECTION_SPECS:
        section_path = PACKAGES_DIR / f"{slug}-{file_suffix}.md"
        body = package[content_key]
        # proposal_document() already opens with its own "## Proposal —
        # ..." heading; the other three are plain letters/messages with
        # no heading of their own, so they need one added for context
        # when downloaded standalone.
        heading = "" if body.lstrip().startswith("#") else f"# {label} — {package['title']} ({package['organisation']})\n\n"
        section_path.write_text(heading + body, encoding="utf-8")
        paths[path_key] = str(section_path.relative_to(REPO_ROOT))

    return paths


def missing_section_paths(processed_record):
    """True if a processed-index record predates the standalone section
    files above (written only a combined packagePath) - the exact real
    state that made the dashboard's per-section preview/download show
    "file not found" for a package prepared before this existed."""
    return any(key not in processed_record for key, _, _, _ in SECTION_SPECS)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    schema_data = load_json(OPPORTUNITY_SCHEMA_PATH)
    pipeline_data = load_json(PIPELINE_PATH)
    crm_data = load_json(CRM_PATH)
    rate_card = load_json(CONFIG_DIR / "rate-card.json")
    bank = load_json(CONFIG_DIR / "practitioner-bank.json")
    # AOS Sprint 18 — Opportunity Qualification Engine's weights/thresholds.
    qualification_config = load_json(CONFIG_DIR / "opportunity-qualification-config.json", {})
    # AOS Sprint 23 — Engagement Templates. Static, shared config; see
    # templates/proposals/proposal-content-library.json's own comment.
    proposal_content_library = load_json(PROPOSAL_CONTENT_LIBRARY_PATH, {})
    # Read-only, optional — service-mapping/'s own output. Sales Director's
    # core logic (pricing, confidence, status) is unaffected either way;
    # this only fills in the additive Service Mapping section (see
    # render_service_mapping_section()).
    service_recommendations = load_json(
        SERVICE_RECOMMENDATIONS_PATH, {"recommendations": {}}
    ).get("recommendations", {})
    # Read-only, optional — account-intelligence/'s own brief, one cycle
    # behind (Sales Director runs before Account Intelligence in the fixed
    # order; see orchestrator-config.json's sales-director note). Same
    # accepted-limitation pattern as CRM's read of Sales Director's own
    # processed-index.json — see crm-runtime-notes.md. When a brief exists
    # it upgrades the proposal to an Executive Proposal; when it doesn't
    # yet, the original generic proposal is used, never a blank.
    ai_feed = load_json(ACCOUNT_INTELLIGENCE_FEED_PATH, {"briefs": []})
    processed_index = load_json(PROCESSED_INDEX_PATH, DEFAULT_PROCESSED_INDEX)
    processed_index.setdefault("processed", {})

    new_candidates = []
    backfill_candidates = []
    for o in schema_data["opportunities"]:
        if o.get("classification") not in TARGET_CLASSIFICATIONS:
            continue
        record = processed_index["processed"].get(o["id"])
        if record is None:
            new_candidates.append(o)
        elif missing_section_paths(record):
            # Prepared by a version of this script that only wrote the
            # combined package.md - the exact state that made the
            # dashboard's per-section preview/download show "file not
            # found on disk". Repair it below rather than skip it forever.
            backfill_candidates.append(o)

    if not new_candidates and not backfill_candidates:
        print("No new classified opportunities to prepare, and no existing packages missing their proposal files. Nothing to do.")
        return 0

    pipeline_by_ref = {e["sourceRef"]: e for e in pipeline_data["pipeline"] if e.get("sourceRef")}
    crm_by_org = {c["companyName"]: c for c in crm_data["companies"]}

    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    ceo_feed = load_json(CEO_FEED_PATH, DEFAULT_CEO_FEED)
    ceo_feed.setdefault("feed", [])
    feed_by_id = {e["opportunityId"]: e for e in ceo_feed["feed"]}

    prepared = []
    for opportunity in new_candidates:
        pipeline_entry = pipeline_by_ref.get(opportunity["id"])
        crm_entry = crm_by_org.get(opportunity["organisation"])
        service_recommendation = service_recommendations.get(opportunity["id"])
        ai_entry = find_account_intelligence_entry(opportunity["organisation"], ai_feed)
        package = build_package(opportunity, pipeline_entry, crm_entry, bank, rate_card, service_recommendation, ai_entry,
                                 qualification_config, proposal_content_library)

        slug = slugify(f"{opportunity['id']}-{opportunity['organisation']}-{opportunity['title']}")[:80]
        paths = write_package_files(package, slug)

        ceo_feed["feed"].append({
            "opportunityId": opportunity["id"],
            "title": opportunity["title"],
            "organisation": opportunity["organisation"],
            "status": package["status"],
            "qualificationVerdict": package["qualification"]["verdict"],
            "qualificationScore": package["qualification"]["weightedScore"],
            **paths,
        })
        processed_index["processed"][opportunity["id"]] = {
            "datePrepared": TODAY,
            "status": package["status"],
            **paths,
        }
        prepared.append(package)
        print(f"  {opportunity['id']}: {opportunity['title']} -> confidence {package['confidenceScore']}/100 -> {package['status']}")

    backfilled = []
    for opportunity in backfill_candidates:
        pipeline_entry = pipeline_by_ref.get(opportunity["id"])
        crm_entry = crm_by_org.get(opportunity["organisation"])
        service_recommendation = service_recommendations.get(opportunity["id"])
        ai_entry = find_account_intelligence_entry(opportunity["organisation"], ai_feed)
        package = build_package(opportunity, pipeline_entry, crm_entry, bank, rate_card, service_recommendation, ai_entry,
                                 qualification_config, proposal_content_library)

        slug = slugify(f"{opportunity['id']}-{opportunity['organisation']}-{opportunity['title']}")[:80]
        paths = write_package_files(package, slug)

        # Only add the missing path fields - never overwrite a status the
        # founder may already have acted on just because it's being
        # repaired today. setdefault, not a plain assignment, for the
        # same reason — qualificationVerdict/qualificationScore are new
        # fields older feed entries lack, but a founder-visible value
        # already present must never be silently replaced.
        processed_index["processed"][opportunity["id"]].update(paths)
        feed_entry = feed_by_id.get(opportunity["id"])
        if feed_entry is not None:
            feed_entry.update(paths)
            feed_entry.setdefault("qualificationVerdict", package["qualification"]["verdict"])
            feed_entry.setdefault("qualificationScore", package["qualification"]["weightedScore"])
        backfilled.append(opportunity)
        print(f"  (backfill) {opportunity['id']}: {opportunity['title']} -> regenerated missing proposal files")

    save_json(CEO_FEED_PATH, ceo_feed)
    save_json(PROCESSED_INDEX_PATH, processed_index)

    report_path = OUTPUT_DIR / f"{TODAY}-sales-director-report.md"
    report_lines = [
        "# Sales Director — Daily Preparation Report",
        "",
        f"**Date:** {TODAY}",
        f"**Packages prepared:** {len(prepared)}",
        f"**Packages repaired (missing proposal files backfilled):** {len(backfilled)}",
        "",
    ]
    for p in prepared:
        report_lines.append(f"- **{p['title']}** ({p['organisation']}) — {p['confidenceScore']}/100 — {p['status']}")
    for o in backfilled:
        report_lines.append(f"- (backfill) **{o['title']}** ({o['organisation']})")
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n{len(prepared)} packages prepared, {len(backfilled)} repaired. Report: {report_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
