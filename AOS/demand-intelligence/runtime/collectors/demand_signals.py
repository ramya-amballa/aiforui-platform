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
     ever reaching entity extraction, saving that work entirely.
  3. Only for articles that matched at least one category, and not
     already seen (own seen-articles index, separate from collect.py's
     own opportunity-level dedupe-index.json): the configured
     extraction backend confirms there's a real, specific named
     organisation and extracts it. Only "high" confidence extractions
     become a lead; "medium"/"low" are logged, never fabricated into
     one.

AOS Sprint 7 made the extraction backend a config choice, not a hard
dependency: config/sources.json's demandSignals.extractionBackend is
"deterministic" by default — extractors/deterministic_extractor.py,
fully offline, no paid API, spaCy Named Entity Recognition plus
deterministic keyword/regex rules (see that module's own docstring for
exactly how it decides an article names a real organisation). Setting
it to "claude" opts into extractors/claude_extractor.py instead — the
same Claude API call this connector always had, now an explicitly
optional plugin, still gated on ANTHROPIC_API_KEY. Either way,
collectors/demand_signals.py calls extractor.extract(title, summary,
model=model) and only cares that the return shape matches; it does
not know or care which backend actually ran.

Every extracted signal's scores are a genuine function of its own
analysis (demand_engine.opportunity_scores_from_result) — a weak
signal scores lower, a strong one reaches opportunity-scoring-engine.md's
existing, unmodified "Priority" band and "Immediate Proposal"
classification, entirely through the unmodified scoring/classification
pipeline every other opportunity already goes through. No change to
ingest.py's scoring or classification logic was needed or made.

If the configured backend's own dependency is missing (spaCy/its model
for "deterministic", ANTHROPIC_API_KEY for "claude"), this connector
skips cleanly, exactly like every other credential-gated connector.
"""

from pathlib import Path

import demand_engine
from .extractors import base as extractor_base
from .extractors import claude_extractor, deterministic_extractor
from .feed_fetch import fetch_feed_entries

SOURCE_NAME = "Demand Signal"

COLLECTORS_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = COLLECTORS_DIR.parent
SEEN_ARTICLES_PATH = RUNTIME_DIR / "config" / "demand-signals-seen-articles.json"

NEEDED_SERVICES_DOMAIN_TAGS = ["ADGL", "AI Deployment Governance", "AI Governance", "Technology Risk"]

EXTRACTORS = {
    "deterministic": deterministic_extractor,
    "claude": claude_extractor,
}
DEFAULT_BACKEND = "deterministic"


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


def resolve_extractor(config):
    """Returns the configured extractor module, or None (with a
    printed reason) if its own dependency isn't available — never
    raises, and callers treat None exactly like any other
    missing-dependency connector: a clean skip."""
    backend_name = config.get("extractionBackend", DEFAULT_BACKEND)
    extractor = EXTRACTORS.get(backend_name)
    if extractor is None:
        print(f"    Demand Signals: unknown extractionBackend '{backend_name}', skipping")
        return None

    if backend_name == "deterministic":
        model_name = config.get("model") or "en_core_web_sm"
        if not deterministic_extractor.model_available(model_name):
            print(f"    Demand Signals: spaCy or its '{model_name}' model isn't installed — skipping. "
                  f"Run: pip install spacy && python3 -m spacy download {model_name}")
            return None
    elif backend_name == "claude":
        if not claude_extractor.model_available():
            print("    Demand Signals: extractionBackend is 'claude' but ANTHROPIC_API_KEY isn't "
                  "configured — skipping")
            return None

    return extractor


def collect(keywords, config):
    feed_urls = config.get("feedUrls", [])
    if not feed_urls:
        print("    Demand Signals: no feed URLs configured, skipping")
        return []

    extractor = resolve_extractor(config)
    if extractor is None:
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

            title = extractor_base.strip_html(entry.get("title", ""))
            summary = extractor_base.strip_html(entry.get("summary", ""))

            text = f"{title} {summary}"
            matched_categories = demand_engine.classify_categories(text, categories_config)
            if not matched_categories:
                continue  # no deterministic category matched — never spend extraction effort on this

            extraction = extractor.extract(title, summary, model=model)
            if not extraction or not extraction.get("isDemandSignal"):
                continue
            if extraction.get("confidence") != "high":
                print(f"    [skipped, confidence={extraction.get('confidence')}] "
                      f"{extraction.get('organisation') or title}")
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
