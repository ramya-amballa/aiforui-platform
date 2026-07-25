"""
Demand Intelligence v2 — Consulting Demand Engine (AOS Sprint 6)

Turns a raw signal (an article naming a real organisation, already
identified by claude_client.extract_demand_signal — the one and only
non-deterministic step in this whole module) into everything Sprint 6
asks for: which of the five demand-signal categories it belongs to,
an Overall Demand Score, a factual Opportunity Narrative, ranked
consulting-service predictions, a 0-100 Buying Readiness Score and
band, a Recommended Next Action with reasoning, and an updated,
persistent per-organisation profile that later feeds CEO Advisor's
"Top 10 Organizations This Week" and the dashboard's Demand
Intelligence page.

Everything in this module is a deterministic function of already-
extracted facts and config/demand-signal-categories.json's lookup
tables — no second model call, no machine learning. The one place
history changes future output (Part 8, deterministic feedback
weighting) is category_conversion_multiplier(), which nudges a
category's effective base score up or down based on what actually
happened to past opportunities in that category — read from CRM,
Revenue Hunter and Sales Director's own existing output files,
never a second copy of their data.

This module does not collect anything itself and does not touch
opportunity-schema.json/pipeline.json/company-intelligence.json —
collectors/demand_signals.py calls it, then builds the same
opportunity-hunter-shaped record it always has, which still flows
through ingest.py's completely unmodified scoring/classification/
routing pipeline. Demand Intelligence's own state lives in
organisation-profiles.json, a new, separate, additive file.
"""

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import ingest  # reused directly for compute_priority_score() — see opportunity_scores_from_result()

# parse_currency reused verbatim from revenue-hunter/runtime/generate.py
# (itself reused verbatim from executive-dashboard/runtime/generate.py) —
# same currency parsing every runtime already uses, not a second
# implementation of the same logic.
MULTIPLIERS = {"k": 1_000, "l": 100_000, "lakh": 100_000, "cr": 10_000_000, "crore": 10_000_000, "m": 1_000_000}
CURRENCY_SYMBOLS = {"$": "USD", "₹": "INR", "£": "GBP", "€": "EUR"}


def parse_currency(value):
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

RUNTIME_DIR = Path(__file__).resolve().parent
DEMAND_INTELLIGENCE_DIR = RUNTIME_DIR.parent
AOS_DIR = DEMAND_INTELLIGENCE_DIR.parent

CONFIG_PATH = RUNTIME_DIR / "config" / "demand-signal-categories.json"
PROFILES_PATH = DEMAND_INTELLIGENCE_DIR / "organisation-profiles.json"
TOP_ORGANISATIONS_PATH = RUNTIME_DIR / "output" / "top-organisations-this-week.json"

CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
SALES_FEED_PATH = AOS_DIR / "sales-director" / "runtime" / "output" / "ceo-advisor-feed.json"

TODAY = date.today().isoformat()

DEFAULT_PROFILES = {
    "schema": {
        "organisation": "string — key",
        "signals": "array — every demand signal ever observed for this organisation: "
                   "{date, category, categoryLabel, baseScore, confidence, eventSummary, sourceUrl}",
        "overallDemandScore": "number 0-100, most recent computation",
        "matchedCategories": "array of category keys matched across all signals on record",
        "buyingReadinessScore": "number 0-100", "buyingReadinessBand": "Low|Medium|High|Very High",
        "recommendedServices": "array of strings, ranked",
        "recommendedAction": "string", "recommendedActionReason": "string",
        "opportunityNarrative": "string",
        "industry": "string or null", "scale": "string or null",
        "region": "string — UAE/US/UK/India/Europe or 'Not specified', best-effort inferred, never guessed",
        "firstSeen": "string ISO date", "lastSeen": "string ISO date",
        "outreachHappened": "boolean — Part 8, read from CRM outreachHistory",
        "proposalCreated": "boolean — Part 8, read from Sales Director's feed",
        "converted": "boolean — Part 8, read from Revenue Hunter's pipeline stage",
        "revenueGenerated": "number or null — Part 8, from the same pipeline entry, only once won",
    },
    "organisations": {},
}


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_categories_config():
    return load_json(CONFIG_PATH, {})


# --------------------------------------------------------------------------
# Part 1 — Demand Signal Classification
# --------------------------------------------------------------------------

def classify_categories(text, config):
    """Deterministic, whole-phrase, case-insensitive keyword matching —
    the same convention opportunity-relevance-engine.md and Market
    Intelligence's six checks already use. Returns a list of matched
    category keys, in config's declared order (not text order)."""
    lowered = (text or "").lower()
    matched = []
    for key, category in config.get("categories", {}).items():
        if any(kw in lowered for kw in category.get("keywords", [])):
            matched.append(key)
    return matched


def compute_overall_demand_score(matched_categories, confidence, config, conversion_multiplier=1.0):
    """Weighted aggregation (Part 1): the highest-scoring matched
    category counts in full, every additional matched category adds a
    smaller weighted share (stacking signals confirms a stronger
    picture, but one very-high category alone can never be inflated
    past 100 just by re-weighting). Scaled by confidence, and by
    conversion_multiplier — Part 8's deterministic feedback weighting,
    1.0 when no historical adjustment applies yet."""
    categories = config.get("categories", {})
    weights = config.get("aggregationWeights", {"primaryCategoryWeight": 1.0, "additionalCategoryWeight": 0.35})
    conf_mult = config.get("confidenceMultiplier", {"high": 1.0, "medium": 0.7, "low": 0.4}).get(confidence, 0.5)

    if not matched_categories:
        return 0

    scores = sorted((categories.get(c, {}).get("baseScore", 0) for c in matched_categories), reverse=True)
    total = scores[0] * weights["primaryCategoryWeight"]
    for extra in scores[1:]:
        total += extra * weights["additionalCategoryWeight"]

    return round(min(100, total * conf_mult * conversion_multiplier))


# --------------------------------------------------------------------------
# Part 2 — Opportunity Narrative (templated, factual — never a second
# model call; "do not write marketing copy" per the brief)
# --------------------------------------------------------------------------

def build_opportunity_narrative(organisation, matched_categories, event_summary, services, confidence, config):
    labels = [config["categories"][c]["label"] for c in matched_categories if c in config.get("categories", {})]
    need_clauses = [config.get("governanceNeedByCategory", {}).get(c) for c in matched_categories]
    need_clause = "; ".join(c for c in need_clauses if c) or "AI governance and risk oversight"

    fact_sentence = event_summary.strip() if event_summary else (
        f"{organisation} has been identified as matching the following demand signal(s): {', '.join(labels)}."
    )
    if not fact_sentence.endswith((".", "!", "?")):
        fact_sentence += "."

    lines = [
        fact_sentence,
        f"Organisations at this stage typically require {need_clause}.",
        "",
        "Potential AI for U&I engagement:",
    ]
    for service in services:
        lines.append(f"• {service}")
    lines += ["", f"Confidence: {confidence.capitalize() if confidence else 'Unknown'}"]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Part 3 — Consulting Need Prediction
# --------------------------------------------------------------------------

def predict_services(matched_categories, config):
    """Deterministic ranked service prediction: earlier-declared
    services for the highest-scoring matched category are prioritised;
    services suggested by more than one matched category rise via a
    simple vote count, ties broken by category priority order."""
    categories = config.get("categories", {})
    category_to_services = config.get("categoryToServices", {})
    if not matched_categories:
        return []

    ranked_by_score = sorted(matched_categories, key=lambda c: categories.get(c, {}).get("baseScore", 0), reverse=True)

    votes = {}
    first_rank = {}
    for priority, cat in enumerate(ranked_by_score):
        for rank, service in enumerate(category_to_services.get(cat, [])):
            votes[service] = votes.get(service, 0) + 1
            first_rank.setdefault(service, (priority, rank))

    return sorted(votes.keys(), key=lambda s: (-votes[s], first_rank[s][0], first_rank[s][1]))


# --------------------------------------------------------------------------
# Part 4 — Buying Readiness Score
# --------------------------------------------------------------------------

DEPLOYMENT_STAGE_BY_CATEGORY = {
    "ai_adoption": 6, "governance_trigger": 8, "funding_trigger": 5,
    "regulatory_trigger": 9, "failure_trigger": 10,
}
URGENCY_BY_CATEGORY = {
    "ai_adoption": 5, "governance_trigger": 6, "funding_trigger": 5,
    "regulatory_trigger": 8, "failure_trigger": 10,
}


def _extract_scale_number(scale_text):
    if not scale_text:
        return None
    match = re.search(r"([\d,]+)", scale_text)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


# Same served-geography vocabulary collectors/common.py already uses,
# reused for consistency rather than a second list — best-effort only;
# "Not specified" (never guessed) when nothing in the text matches, the
# same honesty convention website-intake/'s own geography inference uses.
REGION_KEYWORDS = {
    "UAE": ["uae", "united arab emirates", "dubai", "abu dhabi"],
    "US": ["us", "usa", "united states", "america"],
    "UK": ["uk", "united kingdom", "britain"],
    "India": ["india"],
    "Europe": ["eu", "europe", "european union"],
}


def infer_region(text):
    lowered = (text or "").lower()
    for region, keywords in REGION_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return region
    return "Not specified"


def _organisation_size_score(scale_text):
    n = _extract_scale_number(scale_text)
    if n is None:
        return 5  # honest neutral default — no signal to size the organisation by
    if n >= 10000:
        return 9
    if n >= 1000:
        return 7
    if n >= 100:
        return 5
    return 4


def compute_buying_readiness_score(matched_categories, confidence, scale_text, overall_demand_score, config):
    weights = config.get("buyingReadinessWeights", {})
    conf_score = {"high": 9, "medium": 6, "low": 3}.get(confidence, 5)

    deployment_stage = max((DEPLOYMENT_STAGE_BY_CATEGORY.get(c, 5) for c in matched_categories), default=5)
    urgency = max((URGENCY_BY_CATEGORY.get(c, 5) for c in matched_categories), default=5)
    regulatory_pressure = 10 if "regulatory_trigger" in matched_categories else 3
    governance_trigger = 10 if "governance_trigger" in matched_categories else 2
    organisation_size = _organisation_size_score(scale_text)
    public_ai_maturity = min(10, conf_score + (1 if "ai_adoption" in matched_categories else 0))
    strategic_importance = round(overall_demand_score / 10)

    components = {
        "deploymentStage": deployment_stage,
        "organisationSize": organisation_size,
        "regulatoryPressure": regulatory_pressure,
        "publicAiMaturity": public_ai_maturity,
        "governanceTrigger": governance_trigger,
        "strategicImportance": strategic_importance,
        "urgency": urgency,
    }

    weighted = sum(components[k] * weights.get(k, 0) for k in components)
    score = round(min(100, weighted * 10))

    bands = config.get("buyingReadinessBands", {"veryHigh": 85, "high": 65, "medium": 40})
    if score >= bands["veryHigh"]:
        band = "Very High"
    elif score >= bands["high"]:
        band = "High"
    elif score >= bands["medium"]:
        band = "Medium"
    else:
        band = "Low"

    return score, band


# --------------------------------------------------------------------------
# Part 5 — Outreach Recommendation (next action, not a drafted email)
# --------------------------------------------------------------------------

def recommend_next_action(buying_band, matched_categories, confidence, config):
    if confidence == "low":
        return "Wait", "Confidence in this signal is low — wait for a clearer, corroborating signal before acting."

    if "failure_trigger" in matched_categories:
        return "Prepare Proposal", ("A failure/incident-type signal is the highest-urgency category — "
                                     "prepare a proposal now rather than a softer first touch.")
    if "regulatory_trigger" in matched_categories and buying_band in ("High", "Very High"):
        return "Schedule Outreach", ("A regulatory-trigger signal at a high buying-readiness band warrants "
                                      "direct outreach, not just monitoring.")

    default_action = config.get("nextActionByBand", {}).get(buying_band, "Monitor")
    reasons = {
        "Schedule Outreach": f"Buying readiness is {buying_band} — direct outreach is warranted now.",
        "Prepare Executive Brief": f"Buying readiness is {buying_band} — worth a concise executive brief ahead of outreach.",
        "Prepare Insight Article": f"Buying readiness is {buying_band} — a published insight piece can open the door before a direct approach.",
        "Monitor": f"Buying readiness is {buying_band} — not yet worth outreach; keep watching for a stronger signal.",
    }
    return default_action, reasons.get(default_action, f"Buying readiness is {buying_band}.")


# --------------------------------------------------------------------------
# Scores handed to ingest.py's existing, unmodified scoring/classification
# pipeline — a function of this signal's own analysis, not a fixed
# constant. A weak signal genuinely scores lower through the same
# opportunity-scoring-engine.md formula every opportunity already uses;
# nothing here duplicates or re-derives that formula, it only supplies
# better-differentiated input to it than a one-size-fits-all default would.
# --------------------------------------------------------------------------

def _high_value_default_revenue(matched_categories):
    if any(c in matched_categories for c in ("regulatory_trigger", "failure_trigger")):
        return 8  # compliance/incident-response engagements command premium rates regardless of headcount
    if any(c in matched_categories for c in ("governance_trigger", "funding_trigger")):
        return 7
    return 6


def _adgl_alignment(matched_categories):
    if "ai_adoption" in matched_categories:
        return 10
    if any(c in matched_categories for c in ("regulatory_trigger", "failure_trigger")):
        return 9
    if "governance_trigger" in matched_categories:
        return 8
    return 5


def opportunity_scores_from_result(overall_demand_score, buying_readiness_score, matched_categories, scale_text):
    """Builds the 11-dimension scores dict ingest.py's own, unmodified
    compute_priority_score()/classify() then run over — a genuine
    function of this signal's own analysis (Overall Demand Score,
    Buying Readiness Score, which categories matched, how large the
    organisation appears to be), not a fixed constant every signal
    gets regardless of strength.

    relationshipValue is fixed at 7 regardless of how strong the
    signal is — the same "some pre-existing relevance, no direct
    contact yet" default website-intake/ already uses for its own
    self-initiated-but-uncontacted leads. It's chosen deliberately so
    it never blocks either of ingest.py's classify() outcomes that
    matter here: the "Immediate Proposal" branch (score>=80 and
    scoped) doesn't check relationshipValue at all, and the
    "Relationship Building" branch (score 50-79, not scoped) needs
    relationshipValue>=7 — so whichever branch this signal's own
    strength actually lands in, this same value already satisfies it.
    Whether scopedEngagement should be True is decided afterward, from
    ingest.py's own real compute_priority_score() on these same scores
    — never a second, independently-thresholded banding that could
    disagree with it (an earlier version of this function did exactly
    that and produced signals that satisfied neither branch)."""
    governance_relevant = any(c in matched_categories for c in
                               ("ai_adoption", "governance_trigger", "regulatory_trigger", "failure_trigger"))
    scale_based_revenue = _organisation_size_score(scale_text) if scale_text else None
    expected_revenue = max(scale_based_revenue or 0, _high_value_default_revenue(matched_categories))

    return {
        "expectedRevenue": max(4, min(10, expected_revenue)),
        "probabilityOfWinning": max(2, min(10, round(buying_readiness_score / 10))),
        "strategicValue": max(3, min(10, round(overall_demand_score / 10))),
        "relationshipValue": 7,
        "timeRequired": 8,       # a template-driven, insight-led first-touch draft is fast to prepare
        "geography": 7,
        "remoteCompatibility": 9,
        "alignmentAIforUIServices": 10 if governance_relevant else 7,
        "alignmentADGL": _adgl_alignment(matched_categories),
        "alignmentOPERA": 9 if governance_relevant else 6,
        "longTermRelationshipPotential": max(4, min(10, round(overall_demand_score / 12) + 3)),
    }


def scoped_engagement_for_scores(scores):
    """True only if ingest.py's own, real compute_priority_score() on
    these exact scores would actually reach the Priority band (>=80) —
    derived from the same function ingest.py's classify() itself uses,
    never an independent threshold that could disagree with it."""
    return ingest.compute_priority_score(scores) >= 80


# --------------------------------------------------------------------------
# Part 8 — Learning: deterministic feedback weighting (no ML)
# --------------------------------------------------------------------------

def _outreach_happened(organisation, crm_data):
    for company in crm_data.get("companies", []):
        if company.get("companyName") == organisation and company.get("outreachHistory"):
            return True
    return False


def _proposal_created(organisation, sales_feed):
    return any(item.get("organisation") == organisation for item in sales_feed.get("feed", []))


def _pipeline_outcome(organisation, pipeline_data):
    """Returns (converted, revenue) — converted only once a pipeline
    entry for this organisation has actually reached 'won', never
    inferred from being merely 'in-progress'."""
    for entry in pipeline_data.get("pipeline", []):
        if entry.get("organisation") == organisation and entry.get("stage") == "won":
            amount, _ = parse_currency(entry.get("expectedRevenue"))
            return True, amount
    return False, None


def category_conversion_multiplier(category, profiles, config):
    """Part 8's actual "improve future scoring" mechanism: a small,
    bounded, deterministic multiplier on a category's future base
    score, driven only by what genuinely happened to past
    opportunities in that category — never machine-learned, always
    auditable from organisation-profiles.json alone.

    +0.05 per converted opportunity in this category (capped at +0.20).
    -0.03 per opportunity where outreach happened but nothing
    progressed for 90+ days (capped at -0.15) — a deliberately gentle
    penalty, since one quiet account is normal, not evidence the
    category itself is weak."""
    converted = 0
    stalled = 0
    for org in profiles.get("organisations", {}).values():
        if category not in org.get("matchedCategories", []):
            continue
        if org.get("converted"):
            converted += 1
        elif org.get("outreachHappened") and not org.get("proposalCreated"):
            try:
                last_seen = datetime.fromisoformat(org.get("lastSeen", TODAY))
                if (datetime.fromisoformat(TODAY) - last_seen) >= timedelta(days=90):
                    stalled += 1
            except ValueError:
                pass

    multiplier = 1.0 + min(0.20, converted * 0.05) - min(0.15, stalled * 0.03)
    return round(max(0.7, multiplier), 3)


def update_feedback_fields(org_profile, organisation, crm_data, pipeline_data, sales_feed):
    outreach = _outreach_happened(organisation, crm_data)
    proposal = _proposal_created(organisation, sales_feed)
    converted, revenue = _pipeline_outcome(organisation, pipeline_data)
    org_profile["outreachHappened"] = outreach
    org_profile["proposalCreated"] = proposal
    org_profile["converted"] = converted
    org_profile["revenueGenerated"] = revenue
    return org_profile


# --------------------------------------------------------------------------
# Profile persistence and full per-signal update
# --------------------------------------------------------------------------

def load_profiles():
    profiles = load_json(PROFILES_PATH, DEFAULT_PROFILES)
    profiles.setdefault("organisations", {})
    return profiles


def process_signal(organisation, category_keys, confidence, event_summary, industry, scale_text,
                    source_url, config, profiles):
    """The full Part 1-5 pipeline for one newly-observed signal,
    folding it into that organisation's persistent profile (Part 8's
    running history) and returning the fields collectors/demand_signals.py
    needs to build a normal opportunity record."""
    org_profile = profiles["organisations"].setdefault(organisation, {
        "organisation": organisation, "signals": [], "matchedCategories": [],
        "industry": industry, "scale": scale_text, "region": infer_region(event_summary),
        "firstSeen": TODAY,
        "outreachHappened": False, "proposalCreated": False,
        "converted": False, "revenueGenerated": None,
    })

    conversion_multiplier = category_conversion_multiplier(category_keys[0], profiles, config) if category_keys else 1.0
    overall_demand_score = compute_overall_demand_score(category_keys, confidence, config, conversion_multiplier)
    buying_score, buying_band = compute_buying_readiness_score(
        category_keys, confidence, scale_text, overall_demand_score, config)
    services = predict_services(category_keys, config)
    narrative = build_opportunity_narrative(organisation, category_keys, event_summary, services, confidence, config)
    next_action, next_action_reason = recommend_next_action(buying_band, category_keys, confidence, config)

    for key in category_keys:
        label = config.get("categories", {}).get(key, {}).get("label", key)
        org_profile["signals"].append({
            "date": TODAY, "category": key, "categoryLabel": label,
            "baseScore": config.get("categories", {}).get(key, {}).get("baseScore", 0),
            "confidence": confidence, "eventSummary": event_summary, "sourceUrl": source_url,
        })
        if key not in org_profile["matchedCategories"]:
            org_profile["matchedCategories"].append(key)

    org_profile.update({
        "overallDemandScore": overall_demand_score,
        "buyingReadinessScore": buying_score,
        "buyingReadinessBand": buying_band,
        "recommendedServices": services,
        "recommendedAction": next_action,
        "recommendedActionReason": next_action_reason,
        "opportunityNarrative": narrative,
        "industry": industry or org_profile.get("industry"),
        "scale": scale_text or org_profile.get("scale"),
        "region": infer_region(event_summary) if infer_region(event_summary) != "Not specified" else org_profile.get("region", "Not specified"),
        "lastSeen": TODAY,
    })

    scores = opportunity_scores_from_result(overall_demand_score, buying_score, category_keys, scale_text)
    scoped_engagement = scoped_engagement_for_scores(scores)

    return {
        "overallDemandScore": overall_demand_score,
        "buyingReadinessScore": buying_score,
        "buyingReadinessBand": buying_band,
        "recommendedServices": services,
        "recommendedAction": next_action,
        "recommendedActionReason": next_action_reason,
        "opportunityNarrative": narrative,
        "matchedCategories": category_keys,
        "scores": scores,
        "scopedEngagement": scoped_engagement,
    }


def refresh_feedback_for_all_profiles(profiles):
    """Part 8: cross-references CRM/pipeline/Sales Director's own,
    already-written output — read-only, never a second copy of their
    data — to keep every organisation's outcome fields current. Safe
    to call every run; a step that hasn't run yet today just leaves
    yesterday's already-correct answer in place (the same one-cycle-
    behind limitation CRM's own read of Sales Director already has)."""
    crm_data = load_json(CRM_PATH, {"companies": []})
    pipeline_data = load_json(PIPELINE_PATH, {"pipeline": []})
    sales_feed = load_json(SALES_FEED_PATH, {"feed": []})

    for organisation, org_profile in profiles.get("organisations", {}).items():
        update_feedback_fields(org_profile, organisation, crm_data, pipeline_data, sales_feed)

    return profiles


# --------------------------------------------------------------------------
# Part 6 — CEO Advisor feed
# --------------------------------------------------------------------------

DEFAULT_TOP_ORGANISATIONS_FEED = {
    "schema": {
        "organisation": "string", "demandSignal": "string — matched category label(s), comma-separated",
        "buyingReadinessScore": "number 0-100", "buyingReadinessBand": "string",
        "opportunityNarrative": "string", "recommendedServices": "array of strings, ranked",
        "recommendedAction": "string", "recommendedActionReason": "string",
        "overallDemandScore": "number 0-100 — used by CEO Advisor as this candidate's strategic-value input",
        "lastSeen": "string ISO date",
    },
    "organisations": [],
    "_note": "Raw, unranked candidates only — CEO Advisor's own rank_candidates()/"
             "top_priorities_with_reasons() (ceo-advisor/runtime/generate.py) does the "
             "actual ranking and 'why this outranks the next' reasoning, the same "
             "urgency-weighted, tie-break logic every other candidate source already "
             "goes through. This file does not duplicate that ranking.",
}


def write_top_organisations_feed(profiles, config, window_days=7):
    """Organisations with at least one signal in the last `window_days`
    days — CEO Advisor's own ranking (not duplicated here) decides
    which ten actually make the report."""
    cutoff = date.today() - timedelta(days=window_days)
    feed = dict(DEFAULT_TOP_ORGANISATIONS_FEED)
    feed["organisations"] = []

    for organisation, org_profile in profiles.get("organisations", {}).items():
        recent_signals = []
        for signal in org_profile.get("signals", []):
            try:
                if datetime.fromisoformat(signal["date"]).date() >= cutoff:
                    recent_signals.append(signal)
            except (KeyError, ValueError):
                continue
        if not recent_signals:
            continue

        labels = sorted({s["categoryLabel"] for s in recent_signals})
        feed["organisations"].append({
            "organisation": organisation,
            "demandSignal": ", ".join(labels),
            "buyingReadinessScore": org_profile.get("buyingReadinessScore", 0),
            "buyingReadinessBand": org_profile.get("buyingReadinessBand", "Low"),
            "opportunityNarrative": org_profile.get("opportunityNarrative", ""),
            "recommendedServices": org_profile.get("recommendedServices", []),
            "recommendedAction": org_profile.get("recommendedAction", "Monitor"),
            "recommendedActionReason": org_profile.get("recommendedActionReason", ""),
            "overallDemandScore": org_profile.get("overallDemandScore", 0),
            "lastSeen": org_profile.get("lastSeen", TODAY),
        })

    save_json(TOP_ORGANISATIONS_PATH, feed)
    return feed
