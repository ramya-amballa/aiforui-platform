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
REGULATORY_FRAMEWORK_ANNEXES_PATH = TEMPLATES_DIR / "regulatory-framework-annexes.json"
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


RISK_TABLE_HEADER = ("| # | Risk | Likelihood (1-5) | Impact (1-5) | Risk Rating | Owner | Mitigation | Target Closure | Status |\n"
                     "|---|---|---|---|---|---|---|---|---|")


def _risk_table_rows(risks, empty_message):
    """AOS Sprint 24 — Quality Elevation. Shared table format for every
    risk source feeding a Risk Register — company-specific (Account
    Intelligence) and framework-standard (regulatory-framework-annexes.json)
    rows read identically, scored against the same Risk Scoring
    Methodology (see the template's own appendix), never a second,
    inconsistent register format. Likelihood, Impact, Risk Rating,
    Owner, Mitigation and Target Closure are always left blank — real
    engagement judgement, never invented."""
    if not risks:
        return f"{RISK_TABLE_HEADER}\n| — | {empty_message} | | | | | | | |"
    lines = [RISK_TABLE_HEADER]
    for i, r in enumerate(risks, start=1):
        lines.append(f"| {i} | {r['risk']} — {r['why']} | {{LIKELIHOOD}} | {{IMPACT}} | {{RISK_RATING}} | "
                      f"{{OWNER}} | {{MITIGATION}} | {{TARGET_CLOSURE}} | Open |")
    return "\n".join(lines)


def risk_register_rows(ai_entry):
    risks = (ai_entry or {}).get("governanceRisks", [])
    return _risk_table_rows(risks, "Not enough signal yet — to be identified during Discovery.")


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


def select_regulatory_framework(opportunity, framework_config):
    """AOS Sprint 23 — Engagement Templates. Reuses the opportunity's
    own real domainTags (the identical field service-mapping's
    determine_proposal_template() already selects a proposal template
    from — never a second, independent detection rule) against
    frameworkPriority's stable order, so an opportunity carrying more
    than one recognised tag resolves to one answer, deterministically.
    None when no recognised tag is present — the caller falls back to
    the general ADGL default, never an invented framework."""
    domain_tags = set((opportunity or {}).get("domainTags", []))
    frameworks = framework_config.get("frameworks", {})
    for key in framework_config.get("frameworkPriority", []):
        if key in domain_tags and key in frameworks:
            return key
    return None


def regulatory_framework_label(framework_key, framework_config):
    frameworks = framework_config.get("frameworks", {})
    if framework_key and framework_key in frameworks:
        return frameworks[framework_key]["frameworkLabel"]
    default = frameworks.get("AI Deployment Governance (ADGL)")
    return default["frameworkLabel"] if default else "General AI Governance"


def regulatory_framework_discovery_questions(framework_key, framework_config):
    frameworks = framework_config.get("frameworks", {})
    key = framework_key if framework_key in frameworks else "AI Deployment Governance (ADGL)"
    questions = frameworks.get(key, {}).get("discoveryQuestions", [])
    if not questions:
        return "- Not enough signal yet — no framework-specific questions on record."
    return "\n".join(f"- {q}" for q in questions)


def regulatory_framework_seed_risks(framework_key, framework_config):
    frameworks = framework_config.get("frameworks", {})
    key = framework_key if framework_key in frameworks else "AI Deployment Governance (ADGL)"
    risks = frameworks.get(key, {}).get("riskSeedRisks", [])
    return _risk_table_rows(risks, "Not enough signal yet — no framework-specific starting risks on record.")


def regulatory_framework_reporting_note(framework_key, framework_config):
    frameworks = framework_config.get("frameworks", {})
    key = framework_key if framework_key in frameworks else "AI Deployment Governance (ADGL)"
    return frameworks.get(key, {}).get("reportingNote", "Not enough signal yet — no framework-specific reporting guidance on record.")


def build_placeholders(pipeline_entry, opportunity, ai_entry, service_recommendation, bank, framework_config=None):
    framework_config = framework_config or {}
    company = (ai_entry or {}).get("companyProfile", {})
    framework_key = select_regulatory_framework(opportunity, framework_config)
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
        "{{REGULATORY_FRAMEWORK_LABEL}}": regulatory_framework_label(framework_key, framework_config),
        "{{REGULATORY_FRAMEWORK_DISCOVERY_QUESTIONS}}": regulatory_framework_discovery_questions(framework_key, framework_config),
        "{{REGULATORY_FRAMEWORK_SEED_RISKS}}": regulatory_framework_seed_risks(framework_key, framework_config),
        "{{REGULATORY_FRAMEWORK_REPORTING_NOTE}}": regulatory_framework_reporting_note(framework_key, framework_config),
    }


def render_artifact(template_filename, placeholders):
    template_path = TEMPLATES_DIR / template_filename
    text = template_path.read_text(encoding="utf-8")
    for key, value in placeholders.items():
        text = text.replace(key, str(value))
    return text


def build_delivery_kit(pipeline_entry, opportunity, ai_entry, service_recommendation, bank, delivery_log,
                        framework_config=None):
    organisation = pipeline_entry["organisation"]
    placeholders = build_placeholders(pipeline_entry, opportunity, ai_entry, service_recommendation, bank, framework_config)
    phase, notes = engagement_phase(organisation, delivery_log)

    artifacts = {
        suffix: render_artifact(template_filename, placeholders)
        for template_filename, suffix, _label in ARTIFACT_SPECS
    }

    feed_entry = {
        "organisation": organisation,
        "engagementRef": placeholders["{{ENGAGEMENT_REF}}"],
        "primaryService": placeholders["{{PRIMARY_SERVICE}}"],
        "regulatoryFramework": placeholders["{{REGULATORY_FRAMEWORK_LABEL}}"],
        "phase": phase,
        "noteCount": len(notes),
        "generatedDate": TODAY,
        "kitPath": None,  # filled in by generate.py once the directory path is known
    }
    return artifacts, feed_entry
