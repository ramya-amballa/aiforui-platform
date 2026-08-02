import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import registry_validation as validation  # noqa: E402


class ExtractConfidenceTests(unittest.TestCase):
    def test_extracts_the_real_markdown_confidence_pattern(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "package.md"
            p.write_text("**Confidence score:** 73/100  \n", encoding="utf-8")
            self.assertEqual(validation.extract_confidence(p, "daily-report"), 73.0)

    def test_extracts_confidencescore_json_field(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "feed.json"
            p.write_text(json.dumps({"confidenceScore": 82}), encoding="utf-8")
            self.assertEqual(validation.extract_confidence(p, "feed"), 82)

    def test_extracts_qualificationscore_json_field(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "feed.json"
            p.write_text(json.dumps({"qualificationScore": 64}), encoding="utf-8")
            self.assertEqual(validation.extract_confidence(p, "feed"), 64)

    def test_returns_none_honestly_when_no_confidence_pattern_present(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "report.md"
            p.write_text("# A report with no confidence line at all\n", encoding="utf-8")
            self.assertIsNone(validation.extract_confidence(p, "daily-report"))

    def test_never_guesses_from_malformed_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "broken.json"
            p.write_text("{not valid json", encoding="utf-8")
            self.assertIsNone(validation.extract_confidence(p, "feed"))

    def test_ignores_a_confidence_shaped_field_that_is_not_a_number(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "feed.json"
            p.write_text(json.dumps({"confidenceScore": "not a number"}), encoding="utf-8")
            self.assertIsNone(validation.extract_confidence(p, "feed"))


class ValidateArtifactTests(unittest.TestCase):
    def test_valid_feed_with_schema_key_has_no_flags(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x-feed.json"
            p.write_text(json.dumps({"schema": {}, "items": []}), encoding="utf-8")
            self.assertEqual(validation.validate_artifact(p, "output/x/x-feed.json", "feed"), [])

    def test_feed_missing_schema_key_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x-feed.json"
            p.write_text(json.dumps({"items": []}), encoding="utf-8")
            self.assertEqual(validation.validate_artifact(p, "output/x/x-feed.json", "feed"), ["feed-missing-schema-key"])

    def test_non_feed_json_missing_schema_key_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"
            p.write_text(json.dumps({"items": []}), encoding="utf-8")
            self.assertEqual(validation.validate_artifact(p, "output/x/x.json", "stable-snapshot"), [])

    def test_invalid_json_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "broken.json"
            p.write_text("{not valid", encoding="utf-8")
            self.assertEqual(validation.validate_artifact(p, "output/x/broken.json", "feed"), ["invalid-json"])

    def test_empty_file_is_flagged_unless_it_is_gitkeep(self):
        with tempfile.TemporaryDirectory() as d:
            empty = Path(d) / "empty.md"
            empty.write_text("", encoding="utf-8")
            self.assertEqual(validation.validate_artifact(empty, "output/x/empty.md", "daily-report"), ["empty-file"])

            gitkeep = Path(d) / ".gitkeep"
            gitkeep.write_text("", encoding="utf-8")
            self.assertEqual(validation.validate_artifact(gitkeep, "output/x/.gitkeep", "other"), [])

    def test_ordinary_markdown_report_has_no_flags(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "report.md"
            p.write_text("# A perfectly normal report\n", encoding="utf-8")
            self.assertEqual(validation.validate_artifact(p, "output/x/report.md", "daily-report"), [])

    def test_real_pilot_schema_contract_flags_a_broken_account_intelligence_feed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "account-intelligence-feed.json"
            # missing 'briefs', which the real pilot schema requires
            p.write_text(json.dumps({"schema": {}}), encoding="utf-8")
            flags = validation.validate_artifact(
                p, "output/account-intelligence/account-intelligence-feed.json", "feed"
            )
            self.assertIn("schema-contract:missing required field: briefs", flags)

    def test_real_pilot_schema_contract_passes_a_correctly_shaped_feed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "account-intelligence-feed.json"
            p.write_text(json.dumps({"schema": {}, "briefs": []}), encoding="utf-8")
            flags = validation.validate_artifact(
                p, "output/account-intelligence/account-intelligence-feed.json", "feed"
            )
            self.assertEqual(flags, [])

    def test_paths_with_no_pilot_schema_are_unaffected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "some-other-feed.json"
            p.write_text(json.dumps({"schema": {}, "anything": True}), encoding="utf-8")
            flags = validation.validate_artifact(p, "output/some-other-employee/some-other-feed.json", "feed")
            self.assertEqual(flags, [])


if __name__ == "__main__":
    unittest.main()
