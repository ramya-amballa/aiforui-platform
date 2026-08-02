import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import registry_model as model  # noqa: E402


class StableArtifactIdTests(unittest.TestCase):
    def test_same_path_always_produces_the_same_id(self):
        a = model.stable_artifact_id("output/sales-director/2026-08-02-sales-director-report.md")
        b = model.stable_artifact_id("output/sales-director/2026-08-02-sales-director-report.md")
        self.assertEqual(a, b)

    def test_different_paths_produce_different_ids(self):
        a = model.stable_artifact_id("output/sales-director/2026-08-02-sales-director-report.md")
        b = model.stable_artifact_id("output/revenue-hunter/2026-08-02-revenue-dashboard.md")
        self.assertNotEqual(a, b)

    def test_id_has_a_stable_readable_prefix(self):
        self.assertTrue(model.stable_artifact_id("output/x/y.md").startswith("art_"))


class ContentHashTests(unittest.TestCase):
    def test_identical_content_produces_identical_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = Path(d) / "a.md"
            p2 = Path(d) / "b.md"
            p1.write_text("same content\n", encoding="utf-8")
            p2.write_text("same content\n", encoding="utf-8")
            self.assertEqual(model.content_hash(p1), model.content_hash(p2))

    def test_different_content_produces_different_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = Path(d) / "a.md"
            p2 = Path(d) / "b.md"
            p1.write_text("content one\n", encoding="utf-8")
            p2.write_text("content two\n", encoding="utf-8")
            self.assertNotEqual(model.content_hash(p1), model.content_hash(p2))

    def test_hash_is_prefixed_with_algorithm_name(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.md"
            p.write_text("x", encoding="utf-8")
            self.assertTrue(model.content_hash(p).startswith("sha256:"))


class ExtractProducedDateTests(unittest.TestCase):
    def test_extracts_a_real_embedded_date(self):
        self.assertEqual(
            model.extract_produced_date("output/sales-director/2026-08-02-sales-director-report.md"),
            "2026-08-02",
        )

    def test_returns_none_honestly_when_no_date_is_embedded(self):
        self.assertIsNone(model.extract_produced_date("output/revenue-hunter/revenue-dashboard.md"))


class ClassifyArtifactTests(unittest.TestCase):
    def test_dated_report_is_a_daily_report(self):
        self.assertEqual(
            model.classify_artifact("output/sales-director/2026-08-02-sales-director-report.md"),
            "daily-report",
        )

    def test_feed_file_is_a_feed(self):
        self.assertEqual(
            model.classify_artifact("output/account-intelligence/account-intelligence-feed.json"),
            "feed",
        )

    def test_undated_stable_file_is_a_stable_snapshot(self):
        self.assertEqual(
            model.classify_artifact("output/revenue-hunter/revenue-dashboard.md"),
            "stable-snapshot",
        )

    def test_delivery_kit_component(self):
        self.assertEqual(
            model.classify_artifact("output/delivery-intelligence/delivery-kits/bbva/kickoff-agenda.md"),
            "delivery-kit-component",
        )

    def test_account_brief(self):
        self.assertEqual(
            model.classify_artifact("output/account-intelligence/account-briefs/bbva.md"),
            "account-brief",
        )

    def test_strategy_document(self):
        self.assertEqual(
            model.classify_artifact("output/reverse-job-hunt/strategies/bbva.md"),
            "strategy-document",
        )

    def test_company_profile(self):
        self.assertEqual(
            model.classify_artifact("output/company-360/company-profiles/bbva.md"),
            "company-profile",
        )

    def test_orchestrator_log(self):
        self.assertEqual(
            model.classify_artifact("output/orchestrator/logs/2026-08-02-040232-orchestrator.log"),
            "orchestrator-log",
        )

    def test_orchestrator_report(self):
        self.assertEqual(
            model.classify_artifact("output/orchestrator/reports/2026-08-02-daily-execution-report.md"),
            "orchestrator-report",
        )

    def test_orchestrator_status(self):
        self.assertEqual(model.classify_artifact("output/orchestrator/status.json"), "orchestrator-status")

    def test_daily_brief_archive(self):
        self.assertEqual(
            model.classify_artifact("output/daily-briefs/2026/08/02/executive-dashboard.md"),
            "daily-brief-archive",
        )

    def test_unrecognised_shape_is_other_not_a_guess(self):
        self.assertEqual(model.classify_artifact("output/README.md"), "other")


class EmployeeForPathTests(unittest.TestCase):
    def test_ordinary_employee_artifact(self):
        self.assertEqual(model.employee_for_path("output/sales-director/report.md"), "sales-director")

    def test_orchestrator_artifacts_have_no_owning_employee(self):
        self.assertIsNone(model.employee_for_path("output/orchestrator/status.json"))

    def test_daily_briefs_have_no_owning_employee(self):
        self.assertIsNone(model.employee_for_path("output/daily-briefs/2026/08/02/executive-dashboard.md"))

    def test_top_level_output_file_has_no_owning_employee(self):
        self.assertIsNone(model.employee_for_path("output/README.md"))


class DependencyGraphTests(unittest.TestCase):
    def test_reads_the_real_dependson_graph_from_the_live_orchestrator_config(self):
        # Deliberately uses the real, committed orchestrator-config.json —
        # not a fixture — so this test fails loudly if that file's real
        # shape ever changes in a way lineage depends on.
        graph = model.load_dependency_graph()
        self.assertIn("sales-director", graph)
        self.assertIn("demand-intelligence", graph["sales-director"])
        # ceo-advisor must depend on every other employee, per the
        # Constitution's own terminal-node invariant.
        self.assertIn("sales-director", graph["ceo-advisor"])
        self.assertIn("delivery-intelligence", graph["ceo-advisor"])

    def test_missing_config_produces_an_empty_graph_not_a_crash(self):
        graph = model.load_dependency_graph(config_path=Path("/nonexistent/orchestrator-config.json"))
        self.assertEqual(graph, {})


class LineageForEmployeeTests(unittest.TestCase):
    def test_lineage_names_declared_dependencies(self):
        graph = {"sales-director": ["demand-intelligence", "crm"]}
        lineage = model.lineage_for_employee("sales-director", graph)
        self.assertEqual(lineage["employee"], "sales-director")
        self.assertEqual(lineage["dependsOnEmployees"], ["demand-intelligence", "crm"])
        self.assertIn("orchestrator-config.json", lineage["note"])

    def test_employee_with_no_declared_dependencies_gets_an_empty_list_not_a_guess(self):
        lineage = model.lineage_for_employee("tender-intelligence", {})
        self.assertEqual(lineage["dependsOnEmployees"], [])

    def test_platform_artifacts_have_no_employee_lineage(self):
        lineage = model.lineage_for_employee(None, {"sales-director": ["crm"]})
        self.assertIsNone(lineage["employee"])
        self.assertEqual(lineage["dependsOnEmployees"], [])


class BuildArtifactRecordTests(unittest.TestCase):
    def test_produces_every_documented_field(self):
        with tempfile.TemporaryDirectory() as d:
            aos_dir = Path(d)
            output_dir = aos_dir / "output" / "sales-director"
            output_dir.mkdir(parents=True)
            f = output_dir / "2026-08-02-sales-director-report.md"
            f.write_text("# Report\n", encoding="utf-8")

            record = model.build_artifact_record(
                f, "output/sales-director/2026-08-02-sales-director-report.md", {"sales-director": ["crm"]}
            )

            self.assertEqual(record["employee"], "sales-director")
            self.assertEqual(record["artifactType"], "daily-report")
            self.assertEqual(record["producedDate"], "2026-08-02")
            self.assertTrue(record["contentHash"].startswith("sha256:"))
            self.assertGreater(record["sizeBytes"], 0)
            self.assertEqual(record["schemaVersion"], "unversioned")
            self.assertIsNone(record["confidence"])
            self.assertEqual(record["lifecycle"], "published")
            self.assertEqual(record["lineage"]["dependsOnEmployees"], ["crm"])
            self.assertTrue(record["id"].startswith("art_"))

    def test_never_fabricates_a_confidence_score(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "x.md"
            f.write_text("content", encoding="utf-8")
            record = model.build_artifact_record(f, "output/x/x.md", {})
            self.assertIsNone(record["confidence"])

    def test_surfaces_a_real_confidence_pattern_already_present_in_content(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "package.md"
            f.write_text("**Confidence score:** 91/100  \n", encoding="utf-8")
            record = model.build_artifact_record(f, "output/sales-director/package.md", {})
            self.assertEqual(record["confidence"], 91.0)

    def test_includes_an_empty_validation_flags_list_when_nothing_is_wrong(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "report.md"
            f.write_text("# Fine\n", encoding="utf-8")
            record = model.build_artifact_record(f, "output/x/report.md", {})
            self.assertEqual(record["validationFlags"], [])

    def test_flags_a_feed_missing_its_schema_key(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "x-feed.json"
            f.write_text(json.dumps({"items": []}), encoding="utf-8")
            record = model.build_artifact_record(f, "output/x/x-feed.json", {})
            self.assertEqual(record["validationFlags"], ["feed-missing-schema-key"])


if __name__ == "__main__":
    unittest.main()
