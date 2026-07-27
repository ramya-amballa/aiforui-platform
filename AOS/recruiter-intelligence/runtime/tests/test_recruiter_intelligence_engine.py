#!/usr/bin/env python3
"""
Tests for Recruiter Intelligence (AOS Sprint 10): profile building from
real opportunity/CRM data, the four generated views, and generate.py's
end-to-end run.

Run with:
    python3 -m unittest tests.test_recruiter_intelligence_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import recruiter_intelligence_engine as engine  # noqa: E402
import generate  # noqa: E402

CONFIG = engine.load_json(engine.CONFIG_PATH, {})

OPP = {
    "id": "opp-1", "source": "Acme Recruiters", "sourceCategory": "Recruiter Channel",
    "organisation": "BBVA", "title": "AI Governance Lead",
    "domainTags": ["AI Governance", "ADGL"], "location": "Dubai, UAE", "description": "",
}
COMPANY = {
    "companyName": "BBVA", "industry": "Financial Services", "recruiter": "Acme Recruiters",
    "relationshipTemperature": "warm", "lastTouch": "2026-07-20", "nextFollowUpDue": "2026-07-30",
    "existingRelationship": "prior conversation",
    "outreachHistory": [{"date": "2026-07-15", "channel": "email", "summary": "intro"}],
}


class BuildProfileTests(unittest.TestCase):
    def test_derives_specialisation_industries_countries_from_real_data(self):
        profile = engine.build_or_update_profile(
            "Acme Recruiters", [OPP], [COMPANY], {}, CONFIG, None)
        self.assertIn("AI Governance", profile["specialisation"])
        self.assertEqual(profile["industries"], ["Financial Services"])
        self.assertEqual(profile["countries"], ["UAE"])
        self.assertEqual(profile["rolesHired"], ["AI Governance Lead"])

    def test_relationship_strength_reuses_crm_temperature(self):
        profile = engine.build_or_update_profile("Acme Recruiters", [OPP], [COMPANY], {}, CONFIG, None)
        self.assertEqual(profile["relationshipBand"], "Warm")
        self.assertEqual(profile["relationshipStrength"], 65)

    def test_response_rate_from_existing_relationship(self):
        profile = engine.build_or_update_profile("Acme Recruiters", [OPP], [COMPANY], {}, CONFIG, None)
        self.assertEqual(profile["responseRate"], 100)

    def test_no_companies_gives_honest_null_response_rate(self):
        profile = engine.build_or_update_profile("Acme Recruiters", [OPP], [], {}, CONFIG, None)
        self.assertIsNone(profile["responseRate"])

    def test_success_rate_from_won_pipeline_entry(self):
        pipeline_by_org = {"BBVA": {"organisation": "BBVA", "stage": "won"}}
        profile = engine.build_or_update_profile("Acme Recruiters", [OPP], [COMPANY], pipeline_by_org, CONFIG, None)
        self.assertEqual(profile["successRate"], 100)

    def test_no_pipeline_record_gives_honest_null_success_rate(self):
        profile = engine.build_or_update_profile("Acme Recruiters", [OPP], [COMPANY], {}, CONFIG, None)
        self.assertIsNone(profile["successRate"])

    def test_first_seen_preserved_across_updates(self):
        first = engine.build_or_update_profile("Acme Recruiters", [OPP], [COMPANY], {}, CONFIG, None)
        first["firstSeen"] = "2020-01-01"
        second = engine.build_or_update_profile("Acme Recruiters", [OPP], [COMPANY], {}, CONFIG, first)
        self.assertEqual(second["firstSeen"], "2020-01-01")


class DormancyAndFollowUpTests(unittest.TestCase):
    def test_dormant_when_last_interaction_beyond_threshold(self):
        profile = {"lastInteraction": "2020-01-01", "opportunityCount": 1}
        self.assertTrue(engine.is_dormant(profile, CONFIG))

    def test_not_dormant_when_recent(self):
        profile = {"lastInteraction": engine.TODAY, "opportunityCount": 1}
        self.assertFalse(engine.is_dormant(profile, CONFIG))

    def test_known_contact_never_touched_is_dormant(self):
        profile = {"lastInteraction": None, "opportunityCount": 1}
        self.assertTrue(engine.is_dormant(profile, CONFIG))

    def test_due_this_week_within_window(self):
        from datetime import date, timedelta
        profile = {"nextFollowUp": (date.today() + timedelta(days=3)).isoformat()}
        self.assertTrue(engine.is_due_this_week(profile, CONFIG))

    def test_not_due_when_far_in_future(self):
        from datetime import date, timedelta
        profile = {"nextFollowUp": (date.today() + timedelta(days=60)).isoformat()}
        self.assertFalse(engine.is_due_this_week(profile, CONFIG))


class PriorityScoreTests(unittest.TestCase):
    def test_weighted_sum(self):
        profile = {"relationshipStrength": 90, "responseRate": 100, "successRate": 50}
        score = engine.priority_score(profile, CONFIG)
        self.assertEqual(score, round(90 * 0.4 + 100 * 0.3 + 50 * 0.3, 1))

    def test_missing_fields_treated_as_zero_not_guessed(self):
        profile = {"relationshipStrength": 50, "responseRate": None, "successRate": None}
        score = engine.priority_score(profile, CONFIG)
        self.assertEqual(score, round(50 * 0.4, 1))


class HiringDomainFilterTests(unittest.TestCase):
    def test_matches_ai_governance(self):
        profile = {"specialisation": ["AI Governance"]}
        self.assertTrue(engine.matches_hiring_domain(profile, "aiGovernance", CONFIG))

    def test_no_match_when_specialisation_absent(self):
        profile = {"specialisation": ["GRC"]}
        self.assertFalse(engine.matches_hiring_domain(profile, "aiGovernance", CONFIG))


class BuildFeedIntegrationTests(unittest.TestCase):
    def test_feed_contains_all_four_views(self):
        profiles = {"recruiters": {"Acme Recruiters": engine.build_or_update_profile(
            "Acme Recruiters", [OPP], [COMPANY], {}, CONFIG, None)}}
        feed = engine.build_feed(profiles, CONFIG)
        for key in ("weeklyFollowUpList", "dormantRelationships", "priorityRecruiters",
                    "hiringAiGovernance", "hiringGrc", "hiringFractionalConsultants"):
            self.assertIn(key, feed)


class GenerateMainTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)
        (self.tmp_path / "output").mkdir(parents=True, exist_ok=True)

    def _start_patches(self):
        patches = [
            patch("recruiter_intelligence_engine.OPPORTUNITY_SCHEMA_PATH", self.tmp_path / "opps.json"),
            patch("recruiter_intelligence_engine.CRM_PATH", self.tmp_path / "crm.json"),
            patch("recruiter_intelligence_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"),
            patch("recruiter_intelligence_engine.PROFILES_PATH", self.tmp_path / "profiles.json"),
            patch("recruiter_intelligence_engine.FEED_PATH", self.tmp_path / "feed.json"),
            patch("recruiter_intelligence_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_no_data_writes_empty_feed_honestly(self):
        self._start_patches()
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": []})
        engine.save_json(self.tmp_path / "crm.json", {"companies": []})
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": []})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        self.assertFalse((self.tmp_path / "feed.json").exists())

    def test_generates_feed_and_persists_profile(self):
        self._start_patches()
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": [OPP]})
        engine.save_json(self.tmp_path / "crm.json", {"companies": [COMPANY]})
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": [{"organisation": "BBVA", "stage": "won"}]})

        exit_code = generate.main()
        self.assertEqual(exit_code, 0)

        feed = engine.load_json(self.tmp_path / "feed.json", {})
        self.assertEqual(len(feed["contacts"]), 1)
        self.assertEqual(feed["contacts"][0]["recruiter"], "Acme Recruiters")

        profiles = engine.load_json(self.tmp_path / "profiles.json", {})
        self.assertIn("Acme Recruiters", profiles["recruiters"])

    def test_rerun_preserves_first_seen(self):
        self._start_patches()
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": [OPP]})
        engine.save_json(self.tmp_path / "crm.json", {"companies": [COMPANY]})
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": []})

        generate.main()
        profiles = engine.load_json(self.tmp_path / "profiles.json", {})
        first_seen_1 = profiles["recruiters"]["Acme Recruiters"]["firstSeen"]

        generate.main()
        profiles = engine.load_json(self.tmp_path / "profiles.json", {})
        first_seen_2 = profiles["recruiters"]["Acme Recruiters"]["firstSeen"]
        self.assertEqual(first_seen_1, first_seen_2)


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_repeated_calls_never_share_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.json"
            default = {"recruiters": {}}
            first = engine.load_json(missing_path, default)
            first["recruiters"]["polluted"] = {"recruiter": "polluted"}
            second = engine.load_json(missing_path, default)
            self.assertEqual(second["recruiters"], {})


if __name__ == "__main__":
    unittest.main()
