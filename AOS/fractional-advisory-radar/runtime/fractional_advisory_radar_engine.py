"""
Fractional Advisory Radar (AOS Sprint 11)

Detects organisations likely to need fractional AI Governance support
by re-reading Demand Intelligence's own already-collected signals
(organisation-profiles.json) through a new lens — never a second,
independently-collected feed. The public signals this sprint asks to
monitor (Microsoft Copilot deployment, ISO 42001, NIST AI RMF, AI
Governance Committee, Responsible AI initiatives, Chief AI Officer
appointments) are already exactly what demand-signal-categories.json's
five categories detect; this engine reuses that classification rather
than re-scanning the same RSS feeds with a second taxonomy.

What is genuinely new here: a stage classification (Emerging / Growing
/ Enterprise / Urgent), an estimated Fractional Advisory Potential, and
a recommended engagement model (Discovery workshop / Retainer /
Advisory / Implementation) — all derived deterministically from
organisation-profiles.json's own already-computed fields (matched
categories, buying readiness, scale) plus this engine's own small,
documented lookup tables.

Read-only with respect to every other employee's data.
"""

import copy
import json
import re
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
RADAR_DIR = RUNTIME_DIR.parent
AOS_DIR = RADAR_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_PATH = RUNTIME_DIR / "config" / "fractional-advisory-radar-config.json"
DEMAND_INTELLIGENCE_DIR = AOS_DIR / "demand-intelligence"
PROFILES_PATH = DEMAND_INTELLIGENCE_DIR / "organisation-profiles.json"
OPPORTUNITY_SCHEMA_PATH = DEMAND_INTELLIGENCE_DIR / "opportunity-schema.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
DEMAND_CATEGORIES_CONFIG_PATH = DEMAND_INTELLIGENCE_DIR / "runtime" / "config" / "demand-signal-categories.json"

FEED_PATH = RUNTIME_DIR / "output" / "fractional-advisory-radar-feed.json"

STAGE_ORDER = ["Urgent", "Enterprise", "Growing", "Emerging"]


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


def load_demand_categories_config():
    return load_json(DEMAND_CATEGORIES_CONFIG_PATH, {"categories": {}})


def _extract_scale_number(scale_text):
    """Same convention demand_engine.py's own _extract_scale_number()
    already uses — reimplemented locally, not imported, keeping this
    employee's runtime self-contained like every other AOS employee."""
    if not scale_text:
        return None
    match = re.search(r"([\d,]+)", scale_text)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def ordered_matched_categories(matched_categories, demand_categories_config):
    categories = demand_categories_config.get("categories", {})
    return sorted(matched_categories, key=lambda c: categories.get(c, {}).get("baseScore", 0), reverse=True)


def classify_stage(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    if not matched:
        return "Emerging"

    stage_by_category = config.get("stageByCategory", {})
    stages_present = [stage_by_category.get(c) for c in matched if stage_by_category.get(c)]
    stage = min(stages_present, key=lambda s: STAGE_ORDER.index(s)) if stages_present else "Emerging"

    upgrade = config.get("stageScaleUpgrade", {})
    if stage == upgrade.get("upgradeFrom"):
        scale_number = _extract_scale_number(profile.get("scale"))
        if scale_number is not None and scale_number >= upgrade.get("scaleThreshold", 10000):
            stage = upgrade.get("upgradeTo", stage)
    return stage


def recommended_engagement_model(stage, config):
    return config.get("engagementModelByStage", {}).get(stage, "Discovery workshop")


def fractional_advisory_potential(stage, profile, config):
    """0-100: a stage-based value, nudged by Buying Readiness Score
    (already computed by demand_engine.py) so two orgs at the same
    stage are still differentiated by their actual readiness."""
    base = config.get("potentialScoreByStage", {}).get(stage, 30)
    readiness_adjustment = round((profile.get("buyingReadinessScore", 0) - 50) / 10)
    return max(0, min(100, base + readiness_adjustment))


def _find_opportunity_record(organisation, opportunity_schema):
    for opp in opportunity_schema.get("opportunities", []):
        if opp.get("organisation") == organisation:
            return opp
    return None


def _find_pipeline_record(organisation, pipeline_data):
    for entry in pipeline_data.get("pipeline", []):
        if entry.get("organisation") == organisation:
            return entry
    return None


def expected_consulting_revenue(profile, stage, opportunity_schema, pipeline_data, config):
    """Prefers a real pipeline.json/opportunity-schema.json figure over
    a heuristic, same 'prefer the real record' pattern established in
    Sprint 9/10 — never a second, contradicting estimate when a real
    one already exists."""
    organisation = profile.get("organisation")
    pipeline_entry = _find_pipeline_record(organisation, pipeline_data)
    if pipeline_entry and pipeline_entry.get("expectedRevenue") not in (None, "", "Not yet estimated"):
        return {"score": None, "estimate": str(pipeline_entry["expectedRevenue"]), "source": "Revenue Hunter's pipeline.json (real estimate)"}

    opp = _find_opportunity_record(organisation, opportunity_schema)
    if opp:
        score = opp.get("scores", {}).get("expectedRevenue")
        return {"score": score, "estimate": f"{score}/10 (opportunity-schema.json)", "source": "Real opportunity record"}

    score = config.get("revenueEstimateByStage", {}).get(stage, 3)
    return {"score": score, "estimate": f"{score}/10 (stage-based heuristic)", "source": "Stage-based heuristic (no real revenue record yet)"}


def build_entry(profile, demand_categories_config, config, opportunity_schema, pipeline_data):
    stage = classify_stage(profile, demand_categories_config, config)
    engagement_model = recommended_engagement_model(stage, config)
    potential = fractional_advisory_potential(stage, profile, config)
    revenue = expected_consulting_revenue(profile, stage, opportunity_schema, pipeline_data, config)

    return {
        "organisation": profile.get("organisation"),
        "industry": profile.get("industry") or "Not specified",
        "stage": stage,
        "fractionalAdvisoryPotential": potential,
        "recommendedEngagementModel": engagement_model,
        "expectedConsultingRevenue": revenue,
        "buyingReadinessBand": profile.get("buyingReadinessBand", "Low"),
        "matchedCategories": profile.get("matchedCategories", []),
        "lastSeen": profile.get("lastSeen", ""),
    }


def build_feed(profiles, demand_categories_config, config, opportunity_schema, pipeline_data):
    entries = [
        build_entry(profile, demand_categories_config, config, opportunity_schema, pipeline_data)
        for profile in profiles.get("organisations", {}).values()
    ]
    entries.sort(key=lambda e: e["expectedConsultingRevenue"]["score"] if e["expectedConsultingRevenue"]["score"] is not None else -1, reverse=True)
    return {
        "schema": {
            "organisation": "string", "industry": "string", "stage": "string — Emerging|Growing|Enterprise|Urgent",
            "fractionalAdvisoryPotential": "number 0-100", "recommendedEngagementModel": "string",
            "expectedConsultingRevenue": "object — {score, estimate, source}",
            "buyingReadinessBand": "string", "matchedCategories": "array", "lastSeen": "string",
        },
        "organisations": entries,
    }
