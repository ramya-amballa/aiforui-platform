#!/usr/bin/env python3
"""
Regression tests for prepare.py's proposal-file generation and the
dashboard's ability to actually find those files afterward.

Real bug this suite exists to catch: prepare.py always computed a
cover letter, proposal, recruiter outreach and client outreach for
every prepared opportunity, but only ever wrote them combined into one
package.md file and recorded a single packagePath. The dashboard's
"Download a Proposal" button then resolved that path via aos_path()
(AOS/-relative) instead of REPO_ROOT (which is what packagePath is
actually relative to) - doubling the "AOS/" prefix into a path that
never existed, so every proposal - including a real BBVA package a
founder was trying to review - showed "Package file not found on
disk" even though prepare.py had written it correctly. Fixed by (a)
resolving packagePath via REPO_ROOT in the dashboard, and (b) writing
four standalone artifact files (proposal, cover letter, recruiter
message, client outreach) alongside the combined package, so the
dashboard can preview/copy/download each piece on its own instead of
only the combined file.

Every test mocks every path prepare.py touches (schema, pipeline, CRM,
service recommendations, processed-index, feed, packages dir, and
REPO_ROOT itself) so nothing here reads or writes real AOS data.

Run with:
    python3 -m unittest tests.test_prepare -v   (from runtime/)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import prepare  # noqa: E402

ALL_PATH_KEYS = ("packagePath", "proposalPath", "coverLetterPath",
                 "recruiterMessagePath", "clientOutreachPath")

DIRECT_OPPORTUNITY = {
    "id": "test-bbva-001",
    "title": "AI Adoption",
    "organisation": "BBVA",
    "classification": "Immediate Proposal",
    "description": "BBVA is adopting AI at scale across its operations.",
    "domainTags": ["ADGL", "AI Governance"],
    "location": "Spain",
    "sourceCategory": "Demand Signal",
    "source": "Demand Signal",
    "autoScored": True,
    "scopedEngagement": True,
    "priorityScore": 82,
    "scores": {"probabilityOfWinning": 6, "timeRequired": 7},
}

RECRUITER_OPPORTUNITY = dict(
    DIRECT_OPPORTUNITY,
    id="test-recruiter-001",
    organisation="Acme Corp",
    sourceCategory="Recruiter Channel",
    source="TalentAgency",
)


class ProposalFileGenerationTests(unittest.TestCase):
    """Creates a sample opportunity, runs the real Sales Director runtime
    (prepare.main()), and verifies every proposal file it claims to have
    written genuinely exists on disk with real content."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)
        self.packages_dir = self.tmp_path / "packages"

        patches = [
            patch("prepare.REPO_ROOT", self.tmp_path),
            patch("prepare.OPPORTUNITY_SCHEMA_PATH", self.tmp_path / "opportunity-schema.json"),
            patch("prepare.PIPELINE_PATH", self.tmp_path / "pipeline.json"),
            patch("prepare.CRM_PATH", self.tmp_path / "company-intelligence.json"),
            patch("prepare.SERVICE_RECOMMENDATIONS_PATH", self.tmp_path / "service-recommendations.json"),
            patch("prepare.OUTPUT_DIR", self.tmp_path),
            patch("prepare.PACKAGES_DIR", self.packages_dir),
            patch("prepare.PROCESSED_INDEX_PATH", self.tmp_path / "processed-index.json"),
            patch("prepare.CEO_FEED_PATH", self.tmp_path / "ceo-advisor-feed.json"),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        prepare.save_json(self.tmp_path / "pipeline.json", {"pipeline": []})
        prepare.save_json(self.tmp_path / "company-intelligence.json", {"companies": []})
        prepare.save_json(self.tmp_path / "service-recommendations.json", {"recommendations": {}})

    def _write_opportunities(self, opportunities):
        prepare.save_json(self.tmp_path / "opportunity-schema.json", {"opportunities": opportunities})

    def test_prepare_creates_all_five_files_and_records_their_paths(self):
        self._write_opportunities([DIRECT_OPPORTUNITY])
        exit_code = prepare.main()
        self.assertEqual(exit_code, 0)

        feed = prepare.load_json(self.tmp_path / "ceo-advisor-feed.json")
        self.assertEqual(len(feed["feed"]), 1)
        entry = feed["feed"][0]
        self.assertEqual(entry["organisation"], "BBVA")

        for key in ALL_PATH_KEYS:
            self.assertIn(key, entry, f"{key} missing from feed entry")
            file_path = prepare.REPO_ROOT / entry[key]
            self.assertTrue(file_path.exists(), f"{key} -> {file_path} does not exist on disk")
            self.assertTrue(file_path.read_text(encoding="utf-8").strip(), f"{key} file is empty")

        # Same paths must also be recorded in processed-index.json, so a
        # later run can tell this opportunity already has every file.
        processed = prepare.load_json(self.tmp_path / "processed-index.json")
        record = processed["processed"]["test-bbva-001"]
        for key in ALL_PATH_KEYS:
            self.assertIn(key, record)

    def test_dashboard_resolves_every_section_path_via_repo_root(self):
        """Mirrors 08_Sales_Director.py's own resolution
        (REPO_ROOT / selected[key]) exactly, since importing a Streamlit
        page directly isn't practical in a unit test - this is the same
        doubled-"AOS/"-prefix bug the dashboard fix addressed, pinned
        here so a future change to either side can't reintroduce it
        without this test catching it."""
        self._write_opportunities([DIRECT_OPPORTUNITY])
        prepare.main()

        feed = prepare.load_json(self.tmp_path / "ceo-advisor-feed.json")
        entry = feed["feed"][0]
        for key in ALL_PATH_KEYS:
            resolved = prepare.REPO_ROOT / entry[key]
            self.assertTrue(resolved.exists(), f"dashboard-style resolution of {key} failed: {resolved}")
            content = resolved.read_text(encoding="utf-8")
            self.assertGreater(len(content), 0)

    def test_recruiter_message_states_not_applicable_for_direct_organisation(self):
        # DIRECT_OPPORTUNITY has no recruiter channel - the recruiter
        # message file must still exist (never omitted), but honestly
        # say it doesn't apply rather than fabricate a message.
        self._write_opportunities([DIRECT_OPPORTUNITY])
        prepare.main()
        feed = prepare.load_json(self.tmp_path / "ceo-advisor-feed.json")
        entry = feed["feed"][0]
        content = (prepare.REPO_ROOT / entry["recruiterMessagePath"]).read_text(encoding="utf-8")
        self.assertIn("Not applicable", content)

    def test_recruiter_message_is_real_for_recruiter_channel_organisation(self):
        self._write_opportunities([RECRUITER_OPPORTUNITY])
        prepare.main()
        feed = prepare.load_json(self.tmp_path / "ceo-advisor-feed.json")
        entry = feed["feed"][0]
        content = (prepare.REPO_ROOT / entry["recruiterMessagePath"]).read_text(encoding="utf-8")
        self.assertNotIn("Not applicable", content)
        self.assertIn("TalentAgency", content)

    def test_rerun_is_idempotent_and_does_not_duplicate_feed_entries(self):
        self._write_opportunities([DIRECT_OPPORTUNITY])
        prepare.main()
        prepare.main()
        feed = prepare.load_json(self.tmp_path / "ceo-advisor-feed.json")
        self.assertEqual(len(feed["feed"]), 1)

    def test_backfills_missing_section_paths_for_legacy_record(self):
        # Simulates the exact real-world state that produced "Package
        # file not found on disk" for a pre-fix package: an opportunity
        # already processed by an older prepare.py that only ever wrote
        # the combined package.md and recorded just packagePath. A later
        # run must repair it - write the four missing files and add the
        # missing path keys - without duplicating the feed entry or
        # silently changing its already-recorded status.
        self._write_opportunities([DIRECT_OPPORTUNITY])

        self.packages_dir.mkdir(parents=True, exist_ok=True)
        legacy_package_file = self.packages_dir / "test-bbva-001-bbva-ai-adoption.md"
        legacy_package_file.write_text("# legacy combined package only\n", encoding="utf-8")
        legacy_relative = str(legacy_package_file.relative_to(self.tmp_path))

        prepare.save_json(self.tmp_path / "processed-index.json", {"processed": {
            "test-bbva-001": {
                "datePrepared": "2026-07-20",
                "status": "Needs Review",
                "packagePath": legacy_relative,
            }
        }})
        prepare.save_json(self.tmp_path / "ceo-advisor-feed.json", {"feed": [{
            "opportunityId": "test-bbva-001",
            "title": "AI Adoption",
            "organisation": "BBVA",
            "status": "Needs Review",
            "packagePath": legacy_relative,
        }]})

        exit_code = prepare.main()
        self.assertEqual(exit_code, 0)

        feed = prepare.load_json(self.tmp_path / "ceo-advisor-feed.json")
        self.assertEqual(len(feed["feed"]), 1, "backfill must update the existing entry, not append a duplicate")
        entry = feed["feed"][0]
        self.assertEqual(entry["status"], "Needs Review", "backfill must not silently change a recorded status")
        for key in ("proposalPath", "coverLetterPath", "recruiterMessagePath", "clientOutreachPath"):
            self.assertIn(key, entry)
            self.assertTrue((prepare.REPO_ROOT / entry[key]).exists())

    def test_no_fabricated_records_every_recorded_path_has_a_real_file(self):
        """Do-not-fabricate check: for every entry ever written to the feed
        or processed-index, every path key it records must point to a
        file that actually exists - never a path recorded speculatively."""
        self._write_opportunities([DIRECT_OPPORTUNITY, RECRUITER_OPPORTUNITY])
        prepare.main()

        feed = prepare.load_json(self.tmp_path / "ceo-advisor-feed.json")
        processed = prepare.load_json(self.tmp_path / "processed-index.json")
        self.assertEqual(len(feed["feed"]), 2)

        for entry in feed["feed"]:
            for key in ALL_PATH_KEYS:
                self.assertTrue((prepare.REPO_ROOT / entry[key]).exists(),
                                f"feed entry for {entry['opportunityId']} claims {key} but no file exists")
        for record in processed["processed"].values():
            for key in ALL_PATH_KEYS:
                self.assertTrue((prepare.REPO_ROOT / record[key]).exists(),
                                f"processed-index record claims {key} but no file exists")


if __name__ == "__main__":
    unittest.main()
