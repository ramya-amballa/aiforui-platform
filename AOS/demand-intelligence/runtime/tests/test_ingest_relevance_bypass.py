#!/usr/bin/env python3
"""
Regression test for ingest.py's compute_relevance_for_record() — the
one change website-intake/ required in Demand Intelligence. Confirms
website-sourced records bypass scoring while every other source is
still scored exactly as relevance.py's own model produces, unchanged.

Run with:
    python3 -m unittest tests.test_ingest_relevance_bypass -v   (from runtime/)
"""

import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import ingest  # noqa: E402
import relevance  # noqa: E402


class RelevanceBypassTests(unittest.TestCase):
    def test_website_source_bypasses_scoring(self):
        record = {
            "source": "Website", "title": "Website Enquiry — ADGL enquiry",
            "organisation": "Acme Bank", "description": "General conversational enquiry text.",
        }
        result = ingest.compute_relevance_for_record(record)
        self.assertEqual(result["score"], 100)
        self.assertIsNone(result["reason"])

    def test_non_website_source_still_scored_by_relevance_model(self):
        # A real false positive from opportunity-relevance-engine.md's
        # own worked example: "RAG" as a bare substring match, no real
        # AI-governance content — must still score low and unchanged.
        record = {
            "source": "RemoteOK", "title": "Paralegal",
            "organisation": "Giga Energy", "description": "Drag files into the storage folder.",
        }
        result = ingest.compute_relevance_for_record(record)
        self.assertEqual(result, relevance.compute_relevance(record))
        self.assertLess(result["score"], relevance.RELEVANCE_THRESHOLD)

    def test_missing_source_field_is_scored_not_bypassed(self):
        # Only an exact "Website" source bypasses — anything else,
        # including an absent source, goes through the real model.
        record = {"title": "Some Role", "organisation": "Some Co", "description": "No AI content at all."}
        result = ingest.compute_relevance_for_record(record)
        self.assertEqual(result, relevance.compute_relevance(record))


if __name__ == "__main__":
    unittest.main()
