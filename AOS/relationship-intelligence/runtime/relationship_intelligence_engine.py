"""
Relationship Intelligence Engine (AOS Sprint 13)

Reads relationship-profiles.json — a founder-maintained, persistent,
person-level record, exactly like 06-CRM/company-intelligence.json is
for companies. Nothing here is auto-collected (there is no LinkedIn,
email or calendar integration in AOS); every meeting, call, message,
conference interaction, birthday and upcoming conference is
founder-entered, and this engine only ever reads that record, never
invents a person or interaction it has no evidence of.

See ../relationship-intelligence-engine.md for the full field list and
scoring model.
"""

import copy
import json
from datetime import date, datetime, timedelta
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
RELATIONSHIP_INTELLIGENCE_DIR = RUNTIME_DIR.parent
AOS_DIR = RELATIONSHIP_INTELLIGENCE_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_PATH = RUNTIME_DIR / "config" / "relationship-intelligence-config.json"
PROFILES_PATH = RELATIONSHIP_INTELLIGENCE_DIR / "relationship-profiles.json"

CRM_PATH = AOS_DIR / "06-CRM" / "company-intelligence.json"
ORGANISATION_PROFILES_PATH = AOS_DIR / "demand-intelligence" / "organisation-profiles.json"

FEED_PATH = RUNTIME_DIR / "output" / "relationship-intelligence-feed.json"

TODAY = date.today()

DEFAULT_PROFILES = {
    "schema": {
        "person": "string — key",
        "company": "string",
        "role": "string",
        "linkedIn": "string or null",
        "email": "string or null",
        "meetings": "array of {date, summary}",
        "calls": "array of {date, summary}",
        "messages": "array of {date, channel, summary, responded (bool)}",
        "conferenceInteractions": "array of {date, conference, summary}",
        "sharedInterests": "array of strings",
        "productsDiscussed": "array of strings",
        "resourcesShared": "array of {date, resource}",
        "birthday": "string 'MM-DD' or null",
        "workAnniversary": "string 'MM-DD' or null",
        "upcomingConference": "{name, date} or null",
    },
    "people": {},
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
    profiles.setdefault("people", {})
    return profiles


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

def _parse_date(value):
    try:
        return datetime.fromisoformat(value).date()
    except (TypeError, ValueError):
        return None


def days_since(date_str, today=None):
    today = today or TODAY
    parsed = _parse_date(date_str)
    if parsed is None:
        return None
    return (today - parsed).days


def last_interaction(profile):
    dates = []
    for entry in profile.get("meetings", []):
        dates.append(entry.get("date"))
    for entry in profile.get("calls", []):
        dates.append(entry.get("date"))
    for entry in profile.get("messages", []):
        dates.append(entry.get("date"))
    for entry in profile.get("conferenceInteractions", []):
        dates.append(entry.get("date"))
    valid = [d for d in dates if _parse_date(d) is not None]
    return max(valid) if valid else None


def _next_occurrence(month_day, today=None):
    """Next date (this year or next) a recurring 'MM-DD' field falls on,
    on or after today. Returns None for a missing/invalid field."""
    today = today or TODAY
    if not month_day:
        return None
    try:
        month, day = (int(p) for p in month_day.split("-"))
        candidate = date(today.year, month, day)
    except (ValueError, TypeError):
        return None
    if candidate < today:
        candidate = date(today.year + 1, month, day)
    return candidate


def _within_window(target_date, today, window_days):
    if target_date is None:
        return False
    delta = (target_date - today).days
    return 0 <= delta <= window_days


# --------------------------------------------------------------------------
# Relationship Health Score — relationship-intelligence-engine.md
# --------------------------------------------------------------------------

def _recency_score(days, stale_threshold):
    if days is None:
        return 0
    if days <= stale_threshold:
        return 10
    if days <= stale_threshold * 2:
        return 6
    if days <= stale_threshold * 4:
        return 3
    return 0


def _response_rate_score(profile):
    messages = profile.get("messages", [])
    if not messages:
        return 5  # neutral — no signal either way
    responded = sum(1 for m in messages if m.get("responded"))
    return round(10 * responded / len(messages), 1)


def _channel_diversity_score(profile):
    channels = ("meetings", "calls", "messages", "conferenceInteractions")
    used = sum(1 for c in channels if profile.get(c))
    return round(10 * used / len(channels), 1)


def relationship_health_score(profile, config, today=None):
    today = today or TODAY
    stale_threshold = config.get("staleThresholdDays", 45)
    weights = config.get("healthWeights", {})
    recency = _recency_score(days_since(last_interaction(profile), today), stale_threshold)
    response = _response_rate_score(profile)
    diversity = _channel_diversity_score(profile)
    weighted = (
        recency * weights.get("recency", 0.40)
        + response * weights.get("responseRate", 0.30)
        + diversity * weights.get("channelDiversity", 0.30)
    )
    return round(weighted * 10)


def relationship_health_band(profile, health_score, config):
    if last_interaction(profile) is None:
        return "New"
    thresholds = config.get("healthBandThresholds", {})
    if health_score >= thresholds.get("strong", 75):
        return "Strong"
    if health_score >= thresholds.get("healthy", 50):
        return "Healthy"
    if health_score >= thresholds.get("cooling", 25):
        return "Cooling"
    return "At Risk"


def is_dormant(profile, config, today=None):
    today = today or TODAY
    threshold = config.get("dormancyThresholdDays", 90)
    days = days_since(last_interaction(profile), today)
    return days is not None and days >= threshold


def relationship_risk(band, dormant):
    if band == "New":
        return "Not enough data yet"
    if band == "At Risk" or dormant:
        return "High"
    if band == "Cooling":
        return "Medium"
    return "Low"


def relationship_opportunity(profile, crm_by_company, org_profiles_by_company):
    company = profile.get("company")
    org_profile = org_profiles_by_company.get(company)
    if org_profile and org_profile.get("buyingReadinessBand") in ("High", "Very High"):
        band = org_profile["buyingReadinessBand"]
        return f"High — {company} shows {band} buying readiness (Demand Intelligence); a reconnect here could open a real opportunity."
    crm_entry = crm_by_company.get(company)
    if crm_entry and (crm_entry.get("existingRelationship") or "none").lower() != "none":
        return f"Medium — {company} already has an existing relationship on record in CRM; this contact could help move it forward."
    return "Not enough signal yet to flag a specific opportunity."


def reconnect_recommendation(profile, config, today=None):
    today = today or TODAY
    last = last_interaction(profile)
    if last is None:
        return False, None
    days = days_since(last, today)
    threshold = config.get("reconnectThresholdDays", 30)
    if days >= threshold:
        return True, f"It has been {days} days since the last interaction with {profile.get('person')}."
    return False, None


def birthday_reminder(profile, config, today=None):
    today = today or TODAY
    window = config.get("reminderWindowDays", 14)
    occurrence = _next_occurrence(profile.get("birthday"), today)
    return _within_window(occurrence, today, window), occurrence


def work_anniversary_reminder(profile, config, today=None):
    today = today or TODAY
    window = config.get("reminderWindowDays", 14)
    occurrence = _next_occurrence(profile.get("workAnniversary"), today)
    return _within_window(occurrence, today, window), occurrence


def conference_reminder(profile, config, today=None):
    today = today or TODAY
    window = config.get("reminderWindowDays", 14)
    upcoming = profile.get("upcomingConference") or {}
    target = _parse_date(upcoming.get("date"))
    return _within_window(target, today, window), upcoming.get("name"), target


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def build_entry(profile, config, crm_by_company, org_profiles_by_company, today=None):
    today = today or TODAY
    health = relationship_health_score(profile, config, today)
    band = relationship_health_band(profile, health, config)
    dormant = is_dormant(profile, config, today)
    risk = relationship_risk(band, dormant)
    opportunity = relationship_opportunity(profile, crm_by_company, org_profiles_by_company)
    reconnect, reconnect_reason = reconnect_recommendation(profile, config, today)
    birthday_due, birthday_date = birthday_reminder(profile, config, today)
    anniversary_due, anniversary_date = work_anniversary_reminder(profile, config, today)
    conference_due, conference_name, conference_date = conference_reminder(profile, config, today)

    return {
        "person": profile.get("person"),
        "company": profile.get("company"),
        "role": profile.get("role"),
        "linkedIn": profile.get("linkedIn"),
        "email": profile.get("email"),
        "lastInteraction": last_interaction(profile),
        "healthScore": health,
        "healthBand": band,
        "risk": risk,
        "opportunity": opportunity,
        "reconnectRecommended": reconnect,
        "reconnectReason": reconnect_reason,
        "isDormant": dormant,
        "birthdayDue": birthday_due,
        "birthdayDate": birthday_date.isoformat() if birthday_date else None,
        "workAnniversaryDue": anniversary_due,
        "workAnniversaryDate": anniversary_date.isoformat() if anniversary_date else None,
        "conferenceReminderDue": conference_due,
        "conferenceName": conference_name,
        "conferenceDate": conference_date.isoformat() if conference_date else None,
        "sharedInterests": profile.get("sharedInterests", []),
        "productsDiscussed": profile.get("productsDiscussed", []),
        "resourcesShared": profile.get("resourcesShared", []),
        "meetings": profile.get("meetings", []),
        "calls": profile.get("calls", []),
        "messages": profile.get("messages", []),
        "conferenceInteractions": profile.get("conferenceInteractions", []),
    }


def build_feed(profiles, config, crm_data, org_profiles_data, today=None):
    today = today or TODAY
    crm_by_company = {c["companyName"]: c for c in crm_data.get("companies", [])}
    org_profiles_by_company = org_profiles_data.get("organisations", {})

    people = profiles.get("people", {})
    entries = [
        build_entry(profile, config, crm_by_company, org_profiles_by_company, today)
        for profile in people.values()
    ]
    entries.sort(key=lambda e: e["person"] or "")

    return {
        "schema": {
            "person": "string", "company": "string", "healthScore": "number 0-100",
            "healthBand": "string — Strong | Healthy | Cooling | At Risk | New",
            "risk": "string — High | Medium | Low | Not enough data yet",
            "opportunity": "string", "reconnectRecommended": "boolean",
            "birthdayDue": "boolean", "workAnniversaryDue": "boolean", "conferenceReminderDue": "boolean",
        },
        "people": entries,
        "reconnectRecommendations": sorted(
            [e["person"] for e in entries if e["reconnectRecommended"]],
            key=lambda name: next(e["lastInteraction"] for e in entries if e["person"] == name),
        ),
        "birthdayReminders": [e["person"] for e in entries if e["birthdayDue"]],
        "workAnniversaryReminders": [e["person"] for e in entries if e["workAnniversaryDue"]],
        "conferenceReminders": [e["person"] for e in entries if e["conferenceReminderDue"]],
        "atRiskRelationships": [e["person"] for e in entries if e["risk"] == "High"],
    }
