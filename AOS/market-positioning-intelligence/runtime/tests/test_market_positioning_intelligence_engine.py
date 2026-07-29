#!/usr/bin/env python3
"""
Unit and integration tests for Market Positioning Intelligence
(AOS Sprint 21).

The central property under test: this employee never fabricates
competitor, market-share, or win/loss data. Every test that touches
"competitive signal" confirms the honest static string, never a
computed number.

Run with:
    python3 -m unittest tests.test_market_positioning_intelligence_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import market_positioning_intelligence_engine as engine  # noqa: E402
import generate  # noqa: E402

CATALOGUE = {"primaryServices": ["AI Deployment Governance (ADGL)", "AI Governance Advisory", "Executive Workshop"]}


class ServiceDemandCoverageTests(unittest.TestCase):
    def test_counts_real_recommendations_per_service(self):
        recs = {
            "opp-1": {"primaryService": "AI Deployment Governance (ADGL)", "notApplicable": False},
            "opp-2": {"primaryService": "AI Deployment Governance (ADGL)", "notApplicable": False},
            "opp-3": {"primaryService": "AI Governance Advisory", "notApplicable": False},
        }
        coverage = engine.service_demand_coverage(CATALOGUE, recs)
        self.assertEqual(len(coverage), 3)
        by_service = {c["service"]: c["recommendationCount"] for c in coverage}
        self.assertEqual(by_service["AI Deployment Governance (ADGL)"], 2)
        self.assertEqual(by_service["AI Governance Advisory"], 1)

    def test_service_with_zero_recommendations_is_honestly_included(self):
        coverage = engine.service_demand_coverage(CATALOGUE, {})
        self.assertEqual(len(coverage), 3)
        self.assertTrue(all(c["recommendationCount"] == 0 for c in coverage))

    def test_not_applicable_recommendations_are_excluded(self):
        recs = {"opp-1": {"primaryService": "Executive Workshop", "notApplicable": True}}
        coverage = engine.service_demand_coverage(CATALOGUE, recs)
        by_service = {c["service"]: c["recommendationCount"] for c in coverage}
        self.assertEqual(by_service["Executive Workshop"], 0)

    def test_sorted_descending_by_count(self):
        recs = {
            "opp-1": {"primaryService": "Executive Workshop", "notApplicable": False},
            "opp-2": {"primaryService": "Executive Workshop", "notApplicable": False},
            "opp-3": {"primaryService": "AI Governance Advisory", "notApplicable": False},
        }
        coverage = engine.service_demand_coverage(CATALOGUE, recs)
        self.assertEqual(coverage[0]["service"], "Executive Workshop")


class RegulatoryTailwindsTests(unittest.TestCase):
    def test_counts_substantive_developments_by_source(self):
        log = {"log": [
            {"source": "EU AI Act", "substantive": True},
            {"source": "EU AI Act", "substantive": True},
            {"source": "DORA", "substantive": True},
            {"source": "GDPR", "substantive": False},
        ]}
        tailwinds, substantive_count = engine.regulatory_tailwinds(log)
        self.assertEqual(substantive_count, 3)
        by_source = {t["source"]: t["developmentCount"] for t in tailwinds}
        self.assertEqual(by_source["EU AI Act"], 2)
        self.assertEqual(by_source["DORA"], 1)
        self.assertNotIn("GDPR", by_source)

    def test_empty_log_is_honest(self):
        tailwinds, substantive_count = engine.regulatory_tailwinds({"log": []})
        self.assertEqual(tailwinds, [])
        self.assertEqual(substantive_count, 0)


class LostOpportunitiesTests(unittest.TestCase):
    def test_finds_only_lost_stage_entries(self):
        pipeline_data = {"pipeline": [
            {"organisation": "A Co", "title": "X", "stage": "lost"},
            {"organisation": "B Co", "title": "Y", "stage": "won"},
        ]}
        lost = engine.lost_opportunities(pipeline_data)
        self.assertEqual(lost, [{"organisation": "A Co", "title": "X"}])

    def test_never_includes_a_reason_or_competitor_field(self):
        pipeline_data = {"pipeline": [{"organisation": "A Co", "title": "X", "stage": "lost"}]}
        lost = engine.lost_opportunities(pipeline_data)
        self.assertEqual(set(lost[0].keys()), {"organisation", "title"})


class CompetitiveSignalHonestyTests(unittest.TestCase):
    def test_competition_not_tracked_string_is_static(self):
        self.assertIn("Not tracked", engine.COMPETITION_NOT_TRACKED)
        self.assertIn("no data source", engine.COMPETITION_NOT_TRACKED)


class RenderMarkdownTests(unittest.TestCase):
    def test_flags_unvalidated_services(self):
        coverage = [{"service": "AI Deployment Governance (ADGL)", "recommendationCount": 0}]
        markdown = engine.render_market_positioning_markdown(coverage, [], 0, [])
        self.assertIn("not yet validated by any real opportunity", markdown)

    def test_honest_empty_states(self):
        markdown = engine.render_market_positioning_markdown([], [], 0, [])
        self.assertIn("No substantive regulatory development logged yet", markdown)
        self.assertIn("Lost opportunities on record:** 0", markdown)
        self.assertIn(engine.COMPETITION_NOT_TRACKED, markdown)

    def test_real_data_appears_verbatim(self):
        coverage = [{"service": "AI Deployment Governance (ADGL)", "recommendationCount": 3}]
        tailwinds = [{"source": "EU AI Act", "developmentCount": 2}]
        lost = [{"organisation": "A Co", "title": "AI Governance Advisory"}]
        markdown = engine.render_market_positioning_markdown(coverage, tailwinds, 2, lost)
        self.assertIn("3 recommendation(s)", markdown)
        self.assertIn("EU AI Act", markdown)
        self.assertIn("A Co", markdown)


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_default_is_deep_copied_not_shared(self):
        first = engine.load_json(Path("/nonexistent/path.json"), {"log": []})
        first["log"].append({"source": "test"})
        second = engine.load_json(Path("/nonexistent/path.json"), {"log": []})
        self.assertEqual(second["log"], [])


class GenerateEndToEndTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)

        patches = [
            patch("market_positioning_intelligence_engine.SERVICE_CATALOGUE_PATH", self.tmp_path / "catalogue.json"),
            patch("market_positioning_intelligence_engine.SERVICE_RECOMMENDATIONS_PATH", self.tmp_path / "recs.json"),
            patch("market_positioning_intelligence_engine.REGULATORY_LOG_PATH", self.tmp_path / "reg_log.json"),
            patch("market_positioning_intelligence_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"),
            patch("market_positioning_intelligence_engine.FEED_PATH", self.tmp_path / "output" / "market-positioning-feed.json"),
            patch("market_positioning_intelligence_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_runs_honestly_empty_when_nothing_exists_yet(self):
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed = engine.load_json(self.tmp_path / "output" / "market-positioning-feed.json")
        self.assertEqual(feed["serviceDemandCoverage"], [])
        self.assertEqual(feed["lostOpportunities"], [])
        self.assertIn("Not tracked", feed["competitiveSignal"])

    def test_full_run_aggregates_all_sources(self):
        engine.save_json(self.tmp_path / "catalogue.json", CATALOGUE)
        engine.save_json(self.tmp_path / "recs.json", {"recommendations": {
            "opp-1": {"primaryService": "AI Deployment Governance (ADGL)", "notApplicable": False},
        }})
        engine.save_json(self.tmp_path / "reg_log.json", {"log": [
            {"source": "EU AI Act", "substantive": True},
        ]})
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": [
            {"organisation": "A Co", "title": "Test", "stage": "lost"},
        ]})

        exit_code = generate.main()
        self.assertEqual(exit_code, 0)

        feed = engine.load_json(self.tmp_path / "output" / "market-positioning-feed.json")
        self.assertEqual(len(feed["serviceDemandCoverage"]), 3)
        self.assertEqual(feed["substantiveRegulatoryDevelopmentCount"], 1)
        self.assertEqual(len(feed["lostOpportunities"]), 1)

        report = (self.tmp_path / "output" / "market-positioning-report.md").read_text(encoding="utf-8")
        self.assertIn("EU AI Act", report)
        self.assertIn("A Co", report)


if __name__ == "__main__":
    unittest.main()
