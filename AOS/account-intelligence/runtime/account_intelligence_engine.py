"""
Account Intelligence Engine (AOS Sprint 8)

Turns every organisation Demand Intelligence has already qualified
(any key in demand-intelligence/organisation-profiles.json — the same
high-confidence gate collectors/demand_signals.py already applies
before a signal is ever recorded there) into a ten-section Executive
Account Intelligence Brief: an internal strategic briefing to prepare
AI for U&I before any outreach, not a proposal.

Everything here is a deterministic function of already-computed,
already-real facts:
  - demand-intelligence/organisation-profiles.json (signals, matched
    categories, Overall Demand Score, Buying Readiness Score/band,
    recommended services, industry/scale/region) — read-only, and the
    one input every section ultimately traces back to.
  - demand-intelligence/runtime/config/demand-signal-categories.json —
    read-only, for each matched category's own label/baseScore, so
    this module never re-invents which category is "strongest."
  - config/account-intelligence-config.json — this module's own new
    lookup tables (governance risks, stakeholder titles, deployment
    stage/maturity labels, regulatory context by region, outreach
    strategy, conversation starters, scorecard heuristics), each keyed
    by the same five category keys.
  - config/supporting-assets.json — the real, existing AI for U&I
    website pages/products/channels (copied verbatim from
    sales-director/runtime/config/practitioner-bank.json and
    aiforu-platform/src/lib/constants.ts — see that file's own header
    comment), ranked by domainTags overlap, never invented.
  - demand-intelligence/opportunity-schema.json (optional) and
    crm/company-intelligence.json (optional) — read-only cross-
    references, exactly like demand_engine.py's own Part 8 feedback
    weighting already does, so Section 9's scorecard can use a real
    opportunity record's own scores/priority when one exists, rather
    than a second, independent estimate.

No section here invents a fact organisation-profiles.json doesn't
already contain: decision-maker TITLES are suggested (never names),
missing data is stated as "Not specified"/"Not enough public signal"
rather than guessed, and Section 6/7/9's own new derivations
(outreach strategy, conversation starters, sales-cycle/competition-
risk heuristics) are explicitly labelled as heuristics rather than
presented as fact. Does not modify demand-intelligence in any way —
every read here is read-only, consistent with every other downstream
employee's own cross-reference of another employee's already-written
output (CRM reading Sales Director's feed, demand_engine.py reading
CRM/pipeline/Sales Director's feed, etc.).
"""

import copy
import json
import re
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
ACCOUNT_INTELLIGENCE_DIR = RUNTIME_DIR.parent
AOS_DIR = ACCOUNT_INTELLIGENCE_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_PATH = RUNTIME_DIR / "config" / "account-intelligence-config.json"
ASSETS_PATH = RUNTIME_DIR / "config" / "supporting-assets.json"

DEMAND_INTELLIGENCE_DIR = AOS_DIR / "demand-intelligence"
PROFILES_PATH = DEMAND_INTELLIGENCE_DIR / "organisation-profiles.json"
OPPORTUNITY_SCHEMA_PATH = DEMAND_INTELLIGENCE_DIR / "opportunity-schema.json"
DEMAND_CATEGORIES_CONFIG_PATH = DEMAND_INTELLIGENCE_DIR / "runtime" / "config" / "demand-signal-categories.json"

CRM_PATH = AOS_DIR / "crm" / "company-intelligence.json"
SALES_FEED_PATH = AOS_DIR / "sales-director" / "runtime" / "output" / "ceo-advisor-feed.json"

BRIEFS_DIR = RUNTIME_DIR / "output" / "account-briefs"
FEED_PATH = RUNTIME_DIR / "output" / "account-intelligence-feed.json"

# Credited, verbatim copy of demand-intelligence's own extractors/base.py
# VENDOR_BLOCKLIST — reused here for the opposite purpose (detecting a
# vendor genuinely mentioned in a signal's own text, not excluding one
# from being mistaken for the organisation), so Section 2's "AI vendors
# involved" is a real text match, never a fabricated list.
VENDOR_NAMES = [
    "Microsoft", "Copilot", "OpenAI", "ChatGPT", "GPT-4", "GPT-5",
    "Anthropic", "Claude", "Google", "Gemini", "Bard", "Amazon", "AWS",
    "IBM", "Watsonx", "Salesforce", "Einstein", "Meta AI", "Llama",
    "Mistral", "Cohere", "Nvidia", "Azure", "Vertex AI",
]

GOVERNANCE_RISK_ORDER = [
    "Human oversight", "Model governance", "Operational controls", "Privacy",
    "Third-party AI risk", "Monitoring", "Incident management",
    "Audit evidence", "Regulatory readiness",
]


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


def load_supporting_assets():
    return load_json(ASSETS_PATH, {"products": [], "websitePages": [], "channels": []})


def load_demand_categories_config():
    return load_json(DEMAND_CATEGORIES_CONFIG_PATH, {"categories": {}})


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def ordered_matched_categories(matched_categories, demand_categories_config):
    """Strongest-first — the same baseScore-descending order
    demand_engine.py's own compute_overall_demand_score() already uses
    to decide which matched category is "primary." Every section below
    that needs one dominant category (AI maturity, deployment stage,
    strategic objective) uses this same order rather than a second,
    independently-invented ranking."""
    categories = demand_categories_config.get("categories", {})
    return sorted(matched_categories, key=lambda c: categories.get(c, {}).get("baseScore", 0), reverse=True)


def most_recent_confidence(profile):
    signals = profile.get("signals", [])
    if not signals:
        return "low"
    return signals[-1].get("confidence", "low")


def _dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# --------------------------------------------------------------------------
# Section 1 — Company Profile
# --------------------------------------------------------------------------

def company_profile(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    region = profile.get("region") or "Not specified"
    regulatory_context = config.get("regionRegulatoryContext", {}).get(
        region, config.get("regionRegulatoryContext", {}).get("Not specified", "Not specified"))

    maturity = "Not enough signal to assess"
    if matched:
        maturity = config.get("categoryAiMaturityLabel", {}).get(matched[0], maturity)

    objectives = _dedupe_preserve_order(
        config.get("categoryStrategicObjective", {}).get(c) for c in matched
        if config.get("categoryStrategicObjective", {}).get(c)
    )
    priorities = "; ".join(objectives) if objectives else "Not enough public signal yet to infer business priorities"

    initiatives = [s.get("eventSummary") for s in profile.get("signals", []) if s.get("eventSummary")]

    return {
        "industry": profile.get("industry") or "Not specified",
        "headquarters": "Not specified — not captured by Demand Intelligence's current signal extraction",
        "geographicFootprint": region,
        "approximateSize": profile.get("scale") or "Not specified",
        "publicAiInitiatives": initiatives or ["No public AI initiative details recorded yet"],
        "aiMaturityLevel": maturity,
        "regulatoryEnvironment": regulatory_context,
        "businessPriorities": priorities,
    }


# --------------------------------------------------------------------------
# Section 2 — AI Deployment Intelligence
# --------------------------------------------------------------------------

def detect_vendors(profile):
    text = " ".join(s.get("eventSummary", "") or "" for s in profile.get("signals", [])).lower()
    found = [v for v in VENDOR_NAMES if v.lower() in text]
    return _dedupe_preserve_order(found) or ["Not specified — no named AI vendor detected in public signal text"]


def ai_deployment_intelligence(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    labels = [demand_categories_config.get("categories", {}).get(c, {}).get("label", c) for c in matched]
    stage = config.get("categoryDeploymentStage", {}).get(matched[0], "Not specified") if matched else "Not specified"
    objective = config.get("categoryStrategicObjective", {}).get(matched[0], "Not specified") if matched else "Not specified"

    announcements = [
        {"date": s.get("date"), "summary": s.get("eventSummary"), "url": s.get("sourceUrl")}
        for s in profile.get("signals", [])
    ]

    return {
        "technologies": labels or ["Not specified"],
        "stage": stage,
        "scale": profile.get("scale") or "Not specified",
        "publicAnnouncements": announcements,
        "vendorsInvolved": detect_vendors(profile),
        "strategicObjective": objective,
    }


# --------------------------------------------------------------------------
# Section 3 — Governance Risk Assessment
# --------------------------------------------------------------------------

def governance_risk_assessment(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    organisation = profile.get("organisation", "This organisation")

    seen_risks = set()
    risks = []
    for category in matched:
        for item in config.get("categoryToGovernanceRisks", {}).get(category, []):
            risk = item["risk"]
            if risk in seen_risks:
                continue
            seen_risks.add(risk)
            why = item["why"].format(organisation=organisation)
            risks.append({"risk": risk, "why": why})

    risks.sort(key=lambda r: GOVERNANCE_RISK_ORDER.index(r["risk"]) if r["risk"] in GOVERNANCE_RISK_ORDER else 99)
    return risks


# --------------------------------------------------------------------------
# Section 4 — Service Fit
# --------------------------------------------------------------------------

def service_fit(profile):
    """Reuses demand_engine.py's own recommendedServices verbatim — an
    already-ranked, real vote-count-based prediction (Sprint 6, Part 3)
    — never a second service-ranking algorithm. Confidence is a plain
    read of that existing rank position: 1st = High, 2nd = Medium,
    3rd+ = Low."""
    services = profile.get("recommendedServices", [])
    ranked = []
    for i, service in enumerate(services):
        confidence = "High" if i == 0 else "Medium" if i == 1 else "Low"
        ranked.append({"service": service, "confidence": confidence})
    return ranked


# --------------------------------------------------------------------------
# Section 5 — Decision Makers (titles only, never invented names)
# --------------------------------------------------------------------------

def decision_makers(profile, demand_categories_config, config):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    titles = []
    for category in matched:
        for title in config.get("categoryToStakeholderTitles", {}).get(category, []):
            if title not in titles:
                titles.append(title)
    return titles or ["Not enough signal to suggest a specific stakeholder title yet"]


# --------------------------------------------------------------------------
# Section 6 — Outreach Strategy
# --------------------------------------------------------------------------

def outreach_strategy(profile, config):
    """Six-value vocabulary this brief answers a different question
    with than demand_engine.py's own recommendedAction: recommendedAction
    is Demand Intelligence's next INTERNAL pipeline action; this is how
    the FIRST TOUCH with this organisation should be framed. Both are
    deterministic re-labellings of the exact same already-computed
    buyingReadinessBand/confidence/matchedCategories fields — never a
    second scoring engine, no new score computed here."""
    band = profile.get("buyingReadinessBand", "Low")
    confidence = most_recent_confidence(profile)
    matched = profile.get("matchedCategories", [])
    reasons = config.get("outreachStrategy", {}).get("reasons", {})

    if confidence == "low":
        strategy = "Wait"
    elif "failure_trigger" in matched or band == "Very High":
        strategy = "Direct proposal"
    elif band == "High":
        strategy = "Discovery workshop"
    elif band == "Medium" and confidence == "high":
        strategy = "Thought leadership"
    elif band == "Medium":
        strategy = "Connection first"
    else:
        strategy = "Monitor"

    reason = reasons.get(strategy, "").format(band=band, confidence=confidence)
    return strategy, reason


# --------------------------------------------------------------------------
# Section 7 — Conversation Starters (professional, never a sales pitch)
# --------------------------------------------------------------------------

def conversation_starters(profile, demand_categories_config, config):
    organisation = profile.get("organisation", "this organisation")
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    templates = config.get("conversationStarterTemplates", {})

    starters = []
    for category in matched:
        for template in templates.get(category, []):
            starters.append(template.format(organisation=organisation))
        if len(starters) >= 3:
            break

    if len(starters) < 3:
        for template in templates.get("generic", []):
            candidate = template.format(organisation=organisation)
            if candidate not in starters:
                starters.append(candidate)
            if len(starters) >= 3:
                break

    return starters[:3]


# --------------------------------------------------------------------------
# Section 8 — Supporting Assets
# --------------------------------------------------------------------------

def _domain_tags_for_matched(matched_categories, config):
    tags = []
    for category in matched_categories:
        tags.extend(config.get("categoryToDomainTags", {}).get(category, []))
    return set(tags)


def supporting_assets(profile, demand_categories_config, config, assets, max_items=6):
    matched = ordered_matched_categories(profile.get("matchedCategories", []), demand_categories_config)
    domain_tags = _domain_tags_for_matched(matched, config)

    all_assets = assets.get("products", []) + assets.get("websitePages", []) + assets.get("channels", [])

    matched_items = []
    general_items = []
    for asset in all_assets:
        overlap = len(domain_tags & set(asset.get("domainTags", [])))
        if asset.get("isGeneral"):
            general_items.append(asset)
        elif overlap > 0:
            matched_items.append((overlap, asset))
        # assets with no domain overlap and not marked general are simply
        # not relevant to this organisation — never shown

    matched_items.sort(key=lambda pair: pair[0], reverse=True)
    ranked = [a for _, a in matched_items] + general_items
    return ranked[:max_items]


# --------------------------------------------------------------------------
# Section 9 — Opportunity Scorecard
# --------------------------------------------------------------------------

def _find_opportunity_record(organisation, opportunity_schema):
    for opp in opportunity_schema.get("opportunities", []):
        if opp.get("organisation") == organisation:
            return opp
    return None


def opportunity_scorecard(profile, opportunity_schema, config):
    """Reuses a real opportunity-schema.json record's own already-scored
    11-dimension scores/priorityScore when this organisation has one
    (produced by ingest.py's own unmodified scoring engine) rather than
    a second, independent estimate. Falls back to Buying Readiness
    Score/Overall Demand Score-derived estimates only when no real
    opportunity record exists yet, clearly labelled as such."""
    organisation = profile.get("organisation")
    opp = _find_opportunity_record(organisation, opportunity_schema)
    band = profile.get("buyingReadinessBand", "Low")

    scorecard_config = config.get("opportunityScorecard", {})
    sales_cycle = scorecard_config.get("estimatedSalesCycleByBand", {}).get(band, "Not specified")

    signal_count = len(profile.get("signals", []))
    threshold = scorecard_config.get("competitionRiskBySignalCount", {}).get("threshold", 3)
    if signal_count >= threshold:
        competition_risk = scorecard_config.get("competitionRiskBySignalCount", {}).get("atOrAboveThreshold", "Not specified")
    else:
        competition_risk = scorecard_config.get("competitionRiskBySignalCount", {}).get("belowThreshold", "Not specified")

    if opp:
        scores = opp.get("scores", {})
        return {
            "strategicValue": scores.get("strategicValue"),
            "revenuePotential": scores.get("expectedRevenue"),
            "buyingReadiness": profile.get("buyingReadinessScore", 0),
            "relationshipValue": scores.get("relationshipValue"),
            "competitionRisk": competition_risk,
            "estimatedSalesCycle": sales_cycle,
            "overallPriority": opp.get("priorityScore"),
            "source": "Real opportunity record (opportunity-schema.json)",
        }

    return {
        "strategicValue": round(profile.get("overallDemandScore", 0) / 10),
        "revenuePotential": "Not yet estimated — no opportunity record on record for this organisation",
        "buyingReadiness": profile.get("buyingReadinessScore", 0),
        "relationshipValue": "Not yet estimated",
        "competitionRisk": competition_risk,
        "estimatedSalesCycle": sales_cycle,
        "overallPriority": profile.get("buyingReadinessScore", 0),
        "source": "Estimated from Demand Intelligence profile only — no opportunity record yet",
    }


# --------------------------------------------------------------------------
# Section 10 — Executive Summary (<=300 words, always enforced)
# --------------------------------------------------------------------------

def executive_summary(profile, company, deployment, top_risk, top_service, strategy, scorecard, max_words=300):
    # Deliberately no .lower() on any of these fragments — several
    # (e.g. "AI Adoption", "Third-party AI risk") contain "AI" as an
    # acronym, and forcing lowercase mid-sentence turned it into "ai".
    organisation = profile.get("organisation", "This organisation")
    lines = [
        f"{organisation} ({company['industry']}, {company['geographicFootprint']}) is currently at the "
        f"\"{deployment['stage']}\" stage: {deployment['strategicObjective']}.",
    ]
    if top_risk:
        lines.append(f"The most likely governance gap is {top_risk['risk']} — {top_risk['why']}")
    if top_service:
        lines.append(f"The best-fit AI for U&I service is {top_service['service']} ({top_service['confidence']} confidence).")
    lines.append(f"Recommended opening move: {strategy[0]} — {strategy[1]}")
    lines.append(
        f"Overall priority is {scorecard['overallPriority']}/100 with buying readiness {scorecard['buyingReadiness']}/100 "
        f"({profile.get('buyingReadinessBand', 'Low')} band), estimated sales cycle {scorecard['estimatedSalesCycle']}."
    )

    summary = " ".join(lines)
    words = summary.split()
    if len(words) > max_words:
        summary = " ".join(words[:max_words]).rstrip(".,;:") + "…"
    return summary


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_brief_markdown(profile, company, deployment, risks, services, titles, strategy, starters, assets, scorecard, summary):
    organisation = profile.get("organisation", "Unknown")
    lines = [
        f"# Account Intelligence Brief — {organisation}",
        "",
        f"*Internal strategic briefing — not a proposal. Prepared {profile.get('lastSeen', '')}.*",
        "",
        "---",
        "",
        "## Section 10 — Executive Summary",
        "",
        summary,
        "",
        "---",
        "",
        "## Section 1 — Company Profile",
        "",
        f"- **Industry:** {company['industry']}",
        f"- **Headquarters:** {company['headquarters']}",
        f"- **Geographic footprint:** {company['geographicFootprint']}",
        f"- **Approximate size:** {company['approximateSize']}",
        f"- **AI maturity level:** {company['aiMaturityLevel']}",
        f"- **Regulatory environment:** {company['regulatoryEnvironment']}",
        f"- **Business priorities:** {company['businessPriorities']}",
        "",
        "**Public AI initiatives:**",
    ]
    lines += [f"- {i}" for i in company["publicAiInitiatives"]]

    lines += [
        "",
        "---",
        "",
        "## Section 2 — AI Deployment Intelligence",
        "",
        f"- **Technologies/categories observed:** {', '.join(deployment['technologies'])}",
        f"- **Stage of deployment:** {deployment['stage']}",
        f"- **Scale of deployment:** {deployment['scale']}",
        f"- **AI vendors involved:** {', '.join(deployment['vendorsInvolved'])}",
        f"- **Strategic objective:** {deployment['strategicObjective']}",
        "",
        "**Public announcements:**",
    ]
    for a in deployment["publicAnnouncements"]:
        url_part = f" — [source]({a['url']})" if a.get("url") else ""
        lines.append(f"- {a.get('date', '')}: {a.get('summary', '')}{url_part}")
    if not deployment["publicAnnouncements"]:
        lines.append("- None recorded yet")

    lines += ["", "---", "", "## Section 3 — Governance Risk Assessment", ""]
    if risks:
        for r in risks:
            lines.append(f"- **{r['risk']}** — {r['why']}")
    else:
        lines.append("- Not enough signal yet to assess likely governance risks.")

    lines += ["", "---", "", "## Section 4 — Service Fit", ""]
    if services:
        for s in services:
            lines.append(f"- **{s['service']}** — {s['confidence']} confidence")
    else:
        lines.append("- Not enough signal yet to rank service fit.")

    lines += ["", "---", "", "## Section 5 — Decision Makers", "", "_Titles only — no names invented._", ""]
    lines += [f"- {t}" for t in titles]

    lines += [
        "", "---", "", "## Section 6 — Outreach Strategy", "",
        f"**Recommended approach:** {strategy[0]}", "", strategy[1],
    ]

    lines += ["", "---", "", "## Section 7 — Conversation Starters", ""]
    lines += [f"{i}. {s}" for i, s in enumerate(starters, start=1)]

    lines += ["", "---", "", "## Section 8 — Supporting Assets", ""]
    if assets:
        for a in assets:
            lines.append(f"- **{a['title']}** ({a['type']}) — {a['url']}")
    else:
        lines.append("- No specifically relevant assets identified yet.")

    lines += [
        "", "---", "", "## Section 9 — Opportunity Scorecard", "",
        f"- **Strategic Value:** {scorecard['strategicValue']}",
        f"- **Revenue Potential:** {scorecard['revenuePotential']}",
        f"- **Buying Readiness:** {scorecard['buyingReadiness']}/100",
        f"- **Relationship Value:** {scorecard['relationshipValue']}",
        f"- **Competition Risk:** {scorecard['competitionRisk']}",
        f"- **Estimated Sales Cycle:** {scorecard['estimatedSalesCycle']}",
        f"- **Overall Priority:** {scorecard['overallPriority']}",
        "",
        f"*Source: {scorecard['source']}*",
        "",
    ]
    return "\n".join(lines)


def build_brief(profile, opportunity_schema, demand_categories_config, config, assets):
    """The full Section 1-10 pipeline for one organisation's already-
    persisted Demand Intelligence profile. Returns (markdown, feed_entry) —
    feed_entry is the compact, searchable record account-intelligence-feed.json
    stores; markdown is the full brief written to output/account-briefs/."""
    company = company_profile(profile, demand_categories_config, config)
    deployment = ai_deployment_intelligence(profile, demand_categories_config, config)
    risks = governance_risk_assessment(profile, demand_categories_config, config)
    services = service_fit(profile)
    titles = decision_makers(profile, demand_categories_config, config)
    strategy = outreach_strategy(profile, config)
    starters = conversation_starters(profile, demand_categories_config, config)
    assets_ranked = supporting_assets(profile, demand_categories_config, config, assets)
    scorecard = opportunity_scorecard(profile, opportunity_schema, config)
    summary = executive_summary(
        profile, company, deployment,
        risks[0] if risks else None,
        services[0] if services else None,
        strategy, scorecard,
    )

    markdown = render_brief_markdown(profile, company, deployment, risks, services, titles, strategy, starters, assets_ranked, scorecard, summary)

    organisation = profile.get("organisation", "Unknown")
    feed_entry = {
        "organisation": organisation,
        "industry": company["industry"],
        "region": company["geographicFootprint"],
        "buyingReadinessBand": profile.get("buyingReadinessBand", "Low"),
        "outreachStrategy": strategy[0],
        "overallPriority": scorecard["overallPriority"],
        "lastSeen": profile.get("lastSeen", ""),
        "briefPath": None,  # filled in by generate.py once the file path is known
        "executiveSummary": summary,
        # AOS Sprint 12 — additive, structured fields so downstream
        # consumers (Sales Director's Executive Proposal Generator)
        # can trace every proposal section back to this brief's own
        # already-computed data, without parsing the rendered markdown.
        "companyProfile": company,
        "deploymentStage": deployment["stage"],
        "aiInitiatives": company["publicAiInitiatives"],
        "governanceRisks": risks,
        "serviceFit": services,
        "decisionMakerTitles": titles,
        "supportingAssets": assets_ranked,
    }
    return markdown, feed_entry
