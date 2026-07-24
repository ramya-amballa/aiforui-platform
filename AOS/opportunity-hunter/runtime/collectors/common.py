"""
Shared helpers for every collector: keyword matching, the domain-tag
map, heuristic scoring for autonomously-discovered postings (no human
has judged these yet, unlike a manually-logged opportunity), and a
dependency-free HTTP JSON fetcher.
"""

import json
import urllib.error
import urllib.request

# opportunity-scoring-engine.md's eleven dimensions have no objective
# answer from a scraped posting alone (relationshipValue, strategicValue
# and similar are judgment calls). These heuristics use only what a
# posting can actually tell us, and are deliberately conservative —
# every auto-scored opportunity is flagged `autoScored: true` so a
# human knows to sanity-check it, not treat it as already-vetted.
KEYWORD_DOMAIN_TAGS = {
    "ai governance": ["AI Governance"],
    "ai deployment": ["ADGL", "AI Deployment Governance"],
    "ai risk": ["AI Governance", "Technology Risk"],
    "ai compliance": ["AI Governance", "GRC"],
    "responsible ai": ["AI Governance"],
    "ai security": ["Security Governance"],
    "ai audit": ["AI Governance", "Third-Party Risk"],
    "ai strategy": ["AI Governance"],
    "ai transformation": ["AI Governance"],
    "nist ai rmf": ["AI Governance", "GRC"],
    "iso 42001": ["AI Governance", "GRC"],
    "microsoft copilot": ["ADGL", "AI Deployment Governance"],
    "chatgpt enterprise": ["ADGL", "AI Deployment Governance"],
    "rag": ["ADGL", "AI Deployment Governance"],
    "ai agents": ["ADGL", "AI Deployment Governance"],
}

# Channel type per opportunity-schema.json's sourceCategory enum.
CONNECTOR_SOURCE_CATEGORY = {
    "Upwork": "Marketplace",
    "LinkedIn Jobs": "Professional Network",
    "Google Jobs": "Professional Network",
    "Greenhouse": "Professional Network",
    "Lever": "Professional Network",
    "Ashby": "Professional Network",
    "Wellfound": "Professional Network",
    "RemoteOK": "Professional Network",
    "FlexJobs": "Professional Network",
    "UAE Recruiters": "Recruiter Channel",
    "Consulting Firms": "Consulting Channel",
}

SERVED_GEOGRAPHIES = ["uae", "united arab emirates", "dubai", "abu dhabi", "us", "usa", "united states",
                       "uk", "united kingdom", "india", "eu", "europe", "remote"]


def match_keywords(text, keywords):
    """Case-insensitive substring match; returns the subset of `keywords`
    found in `text`. A posting with zero matches should not be collected."""
    lowered = (text or "").lower()
    return [kw for kw in keywords if kw.lower() in lowered]


def domain_tags_for(matched_keywords):
    tags = []
    for kw in matched_keywords:
        for tag in KEYWORD_DOMAIN_TAGS.get(kw.lower(), []):
            if tag not in tags:
                tags.append(tag)
    return tags or ["AI Governance"]


def heuristic_scores(title, description, location, remote, matched_keywords):
    text = f"{title} {description}".lower()
    adgl_hits = sum(1 for kw in matched_keywords if kw.lower() in
                    ("microsoft copilot", "chatgpt enterprise", "rag", "ai agents", "ai deployment"))
    governance_hits = sum(1 for kw in matched_keywords if kw.lower() in
                          ("ai governance", "ai risk", "ai compliance", "responsible ai", "ai audit",
                           "nist ai rmf", "iso 42001"))

    location_text = (location or "").lower()
    is_served_geography = remote or any(g in location_text for g in SERVED_GEOGRAPHIES)

    return {
        # Unknown until a real conversation happens; neutral, not zero.
        "expectedRevenue": 5,
        "probabilityOfWinning": 4,
        "strategicValue": min(10, 4 + 2 * governance_hits),
        # No prior contact exists yet for an auto-discovered posting.
        "relationshipValue": 2,
        "timeRequired": 7,
        "geography": 8 if is_served_geography else 3,
        "remoteCompatibility": 10 if remote else 4,
        "alignmentAIforUIServices": min(10, 4 + 1.5 * (governance_hits + adgl_hits)),
        "alignmentADGL": min(10, 3 + 2.5 * adgl_hits),
        "alignmentOPERA": 6,
        "longTermRelationshipPotential": 5,
    }


def build_opportunity(*, source, title, organisation, description, url, location, remote,
                       matched_keywords, source_category=None):
    return {
        "source": source,
        "sourceCategory": source_category or CONNECTOR_SOURCE_CATEGORY.get(source, "Professional Network"),
        "title": title,
        "organisation": organisation,
        "description": description or "",
        "url": url,
        "location": location or "Not specified",
        "remote": bool(remote),
        "domainTags": domain_tags_for(matched_keywords),
        "scores": heuristic_scores(title, description, location, remote, matched_keywords),
        "scopedEngagement": False,
        "recurrencePattern": "none",
        "autoScored": True,
        "autoCollected": True,
        "matchedKeywords": matched_keywords,
    }


def http_get_json(url, timeout=15, headers=None):
    """Dependency-free JSON GET. Returns parsed JSON, or None on any
    failure — a single source being unreachable must never stop the
    rest of the collection run."""
    request = urllib.request.Request(url, headers=headers or {"User-Agent": "AOS-OpportunityHunter/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        print(f"    fetch failed ({url}): {exc}")
        return None
