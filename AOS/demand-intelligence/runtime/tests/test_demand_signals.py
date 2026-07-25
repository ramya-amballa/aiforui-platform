#!/usr/bin/env python3
"""
Unit tests for collectors/demand_signals.py: the connector skips
cleanly with no API key or no feed URLs, only "high" confidence
extractions become opportunity records, and — most importantly — that
this collector's tuned SIGNAL_SCORES actually land in
ingest.py's real, unmodified priority-scoring/classification pipeline
where they're supposed to: priority_score >= 80 (the "Priority" band)
and classification "Immediate Proposal", using ingest.py's real
compute_priority_score/band_for/classify functions, not a
reimplementation of them.

Every test mocks the network boundary (collectors.demand_signals's own
fetch_feed_entries and claude_client.extract_demand_signal) — no live
network or API call is made.

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

import ingest  # noqa: E402
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
             patch("collectors.demand_signals.SEEN_ARTICLES_PATH", self.tmp_path / "seen.json"):
            return demand_signals.collect([], {"feedUrls": ["https://example.com/feed"]})

    def test_high_confidence_creates_a_record(self):
        results = self._collect_with(HIGH_CONFIDENCE_EXTRACTION)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["organisation"], "Land O'Lakes")
        self.assertEqual(results[0]["source"], "Demand Signal")

    def test_medium_confidence_does_not_create_a_record(self):
        extraction = dict(HIGH_CONFIDENCE_EXTRACTION, confidence="medium")
        results = self._collect_with(extraction)
        self.assertEqual(results, [])

    def test_not_a_demand_signal_does_not_create_a_record(self):
        extraction = {"isDemandSignal": False, "organisation": "", "aiTool": "", "scale": "",
                      "industry": "", "confidence": "low"}
        results = self._collect_with(extraction)
        self.assertEqual(results, [])

    def test_missing_organisation_does_not_create_a_record(self):
        extraction = dict(HIGH_CONFIDENCE_EXTRACTION, organisation="")
        results = self._collect_with(extraction)
        self.assertEqual(results, [])


class ScoringIntegrationTests(unittest.TestCase):
    """Proves demand_signals.SIGNAL_SCORES actually produces the
    intended outcome through ingest.py's real, unmodified scoring and
    classification functions — not a hand-checked assumption."""

    def test_lands_in_priority_band_as_immediate_proposal(self):
        priority_score = ingest.compute_priority_score(demand_signals.SIGNAL_SCORES)
        self.assertGreaterEqual(priority_score, 80, "SIGNAL_SCORES should land in the Priority band")
        self.assertEqual(ingest.band_for(priority_score), "Priority")

        classification = ingest.classify(
            priority_score, demand_signals.SIGNAL_SCORES,
            source_category="Technology Practice", scoped_engagement=True,
            recurrence_pattern="none",
        )
        self.assertEqual(classification, "Immediate Proposal")


if __name__ == "__main__":
    unittest.main()
