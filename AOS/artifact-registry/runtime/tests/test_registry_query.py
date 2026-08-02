import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import registry_query as query  # noqa: E402


def make_index():
    return {
        "schemaVersion": "1",
        "generatedAt": "2026-08-02T04:00:00+00:00",
        "artifactCount": 4,
        "employeeCounts": {"sales-director": 1, "account-intelligence": 2, "delivery-intelligence": 1},
        "artifacts": [
            {
                "id": "art_1", "employee": "sales-director", "artifactType": "daily-report",
                "path": "output/sales-director/2026-08-01-sales-director-report.md",
                "producedDate": "2026-08-01", "fileModifiedAt": "2026-08-01T04:00:00+00:00",
                "lineage": {"employee": "sales-director", "dependsOnEmployees": ["crm"], "note": "x"},
            },
            {
                "id": "art_2", "employee": "sales-director", "artifactType": "daily-report",
                "path": "output/sales-director/2026-08-02-sales-director-report.md",
                "producedDate": "2026-08-02", "fileModifiedAt": "2026-08-02T04:00:00+00:00",
                "lineage": {"employee": "sales-director", "dependsOnEmployees": ["crm"], "note": "x"},
            },
            {
                "id": "art_3", "employee": "account-intelligence", "artifactType": "account-brief",
                "path": "output/account-intelligence/account-briefs/bbva.md",
                "producedDate": None, "fileModifiedAt": "2026-08-02T04:00:00+00:00",
                "lineage": {"employee": "account-intelligence", "dependsOnEmployees": [], "note": "x"},
            },
            {
                "id": "art_4", "employee": "delivery-intelligence", "artifactType": "delivery-kit-component",
                "path": "output/delivery-intelligence/delivery-kits/bbva/kickoff-agenda.md",
                "producedDate": None, "fileModifiedAt": "2026-08-02T04:00:00+00:00",
                "lineage": {"employee": "delivery-intelligence", "dependsOnEmployees": [], "note": "x"},
            },
        ],
    }


class LoadIndexTests(unittest.TestCase):
    def test_missing_index_returns_an_empty_shaped_index_not_an_error(self):
        index = query.load_index(index_path=Path("/nonexistent/artifact-index.json"))
        self.assertEqual(index["artifactCount"], 0)
        self.assertEqual(index["artifacts"], [])
        self.assertIsNone(index["generatedAt"])

    def test_existing_index_loads_real_content(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "artifact-index.json"
            p.write_text(json.dumps(make_index()), encoding="utf-8")
            index = query.load_index(index_path=p)
            self.assertEqual(index["artifactCount"], 4)


class IsAvailableTests(unittest.TestCase):
    def test_never_built_index_is_not_available(self):
        self.assertFalse(query.is_available(query.EMPTY_INDEX))

    def test_built_index_is_available_even_if_empty_of_artifacts(self):
        built_but_empty = dict(query.EMPTY_INDEX)
        built_but_empty["generatedAt"] = "2026-08-02T04:00:00+00:00"
        self.assertTrue(query.is_available(built_but_empty))


class AllArtifactsTests(unittest.TestCase):
    def test_filters_by_employee(self):
        index = make_index()
        results = query.all_artifacts(index, employee="sales-director")
        self.assertEqual(len(results), 2)

    def test_filters_by_artifact_type(self):
        index = make_index()
        results = query.all_artifacts(index, artifact_type="delivery-kit-component")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "art_4")

    def test_no_filters_returns_everything(self):
        index = make_index()
        self.assertEqual(len(query.all_artifacts(index)), 4)


class LatestForEmployeeTests(unittest.TestCase):
    def test_returns_the_most_recently_produced_artifact(self):
        index = make_index()
        latest = query.latest_for_employee(index, "sales-director")
        self.assertEqual(latest["id"], "art_2")

    def test_returns_none_when_employee_has_nothing_indexed(self):
        index = make_index()
        self.assertIsNone(query.latest_for_employee(index, "recruiter-intelligence"))


class GetByIdTests(unittest.TestCase):
    def test_finds_a_real_artifact(self):
        index = make_index()
        self.assertEqual(query.get_by_id(index, "art_3")["employee"], "account-intelligence")

    def test_returns_none_for_an_unknown_id(self):
        index = make_index()
        self.assertIsNone(query.get_by_id(index, "art_does_not_exist"))


class ArtifactsForOrganisationTests(unittest.TestCase):
    def test_finds_account_brief_and_delivery_kit_component_by_slug(self):
        index = make_index()
        results = query.artifacts_for_organisation(index, "BBVA")
        ids = {a["id"] for a in results}
        self.assertEqual(ids, {"art_3", "art_4"})

    def test_organisation_with_no_indexed_artifacts_returns_empty_not_none(self):
        index = make_index()
        self.assertEqual(query.artifacts_for_organisation(index, "Nonexistent Corp"), [])

    def test_can_be_scoped_to_one_employee(self):
        index = make_index()
        results = query.artifacts_for_organisation(index, "BBVA", employee="account-intelligence")
        self.assertEqual([a["id"] for a in results], ["art_3"])


class LineageForTests(unittest.TestCase):
    def test_returns_the_lineage_of_a_real_artifact(self):
        index = make_index()
        lineage = query.lineage_for(index, "art_1")
        self.assertEqual(lineage["dependsOnEmployees"], ["crm"])

    def test_returns_none_for_an_unknown_artifact(self):
        index = make_index()
        self.assertIsNone(query.lineage_for(index, "art_missing"))


class FlaggedArtifactsTests(unittest.TestCase):
    def test_returns_only_artifacts_with_flags(self):
        index = make_index()
        index["artifacts"][0]["validationFlags"] = ["empty-file"]
        index["artifacts"][1]["validationFlags"] = []
        results = query.flagged_artifacts(index)
        self.assertEqual([a["id"] for a in results], ["art_1"])

    def test_empty_when_nothing_is_flagged(self):
        index = make_index()
        for a in index["artifacts"]:
            a["validationFlags"] = []
        self.assertEqual(query.flagged_artifacts(index), [])


class SummaryTests(unittest.TestCase):
    def test_reports_honestly_when_not_available(self):
        self.assertIn("Not available yet", query.summary(query.EMPTY_INDEX))

    def test_reports_real_counts_when_available(self):
        text = query.summary(make_index())
        self.assertIn("4 artifact(s)", text)
        self.assertIn("3 employee(s)", text)


if __name__ == "__main__":
    unittest.main()
