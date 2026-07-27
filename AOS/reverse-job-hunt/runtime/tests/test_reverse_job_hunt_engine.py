#!/usr/bin/env python3
"""
Unit and integration tests for Reverse Job Hunt (AOS Sprint 9): each
section builder in reverse_job_hunt_engine.py, plus generate.py's
end-to-end run over a sample organisation profile.

Every test uses a hand-built fixture profile/config, never real AOS
data, and patches every path account_intelligence_engine.py or
generate.py touches so nothing here reads or writes real AOS files.

Run with:
    python3 -m unittest tests.test_reverse_job_hunt_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import reverse_job_hunt_engine as engine  # noqa: E402
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
        "organisation": "BBVA",
        "signals": [
            {"date": "2026-07-20", "category": "ai_adoption", "categoryLabel": "AI Adoption", "baseScore": 70,
             "confidence": "high", "eventSummary": "BBVA rolled out Microsoft Copilot to 40,000 employees.",
             "sourceUrl": "https://example.com/1"},
        ],
        "overallDemandScore": 70, "matchedCategories": ["ai_adoption"],
        "buyingReadinessScore": 58, "buyingReadinessBand": "Medium",
        "recommendedServices": ["AI Deployment Governance (ADGL)"],
        "recommendedAction": "Prepare Insight Article", "recommendedActionReason": "test",
        "opportunityNarrative": "test narrative",
        "industry": "Financial Services", "scale": "40,000 employees", "region": "Europe",
        "firstSeen": "2026-07-20", "lastSeen": "2026-07-20",
        "outreachHappened": False, "proposalCreated": False, "converted": False, "revenueGenerated": None,
    }
    base.update(overrides)
    return base


class PursuitReasonsTests(unittest.TestCase):
    def test_returns_reasons_for_matched_categories(self):
        profile = make_profile(matchedCategories=["ai_adoption", "governance_trigger"])
        reasons = engine.pursuit_reasons(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(len(reasons), 2)

    def test_no_matched_categories_is_honest(self):
        profile = make_profile(matchedCategories=[])
        reasons = engine.pursuit_reasons(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertIn("Not enough public signal", reasons[0])


class ConsultingPotentialTests(unittest.TestCase):
    def test_uses_real_pipeline_estimate_when_present(self):
        profile = make_profile()
        pipeline_data = {"pipeline": [{"organisation": "BBVA", "expectedRevenue": "$50,000"}]}
        result = engine.consulting_potential(profile, {"opportunities": []}, pipeline_data, CONFIG)
        self.assertIn("Revenue Hunter", result["source"])
        self.assertEqual(result["estimate"], "$50,000")

    def test_uses_real_opportunity_record_when_no_pipeline_estimate(self):
        profile = make_profile()
        opportunity_schema = {"opportunities": [{"organisation": "BBVA", "scores": {"expectedRevenue": 8}}]}
        result = engine.consulting_potential(profile, opportunity_schema, {"pipeline": []}, CONFIG)
        self.assertIn("Real opportunity record", result["source"])
        self.assertEqual(result["score"], 8)

    def test_falls_back_to_scale_heuristic(self):
        profile = make_profile(scale="40,000 employees")
        result = engine.consulting_potential(profile, {"opportunities": []}, {"pipeline": []}, CONFIG)
        self.assertEqual(result["score"], 10)
        self.assertIn("Scale heuristic", result["source"])

    def test_unclear_scale_is_honest(self):
        profile = make_profile(scale=None)
        result = engine.consulting_potential(profile, {"opportunities": []}, {"pipeline": []}, CONFIG)
        self.assertIn("Unclear", result["estimate"])


class RelevanceReasonsTests(unittest.TestCase):
    def test_returns_relevance_for_matched_categories(self):
        profile = make_profile(matchedCategories=["regulatory_trigger"])
        reasons = engine.relevance_reasons(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertTrue(any("Third-Party Risk Review" in r or "Policy & Control" in r for r in reasons))


class MaturityTests(unittest.TestCase):
    def test_ai_maturity_uses_strongest_matched_category(self):
        profile = make_profile(matchedCategories=["ai_adoption", "governance_trigger"])
        self.assertEqual(engine.ai_maturity(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Governance-formalising")

    def test_governance_maturity_is_a_distinct_dimension(self):
        profile = make_profile(matchedCategories=["ai_adoption"])
        ai_mat = engine.ai_maturity(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        gov_mat = engine.governance_maturity(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertNotEqual(ai_mat, gov_mat)

    def test_no_signal_is_honest(self):
        profile = make_profile(matchedCategories=[])
        self.assertEqual(engine.ai_maturity(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Not enough signal to assess")
        self.assertEqual(engine.governance_maturity(profile, DEMAND_CATEGORIES_CONFIG, CONFIG), "Not enough signal to assess")


class EntryPointTests(unittest.TestCase):
    """All six vocabulary values must be genuinely reachable — the same
    design-smell guard used for Account Intelligence's Outreach
    Strategy in Sprint 8."""

    def test_existing_crm_relationship_always_wins(self):
        profile = make_profile(buyingReadinessBand="Low")
        crm_entry = {"companyName": "BBVA", "existingRelationship": "prior client"}
        value, _ = engine.entry_point(profile, crm_entry, CONFIG)
        self.assertEqual(value, "Warm introduction")

    def test_low_confidence_is_linkedin_relationship(self):
        profile = make_profile(buyingReadinessBand="Very High",
                                signals=[dict(make_profile()["signals"][0], confidence="low")])
        value, _ = engine.entry_point(profile, None, CONFIG)
        self.assertEqual(value, "LinkedIn relationship")

    def test_very_high_band_with_urgent_category_is_fractional_advisory(self):
        profile = make_profile(buyingReadinessBand="Very High", matchedCategories=["failure_trigger"])
        value, _ = engine.entry_point(profile, None, CONFIG)
        self.assertEqual(value, "Fractional advisory")

    def test_high_band_is_discovery_workshop(self):
        profile = make_profile(buyingReadinessBand="High", matchedCategories=["ai_adoption"])
        value, _ = engine.entry_point(profile, None, CONFIG)
        self.assertEqual(value, "Discovery workshop")

    def test_medium_band_high_confidence_is_executive_briefing(self):
        profile = make_profile(buyingReadinessBand="Medium",
                                signals=[dict(make_profile()["signals"][0], confidence="high")])
        value, _ = engine.entry_point(profile, None, CONFIG)
        self.assertEqual(value, "Executive briefing")

    def test_medium_band_medium_confidence_is_conference(self):
        profile = make_profile(buyingReadinessBand="Medium",
                                signals=[dict(make_profile()["signals"][0], confidence="medium")])
        value, _ = engine.entry_point(profile, None, CONFIG)
        self.assertEqual(value, "Conference")

    def test_low_band_is_linkedin_relationship(self):
        profile = make_profile(buyingReadinessBand="Low",
                                signals=[dict(make_profile()["signals"][0], confidence="medium")])
        value, _ = engine.entry_point(profile, None, CONFIG)
        self.assertEqual(value, "LinkedIn relationship")


class ProbabilityOfEngagementTests(unittest.TestCase):
    def test_reuses_buying_readiness_score_verbatim(self):
        profile = make_profile(buyingReadinessScore=64)
        self.assertEqual(engine.probability_of_engagement(profile), 64)


class RecommendedTimelineTests(unittest.TestCase):
    def test_maps_band_to_timeline(self):
        profile = make_profile(buyingReadinessBand="Very High")
        self.assertIn("Immediate", engine.recommended_timeline(profile, CONFIG))


class FirstTouchTests(unittest.TestCase):
    def test_parameterises_organisation_and_category(self):
        profile = make_profile(matchedCategories=["governance_trigger"])
        touch = engine.first_touch(profile, "Executive briefing", DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertIn("BBVA", touch)
        self.assertIn("Governance Trigger", touch)

    def test_never_a_sales_pitch(self):
        profile = make_profile()
        for entry_point_value in CONFIG.get("entryPoint", {}).get("options", []):
            touch = engine.first_touch(profile, entry_point_value, DEMAND_CATEGORIES_CONFIG, CONFIG)
            self.assertNotIn("Buy now", touch)


class NinetyDaySequenceTests(unittest.TestCase):
    def test_returns_three_phases_for_every_entry_point(self):
        for entry_point_value in CONFIG.get("entryPoint", {}).get("options", []):
            sequence = engine.ninety_day_sequence(entry_point_value, CONFIG)
            self.assertEqual(len(sequence), 3, f"{entry_point_value} did not return 3 phases")
            self.assertTrue(sequence[0].startswith("Days 1-30"))
            self.assertTrue(sequence[1].startswith("Days 31-60"))
            self.assertTrue(sequence[2].startswith("Days 61-90"))


class ExpectedConsultingRoiTests(unittest.TestCase):
    def test_computes_expected_value(self):
        self.assertEqual(engine.expected_consulting_roi(10, 78), 7.8)

    def test_none_score_is_honest_not_zero(self):
        self.assertIsNone(engine.expected_consulting_roi(None, 78))


class BuildStrategyIntegrationTests(unittest.TestCase):
    def test_produces_all_ten_sections(self):
        profile = make_profile()
        markdown, feed_entry = engine.build_strategy(
            profile, {"opportunities": []}, {"pipeline": []}, {"companies": []}, {"briefs": []},
            DEMAND_CATEGORIES_CONFIG, CONFIG)
        for i in range(1, 11):
            self.assertIn(f"## {i}.", markdown)
        self.assertEqual(feed_entry["organisation"], "BBVA")
        self.assertIsNone(feed_entry["strategyPath"])  # generate.py fills this in

    def test_cross_references_account_intelligence_when_available(self):
        profile = make_profile()
        ai_feed = {"briefs": [{"organisation": "BBVA", "outreachStrategy": "Thought leadership"}]}
        markdown, _ = engine.build_strategy(
            profile, {"opportunities": []}, {"pipeline": []}, {"companies": []}, ai_feed,
            DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertIn("Thought leadership", markdown)

    def test_no_account_intelligence_entry_is_handled_honestly(self):
        profile = make_profile()
        markdown, _ = engine.build_strategy(
            profile, {"opportunities": []}, {"pipeline": []}, {"companies": []}, {"briefs": []},
            DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertNotIn("Cross-reference", markdown)

    def test_client_acquisition_campaign_section_present(self):
        profile = make_profile()
        markdown, feed_entry = engine.build_strategy(
            profile, {"opportunities": []}, {"pipeline": []}, {"companies": []}, {"briefs": []},
            DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertIn("## 11. Client Acquisition Campaign", markdown)
        self.assertEqual(feed_entry["campaignStatus"], "Not started")
        self.assertEqual(feed_entry["touchpointCount"], 0)
        self.assertIsNone(feed_entry["assetToShareFirst"])

    def test_client_acquisition_uses_real_relationship_contact_and_touchpoints(self):
        profile = make_profile()
        ai_feed = {"briefs": [{"organisation": "BBVA", "decisionMakerTitles": ["Chief Risk Officer"],
                                "supportingAssets": [{"title": "ADGL Methodology", "type": "Methodology", "url": "/resources/adgl"}]}]}
        relationship_profiles = {"people": {"Jane Doe": {"person": "Jane Doe", "company": "BBVA", "role": "CRO"}}}
        touchpoint_log = {"campaigns": {"BBVA": {"status": "Open", "touchpoints": [
            {"date": "2026-07-01", "channel": "LinkedIn", "summary": "Sent connection request"},
        ]}}}
        markdown, feed_entry = engine.build_strategy(
            profile, {"opportunities": []}, {"pipeline": []}, {"companies": []}, ai_feed,
            DEMAND_CATEGORIES_CONFIG, CONFIG, relationship_profiles, touchpoint_log)
        self.assertIn("Jane Doe", markdown)
        self.assertIn("ADGL Methodology", markdown)
        self.assertIn("Sent connection request", markdown)
        self.assertEqual(feed_entry["campaignStatus"], "Open")
        self.assertEqual(feed_entry["touchpointCount"], 1)
        self.assertEqual(feed_entry["assetToShareFirst"], "ADGL Methodology")


class ClientAcquisitionEngineTests(unittest.TestCase):
    """AOS Sprint 16 — Client Acquisition Engine, consolidated into
    Reverse Job Hunt per explicit instruction rather than a new
    standalone employee."""

    def test_crm_path_points_to_the_real_crm_directory(self):
        # Regression: this constant once pointed to a nonexistent
        # AOS/crm/ directory (the same wrong-directory bug already
        # caught once in recruiter_intelligence_engine.py), silently
        # making every CRM cross-reference (entry_point's relationship
        # check included) see an empty default forever.
        self.assertEqual(engine.CRM_PATH.parts[-2:], ("06-CRM", "company-intelligence.json"))

    def test_linkedin_request_uses_real_tracked_contact_when_available(self):
        contact = {"person": "Jane Doe", "company": "BBVA", "role": "Chief Risk Officer"}
        result = engine.linkedin_connection_request("BBVA", ["Chief Risk Officer"], contact)
        self.assertIn("Jane Doe", result)
        self.assertIn("Chief Risk Officer", result)

    def test_linkedin_request_falls_back_to_title_when_no_contact_tracked(self):
        result = engine.linkedin_connection_request("BBVA", ["Chief Risk Officer"], None)
        self.assertIn("Chief Risk Officer", result)
        self.assertNotIn("Jane Doe", result)

    def test_linkedin_request_is_honest_when_nothing_available(self):
        result = engine.linkedin_connection_request("BBVA", [], None)
        self.assertIn("Not enough signal", result)

    def test_follow_up_message_ties_to_first_sequence_step(self):
        result = engine.follow_up_message("BBVA", ["Send a LinkedIn connection request", "Share ADGL resource"])
        self.assertIn("Send a LinkedIn connection request", result)

    def test_follow_up_message_honest_when_no_sequence(self):
        result = engine.follow_up_message("BBVA", [])
        self.assertIn("Not enough signal", result)

    def test_asset_to_share_first_is_top_ranked_asset(self):
        ai_feed_entry = {"supportingAssets": [{"title": "ADGL Methodology", "type": "Methodology", "url": "/x"},
                                                {"title": "Whitepaper", "type": "Whitepaper", "url": "/y"}]}
        result = engine.asset_to_share_first(ai_feed_entry)
        self.assertEqual(result["title"], "ADGL Methodology")

    def test_asset_to_share_first_none_when_no_brief(self):
        self.assertIsNone(engine.asset_to_share_first(None))
        self.assertIsNone(engine.asset_to_share_first({"supportingAssets": []}))

    def test_campaign_status_not_started_when_no_record(self):
        result = engine.campaign_status("BBVA", {"campaigns": {}})
        self.assertEqual(result["status"], "Not started")
        self.assertEqual(result["touchpoints"], [])

    def test_campaign_status_reflects_real_touchpoint_log(self):
        touchpoint_log = {"campaigns": {"BBVA": {"status": "Won", "touchpoints": [
            {"date": "2026-07-01", "channel": "Email", "summary": "Sent proposal"},
        ]}}}
        result = engine.campaign_status("BBVA", touchpoint_log)
        self.assertEqual(result["status"], "Won")
        self.assertEqual(len(result["touchpoints"]), 1)

    def test_find_relationship_contact_matches_by_company(self):
        profiles = {"people": {"Jane Doe": {"person": "Jane Doe", "company": "BBVA"},
                                 "John Roe": {"person": "John Roe", "company": "Acme"}}}
        found = engine._find_relationship_contact("BBVA", profiles)
        self.assertEqual(found["person"], "Jane Doe")
        self.assertIsNone(engine._find_relationship_contact("Nonexistent Co", profiles))


class GenerateMainTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)
        (self.tmp_path / "output").mkdir(parents=True, exist_ok=True)

    def _patches(self):
        return [
            patch("reverse_job_hunt_engine.PROFILES_PATH", self.tmp_path / "profiles.json"),
            patch("reverse_job_hunt_engine.OPPORTUNITY_SCHEMA_PATH", self.tmp_path / "opps.json"),
            patch("reverse_job_hunt_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"),
            patch("reverse_job_hunt_engine.CRM_PATH", self.tmp_path / "crm.json"),
            patch("reverse_job_hunt_engine.ACCOUNT_INTELLIGENCE_FEED_PATH", self.tmp_path / "ai_feed.json"),
            patch("reverse_job_hunt_engine.RELATIONSHIP_PROFILES_PATH", self.tmp_path / "relationship_profiles.json"),
            patch("reverse_job_hunt_engine.TOUCHPOINT_LOG_PATH", self.tmp_path / "touchpoint_log.json"),
            patch("reverse_job_hunt_engine.STRATEGIES_DIR", self.tmp_path / "strategies"),
            patch("reverse_job_hunt_engine.FEED_PATH", self.tmp_path / "feed.json"),
            patch("reverse_job_hunt_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]

    def _start_patches(self):
        patches = self._patches()
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_no_qualified_organisations_writes_nothing(self):
        self._start_patches()
        engine.save_json(self.tmp_path / "profiles.json", {"organisations": {}})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        self.assertFalse((self.tmp_path / "feed.json").exists())

    def test_generates_a_strategy_file_and_feed_entry(self):
        self._start_patches()
        engine.save_json(self.tmp_path / "profiles.json", {"organisations": {"BBVA": make_profile()}})
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": []})
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": []})
        engine.save_json(self.tmp_path / "crm.json", {"companies": []})
        engine.save_json(self.tmp_path / "ai_feed.json", {"briefs": []})

        exit_code = generate.main()
        self.assertEqual(exit_code, 0)

        feed = engine.load_json(self.tmp_path / "feed.json", {})
        self.assertEqual(len(feed["strategies"]), 1)
        entry = feed["strategies"][0]
        self.assertEqual(entry["organisation"], "BBVA")
        strategy_path = self.tmp_path / entry["strategyPath"]
        self.assertTrue(strategy_path.exists())
        self.assertIn("Reverse Job Hunt Strategy — BBVA", strategy_path.read_text(encoding="utf-8"))

    def test_report_ranks_by_expected_roi_descending(self):
        self._start_patches()
        low_roi_profile = make_profile(organisation="LowROI", buyingReadinessScore=20, buyingReadinessBand="Low", scale=None)
        high_roi_profile = make_profile(organisation="HighROI", buyingReadinessScore=90, buyingReadinessBand="Very High",
                                         scale="50,000 employees", matchedCategories=["failure_trigger"])
        engine.save_json(self.tmp_path / "profiles.json", {"organisations": {
            "LowROI": low_roi_profile, "HighROI": high_roi_profile,
        }})
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": []})
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": []})
        engine.save_json(self.tmp_path / "crm.json", {"companies": []})
        engine.save_json(self.tmp_path / "ai_feed.json", {"briefs": []})

        generate.main()
        report_files = list((self.tmp_path / "output").glob("*-reverse-job-hunt-report.md"))
        self.assertEqual(len(report_files), 1)
        content = report_files[0].read_text(encoding="utf-8")
        self.assertLess(content.index("HighROI"), content.index("LowROI"))


class SlugifyTests(unittest.TestCase):
    def test_basic_slug(self):
        self.assertEqual(engine.slugify("BBVA S.A."), "bbva-s-a")


class LoadJsonMutableDefaultTests(unittest.TestCase):
    """Regression test mirroring the real bug found in sales-director's
    prepare.py: a shared mutable default dict returned by reference lets
    one call's in-place mutation leak into the next call in the same
    process. reverse_job_hunt_engine.load_json() must deep-copy."""

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
