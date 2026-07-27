"""
Recruiter Intelligence Engine (AOS Sprint 10)

Maintains a knowledge base of every recruiter and consulting contact
AOS has real evidence of, built by scanning two already-existing, real
data sources — never a second, independently-collected feed:

  - demand-intelligence/opportunity-schema.json: any opportunity whose
    sourceCategory is "Recruiter Channel" or "Consulting Channel"
    contributes a contact (its own `source` field is the recruiter/
    firm name), a role hired (title), a location, and domainTags
    (feeding specialisation).
  - crm/company-intelligence.json: any company with a `recruiter` name
    set contributes that company's industry, relationshipTemperature,
    lastTouch and nextFollowUpDue to that recruiter's profile — CRM's
    own already-computed relationship fields, reused verbatim via a
    hottest/soonest aggregation, never recomputed independently.

Persists to recruiter-profiles.json (a sibling of
demand-intelligence/organisation-profiles.json's own pattern): every
contact ever observed, accumulated across runs. Read-only with respect
to opportunity-schema.json and company-intelligence.json — never
writes to either.
"""

import copy
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
RECRUITER_INTELLIGENCE_DIR = RUNTIME_DIR.parent
AOS_DIR = RECRUITER_INTELLIGENCE_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_PATH = RUNTIME_DIR / "config" / "recruiter-intelligence-config.json"
PROFILES_PATH = RECRUITER_INTELLIGENCE_DIR / "recruiter-profiles.json"

OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "demand-intelligence" / "opportunity-schema.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"

FEED_PATH = RUNTIME_DIR / "output" / "recruiter-intelligence-feed.json"

TODAY = date.today().isoformat()

SOURCE_CATEGORIES = {"Recruiter Channel": "Recruiter", "Consulting Channel": "Consulting Firm"}

# Same region/country vocabulary demand_engine.py's own infer_region()
# already established — credited, verbatim copy, reused here for a
# different field (this contact's "countries") rather than a second
# independently-invented list.
REGION_KEYWORDS = {
    "UAE": ["uae", "united arab emirates", "dubai", "abu dhabi"],
    "US": ["us", "usa", "united states", "america"],
    "UK": ["uk", "united kingdom", "britain"],
    "India": ["india"],
    "Europe": ["eu", "europe", "european union"],
}

DEFAULT_PROFILES = {
    "schema": {
        "recruiter": "string — key, from the opportunity 'source' field",
        "firm": "string — same as recruiter unless the current data model distinguishes them (it doesn't yet)",
        "contactType": "string — Recruiter | Consulting Firm",
        "specialisation": "array of strings — ranked domainTags observed across this contact's sourced opportunities",
        "industries": "array of strings — industries of companies this contact introduced (from CRM)",
        "countries": "array of strings — regions inferred from sourced opportunities' location/description text",
        "rolesHired": "array of strings — opportunity titles sourced from this contact",
        "responseHistory": "array — {date, company, channel, summary}, from CRM outreachHistory for attributed companies",
        "lastInteraction": "string ISO date or null",
        "nextFollowUp": "string ISO date or null",
        "relationshipStrength": "number 0-100, from CRM's own relationshipTemperature",
        "relationshipBand": "string — Hot | Warm | Cooling | Cold | Unknown",
        "responseRate": "number 0-100 or null — % of attributed companies with existingRelationship beyond 'none'",
        "successRate": "number 0-100 or null — % of sourced opportunities whose pipeline stage is 'won'",
        "opportunityCount": "number",
        "firstSeen": "string ISO date",
        "lastSeen": "string ISO date",
    },
    "recruiters": {},
}


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


def load_config():
    return load_json(CONFIG_PATH, {})


def load_profiles():
    profiles = load_json(PROFILES_PATH, DEFAULT_PROFILES)
    profiles.setdefault("recruiters", {})
    return profiles


def infer_region(text):
    lowered = (text or "").lower()
    for region, keywords in REGION_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return region
    return "Not specified"


def _dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _rank_by_votes(items):
    votes = {}
    first_index = {}
    for i, item in enumerate(items):
        votes[item] = votes.get(item, 0) + 1
        first_index.setdefault(item, i)
    return sorted(votes.keys(), key=lambda k: (-votes[k], first_index[k]))


def _company_source_opportunities(opportunity_schema):
    """Recruiter/Consulting-Channel opportunities keyed by their source name."""
    by_source = {}
    for opp in opportunity_schema.get("opportunities", []):
        category = opp.get("sourceCategory")
        if category not in SOURCE_CATEGORIES:
            continue
        source = opp.get("source")
        if not source:
            continue
        by_source.setdefault(source, []).append(opp)
    return by_source


def _companies_by_recruiter(crm_data):
    by_recruiter = {}
    for company in crm_data.get("companies", []):
        recruiter = company.get("recruiter")
        if not recruiter:
            continue
        by_recruiter.setdefault(recruiter, []).append(company)
    return by_recruiter


def build_or_update_profile(recruiter_name, opportunities, companies, pipeline_by_org, config, existing):
    contact_type = "Recruiter"
    if opportunities:
        contact_type = SOURCE_CATEGORIES.get(opportunities[0].get("sourceCategory"), "Recruiter")

    domain_tags = [t for opp in opportunities for t in opp.get("domainTags", [])]
    specialisation = _rank_by_votes(domain_tags)

    industries = _dedupe_preserve_order(c.get("industry") for c in companies)
    roles_hired = _dedupe_preserve_order(opp.get("title") for opp in opportunities)

    location_texts = [f"{opp.get('location', '')} {opp.get('description', '')}" for opp in opportunities]
    countries = _dedupe_preserve_order(infer_region(t) for t in location_texts)
    countries = [c for c in countries if c != "Not specified"] or ["Not specified"]

    response_history = []
    for c in companies:
        for entry in c.get("outreachHistory", []):
            response_history.append({
                "date": entry.get("date"), "company": c.get("companyName"),
                "channel": entry.get("channel"), "summary": entry.get("summary"),
            })
    response_history.sort(key=lambda e: e.get("date") or "")

    last_touches = _dedupe_preserve_order(c.get("lastTouch") for c in companies)
    last_interaction = max(last_touches) if last_touches else None

    follow_ups = _dedupe_preserve_order(c.get("nextFollowUpDue") for c in companies)
    next_follow_up = min(follow_ups) if follow_ups else None

    temps = [c.get("relationshipTemperature", "unknown") for c in companies]
    temp_scores = config.get("relationshipTemperatureScore", {})
    best_temp = max(temps, key=lambda t: temp_scores.get(t, 0), default="unknown")
    relationship_strength = temp_scores.get(best_temp, 0)
    relationship_band = best_temp.capitalize() if best_temp != "unknown" else "Unknown"

    if companies:
        engaged = sum(1 for c in companies if (c.get("existingRelationship") or "none").lower() != "none")
        response_rate = round(100 * engaged / len(companies))
    else:
        response_rate = None

    org_names = {opp.get("organisation") for opp in opportunities if opp.get("organisation")}
    pipeline_entries = [pipeline_by_org[org] for org in org_names if org in pipeline_by_org]
    if pipeline_entries:
        won = sum(1 for e in pipeline_entries if e.get("stage") == "won")
        success_rate = round(100 * won / len(pipeline_entries))
    else:
        success_rate = None

    profile = {
        "recruiter": recruiter_name,
        "firm": existing.get("firm", recruiter_name) if existing else recruiter_name,
        "contactType": contact_type,
        "specialisation": specialisation,
        "industries": industries,
        "countries": countries,
        "rolesHired": roles_hired,
        "responseHistory": response_history,
        "lastInteraction": last_interaction,
        "nextFollowUp": next_follow_up,
        "relationshipStrength": relationship_strength,
        "relationshipBand": relationship_band,
        "responseRate": response_rate,
        "successRate": success_rate,
        "opportunityCount": len(opportunities),
        "firstSeen": (existing or {}).get("firstSeen", TODAY),
        "lastSeen": TODAY,
    }
    return profile


def is_dormant(profile, config):
    threshold = config.get("dormancyThresholdDays", 60)
    if not profile.get("lastInteraction"):
        return profile.get("opportunityCount", 0) > 0  # known but never actually touched
    try:
        last = datetime.fromisoformat(profile["lastInteraction"])
    except ValueError:
        return False
    return (datetime.fromisoformat(TODAY) - last) >= timedelta(days=threshold)


def is_due_this_week(profile, config):
    if not profile.get("nextFollowUp"):
        return False
    try:
        due = datetime.fromisoformat(profile["nextFollowUp"]).date()
    except ValueError:
        return False
    window = config.get("weeklyFollowUpWindowDays", 7)
    return due <= date.today() + timedelta(days=window)


def priority_score(profile, config):
    weights = config.get("priorityWeights", {})
    strength = profile.get("relationshipStrength") or 0
    response = profile.get("responseRate") or 0
    success = profile.get("successRate") or 0
    return round(
        strength * weights.get("relationshipStrength", 0)
        + response * weights.get("responseRate", 0)
        + success * weights.get("successRate", 0),
        1,
    )


def matches_hiring_domain(profile, domain_key, config):
    tags = config.get("hiringDomainTags", {}).get(domain_key, [])
    return any(t in profile.get("specialisation", []) for t in tags)


def refresh_all_profiles(opportunity_schema, crm_data, pipeline_data, config, profiles):
    opps_by_source = _company_source_opportunities(opportunity_schema)
    companies_by_recruiter = _companies_by_recruiter(crm_data)
    pipeline_by_org = {e.get("organisation"): e for e in pipeline_data.get("pipeline", []) if e.get("organisation")}

    all_names = set(opps_by_source.keys()) | set(companies_by_recruiter.keys())
    for name in all_names:
        existing = profiles["recruiters"].get(name)
        profiles["recruiters"][name] = build_or_update_profile(
            name, opps_by_source.get(name, []), companies_by_recruiter.get(name, []),
            pipeline_by_org, config, existing,
        )
    return profiles


def build_feed(profiles, config):
    contacts = list(profiles.get("recruiters", {}).values())
    return {
        "schema": {
            "recruiter": "string", "firm": "string", "contactType": "string",
            "relationshipStrength": "number 0-100", "relationshipBand": "string",
            "responseRate": "number or null", "successRate": "number or null",
            "priorityScore": "number 0-100", "isDormant": "boolean", "isDueThisWeek": "boolean",
            "nextFollowUp": "string or null", "lastInteraction": "string or null",
        },
        "contacts": [
            {
                "recruiter": c["recruiter"], "firm": c["firm"], "contactType": c["contactType"],
                "specialisation": c["specialisation"], "industries": c["industries"], "countries": c["countries"],
                "relationshipStrength": c["relationshipStrength"], "relationshipBand": c["relationshipBand"],
                "responseRate": c["responseRate"], "successRate": c["successRate"],
                "priorityScore": priority_score(c, config),
                "isDormant": is_dormant(c, config), "isDueThisWeek": is_due_this_week(c, config),
                "nextFollowUp": c["nextFollowUp"], "lastInteraction": c["lastInteraction"],
                "opportunityCount": c["opportunityCount"],
            }
            for c in contacts
        ],
        "weeklyFollowUpList": sorted(
            [c["recruiter"] for c in contacts if is_due_this_week(c, config)],
            key=lambda name: profiles["recruiters"][name]["nextFollowUp"] or "",
        ),
        "dormantRelationships": [c["recruiter"] for c in contacts if is_dormant(c, config)],
        "priorityRecruiters": sorted(
            [c["recruiter"] for c in contacts], key=lambda name: priority_score(profiles["recruiters"][name], config), reverse=True
        )[:10],
        "hiringAiGovernance": [c["recruiter"] for c in contacts if matches_hiring_domain(c, "aiGovernance", config)],
        "hiringGrc": [c["recruiter"] for c in contacts if matches_hiring_domain(c, "grc", config)],
        "hiringFractionalConsultants": [c["recruiter"] for c in contacts if matches_hiring_domain(c, "fractionalConsultants", config)],
    }
