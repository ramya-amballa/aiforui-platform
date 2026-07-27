#!/usr/bin/env python3
"""Tests for Fractional Advisory Radar (AOS Sprint 11).

Run with:
    python3 -m unittest tests.test_fractional_advisory_radar_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import fractional_advisory_radar_engine as engine  # noqa: E402
import generate  # noqa: E402

DEMAND_CATEGORIES_CONFIG = {
    "categories": {
        "ai_adoption": {"label": "AI Adoption", "baseScore": 70},
        "governance_trigger": {"label": "Governance Trigger", "baseScore": 85},
        "funding_trigger": {"label": "Funding Trigger", "baseScore": 75},
        "regulatory_trigger": {"label": "Regulatory Trigger", "baseScore": 95},
        "failure_trigger": {"label": "Failure Trigger", "baseScore": 100},
    }
}
CONFIG = engine.load_json(engine.CONFIG_PATH, {})


def make_profile(**overrides):
    base = {
        "organisation": "BBVA", "matchedCategories": ["ai_adoption"],
        "buyingReadinessScore": 50, "buyingReadinessBand": "Medium",
        "scale": "500 employees", "industry": "Financial Services", "lastSeen": "2026-07-27",
    }
    base.update(overrides)
    return base


class ClassifyStageTests(unittest.TestCase):
    def test_failure_trigger_is_urgent(self):
        profile = make_profile(matchedCategories=["failure_trigger"])
        self.assertEqual(engine.classify_stage(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Urgent")

    def test_regulatory_trigger_is_enterprise(self):
        profile = make_profile(matchedCategories=["regulatory_trigger"])
        self.assertEqual(engine.classify_stage(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Enterprise")

    def test_governance_trigger_is_enterprise(self):
        profile = make_profile(matchedCategories=["governance_trigger"])
        self.assertEqual(engine.classify_stage(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Enterprise")

    def test_funding_trigger_is_growing(self):
        profile = make_profile(matchedCategories=["funding_trigger"])
        self.assertEqual(engine.classify_stage(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Growing")

    def test_ai_adoption_alone_is_emerging(self):
        profile = make_profile(matchedCategories=["ai_adoption"], scale="200 employees")
        self.assertEqual(engine.classify_stage(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Emerging")

    def test_large_scale_ai_adoption_upgrades_to_growing(self):
        profile = make_profile(matchedCategories=["ai_adoption"], scale="50,000 employees")
        self.assertEqual(engine.classify_stage(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Growing")

    def test_no_matched_categories_is_emerging(self):
        profile = make_profile(matchedCategories=[])
        self.assertEqual(engine.classify_stage(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Emerging")

    def test_strongest_category_wins_when_multiple_matched(self):
        profile = make_profile(matchedCategories=["ai_adoption", "failure_trigger"])
        self.assertEqual(engine.classify_stage(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Urgent")


class EngagementModelTests(unittest.TestCase):
    def test_all_four_stages_map_to_distinct_models(self):
        models = {engine.recommended_engagement_model(stage, CONFIG) for stage in engine.STAGE_ORDER}
        self.assertEqual(len(models), 4)

    def test_urgent_is_implementation(self):
        self.assertEqual(engine.recommended_engagement_model("Urgent", CONFIG), "Implementation")

    def test_emerging_is_discovery_workshop(self):
        self.assertEqual(engine.recommended_engagement_model("Emerging", CONFIG), "Discovery workshop")


class FractionalAdvisoryPotentialTests(unittest.TestCase):
    def test_higher_stage_and_readiness_scores_higher(self):
        low = engine.fractional_advisory_potential("Emerging", make_profile(buyingReadinessScore=20), CONFIG)
        high = engine.fractional_advisory_potential("Urgent", make_profile(buyingReadinessScore=90), CONFIG)
        self.assertGreater(high, low)

    def test_never_exceeds_bounds(self):
        potential = engine.fractional_advisory_potential("Urgent", make_profile(buyingReadinessScore=100), CONFIG)
        self.assertLessEqual(potential, 100)
        potential = engine.fractional_advisory_potential("Emerging", make_profile(buyingReadinessScore=0), CONFIG)
        self.assertGreaterEqual(potential, 0)


class ExpectedConsultingRevenueTests(unittest.TestCase):
    def test_prefers_real_pipeline_estimate(self):
        pipeline_data = {"pipeline": [{"organisation": "BBVA", "expectedRevenue": "$40,000"}]}
        result = engine.expected_consulting_revenue(make_profile(), "Enterprise", {"opportunities": []}, pipeline_data, CONFIG)
        self.assertIn("Revenue Hunter", result["source"])

    def test_prefers_real_opportunity_record_over_heuristic(self):
        opportunity_schema = {"opportunities": [{"organisation": "BBVA", "scores": {"expectedRevenue": 7}}]}
        result = engine.expected_consulting_revenue(make_profile(), "Enterprise", opportunity_schema, {"pipeline": []}, CONFIG)
        self.assertEqual(result["score"], 7)
        self.assertIn("Real opportunity record", result["source"])

    def test_falls_back_to_stage_heuristic_honestly(self):
        result = engine.expected_consulting_revenue(make_profile(), "Urgent", {"opportunities": []}, {"pipeline": []}, CONFIG)
        self.assertIn("heuristic", result["source"])
        self.assertEqual(result["score"], 9)


class BuildFeedIntegrationTests(unittest.TestCase):
    def test_sorted_by_expected_revenue_descending(self):
        profiles = {"organisations": {
            "Low": make_profile(organisation="Low", matchedCategories=["ai_adoption"], scale=None),
            "High": make_profile(organisation="High", matchedCategories=["failure_trigger"]),
        }}
        feed = engine.build_feed(profiles, DEMAND_CATEGORIES_CONFIG, CONFIG, {"opportunities": []}, {"pipeline": []})
        self.assertEqual(feed["organisations"][0]["organisation"], "High")


class GenerateMainTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)
        (self.tmp_path / "output").mkdir(parents=True, exist_ok=True)

    def _start_patches(self):
        patches = [
            patch("fractional_advisory_radar_engine.PROFILES_PATH", self.tmp_path / "profiles.json"),
            patch("fractional_advisory_radar_engine.OPPORTUNITY_SCHEMA_PATH", self.tmp_path / "opps.json"),
            patch("fractional_advisory_radar_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"),
            patch("fractional_advisory_radar_engine.FEED_PATH", self.tmp_path / "feed.json"),
            patch("fractional_advisory_radar_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_no_qualified_organisations_writes_nothing(self):
        self._start_patches()
        engine.save_json(self.tmp_path / "profiles.json", {"organisations": {}})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        self.assertFalse((self.tmp_path / "feed.json").exists())

    def test_generates_feed_for_qualified_organisation(self):
        self._start_patches()
        engine.save_json(self.tmp_path / "profiles.json", {"organisations": {"BBVA": make_profile()}})
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": []})
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": []})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed = engine.load_json(self.tmp_path / "feed.json", {})
        self.assertEqual(len(feed["organisations"]), 1)


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_repeated_calls_never_share_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.json"
            default = {"organisations": {}}
            first = engine.load_json(missing_path, default)
            first["organisations"]["polluted"] = {"organisation": "polluted"}
            second = engine.load_json(missing_path, default)
            self.assertEqual(second["organisations"], {})


if __name__ == "__main__":
    unittest.main()
