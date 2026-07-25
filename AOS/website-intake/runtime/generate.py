#!/usr/bin/env python3
"""
Website Intake Runtime — execution mode

Usage:
    python3 generate.py

Reads every raw enquiry submission JSON file in runtime/inbox/ (written
by the website's contact-form API route — see
../website-intake-model.md's "How a Submission Reaches This Runtime"
section for the exact schema and the connector-ready delivery
mechanism). For each one, in order:

  1. Generates a unique, deterministic Lead ID.
  2. Classifies the lead (ADGL enquiry / AI Governance Advisory / AI
     Risk Assessment / Fractional Consulting / Training / Workshop /
     Partnership / Speaking / Unknown).
  3. Estimates qualification (probability, strategic value, revenue
     potential, urgency, industry, geography — organisation size is
     always "Unknown", since the form collects nothing that could
     support even a heuristic guess at it).
  4. Builds a real demand-intelligence/runtime/inbox/-shaped record and
     hands off to ingest.py (subprocess, exactly as the Orchestrator
     itself invokes every employee) — the SAME relevance filter,
     scoring, classification and routing to Revenue Hunter's
     pipeline.json / CRM's company-intelligence.json that every other
     source already goes through. This runtime does not re-implement
     any of that.
  5. Guarantees a CRM record exists for the organisation even when
     ingest.py's own classification-conditional routing doesn't create
     one (see ensure_crm_record()) — a self-initiated website enquiry
     is always worth tracking, unlike an auto-collected scraped
     posting.
  6. Invokes Revenue Hunter's and the Service Mapping Engine's own
     generate.py (subprocess) so the new opportunity is admitted to the
     pipeline and mapped to a recommended service the same day, not
     one cycle behind — both scripts are already idempotent (their own
     processed-index files), so calling them an extra time mid-day is
     safe and changes nothing for opportunities they've already
     handled.
  7. Writes a Sales Package (recommended service, proposal template,
     discovery call agenda, follow-up tasks) and a CEO Advisor feed
     entry.

Never re-implements Demand Intelligence's relevance/scoring/
classification, Revenue Hunter's scoring, CRM's schema, or the Service
Mapping Engine's decision tables — every one of those is invoked as
its own already-built script, exactly as documented above.

No email is ever sent from this script — "no emails are to be sent
automatically" is a hard constraint; every output is a file on disk.

Idempotent: raw submission files are moved to runtime/processed/ after
handling, so a re-run never double-processes the same submission — the
same convention ingest.py itself already uses for its own inbox.
"""

import hashlib
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
WEBSITE_INTAKE_DIR = RUNTIME_DIR.parent
AOS_DIR = WEBSITE_INTAKE_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_DIR = RUNTIME_DIR / "config"
INBOX_DIR = RUNTIME_DIR / "inbox"
PROCESSED_DIR = RUNTIME_DIR / "processed"
OUTPUT_DIR = RUNTIME_DIR / "output"
LOGS_DIR = RUNTIME_DIR / "logs"
LEADS_PATH = WEBSITE_INTAKE_DIR / "leads.json"

DEMAND_INTELLIGENCE_INBOX = AOS_DIR / "demand-intelligence" / "runtime" / "inbox"
OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "demand-intelligence" / "opportunity-schema.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
SERVICE_RECOMMENDATIONS_PATH = AOS_DIR / "service-mapping" / "service-recommendations.json"

INGEST_SCRIPT = AOS_DIR / "demand-intelligence" / "runtime" / "ingest.py"
REVENUE_HUNTER_SCRIPT = AOS_DIR / "revenue-hunter" / "runtime" / "generate.py"
SERVICE_MAPPING_SCRIPT = AOS_DIR / "service-mapping" / "runtime" / "generate.py"

TODAY = date.today()
RUN_STARTED = datetime.now(timezone.utc)

LEAD_ID_MARKER = "AOS Website Intake — leadId="

DEFAULT_LEADS = {
    "schema": {
        "leadId": "string — unique, content-derived, immutable once assigned",
        "dateReceived": "string — ISO 8601 date",
        "name": "string", "email": "string", "organisation": "string", "role": "string or null",
        "message": "string — raw submission text, unedited",
        "sourcePage": "string — contact, start-a-conversation, adgl, opera, or selected-engagement-areas",
        "leadClassification": "string — one of website-intake-config.json's leadClassifications",
        "qualification": {
            "probability": "number 0-10", "strategicValue": "number 0-10", "revenuePotential": "number 0-10",
            "urgency": "string — High, Medium, or Low",
            "industry": "string — best-effort keyword inference from the message, or 'Not specified'",
            "geography": "string — best-effort keyword inference from the message, or 'Not specified'",
            "organisationSize": "string — always 'Unknown'; the form collects nothing that could support even a heuristic guess",
        },
        "opportunityId": "string or null — the demand-intelligence/opportunity-schema.json id this lead became, once ingest.py has processed it",
        "salesPackage": {
            "crmRecordExists": "boolean",
            "recommendedService": "string or null — from service-mapping/service-recommendations.json, once mapped",
            "recommendedProposalTemplate": "string or null",
            "discoveryCallAgenda": "array of strings",
            "followUpTasks": "array of strings",
        },
    },
    "leads": {},
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


def _matches(text, keyword):
    pattern = r"\b" + re.escape(keyword.lower()) + r"s?\b"
    return re.search(pattern, (text or "").lower()) is not None


def any_keyword_matches(text, keywords):
    return any(_matches(text, kw) for kw in keywords)


# --------------------------------------------------------------------------
# 1. Lead ID
# --------------------------------------------------------------------------

def generate_lead_id(raw):
    basis = "|".join([raw.get("email", ""), raw.get("submittedAt", ""), raw.get("sourcePage", ""),
                       raw.get("message", "")])
    return "lead-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------
# 2. Lead Classification
# --------------------------------------------------------------------------

def classify_lead(raw, config):
    source_page = (raw.get("sourcePage") or "").strip().lower()
    text = f"{raw.get('message', '')}"

    if source_page in config["sourcePageClassification"]:
        return config["sourcePageClassification"][source_page], f"sourcePage={source_page}"

    for classification, keywords in config["classificationKeywords"].items():
        if classification == "_note":
            continue
        if any_keyword_matches(text, keywords):
            return classification, f"keyword match for {classification}"

    return "Unknown", "no sourcePage or keyword signal"


# --------------------------------------------------------------------------
# 3. Qualification
# --------------------------------------------------------------------------

REVENUE_POTENTIAL_BY_CLASSIFICATION = {
    "ADGL enquiry": 7, "AI Governance Advisory": 6, "AI Risk Assessment": 6,
    "Fractional Consulting": 8, "Training": 4, "Workshop": 4,
    "Partnership": 5, "Speaking": 3, "Unknown": 4,
}
ALIGNMENT_BY_CLASSIFICATION = {
    "ADGL enquiry": 8, "AI Governance Advisory": 8, "AI Risk Assessment": 8, "Fractional Consulting": 8,
    "Training": 6, "Workshop": 6, "Partnership": 6, "Speaking": 5, "Unknown": 4,
}


def estimate_urgency(message, config):
    if any_keyword_matches(message, config["urgencyKeywords"]["High"]):
        return "High"
    if any_keyword_matches(message, config["urgencyKeywords"]["Medium"]):
        return "Medium"
    return "Low"


def estimate_industry(message, organisation, config):
    text = f"{message} {organisation}"
    for industry, keywords in config["industryKeywords"].items():
        if industry == "_note":
            continue
        if any_keyword_matches(text, keywords):
            return industry, "keyword-inferred"
    return "Not specified", "not specified"


def estimate_geography(message, config):
    for geography, keywords in config["geographyKeywords"].items():
        if geography == "_note":
            continue
        if any_keyword_matches(message, keywords):
            return geography, "keyword-inferred"
    return "Not specified", "not specified"


def estimate_qualification(raw, lead_classification, config):
    message = raw.get("message", "")
    urgency = estimate_urgency(message, config)
    industry, industry_basis = estimate_industry(message, raw.get("organization", ""), config)
    geography, geography_basis = estimate_geography(message, config)

    defaults = config["qualificationDefaults"]
    probability = defaults["probabilityOfWinningBase"]
    word_count = len(message.split())
    if word_count >= 40:
        probability += 1
    elif word_count < 10:
        probability -= 1
    probability = max(0, min(10, probability))

    strategic_value = defaults["strategicValueBase"]
    source_page = (raw.get("sourcePage") or "").strip().lower()
    if source_page in ("adgl", "opera"):
        strategic_value += 3
    elif lead_classification in ("ADGL enquiry", "AI Governance Advisory"):
        strategic_value += 2
    strategic_value = max(0, min(10, strategic_value))

    revenue_potential = REVENUE_POTENTIAL_BY_CLASSIFICATION.get(lead_classification, 4)

    return {
        "probability": probability,
        "strategicValue": strategic_value,
        "revenuePotential": revenue_potential,
        "urgency": urgency,
        "industry": industry,
        "industryBasis": industry_basis,
        "geography": geography,
        "geographyBasis": geography_basis,
        "organisationSize": "Unknown",
    }


URGENCY_TIME_REQUIRED = {"High": 8, "Medium": 5, "Low": 3}


def build_opportunity_scores(lead_classification, qualification, raw, config):
    defaults = config["qualificationDefaults"]
    source_page = (raw.get("sourcePage") or "").strip().lower()

    return {
        "expectedRevenue": qualification["revenuePotential"],
        "probabilityOfWinning": qualification["probability"],
        "strategicValue": qualification["strategicValue"],
        "relationshipValue": defaults["relationshipValue"],
        "timeRequired": URGENCY_TIME_REQUIRED.get(qualification["urgency"], 5),
        "geography": 8 if qualification["geography"] != "Not specified" else 6,
        "remoteCompatibility": defaults["remoteCompatibility"],
        "alignmentAIforUIServices": ALIGNMENT_BY_CLASSIFICATION.get(lead_classification, 4),
        "alignmentADGL": 8 if (lead_classification == "ADGL enquiry" or source_page == "adgl") else 3,
        "alignmentOPERA": 8 if source_page == "opera" else (5 if lead_classification == "AI Governance Advisory" else 3),
        "longTermRelationshipPotential": defaults["longTermRelationshipPotential"],
    }


# --------------------------------------------------------------------------
# 4. Build the demand-intelligence inbox record and hand off to ingest.py
# --------------------------------------------------------------------------

def organisation_from(raw):
    organisation = (raw.get("organization") or "").strip()
    if organisation:
        return organisation
    email = raw.get("email", "")
    if "@" in email:
        domain = email.split("@", 1)[1].strip()
        if domain:
            return domain
    return "Individual Enquiry"


def build_opportunity_input_record(raw, lead_id, lead_classification, qualification, config):
    domain_tags = config["domainTagsByClassification"].get(lead_classification, [])
    source_category = config["sourceCategoryByClassification"].get(
        lead_classification, config["sourceCategoryByClassification"]["default"]
    )
    scores = build_opportunity_scores(lead_classification, qualification, raw, config)
    message = raw.get("message", "")
    scoped_engagement = (
        lead_classification in ("ADGL enquiry", "AI Risk Assessment", "Fractional Consulting")
        and len(message.split()) >= 15
    )

    return {
        "source": "Website",
        "sourceCategory": source_category,
        "title": f"Website Enquiry — {lead_classification}",
        "organisation": organisation_from(raw),
        "description": message,
        "url": None,
        "location": "Not specified",
        "remote": True,
        "domainTags": domain_tags,
        "scores": scores,
        "scopedEngagement": scoped_engagement,
        "recurrencePattern": "none",
        "notes": f"{LEAD_ID_MARKER}{lead_id}",
    }


def run_script(script_path, fh):
    """Invokes another employee's own script as its own subprocess —
    the same invocation pattern orchestrator.py uses for every
    employee, reused here since Website Intake hands off to three of
    them within its own run. Never imported, never called in-process,
    so a crash in one can never reach this script."""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent),
            capture_output=True, text=True, timeout=120,
        )
        output = (result.stdout or "") + (result.stderr or "")
        fh.write(f"--- {script_path.name} ---\n{output}\n")
        return result.returncode, output
    except subprocess.TimeoutExpired:
        fh.write(f"--- {script_path.name} --- TIMEOUT\n")
        return None, "timed out"


def find_opportunity_id_for_lead(lead_id):
    schema_data = load_json(OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    marker = f"{LEAD_ID_MARKER}{lead_id}"
    for opp in schema_data.get("opportunities", []):
        if opp.get("notes") == marker:
            return opp["id"]
    return None


# --------------------------------------------------------------------------
# 5. Guarantee a CRM record — mirrors ingest.py's route_to_crm() "new
# company" defaults exactly, only invoked here for the gap where
# classification didn't already route one (Follow Recruiter/
# Relationship Building/Partnership/Immediate Proposal only). A
# self-initiated website enquiry is always worth tracking, unlike an
# auto-collected posting.
# --------------------------------------------------------------------------

def ensure_crm_record(organisation, lead_id, lead_classification, domain_tags):
    crm_data = load_json(CRM_PATH, {"companies": []})
    existing = next((c for c in crm_data["companies"] if c.get("companyName") == organisation), None)
    if existing is not None:
        return False  # already exists — created either by ingest.py's own routing, or a prior lead

    crm_data.setdefault("companies", []).append({
        "companyName": organisation,
        "industry": "Not specified",
        "aiMaturity": "Unknown",
        "regulations": domain_tags,
        "existingRelationship": "none",
        "recruiter": None,
        "previousApplications": [],
        "tailoredPositioning": "",
        "lastTouch": TODAY.isoformat(),
        "relationshipTemperature": "warm",
        "nextFollowUpDue": (TODAY + timedelta(days=10)).isoformat(),
        "outreachHistory": [{
            "date": TODAY.isoformat(), "channel": "Website",
            "summary": f"Website enquiry received: {lead_classification} — lead {lead_id}",
        }],
        "notes": "",
    })
    save_json(CRM_PATH, crm_data)
    return True


# --------------------------------------------------------------------------
# 6 & 7. Sales Package + CEO Advisor notification
# --------------------------------------------------------------------------

def build_sales_package(lead_classification, opportunity_id, qualification, crm_created, config):
    service_recommendations = load_json(SERVICE_RECOMMENDATIONS_PATH, {"recommendations": {}})
    recommendation = service_recommendations.get("recommendations", {}).get(opportunity_id) if opportunity_id else None

    agenda = list(config["discoveryCallAgendaByClassification"].get(
        lead_classification, config["discoveryCallAgendaByClassification"]["default"]
    ))
    follow_up_tasks = list(config["followUpTasksByUrgency"].get(qualification["urgency"], []))

    return {
        "crmRecordExists": True,  # ensure_crm_record() guarantees this before this is ever called
        "recommendedService": recommendation.get("primaryService") if recommendation else None,
        "recommendedProposalTemplate": recommendation.get("recommendedProposalTemplate") if recommendation else None,
        "discoveryCallAgenda": agenda,
        "followUpTasks": follow_up_tasks,
    }


def write_ceo_advisor_feed(new_leads):
    feed_path = OUTPUT_DIR / "ceo-advisor-feed.json"
    feed = {
        "schema": {
            "leadId": "string", "organisation": "string", "leadClassification": "string",
            "urgency": "string — High, Medium, or Low — the only field 09-CEO-Advisor normalises",
            "opportunityId": "string or null",
        },
        "feed": [
            {
                "leadId": lead["leadId"], "organisation": lead["organisation"],
                "leadClassification": lead["leadClassification"], "urgency": lead["qualification"]["urgency"],
                "opportunityId": lead["opportunityId"],
            }
            for lead in new_leads
        ],
    }
    OUTPUT_DIR.mkdir(exist_ok=True)
    save_json(feed_path, feed)


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def render_report(new_leads):
    lines = [
        "# Website Intake Report",
        "",
        f"**Date:** {TODAY.isoformat()}",
        f"**New leads this run:** {len(new_leads)}",
        "",
    ]
    if not new_leads:
        lines.append("_No new website submissions this run._")
        return "\n".join(lines) + "\n"

    lines.append("| Lead ID | Organisation | Classification | Urgency | Opportunity ID | Recommended Service |")
    lines.append("|---|---|---|---|---|---|")
    for lead in new_leads:
        lines.append(f"| {lead['leadId']} | {lead['organisation']} | {lead['leadClassification']} | "
                      f"{lead['qualification']['urgency']} | {lead['opportunityId'] or 'pending'} | "
                      f"{lead['salesPackage']['recommendedService'] or 'pending'} |")

    lines += ["", "## Follow-Up Tasks", ""]
    for lead in new_leads:
        if lead["salesPackage"]["followUpTasks"]:
            lines.append(f"- **{lead['organisation']}** ({lead['leadId']}): " +
                         "; ".join(lead["salesPackage"]["followUpTasks"]))

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    LOGS_DIR.mkdir(exist_ok=True)
    log_path = LOGS_DIR / f"{TODAY.isoformat()}-{RUN_STARTED.strftime('%H%M%S')}-website-intake.log"
    fh = open(log_path, "w", encoding="utf-8")

    config = load_json(CONFIG_DIR / "website-intake-config.json")
    leads_store = load_json(LEADS_PATH, DEFAULT_LEADS)
    leads_store.setdefault("leads", {})

    raw_submissions, source_files = [], []
    for path in sorted(INBOX_DIR.iterdir()):
        if path.name == ".gitkeep" or path.is_dir():
            continue
        try:
            raw_submissions.append(json.loads(path.read_text(encoding="utf-8")))
            source_files.append(path)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  skip {path.name}: {exc}", file=sys.stderr)
            fh.write(f"skip {path.name}: {exc}\n")

    if not raw_submissions:
        print("No new website submissions in runtime/inbox/. Nothing to do.")
        fh.write("No new website submissions.\n")
        fh.close()
        return 0

    new_leads = []
    for raw in raw_submissions:
        lead_id = generate_lead_id(raw)
        lead_classification, reason = classify_lead(raw, config)
        qualification = estimate_qualification(raw, lead_classification, config)
        organisation = organisation_from(raw)
        domain_tags = config["domainTagsByClassification"].get(lead_classification, [])

        opportunity_input = build_opportunity_input_record(raw, lead_id, lead_classification, qualification, config)
        DEMAND_INTELLIGENCE_INBOX.mkdir(exist_ok=True)
        inbox_path = DEMAND_INTELLIGENCE_INBOX / f"{TODAY.isoformat()}-website-lead-{lead_id}.json"
        save_json(inbox_path, [opportunity_input])

        print(f"  {lead_id}: {organisation} -> {lead_classification} ({reason})")
        fh.write(f"{lead_id}: {organisation} -> {lead_classification} ({reason})\n")

        # Hand off to Demand Intelligence's own ingestion — relevance
        # filter, scoring, classification, routing to Revenue
        # Hunter/CRM, all unchanged and untouched by this script.
        run_script(INGEST_SCRIPT, fh)

        opportunity_id = find_opportunity_id_for_lead(lead_id)

        # Guarantee a CRM record regardless of ingest.py's own
        # classification-conditional routing.
        crm_created = ensure_crm_record(organisation, lead_id, lead_classification, domain_tags)

        # Same-day admission to Revenue Hunter's pipeline and the
        # Service Mapping Engine's recommendations — both scripts are
        # already idempotent, so calling them now (in addition to their
        # own regularly scheduled Orchestrator step) is safe.
        run_script(REVENUE_HUNTER_SCRIPT, fh)
        run_script(SERVICE_MAPPING_SCRIPT, fh)

        sales_package = build_sales_package(lead_classification, opportunity_id, qualification, crm_created, config)

        lead_record = {
            "leadId": lead_id,
            "dateReceived": TODAY.isoformat(),
            "name": raw.get("name", ""),
            "email": raw.get("email", ""),
            "organisation": organisation,
            "role": raw.get("role") or None,
            "message": raw.get("message", ""),
            "sourcePage": raw.get("sourcePage", "contact"),
            "leadClassification": lead_classification,
            "qualification": qualification,
            "opportunityId": opportunity_id,
            "salesPackage": sales_package,
        }
        leads_store["leads"][lead_id] = lead_record
        new_leads.append(lead_record)

    save_json(LEADS_PATH, leads_store)
    write_ceo_advisor_feed(new_leads)

    OUTPUT_DIR.mkdir(exist_ok=True)
    report = render_report(new_leads)
    (OUTPUT_DIR / f"{TODAY.isoformat()}-website-intake-report.md").write_text(report, encoding="utf-8")
    (OUTPUT_DIR / "website-intake-report.md").write_text(report, encoding="utf-8")

    PROCESSED_DIR.mkdir(exist_ok=True)
    for path in source_files:
        path.rename(PROCESSED_DIR / path.name)

    summary = f"\n{len(new_leads)} website lead(s) processed."
    print(summary)
    fh.write(summary + "\n")
    fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
