#!/usr/bin/env python3
"""
Unit tests for the offline extraction backend (AOS Sprint 7):
collectors/extractors/base.py's shared helpers and
collectors/extractors/deterministic_extractor.py's spaCy-NER-plus-rules
extraction. Requires spacy and en_core_web_sm to be installed; skipped
cleanly (not failed) if they aren't, exactly like the connector itself
would skip.

Run with:
    python3 -m unittest tests.test_deterministic_extractor -v   (from runtime/)
"""

import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from collectors.extractors import base  # noqa: E402
from collectors.extractors import deterministic_extractor as extractor  # noqa: E402

MODEL_MISSING = not extractor.model_available("en_core_web_sm")


class VendorBlocklistTests(unittest.TestCase):
    def test_recognises_known_vendors(self):
        self.assertTrue(base.is_vendor_name("Microsoft Copilot"))
        self.assertTrue(base.is_vendor_name("OpenAI"))

    def test_real_company_not_flagged(self):
        self.assertFalse(base.is_vendor_name("Land O'Lakes"))
        self.assertFalse(base.is_vendor_name("Acme Bank"))


class GenericWordFilterTests(unittest.TestCase):
    def test_bare_acronym_is_generic(self):
        self.assertTrue(base.is_generic_only("AI"))
        self.assertTrue(base.is_generic_only("Chief AI Officer"))

    def test_real_name_is_not_generic(self):
        self.assertFalse(base.is_generic_only("Acme AI"))
        self.assertFalse(base.is_generic_only("Beta Retail"))


class HtmlStrippingTests(unittest.TestCase):
    def test_strips_tags_without_gluing_words(self):
        html = "<p>MCP extends Dynamics 365.</p>\n<p>The post appeared first on <a href=\"x\">Microsoft Copilot Blog</a>.</p>"
        stripped = base.strip_html(html)
        self.assertNotIn("<", stripped)
        self.assertNotIn(">", stripped)
        self.assertIn("MCP extends Dynamics 365", stripped)

    def test_handles_none_and_empty(self):
        self.assertEqual(base.strip_html(None), "")
        self.assertEqual(base.strip_html(""), "")


class CapitalizedPhraseCandidatesTests(unittest.TestCase):
    def test_does_not_bridge_across_sentence_boundary(self):
        text = "The Chief AI Officer resigned. Beta Retail announced a new hire."
        candidates = base.capitalized_phrase_candidates(text)
        self.assertNotIn("Officer Beta", " ".join(candidates))
        self.assertIn("Beta Retail", candidates)


@unittest.skipIf(MODEL_MISSING, "spacy or en_core_web_sm not installed")
class DeterministicExtractionTests(unittest.TestCase):
    def test_vendor_headline_names_real_customer(self):
        result = extractor.extract(
            "Microsoft: Land O'Lakes deploys Copilot to 40,000 employees",
            "Land O'Lakes rolled out Microsoft Copilot across its workforce...",
        )
        self.assertTrue(result["isDemandSignal"])
        self.assertEqual(result["organisation"], "Land O'Lakes")
        self.assertEqual(result["confidence"], "high")
        self.assertEqual(result["scale"], "40,000 employees")

    def test_governance_announcement_names_bank(self):
        result = extractor.extract(
            "Acme Bank adopts AI governance framework",
            "Acme Bank announced a new responsible AI programme this week.",
        )
        self.assertTrue(result["isDemandSignal"])
        self.assertEqual(result["organisation"], "Acme Bank")
        self.assertEqual(result["industry"], "Financial Services")

    def test_unrelated_local_news_is_not_a_signal(self):
        result = extractor.extract(
            "Local bakery wins pastry award",
            "A neighbourhood bakery won a regional pastry competition.",
        )
        self.assertFalse(result["isDemandSignal"])

    def test_vendor_self_promotion_is_not_a_signal(self):
        result = extractor.extract(
            "OpenAI announces ChatGPT Enterprise updates",
            "OpenAI rolled out new features for ChatGPT Enterprise this week.",
        )
        self.assertFalse(result["isDemandSignal"])

    def test_startup_with_generic_ai_mention_still_names_the_company(self):
        result = extractor.extract(
            "Startup XYZ launches new AI assistant",
            "Startup XYZ unveiled an internal AI assistant for customer service.",
        )
        self.assertTrue(result["isDemandSignal"])
        self.assertEqual(result["organisation"], "Startup XYZ")
        self.assertEqual(result["confidence"], "high")


if __name__ == "__main__":
    unittest.main()
