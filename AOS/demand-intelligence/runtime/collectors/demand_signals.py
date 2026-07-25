"""
Demand Signals — proactive discovery, not job-board collection.

Monitors AI-vendor and tech-news RSS feeds for evidence that a named
organisation (not the vendor) is worth AI for U&I's attention this
week — AI adoption at scale, a governance trigger, a funding round, a
regulatory trigger, or an AI failure/incident (AOS Sprint 6's five
deterministic demand-signal categories; see demand_engine.py and
config/demand-signal-categories.json). That kind of evidence is a
stronger, earlier, higher-value discovery than a generic "AI Analyst"
job posting, and one no job board will ever surface.

Three-stage pipeline per feed entry:
  1. A real RSS/Atom fetch (feed_fetch.fetch_feed_entries, reused
     verbatim from 05-Market-Intelligence/runtime/feeds.py).
  2. Deterministic keyword classification (demand_engine.classify_categories)
     against the article's own title+summary — no model call. An
     article matching none of the five categories is skipped before
     ever reaching Claude, saving the API cost entirely.
  3. Only for articles that matched at least one category, and not
     already seen (own seen-articles index, separate from collect.py's
     own opportunity-level dedupe-index.json): Claude
     (claude_client.extract_demand_signal) confirms there's a real,
     specific named organisation and extracts it — the one and only
     non-deterministic step in this whole pipeline. Only "high"
     confidence extractions become a lead; "medium"/"low" are logged,
     never fabricated into one.

Every extracted signal's scores are a genuine function of its own
analysis (demand_engine.opportunity_scores_from_result) — a weak
signal scores lower, a strong one reaches opportunity-scoring-engine.md's
existing, unmodified "Priority" band and "Immediate Proposal"
classification, entirely through the unmodified scoring/classification
pipeline every other opportunity already goes through. No change to
ingest.py's scoring or classification logic was needed or made.

If ANTHROPIC_API_KEY is not set, this connector skips cleanly, exactly
like every other credential-gated connector.
"""

from pathlib import Path

import demand_engine
from . import claude_client
from .feed_fetch import fetch_feed_entries

SOURCE_NAME = "Demand Signal"

COLLECTORS_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = COLLECTORS_DIR.parent
SEEN_ARTICLES_PATH = RUNTIME_DIR / "config" / "demand-signals-seen-articles.json"

NEEDED_SERVICES_DOMAIN_TAGS = ["ADGL", "AI Deployment Governance", "AI Governance", "Technology Risk"]


def load_json(path, default):
    if not path.exists():
        return default
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def build_title(organisation, matched_categories, config):
    labels = [config["categories"][c]["label"] for c in matched_categories if c in config.get("categories", {})]
    return f"{organisation} — {', '.join(labels)}" if labels else f"{organisation} — AI governance opportunity"


def collect(keywords, config):
    if not claude_client.api_key_configured():
        print("    Demand Signals: connector-ready, no ANTHROPIC_API_KEY configured — skipping")
        return []

    feed_urls = config.get("feedUrls", [])
    if not feed_urls:
        print("    Demand Signals: no feed URLs configured, skipping")
        return []

    model = config.get("model")
    seen = load_json(SEEN_ARTICLES_PATH, {"seen": {}})
    seen.setdefault("seen", {})

    categories_config = demand_engine.load_categories_config()
    profiles = demand_engine.load_profiles()

    results = []
    for feed_url in feed_urls:
        entries = fetch_feed_entries(feed_url)
        for entry in entries:
            article_key = entry.get("guid") or entry.get("link")
            if not article_key or article_key in seen["seen"]:
                continue
            seen["seen"][article_key] = {"checked": True}

            text = f"{entry.get('title', '')} {entry.get('summary', '')}"
            matched_categories = demand_engine.classify_categories(text, categories_config)
            if not matched_categories:
                continue  # no deterministic category matched — never spend a Claude call on this

            extraction = claude_client.extract_demand_signal(
                entry.get("title", ""), entry.get("summary", ""), model=model,
            )
            if not extraction or not extraction.get("isDemandSignal"):
                continue
            if extraction.get("confidence") != "high":
                print(f"    [skipped, confidence={extraction.get('confidence')}] "
                      f"{extraction.get('organisation') or entry.get('title')}")
                continue
            organisation = extraction.get("organisation")
            if not organisation:
                continue

            analysis = demand_engine.process_signal(
                organisation=organisation,
                category_keys=matched_categories,
                confidence=extraction.get("confidence"),
                event_summary=extraction.get("eventSummary") or "",
                industry=extraction.get("industry") or None,
                scale_text=extraction.get("scale") or None,
                source_url=entry.get("link"),
                config=categories_config,
                profiles=profiles,
            )

            results.append({
                "source": SOURCE_NAME,
                "sourceCategory": "Technology Practice",
                "title": build_title(organisation, matched_categories, categories_config),
                "organisation": organisation,
                "description": analysis["opportunityNarrative"] + f"\n\nSource article: \"{entry.get('title', '')}\" — {entry.get('link', '')}",
                "url": entry.get("link"),
                "location": "Not specified",
                "remote": True,
                "domainTags": list(NEEDED_SERVICES_DOMAIN_TAGS),
                "scores": analysis["scores"],
                "scopedEngagement": analysis["scopedEngagement"],
                "recurrencePattern": "none",
                "autoScored": True,
                "autoCollected": True,
                "matchedKeywords": [],
            })
            print(f"    [signal] {organisation}: {', '.join(matched_categories)} "
                  f"-> demand {analysis['overallDemandScore']}, buying {analysis['buyingReadinessScore']} "
                  f"({analysis['buyingReadinessBand']}), action: {analysis['recommendedAction']}")

    demand_engine.refresh_feedback_for_all_profiles(profiles)
    demand_engine.save_json(demand_engine.PROFILES_PATH, profiles)
    demand_engine.write_top_organisations_feed(profiles, categories_config)

    save_json(SEEN_ARTICLES_PATH, seen)
    return results
