#!/usr/bin/env python3
"""
Unit and integration tests for Capacity Management (AOS Sprint 22).

Every effort figure is checked to come verbatim from rate-card.json's
own typicalDays — never a second, independently-invented estimate —
and every "not estimated" path (an engagement type with no rate-card
entry, an opportunity with no service-mapping recommendation yet) is
checked to stay honestly null rather than default to a guessed number.

Run with:
    python3 -m unittest tests.test_capacity_management_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import capacity_management_engine as engine  # noqa: E402
import generate  # noqa: E402

RATE_CARD = {"types": {
    "Consulting Project": {"dayRate": 850, "typicalDays": {"min": 10, "max": 40}, "unit": "per day"},
    "Enterprise Contract": {"dayRate": 950, "typicalDays": {"min": 30, "max": 120}, "unit": "per day"},
    "Grant": {"note": "Grant-funded; price per the grant's own terms, not a day rate."},
}}


class TypicalDaysForTests(unittest.TestCase):
    def test_returns_real_range_for_known_type(self):
        self.assertEqual(engine.typical_days_for("Consulting Project", RATE_CARD), (10, 40))

    def test_honest_none_when_no_typical_days(self):
        self.assertIsNone(engine.typical_days_for("Grant", RATE_CARD))

    def test_honest_none_for_unknown_type(self):
        self.assertIsNone(engine.typical_days_for("Nonexistent Type", RATE_CARD))


class DeliveryPhaseForTests(unittest.TestCase):
    def test_not_started_when_no_log_entry(self):
        self.assertEqual(engine.delivery_phase_for("BBVA", {"engagements": {}}), "Not started")

    def test_reflects_real_logged_phase(self):
        log = {"engagements": {"BBVA": {"phase": "Discovery", "notes": []}}}
        self.assertEqual(engine.delivery_phase_for("BBVA", log), "Discovery")


class ActiveEngagementLoadTests(unittest.TestCase):
    def test_sums_real_typical_days_for_won_not_closed_engagements(self):
        pipeline_data = {"pipeline": [
            {"organisation": "BBVA", "title": "X", "type": "Consulting Project", "stage": "won"},
            {"organisation": "Acme", "title": "Y", "type": "Enterprise Contract", "stage": "won"},
        ]}
        engagements, min_total, max_total = engine.active_engagement_load(pipeline_data, {"engagements": {}}, RATE_CARD)
        self.assertEqual(len(engagements), 2)
        self.assertEqual(min_total, 40)  # 10 + 30
        self.assertEqual(max_total, 160)  # 40 + 120

    def test_excludes_closed_engagements(self):
        pipeline_data = {"pipeline": [{"organisation": "BBVA", "title": "X", "type": "Consulting Project", "stage": "won"}]}
        delivery_log = {"engagements": {"BBVA": {"phase": "Closed", "notes": []}}}
        engagements, min_total, max_total = engine.active_engagement_load(pipeline_data, delivery_log, RATE_CARD)
        self.assertEqual(engagements, [])
        self.assertEqual(min_total, 0)

    def test_excludes_non_won_stages(self):
        pipeline_data = {"pipeline": [{"organisation": "BBVA", "title": "X", "type": "Consulting Project", "stage": "identified"}]}
        engagements, _, _ = engine.active_engagement_load(pipeline_data, {"engagements": {}}, RATE_CARD)
        self.assertEqual(engagements, [])

    def test_honest_unestimated_when_no_rate_card_entry(self):
        pipeline_data = {"pipeline": [{"organisation": "BBVA", "title": "X", "type": "Grant", "stage": "won"}]}
        engagements, min_total, max_total = engine.active_engagement_load(pipeline_data, {"engagements": {}}, RATE_CARD)
        self.assertIsNone(engagements[0]["estimatedDaysMin"])
        self.assertEqual(min_total, 0)


class IncomingPipelineLoadTests(unittest.TestCase):
    def test_sums_pending_proposals_via_service_mapping(self):
        ceo_feed = {"feed": [
            {"opportunityId": "opp-1", "organisation": "BBVA", "title": "X", "status": "Ready To Send"},
        ]}
        service_recs = {"opp-1": {"recommendedEngagementType": "Consulting Project", "notApplicable": False}}
        pending, min_total, max_total = engine.incoming_pipeline_load(ceo_feed, service_recs, RATE_CARD)
        self.assertEqual(len(pending), 1)
        self.assertEqual((min_total, max_total), (10, 40))

    def test_excludes_non_pending_statuses(self):
        ceo_feed = {"feed": [{"opportunityId": "opp-1", "organisation": "BBVA", "title": "X", "status": "Needs Review"}]}
        pending, _, _ = engine.incoming_pipeline_load(ceo_feed, {}, RATE_CARD)
        self.assertEqual(pending, [])

    def test_honest_unestimated_when_no_service_recommendation_yet(self):
        ceo_feed = {"feed": [{"opportunityId": "opp-1", "organisation": "BBVA", "title": "X", "status": "Proposal Ready"}]}
        pending, min_total, max_total = engine.incoming_pipeline_load(ceo_feed, {}, RATE_CARD)
        self.assertIsNone(pending[0]["estimatedDaysMin"])
        self.assertEqual(min_total, 0)

    def test_not_applicable_recommendation_is_honestly_unestimated(self):
        ceo_feed = {"feed": [{"opportunityId": "opp-1", "organisation": "BBVA", "title": "X", "status": "Proposal Ready"}]}
        service_recs = {"opp-1": {"notApplicable": True}}
        pending, min_total, max_total = engine.incoming_pipeline_load(ceo_feed, service_recs, RATE_CARD)
        self.assertIsNone(pending[0]["estimatedDaysMin"])


class WeeksOfCommittedWorkTests(unittest.TestCase):
    def test_computes_real_ratio(self):
        min_w, max_w = engine.weeks_of_committed_work(20, 40, 4)
        self.assertEqual((min_w, max_w), (5.0, 10.0))

    def test_honest_none_when_no_available_days_configured(self):
        self.assertEqual(engine.weeks_of_committed_work(20, 40, 0), (None, None))


class CapacityStatusTests(unittest.TestCase):
    THRESHOLDS = {"nearCapacity": 6, "overCapacity": 10}

    def test_available_capacity_below_near_threshold(self):
        self.assertEqual(engine.capacity_status(3, self.THRESHOLDS), "Available Capacity")

    def test_near_capacity_at_threshold(self):
        self.assertEqual(engine.capacity_status(6, self.THRESHOLDS), "Near Capacity")

    def test_over_capacity_at_threshold(self):
        self.assertEqual(engine.capacity_status(10, self.THRESHOLDS), "Over Capacity")

    def test_honest_not_enough_signal_when_none(self):
        self.assertEqual(engine.capacity_status(None, self.THRESHOLDS), "Not enough signal yet")


class RenderMarkdownTests(unittest.TestCase):
    def test_honest_empty_states(self):
        markdown = engine.render_capacity_markdown([], 0, 0, [], 0, 0, None, None, "Not enough signal yet", 4)
        self.assertIn("No active engagements on record", markdown)
        self.assertIn("No pending proposals on record", markdown)
        self.assertIn("Not enough signal yet", markdown)

    def test_real_data_appears_verbatim(self):
        active = [{"organisation": "BBVA", "title": "X", "type": "Consulting Project", "phase": "Discovery",
                    "estimatedDaysMin": 10, "estimatedDaysMax": 40}]
        markdown = engine.render_capacity_markdown(active, 10, 40, [], 0, 0, 2.5, 10.0, "Near Capacity", 4)
        self.assertIn("BBVA", markdown)
        self.assertIn("Near Capacity", markdown)
        self.assertIn("2.5-10.0", markdown)


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_default_is_deep_copied_not_shared(self):
        first = engine.load_json(Path("/nonexistent/path.json"), {"pipeline": []})
        first["pipeline"].append({"organisation": "X"})
        second = engine.load_json(Path("/nonexistent/path.json"), {"pipeline": []})
        self.assertEqual(second["pipeline"], [])


class GenerateEndToEndTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)

        patches = [
            patch("capacity_management_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"),
            patch("capacity_management_engine.DELIVERY_LOG_PATH", self.tmp_path / "delivery-log.json"),
            patch("capacity_management_engine.CEO_ADVISOR_FEED_PATH", self.tmp_path / "ceo-advisor-feed.json"),
            patch("capacity_management_engine.SERVICE_RECOMMENDATIONS_PATH", self.tmp_path / "service_recs.json"),
            patch("capacity_management_engine.RATE_CARD_PATH", self.tmp_path / "rate-card.json"),
            patch("capacity_management_engine.CONFIG_PATH", self.tmp_path / "capacity-config.json"),
            patch("capacity_management_engine.FEED_PATH", self.tmp_path / "output" / "capacity-feed.json"),
            patch("capacity_management_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        engine.save_json(self.tmp_path / "rate-card.json", RATE_CARD)

    def test_runs_honestly_empty_when_nothing_exists_yet(self):
        # Zero committed work with a real available-days-per-week config
        # is genuinely "Available Capacity" — not "no signal." "No
        # signal" is reserved for when the ratio itself can't be
        # computed (see test_honest_not_enough_signal_when_config_missing).
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed = engine.load_json(self.tmp_path / "output" / "capacity-feed.json")
        self.assertEqual(feed["activeEngagements"], [])
        self.assertEqual(feed["pendingProposals"], [])
        self.assertEqual(feed["capacityStatus"], "Available Capacity")

    def test_honest_not_enough_signal_when_config_missing(self):
        engine.save_json(self.tmp_path / "capacity-config.json", {"foundersAvailableDaysPerWeek": 0})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed = engine.load_json(self.tmp_path / "output" / "capacity-feed.json")
        self.assertEqual(feed["capacityStatus"], "Not enough signal yet")
        self.assertIsNone(feed["weeksOfCommittedWorkMin"])

    def test_full_run_computes_real_capacity_status(self):
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": [
            {"organisation": "BBVA", "title": "AI Governance Advisory", "type": "Enterprise Contract", "stage": "won"},
        ]})
        engine.save_json(self.tmp_path / "delivery-log.json", {"engagements": {}})
        engine.save_json(self.tmp_path / "ceo-advisor-feed.json", {"feed": [
            {"opportunityId": "opp-1", "organisation": "Acme", "title": "AI Risk Assessment", "status": "Ready To Send"},
        ]})
        engine.save_json(self.tmp_path / "service_recs.json", {"recommendations": {
            "opp-1": {"recommendedEngagementType": "Consulting Project", "notApplicable": False},
        }})
        engine.save_json(self.tmp_path / "capacity-config.json", {
            "foundersAvailableDaysPerWeek": 4,
            "weeksOfCommittedWorkThresholds": {"nearCapacity": 6, "overCapacity": 10},
        })

        exit_code = generate.main()
        self.assertEqual(exit_code, 0)

        feed = engine.load_json(self.tmp_path / "output" / "capacity-feed.json")
        self.assertEqual(len(feed["activeEngagements"]), 1)
        self.assertEqual(len(feed["pendingProposals"]), 1)
        # 30-120 (active) + 10-40 (pending) = 40-160 days / 4 per week = 10.0-40.0 weeks
        self.assertEqual(feed["weeksOfCommittedWorkMin"], 10.0)
        self.assertEqual(feed["capacityStatus"], "Over Capacity")

        report = (self.tmp_path / "output" / "capacity-report.md").read_text(encoding="utf-8")
        self.assertIn("BBVA", report)
        self.assertIn("Acme", report)
        self.assertIn("Over Capacity", report)


if __name__ == "__main__":
    unittest.main()
