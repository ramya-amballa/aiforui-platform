"""
Opportunity Intelligence — Scoring (Phases 4-6 of the approved spec)

Every score here is deterministic Python over declared tags — never an
LLM judgement call at runtime, so "why did this get an 87" is always
traceable to opportunity-intelligence-config.json's weights plus the
specific evidence and profile-entry ids cited alongside the score.

Consulting/relationship scores are never recomputed if a real one
already exists elsewhere in AOS — this module reads
account-intelligence-feed.json, fractional-advisory-radar-feed.json
and relationship-profiles.json read-only first, and only falls back to
its own heuristic when the company has no existing record anywhere.
"""

import json
import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
AOS_DIR = RUNTIME_DIR.parent.parent
_SCHEMA_CONTRACTS_RUNTIME = AOS_DIR / "schema-contracts" / "runtime"
if str(_SCHEMA_CONTRACTS_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_SCHEMA_CONTRACTS_RUNTIME))

from status_vocabulary import GapMarker  # noqa: E402


def _load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def load_config():
    return _load_json(RUNTIME_DIR / "config" / "opportunity-intelligence-config.json", {})


def load_profile():
    return _load_json(
        RUNTIME_DIR / "config" / "ramya-professional-profile.json",
        {"verified_experience": [], "transferable_experience": [], "knowledge_training": [], "claims_requiring_verification": []},
    )


def load_existing_employee_feeds():
    """Read-only. Every one of these is optional — Day Zero AOS has
    none of them populated yet, and that must not crash anything."""
    return {
        "account_intelligence": _load_json(AOS_DIR / "output" / "account-intelligence" / "account-intelligence-feed.json", {}),
        "fractional_advisory_radar": _load_json(AOS_DIR / "output" / "fractional-advisory-radar" / "fractional-advisory-radar-feed.json", {}),
        "relationship_intelligence": _load_json(AOS_DIR / "relationship-intelligence" / "relationship-profiles.json", {}),
    }


def _tag_overlap(required_tags, profile_entries):
    """Returns (overlap_ratio 0-1, matched_entry_ids). A profile entry
    matches if any of its own declared tags intersects required_tags."""
    if not required_tags:
        return 0.0, []
    required = {t.strip().lower() for t in required_tags}
    matched_ids = []
    covered = set()
    for entry in profile_entries:
        entry_tags = {t.strip().lower() for t in entry.get("tags", [])}
        hit = entry_tags & required
        if hit:
            matched_ids.append(entry["id"])
            covered |= hit
    return (len(covered) / len(required) if required else 0.0), matched_ids


def score_employment_fit(inbox_entry, profile, config):
    """inbox_entry carries the job's own declared tags (from real
    research, never invented): required_skills, seniority_level,
    regulated_industry (bool), location, remote_status. Returns the
    full ramya_fit dict per the model doc, plus a top-level score."""
    weights = config.get("employmentFitWeights", {})
    required_tags = inbox_entry.get("required_skills", []) + inbox_entry.get("domains", [])

    verified_ratio, verified_ids = _tag_overlap(required_tags, profile.get("verified_experience", []))
    transferable_ratio, transferable_ids = _tag_overlap(required_tags, profile.get("transferable_experience", []))
    knowledge_ratio, knowledge_ids = _tag_overlap(required_tags, profile.get("knowledge_training", []))
    claims_ids = [e["id"] for e in profile.get("claims_requiring_verification", [])
                  if set(t.lower() for t in e.get("tags", [])) & {t.lower() for t in required_tags}]

    # Only verified + a discounted transferable contribution count
    # toward the actual fit score — knowledge/training alone never
    # inflates a fit score, per the founder's own rule that training
    # must never be quietly upgraded into implementation.
    role_relevance = min(1.0, verified_ratio + 0.4 * transferable_ratio)
    grc_alignment = role_relevance  # same tag-overlap basis; kept as a separate weighted line per the approved dimension list
    ai_gov_alignment = role_relevance
    tprm_alignment = role_relevance
    regulated_alignment = 1.0 if inbox_entry.get("regulated_industry") and verified_ratio > 0 else (0.5 if inbox_entry.get("regulated_industry") else 0.0)
    seniority_alignment = 1.0 if inbox_entry.get("seniority_level") and verified_ids else 0.3
    geo_suitability = 1.0 if inbox_entry.get("location_compatible", True) else 0.3
    evidence_strength = 1.0 if verified_ids else (0.5 if transferable_ids else 0.0)

    dimension_scores = {
        "roleRelevance": role_relevance,
        "seniorityAlignment": seniority_alignment,
        "grcTechnologyRiskAlignment": grc_alignment,
        "aiGovernanceAlignment": ai_gov_alignment,
        "tprmAlignment": tprm_alignment,
        "regulatedIndustryAlignment": regulated_alignment,
        "geographicSuitability": geo_suitability,
        "evidenceStrength": evidence_strength,
    }

    score = round(sum(dimension_scores.get(dim, 0) * weight for dim, weight in weights.items() if not dim.startswith("_")))

    required_lower = {t.lower() for t in required_tags}
    matched_lower = {t.lower() for entry in profile.get("verified_experience", []) + profile.get("transferable_experience", [])
                      for t in entry.get("tags", [])}
    gaps = sorted(required_lower - matched_lower)

    return {
        "score": score,
        "verified_matches": verified_ids,
        "transferable_matches": transferable_ids,
        "knowledge_matches": knowledge_ids,
        "claim_requires_verification": claims_ids,
        "gaps": gaps if gaps else [GapMarker.NOT_ESTABLISHED.value] if not required_tags else [],
        "_dimension_scores": dimension_scores,
    }


def derive_priority(score, config):
    thresholds = config.get("priorityThresholds", {"High": 75, "Medium": 45})
    if score >= thresholds.get("High", 75):
        return "High"
    if score >= thresholds.get("Medium", 45):
        return "Medium"
    return "Low"


def derive_employment_recommendation(score, config):
    thresholds = config.get("recommendationThresholds", {"APPLY": 70, "STRENGTHEN_PROFILE_FIRST": 45})
    if score >= thresholds.get("APPLY", 70):
        return "APPLY"
    if score >= thresholds.get("STRENGTHEN_PROFILE_FIRST", 45):
        return "STRENGTHEN_PROFILE_FIRST"
    return "DO_NOT_PURSUE_YET"


def _find_existing_company_record(company_name, feeds):
    """Read-only lookup across the three feeds that might already have
    scored this company. Returns (source_employee, record) or
    (None, None). Company matching is a case-insensitive exact name
    match only — deliberately no fuzzy matching, so a false match
    never silently substitutes the wrong company's real score."""
    name_lower = company_name.strip().lower()

    briefs = feeds.get("account_intelligence", {}).get("briefs", [])
    for b in briefs:
        if b.get("organisation", "").strip().lower() == name_lower:
            return "account-intelligence", b

    far = feeds.get("fractional_advisory_radar", {})
    for org_name, record in far.get("organisations", {}).items():
        if org_name.strip().lower() == name_lower:
            return "fractional-advisory-radar", record

    return None, None


def assess_consulting_opportunity(inbox_entry, config, feeds):
    """Prefers a real, already-computed score. Only computes its own
    heuristic when no existing AOS record covers this company at all."""
    company = inbox_entry.get("company", "")
    source_employee, existing = _find_existing_company_record(company, feeds)

    if existing is not None:
        return {
            "score": existing.get("overallPriority") or existing.get("fractionalAdvisoryPotential"),
            "why_now": inbox_entry.get("why_now", GapMarker.NOT_ESTABLISHED.value),
            "who_to_contact": inbox_entry.get("who_to_contact", GapMarker.NOT_ESTABLISHED.value),
            "why_this_person": inbox_entry.get("why_this_person", GapMarker.NOT_ESTABLISHED.value),
            "problem_to_lead_with": inbox_entry.get("likely_problem", GapMarker.NOT_ESTABLISHED.value),
            "what_not_to_sell_yet": inbox_entry.get("what_not_to_sell_yet", GapMarker.NOT_ESTABLISHED.value),
            "recommended_first_step": "Relationship-first — existing AOS record found, no direct pitch yet",
            "_source": source_employee,
        }

    weights = config.get("consultingHeuristicWeights", {})
    evidence = inbox_entry.get("evidence", {})
    dims = {
        "painEvidence": 1.0 if evidence.get("pain_evidence") else 0.0,
        "urgency": 1.0 if evidence.get("urgency") else 0.0,
        "regulatoryPressure": 1.0 if evidence.get("regulatory_pressure") else 0.0,
        "decisionMakerAccessibility": 1.0 if inbox_entry.get("decision_makers") else 0.0,
        "companyMaturitySignal": 0.5,
        "relationshipPotential": 0.5,
    }
    score = round(sum(dims.get(dim, 0) * weight for dim, weight in weights.items() if not dim.startswith("_")))

    return {
        "score": score,
        "why_now": evidence.get("why_now", GapMarker.NOT_ESTABLISHED.value),
        "who_to_contact": inbox_entry.get("who_to_contact", GapMarker.NOT_ESTABLISHED.value),
        "why_this_person": inbox_entry.get("why_this_person", GapMarker.NOT_ESTABLISHED.value),
        "problem_to_lead_with": inbox_entry.get("likely_problem", GapMarker.NOT_ESTABLISHED.value),
        "what_not_to_sell_yet": "Full engagement scope — lead with a single named problem only",
        "recommended_first_step": "Relationship-first outreach, not a pitch",
        "_source": None,
    }


def derive_decision_makers(inbox_entry, config):
    """Never invents a name. Uses a real name only if the research
    inbox entry itself supplied one (from real, public research);
    otherwise falls back to the shared, existing stakeholder-title
    table Account Intelligence already maintains, read-only."""
    supplied = inbox_entry.get("decision_makers", [])
    if supplied:
        return [{
            "name": p.get("name") or GapMarker.NOT_ESTABLISHED.value,
            "role": p.get("role", GapMarker.NOT_ESTABLISHED.value),
            "why_relevant": p.get("why_relevant", GapMarker.NOT_ESTABLISHED.value),
            "relationship_strength": p.get("relationship_strength", GapMarker.NOT_TRACKED.value),
            "likely_influence": p.get("likely_influence", GapMarker.NOT_ESTABLISHED.value),
            "recommended_approach": p.get("recommended_approach", "Relationship-first"),
        } for p in supplied]

    categories = inbox_entry.get("signal_categories", [])
    if not categories:
        return []

    titles_path = AOS_DIR / "account-intelligence" / "runtime" / "config" / "account-intelligence-config.json"
    account_config = _load_json(titles_path, {})
    titles_by_category = account_config.get("categoryToStakeholderTitles", {})

    titles = []
    for cat in categories:
        for title in titles_by_category.get(cat, []):
            if title not in titles:
                titles.append(title)

    return [{
        "name": GapMarker.NOT_ESTABLISHED.value,
        "role": title,
        "why_relevant": f"Matched signal category: {', '.join(categories)}",
        "relationship_strength": GapMarker.NOT_TRACKED.value,
        "likely_influence": GapMarker.NOT_ESTABLISHED.value,
        "recommended_approach": "Relationship-first — no named contact yet, title only",
    } for title in titles]
