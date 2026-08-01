#!/usr/bin/env python3
"""
Market Positioning Intelligence — generator (AOS Sprint 21)

Usage:
    python3 generate.py

A pure read-only aggregator, regenerated in full every run — nothing
here is founder-edited, so there is nothing to protect from being
overwritten. Reads service-mapping's own real recommendations,
market-intelligence's own regulatory log, and Revenue Hunter's
pipeline (for the one real, non-fabricated competitive data point AOS
has: a count of lost opportunities). Runs honestly even when every
source is still empty — an empty result here means nothing has
happened yet, not that the check failed.
"""

import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import market_positioning_intelligence_engine as engine  # noqa: E402


def main():
    service_catalogue = engine.load_json(engine.SERVICE_CATALOGUE_PATH, {"primaryServices": []})
    service_recommendations = engine.load_json(
        engine.SERVICE_RECOMMENDATIONS_PATH, {"recommendations": {}}
    ).get("recommendations", {})
    regulatory_log = engine.load_json(engine.REGULATORY_LOG_PATH, {"log": []})
    pipeline_data = engine.load_json(engine.PIPELINE_PATH, {"pipeline": []})

    coverage = engine.service_demand_coverage(service_catalogue, service_recommendations)
    tailwinds, substantive_count = engine.regulatory_tailwinds(regulatory_log)
    lost = engine.lost_opportunities(pipeline_data)

    feed = {
        "schema": {
            "serviceDemandCoverage": "array of {service, recommendationCount} — every one of the 10 catalogue services, sorted by count",
            "regulatoryTailwinds": "array of {source, developmentCount} — substantive developments only",
            "substantiveRegulatoryDevelopmentCount": "number",
            "competitiveSignal": "string — always honest; AOS has no competitor/market-share data source",
            "lostOpportunities": "array of {organisation, title} — real pipeline.json stage=='lost' entries only",
        },
        "serviceDemandCoverage": coverage,
        "regulatoryTailwinds": tailwinds,
        "substantiveRegulatoryDevelopmentCount": substantive_count,
        "competitiveSignal": engine.COMPETITION_NOT_TRACKED,
        "lostOpportunities": lost,
    }
    engine.save_json(engine.FEED_PATH, feed)

    report = engine.render_market_positioning_markdown(coverage, tailwinds, substantive_count, lost)
    report_path = engine.FEED_PATH.parent / f"{engine.TODAY}-market-positioning-report.md"
    report_path.write_text(report, encoding="utf-8")
    (engine.FEED_PATH.parent / "market-positioning-report.md").write_text(report, encoding="utf-8")

    unvalidated = [c["service"] for c in coverage if c["recommendationCount"] == 0]
    print(f"Service demand coverage: {len(coverage) - len(unvalidated)}/{len(coverage)} services validated by real demand")
    print(f"Regulatory tailwinds: {len(tailwinds)} source(s), {substantive_count} substantive development(s)")
    print(f"Lost opportunities on record: {len(lost)}")
    print(f"Report: {report_path.relative_to(engine.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
