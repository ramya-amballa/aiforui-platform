"""
Executive Brand Intelligence Engine (AOS Sprint 15)

Manages AI for U&I's thought-leadership plan automatically — but every
section is a read of real data another employee already computed, not
a second, independently-invented signal:

  - Companies to Engage:    demand-intelligence/organisation-profiles.json's
                            own buyingReadinessScore, this week's window.
  - Executives to Follow:   relationship-intelligence/relationship-profiles.json's
                            own tracked people (real names, founder-
                            entered) — never a fabricated name.
  - Topics to Write /
    Newsletter Themes:      the most common governance risk and demand-
                            signal category across this week's Account
                            Intelligence briefs and organisation profiles.
  - Products to Update /
    Whitepapers to Publish: the shared supporting-assets.json catalogue
                            (the same one Account Intelligence's own
                            supporting_assets() ranks), re-ranked against
                            this week's trending domain tags.
  - Conferences to Monitor: relationship-profiles.json's own
                            upcomingConference fields, deduplicated.
  - GitHub Improvements /
    LinkedIn Strategy:      a single, honest, evidence-cited suggestion
                            tied to this week's trending risk/domain —
                            never a claim about the repo's actual state
                            (star count, issues, etc.), since AOS has no
                            GitHub API integration.

Visibility Impact, Lead Generation Potential and Expected Consulting
Influence are explicit heuristics grounded in real counts (how many
companies qualify, how many are high-readiness, how many services rank
High confidence this week) — never an arbitrary number.
"""

import copy
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
EXECUTIVE_BRAND_INTELLIGENCE_DIR = RUNTIME_DIR.parent
AOS_DIR = EXECUTIVE_BRAND_INTELLIGENCE_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_PATH = RUNTIME_DIR / "config" / "executive-brand-intelligence-config.json"
HISTORY_PATH = RUNTIME_DIR / "brand-plan-history.json"
FEED_PATH = AOS_DIR / "output" / "executive-brand-intelligence" / "executive-brand-intelligence-feed.json"

DEMAND_CATEGORIES_PATH = AOS_DIR / "demand-intelligence" / "runtime" / "config" / "demand-signal-categories.json"
ORGANISATION_PROFILES_PATH = AOS_DIR / "demand-intelligence" / "organisation-profiles.json"
ACCOUNT_INTELLIGENCE_FEED_PATH = AOS_DIR / "output" / "account-intelligence" / "account-intelligence-feed.json"
RELATIONSHIP_PROFILES_PATH = AOS_DIR / "relationship-intelligence" / "relationship-profiles.json"
SUPPORTING_ASSETS_PATH = AOS_DIR / "account-intelligence" / "runtime" / "config" / "supporting-assets.json"
ACCOUNT_INTELLIGENCE_CONFIG_PATH = AOS_DIR / "account-intelligence" / "runtime" / "config" / "account-intelligence-config.json"

TODAY = date.today()

DEFAULT_HISTORY = {"weeks": []}


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


# --------------------------------------------------------------------------
# Windowing — same "lastSeen within N days" pattern demand_engine.py's own
# top-organisations-this-week.json already uses.
# --------------------------------------------------------------------------

def _within_window(date_str, today, window_days):
    if not date_str:
        return False
    try:
        parsed = datetime.fromisoformat(date_str).date()
    except ValueError:
        return False
    return (today - parsed).days <= window_days


def organisations_this_week(org_profiles, config, today=None):
    today = today or TODAY
    window = config.get("windowDays", 7)
    return [
        p for p in org_profiles.get("organisations", {}).values()
        if _within_window(p.get("lastSeen"), today, window)
    ]


def briefs_this_week(account_feed, org_names_this_week):
    names = set(org_names_this_week)
    return [b for b in account_feed.get("briefs", []) if b.get("organisation") in names]


# --------------------------------------------------------------------------
# Companies to Engage
# --------------------------------------------------------------------------

def companies_to_engage(orgs_this_week, config):
    ranked = sorted(orgs_this_week, key=lambda o: o.get("buyingReadinessScore", 0), reverse=True)
    count = config.get("companiesToEngageCount", 5)
    return [
        {"organisation": o["organisation"], "industry": o.get("industry", "Not specified"),
         "buyingReadinessBand": o.get("buyingReadinessBand", "Low"),
         "buyingReadinessScore": o.get("buyingReadinessScore", 0)}
        for o in ranked[:count]
    ]


# --------------------------------------------------------------------------
# Executives to Follow — real, founder-tracked people only
# --------------------------------------------------------------------------

def executives_to_follow(relationship_profiles):
    people = relationship_profiles.get("people", {})
    return [
        {"person": p.get("person"), "company": p.get("company"), "role": p.get("role")}
        for p in people.values()
    ]


# --------------------------------------------------------------------------
# Trending domain / governance risk — the real evidence behind Topics to
# Write, Newsletter Themes, GitHub Improvements and LinkedIn Strategy.
# --------------------------------------------------------------------------

def trending_domain(orgs_this_week, demand_categories_config):
    """Returns (label, category_key, count) for the most common matched
    demand-signal category across this week's qualified organisations —
    category_key is what categoryToDomainTags is keyed by, so
    assets_to_update() can look up its real domainTags rather than
    guessing from the label text."""
    labels = demand_categories_config.get("categories", {})
    counter = Counter()
    for org in orgs_this_week:
        for key in org.get("matchedCategories", []):
            if key in labels:
                counter[key] += 1
    if not counter:
        return None, None, 0
    key, count = counter.most_common(1)[0]
    return labels[key].get("label"), key, count


def trending_governance_risk(briefs):
    counter = Counter()
    for brief in briefs:
        for risk in brief.get("governanceRisks", []):
            name = risk.get("risk")
            if name:
                counter[name] += 1
    if not counter:
        return None, 0
    risk, count = counter.most_common(1)[0]
    return risk, count


def topics_to_write(top_domain, top_domain_count, top_risk, top_risk_count, orgs_this_week, config):
    if not top_domain and not top_risk:
        return []
    industries = Counter(o.get("industry") for o in orgs_this_week if o.get("industry"))
    top_industry = industries.most_common(1)[0][0] if industries else "AI for U&I's client base"

    topics = []
    if top_risk:
        topics.append(f"{top_risk}: what {top_industry} leaders should do next "
                       f"(seen across {top_risk_count} qualified account(s) this week)")
    if top_domain:
        topics.append(f"{top_domain}: this week's most common signal across {top_domain_count} organisation(s)")
    topics.append("A practitioner's field notes: what changed in AI governance this week")
    return topics[:config.get("topicsToWriteCount", 3)]


# --------------------------------------------------------------------------
# Products to Update / Whitepapers to Publish — the shared supporting-
# assets catalogue, re-ranked against this week's trending domain tags,
# same domain-tag-overlap pattern account_intelligence_engine.py's own
# supporting_assets() uses, credited rather than re-imported (each
# employee stays self-contained).
# --------------------------------------------------------------------------

def assets_to_update(assets, top_domain_key, account_intelligence_config, config):
    """Reuses account-intelligence-config.json's own categoryToDomainTags
    bridge (credited, not re-imported — see that config's own '_note')
    rather than inventing a second category->domainTags mapping."""
    all_assets = assets.get("products", []) + assets.get("websitePages", []) + assets.get("channels", [])
    domain_tags = set(account_intelligence_config.get("categoryToDomainTags", {}).get(top_domain_key, [])) if top_domain_key else set()

    if domain_tags:
        ranked = sorted(all_assets, key=lambda a: len(domain_tags & set(a.get("domainTags", []))), reverse=True)
    else:
        ranked = all_assets
    count = config.get("assetsToUpdateCount", 4)
    return [{"title": a["title"], "type": a["type"], "url": a["url"]} for a in ranked[:count]]


def whitepapers_to_publish(assets):
    all_assets = assets.get("products", []) + assets.get("websitePages", []) + assets.get("channels", [])
    return [{"title": a["title"], "type": a["type"], "url": a["url"]}
            for a in all_assets if "whitepaper" in a.get("type", "").lower() or "playbook" in a.get("type", "").lower()]


# --------------------------------------------------------------------------
# Conferences to Monitor — relationship-profiles.json's own founder-
# entered upcomingConference fields, deduplicated by name.
# --------------------------------------------------------------------------

def conferences_to_monitor(relationship_profiles):
    seen = {}
    for person in relationship_profiles.get("people", {}).values():
        conf = person.get("upcomingConference")
        if conf and conf.get("name"):
            seen.setdefault(conf["name"], conf.get("date"))
    return [{"name": name, "date": d} for name, d in sorted(seen.items(), key=lambda kv: kv[1] or "")]


# --------------------------------------------------------------------------
# GitHub Improvements / LinkedIn Strategy — one honest, evidence-cited
# suggestion each, never a claim about the repo's or LinkedIn account's
# actual current state (no GitHub/LinkedIn API integration in AOS).
# --------------------------------------------------------------------------

def github_improvement_suggestion(top_domain, top_risk):
    if not top_domain and not top_risk:
        return "Not enough signal this week to recommend a specific GitHub update."
    subject = top_risk or top_domain
    return (f"Review README/resource pages for coverage of '{subject}' — this week's most common signal "
            f"across qualified accounts — and add or update a page if it's thin.")


def linkedin_strategy(briefs, top_risk):
    if not briefs:
        return "Not enough qualified accounts this week to recommend a specific LinkedIn focus."
    strategy_counter = Counter(b.get("outreachStrategy") for b in briefs if b.get("outreachStrategy"))
    if not strategy_counter:
        return "Not enough signal this week to recommend a specific LinkedIn focus."
    top_strategy, count = strategy_counter.most_common(1)[0]
    subject = f" — lead with {top_risk}" if top_risk else ""
    return f"{count} of {len(briefs)} qualified account(s) this week point to '{top_strategy}'{subject}."


# --------------------------------------------------------------------------
# Estimates — explicit heuristics, grounded in real counts, never an
# arbitrary number.
# --------------------------------------------------------------------------

def _tier(value, thresholds):
    if value >= thresholds.get("high", 999999):
        return "High"
    if value >= thresholds.get("medium", 999999):
        return "Medium"
    return "Low"


def visibility_impact(orgs_this_week, config):
    return _tier(len(orgs_this_week), config.get("visibilityImpactThresholds", {}))


def lead_generation_potential(orgs_this_week, config):
    high_readiness = sum(1 for o in orgs_this_week if o.get("buyingReadinessBand") in ("High", "Very High"))
    return _tier(high_readiness, config.get("leadGenerationThresholds", {}))


def expected_consulting_influence(briefs, config):
    high_confidence_services = sum(
        1 for b in briefs for s in b.get("serviceFit", []) if s.get("confidence") == "High"
    )
    return _tier(high_confidence_services, config.get("consultingInfluenceThresholds", {}))


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def build_weekly_plan(org_profiles, account_feed, relationship_profiles, assets, demand_categories_config,
                       account_intelligence_config, config, today=None):
    today = today or TODAY
    orgs_this_week = organisations_this_week(org_profiles, config, today)
    org_names = [o["organisation"] for o in orgs_this_week]
    briefs = briefs_this_week(account_feed, org_names)

    top_domain, top_domain_key, top_domain_count = trending_domain(orgs_this_week, demand_categories_config)
    top_risk, top_risk_count = trending_governance_risk(briefs)

    return {
        "weekOf": today.isoformat(),
        "companiesThisWeek": len(orgs_this_week),
        "trendingDomain": top_domain,
        "trendingGovernanceRisk": top_risk,
        "companiesToEngage": companies_to_engage(orgs_this_week, config),
        "executivesToFollow": executives_to_follow(relationship_profiles),
        "topicsToWrite": topics_to_write(top_domain, top_domain_count, top_risk, top_risk_count, orgs_this_week, config),
        "productsToUpdate": assets_to_update(assets, top_domain_key, account_intelligence_config, config),
        "whitepapersToPublish": whitepapers_to_publish(assets),
        "conferencesToMonitor": conferences_to_monitor(relationship_profiles),
        "newsletterThemes": topics_to_write(top_domain, top_domain_count, top_risk, top_risk_count, orgs_this_week, config),
        "githubImprovements": github_improvement_suggestion(top_domain, top_risk),
        "linkedinStrategy": linkedin_strategy(briefs, top_risk),
        "visibilityImpact": visibility_impact(orgs_this_week, config),
        "leadGenerationPotential": lead_generation_potential(orgs_this_week, config),
        "expectedConsultingInfluence": expected_consulting_influence(briefs, config),
    }


def build_monthly_authority_report(history, config, today=None):
    today = today or TODAY
    window = config.get("monthlyWindowDays", 30)
    recent_weeks = [w for w in history.get("weeks", []) if _within_window(w.get("weekOf"), today, window)]

    if not recent_weeks:
        return {"weeksIncluded": 0, "topDomain": None, "topRisk": None, "totalCompaniesEngaged": 0}

    domain_counter = Counter(w["trendingDomain"] for w in recent_weeks if w.get("trendingDomain"))
    risk_counter = Counter(w["trendingGovernanceRisk"] for w in recent_weeks if w.get("trendingGovernanceRisk"))
    companies = {c["organisation"] for w in recent_weeks for c in w.get("companiesToEngage", [])}

    return {
        "weeksIncluded": len(recent_weeks),
        "topDomain": domain_counter.most_common(1)[0][0] if domain_counter else None,
        "topRisk": risk_counter.most_common(1)[0][0] if risk_counter else None,
        "totalCompaniesEngaged": len(companies),
    }
