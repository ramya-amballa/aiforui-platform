#!/usr/bin/env python3
"""
Tender & RFP Intelligence — daily generator (AOS Sprint 14)

Usage:
    python3 generate.py

Reads config/tender-intelligence-config.json's feedUrls — each entry
{"url", "sourceType"} — and fetches every configured procurement RSS/
Atom feed via feed_fetch.fetch_feed_entries (a real network fetch, the
same dependency-free approach demand-intelligence/market-intelligence
already use). No feed URLs configured means this connector cleanly
does nothing, honestly, rather than fabricating a tender.

Every fetched entry is classified against seven deterministic domain
keywords (see tender_intelligence_engine.classify_domains); entries
matching none are skipped entirely, never treated as GRC-relevant on a
guess. Matching entries are deduped against a persistent
config/tender-seen.json index so a re-run only reports genuinely new
tenders.

Writes output/{date}-tender-intelligence-report.md and
output/tender-intelligence-feed.json.
"""

import sys
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import tender_intelligence_engine as engine  # noqa: E402
from feed_fetch import fetch_feed_entries  # noqa: E402

TODAY = date.today().isoformat()


def collect(config):
    feed_sources = config.get("feedUrls", [])
    if not feed_sources:
        print("    Tender Intelligence: no feed URLs configured, skipping")
        return []

    seen = engine.load_json(engine.SEEN_TENDERS_PATH, {"seen": {}})
    seen.setdefault("seen", {})

    tenders = []
    for source in feed_sources:
        url = source.get("url")
        source_type = source.get("sourceType", "Not specified")
        if not url:
            continue
        entries = fetch_feed_entries(url)
        for entry in entries:
            key = entry.get("guid") or entry.get("link")
            if not key or key in seen["seen"]:
                continue
            seen["seen"][key] = {"checked": True}

            tender = engine.build_tender_entry(entry, source_type, config)
            if tender is None:
                continue
            tenders.append(tender)
            print(f"    [tender] {tender['title']} ({source_type}) -> fit {tender['fitScore']}/100 "
                  f"({tender['fitBand']}), value {tender['estimatedValue']}")

    engine.save_json(engine.SEEN_TENDERS_PATH, seen)
    return tenders


def render_report(feed):
    tenders = feed["tenders"]
    lines = [
        "# Tender & RFP Intelligence — Daily Report",
        "",
        f"**Date:** {TODAY}",
        f"**Tenders tracked:** {len(tenders)}",
        "",
    ]
    if not tenders:
        lines.append("_No tenders tracked yet — configure real procurement feed URLs in "
                      "config/tender-intelligence-config.json's feedUrls._")
        lines.append("")
        return "\n".join(lines)

    for t in tenders:
        lines += [
            f"## {t['title']} ({t['sourceType']})",
            "",
            f"**Fit Score:** {t['fitScore']}/100 ({t['fitBand']})  ",
            f"**Estimated Value:** {t['estimatedValue']}  ",
            f"**Deadline:** {t['deadline']}  ",
            f"**Matched Domains:** {', '.join(t['matchedDomains'])}",
            "",
            t["tenderSummary"],
            "",
            f"**Eligibility:** {t['eligibility']}",
            "",
            f"**Required Partners:** {t['requiredPartners']}",
            "",
            f"**Recommended Response:** {t['recommendedResponse']}",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def main():
    config = engine.load_config()
    tenders = collect(config)

    # Every tender ever collected accumulates in the feed (persistent,
    # not just this run's new ones) — merge with whatever the feed
    # already has, keyed by sourceUrl, same accumulation pattern as
    # organisation-profiles.json/recruiter-profiles.json.
    existing_feed = engine.load_json(engine.FEED_PATH, {"tenders": []})
    by_url = {t.get("sourceUrl"): t for t in existing_feed.get("tenders", [])}
    for t in tenders:
        by_url[t["sourceUrl"]] = t

    feed = engine.build_feed(list(by_url.values()))
    engine.FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine.save_json(engine.FEED_PATH, feed)

    if not feed["tenders"]:
        print("No tenders tracked yet. Nothing more to do.")

    report_path = engine.FEED_PATH.parent / f"{TODAY}-tender-intelligence-report.md"
    report_path.write_text(render_report(feed), encoding="utf-8")

    print(f"{len(tenders)} new tender(s) this run, {len(feed['tenders'])} tracked overall. "
          f"Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
