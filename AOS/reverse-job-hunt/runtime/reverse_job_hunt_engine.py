"""
Reverse Job Hunt Engine (AOS Sprint 9)

Turns AOS from a reactive opportunity finder into a proactive business
development system: for every organisation already qualified by
Demand Intelligence (the same population Account Intelligence, Sprint
8, already briefs), generates a Reverse Job Hunt Strategy — an
internal business-development playbook, not a proposal, answering why
to pursue this organisation, its consulting potential, why AI for U&I
is relevant, its current AI and governance maturity, the recommended
entry point, estimated probability of engagement, recommended
timeline, recommended first touch, and a suggested 90-day sequence of
actions.

Purely additive and read-only with respect to every other employee.
Does not modify demand_engine.py, ingest.py, account_intelligence_engine.py
or any config those own — every fact here is either read directly from
an upstream employee's own already-computed field
(organisation-profiles.json's buyingReadinessScore/Band, matched
categories, scale; account-intelligence-feed.json's outreach strategy
and executive summary, when it exists; a real opportunity-schema.json
record's own scores, when one exists; CRM's existingRelationship, when
present), or a small, clearly-labelled new heuristic this engine owns
(consulting-potential scale tiers, the entry-point vocabulary, the
90-day sequences). No existing scoring formula is touched or
recomputed differently than its own employee already computes it.

Read-only: never writes to organisation-profiles.json,
opportunity-schema.json, company-intelligence.json,
account-intelligence-feed.json, or any other employee's output.
"""

import copy
import json
import re
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
REVERSE_JOB_HUNT_DIR = RUNTIME_DIR.parent
AOS_DIR = REVERSE_JOB_HUNT_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_PATH = RUNTIME_DIR / "config" / "reverse-job-hunt-config.json"

DEMAND_INTELLIGENCE_DIR = AOS_DIR / "demand-intelligence"
PROFILES_PATH = DEMAND_INTELLIGENCE_DIR / "organisation-profiles.json"
OPPORTUNITY_SCHEMA_PATH = DEMAND_INTELLIGENCE_DIR / "opportunity-schema.json"
DEMAND_CATEGORIES_CONFIG_PATH = DEMAND_INTELLIGENCE_DIR / "runtime" / "config" / "demand-signal-categories.json"

ACCOUNT_INTELLIGENCE_FEED_PATH = AOS_DIR / "account-intelligence" / "runtime" / "output" / "account-intelligence-feed.json"
CRM_PATH = AOS_DIR / "crm" / "company-intelligence.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"

STRATEGIES_DIR = RUNTIME_DIR / "output" / "strategies"
FEED_PATH = RUNTIME_DIR / "output" / "reverse-job-hunt-feed.json"


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


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def ordered_matched_categories(matched_categories, demand_categories_config):
    """Strongest-first, same baseScore-descending convention every other
    downstream reader of demand-intelligence's categories already uses."""
    categories = demand_categories_config.get("categories", {})
    return sorted(matched_categories, key=lambda c: categories.get(c, {}).get("baseScore", 0), reverse=True)


def _dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


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


def _find_crm_entry(organisation, crm_data):
    for company in crm_data.get("companies", []):
        if company.get("companyName") == organisation:
            return company
    return None


def _find_account_intelligence_entry(organisation, ai_feed):
    for entry in ai_feed.get("briefs", []):
        if entry.get("organisation") == organisation:
            return entry
    return None


def _existing_relationship(crm_entry):
    if not crm_entry:
        return "none"
    return (crm_entry.get("existingRelationship") or "none").lower()


def _extract_scale_number(scale_text):
    """Same convention demand_engine.py's own _extract_scale_number()
    already uses (first number in the text) — reimplemented locally,
    not imported, keeping this employee's runtime self-contained like
    every other AOS employee."""
    if not scale_text:
        return None
    match = re.search(r"([\d,]+)", scale_text)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Section 1 — Why This Company Should Be Pursued
# --------------------------------------------------------------------------

def pursuit_reasons(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    reasons = _dedupe_preserve_order(
        config.get("categoryPursuitReason", {}).get(c) for c in matched
        if config.get("categoryPursuitReason", {}).get(c)
    )
    if not reasons:
        return ["Not enough public signal yet to justify active pursuit"]
    return reasons


# --------------------------------------------------------------------------
# Section 2 — Estimated Consulting Potential
# --------------------------------------------------------------------------

def consulting_potential(profile, opportunity_schema, pipeline_data, config):
    """Prefers a real opportunity-schema.json/pipeline.json record's own
    figures over a heuristic, exactly like Account Intelligence's own
    Opportunity Scorecard already does — never a second, contradicting
    estimate when a real one exists."""
    organisation = profile.get("organisation")
    opp = _find_opportunity_record(organisation, opportunity_schema)
    pipeline_entry = _find_pipeline_record(organisation, pipeline_data)

    if pipeline_entry and pipeline_entry.get("expectedRevenue") not in (None, "", "Not yet estimated"):
        return {
            "score": opp.get("scores", {}).get("expectedRevenue") if opp else None,
            "estimate": str(pipeline_entry["expectedRevenue"]),
            "source": "Revenue Hunter's pipeline.json (real estimate)",
        }
    if opp:
        return {
            "score": opp.get("scores", {}).get("expectedRevenue"),
            "estimate": f"{opp.get('scores', {}).get('expectedRevenue', 'Not specified')}/10 (opportunity-schema.json)",
            "source": "Real opportunity record (opportunity-schema.json)",
        }

    thresholds = config.get("consultingPotentialScaleThresholds", {})
    scale_number = _extract_scale_number(profile.get("scale"))
    if scale_number is None:
        return {"score": 3, "estimate": thresholds.get("unclearLabel", "Unclear"), "source": "Scale heuristic (no organisation size on record)"}
    if scale_number >= thresholds.get("veryLargeThreshold", 10000):
        return {"score": 10, "estimate": thresholds.get("veryLargeLabel", "High"), "source": "Scale heuristic"}
    if scale_number >= thresholds.get("largeThreshold", 1000):
        return {"score": 7, "estimate": thresholds.get("largeLabel", "Medium-High"), "source": "Scale heuristic"}
    if scale_number >= thresholds.get("midThreshold", 100):
        return {"score": 5, "estimate": thresholds.get("midLabel", "Medium"), "source": "Scale heuristic"}
    return {"score": 3, "estimate": thresholds.get("unclearLabel", "Unclear"), "source": "Scale heuristic"}


# --------------------------------------------------------------------------
# Section 3 — Why AI for U&I Is Relevant
# --------------------------------------------------------------------------

def relevance_reasons(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    reasons = _dedupe_preserve_order(
        config.get("categoryRelevanceReason", {}).get(c) for c in matched
        if config.get("categoryRelevanceReason", {}).get(c)
    )
    if not reasons:
        return ["Not enough public signal yet to identify a specific relevance angle"]
    return reasons


# --------------------------------------------------------------------------
# Section 4/5 — Current AI Maturity / Current Governance Maturity
# --------------------------------------------------------------------------

def ai_maturity(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    if not matched:
        return "Not enough signal to assess"
    return config.get("categoryAiMaturityLabel", {}).get(matched[0], "Not enough signal to assess")


def governance_maturity(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    if not matched:
        return "Not enough signal to assess"
    return config.get("categoryGovernanceMaturityLabel", {}).get(matched[0], "Not enough signal to assess")


# --------------------------------------------------------------------------
# Section 6 — Recommended Entry Point
# --------------------------------------------------------------------------

def entry_point(profile, crm_entry, config):
    """Six-value vocabulary. Precedence: an existing CRM relationship
    always wins; otherwise low confidence in the underlying signal
    always means the lightest-touch option; otherwise Buying Readiness
    Band plus whether an urgent category is present decides the rest.
    Every value is genuinely reachable (see EntryPointTests)."""
    relationship = _existing_relationship(crm_entry)
    if relationship not in ("none", ""):
        return "Warm introduction", f"CRM already records an existing relationship ({relationship}) — a warm path beats any cold one."

    confidence = profile.get("signals", [])[-1].get("confidence", "low") if profile.get("signals") else "low"
    band = profile.get("buyingReadinessBand", "Low")
    matched = profile.get("matchedCategories", [])
    urgent = any(c in matched for c in ("governance_trigger", "regulatory_trigger", "failure_trigger"))

    if confidence == "low":
        return "LinkedIn relationship", "Confidence in the underlying signal is low — start with the lightest-touch option and gather more signal before investing further."
    if band == "Very High" and urgent:
        return "Fractional advisory", "Buying readiness is Very High and an urgent governance/regulatory/failure category is on record — worth proposing a sustained arrangement directly."
    if band in ("Very High", "High"):
        return "Discovery workshop", f"Buying readiness is {band} — a structured discovery conversation is warranted now."
    if band == "Medium" and confidence == "high":
        return "Executive briefing", "Buying readiness is Medium with a high-confidence signal — a short executive briefing is a credible next step."
    if band == "Medium":
        return "Conference", "Buying readiness is Medium but confidence is not yet high — a lower-commitment touchpoint fits better than a direct ask."
    return "LinkedIn relationship", f"Buying readiness is {band} — start light and build the relationship before any direct ask."


# --------------------------------------------------------------------------
# Section 7 — Estimated Probability of Engagement
# --------------------------------------------------------------------------

def probability_of_engagement(profile):
    """Reuses Demand Intelligence's own Buying Readiness Score verbatim
    (0-100) as the probability-of-engagement estimate — the same
    underlying question ("how ready is this organisation"), never a
    second, independently-computed number that could disagree with it."""
    return profile.get("buyingReadinessScore", 0)


# --------------------------------------------------------------------------
# Section 8 — Recommended Timeline
# --------------------------------------------------------------------------

def recommended_timeline(profile, config):
    band = profile.get("buyingReadinessBand", "Low")
    return config.get("timelineByBand", {}).get(band, "Not specified")


# --------------------------------------------------------------------------
# Section 9 — Recommended First Touch
# --------------------------------------------------------------------------

def first_touch(profile, entry_point_value, demand_categories_config, config):
    organisation = profile.get("organisation", "this organisation")
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    category_label = demand_categories_config.get("categories", {}).get(matched[0], {}).get("label", "recent activity") if matched else "recent activity"
    template = config.get("firstTouchTemplateByEntryPoint", {}).get(entry_point_value, "")
    return template.format(organisation=organisation, categoryLabel=category_label)


# --------------------------------------------------------------------------
# Section 10 — Suggested 90-Day Sequence
# --------------------------------------------------------------------------

def ninety_day_sequence(entry_point_value, config):
    return config.get("ninetyDaySequenceByEntryPoint", {}).get(entry_point_value, [])


# --------------------------------------------------------------------------
# Expected Consulting ROI (dashboard sort key)
# --------------------------------------------------------------------------

def expected_consulting_roi(consulting_potential_score, probability_pct):
    """A new, honestly-labelled heuristic this engine introduces for
    dashboard sorting only: expected-value-style estimate = consulting
    potential (0-10) x probability of engagement (0-100), scaled back
    to a 0-10 range. Never fed back into or replacing any existing
    scoring formula elsewhere in AOS."""
    if consulting_potential_score is None:
        return None
    return round(consulting_potential_score * probability_pct / 100, 1)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_strategy_markdown(profile, pursuit, potential, relevance, ai_mat, gov_mat,
                              entry_point_value, entry_point_reason, probability_pct,
                              timeline, touch, sequence, roi, ai_feed_entry):
    organisation = profile.get("organisation", "Unknown")
    lines = [
        f"# Reverse Job Hunt Strategy — {organisation}",
        "",
        "*Internal business development playbook — not a proposal.*",
        "",
        "---",
        "",
        "## 1. Why This Company Should Be Pursued",
        "",
    ]
    lines += [f"- {r}" for r in pursuit]

    lines += ["", "---", "", "## 2. Estimated Consulting Potential", "",
              f"- **Estimate:** {potential['estimate']}",
              f"- *Source: {potential['source']}*"]

    lines += ["", "---", "", "## 3. Why AI for U&I Is Relevant", ""]
    lines += [f"- {r}" for r in relevance]

    lines += ["", "---", "", "## 4. Current AI Maturity", "", f"{ai_mat}"]
    lines += ["", "---", "", "## 5. Current Governance Maturity", "", f"{gov_mat}"]

    lines += ["", "---", "", "## 6. Recommended Entry Point", "",
              f"**{entry_point_value}**", "", entry_point_reason]

    lines += ["", "---", "", "## 7. Estimated Probability of Engagement", "",
              f"{probability_pct}% (reusing Demand Intelligence's own Buying Readiness Score)"]

    lines += ["", "---", "", "## 8. Recommended Timeline", "", timeline]

    lines += ["", "---", "", "## 9. Recommended First Touch", "", touch]

    lines += ["", "---", "", "## 10. Suggested Sequence of Actions Over 90 Days", ""]
    lines += [f"- {step}" for step in sequence]

    lines += ["", "---", "", "## Expected Consulting ROI (dashboard sort key)", "",
              f"{roi if roi is not None else 'Not yet estimated'} (0-10 scale — consulting potential x probability of engagement, "
              "an expected-value-style estimate this engine introduces; does not replace or feed back into any existing score elsewhere in AOS)."]

    if ai_feed_entry:
        lines += [
            "", "---", "",
            "## Cross-reference: Account Intelligence's Own Outreach Strategy",
            "",
            f"Account Intelligence (a separate brief, a different question — the first-touch *framing*, not the BD entry-point "
            f"*channel* this engine recommends) currently recommends: **{ai_feed_entry.get('outreachStrategy', 'Not available')}**. "
            "Shown for consistency-checking only — this engine's own Section 6 recommendation above is not overridden by it.",
        ]

    lines += ["", "---", "", "*Preparation only — nothing here is sent automatically.*"]
    return "\n".join(lines)


def build_strategy(profile, opportunity_schema, pipeline_data, crm_data, ai_feed,
                    demand_categories_config, config):
    organisation = profile.get("organisation", "Unknown")
    crm_entry = _find_crm_entry(organisation, crm_data)
    ai_feed_entry = _find_account_intelligence_entry(organisation, ai_feed)

    pursuit = pursuit_reasons(profile, demand_categories_config, config)
    potential = consulting_potential(profile, opportunity_schema, pipeline_data, config)
    relevance = relevance_reasons(profile, demand_categories_config, config)
    ai_mat = ai_maturity(profile, demand_categories_config, config)
    gov_mat = governance_maturity(profile, demand_categories_config, config)
    entry_point_value, entry_point_reason = entry_point(profile, crm_entry, config)
    probability_pct = probability_of_engagement(profile)
    timeline = recommended_timeline(profile, config)
    touch = first_touch(profile, entry_point_value, demand_categories_config, config)
    sequence = ninety_day_sequence(entry_point_value, config)
    roi = expected_consulting_roi(potential.get("score"), probability_pct)

    markdown = render_strategy_markdown(
        profile, pursuit, potential, relevance, ai_mat, gov_mat,
        entry_point_value, entry_point_reason, probability_pct,
        timeline, touch, sequence, roi, ai_feed_entry,
    )

    feed_entry = {
        "organisation": organisation,
        "industry": profile.get("industry") or "Not specified",
        "buyingReadinessBand": profile.get("buyingReadinessBand", "Low"),
        "entryPoint": entry_point_value,
        "probabilityOfEngagement": probability_pct,
        "recommendedTimeline": timeline,
        "consultingPotentialEstimate": potential["estimate"],
        "expectedConsultingRoi": roi,
        "lastSeen": profile.get("lastSeen", ""),
        "strategyPath": None,  # filled in by generate.py once the file path is known
    }
    return markdown, feed_entry
