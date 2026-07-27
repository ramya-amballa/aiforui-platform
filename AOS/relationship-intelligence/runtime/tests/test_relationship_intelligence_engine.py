#!/usr/bin/env python3
"""
Unit and integration tests for Relationship Intelligence (AOS Sprint 13).

Every test uses a hand-built fixture profile/config and an explicit
`today` date passed into each function (never real wall-clock time),
plus patches every path generate.py touches so nothing here reads or
writes real AOS data.

Run with:
    python3 -m unittest tests.test_relationship_intelligence_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import relationship_intelligence_engine as engine  # noqa: E402
import generate  # noqa: E402

TODAY = date(2026, 7, 27)

CONFIG = {
    "staleThresholdDays": 45,
    "reconnectThresholdDays": 30,
    "reminderWindowDays": 14,
    "dormancyThresholdDays": 90,
    "healthWeights": {"recency": 0.40, "responseRate": 0.30, "channelDiversity": 0.30},
    "healthBandThresholds": {"strong": 75, "healthy": 50, "cooling": 25},
}


def make_profile(**overrides):
    base = {
        "person": "Jane Doe",
        "company": "Acme Corp",
        "role": "Chief Risk Officer",
        "linkedIn": "https://linkedin.com/in/janedoe",
        "email": "jane@acme.com",
        "meetings": [{"date": "2026-07-10", "summary": "Coffee chat about AI governance."}],
        "calls": [],
        "messages": [{"date": "2026-07-15", "channel": "LinkedIn", "summary": "Follow-up", "responded": True}],
        "conferenceInteractions": [],
        "sharedInterests": ["AI Governance"],
        "productsDiscussed": ["ADGL Methodology"],
        "resourcesShared": [],
        "birthday": None,
        "workAnniversary": None,
        "upcomingConference": None,
    }
    base.update(overrides)
    return base


class LastInteractionTests(unittest.TestCase):
    def test_finds_most_recent_across_all_channels(self):
        profile = make_profile(
            meetings=[{"date": "2026-01-01", "summary": "x"}],
            calls=[{"date": "2026-07-20", "summary": "x"}],
            messages=[{"date": "2026-06-01", "channel": "email", "summary": "x", "responded": False}],
        )
        self.assertEqual(engine.last_interaction(profile), "2026-07-20")

    def test_none_when_no_interactions(self):
        profile = make_profile(meetings=[], calls=[], messages=[], conferenceInteractions=[])
        self.assertIsNone(engine.last_interaction(profile))


class HealthScoreTests(unittest.TestCase):
    def test_recent_diverse_responded_relationship_scores_high(self):
        profile = make_profile(
            meetings=[{"date": "2026-07-20", "summary": "x"}],
            calls=[{"date": "2026-07-22", "summary": "x"}],
            messages=[{"date": "2026-07-25", "channel": "email", "summary": "x", "responded": True}],
            conferenceInteractions=[{"date": "2026-07-01", "conference": "AI Summit", "summary": "x"}],
        )
        score = engine.relationship_health_score(profile, CONFIG, today=TODAY)
        self.assertGreaterEqual(score, 90)

    def test_stale_unresponded_single_channel_scores_low(self):
        profile = make_profile(
            meetings=[{"date": "2025-01-01", "summary": "x"}],
            calls=[], conferenceInteractions=[],
            messages=[{"date": "2025-01-02", "channel": "email", "summary": "x", "responded": False}],
        )
        score = engine.relationship_health_score(profile, CONFIG, today=TODAY)
        self.assertLess(score, 30)

    def test_no_messages_is_neutral_not_penalised(self):
        profile = make_profile(messages=[])
        score_no_messages = engine.relationship_health_score(profile, CONFIG, today=TODAY)
        profile_bad_messages = make_profile(
            messages=[{"date": "2026-07-15", "channel": "email", "summary": "x", "responded": False}]
        )
        score_bad_messages = engine.relationship_health_score(profile_bad_messages, CONFIG, today=TODAY)
        self.assertGreater(score_no_messages, score_bad_messages)


class HealthBandTests(unittest.TestCase):
    """Design-smell guard: every band in the vocabulary must be reachable."""

    def test_new_for_zero_interactions(self):
        profile = make_profile(meetings=[], calls=[], messages=[], conferenceInteractions=[])
        score = engine.relationship_health_score(profile, CONFIG, today=TODAY)
        self.assertEqual(engine.relationship_health_band(profile, score, CONFIG), "New")

    def test_strong_for_recent_diverse_engaged_relationship(self):
        profile = make_profile(
            meetings=[{"date": "2026-07-20", "summary": "x"}],
            calls=[{"date": "2026-07-22", "summary": "x"}],
            messages=[{"date": "2026-07-25", "channel": "email", "summary": "x", "responded": True}],
            conferenceInteractions=[{"date": "2026-07-01", "conference": "AI Summit", "summary": "x"}],
        )
        score = engine.relationship_health_score(profile, CONFIG, today=TODAY)
        self.assertEqual(engine.relationship_health_band(profile, score, CONFIG), "Strong")

    def test_at_risk_for_very_stale_single_touch(self):
        profile = make_profile(meetings=[{"date": "2024-01-01", "summary": "x"}], calls=[], messages=[])
        score = engine.relationship_health_score(profile, CONFIG, today=TODAY)
        self.assertEqual(engine.relationship_health_band(profile, score, CONFIG), "At Risk")

    def test_healthy_and_cooling_bands_are_reachable(self):
        # healthy: recent-ish but single channel, no message signal
        healthy_profile = make_profile(meetings=[{"date": "2026-07-01", "summary": "x"}], calls=[], messages=[])
        healthy_score = engine.relationship_health_score(healthy_profile, CONFIG, today=TODAY)
        self.assertEqual(engine.relationship_health_band(healthy_profile, healthy_score, CONFIG), "Healthy")

        # cooling: moderately stale, single channel, unresponded message
        cooling_profile = make_profile(
            meetings=[{"date": "2026-04-01", "summary": "x"}], calls=[],
            messages=[{"date": "2026-04-01", "channel": "email", "summary": "x", "responded": False}],
        )
        cooling_score = engine.relationship_health_score(cooling_profile, CONFIG, today=TODAY)
        self.assertEqual(engine.relationship_health_band(cooling_profile, cooling_score, CONFIG), "Cooling")


class RiskTests(unittest.TestCase):
    def test_every_risk_value_is_reachable(self):
        self.assertEqual(engine.relationship_risk("New", False), "Not enough data yet")
        self.assertEqual(engine.relationship_risk("At Risk", False), "High")
        self.assertEqual(engine.relationship_risk("Healthy", True), "High")  # dormant overrides
        self.assertEqual(engine.relationship_risk("Cooling", False), "Medium")
        self.assertEqual(engine.relationship_risk("Strong", False), "Low")


class OpportunityTests(unittest.TestCase):
    def test_high_buying_readiness_flags_high_opportunity(self):
        profile = make_profile(company="BBVA")
        org_profiles = {"BBVA": {"buyingReadinessBand": "High"}}
        result = engine.relationship_opportunity(profile, {}, org_profiles)
        self.assertIn("High", result)
        self.assertIn("BBVA", result)

    def test_existing_crm_relationship_flags_medium_opportunity(self):
        profile = make_profile(company="Acme Corp")
        crm_by_company = {"Acme Corp": {"existingRelationship": "prior conversation"}}
        result = engine.relationship_opportunity(profile, crm_by_company, {})
        self.assertIn("Medium", result)

    def test_no_signal_is_honest(self):
        profile = make_profile(company="Nobody Inc")
        result = engine.relationship_opportunity(profile, {}, {})
        self.assertIn("Not enough signal yet", result)


class ReconnectRecommendationTests(unittest.TestCase):
    def test_recommends_reconnect_past_threshold(self):
        profile = make_profile(meetings=[{"date": "2026-06-01", "summary": "x"}], calls=[], messages=[])
        recommended, reason = engine.reconnect_recommendation(profile, CONFIG, today=TODAY)
        self.assertTrue(recommended)
        self.assertIn("Jane Doe", reason)

    def test_no_recommendation_when_recent(self):
        profile = make_profile(meetings=[{"date": "2026-07-25", "summary": "x"}], calls=[], messages=[])
        recommended, reason = engine.reconnect_recommendation(profile, CONFIG, today=TODAY)
        self.assertFalse(recommended)

    def test_no_recommendation_when_never_interacted(self):
        profile = make_profile(meetings=[], calls=[], messages=[], conferenceInteractions=[])
        recommended, reason = engine.reconnect_recommendation(profile, CONFIG, today=TODAY)
        self.assertFalse(recommended)


class ReminderTests(unittest.TestCase):
    def test_birthday_within_window_is_due(self):
        profile = make_profile(birthday="08-05")  # 9 days after 2026-07-27
        due, occurrence = engine.birthday_reminder(profile, CONFIG, today=TODAY)
        self.assertTrue(due)
        self.assertEqual(occurrence, date(2026, 8, 5))

    def test_birthday_outside_window_is_not_due(self):
        profile = make_profile(birthday="12-25")
        due, _ = engine.birthday_reminder(profile, CONFIG, today=TODAY)
        self.assertFalse(due)

    def test_birthday_wraps_to_next_year(self):
        profile = make_profile(birthday="01-02")
        due, occurrence = engine.birthday_reminder(profile, CONFIG, today=TODAY)
        self.assertFalse(due)
        self.assertEqual(occurrence.year, 2027)

    def test_missing_birthday_is_honestly_not_due(self):
        profile = make_profile(birthday=None)
        due, occurrence = engine.birthday_reminder(profile, CONFIG, today=TODAY)
        self.assertFalse(due)
        self.assertIsNone(occurrence)

    def test_work_anniversary_within_window(self):
        profile = make_profile(workAnniversary="08-01")
        due, _ = engine.work_anniversary_reminder(profile, CONFIG, today=TODAY)
        self.assertTrue(due)

    def test_conference_reminder_within_window(self):
        profile = make_profile(upcomingConference={"name": "AI Governance Summit", "date": "2026-08-03"})
        due, name, target = engine.conference_reminder(profile, CONFIG, today=TODAY)
        self.assertTrue(due)
        self.assertEqual(name, "AI Governance Summit")
        self.assertEqual(target, date(2026, 8, 3))

    def test_conference_reminder_missing_is_honestly_not_due(self):
        profile = make_profile(upcomingConference=None)
        due, name, target = engine.conference_reminder(profile, CONFIG, today=TODAY)
        self.assertFalse(due)
        self.assertIsNone(name)
        self.assertIsNone(target)


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_default_is_deep_copied_not_shared(self):
        first = engine.load_json(Path("/nonexistent/path.json"), {"people": {}})
        first["people"]["X"] = {"person": "X"}
        second = engine.load_json(Path("/nonexistent/path.json"), {"people": {}})
        self.assertEqual(second["people"], {})


class BuildFeedTests(unittest.TestCase):
    def test_feed_lists_are_populated_from_real_profiles(self):
        profiles = {"people": {
            "Jane Doe": make_profile(
                meetings=[{"date": "2026-05-01", "summary": "x"}], calls=[], messages=[],
                company="BBVA",
            ),
        }}
        org_profiles = {"organisations": {"BBVA": {"buyingReadinessBand": "High"}}}
        feed = engine.build_feed(profiles, CONFIG, {"companies": []}, org_profiles, today=TODAY)
        self.assertEqual(len(feed["people"]), 1)
        self.assertIn("Jane Doe", feed["reconnectRecommendations"])
        self.assertIn("High", feed["people"][0]["opportunity"])

    def test_empty_profiles_produce_empty_honest_feed(self):
        feed = engine.build_feed({"people": {}}, CONFIG, {"companies": []}, {"organisations": {}}, today=TODAY)
        self.assertEqual(feed["people"], [])
        self.assertEqual(feed["reconnectRecommendations"], [])


class GenerateEndToEndTests(unittest.TestCase):
    """Runs the real generate.main() over a sample profile with every
    path mocked, confirming a real feed file is written — never
    fabricated when the record is genuinely empty."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)

        patches = [
            patch("relationship_intelligence_engine.PROFILES_PATH", self.tmp_path / "relationship-profiles.json"),
            patch("relationship_intelligence_engine.CRM_PATH", self.tmp_path / "company-intelligence.json"),
            patch("relationship_intelligence_engine.ORGANISATION_PROFILES_PATH", self.tmp_path / "organisation-profiles.json"),
            patch("relationship_intelligence_engine.FEED_PATH", self.tmp_path / "output" / "relationship-intelligence-feed.json"),
            patch("relationship_intelligence_engine.RUNTIME_DIR", self.tmp_path),
            patch("relationship_intelligence_engine.REPO_ROOT", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_no_profiles_writes_nothing(self):
        engine.save_json(self.tmp_path / "relationship-profiles.json", {"people": {}})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        self.assertFalse((self.tmp_path / "output" / "relationship-intelligence-feed.json").exists())

    def test_real_profile_produces_real_feed(self):
        engine.save_json(self.tmp_path / "relationship-profiles.json", {"people": {"Jane Doe": make_profile()}})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed_path = self.tmp_path / "output" / "relationship-intelligence-feed.json"
        self.assertTrue(feed_path.exists())
        feed = engine.load_json(feed_path)
        self.assertEqual(len(feed["people"]), 1)
        self.assertEqual(feed["people"][0]["person"], "Jane Doe")


if __name__ == "__main__":
    unittest.main()
