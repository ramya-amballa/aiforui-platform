import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import generate  # noqa: E402


class DiscoveryRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inbox_dir = Path(self.tmp.name) / "inbox"
        self.output_dir = Path(self.tmp.name) / "output"
        self.feed_path = self.output_dir / "opportunity-intelligence-feed.json"
        self.inbox_dir.mkdir()

        self.patches = [
            patch.object(generate, "INBOX_DIR", self.inbox_dir),
            patch.object(generate, "OUTPUT_DIR", self.output_dir),
            patch.object(generate, "FEED_PATH", self.feed_path),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_inbox_entry(self, filename, entry):
        (self.inbox_dir / filename).write_text(json.dumps(entry), encoding="utf-8")

    def test_empty_inbox_produces_an_empty_but_valid_feed(self):
        feed, created, invalid, dup = generate.run_discovery()
        self.assertEqual(created, [])
        self.assertTrue(self.feed_path.exists())
        self.assertEqual(feed["opportunities"], [])

    def test_valid_entry_becomes_an_opportunity_in_the_feed(self):
        self._write_inbox_entry("a.json", {
            "opportunity_type": "CONSULTING", "company": "New Bank", "source": "public press release",
            "evidence": {"pain_evidence": True},
        })
        feed, created, invalid, dup = generate.run_discovery()
        self.assertEqual(len(created), 1)
        self.assertEqual(invalid, [])
        self.assertEqual(feed["opportunities"][0]["company"], "New Bank")

    def test_invalid_entry_is_skipped_not_crashed_on(self):
        self._write_inbox_entry("bad.json", {"opportunity_type": "NOT_REAL"})
        feed, created, invalid, dup = generate.run_discovery()
        self.assertEqual(created, [])
        self.assertEqual(len(invalid), 1)

    def test_re_running_does_not_duplicate_an_already_processed_entry(self):
        """TEST 8 at the CLI level."""
        entry = {"opportunity_type": "CONSULTING", "company": "Repeat Co", "source": "note"}
        self._write_inbox_entry("a.json", entry)
        generate.run_discovery()
        feed, created, invalid, dup = generate.run_discovery()
        self.assertEqual(created, [])
        self.assertEqual(len(dup), 1)
        self.assertEqual(len(feed["opportunities"]), 1)

    def test_report_file_is_written(self):
        self._write_inbox_entry("a.json", {"opportunity_type": "RELATIONSHIP", "company": "X", "source": "y"})
        generate.run_discovery()
        reports = list(self.output_dir.glob("*-opportunity-intelligence-report.md"))
        self.assertEqual(len(reports), 1)


class ApprovalCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inbox_dir = Path(self.tmp.name) / "inbox"
        self.output_dir = Path(self.tmp.name) / "output"
        self.feed_path = self.output_dir / "opportunity-intelligence-feed.json"
        self.inbox_dir.mkdir()
        self.patches = [
            patch.object(generate, "INBOX_DIR", self.inbox_dir),
            patch.object(generate, "OUTPUT_DIR", self.output_dir),
            patch.object(generate, "FEED_PATH", self.feed_path),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        (self.inbox_dir / "a.json").write_text(json.dumps({
            "opportunity_type": "RELATIONSHIP", "company": "X", "source": "y",
        }), encoding="utf-8")
        feed, created, _, _ = generate.run_discovery()
        self.opportunity_id = created[0]["opportunity_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_approve_action_persists_to_disk(self):
        generate.apply_approval_action("approve", self.opportunity_id, "dm", "Ramya", "looks good")
        feed = generate.load_feed()
        opp = next(o for o in feed["opportunities"] if o["opportunity_id"] == self.opportunity_id)
        self.assertEqual(opp["drafts"]["dm"]["approval_status"], "APPROVED")
        self.assertEqual(opp["drafts"]["dm"]["approved_by"], "Ramya")

    def test_mark_executed_while_pending_fails_safely_via_the_cli_path(self):
        """TEST 12, exercised through the same code path generate.py's
        CLI actually uses."""
        result = generate.apply_approval_action("mark-executed", self.opportunity_id, "dm", "Ramya", None)
        self.assertEqual(result, 1)  # non-zero exit — the CLI reports failure, doesn't silently succeed
        feed = generate.load_feed()
        opp = next(o for o in feed["opportunities"] if o["opportunity_id"] == self.opportunity_id)
        self.assertEqual(opp["drafts"]["dm"]["approval_status"], "PENDING_APPROVAL")

    def test_unknown_opportunity_id_fails_cleanly(self):
        result = generate.apply_approval_action("approve", "opp-does-not-exist", "dm", "Ramya", None)
        self.assertEqual(result, 1)

    def test_unknown_draft_key_fails_cleanly(self):
        result = generate.apply_approval_action("approve", self.opportunity_id, "not_a_real_draft", "Ramya", None)
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
