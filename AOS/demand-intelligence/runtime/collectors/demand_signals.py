"""
Demand Signals — proactive discovery, not job-board collection.

Monitors AI-vendor and tech-news RSS feeds for a specific pattern: a
named organisation (not the vendor) deploying/adopting an AI tool at
scale (e.g. "Company X deployed Copilot to 40,000 employees"). That
kind of event is a strong, early signal that the organisation will
soon need AI governance, human oversight, deployment controls, and
risk assessment — a stronger, higher-value discovery than a generic
"AI Analyst" job posting, and one no job board will ever surface.

Two-stage pipeline per feed entry:
  1. A real RSS/Atom fetch (feed_fetch.fetch_feed_entries, reused
     verbatim from 05-Market-Intelligence/runtime/feeds.py — the same
     dependency-free parser, not re-derived).
  2. Only entries not already seen (own seen-articles index, separate
     from collect.py's own opportunity-level dedupe-index.json, so a
     re-run never re-spends a Claude API call on an article already
     read) are sent to Claude (claude_client.extract_demand_signal) to
     decide: does this article name a specific organisation adopting
     an AI tool at scale? Only "high" confidence extractions become a
     lead — "medium"/"low" are logged, never fabricated into one.

Every extracted signal is scored well above a generic job posting's
defaults (see SIGNAL_SCORES below) — a named enterprise adopting AI at
scale is a materially stronger, more strategic discovery than "someone
is hiring" — landing it in opportunity-scoring-engine.md's existing
"Immediate Proposal" classification and "Priority" band entirely
through the unmodified scoring/classification pipeline every other
opportunity already goes through. No change to ingest.py's scoring or
classification logic was needed or made.

If ANTHROPIC_API_KEY is not set, this connector skips cleanly, exactly
like every other credential-gated connector.
"""

from pathlib import Path

from . import claude_client
from .feed_fetch import fetch_feed_entries

SOURCE_NAME = "Demand Signal"

COLLECTORS_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = COLLECTORS_DIR.parent
SEEN_ARTICLES_PATH = RUNTIME_DIR / "config" / "demand-signals-seen-articles.json"

# A named enterprise adopting AI at meaningful scale is a materially
# stronger, more strategic discovery than a generic job posting — these
# heuristic values (0-10, same scale and honesty convention as
# collectors/common.py's heuristic_scores) are tuned so a genuine,
# high-confidence signal lands at a priority_score >= 80
# (opportunity-scoring-engine.md's "Priority" band) with
# scopedEngagement=True, which demand-intelligence/runtime/ingest.py's
# existing, unmodified classify() then routes to "Immediate Proposal"
# — Sales Director prepares a first-touch proposal, Revenue Hunter adds
# it to the pipeline, CRM logs it "hot" — the same real playbook a
# named, scoped ask would get, because this is exactly what warrants
# proactive, insight-led outreach.
SIGNAL_SCORES = {
    "expectedRevenue": 9,
    "probabilityOfWinning": 7,
    "strategicValue": 10,
    "relationshipValue": 3,       # honest: no prior contact exists yet
    "timeRequired": 8,             # a template-driven, insight-led first-touch draft is fast to prepare
    "geography": 7,
    "remoteCompatibility": 9,
    "alignmentAIforUIServices": 10,
    "alignmentADGL": 10,
    "alignmentOPERA": 9,
    "longTermRelationshipPotential": 8,
}
# Verified (not just hand-calculated) to land in opportunity-scoring-engine.md's
# "Priority" band (>=80) via ingest.py's real compute_priority_score() —
# see tests/test_demand_signals.py's ScoringIntegrationTests, which runs
# these values through the actual, unmodified scoring/classification
# functions rather than trusting arithmetic done by hand.

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


def build_description(extraction, article_title, article_link):
    scale_part = f" at {extraction['scale']}" if extraction.get("scale") else ""
    industry_part = f" ({extraction['industry']})" if extraction.get("industry") else ""
    tool_part = extraction.get("aiTool") or "an AI system"
    return (
        f"{extraction['organisation']}{industry_part} was reported to have adopted "
        f"{tool_part}{scale_part}. This organisation likely needs AI governance, "
        f"human oversight, AI deployment controls, ADGL, and AI risk assessment "
        f"before/alongside this rollout.\n\n"
        f"Source article: \"{article_title}\" — {article_link}"
    )


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

    results = []
    for feed_url in feed_urls:
        entries = fetch_feed_entries(feed_url)
        for entry in entries:
            article_key = entry.get("guid") or entry.get("link")
            if not article_key or article_key in seen["seen"]:
                continue
            seen["seen"][article_key] = {"checked": True}

            extraction = claude_client.extract_demand_signal(
                entry.get("title", ""), entry.get("summary", ""), model=model,
            )
            if not extraction or not extraction.get("isDemandSignal"):
                continue
            if extraction.get("confidence") != "high":
                print(f"    [skipped, confidence={extraction.get('confidence')}] "
                      f"{extraction.get('organisation') or entry.get('title')}")
                continue
            if not extraction.get("organisation"):
                continue

            results.append({
                "source": SOURCE_NAME,
                "sourceCategory": "Technology Practice",
                "title": f"{extraction['organisation']} — AI deployment governance opportunity",
                "organisation": extraction["organisation"],
                "description": build_description(extraction, entry.get("title", ""), entry.get("link", "")),
                "url": entry.get("link"),
                "location": "Not specified",
                "remote": True,
                "domainTags": list(NEEDED_SERVICES_DOMAIN_TAGS),
                "scores": dict(SIGNAL_SCORES),
                "scopedEngagement": True,
                "recurrencePattern": "none",
                "autoScored": True,
                "autoCollected": True,
                "matchedKeywords": [],
            })
            print(f"    [signal] {extraction['organisation']} adopted {extraction.get('aiTool') or 'an AI tool'}"
                  f"{' at ' + extraction['scale'] if extraction.get('scale') else ''}")

    save_json(SEEN_ARTICLES_PATH, seen)
    return results
