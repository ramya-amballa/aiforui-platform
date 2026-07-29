#!/usr/bin/env python3
"""
CEO Advisor — execution mode

Usage:
    python3 generate.py

The final step of every AOS Orchestrator run. Reads, read-only, the
output of every other employee — Demand Intelligence, Market
Intelligence, CRM, Revenue Hunter, Service Mapping Engine, Sales
Director, Website Intake, and Daily Brief — and produces three reports:

  - CEO Daily Report: Executive Summary (<=300 words), Top 3
    Priorities (ranked, each with why it outranks the others),
    Revenue Impact, Strategic Alerts, an Ignore List, and (rolling)
    the current Weekly Strategic Recommendation.
  - CEO Weekly Report: a rolling 7-day retrospective, regenerated
    every run so it's always current — see
    ../ceo-advisor-runtime-notes.md for why this is rolling rather
    than gated to a specific day of the week.
  - CEO Monthly Business Review: the same idea over a rolling 30 days.

Every number and every recommendation traces back to a named source
runtime and file — CEO Advisor never invents a figure and never
recomputes another employee's own scoring, classification, or
forecasting. Where this runtime reuses another employee's logic
verbatim (parse_currency/format_amount, crm_follow_up_status,
decision-model.md's own normalisation values), that's noted at the
point of reuse, not reinvented.

Writes nothing back to any other employee's file. Sends nothing.
"""

import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
CEO_ADVISOR_DIR = RUNTIME_DIR.parent
AOS_DIR = CEO_ADVISOR_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_DIR = RUNTIME_DIR / "config"
OUTPUT_DIR = RUNTIME_DIR / "output"
LOGS_DIR = RUNTIME_DIR / "logs"

OPPORTUNITY_SCHEMA_PATH = AOS_DIR / "demand-intelligence" / "opportunity-schema.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"
CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
MARKET_INTELLIGENCE_FEED_PATH = AOS_DIR / "05-Market-Intelligence" / "runtime" / "output" / "ceo-advisor-feed.json"
SALES_DIRECTOR_FEED_PATH = AOS_DIR / "sales-director" / "runtime" / "output" / "ceo-advisor-feed.json"
WEBSITE_INTAKE_FEED_PATH = AOS_DIR / "website-intake" / "runtime" / "output" / "ceo-advisor-feed.json"
SERVICE_RECOMMENDATIONS_PATH = AOS_DIR / "service-mapping" / "service-recommendations.json"
TOP_ORGANISATIONS_PATH = AOS_DIR / "demand-intelligence" / "runtime" / "output" / "top-organisations-this-week.json"
RECRUITER_INTELLIGENCE_FEED_PATH = AOS_DIR / "recruiter-intelligence" / "runtime" / "output" / "recruiter-intelligence-feed.json"
RELATIONSHIP_INTELLIGENCE_FEED_PATH = AOS_DIR / "relationship-intelligence" / "runtime" / "output" / "relationship-intelligence-feed.json"
EXECUTIVE_BRAND_INTELLIGENCE_FEED_PATH = AOS_DIR / "executive-brand-intelligence" / "runtime" / "output" / "executive-brand-intelligence-feed.json"
CAPACITY_FEED_PATH = AOS_DIR / "capacity-management" / "runtime" / "output" / "capacity-feed.json"
DAILY_BRIEF_PATH = AOS_DIR / "executive-dashboard" / "executive-dashboard.md"
ORCHESTRATOR_STATUS_PATH = AOS_DIR / "orchestrator" / "status.json"

TODAY = date.today()
RUN_STARTED = datetime.now(timezone.utc)


def load_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def days_since(iso_date):
    if not iso_date:
        return None
    try:
        return (TODAY - datetime.strptime(iso_date, "%Y-%m-%d").date()).days
    except ValueError:
        return None


def days_until(iso_date):
    if not iso_date:
        return None
    try:
        return (datetime.strptime(iso_date, "%Y-%m-%d").date() - TODAY).days
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Reused verbatim from executive-dashboard/runtime/generate.py (also
# reused by revenue-hunter/, crm/, service-mapping/) — the same currency
# parser and CRM follow-up categorisation everywhere they're needed, so
# a figure or a relationship's status is read the same way regardless
# of which employee is reading it.
# --------------------------------------------------------------------------

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


def format_amount(value, currency):
    if value is None:
        return "unestimated"
    label = currency or ""
    if value >= 10_000_000:
        return f"{label} {value / 10_000_000:.2f}Cr".strip()
    if value >= 100_000:
        return f"{label} {value / 100_000:.2f}L".strip()
    return f"{label} {value:,.0f}".strip()


MAX_DAYS_BY_TEMPERATURE = {"hot": 3, "warm": 10, "cooling": 21}


def crm_follow_up_status(companies):
    due, cold_risk, escalated = [], [], []
    for company in companies:
        temperature = company.get("relationshipTemperature", "cold")
        if temperature == "cold":
            continue
        max_days = MAX_DAYS_BY_TEMPERATURE.get(temperature)
        since_touch = days_since(company.get("lastTouch"))
        until_due = days_until(company.get("nextFollowUpDue"))
        is_overdue = (until_due is not None and until_due <= 0) or (
            since_touch is not None and max_days is not None and since_touch > max_days
        )
        record = {**company, "days_since_touch": since_touch}
        if is_overdue:
            due.append(record)
        if temperature == "cooling" or (
            temperature in ("hot", "warm") and since_touch is not None and max_days and since_touch >= max_days
        ):
            cold_risk.append(record)
        if temperature == "hot" and since_touch is not None and since_touch > 3 + 3:
            escalated.append(record)
    due.sort(key=lambda c: ({"hot": 0, "warm": 1, "cooling": 2}.get(c.get("relationshipTemperature"), 3),
                             -(c["days_since_touch"] or 0)))
    return {"due": due, "cold_risk": cold_risk, "escalated": escalated}


# --------------------------------------------------------------------------
# Candidate collection — 09-CEO-Advisor/decision-model.md's Step 1
# (normalise) and Step 2 (urgency overlay), one function per source,
# reusing the model's own documented values via config, not reinventing
# them. Every candidate carries its source runtime and file for the
# "must reference the source runtime" constraint.
# --------------------------------------------------------------------------

def urgency_factor_for_days(days_left, config):
    u = config["urgencyFactors"]
    if days_left is None:
        return u["noDeadline"]
    if days_left <= 2:
        return u["within48Hours"]
    if days_left <= 7:
        return u["dueThisWeek"]
    if days_left <= 30:
        return u["dueThisMonth"]
    return u["noDeadline"]


def candidates_from_revenue_hunter(pipeline, config):
    candidates = []
    for entry in pipeline.get("pipeline", []):
        if entry.get("band") != "Priority":
            continue
        days_left = days_until(entry.get("nextActionDue"))
        candidates.append({
            "source": "Revenue Hunter", "sourceFile": "08-Revenue-Hunter/pipeline.json",
            "label": f"{entry['title']} ({entry['organisation']})",
            "organisation": entry.get("organisation"),
            "opportunityId": entry.get("sourceRef"),
            "normalisedValue": entry.get("score", 0) / 10,
            "urgencyFactor": urgency_factor_for_days(days_left, config),
            "effort": entry.get("effortRequired", 5),
            "evidence": f"Priority-band pipeline item, score {entry.get('score', 0)}/100, "
                        f"next action due {entry.get('nextActionDue') or 'unset'}",
        })
    return candidates


def candidates_from_demand_intelligence(schema_data, config):
    candidates = []
    for opp in schema_data.get("opportunities", []):
        if opp.get("band") != "Priority":
            continue
        days_left = days_until(opp.get("nextActionDue"))
        candidates.append({
            "source": "Demand Intelligence", "sourceFile": "demand-intelligence/opportunity-schema.json",
            "label": f"{opp['title']} ({opp['organisation']})",
            "organisation": opp.get("organisation"),
            "opportunityId": opp.get("id"),
            "normalisedValue": opp.get("priorityScore", 0) / 10,
            "urgencyFactor": urgency_factor_for_days(days_left, config),
            "effort": opp.get("scores", {}).get("timeRequired", config["opportunityHunterDefaultEffort"]),
            "evidence": f"Priority-band opportunity, priorityScore {opp.get('priorityScore', 0)}/100, "
                        f"classification {opp.get('classification')}",
        })
    return candidates


def candidates_from_demand_intelligence_organisations(top_organisations_feed, config):
    """AOS Sprint 6 (Demand Intelligence v2), Part 6 — "Top 10
    Organizations This Week". A separate, additive pool from
    candidates_from_demand_intelligence() above: that function surfaces
    individual Priority-band opportunities already in
    opportunity-schema.json; this one surfaces the organisation-level
    consulting-demand analysis (Buying Readiness Score, Opportunity
    Narrative, recommended service/action) demand_engine.py computes
    and writes to top-organisations-this-week.json, which
    opportunity-schema.json itself has no room for. Reuses the same
    band vocabulary (Very High/High/Medium/Low) as
    config["urgencyFactors"]'s within48Hours/dueThisWeek/dueThisMonth/
    noDeadline bands rather than inventing a second urgency scale."""
    band_to_urgency = {
        "Very High": config["urgencyFactors"]["within48Hours"],
        "High": config["urgencyFactors"]["dueThisWeek"],
        "Medium": config["urgencyFactors"]["dueThisMonth"],
        "Low": config["urgencyFactors"]["noDeadline"],
    }
    candidates = []
    for org in top_organisations_feed.get("organisations", []):
        candidates.append({
            "source": "Demand Intelligence", "sourceFile": "demand-intelligence/runtime/output/top-organisations-this-week.json",
            "label": org["organisation"],
            "organisation": org.get("organisation"),
            "demandSignal": org.get("demandSignal", ""),
            "buyingReadinessScore": org.get("buyingReadinessScore", 0),
            "buyingReadinessBand": org.get("buyingReadinessBand", "Low"),
            "opportunityNarrative": org.get("opportunityNarrative", ""),
            "recommendedServices": org.get("recommendedServices", []),
            "recommendedAction": org.get("recommendedAction", "Monitor"),
            "recommendedActionReason": org.get("recommendedActionReason", ""),
            "normalisedValue": org.get("overallDemandScore", 0) / 10,
            "urgencyFactor": band_to_urgency.get(org.get("buyingReadinessBand", "Low"), 0.8),
            "effort": 5,  # an insight-led first-touch approach, consistently quick to prepare — see demand_engine.py
            "evidence": f"Buying readiness {org.get('buyingReadinessScore', 0)}/100 "
                        f"({org.get('buyingReadinessBand', 'Low')}), signal(s): {org.get('demandSignal', 'none')}",
        })
    return candidates


def top_organisations_this_week(top_organisations_feed, config, count=10):
    candidates = candidates_from_demand_intelligence_organisations(top_organisations_feed, config)
    ranked = rank_candidates(candidates, config)
    return top_priorities_with_reasons(ranked, count=count)


def candidates_from_sales_director(feed, schema_by_id, config):
    candidates = []
    for entry in feed.get("feed", []):
        status = entry.get("status")
        if status not in config["salesDirectorFeedValue"]:
            continue
        opp = schema_by_id.get(entry.get("opportunityId"))
        effort = opp.get("scores", {}).get("timeRequired", config["salesDirectorDefaultEffort"]) if opp else config["salesDirectorDefaultEffort"]
        days_left = days_until(opp.get("nextActionDue")) if opp else None
        candidates.append({
            "source": "Sales Director", "sourceFile": "sales-director/runtime/output/ceo-advisor-feed.json",
            "label": f"{entry['title']} ({entry['organisation']})",
            "organisation": entry.get("organisation"),
            "opportunityId": entry.get("opportunityId"),
            "normalisedValue": config["salesDirectorFeedValue"][status],
            "urgencyFactor": urgency_factor_for_days(days_left, config) if days_left is not None
                             else config["urgencyFactors"]["dueThisWeek"],
            "effort": effort,
            "evidence": f"Prepared proposal package, status {status}",
        })
    return candidates


def candidates_from_crm(companies, config):
    status = crm_follow_up_status(companies)
    candidates = []
    for company in status["due"]:
        temperature = company.get("relationshipTemperature")
        overdue = (days_until(company.get("nextFollowUpDue")) or 0) <= 0
        if temperature == "hot" and overdue:
            value = config["crmFollowUpValue"]["hotOverdue"]
        elif temperature == "hot":
            value = config["crmFollowUpValue"]["hot"]
        elif temperature == "warm" and overdue:
            value = config["crmFollowUpValue"]["warmOverdue"]
        else:
            value = config["crmFollowUpValue"]["warm"]
        candidates.append({
            "source": "CRM", "sourceFile": "06-CRM/company-intelligence.json",
            "label": f"Follow up with {company['companyName']}",
            "organisation": company.get("companyName"),
            "opportunityId": None,
            "normalisedValue": value,
            "urgencyFactor": config["urgencyFactors"]["within48Hours"] if overdue else config["urgencyFactors"]["dueThisWeek"],
            "effort": config["crmDefaultEffort"],
            "evidence": f"Relationship {temperature}, {company.get('days_since_touch')} days since last touch"
                        f"{' (overdue)' if overdue else ''}",
        })
    return candidates, status


def candidates_from_website_intake(feed, schema_by_id, config):
    candidates = []
    for entry in feed.get("feed", []):
        urgency = entry.get("urgency")
        if urgency not in config["websiteIntakeUrgencyValue"]:
            continue
        opp = schema_by_id.get(entry.get("opportunityId"))
        effort = opp.get("scores", {}).get("timeRequired", 5) if opp else 5
        days_left = {"High": 1, "Medium": 5, "Low": 20}.get(urgency)
        candidates.append({
            "source": "Website Intake", "sourceFile": "website-intake/runtime/output/ceo-advisor-feed.json",
            "label": f"Respond to website enquiry — {entry['leadClassification']} ({entry['organisation']})",
            "organisation": entry.get("organisation"),
            "opportunityId": entry.get("opportunityId"),
            "normalisedValue": config["websiteIntakeUrgencyValue"][urgency],
            "urgencyFactor": urgency_factor_for_days(days_left, config),
            "effort": effort,
            "evidence": f"Website lead {entry['leadId']}, urgency {urgency}",
        })
    return candidates


def candidates_from_market_intelligence(feed, config):
    candidates = []
    for entry in feed.get("feed", []):
        checks = entry.get("checks", {})
        if checks.get("consultingOpportunity"):
            value = config["marketIntelligenceValue"]["consultingOpportunity"]
        elif checks.get("newProduct"):
            value = config["marketIntelligenceValue"]["newProduct"]
        elif checks.get("linkedinContent") or checks.get("websiteUpdate"):
            value = config["marketIntelligenceValue"]["contentOnly"]
        else:
            continue
        candidates.append({
            "source": "Market Intelligence", "sourceFile": "05-Market-Intelligence/runtime/output/ceo-advisor-feed.json",
            "label": f"Review market signal: {entry.get('title', entry.get('id', 'untitled'))}",
            "organisation": None,
            "opportunityId": None,
            "normalisedValue": value,
            "urgencyFactor": config["urgencyFactors"]["noDeadline"],
            "effort": config["marketIntelligenceDefaultEffort"],
            "evidence": f"Source: {entry.get('source', 'unknown')}",
        })
    return candidates


def candidates_from_orchestrator_failures(status_data, config):
    candidates = []
    for failure in status_data.get("failures", []):
        candidates.append({
            "source": "Orchestrator", "sourceFile": "orchestrator/status.json",
            "label": f"Investigate {failure.get('name', failure.get('key'))} failure",
            "organisation": None,
            "opportunityId": None,
            "normalisedValue": config["orchestratorFailureValue"],
            "urgencyFactor": config["urgencyFactors"]["within48Hours"],
            "effort": config["orchestratorFailureEffort"],
            "evidence": f"{failure.get('error', 'unknown error')} (after {failure.get('attempts', '?')} attempts)",
        })
    return candidates


def enrich_with_service_mapping(candidates, recommendations):
    for candidate in candidates:
        opp_id = candidate.get("opportunityId")
        recommendation = recommendations.get(opp_id) if opp_id else None
        if recommendation and not recommendation.get("notApplicable"):
            candidate["recommendedService"] = recommendation.get("primaryService")
            candidate["recommendedProposalTemplate"] = recommendation.get("recommendedProposalTemplate")
    return candidates


# --------------------------------------------------------------------------
# decision-model.md Steps 3-4: effort tie-break, select top 3 with
# explicit "why this outranks the next one" reasoning.
# --------------------------------------------------------------------------

def rank_candidates(candidates, config):
    """decision-model.md Steps 2-3: urgency-weighted score, descending,
    with effort as a tie-breaker only between the top pick and its
    immediate challenger — exactly the two-candidate comparison Step 3
    describes ("if two candidates land within 10% of each other, the
    lower-effort one wins"), not a general re-sort. Applying the
    threshold pairwise all the way down the list would let a much
    lower-scored candidate several positions down "bubble" past
    higher-scored ones through a chain of narrow, unrelated ties —
    every other position stays in strict, unambiguous score order."""
    for c in candidates:
        c["finalScore"] = c["normalisedValue"] * c["urgencyFactor"]

    ranked = sorted(candidates, key=lambda c: c["finalScore"], reverse=True)

    threshold = config["tieBreakThresholdPct"] / 100
    if len(ranked) >= 2 and ranked[0]["finalScore"] > 0:
        top, challenger = ranked[0], ranked[1]
        within_threshold = abs(top["finalScore"] - challenger["finalScore"]) / top["finalScore"] <= threshold
        if within_threshold and challenger["effort"] > top["effort"]:
            ranked[0], ranked[1] = challenger, top

    return ranked


def top_priorities_with_reasons(ranked, count=3):
    top = ranked[:count]
    for i, candidate in enumerate(top):
        if i + 1 < len(ranked):
            next_candidate = ranked[i + 1]
            candidate["whyItOutranksTheNext"] = (
                f"scores {candidate['finalScore']:.2f} vs {next_candidate['finalScore']:.2f} for "
                f"\"{next_candidate['label']}\" ({next_candidate['source']}) — "
                f"{'higher urgency-weighted value' if candidate['finalScore'] > next_candidate['finalScore'] else 'equal value, lower effort'}"
            )
        else:
            candidate["whyItOutranksTheNext"] = "the only remaining candidate today"
    return top


def update_priorities_log(priorities_log, today_str, top3, alerts):
    """AOS Sprint 20 — appends today's Top 3/alerts to CEO Advisor's own
    daily-priorities-log.json, the one place its recommendations survive
    past tomorrow's overwrite of ceo-daily-report.md. Append-only (never
    deletes a past day's entry) and idempotent (a same-day re-run
    doesn't duplicate today's entry) — returns a new dict, never
    mutates the one passed in."""
    log = list(priorities_log.get("log", []))
    if not any(e["date"] == today_str for e in log):
        log.append({
            "date": today_str,
            "top3": [{"label": c["label"], "organisation": c.get("organisation"), "source": c["source"]} for c in top3],
            "alertTypes": [a["type"] for a in alerts],
        })
    return {"log": log}


# --------------------------------------------------------------------------
# Revenue Impact
# --------------------------------------------------------------------------

def compute_revenue_impact(pipeline, crm_cold_risk_orgs):
    open_items = [p for p in pipeline.get("pipeline", []) if p.get("stage") not in ("won", "lost")]

    at_risk_total, at_risk_currency = 0.0, None
    for item in open_items:
        if item.get("organisation") in crm_cold_risk_orgs:
            amount, currency = parse_currency(item.get("expectedRevenue"))
            if amount is not None:
                at_risk_total += amount
                at_risk_currency = at_risk_currency or currency

    winnable_total, winnable_currency = 0.0, None
    winnable_items = []
    for item in open_items:
        due = days_until(item.get("nextActionDue"))
        if item.get("stage") in ("in-progress", "qualified") and due is not None and due <= 0:
            amount, currency = parse_currency(item.get("expectedRevenue"))
            if amount is not None:
                winnable_total += amount
                winnable_currency = winnable_currency or currency
                winnable_items.append(item["title"])

    def roi(item):
        amount, _ = parse_currency(item.get("expectedRevenue"))
        amount = amount or 0
        return amount * (item.get("probabilityOfSuccess", 0) / 10) * (item.get("effortRequired", 0) / 10)

    highest_value = max(open_items, key=roi, default=None)
    highest_amount, highest_currency = (parse_currency(highest_value.get("expectedRevenue"))
                                         if highest_value else (None, None))

    return {
        "revenueAtRisk": format_amount(at_risk_total if at_risk_total else None, at_risk_currency),
        "revenueWinnableToday": format_amount(winnable_total if winnable_total else None, winnable_currency),
        "winnableItems": winnable_items,
        "highestValueOpportunity": (
            f"{highest_value['title']} ({highest_value['organisation']}) — "
            f"{format_amount(highest_amount, highest_currency)}"
        ) if highest_value else "None open in pipeline yet",
    }


# --------------------------------------------------------------------------
# Strategic Alerts — deterministic trend detection over dated real
# records only; no alert fires without a real, computed threshold
# crossing (demand-intelligence/opportunity-schema.json's own
# domainTags/dateFound/classification/source, all real fields).
# --------------------------------------------------------------------------

def _in_window(date_str, start_days_ago, end_days_ago):
    d = days_since(date_str)
    return d is not None and end_days_ago <= d < start_days_ago


def detect_strategic_alerts(schema_data, website_leads, config):
    alerts = []
    opportunities = schema_data.get("opportunities", [])
    window = config["trendWindowDays"]

    def count_with_any_tag(tags, start_days_ago, end_days_ago):
        # Distinct opportunities matching any tag in the set — an
        # opportunity carrying both ADGL and AI Deployment Governance
        # must count once, not twice.
        tag_set = set(tags)
        return sum(1 for o in opportunities if tag_set & set(o.get("domainTags", []))
                   and _in_window(o.get("dateFound"), start_days_ago, end_days_ago))

    adgl_tags = ["ADGL", "AI Deployment Governance"]
    adgl_recent = count_with_any_tag(adgl_tags, window, 0)
    adgl_prior = count_with_any_tag(adgl_tags, window * 2, window)
    if adgl_recent >= config["adglDemandIncreaseThreshold"] and adgl_recent > adgl_prior:
        alerts.append({
            "type": "ADGL demand increasing",
            "evidence": f"{adgl_recent} ADGL/AI Deployment Governance opportunities in the last {window} days "
                        f"vs {adgl_prior} in the {window} days before that",
            "source": "Demand Intelligence (demand-intelligence/opportunity-schema.json)",
        })

    recruiter_recent = sum(1 for o in opportunities if o.get("sourceCategory") == "Recruiter Channel"
                            and _in_window(o.get("dateFound"), window, 0))
    recruiter_prior = sum(1 for o in opportunities if o.get("sourceCategory") == "Recruiter Channel"
                           and _in_window(o.get("dateFound"), window * 2, window))
    if recruiter_prior > 0 and recruiter_recent <= recruiter_prior * config["recruiterSlowdownThreshold"]:
        alerts.append({
            "type": "Recruiter activity slowing",
            "evidence": f"{recruiter_recent} recruiter-sourced opportunities in the last {window} days "
                        f"vs {recruiter_prior} in the {window} days before that",
            "source": "Demand Intelligence (demand-intelligence/opportunity-schema.json)",
        })

    recent_leads = [l for l in website_leads.values() if _in_window(l.get("dateReceived"), config["websiteSilenceDays"], 0)]
    if not recent_leads:
        alerts.append({
            "type": "No website enquiries received",
            "evidence": f"0 website leads in the last {config['websiteSilenceDays']} days",
            "source": "Website Intake (website-intake/leads.json)",
        })

    tag_counts = {}
    for o in opportunities:
        if _in_window(o.get("dateFound"), window, 0):
            for tag in o.get("domainTags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    for tag, count in tag_counts.items():
        if count >= config["productOpportunityRecurrenceThreshold"]:
            alerts.append({
                "type": "Product opportunity detected",
                "evidence": f"\"{tag}\" appeared in {count} opportunities in the last {window} days — "
                            f"a recurring pattern worth a productised offer",
                "source": "Demand Intelligence (demand-intelligence/opportunity-schema.json)",
            })

    classification_recent = {}
    classification_prior = {}
    for o in opportunities:
        c = o.get("classification")
        if _in_window(o.get("dateFound"), window, 0):
            classification_recent[c] = classification_recent.get(c, 0) + 1
        elif _in_window(o.get("dateFound"), window * 2, window):
            classification_prior[c] = classification_prior.get(c, 0) + 1
    for classification, recent_count in classification_recent.items():
        prior_count = classification_prior.get(classification, 0)
        if prior_count > 0 and recent_count >= prior_count * 2:
            alerts.append({
                "type": "Consulting demand shift",
                "evidence": f"\"{classification}\" classification doubled: {recent_count} in the last {window} "
                            f"days vs {prior_count} before",
                "source": "Demand Intelligence (demand-intelligence/opportunity-schema.json)",
            })

    return alerts


# --------------------------------------------------------------------------
# Ignore List
# --------------------------------------------------------------------------

def build_ignore_list(schema_data, companies, sales_director_feed, config):
    ignore = []
    for o in schema_data.get("opportunities", []):
        if o.get("band") == "Archived":
            ignore.append({
                "item": f"{o['title']} ({o['organisation']})",
                "reason": f"Archived band, priorityScore {o.get('priorityScore', 0)}/100",
                "source": "Demand Intelligence (demand-intelligence/opportunity-schema.json)",
            })

    for c in companies:
        if c.get("relationshipTemperature") == "cold":
            since = days_since(c.get("lastTouch"))
            if since is not None and since > config["staleColdDays"]:
                ignore.append({
                    "item": f"Re-approaching {c['companyName']}",
                    "reason": f"Cold relationship, {since} days since last touch — past the monthly review window",
                    "source": "CRM (06-CRM/company-intelligence.json)",
                })

    for entry in sales_director_feed.get("feed", []):
        if entry.get("status") == "Needs Review":
            ignore.append({
                "item": f"{entry['title']} ({entry['organisation']})",
                "reason": "Needs Review status — confirm scope before investing further preparation time",
                "source": "Sales Director (sales-director/runtime/output/ceo-advisor-feed.json)",
            })

    return ignore


# --------------------------------------------------------------------------
# Strategic Recommendation — one recommendation, derived from whichever
# real signal is strongest over the period, never a canned suggestion
# independent of the data. Shared by the Daily Report (labelled
# "Weekly Strategic Recommendation" there, since it's always computed
# over the rolling 7-day window) and the Weekly/Monthly reports (each
# recomputed over their own window) — the period_label parameter keeps
# the phrasing honest about which window produced it.
# --------------------------------------------------------------------------

def build_weekly_strategic_recommendation(alerts, revenue_impact, period_label="this week"):
    if not alerts:
        return (f"No strong pattern detected {period_label} across Demand Intelligence, CRM, or Website Intake — "
                f"maintain current outreach cadence rather than changing direction on a quiet period.")

    priority_order = ["Product opportunity detected", "ADGL demand increasing", "Consulting demand shift",
                       "Recruiter activity slowing", "No website enquiries received"]
    chosen = next((a for t in priority_order for a in alerts if a["type"] == t), alerts[0])

    recommendations = {
        "Product opportunity detected": f"Evaluate productising the recurring theme in this alert: {chosen['evidence']} — route the candidate to Product Manager for a formal evaluation.",
        "ADGL demand increasing": f"Prioritise ADGL-related content and outreach {period_label}: {chosen['evidence']}.",
        "Consulting demand shift": f"Re-weight outreach toward the shifting classification: {chosen['evidence']}.",
        "Recruiter activity slowing": f"Diversify sourcing beyond recruiter channels {period_label}: {chosen['evidence']}.",
        "No website enquiries received": "Review whether the website's calls to action and page-specific context (ADGL/OPERA/Selected Engagement Areas) are converting, since Website Intake shows zero enquiries.",
    }
    return recommendations.get(chosen["type"], chosen["evidence"])


# --------------------------------------------------------------------------
# Executive Summary (<=300 words)
# --------------------------------------------------------------------------

def extract_daily_brief_summary():
    if not DAILY_BRIEF_PATH.exists():
        return None
    text = DAILY_BRIEF_PATH.read_text(encoding="utf-8")
    marker = "## Daily Summary"
    if marker not in text:
        return None
    return text.split(marker, 1)[1].strip()


def build_executive_summary(top3, revenue_impact, alerts, daily_brief_summary, config):
    parts = []
    if daily_brief_summary:
        parts.append(f"Daily Brief reports: {daily_brief_summary}")
    if top3:
        parts.append(f"Today's highest-value action is {top3[0]['label']} (source: {top3[0]['source']}).")
    parts.append(f"Revenue winnable today: {revenue_impact['revenueWinnableToday']}; "
                 f"revenue at risk: {revenue_impact['revenueAtRisk']}; "
                 f"highest-value opportunity: {revenue_impact['highestValueOpportunity']}.")
    if alerts:
        parts.append(f"{len(alerts)} strategic alert(s) this period: " +
                      "; ".join(a["type"] for a in alerts) + ".")
    else:
        parts.append("No strategic alerts this period.")

    summary = " ".join(parts)
    words = summary.split()
    max_words = config["executiveSummaryMaxWords"]
    if len(words) > max_words:
        summary = " ".join(words[:max_words]).rstrip(".,;") + "."
    return summary


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_top_organisations_section(top_orgs):
    lines = ["## Top 10 Organizations This Week", ""]
    if not top_orgs:
        lines.append("_No demand-signal organisations identified this week — Demand Intelligence's "
                      "Demand Signals connector may not be configured (needs feedUrls, and either "
                      "spaCy installed for its default offline backend or ANTHROPIC_API_KEY if set "
                      "to the optional Claude backend) or found nothing new in the last 7 days._")
        lines.append("")
        return lines

    lines.append("| # | Organization | Demand Signal | Buying Score | Recommended Service | "
                  "Recommended Action | Est. Strategic Value | Why this outranks the next |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, org in enumerate(top_orgs, start=1):
        top_service = org["recommendedServices"][0] if org.get("recommendedServices") else "—"
        lines.append(
            f"| {i} | {org['organisation']} | {org['demandSignal']} | "
            f"{org['buyingReadinessScore']}/100 ({org['buyingReadinessBand']}) | {top_service} | "
            f"{org['recommendedAction']} | {org['normalisedValue'] * 10:.0f}/100 | "
            f"{org['whyItOutranksTheNext']} |"
        )
    lines.append("")

    for i, org in enumerate(top_orgs, start=1):
        lines.append(f"### {i}. {org['organisation']} — Opportunity Narrative")
        lines.append("")
        lines.append(org["opportunityNarrative"])
        lines.append("")
        lines.append(f"**Recommended action:** {org['recommendedAction']} — {org['recommendedActionReason']}")
        lines.append("")

    return lines


def recruiter_followups_this_week(recruiter_feed):
    """AOS Sprint 10 — reads Recruiter Intelligence's own already-computed
    weeklyFollowUpList/dormantRelationships (recruiter-intelligence-feed.json)
    read-only, and cross-references its own contacts list for display
    detail. No new scoring here — every field is Recruiter Intelligence's
    own, unchanged."""
    contacts_by_name = {c["recruiter"]: c for c in recruiter_feed.get("contacts", [])}
    due = [contacts_by_name[name] for name in recruiter_feed.get("weeklyFollowUpList", []) if name in contacts_by_name]
    dormant = [contacts_by_name[name] for name in recruiter_feed.get("dormantRelationships", []) if name in contacts_by_name]
    return due, dormant


def render_recruiter_followups_section(due, dormant):
    lines = ["## Recruiter Follow-ups", ""]
    if not due and not dormant:
        lines.append("_No recruiter or consulting-contact follow-ups due this week, and none dormant — "
                      "Recruiter Intelligence may not have run yet, or has nothing to flag._")
        lines.append("")
        return lines

    if due:
        lines.append("**Due this week:**")
        lines.append("")
        for c in due:
            lines.append(f"- **{c['recruiter']}** ({c['contactType']}) — next follow-up {c['nextFollowUp']}, "
                          f"relationship {c['relationshipBand']}, priority {c['priorityScore']}/100")
        lines.append("")
    if dormant:
        lines.append("**Dormant (worth reactivating or archiving):**")
        lines.append("")
        for c in dormant:
            last = c.get("lastInteraction") or "never"
            lines.append(f"- **{c['recruiter']}** ({c['contactType']}) — last interaction {last}")
        lines.append("")
    return lines


def relationship_action_today(relationship_feed):
    """AOS Sprint 13 — a single highest-priority relationship action for
    today, chosen from Relationship Intelligence's own already-computed
    reminders/recommendations (relationship-intelligence-feed.json) read
    only — no new scoring here. Priority order: conference reminders,
    then birthdays, then work anniversaries (all time-fixed calendar
    events), then the most-overdue reconnect recommendation
    (discretionary — can happen any day this week, so it only wins when
    nothing calendar-fixed is due)."""
    people = relationship_feed.get("people", [])

    conferences = sorted((p for p in people if p.get("conferenceReminderDue")), key=lambda p: p.get("conferenceDate") or "")
    if conferences:
        p = conferences[0]
        return {"type": "Conference", "person": p["person"], "company": p["company"],
                "detail": f"{p['conferenceName']} on {p['conferenceDate']}."}

    birthdays = sorted((p for p in people if p.get("birthdayDue")), key=lambda p: p.get("birthdayDate") or "")
    if birthdays:
        p = birthdays[0]
        return {"type": "Birthday", "person": p["person"], "company": p["company"],
                "detail": f"{p['person']}'s birthday is {p['birthdayDate']}."}

    anniversaries = sorted((p for p in people if p.get("workAnniversaryDue")), key=lambda p: p.get("workAnniversaryDate") or "")
    if anniversaries:
        p = anniversaries[0]
        return {"type": "Work Anniversary", "person": p["person"], "company": p["company"],
                "detail": f"{p['person']}'s work anniversary is {p['workAnniversaryDate']}."}

    reconnects = sorted((p for p in people if p.get("reconnectRecommended")), key=lambda p: p.get("lastInteraction") or "")
    if reconnects:
        p = reconnects[0]
        return {"type": "Reconnect", "person": p["person"], "company": p["company"], "detail": p["reconnectReason"]}

    return None


def render_relationship_action_section(action):
    lines = ["## Relationship Action Today", ""]
    if not action:
        lines.append("_Nothing due today — Relationship Intelligence may not have run yet, or has nothing to flag._")
        lines.append("")
        return lines
    lines.append(f"**{action['type']}** — **{action['person']}** ({action['company']}): {action['detail']}")
    lines.append("")
    return lines


def branding_action_today(brand_feed):
    """AOS Sprint 15 — recommends one branding action per day, rotating
    deterministically through this week's already-computed Weekly Brand
    Plan (executive-brand-intelligence-feed.json, read-only — no new
    scoring here) so the same item isn't repeated every day. Candidates
    are only the plan's own sections that actually have something to
    say; TODAY's ordinal picks which one, so the choice is stable
    within a day and rotates day to day."""
    plan = brand_feed.get("weeklyPlan")
    if not plan:
        return None

    candidates = []
    if plan.get("topicsToWrite"):
        candidates.append({"type": "Topic to Write", "detail": plan["topicsToWrite"][0]})
    if plan.get("productsToUpdate"):
        p = plan["productsToUpdate"][0]
        candidates.append({"type": "Product to Update", "detail": f"{p['title']} ({p['type']})"})
    if plan.get("conferencesToMonitor"):
        c = plan["conferencesToMonitor"][0]
        candidates.append({"type": "Conference to Monitor", "detail": f"{c['name']} — {c.get('date') or 'date not specified'}"})
    if plan.get("linkedinStrategy"):
        candidates.append({"type": "LinkedIn Strategy", "detail": plan["linkedinStrategy"]})
    if plan.get("githubImprovements"):
        candidates.append({"type": "GitHub Improvement", "detail": plan["githubImprovements"]})

    if not candidates:
        return None
    return candidates[TODAY.toordinal() % len(candidates)]


def render_branding_action_section(action):
    lines = ["## Branding Action Today", ""]
    if not action:
        lines.append("_Nothing to recommend today — Executive Brand Intelligence may not have run yet, "
                      "or has nothing to flag._")
        lines.append("")
        return lines
    lines.append(f"**{action['type']}** — {action['detail']}")
    lines.append("")
    return lines


def render_capacity_status_section(capacity_feed):
    """AOS Sprint 22 — Capacity Management's own already-computed
    status, read-only and one cycle behind (Capacity Management runs
    before CEO Advisor in the fixed orchestrator order, same accepted-
    lag pattern as Executive Memory's daily-priorities-log.json read).
    Never re-derives the status or changes how Top 3 is ranked — purely
    informational, so the founder sees it before deciding whether to
    act on today's recommendations."""
    lines = ["## Capacity Status", ""]
    status = capacity_feed.get("capacityStatus")
    if not status:
        lines.append("_Not available yet — Capacity Management may not have run yet._")
        lines.append("")
        return lines
    lines.append(f"**{status}**")
    min_weeks, max_weeks = capacity_feed.get("weeksOfCommittedWorkMin"), capacity_feed.get("weeksOfCommittedWorkMax")
    if min_weeks is not None:
        lines.append(f"  — {min_weeks}-{max_weeks} weeks of committed work at "
                      f"{capacity_feed.get('foundersAvailableDaysPerWeek')} days/week")
    lines.append("")
    return lines


def render_daily_report(exec_summary, top3, revenue_impact, alerts, ignore_list, weekly_recommendation, top_orgs,
                         recruiter_due, recruiter_dormant, relationship_action, branding_action, capacity_feed):
    lines = [
        "# CEO Daily Report",
        "",
        f"**Date:** {TODAY.isoformat()}",
        "",
        "## Executive Summary",
        "",
        exec_summary,
        "",
        "## Top 3 Priorities",
        "",
    ]
    if top3:
        for i, c in enumerate(top3, start=1):
            lines.append(f"### {i}. {c['label']}")
            lines.append("")
            lines.append(f"**Source:** {c['source']} (`{c['sourceFile']}`)  ")
            lines.append(f"**Evidence:** {c['evidence']}  ")
            lines.append(f"**Score:** {c['finalScore']:.2f} (value {c['normalisedValue']:.1f}/10 "
                          f"x urgency {c['urgencyFactor']}, effort {c['effort']}/10)  ")
            if c.get("recommendedService"):
                lines.append(f"**Recommended Service (Service Mapping Engine):** {c['recommendedService']} "
                              f"— template `{c.get('recommendedProposalTemplate')}`  ")
            lines.append(f"**Why this outranks the next priority:** {c['whyItOutranksTheNext']}")
            lines.append("")
    else:
        lines.append("_No priority candidates today across any source._")
        lines.append("")

    lines += render_top_organisations_section(top_orgs)
    lines += render_recruiter_followups_section(recruiter_due, recruiter_dormant)
    lines += render_relationship_action_section(relationship_action)
    lines += render_branding_action_section(branding_action)
    lines += render_capacity_status_section(capacity_feed)

    lines += ["## Revenue Impact", ""]
    lines.append(f"- **Revenue at risk:** {revenue_impact['revenueAtRisk']}")
    lines.append(f"- **Revenue winnable today:** {revenue_impact['revenueWinnableToday']}"
                  + (f" ({', '.join(revenue_impact['winnableItems'])})" if revenue_impact["winnableItems"] else ""))
    lines.append(f"- **Highest-value opportunity:** {revenue_impact['highestValueOpportunity']}")
    lines.append("")

    lines += ["## Strategic Alerts", ""]
    if alerts:
        for a in alerts:
            lines.append(f"- **{a['type']}** — {a['evidence']} (source: {a['source']})")
    else:
        lines.append("_None this period._")
    lines.append("")

    lines += ["## Ignore List", ""]
    lines.append("Explicitly not worth today's time:")
    lines.append("")
    if ignore_list:
        for item in ignore_list:
            lines.append(f"- **{item['item']}** — {item['reason']} (source: {item['source']})")
    else:
        lines.append("_Nothing to explicitly deprioritise today._")
    lines.append("")

    lines += ["## Weekly Strategic Recommendation", "", weekly_recommendation, ""]

    return "\n".join(lines) + "\n"


def render_period_report(title, window_days, schema_data, pipeline, alerts, weekly_recommendation):
    opportunities = schema_data.get("opportunities", [])
    recent = [o for o in opportunities if _in_window(o.get("dateFound"), window_days, 0)]
    by_classification = {}
    for o in recent:
        by_classification[o.get("classification")] = by_classification.get(o.get("classification"), 0) + 1

    open_items = [p for p in pipeline.get("pipeline", []) if p.get("stage") not in ("won", "lost")]
    total, currency = 0.0, None
    for item in open_items:
        amount, c = parse_currency(item.get("expectedRevenue"))
        if amount is not None:
            total += amount
            currency = currency or c

    lines = [
        f"# {title}",
        "",
        f"**Generated:** {TODAY.isoformat()}",
        f"**Window:** trailing {window_days} days, regenerated every run",
        "",
        f"**Opportunities found this period:** {len(recent)}",
        "",
        "**By classification:** " + (", ".join(f"{k} ({v})" for k, v in sorted(by_classification.items()))
                                      if by_classification else "none"),
        "",
        f"**Total open pipeline value:** {format_amount(total if total else None, currency)}",
        "",
        "## Strategic Alerts This Period",
        "",
    ]
    if alerts:
        for a in alerts:
            lines.append(f"- **{a['type']}** — {a['evidence']} (source: {a['source']})")
    else:
        lines.append("_None this period._")
    lines += ["", "## Strategic Recommendation", "", weekly_recommendation, ""]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    LOGS_DIR.mkdir(exist_ok=True)
    log_path = LOGS_DIR / f"{TODAY.isoformat()}-{RUN_STARTED.strftime('%H%M%S')}-ceo-advisor.log"

    config = load_json(CONFIG_DIR / "ceo-advisor-config.json")
    schema_data = load_json(OPPORTUNITY_SCHEMA_PATH, {"opportunities": []})
    pipeline = load_json(PIPELINE_PATH, {"pipeline": []})
    crm_data = load_json(CRM_PATH, {"companies": []})
    market_intel_feed = load_json(MARKET_INTELLIGENCE_FEED_PATH, {"feed": []})
    sales_director_feed = load_json(SALES_DIRECTOR_FEED_PATH, {"feed": []})
    website_intake_feed = load_json(WEBSITE_INTAKE_FEED_PATH, {"feed": []})
    website_leads = load_json(AOS_DIR / "website-intake" / "leads.json", {"leads": {}}).get("leads", {})
    service_recommendations = load_json(SERVICE_RECOMMENDATIONS_PATH, {"recommendations": {}}).get("recommendations", {})
    top_organisations_feed = load_json(TOP_ORGANISATIONS_PATH, {"organisations": []})
    recruiter_feed = load_json(RECRUITER_INTELLIGENCE_FEED_PATH, {"contacts": [], "weeklyFollowUpList": [], "dormantRelationships": []})
    relationship_feed = load_json(RELATIONSHIP_INTELLIGENCE_FEED_PATH, {"people": []})
    brand_feed = load_json(EXECUTIVE_BRAND_INTELLIGENCE_FEED_PATH, {"weeklyPlan": None})
    # AOS Sprint 22 — read-only, one cycle behind (Capacity Management
    # runs before CEO Advisor in the fixed orchestrator order). Purely
    # informational: never changes candidate ranking or Top 3 selection.
    capacity_feed = load_json(CAPACITY_FEED_PATH, {"capacityStatus": None})
    status_data = load_json(ORCHESTRATOR_STATUS_PATH, {"failures": []})

    schema_by_id = {o["id"]: o for o in schema_data.get("opportunities", [])}

    candidates = []
    candidates += candidates_from_revenue_hunter(pipeline, config)
    candidates += candidates_from_demand_intelligence(schema_data, config)
    candidates += candidates_from_sales_director(sales_director_feed, schema_by_id, config)
    crm_candidates, crm_status = candidates_from_crm(crm_data.get("companies", []), config)
    candidates += crm_candidates
    candidates += candidates_from_website_intake(website_intake_feed, schema_by_id, config)
    candidates += candidates_from_market_intelligence(market_intel_feed, config)
    candidates += candidates_from_orchestrator_failures(status_data, config)
    candidates = enrich_with_service_mapping(candidates, service_recommendations)

    ranked = rank_candidates(candidates, config)
    top3 = top_priorities_with_reasons(ranked, count=3)
    top_orgs = top_organisations_this_week(top_organisations_feed, config, count=10)
    recruiter_due, recruiter_dormant = recruiter_followups_this_week(recruiter_feed)
    relationship_action = relationship_action_today(relationship_feed)
    branding_action = branding_action_today(brand_feed)

    cold_risk_orgs = {c["companyName"] for c in crm_status["cold_risk"]}
    revenue_impact = compute_revenue_impact(pipeline, cold_risk_orgs)

    alerts = detect_strategic_alerts(schema_data, website_leads, config)
    ignore_list = build_ignore_list(schema_data, crm_data.get("companies", []), sales_director_feed, config)
    weekly_recommendation = build_weekly_strategic_recommendation(alerts, revenue_impact)
    daily_brief_summary = extract_daily_brief_summary()
    exec_summary = build_executive_summary(top3, revenue_impact, alerts, daily_brief_summary, config)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # AOS Sprint 20 — Executive Memory reads this read-only to answer
    # "has this been recommended before, and how often" — CEO Advisor's
    # own daily Top 3/alerts otherwise vanish once ceo-daily-report.md
    # is overwritten tomorrow.
    priorities_log = load_json(OUTPUT_DIR / "daily-priorities-log.json", {"log": []})
    priorities_log = update_priorities_log(priorities_log, TODAY.isoformat(), top3, alerts)
    save_json(OUTPUT_DIR / "daily-priorities-log.json", priorities_log)

    daily_report = render_daily_report(exec_summary, top3, revenue_impact, alerts, ignore_list, weekly_recommendation,
                                        top_orgs, recruiter_due, recruiter_dormant, relationship_action, branding_action,
                                        capacity_feed)
    (OUTPUT_DIR / f"{TODAY.isoformat()}-ceo-daily-report.md").write_text(daily_report, encoding="utf-8")
    (OUTPUT_DIR / "ceo-daily-report.md").write_text(daily_report, encoding="utf-8")

    weekly_report = render_period_report("CEO Weekly Report", config["weeklyWindowDays"], schema_data, pipeline,
                                          alerts, weekly_recommendation)
    (OUTPUT_DIR / "ceo-weekly-report.md").write_text(weekly_report, encoding="utf-8")

    monthly_alerts = detect_strategic_alerts(schema_data, website_leads,
                                              {**config, "trendWindowDays": config["monthlyWindowDays"] // 2})
    monthly_recommendation = build_weekly_strategic_recommendation(monthly_alerts, revenue_impact,
                                                                     period_label="this month")
    monthly_report = render_period_report("CEO Monthly Business Review", config["monthlyWindowDays"], schema_data,
                                           pipeline, monthly_alerts, monthly_recommendation)
    (OUTPUT_DIR / "ceo-monthly-business-review.md").write_text(monthly_report, encoding="utf-8")

    summary_line = (f"Top priority: {top3[0]['label']} ({top3[0]['source']})" if top3
                     else "No priority candidates today.")
    print(summary_line)
    print(f"Revenue winnable today: {revenue_impact['revenueWinnableToday']}; "
          f"at risk: {revenue_impact['revenueAtRisk']}")
    print(f"{len(alerts)} strategic alert(s); {len(ignore_list)} item(s) on the ignore list.")
    log_path.write_text(
        f"{summary_line}\n{len(candidates)} candidates considered, {len(alerts)} alerts, "
        f"{len(ignore_list)} ignore-list items.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
