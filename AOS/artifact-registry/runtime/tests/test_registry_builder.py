import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import registry_builder as builder  # noqa: E402
import registry_model as model  # noqa: E402


def make_tmp_output_tree(base):
    """A small, realistic output/ tree — enough shapes to exercise
    every artifactType, without depending on the real repository's
    live output/ contents."""
    aos_dir = Path(base)

    sd = aos_dir / "output" / "sales-director"
    sd.mkdir(parents=True)
    (sd / "2026-08-02-sales-director-report.md").write_text("# Sales Director Report\n", encoding="utf-8")
    (sd / "ceo-advisor-feed.json").write_text(json.dumps({"feed": []}), encoding="utf-8")

    rh = aos_dir / "output" / "revenue-hunter"
    rh.mkdir(parents=True)
    (rh / "revenue-dashboard.md").write_text("# Revenue Dashboard\n", encoding="utf-8")

    orch_logs = aos_dir / "output" / "orchestrator" / "logs"
    orch_logs.mkdir(parents=True)
    (orch_logs / "2026-08-02-040232-orchestrator.log").write_text("run log\n", encoding="utf-8")

    orch_status = aos_dir / "output" / "orchestrator" / "status.json"
    orch_status.write_text(json.dumps({"overallStatus": "SUCCESS"}), encoding="utf-8")

    briefs = aos_dir / "output" / "daily-briefs" / "2026" / "08" / "02"
    briefs.mkdir(parents=True)
    (briefs / "executive-dashboard.md").write_text("# Daily Brief\n", encoding="utf-8")

    config_dir = aos_dir / "orchestrator" / "runtime" / "config"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "orchestrator-config.json"
    config_path.write_text(json.dumps({
        "employees": [
            {"key": "sales-director", "dependsOn": ["demand-intelligence", "crm"]},
            {"key": "revenue-hunter", "dependsOn": ["demand-intelligence"]},
        ]
    }), encoding="utf-8")

    return aos_dir / "output", config_path


class ScanOutputFilesTests(unittest.TestCase):
    def test_finds_every_real_file_and_no_directories(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir, _ = make_tmp_output_tree(d)
            found = builder.scan_output_files(output_dir)
            paths = [rel for _, rel in found]
            self.assertIn("output/sales-director/2026-08-02-sales-director-report.md", paths)
            self.assertIn("output/orchestrator/status.json", paths)
            self.assertEqual(len(found), 6)

    def test_empty_output_tree_produces_no_files_not_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d) / "output"
            output_dir.mkdir()
            self.assertEqual(builder.scan_output_files(output_dir), [])


class BuildIndexTests(unittest.TestCase):
    def test_indexes_every_file_with_correct_counts(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir, config_path = make_tmp_output_tree(d)
            index = builder.build_index(output_dir=output_dir, config_path=config_path)

            self.assertEqual(index["artifactCount"], 6)
            self.assertEqual(index["employeeCounts"], {"revenue-hunter": 1, "sales-director": 2})
            self.assertIn("schema", index)
            self.assertEqual(index["schemaVersion"], model.INDEX_SCHEMA_VERSION)

    def test_platform_artifacts_are_indexed_but_not_counted_per_employee(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir, config_path = make_tmp_output_tree(d)
            index = builder.build_index(output_dir=output_dir, config_path=config_path)

            employees_present = {a["employee"] for a in index["artifacts"]}
            self.assertIn(None, employees_present)  # orchestrator + daily-briefs artifacts
            self.assertNotIn("orchestrator", index["employeeCounts"])

    def test_lineage_is_populated_from_the_real_config_used(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir, config_path = make_tmp_output_tree(d)
            index = builder.build_index(output_dir=output_dir, config_path=config_path)

            sd_report = next(a for a in index["artifacts"] if a["path"].endswith("sales-director-report.md"))
            self.assertEqual(sd_report["lineage"]["dependsOnEmployees"], ["demand-intelligence", "crm"])

    def test_rebuilding_from_scratch_reproduces_identical_ids(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir, config_path = make_tmp_output_tree(d)
            first = builder.build_index(output_dir=output_dir, config_path=config_path)
            second = builder.build_index(output_dir=output_dir, config_path=config_path)

            first_ids = sorted(a["id"] for a in first["artifacts"])
            second_ids = sorted(a["id"] for a in second["artifacts"])
            self.assertEqual(first_ids, second_ids)

    def test_validation_summary_flags_the_schemaless_feed_fixture(self):
        """make_tmp_output_tree's ceo-advisor-feed.json fixture is
        deliberately missing its own 'schema' key — Phase 3's
        validation should flag it, advisory only, without excluding it
        from the index."""
        with tempfile.TemporaryDirectory() as d:
            output_dir, config_path = make_tmp_output_tree(d)
            index = builder.build_index(output_dir=output_dir, config_path=config_path)

            self.assertEqual(index["validationSummary"]["flaggedCount"], 1)
            self.assertEqual(index["validationSummary"]["flagCounts"], {"feed-missing-schema-key": 1})
            # Still indexed, just flagged — advisory never means excluded.
            self.assertEqual(index["artifactCount"], 6)

    def test_clean_output_tree_has_no_flags(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d) / "output" / "revenue-hunter"
            output_dir.mkdir(parents=True)
            (output_dir / "revenue-dashboard.md").write_text("# Revenue Dashboard\n", encoding="utf-8")
            config_path = Path(d) / "missing-config.json"

            index = builder.build_index(output_dir=output_dir.parent, config_path=config_path)

            self.assertEqual(index["validationSummary"], {"flaggedCount": 0, "flagCounts": {}})

    def test_empty_output_tree_produces_a_valid_empty_index(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d) / "output"
            output_dir.mkdir()
            config_path = Path(d) / "missing-config.json"
            index = builder.build_index(output_dir=output_dir, config_path=config_path)

            self.assertEqual(index["artifactCount"], 0)
            self.assertEqual(index["artifacts"], [])
            self.assertEqual(index["employeeCounts"], {})


class SaveIndexTests(unittest.TestCase):
    def test_writes_valid_json_creating_parent_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            index_path = Path(d) / "nested" / "index" / "artifact-index.json"
            builder.save_index({"artifactCount": 0, "artifacts": []}, path=index_path)

            self.assertTrue(index_path.exists())
            with open(index_path) as f:
                data = json.load(f)
            self.assertEqual(data["artifactCount"], 0)


class MainTests(unittest.TestCase):
    def test_main_builds_and_writes_the_index_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            output_dir, config_path = make_tmp_output_tree(d)
            index_path = Path(d) / "artifact-index.json"

            with patch.object(model, "OUTPUT_DIR", output_dir), \
                 patch.object(model, "ORCHESTRATOR_CONFIG_PATH", config_path), \
                 patch.object(builder, "INDEX_PATH", index_path):
                exit_code = builder.main()

            self.assertEqual(exit_code, 0)
            self.assertTrue(index_path.exists())
            with open(index_path) as f:
                data = json.load(f)
            self.assertEqual(data["artifactCount"], 6)


if __name__ == "__main__":
    unittest.main()
