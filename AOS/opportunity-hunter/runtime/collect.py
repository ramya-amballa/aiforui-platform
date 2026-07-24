#!/usr/bin/env python3
"""
Opportunity Hunter — Autonomous Collection Engine

Usage:
    python3 collect.py

Replaces manual opportunity entry with periodic, automated discovery.
For every source configured in config/sources.json:

  1. Calls that source's collector (collectors/<name>.py's
     collect(keywords, config)), searching with the keywords in
     config/keywords.json. A source with no config yet (no board
     tokens, no career-page URLs, no API key) or a source that fails
     for any reason returns/logs cleanly and never stops the run.
  2. Deduplicates every result against dedupe-index.json, keyed by URL
     (or, for sources with no URL, a source+organisation+title hash) —
     a posting already seen on a previous run is dropped silently.
  3. Writes every discovered posting (duplicates included) to
     snapshots/, a full historical record of what each run saw,
     independent of what passed dedup.
  4. Writes only the new (non-duplicate) postings to inbox/ as a single
     dated JSON file, in exactly the shape ingest.py already reads —
     no second parsing path.
  5. Invokes ingest.py's existing main(): the same scoring
     (opportunity-scoring-engine.md), classification, and routing to
     Revenue Hunter / CRM / CEO Advisor that manually-logged
     opportunities go through. This script does not reimplement any of
     that logic — it only discovers and normalises, then hands off.

Designed to run on a daily GitHub Actions schedule
(.github/workflows/opportunity-collection.yml).
"""

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
OPPORTUNITY_HUNTER_DIR = RUNTIME_DIR.parent
AOS_DIR = OPPORTUNITY_HUNTER_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_DIR = RUNTIME_DIR / "config"
INBOX_DIR = RUNTIME_DIR / "inbox"
SNAPSHOTS_DIR = RUNTIME_DIR / "snapshots"
DEDUPE_INDEX_PATH = RUNTIME_DIR / "dedupe-index.json"

TODAY = date.today().isoformat()

from collectors import (
    ashby, consulting_firms, flexjobs, google_jobs, greenhouse,
    lever, linkedin_jobs, remoteok, uae_recruiters, upwork, wellfound,
)

# Keys match config/sources.json exactly; every collector shares the
# collect(keywords, config) signature, so adding a new source later is
# one new module plus one line here — never a change to this loop.
COLLECTORS = {
    "greenhouse": greenhouse,
    "lever": lever,
    "ashby": ashby,
    "remoteok": remoteok,
    "upwork": upwork,
    "linkedinJobs": linkedin_jobs,
    "googleJobs": google_jobs,
    "wellfound": wellfound,
    "flexjobs": flexjobs,
    "uaeRecruiters": uae_recruiters,
    "consultingFirms": consulting_firms,
}

DEFAULT_DEDUPE_INDEX = {
    "schema": {
        "key": "string — sha256(url, or source|organisation|title when a source has no URL)[:16]",
        "firstSeen": "string — ISO 8601 date this key was first discovered",
        "source": "string",
        "title": "string",
    },
    "seen": {},
}


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def dedupe_key(opportunity):
    basis = opportunity.get("url") or "|".join([
        opportunity.get("source", ""),
        opportunity.get("organisation", ""),
        opportunity.get("title", ""),
    ])
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def run_collectors(keywords, sources_config):
    all_results = []
    per_source_counts = {}
    for name, module in COLLECTORS.items():
        config = sources_config.get(name, {})
        print(f"Collecting: {name}")
        try:
            results = module.collect(keywords, config)
        except Exception as exc:  # one source failing must never stop the run
            print(f"  {name}: collection failed: {exc}", file=sys.stderr)
            results = []
        per_source_counts[name] = len(results)
        all_results.extend(results)
    return all_results, per_source_counts


def main():
    keywords_data = load_json(CONFIG_DIR / "keywords.json", {"keywords": []})
    sources_config = load_json(CONFIG_DIR / "sources.json", {})
    keywords = keywords_data.get("keywords", [])

    if not keywords:
        print("No keywords configured in config/keywords.json. Nothing to search for.", file=sys.stderr)
        return 1

    all_results, per_source_counts = run_collectors(keywords, sources_config)

    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    save_json(SNAPSHOTS_DIR / f"{TODAY}-collection-snapshot.json", {
        "date": TODAY,
        "totalDiscovered": len(all_results),
        "perSource": per_source_counts,
        "opportunities": all_results,
    })

    dedupe_index = load_json(DEDUPE_INDEX_PATH, DEFAULT_DEDUPE_INDEX)
    dedupe_index.setdefault("seen", {})

    new_results = []
    for opp in all_results:
        key = dedupe_key(opp)
        if key in dedupe_index["seen"]:
            continue
        dedupe_index["seen"][key] = {"firstSeen": TODAY, "source": opp.get("source", ""), "title": opp.get("title", "")}
        new_results.append(opp)

    save_json(DEDUPE_INDEX_PATH, dedupe_index)

    print(f"\nDiscovered {len(all_results)} postings across {len(COLLECTORS)} sources; "
          f"{len(new_results)} are new after dedup.")

    if not new_results:
        print("No new opportunities. Nothing sent to ingest.")
        return 0

    INBOX_DIR.mkdir(exist_ok=True)
    inbox_path = INBOX_DIR / f"{TODAY}-collected.json"
    save_json(inbox_path, new_results)
    print(f"Wrote {len(new_results)} new opportunities to {inbox_path.relative_to(REPO_ROOT)}")

    import ingest
    return ingest.main()


if __name__ == "__main__":
    sys.exit(main())
