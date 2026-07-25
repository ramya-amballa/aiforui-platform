#!/usr/bin/env python3
"""
Unit tests for demand_engine.py (AOS Sprint 6 — Demand Intelligence v2):
category classification, Overall Demand Score aggregation, service
prediction, Buying Readiness Score/band, next-action recommendation,
the templated Opportunity Narrative, and Part 8's deterministic
feedback weighting. All against fixtures, never real AOS data.

Run with:
    python3 -m unittest tests.test_demand_engine -v   (from runtime/)
"""

import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import demand_engine as de  # noqa: E402

CONFIG = de.load_categories_config()


class CategoryClassificationTests(unittest.TestCase):
    def test_ai_adoption_keyword_matches(self):
        cats = de.classify_categories("Acme Corp announced a Microsoft Copilot rollout company-wide", CONFIG)
        self.assertIn("ai_adoption", cats)

    def test_multiple_categories_can_match_one_text(self):
        text = "Acme Corp appointed a Chief AI Officer while preparing for the EU AI Act"
        cats = de.classify_categories(text, CONFIG)
        self.assertIn("governance_trigger", cats)
        self.assertIn("regulatory_trigger", cats)

    def test_no_keywords_matches_nothing(self):
        cats = de.classify_categories("Acme Corp opened a new bakery downtown", CONFIG)
        self.assertEqual(cats, [])

    def test_failure_trigger_keyword_matches(self):
        cats = de.classify_categories("Acme Corp faces an AI lawsuit after a data leakage incident", CONFIG)
        self.assertIn("failure_trigger", cats)


class OverallDemandScoreTests(unittest.TestCase):
    def test_single_category_high_confidence(self):
        score = de.compute_overall_demand_score(["ai_adoption"], "high", CONFIG)
        self.assertEqual(score, 70)

    def test_no_categories_scores_zero(self):
        self.assertEqual(de.compute_overall_demand_score([], "high", CONFIG), 0)

    def test_lower_confidence_scores_lower(self):
        high = de.compute_overall_demand_score(["ai_adoption"], "high", CONFIG)
        medium = de.compute_overall_demand_score(["ai_adoption"], "medium", CONFIG)
        low = de.compute_overall_demand_score(["ai_adoption"], "low", CONFIG)
        self.assertGreater(high, medium)
        self.assertGreater(medium, low)

    def test_stacking_categories_scores_higher_than_either_alone(self):
        # Neither category alone hits the 100 cap, so stacking is
        # actually observable here (regulatory_trigger + failure_trigger
        # both individually cap at/near 100, which would mask this).
        both = de.compute_overall_demand_score(["ai_adoption", "funding_trigger"], "high", CONFIG)
        either = max(
            de.compute_overall_demand_score(["ai_adoption"], "high", CONFIG),
            de.compute_overall_demand_score(["funding_trigger"], "high", CONFIG),
        )
        self.assertGreater(both, either)

    def test_score_never_exceeds_100(self):
        score = de.compute_overall_demand_score(
            ["failure_trigger", "regulatory_trigger", "governance_trigger", "ai_adoption", "funding_trigger"],
            "high", CONFIG,
        )
        self.assertLessEqual(score, 100)

    def test_conversion_multiplier_scales_score(self):
        base = de.compute_overall_demand_score(["ai_adoption"], "high", CONFIG, conversion_multiplier=1.0)
        boosted = de.compute_overall_demand_score(["ai_adoption"], "high", CONFIG, conversion_multiplier=1.2)
        self.assertGreater(boosted, base)


class ServicePredictionTests(unittest.TestCase):
    def test_empty_categories_returns_no_services(self):
        self.assertEqual(de.predict_services([], CONFIG), [])

    def test_single_category_returns_its_ranked_list(self):
        services = de.predict_services(["ai_adoption"], CONFIG)
        self.assertEqual(services, CONFIG["categoryToServices"]["ai_adoption"])

    def test_service_suggested_by_two_categories_ranks_above_single_mention(self):
        services = de.predict_services(["governance_trigger", "funding_trigger"], CONFIG)
        # "AI Governance Operating Model" appears in both categories' lists —
        # it should outrank a service only one of them suggests.
        self.assertEqual(services[0], "AI Governance Operating Model")


class BuyingReadinessScoreTests(unittest.TestCase):
    def test_failure_trigger_scores_higher_band_than_ai_adoption_alone(self):
        adoption_score = de.compute_overall_demand_score(["ai_adoption"], "high", CONFIG)
        _, adoption_band = de.compute_buying_readiness_score(["ai_adoption"], "high", None, adoption_score, CONFIG)

        failure_score = de.compute_overall_demand_score(["failure_trigger"], "high", CONFIG)
        _, failure_band = de.compute_buying_readiness_score(["failure_trigger"], "high", None, failure_score, CONFIG)

        band_rank = {"Low": 0, "Medium": 1, "High": 2, "Very High": 3}
        self.assertGreater(band_rank[failure_band], band_rank[adoption_band])

    def test_band_is_one_of_four_valid_values(self):
        score = de.compute_overall_demand_score(["ai_adoption"], "medium", CONFIG)
        _, band = de.compute_buying_readiness_score(["ai_adoption"], "medium", None, score, CONFIG)
        self.assertIn(band, ("Low", "Medium", "High", "Very High"))

    def test_larger_scale_scores_at_least_as_high_as_unknown_scale(self):
        score = de.compute_overall_demand_score(["ai_adoption"], "high", CONFIG)
        large, _ = de.compute_buying_readiness_score(["ai_adoption"], "high", "40,000 employees", score, CONFIG)
        unknown, _ = de.compute_buying_readiness_score(["ai_adoption"], "high", None, score, CONFIG)
        self.assertGreaterEqual(large, unknown)


class NextActionTests(unittest.TestCase):
    def test_low_confidence_always_waits(self):
        action, _ = de.recommend_next_action("Very High", ["failure_trigger"], "low", CONFIG)
        self.assertEqual(action, "Wait")

    def test_failure_trigger_prepares_a_proposal_regardless_of_band(self):
        action, _ = de.recommend_next_action("Medium", ["failure_trigger"], "high", CONFIG)
        self.assertEqual(action, "Prepare Proposal")

    def test_low_band_recommends_monitor(self):
        action, _ = de.recommend_next_action("Low", ["funding_trigger"], "medium", CONFIG)
        self.assertEqual(action, "Monitor")


class OpportunityNarrativeTests(unittest.TestCase):
    def test_contains_required_sections(self):
        services = ["AI Deployment Governance (ADGL)", "AI Risk Assessment"]
        narrative = de.build_opportunity_narrative(
            "Acme Corp", ["ai_adoption"], "Acme Corp deployed Copilot to 10,000 staff", services, "high", CONFIG,
        )
        self.assertIn("Potential AI for U&I engagement:", narrative)
        self.assertIn("• AI Deployment Governance (ADGL)", narrative)
        self.assertIn("Confidence: High", narrative)

    def test_no_marketing_superlatives(self):
        services = ["AI Risk Assessment"]
        narrative = de.build_opportunity_narrative(
            "Acme Corp", ["ai_adoption"], "Acme Corp deployed an AI assistant", services, "medium", CONFIG,
        )
        for banned in ("amazing", "revolutionary", "game-changing", "unlock", "supercharge"):
            self.assertNotIn(banned, narrative.lower())


class FeedbackWeightingTests(unittest.TestCase):
    def test_no_history_gives_neutral_multiplier(self):
        profiles = {"organisations": {}}
        multiplier = de.category_conversion_multiplier("ai_adoption", profiles, CONFIG)
        self.assertEqual(multiplier, 1.0)

    def test_converted_history_boosts_multiplier(self):
        profiles = {"organisations": {
            "Acme": {"matchedCategories": ["ai_adoption"], "converted": True, "outreachHappened": True,
                      "proposalCreated": True, "lastSeen": de.TODAY},
        }}
        multiplier = de.category_conversion_multiplier("ai_adoption", profiles, CONFIG)
        self.assertGreater(multiplier, 1.0)

    def test_stalled_history_lowers_multiplier(self):
        profiles = {"organisations": {
            "StaleCo": {"matchedCategories": ["ai_adoption"], "converted": False, "outreachHappened": True,
                        "proposalCreated": False, "lastSeen": "2020-01-01"},
        }}
        multiplier = de.category_conversion_multiplier("ai_adoption", profiles, CONFIG)
        self.assertLess(multiplier, 1.0)

    def test_multiplier_never_goes_below_floor(self):
        organisations = {
            f"Stale{i}": {"matchedCategories": ["ai_adoption"], "converted": False, "outreachHappened": True,
                          "proposalCreated": False, "lastSeen": "2020-01-01"}
            for i in range(20)
        }
        profiles = {"organisations": organisations}
        multiplier = de.category_conversion_multiplier("ai_adoption", profiles, CONFIG)
        self.assertGreaterEqual(multiplier, 0.7)


class ScopedEngagementConsistencyTests(unittest.TestCase):
    """Regression coverage for a real bug this suite caught: an earlier
    version derived scopedEngagement from this module's own
    buying-readiness band independently of ingest.py's real
    compute_priority_score() threshold, so some signals satisfied
    neither classify() branch and silently fell through to the
    "Apply" default meant for plain job postings. scopedEngagement
    must always agree with what ingest.py's own scoring actually
    produces on these same scores."""

    def _classification_for(self, categories, confidence, scale):
        overall = de.compute_overall_demand_score(categories, confidence, CONFIG)
        buying, _ = de.compute_buying_readiness_score(categories, confidence, scale, overall, CONFIG)
        scores = de.opportunity_scores_from_result(overall, buying, categories, scale)
        scoped = de.scoped_engagement_for_scores(scores)
        priority = de.ingest.compute_priority_score(scores)
        return de.ingest.classify(priority, scores, "Technology Practice", scoped, "none")

    def test_never_falls_through_to_apply(self):
        cases = [
            (["regulatory_trigger", "failure_trigger"], "high", None),
            (["ai_adoption"], "high", "40,000 employees"),
            (["ai_adoption"], "medium", None),
            (["funding_trigger"], "medium", None),
            (["governance_trigger"], "high", None),
            (["failure_trigger"], "high", None),
            (["funding_trigger"], "low", None),
        ]
        for categories, confidence, scale in cases:
            with self.subTest(categories=categories, confidence=confidence):
                classification = self._classification_for(categories, confidence, scale)
                self.assertNotEqual(classification, "Apply",
                                    f"{categories}/{confidence} fell through to the job-posting default")


class ProcessSignalIntegrationTests(unittest.TestCase):
    def test_full_pipeline_updates_profile_and_returns_expected_shape(self):
        profiles = de.DEFAULT_PROFILES.copy()
        profiles["organisations"] = {}
        result = de.process_signal(
            organisation="Acme Corp",
            category_keys=["ai_adoption"],
            confidence="high",
            event_summary="Acme Corp deployed Microsoft Copilot to 25,000 employees",
            industry="Retail",
            scale_text="25,000 employees",
            source_url="https://example.com/article",
            config=CONFIG,
            profiles=profiles,
        )
        self.assertIn("overallDemandScore", result)
        self.assertIn("buyingReadinessScore", result)
        self.assertIn("recommendedServices", result)
        self.assertIn("recommendedAction", result)
        self.assertIn("opportunityNarrative", result)
        self.assertIn("scores", result)
        self.assertIn("scopedEngagement", result)
        for field in de.ingest.SCORE_FIELDS:
            self.assertIn(field, result["scores"])

        org = profiles["organisations"]["Acme Corp"]
        self.assertEqual(len(org["signals"]), 1)
        self.assertEqual(org["matchedCategories"], ["ai_adoption"])
        self.assertEqual(org["industry"], "Retail")

    def test_second_signal_for_same_organisation_accumulates_history(self):
        profiles = {"organisations": {}}
        de.process_signal("Acme Corp", ["ai_adoption"], "high", "first event", None, None,
                           "https://example.com/1", CONFIG, profiles)
        de.process_signal("Acme Corp", ["governance_trigger"], "high", "second event", None, None,
                           "https://example.com/2", CONFIG, profiles)
        org = profiles["organisations"]["Acme Corp"]
        self.assertEqual(len(org["signals"]), 2)
        self.assertIn("ai_adoption", org["matchedCategories"])
        self.assertIn("governance_trigger", org["matchedCategories"])


if __name__ == "__main__":
    unittest.main()
