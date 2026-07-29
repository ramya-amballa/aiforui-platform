#!/usr/bin/env python3
"""
Unit and integration tests for Executive Memory (AOS Sprint 20).

Every aggregation is checked for the "never fabricate" boundary
specifically: a closure report still showing the raw
{{LESSONS_LEARNED}} placeholder contributes nothing to the library, a
risk seen at only one organisation is not "recurring," and an empty
history produces an honest empty result, never invented data.

Run with:
    python3 -m unittest tests.test_executive_memory_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import executive_memory_engine as engine  # noqa: E402
import generate  # noqa: E402


class RecurringPrioritiesTests(unittest.TestCase):
    def test_counts_organisation_recurrence_across_days(self):
        log = {"log": [
            {"date": "2026-07-27", "top3": [{"organisation": "BBVA"}, {"organisation": "Acme"}], "alertTypes": ["ADGL demand increasing"]},
            {"date": "2026-07-28", "top3": [{"organisation": "BBVA"}], "alertTypes": ["ADGL demand increasing"]},
            {"date": "2026-07-29", "top3": [{"organisation": "BBVA"}], "alertTypes": []},
        ]}
        recurring_orgs, recurring_alerts, days = engine.recurring_priorities(log, min_occurrences=2)
        self.assertEqual(days, 3)
        self.assertEqual(recurring_orgs, [{"organisation": "BBVA", "daysInTop3": 3}])
        self.assertEqual(recurring_alerts, [{"alertType": "ADGL demand increasing", "daysFired": 2}])

    def test_below_threshold_is_honestly_excluded(self):
        log = {"log": [{"date": "2026-07-29", "top3": [{"organisation": "Acme"}], "alertTypes": []}]}
        recurring_orgs, recurring_alerts, days = engine.recurring_priorities(log, min_occurrences=2)
        self.assertEqual(recurring_orgs, [])
        self.assertEqual(days, 1)

    def test_empty_log_is_honest(self):
        recurring_orgs, recurring_alerts, days = engine.recurring_priorities({"log": []})
        self.assertEqual(recurring_orgs, [])
        self.assertEqual(recurring_alerts, [])
        self.assertEqual(days, 0)

    def test_same_organisation_twice_in_one_day_top3_counts_once(self):
        log = {"log": [{"date": "2026-07-29", "top3": [{"organisation": "BBVA"}, {"organisation": "BBVA"}], "alertTypes": []}]}
        recurring_orgs, _, _ = engine.recurring_priorities(log, min_occurrences=1)
        self.assertEqual(recurring_orgs, [{"organisation": "BBVA", "daysInTop3": 1}])


class LessonsLearnedExtractionTests(unittest.TestCase):
    def test_extracts_real_founder_text(self):
        text = "# Report\n\n## Lessons Learned\n\nThe client underestimated data readiness.\n\n## Recommended Next Steps\n\nFollow up.\n"
        self.assertEqual(engine.extract_lessons_learned(text), "The client underestimated data readiness.")

    def test_unfilled_placeholder_contributes_nothing(self):
        # The real template's literal, un-parameterised token — see
        # templates/delivery/project-closure-report-template.md.
        text = "# Report\n\n## Lessons Learned\n\n{{LESSONS_LEARNED}}\n\n## Recommended Next Steps\n"
        self.assertIsNone(engine.extract_lessons_learned(text))

    def test_no_heading_at_all_is_honest_none(self):
        self.assertIsNone(engine.extract_lessons_learned("# Report\n\nNo sections here.\n"))

    def test_missing_next_heading_still_extracts_to_end_of_file(self):
        text = "# Report\n\n## Lessons Learned\n\nGood engagement overall.\n"
        self.assertEqual(engine.extract_lessons_learned(text), "Good engagement overall.")


class LessonsLearnedLibraryTests(unittest.TestCase):
    def test_builds_library_from_real_files_on_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            closure_path = tmp_path / "closure.md"
            closure_path.write_text("## Lessons Learned\n\nReal lesson text.\n\n## Recommended Next Steps\n", encoding="utf-8")
            with patch("executive_memory_engine.REPO_ROOT", tmp_path):
                delivery_feed = {"engagements": [
                    {"organisation": "BBVA", "artifacts": {"project-closure-report": "closure.md"}},
                ]}
                library = engine.build_lessons_learned_library(delivery_feed)
            self.assertEqual(len(library), 1)
            self.assertEqual(library[0]["lessons"], "Real lesson text.")

    def test_engagement_with_no_closure_report_path_is_skipped(self):
        delivery_feed = {"engagements": [{"organisation": "BBVA", "artifacts": {}}]}
        self.assertEqual(engine.build_lessons_learned_library(delivery_feed), [])

    def test_missing_file_on_disk_is_skipped_not_errored(self):
        delivery_feed = {"engagements": [
            {"organisation": "BBVA", "artifacts": {"project-closure-report": "nonexistent/path.md"}},
        ]}
        self.assertEqual(engine.build_lessons_learned_library(delivery_feed), [])


class RecurringGovernanceRisksTests(unittest.TestCase):
    def test_finds_a_risk_shared_across_two_organisations(self):
        ai_feed = {"briefs": [
            {"organisation": "BBVA", "governanceRisks": [{"risk": "Human oversight", "why": "test"}]},
            {"organisation": "Acme", "governanceRisks": [{"risk": "Human oversight", "why": "test"}]},
            {"organisation": "OtherCo", "governanceRisks": [{"risk": "Privacy", "why": "test"}]},
        ]}
        recurring = engine.recurring_governance_risks(ai_feed, min_occurrences=2)
        self.assertEqual(len(recurring), 1)
        self.assertEqual(recurring[0]["risk"], "Human oversight")
        self.assertEqual(set(recurring[0]["organisations"]), {"BBVA", "Acme"})

    def test_a_risk_seen_at_only_one_organisation_is_not_recurring(self):
        ai_feed = {"briefs": [{"organisation": "BBVA", "governanceRisks": [{"risk": "Privacy", "why": "test"}]}]}
        self.assertEqual(engine.recurring_governance_risks(ai_feed, min_occurrences=2), [])

    def test_no_briefs_is_honest_empty(self):
        self.assertEqual(engine.recurring_governance_risks({"briefs": []}), [])


class RenderMarkdownTests(unittest.TestCase):
    def test_honest_empty_messages_when_nothing_recurs_yet(self):
        markdown = engine.render_executive_memory_markdown([], [], 0, [], [], [])
        self.assertIn("No organisation has recurred", markdown)
        self.assertIn("No alert type has recurred", markdown)
        self.assertIn("No engagement has a completed Lessons Learned", markdown)
        self.assertIn("No governance risk has recurred", markdown)
        self.assertIn("No decisions recorded yet", markdown)

    def test_real_data_appears_verbatim(self):
        markdown = engine.render_executive_memory_markdown(
            [{"organisation": "BBVA", "daysInTop3": 3}],
            [{"alertType": "ADGL demand increasing", "daysFired": 2}],
            5,
            [{"organisation": "BBVA", "lessons": "Real lesson text.", "closureReportPath": "x"}],
            [{"risk": "Human oversight", "organisations": ["BBVA", "Acme"], "occurrenceCount": 2}],
            [{"date": "2026-07-01", "decision": "Do not undercut day rate below floor.", "context": "test"}],
        )
        self.assertIn("BBVA", markdown)
        self.assertIn("Top 3 on 3 day(s)", markdown)
        self.assertIn("ADGL demand increasing", markdown)
        self.assertIn("Real lesson text.", markdown)
        self.assertIn("Human oversight", markdown)
        self.assertIn("Do not undercut day rate below floor.", markdown)


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_default_is_deep_copied_not_shared(self):
        first = engine.load_json(Path("/nonexistent/path.json"), {"log": []})
        first["log"].append({"date": "2026-07-29"})
        second = engine.load_json(Path("/nonexistent/path.json"), {"log": []})
        self.assertEqual(second["log"], [])


class GenerateEndToEndTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)

        patches = [
            patch("executive_memory_engine.CEO_ADVISOR_PRIORITIES_LOG_PATH", self.tmp_path / "priorities_log.json"),
            patch("executive_memory_engine.DELIVERY_INTELLIGENCE_FEED_PATH", self.tmp_path / "delivery_feed.json"),
            patch("executive_memory_engine.ACCOUNT_INTELLIGENCE_FEED_PATH", self.tmp_path / "ai_feed.json"),
            patch("executive_memory_engine.DECISION_LOG_PATH", self.tmp_path / "decision-log.json"),
            patch("executive_memory_engine.FEED_PATH", self.tmp_path / "output" / "executive-memory-feed.json"),
            patch("executive_memory_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_runs_honestly_empty_when_nothing_exists_yet(self):
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed = engine.load_json(self.tmp_path / "output" / "executive-memory-feed.json")
        self.assertEqual(feed["recurringPriorities"], [])
        self.assertEqual(feed["daysTracked"], 0)
        report = (self.tmp_path / "output" / "executive-memory-report.md").read_text(encoding="utf-8")
        self.assertIn("No organisation has recurred", report)

    def test_full_run_aggregates_all_four_sources(self):
        engine.save_json(self.tmp_path / "priorities_log.json", {"log": [
            {"date": "2026-07-28", "top3": [{"organisation": "BBVA", "label": "X", "source": "Y"}], "alertTypes": ["Test alert"]},
            {"date": "2026-07-29", "top3": [{"organisation": "BBVA", "label": "X", "source": "Y"}], "alertTypes": ["Test alert"]},
        ]})
        closure_path = self.tmp_path / "closure.md"
        closure_path.write_text("## Lessons Learned\n\nReal lesson.\n\n## Recommended Next Steps\n", encoding="utf-8")
        engine.save_json(self.tmp_path / "delivery_feed.json", {"engagements": [
            {"organisation": "BBVA", "artifacts": {"project-closure-report": "closure.md"}},
        ]})
        engine.save_json(self.tmp_path / "ai_feed.json", {"briefs": [
            {"organisation": "BBVA", "governanceRisks": [{"risk": "Human oversight", "why": "t"}]},
            {"organisation": "Acme", "governanceRisks": [{"risk": "Human oversight", "why": "t"}]},
        ]})
        engine.save_json(self.tmp_path / "decision-log.json", {"decisions": [
            {"date": "2026-07-01", "decision": "Do not undercut day rate.", "context": "Learned the hard way."},
        ]})

        exit_code = generate.main()
        self.assertEqual(exit_code, 0)

        feed = engine.load_json(self.tmp_path / "output" / "executive-memory-feed.json")
        self.assertEqual(feed["recurringPriorities"], [{"organisation": "BBVA", "daysInTop3": 2}])
        self.assertEqual(feed["daysTracked"], 2)
        self.assertEqual(len(feed["lessonsLearnedLibrary"]), 1)
        self.assertEqual(len(feed["recurringGovernanceRisks"]), 1)
        self.assertEqual(len(feed["founderDecisions"]), 1)

        report = (self.tmp_path / "output" / "executive-memory-report.md").read_text(encoding="utf-8")
        self.assertIn("BBVA", report)
        self.assertIn("Real lesson.", report)
        self.assertIn("Do not undercut day rate.", report)


if __name__ == "__main__":
    unittest.main()
