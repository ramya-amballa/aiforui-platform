"""
Delivery Intelligence Engine (AOS Sprint 17 — Consulting Delivery Engine)

Optimises for consulting revenue past the proposal, not engineering
elegance: a signed engagement is the real trigger — Revenue Hunter's
own `08-Revenue-Hunter/pipeline.json` `stage == "won"` (never a second,
independently-invented "signed" flag) — for generating the core
delivery artifacts every AI Governance engagement needs: kickoff
agenda, discovery questionnaire, AI readiness assessment workbook,
governance roadmap, RACI, risk register, workshop materials, executive
status report, steering committee pack, and project closure report.

Every artifact is rendered from `templates/delivery/`'s own reusable,
ADGL/OPERA-aligned templates (the durable IP every engagement
compounds) — this engine only fills in the placeholders it has real
evidence for (client name, date, reference, primary service, industry,
regulatory environment, decision-maker titles, governance risks, the
ADGL/OPERA phase names themselves — all reused verbatim from Account
Intelligence, Service Mapping and practitioner-bank.json). Every
placeholder for something AOS cannot know (an actual meeting date, a
named attendee, a real workshop outcome) is deliberately left as a
`{{...}}` token for the founder to fill in during real delivery —
never invented.

Read-only with respect to every other employee's data. Writes only to
its own `output/delivery-kits/` and `delivery-intelligence-feed.json`.
`delivery-log.json` (engagement phase/status) is founder-maintained,
exactly like `relationship-profiles.json` and `touchpoint-log.json` —
this engine reads it, never writes it.
"""

import copy
import json
import re
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
DELIVERY_INTELLIGENCE_DIR = RUNTIME_DIR.parent
AOS_DIR = DELIVERY_INTELLIGENCE_DIR.parent
REPO_ROOT = AOS_DIR.parent

PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "demand-intelligence" / "opportunity-schema.json"
ACCOUNT_INTELLIGENCE_FEED_PATH = AOS_DIR / "account-intelligence" / "runtime" / "output" / "account-intelligence-feed.json"
SERVICE_RECOMMENDATIONS_PATH = AOS_DIR / "service-mapping" / "service-recommendations.json"
PRACTITIONER_BANK_PATH = AOS_DIR / "sales-director" / "runtime" / "config" / "practitioner-bank.json"

TEMPLATES_DIR = REPO_ROOT / "AOS" / "templates" / "delivery"
DELIVERY_LOG_PATH = DELIVERY_INTELLIGENCE_DIR / "delivery-log.json"
KITS_DIR = RUNTIME_DIR / "output" / "delivery-kits"
FEED_PATH = RUNTIME_DIR / "output" / "delivery-intelligence-feed.json"

TODAY = date.today().isoformat()
PREPARED_BY = "Ramya Amballa, Founder, AI for U&I"

# (template filename, output filename suffix, human label)
ARTIFACT_SPECS = [
    ("kickoff-agenda-template.md", "kickoff-agenda", "Kickoff Agenda"),
    ("discovery-questionnaire-template.md", "discovery-questionnaire", "Discovery Questionnaire"),
    ("ai-readiness-assessment-workbook-template.md", "readiness-assessment-workbook", "AI Readiness Assessment Workbook"),
    ("governance-roadmap-template.md", "governance-roadmap", "Governance Roadmap"),
    ("raci-template.md", "raci", "RACI"),
    ("risk-register-template.md", "risk-register", "Risk Register"),
    ("workshop-materials-template.md", "workshop-materials", "Workshop Materials"),
    ("executive-status-report-template.md", "executive-status-report", "Executive Status Report"),
    ("steering-committee-pack-template.md", "steering-committee-pack", "Steering Committee Pack"),
    ("project-closure-report-template.md", "project-closure-report", "Project Closure Report"),
]

DEFAULT_DELIVERY_LOG = {
    "schema": {
        "organisation": "string — key",
        "phase": "string — Not started | Kickoff | Discovery | Assessment | Roadmap Delivered | In Delivery | Steering Committee | Closed",
        "notes": "array of {date, note} — founder-entered progress notes",
    },
    "engagements": {},
}

PHASE_ORDER = ["Not started", "Kickoff", "Discovery", "Assessment", "Roadmap Delivered",
               "In Delivery", "Steering Committee", "Closed"]


def load_json(path, default=None):
    if not path.exists():
        if default is not None:
            return copy.deepcopy(default)
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def won_engagements(pipeline_data):
    """Revenue Hunter's own stage field, reused verbatim as the real,
    deterministic 'signed proposal' trigger — never a second,
    independently-invented flag."""
    return [e for e in pipeline_data.get("pipeline", []) if e.get("stage") == "won"]


def find_opportunity(source_ref, opportunity_schema):
    if not source_ref:
        return None
    for opp in opportunity_schema.get("opportunities", []):
        if opp.get("id") == source_ref:
            return opp
    return None


def find_account_intelligence_entry(organisation, ai_feed):
    for entry in ai_feed.get("briefs", []):
        if entry.get("organisation") == organisation:
            return entry
    return None


def find_service_recommendation(opportunity_id, service_recommendations):
    if not opportunity_id:
        return None
    return service_recommendations.get(opportunity_id)


def engagement_phase(organisation, delivery_log):
    """Read-only — the founder's own recorded phase, never inferred.
    'Not started' (distinct from any real phase) when no log entry
    exists yet for this organisation."""
    entry = delivery_log.get("engagements", {}).get(organisation)
    if not entry:
        return "Not started", []
    return entry.get("phase", "Not started"), entry.get("notes", [])


# --------------------------------------------------------------------------
# Placeholder assembly — every value here is a real, already-computed
# fact from another employee, or an honest "Not specified"/"Not enough
# signal yet". Never a fabricated project detail.
# --------------------------------------------------------------------------

def governance_risks_list(ai_entry):
    risks = (ai_entry or {}).get("governanceRisks", [])
    if not risks:
        return "- Not enough signal yet — to be identified during Discovery."
    return "\n".join(f"- **{r['risk']}** — {r['why']}" for r in risks)


def risk_register_rows(ai_entry):
    risks = (ai_entry or {}).get("governanceRisks", [])
    if not risks:
        return ("| # | Risk | Likelihood | Impact | Owner | Mitigation | Status |\n"
                "|---|---|---|---|---|---|---|\n"
                "| — | Not enough signal yet — to be identified during Discovery. | | | | | |")
    lines = ["| # | Risk | Likelihood | Impact | Owner | Mitigation | Status |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(risks, start=1):
        lines.append(f"| {i} | {r['risk']} — {r['why']} | {{LIKELIHOOD}} | {{IMPACT}} | {{OWNER}} | {{MITIGATION}} | Open |")
    return "\n".join(lines)


def primary_service(service_recommendation, ai_entry):
    if service_recommendation and not service_recommendation.get("notApplicable"):
        return service_recommendation.get("primaryService") or "Not specified"
    services = (ai_entry or {}).get("serviceFit", [])
    return services[0]["service"] if services else "Not specified"


def recommended_scope(service_recommendation, opportunity):
    if service_recommendation and not service_recommendation.get("notApplicable"):
        engagement_type = service_recommendation.get("recommendedEngagementType") or "Not specified"
        size = service_recommendation.get("estimatedProjectSize") or "Not specified"
        return f"{engagement_type} ({size})"
    if opportunity:
        return opportunity.get("title", "Not specified")
    return "Not specified"


def decision_maker_titles_text(ai_entry):
    titles = (ai_entry or {}).get("decisionMakerTitles", [])
    return ", ".join(titles) if titles else "Not specified"


def build_placeholders(pipeline_entry, opportunity, ai_entry, service_recommendation, bank):
    company = (ai_entry or {}).get("companyProfile", {})
    return {
        "{{CLIENT_NAME}}": pipeline_entry["organisation"],
        "{{DATE}}": TODAY,
        "{{ENGAGEMENT_REF}}": pipeline_entry.get("id") or pipeline_entry.get("sourceRef") or "Not specified",
        "{{PREPARED_BY}}": PREPARED_BY,
        "{{PRIMARY_SERVICE}}": primary_service(service_recommendation, ai_entry),
        "{{RECOMMENDED_SCOPE}}": recommended_scope(service_recommendation, opportunity),
        "{{INDUSTRY}}": company.get("industry", "Not specified"),
        "{{REGULATORY_ENVIRONMENT}}": company.get("regulatoryEnvironment", "Not specified"),
        "{{DECISION_MAKER_TITLES}}": decision_maker_titles_text(ai_entry),
        "{{GOVERNANCE_RISKS_LIST}}": governance_risks_list(ai_entry),
        "{{RISK_REGISTER_ROWS}}": risk_register_rows(ai_entry),
        "{{ADGL_PHASES_LIST}}": ", ".join(bank.get("adglPhases", [])) or "Not specified",
        "{{OPERA_PHASES_LIST}}": ", ".join(bank.get("operaPhases", [])) or "Not specified",
    }


def render_artifact(template_filename, placeholders):
    template_path = TEMPLATES_DIR / template_filename
    text = template_path.read_text(encoding="utf-8")
    for key, value in placeholders.items():
        text = text.replace(key, str(value))
    return text


def build_delivery_kit(pipeline_entry, opportunity, ai_entry, service_recommendation, bank, delivery_log):
    organisation = pipeline_entry["organisation"]
    placeholders = build_placeholders(pipeline_entry, opportunity, ai_entry, service_recommendation, bank)
    phase, notes = engagement_phase(organisation, delivery_log)

    artifacts = {
        suffix: render_artifact(template_filename, placeholders)
        for template_filename, suffix, _label in ARTIFACT_SPECS
    }

    feed_entry = {
        "organisation": organisation,
        "engagementRef": placeholders["{{ENGAGEMENT_REF}}"],
        "primaryService": placeholders["{{PRIMARY_SERVICE}}"],
        "phase": phase,
        "noteCount": len(notes),
        "generatedDate": TODAY,
        "kitPath": None,  # filled in by generate.py once the directory path is known
    }
    return artifacts, feed_entry
