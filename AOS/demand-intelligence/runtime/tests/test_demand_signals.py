#!/usr/bin/env python3
"""
Unit tests for collectors/demand_signals.py: the connector skips
cleanly with no API key or no feed URLs, and only "high" confidence
extractions of a real, deterministically-category-matched article
become opportunity records. Score/classification correctness is
covered in tests/test_demand_engine.py — this file is scoped to the
collector's own gating and wiring logic.

Every test mocks the network boundary (collectors.demand_signals's own
fetch_feed_entries and claude_client.extract_demand_signal) — no live
network or API call is made. Profile/feed file paths are redirected to
a temp directory so tests never touch real AOS data.

Run with:
    python3 -m unittest tests.test_demand_signals -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import demand_engine  # noqa: E402
from collectors import demand_signals  # noqa: E402

FAKE_ENTRY = {
    "title": "Microsoft: Land O'Lakes deploys Copilot to 40,000 employees",
    "link": "https://example.com/article-1",
    "summary": "Land O'Lakes rolled out Microsoft Copilot across its workforce...",
    "published": "2026-07-25",
    "guid": "https://example.com/article-1",
}

HIGH_CONFIDENCE_EXTRACTION = {
    "isDemandSignal": True,
    "organisation": "Land O'Lakes",
    "eventSummary": "Land O'Lakes deployed Microsoft Copilot to 40,000 employees.",
    "aiTool": "Microsoft Copilot",
    "scale": "40,000 employees",
    "industry": "Agriculture",
    "confidence": "high",
}


class ConnectorSkipTests(unittest.TestCase):
    def test_no_api_key_skips_cleanly(self):
        with patch("collectors.claude_client.api_key_configured", return_value=False):
            results = demand_signals.collect([], {"feedUrls": ["https://example.com/feed"]})
        self.assertEqual(results, [])

    def test_no_feed_urls_skips_cleanly(self):
        with patch("collectors.claude_client.api_key_configured", return_value=True):
            results = demand_signals.collect([], {"feedUrls": []})
        self.assertEqual(results, [])


class ExtractionGatingTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _collect_with(self, extraction):
        with patch("collectors.claude_client.api_key_configured", return_value=True), \
             patch("collectors.demand_signals.fetch_feed_entries", return_value=[FAKE_ENTRY]), \
             patch("collectors.claude_client.extract_demand_signal", return_value=extraction), \
             patch("collectors.demand_signals.SEEN_ARTICLES_PATH", self.tmp_path / "seen.json"), \
             patch("demand_engine.PROFILES_PATH", self.tmp_path / "organisation-profiles.json"), \
             patch("demand_engine.TOP_ORGANISATIONS_PATH", self.tmp_path / "top-organisations-this-week.json"), \
             patch("demand_engine.CRM_PATH", self.tmp_path / "company-intelligence.json"), \
             patch("demand_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"), \
             patch("demand_engine.SALES_FEED_PATH", self.tmp_path / "ceo-advisor-feed.json"):
            return demand_signals.collect([], {"feedUrls": ["https://example.com/feed"]})

    def test_high_confidence_creates_a_record(self):
        results = self._collect_with(HIGH_CONFIDENCE_EXTRACTION)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["organisation"], "Land O'Lakes")
        self.assertEqual(results[0]["source"], "Demand Signal")
        self.assertIn("expectedRevenue", results[0]["scores"])

    def test_medium_confidence_does_not_create_a_record(self):
        extraction = dict(HIGH_CONFIDENCE_EXTRACTION, confidence="medium")
        results = self._collect_with(extraction)
        self.assertEqual(results, [])

    def test_not_a_demand_signal_does_not_create_a_record(self):
        extraction = {"isDemandSignal": False, "organisation": "", "eventSummary": "", "aiTool": "",
                      "scale": "", "industry": "", "confidence": "low"}
        results = self._collect_with(extraction)
        self.assertEqual(results, [])

    def test_missing_organisation_does_not_create_a_record(self):
        extraction = dict(HIGH_CONFIDENCE_EXTRACTION, organisation="")
        results = self._collect_with(extraction)
        self.assertEqual(results, [])

    def test_updates_organisation_profile(self):
        with patch("collectors.claude_client.api_key_configured", return_value=True), \
             patch("collectors.demand_signals.fetch_feed_entries", return_value=[FAKE_ENTRY]), \
             patch("collectors.claude_client.extract_demand_signal", return_value=HIGH_CONFIDENCE_EXTRACTION), \
             patch("collectors.demand_signals.SEEN_ARTICLES_PATH", self.tmp_path / "seen.json"), \
             patch("demand_engine.PROFILES_PATH", self.tmp_path / "organisation-profiles.json"), \
             patch("demand_engine.TOP_ORGANISATIONS_PATH", self.tmp_path / "top-organisations-this-week.json"), \
             patch("demand_engine.CRM_PATH", self.tmp_path / "company-intelligence.json"), \
             patch("demand_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"), \
             patch("demand_engine.SALES_FEED_PATH", self.tmp_path / "ceo-advisor-feed.json"):
            demand_signals.collect([], {"feedUrls": ["https://example.com/feed"]})

        profiles = demand_engine.load_json(self.tmp_path / "organisation-profiles.json", {})
        self.assertIn("Land O'Lakes", profiles.get("organisations", {}))

        feed = demand_engine.load_json(self.tmp_path / "top-organisations-this-week.json", {})
        self.assertEqual(len(feed.get("organisations", [])), 1)
        self.assertEqual(feed["organisations"][0]["organisation"], "Land O'Lakes")

    def test_article_matching_no_category_never_calls_claude(self):
        irrelevant_entry = dict(FAKE_ENTRY, title="Local bakery wins pastry award",
                                 summary="A neighbourhood bakery won a regional pastry competition.")
        with patch("collectors.claude_client.api_key_configured", return_value=True), \
             patch("collectors.demand_signals.fetch_feed_entries", return_value=[irrelevant_entry]), \
             patch("collectors.claude_client.extract_demand_signal") as mock_extract, \
             patch("collectors.demand_signals.SEEN_ARTICLES_PATH", self.tmp_path / "seen.json"), \
             patch("demand_engine.PROFILES_PATH", self.tmp_path / "organisation-profiles.json"), \
             patch("demand_engine.TOP_ORGANISATIONS_PATH", self.tmp_path / "top-organisations-this-week.json"):
            results = demand_signals.collect([], {"feedUrls": ["https://example.com/feed"]})
        mock_extract.assert_not_called()
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
