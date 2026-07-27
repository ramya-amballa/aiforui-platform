#!/usr/bin/env python3
"""
Unit and integration tests for Tender & RFP Intelligence (AOS Sprint 14).

Every test uses hand-built fixture feed entries and a fixture config;
generate.py's own tests patch fetch_feed_entries so nothing here makes
a real network call.

Run with:
    python3 -m unittest tests.test_tender_intelligence_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import tender_intelligence_engine as engine  # noqa: E402
import generate  # noqa: E402

CONFIG = {
    "domainKeywords": {
        "AI Governance": ["ai governance"],
        "Responsible AI": ["responsible ai"],
        "Cyber Risk": ["cybersecurity", "cyber risk"],
        "Vendor Risk": ["third-party risk"],
        "Compliance": ["regulatory compliance"],
    },
    "deadlinePatterns": [
        "deadline[:\\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})",
        "closing date[:\\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})",
    ],
    "localPartnerRequiredSourceTypes": ["Government", "UAE"],
    "fitScoreByDomainMatchCount": {"1": 40, "2": 65, "3": 85},
    "fitScoreCap": 95,
    "recommendedResponseByFitBand": {
        "High": "Prepare a full response.",
        "Medium": "Register interest and monitor.",
        "Low": "Note only.",
    },
    "fitBandThresholds": {"high": 70, "medium": 40},
}


class ClassifyDomainsTests(unittest.TestCase):
    def test_matches_multiple_domains(self):
        text = "Request for proposal: AI Governance and Cybersecurity advisory services."
        matched = engine.classify_domains(text, CONFIG["domainKeywords"])
        self.assertIn("AI Governance", matched)
        self.assertIn("Cyber Risk", matched)

    def test_no_match_returns_empty(self):
        text = "Tender for road construction and asphalt supply."
        matched = engine.classify_domains(text, CONFIG["domainKeywords"])
        self.assertEqual(matched, [])


class ParseEstimatedValueTests(unittest.TestCase):
    def test_parses_dollar_millions(self):
        amount, currency = engine.parse_estimated_value("Estimated contract value $2.5M over three years.")
        self.assertEqual(currency, "USD")
        self.assertAlmostEqual(amount, 2_500_000)

    def test_parses_known_currency_code(self):
        amount, currency = engine.parse_estimated_value("Budget: EUR 500,000 for this engagement.")
        self.assertEqual(currency, "EUR")
        self.assertAlmostEqual(amount, 500_000)

    def test_no_number_returns_none_honestly(self):
        amount, currency = engine.parse_estimated_value("No budget has been disclosed for this tender.")
        self.assertIsNone(amount)

    def test_unknown_three_letter_word_is_not_mistaken_for_currency(self):
        # "for" is a stray English word, not a currency code — must not
        # be mislabelled the way the un-narrowed upstream parser would.
        amount, currency = engine.parse_estimated_value("Request for proposal, no budget disclosed.")
        self.assertIsNone(currency)

    def test_a_deadline_date_is_never_mistaken_for_an_estimated_value(self):
        # Real bug caught during live verification: a tender with no
        # monetary figure at all, but a "Closing date: 2026-08-20" —
        # without a real currency marker nearby, this must not turn the
        # date's own digits into a fabricated-looking monetary estimate.
        amount, currency = engine.parse_estimated_value(
            "UAE government agency seeking cybersecurity and third-party risk assessment. Closing date: 2026-08-20."
        )
        self.assertIsNone(amount)
        self.assertIsNone(currency)


class FormatEstimatedValueTests(unittest.TestCase):
    def test_none_is_not_specified(self):
        self.assertEqual(engine.format_estimated_value(None, None), "Not specified")

    def test_millions_formatted(self):
        self.assertEqual(engine.format_estimated_value(2_500_000, "USD"), "USD 2.5M")


class FitScoreTests(unittest.TestCase):
    def test_more_domain_matches_scores_higher(self):
        one = engine.fit_score(["AI Governance"], CONFIG)
        two = engine.fit_score(["AI Governance", "Cyber Risk"], CONFIG)
        three = engine.fit_score(["AI Governance", "Cyber Risk", "Compliance"], CONFIG)
        self.assertLess(one, two)
        self.assertLess(two, three)

    def test_every_fit_band_is_reachable(self):
        self.assertEqual(engine.fit_band(85, CONFIG), "High")
        self.assertEqual(engine.fit_band(50, CONFIG), "Medium")
        self.assertEqual(engine.fit_band(10, CONFIG), "Low")


class RequiredPartnersTests(unittest.TestCase):
    def test_flags_local_partner_for_configured_source_type(self):
        note = engine.required_partners_note("Government", CONFIG)
        self.assertIn("local", note.lower())

    def test_honest_not_specified_for_other_source_types(self):
        note = engine.required_partners_note("World Bank", CONFIG)
        self.assertIn("Not specified", note)


class ParseDeadlineTests(unittest.TestCase):
    def test_extracts_deadline_date(self):
        deadline = engine.parse_deadline("Submission deadline: 2026-09-15 for all bidders.", CONFIG["deadlinePatterns"])
        self.assertEqual(deadline, "2026-09-15")

    def test_none_when_absent(self):
        deadline = engine.parse_deadline("No date mentioned in this notice.", CONFIG["deadlinePatterns"])
        self.assertIsNone(deadline)


class BuildTenderEntryTests(unittest.TestCase):
    def test_returns_none_when_no_domain_matches(self):
        entry = {"title": "Road construction tender", "summary": "Asphalt and paving services.", "link": "https://example.com/1"}
        result = engine.build_tender_entry(entry, "Government", CONFIG)
        self.assertIsNone(result)

    def test_builds_full_entry_when_domain_matches(self):
        entry = {
            "title": "AI Governance Advisory RFP",
            "summary": "Seeking AI Governance advisory services. Estimated budget $1.2M. Deadline: 2026-10-01.",
            "link": "https://example.com/2",
        }
        result = engine.build_tender_entry(entry, "UN", CONFIG)
        self.assertIsNotNone(result)
        self.assertEqual(result["sourceType"], "UN")
        self.assertIn("AI Governance", result["matchedDomains"])
        self.assertEqual(result["deadline"], "2026-10-01")
        self.assertIn("1.2M", result["estimatedValue"])
        self.assertIn("Not specified", result["eligibility"])

    def test_never_fabricates_estimated_value_or_deadline(self):
        entry = {
            "title": "Vendor Risk Assessment RFP",
            "summary": "Seeking third-party risk assessment services. No budget or deadline disclosed.",
            "link": "https://example.com/3",
        }
        result = engine.build_tender_entry(entry, "Banking", CONFIG)
        self.assertEqual(result["estimatedValue"], "Not specified")
        self.assertEqual(result["deadline"], "Not specified")


class BuildFeedTests(unittest.TestCase):
    def test_sorted_by_estimated_value_descending_unestimated_last(self):
        tenders = [
            {"title": "A", "estimatedValueAmount": None},
            {"title": "B", "estimatedValueAmount": 5_000_000},
            {"title": "C", "estimatedValueAmount": 1_000_000},
        ]
        feed = engine.build_feed(tenders)
        titles = [t["title"] for t in feed["tenders"]]
        self.assertEqual(titles, ["B", "C", "A"])


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_default_is_deep_copied_not_shared(self):
        first = engine.load_json(Path("/nonexistent/path.json"), {"seen": {}})
        first["seen"]["X"] = {"checked": True}
        second = engine.load_json(Path("/nonexistent/path.json"), {"seen": {}})
        self.assertEqual(second["seen"], {})


class GenerateEndToEndTests(unittest.TestCase):
    """Runs the real generate.main() over mocked feed entries (no real
    network call), confirming a genuinely new tender is written to the
    feed and an unconfigured connector does nothing."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)

        patches = [
            patch("tender_intelligence_engine.SEEN_TENDERS_PATH", self.tmp_path / "tender-seen.json"),
            patch("tender_intelligence_engine.FEED_PATH", self.tmp_path / "output" / "tender-intelligence-feed.json"),
            patch("tender_intelligence_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_no_feed_urls_configured_writes_empty_honest_feed(self):
        with patch("generate.engine.load_config", return_value={"feedUrls": []}):
            exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed = engine.load_json(self.tmp_path / "output" / "tender-intelligence-feed.json")
        self.assertEqual(feed["tenders"], [])

    def test_matching_entry_from_configured_feed_is_written(self):
        config = dict(CONFIG, feedUrls=[{"url": "https://example.com/feed.xml", "sourceType": "UN"}])
        fake_entries = [{
            "title": "AI Governance Advisory RFP",
            "summary": "Seeking AI Governance advisory services. Budget $1.2M.",
            "link": "https://example.com/tender/1",
            "guid": "https://example.com/tender/1",
        }]
        with patch("generate.engine.load_config", return_value=config), \
             patch("generate.fetch_feed_entries", return_value=fake_entries):
            exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed = engine.load_json(self.tmp_path / "output" / "tender-intelligence-feed.json")
        self.assertEqual(len(feed["tenders"]), 1)
        self.assertEqual(feed["tenders"][0]["sourceType"], "UN")

    def test_rerun_does_not_duplicate_already_seen_tender(self):
        config = dict(CONFIG, feedUrls=[{"url": "https://example.com/feed.xml", "sourceType": "UN"}])
        fake_entries = [{
            "title": "AI Governance Advisory RFP",
            "summary": "Seeking AI Governance advisory services.",
            "link": "https://example.com/tender/1",
            "guid": "https://example.com/tender/1",
        }]
        with patch("generate.engine.load_config", return_value=config), \
             patch("generate.fetch_feed_entries", return_value=fake_entries):
            generate.main()
            generate.main()
        feed = engine.load_json(self.tmp_path / "output" / "tender-intelligence-feed.json")
        self.assertEqual(len(feed["tenders"]), 1)


if __name__ == "__main__":
    unittest.main()
