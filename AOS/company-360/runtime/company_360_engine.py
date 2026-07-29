"""
Company 360 Engine (AOS Sprint 19)

A pure read-only consolidator. AOS scattered per-organisation facts
across eight employees, each with its own field names and even its own
key field for "which company" (organisation / companyName / company).
Company 360 joins them into one view per organisation — it computes
nothing new, invents no fact, and reconciles no two independently-
computed numbers into a third. Where two employees genuinely compute
two different things that could be mistaken for the same fact (e.g.
Account Intelligence's overallPriority vs Reverse Job Hunt's
consultingPotentialEstimate — both "how big is this deal" when no real
pipeline record exists yet, from two different formulas), both are
shown side by side, labelled by the employee that produced them,
never averaged or merged.

Every organisation Company 360 knows about is one already known to
demand-intelligence/organisation-profiles.json — the broadest,
canonical per-organisation store every other employee's own
organisation string traces back to. Everything else is an optional,
read-only cross-reference: a company with no Account Intelligence
brief yet, no CRM record yet, or no pipeline entry yet still gets a
360 view, honestly showing what doesn't exist yet rather than omitting
the organisation.

Regenerated in full on every run — like Account Intelligence and
Reverse Job Hunt's own reports, not like Sales Director's proposals or
Delivery Intelligence's kits, there is nothing here the founder would
hand-edit, so there is nothing to protect from being overwritten.

Key-matching note: organisation-profiles.json, account-intelligence-
feed.json, reverse-job-hunt-feed.json, pipeline.json and delivery-
log.json all copy the identical `organisation` string end to end
(machine-written), so those are matched by exact string equality.
06-CRM's `companyName` and relationship-intelligence's `company` are
free-text fields the founder may enter separately, so those two are
matched via normalise() (lowercase + trim) instead — a purely internal
join key, never surfaced or persisted as a new canonical id.
"""

import copy
import json
import re
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
COMPANY_360_DIR = RUNTIME_DIR.parent
AOS_DIR = COMPANY_360_DIR.parent
REPO_ROOT = AOS_DIR.parent

ORGANISATION_PROFILES_PATH = AOS_DIR / "demand-intelligence" / "organisation-profiles.json"
OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "demand-intelligence" / "opportunity-schema.json"
ACCOUNT_INTELLIGENCE_FEED_PATH = AOS_DIR / "account-intelligence" / "runtime" / "output" / "account-intelligence-feed.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
RELATIONSHIP_PROFILES_PATH = AOS_DIR / "relationship-intelligence" / "relationship-profiles.json"
RELATIONSHIP_FEED_PATH = AOS_DIR / "relationship-intelligence" / "runtime" / "output" / "relationship-intelligence-feed.json"
REVERSE_JOB_HUNT_FEED_PATH = AOS_DIR / "reverse-job-hunt" / "runtime" / "output" / "reverse-job-hunt-feed.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
SERVICE_RECOMMENDATIONS_PATH = AOS_DIR / "service-mapping" / "service-recommendations.json"
DELIVERY_LOG_PATH = AOS_DIR / "delivery-intelligence" / "delivery-log.json"
DELIVERY_INTELLIGENCE_FEED_PATH = AOS_DIR / "delivery-intelligence" / "runtime" / "output" / "delivery-intelligence-feed.json"

PROFILES_DIR = RUNTIME_DIR / "output" / "company-profiles"
FEED_PATH = RUNTIME_DIR / "output" / "company-360-feed.json"

TODAY = date.today().isoformat()


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


def normalise(name):
    return (name or "").strip().lower()


# --------------------------------------------------------------------------
# Finders — one small, exact-purpose function per source, the same
# pattern every other employee already uses (each keeps its own finder
# rather than sharing one), because each source's match rule differs
# slightly (exact vs normalised, single entry vs list).
# --------------------------------------------------------------------------

def find_account_intelligence_entry(organisation, ai_feed):
    for entry in ai_feed.get("briefs", []):
        if entry.get("organisation") == organisation:
            return entry
    return None


def find_crm_entry(organisation, crm_data):
    target = normalise(organisation)
    for company in crm_data.get("companies", []):
        if normalise(company.get("companyName")) == target:
            return company
    return None


def find_relationship_people(organisation, relationship_feed):
    target = normalise(organisation)
    return [p for p in relationship_feed.get("people", []) if normalise(p.get("company")) == target]


def find_reverse_job_hunt_entry(organisation, rjh_feed):
    for entry in rjh_feed.get("strategies", []):
        if entry.get("organisation") == organisation:
            return entry
    return None


def find_pipeline_entries(organisation, pipeline_data):
    return [e for e in pipeline_data.get("pipeline", []) if e.get("organisation") == organisation]


def find_service_recommendations(organisation, opportunity_schema, service_recommendations):
    org_opportunity_ids = {
        opp["id"] for opp in opportunity_schema.get("opportunities", [])
        if opp.get("organisation") == organisation
    }
    return [
        rec for opp_id, rec in service_recommendations.items()
        if opp_id in org_opportunity_ids and not rec.get("notApplicable")
    ]


def find_delivery_engagement(organisation, delivery_log, delivery_feed):
    log_entry = delivery_log.get("engagements", {}).get(organisation)
    phase = log_entry.get("phase", "Not started") if log_entry else "Not started"
    feed_entry = next((e for e in delivery_feed.get("engagements", []) if e.get("organisation") == organisation), None)
    return {
        "phase": phase,
        "noteCount": len(log_entry.get("notes", [])) if log_entry else 0,
        "kitPath": feed_entry.get("kitPath") if feed_entry else None,
    }


# --------------------------------------------------------------------------
# Assembly — one dict per organisation, every field traceable back to
# the employee that computed it. No new score, verdict or label is
# invented here.
# --------------------------------------------------------------------------

def build_company_360(organisation, profile, ai_feed, crm_data, relationship_feed, rjh_feed,
                       pipeline_data, opportunity_schema, service_recommendations, delivery_log, delivery_feed):
    ai_entry = find_account_intelligence_entry(organisation, ai_feed)
    crm_entry = find_crm_entry(organisation, crm_data)
    people = find_relationship_people(organisation, relationship_feed)
    rjh_entry = find_reverse_job_hunt_entry(organisation, rjh_feed)
    pipeline_entries = find_pipeline_entries(organisation, pipeline_data)
    service_recs = find_service_recommendations(organisation, opportunity_schema, service_recommendations)
    delivery = find_delivery_engagement(organisation, delivery_log, delivery_feed)

    return {
        "organisation": organisation,
        "industry": profile.get("industry", "Not specified"),
        "region": profile.get("region", "Not specified"),
        "scale": profile.get("scale", "Not specified"),

        "demandIntelligence": {
            "overallDemandScore": profile.get("overallDemandScore", 0),
            "buyingReadinessScore": profile.get("buyingReadinessScore", 0),
            "buyingReadinessBand": profile.get("buyingReadinessBand", "Low"),
            "matchedCategories": profile.get("matchedCategories", []),
            "recommendedAction": profile.get("recommendedAction", "Not specified"),
            "recommendedActionReason": profile.get("recommendedActionReason", ""),
            "firstSeen": profile.get("firstSeen"), "lastSeen": profile.get("lastSeen"),
            "outreachHappened": profile.get("outreachHappened", False),
            "proposalCreated": profile.get("proposalCreated", False),
            "converted": profile.get("converted", False),
            "revenueGenerated": profile.get("revenueGenerated"),
        },

        "accountIntelligence": ({
            "executiveSummary": ai_entry.get("executiveSummary"),
            "deploymentStage": ai_entry.get("deploymentStage"),
            "governanceRisks": ai_entry.get("governanceRisks", []),
            "serviceFit": ai_entry.get("serviceFit", []),
            "decisionMakerTitles": ai_entry.get("decisionMakerTitles", []),
            "outreachStrategy": ai_entry.get("outreachStrategy"),
            "overallPriority": ai_entry.get("overallPriority"),
            "briefPath": ai_entry.get("briefPath"),
        } if ai_entry else None),

        "crm": ({
            "existingRelationship": crm_entry.get("existingRelationship", "none"),
            "relationshipTemperature": crm_entry.get("relationshipTemperature"),
            "recruiter": crm_entry.get("recruiter"),
            "previousApplicationCount": len(crm_entry.get("previousApplications", [])),
            "lastTouch": crm_entry.get("lastTouch"),
            "nextFollowUpDue": crm_entry.get("nextFollowUpDue"),
        } if crm_entry else None),

        "relationshipIntelligence": [
            {"person": p.get("person"), "role": p.get("role"), "healthScore": p.get("healthScore"),
             "healthBand": p.get("healthBand"), "risk": p.get("risk"), "reconnectRecommended": p.get("reconnectRecommended")}
            for p in people
        ],

        "reverseJobHunt": ({
            "entryPoint": rjh_entry.get("entryPoint"),
            "probabilityOfEngagement": rjh_entry.get("probabilityOfEngagement"),
            "consultingPotentialEstimate": rjh_entry.get("consultingPotentialEstimate"),
            "expectedConsultingRoi": rjh_entry.get("expectedConsultingRoi"),
            "campaignStatus": rjh_entry.get("campaignStatus"),
            "touchpointCount": rjh_entry.get("touchpointCount"),
        } if rjh_entry else None),

        "pipeline": [
            {"id": e.get("id"), "type": e.get("type"), "title": e.get("title"), "stage": e.get("stage"),
             "expectedRevenue": e.get("expectedRevenue"), "score": e.get("score"), "band": e.get("band")}
            for e in pipeline_entries
        ],

        "serviceMapping": [
            {"opportunityId": r.get("opportunityId"), "primaryService": r.get("primaryService"),
             "recommendedEngagementType": r.get("recommendedEngagementType"), "estimatedProjectSize": r.get("estimatedProjectSize")}
            for r in service_recs
        ],

        "deliveryIntelligence": delivery,
    }


# --------------------------------------------------------------------------
# Markdown — one printable 360 profile per organisation. Every "not on
# record" line is an honest gap, not an empty section silently dropped.
# --------------------------------------------------------------------------

def render_company_360_markdown(entry):
    org = entry["organisation"]
    di = entry["demandIntelligence"]
    lines = [
        f"# Company 360 — {org}",
        "",
        f"**Industry:** {entry['industry']}  ",
        f"**Region:** {entry['region']}  ",
        f"**Scale:** {entry['scale']}  ",
        f"**Generated:** {TODAY}",
        "",
        "---",
        "",
        "## Demand Intelligence (canonical source)",
        "",
        f"- **Buying readiness:** {di['buyingReadinessScore']}/100 ({di['buyingReadinessBand']})",
        f"- **Overall demand score:** {di['overallDemandScore']}/100",
        f"- **Matched categories:** {', '.join(di['matchedCategories']) or 'None'}",
        f"- **Recommended action (pipeline):** {di['recommendedAction']} — {di['recommendedActionReason']}",
        f"- **Outreach happened:** {di['outreachHappened']} | **Proposal created:** {di['proposalCreated']} | "
        f"**Converted:** {di['converted']} | **Revenue generated:** {di['revenueGenerated'] or 'Not yet'}",
        "",
    ]

    ai = entry["accountIntelligence"]
    lines += ["## Account Intelligence", ""]
    if ai:
        lines += [
            f"- **Executive summary:** {ai['executiveSummary']}",
            f"- **Deployment stage:** {ai['deploymentStage']}",
            f"- **Outreach strategy (first touch framing):** {ai['outreachStrategy']}",
            f"- **Overall priority:** {ai['overallPriority']}",
            f"- **Decision-maker titles:** {', '.join(ai['decisionMakerTitles']) or 'Not specified'}",
            "- **Governance risks:**",
        ]
        lines += [f"  - {r['risk']} — {r['why']}" for r in ai["governanceRisks"]] or ["  - None flagged"]
        lines += ["- **Service fit:**"]
        lines += [f"  - {s['service']} ({s['confidence']})" for s in ai["serviceFit"]] or ["  - None flagged"]
    else:
        lines += ["_No brief on record yet for this organisation._"]
    lines.append("")

    crm = entry["crm"]
    lines += ["## CRM (relationship record)", ""]
    if crm:
        lines += [
            f"- **Existing relationship:** {crm['existingRelationship']}",
            f"- **Relationship temperature:** {crm['relationshipTemperature'] or 'Not set'}",
            f"- **Recruiter:** {crm['recruiter'] or 'None'}",
            f"- **Previous applications on record:** {crm['previousApplicationCount']}",
            f"- **Last touch:** {crm['lastTouch'] or 'Not recorded'} | **Next follow-up due:** {crm['nextFollowUpDue'] or 'Not set'}",
        ]
    else:
        lines += ["_No CRM record yet for this organisation._"]
    lines.append("")

    people = entry["relationshipIntelligence"]
    lines += ["## Relationship Intelligence (individual contacts)", ""]
    if people:
        for p in people:
            lines.append(f"- **{p['person']}** ({p['role'] or 'role not specified'}) — health {p['healthScore']}/100 "
                          f"({p['healthBand']}), risk: {p['risk']}"
                          + (", reconnect recommended" if p["reconnectRecommended"] else ""))
    else:
        lines += ["_No individual contacts tracked yet for this organisation._"]
    lines.append("")

    rjh = entry["reverseJobHunt"]
    lines += ["## Reverse Job Hunt (BD campaign)", ""]
    if rjh:
        lines += [
            f"- **Entry point (channel):** {rjh['entryPoint']}",
            f"- **Probability of engagement:** {rjh['probabilityOfEngagement']}",
            f"- **Consulting potential estimate:** {rjh['consultingPotentialEstimate']} "
            f"(a separate, independently-derived estimate from Account Intelligence's Overall Priority above — not the same figure)",
            f"- **Expected consulting ROI:** {rjh['expectedConsultingRoi']}",
            f"- **Campaign status:** {rjh['campaignStatus']} | **Touchpoints logged:** {rjh['touchpointCount']}",
        ]
    else:
        lines += ["_No BD campaign strategy on record yet for this organisation._"]
    lines.append("")

    pipeline = entry["pipeline"]
    lines += ["## Revenue Hunter Pipeline History", ""]
    if pipeline:
        lines += [f"- **{p['id']}** — {p['title']} ({p['type']}) — stage: {p['stage']}, "
                   f"expected revenue: {p['expectedRevenue']}, score: {p['score']}/100 ({p['band']})" for p in pipeline]
    else:
        lines += ["_No pipeline entries yet for this organisation._"]
    lines.append("")

    service_recs = entry["serviceMapping"]
    lines += ["## Service Mapping Recommendations", ""]
    if service_recs:
        lines += [f"- {r['primaryService']} — {r['recommendedEngagementType']} ({r['estimatedProjectSize']}) "
                   f"[{r['opportunityId']}]" for r in service_recs]
    else:
        lines += ["_No mapped opportunities yet for this organisation._"]
    lines.append("")

    delivery = entry["deliveryIntelligence"]
    lines += [
        "## Delivery Intelligence",
        "",
        f"- **Phase:** {delivery['phase']}" + (f" ({delivery['noteCount']} note(s) logged)" if delivery["noteCount"] else ""),
    ]
    if delivery["kitPath"]:
        lines.append(f"- **Delivery kit:** {delivery['kitPath']}")
    lines += [
        "",
        "---",
        "",
        "*Company 360 is a read-only rollup. It computes nothing new — every figure above is reused verbatim "
        "from the employee that produced it, labelled by source. Where two employees independently estimate "
        "the same kind of thing (e.g. deal size, before a real pipeline record exists), both are shown, never "
        "averaged or merged into a third number.*",
    ]
    return "\n".join(lines)

