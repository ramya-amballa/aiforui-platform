"""
Tender & RFP Intelligence Engine (AOS Sprint 14)

Monitors real, founder-configured procurement RSS/Atom feeds
(config/tender-intelligence-config.json's feedUrls — empty by default,
same "connector does nothing until configured" pattern as
demand-intelligence's Demand Signals connector) for tenders whose
title/summary matches at least one of seven deterministic domain
keywords (AI Governance, Responsible AI, Technology Risk, GRC, Cyber
Risk, Vendor Risk, Compliance). A tender matching none of them is
skipped entirely — never treated as GRC-relevant on a guess.

Per matching tender: Tender Summary, Estimated Value (parsed from the
tender's own text — "Not specified" when no real figure is present,
never invented), Eligibility (an honest pointer to the source
document — this engine has no eligibility-rules database), Fit Score
(an explicit heuristic, not a claim of true win probability — AOS has
no historical tender win-rate data yet), Required Partners (a
deterministic flag for source types where a local/registered partner
is typically required, otherwise an honest "not specified"), Deadline
(parsed from the tender's own text via configured date patterns —
"Not specified" when absent), and a Recommended Response tied to the
Fit Score band.
"""

import copy
import json
import re
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
TENDER_INTELLIGENCE_DIR = RUNTIME_DIR.parent
AOS_DIR = TENDER_INTELLIGENCE_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_PATH = RUNTIME_DIR / "config" / "tender-intelligence-config.json"
SEEN_TENDERS_PATH = RUNTIME_DIR / "config" / "tender-seen.json"
FEED_PATH = AOS_DIR / "output" / "tender-intelligence" / "tender-intelligence-feed.json"

TODAY = date.today().isoformat()

# Reused verbatim from crm/runtime/generate.py (itself reused verbatim
# from revenue-hunter's/executive-dashboard's own), rather than a
# second, independently-written currency parser. One deviation: the
# original's fallback of "any 3-letter run of letters is a currency
# code" is too loose for free-form tender prose (a stray English word
# would otherwise be mislabelled as a currency) — narrowed here to a
# real ISO currency code allowlist so a missing symbol never produces
# a fabricated-looking currency label.
MULTIPLIERS = {"k": 1_000, "l": 100_000, "lakh": 100_000, "cr": 10_000_000, "crore": 10_000_000, "m": 1_000_000, "b": 1_000_000_000}
CURRENCY_SYMBOLS = {"$": "USD", "₹": "INR", "£": "GBP", "€": "EUR"}
KNOWN_CURRENCY_CODES = {"USD", "EUR", "GBP", "INR", "AED", "SAR", "CAD", "AUD", "CHF", "JPY", "CNY", "ZAR", "NGN"}


def parse_estimated_value(text):
    """Requires an actual currency indicator (symbol or known ISO code)
    to be present, and only reads the number immediately following it —
    never the largest number anywhere in the text. Tender prose is full
    of unrelated numbers (dates, reference IDs, deadlines); treating any
    of those as a monetary estimate would be a fabrication, so absent a
    real currency marker this honestly returns (None, None)."""
    if not text:
        return None, None

    currency, window = None, None
    for symbol, code in CURRENCY_SYMBOLS.items():
        idx = text.find(symbol)
        if idx != -1:
            currency, window = code, text[idx:idx + 30]
            break
    if currency is None:
        for code in KNOWN_CURRENCY_CODES:
            match = re.search(rf"\b{code}\b", text)
            if match:
                currency, window = code, text[match.start():match.start() + 30]
                break
    if currency is None:
        return None, None

    num_match = re.search(r"(\d[\d,]*\.?\d*)\s*(k|l|lakh|cr|crore|m|b)?", window, flags=re.IGNORECASE)
    if not num_match or not num_match.group(1):
        return None, currency
    try:
        amount = float(num_match.group(1).replace(",", ""))
    except ValueError:
        return None, currency
    suffix = num_match.group(2)
    amount *= MULTIPLIERS.get(suffix.lower(), 1) if suffix else 1
    return amount, currency


def format_estimated_value(amount, currency):
    if amount is None:
        return "Not specified"
    label = currency or ""
    if amount >= 1_000_000:
        return f"{label} {amount / 1_000_000:.1f}M".strip()
    if amount >= 1_000:
        return f"{label} {amount / 1_000:.0f}K".strip()
    return f"{label} {amount:,.0f}".strip()


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


def strip_html(text):
    """Reused verbatim from demand-intelligence's own
    collectors/extractors/base.py — RSS summaries routinely carry raw,
    unstripped HTML, and a second independently-written stripper isn't
    needed for the same well-understood problem."""
    return re.sub(r"<[^>]+>", " ", text or "")


def classify_domains(text, domain_keywords):
    lowered = text.lower()
    matched = []
    for domain, keywords in domain_keywords.items():
        if any(kw in lowered for kw in keywords):
            matched.append(domain)
    return matched


def parse_deadline(text, deadline_patterns):
    lowered = text.lower()
    for pattern in deadline_patterns:
        match = re.search(pattern, lowered)
        if match:
            return match.group(1)
    return None


def eligibility_note(source_url):
    return f"Not specified by this connector — review the full tender notice: {source_url or 'source link not available'}."


def required_partners_note(source_type, config):
    local_partner_types = config.get("localPartnerRequiredSourceTypes", [])
    if source_type in local_partner_types:
        return f"Likely requires a local/registered partner for a {source_type} tender — verify in the tender documents."
    return "Not specified — review tender documents for any partnering requirements."


def fit_score(matched_domains, config):
    thresholds = config.get("fitScoreByDomainMatchCount", {})
    count = str(min(len(matched_domains), 3))
    score = thresholds.get(count, thresholds.get("1", 40))
    return min(score, config.get("fitScoreCap", 95))


def fit_band(score, config):
    thresholds = config.get("fitBandThresholds", {})
    if score >= thresholds.get("high", 70):
        return "High"
    if score >= thresholds.get("medium", 40):
        return "Medium"
    return "Low"


def recommended_response(band, config):
    responses = config.get("recommendedResponseByFitBand", {})
    return responses.get(band, "Review manually — no recommended-response rule configured for this band.")


def build_tender_entry(entry, source_type, config):
    """Returns None when the tender's title+summary matches none of the
    seven deterministic domain keywords — never fabricated relevance."""
    title = strip_html(entry.get("title", ""))
    summary = strip_html(entry.get("summary", ""))
    text = f"{title} {summary}"

    matched_domains = classify_domains(text, config.get("domainKeywords", {}))
    if not matched_domains:
        return None

    amount, currency = parse_estimated_value(text)
    score = fit_score(matched_domains, config)
    band = fit_band(score, config)

    return {
        "title": title,
        "sourceType": source_type,
        "sourceUrl": entry.get("link"),
        "matchedDomains": matched_domains,
        "tenderSummary": summary or title,
        "estimatedValue": format_estimated_value(amount, currency),
        "estimatedValueAmount": amount,
        "eligibility": eligibility_note(entry.get("link")),
        "fitScore": score,
        "fitBand": band,
        "requiredPartners": required_partners_note(source_type, config),
        "deadline": parse_deadline(text, config.get("deadlinePatterns", [])) or "Not specified",
        "recommendedResponse": recommended_response(band, config),
        "firstSeen": TODAY,
    }


def build_feed(tenders):
    sorted_tenders = sorted(
        tenders, key=lambda t: t.get("estimatedValueAmount") or 0, reverse=True,
    )
    return {
        "schema": {
            "title": "string", "sourceType": "string", "matchedDomains": "array of strings",
            "estimatedValue": "string", "fitScore": "number 0-100", "fitBand": "string — High | Medium | Low",
            "deadline": "string or 'Not specified'", "recommendedResponse": "string",
        },
        "tenders": sorted_tenders,
    }
