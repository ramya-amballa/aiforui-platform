#!/usr/bin/env python3
"""
Unit and integration tests for Company 360 (AOS Sprint 19).

Every finder is tested for both the exact-match sources (organisation)
and the normalised-match sources (CRM's companyName, relationship-
intelligence's company) — including a real casing/whitespace mismatch,
since that's the one genuine risk this employee introduces (three
different field names for "which company" across the codebase).

Run with:
    python3 -m unittest tests.test_company_360_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import company_360_engine as engine  # noqa: E402
import generate  # noqa: E402

PROFILE = {
    "organisation": "BBVA", "industry": "Banking", "region": "Europe", "scale": "40,000 employees",
    "overallDemandScore": 70, "buyingReadinessScore": 80, "buyingReadinessBand": "High",
    "matchedCategories": ["ai_adoption"], "recommendedAction": "Prepare Insight Article",
    "recommendedActionReason": "test", "firstSeen": "2026-07-20", "lastSeen": "2026-07-27",
    "outreachHappened": False, "proposalCreated": False, "converted": False, "revenueGenerated": None,
}

AI_ENTRY = {
    "organisation": "BBVA", "executiveSummary": "BBVA is scaling AI adoption.",
    "deploymentStage": "Scaling", "outreachStrategy": "Prepare Insight Article",
    "overallPriority": 62, "decisionMakerTitles": ["Chief Risk Officer"],
    "governanceRisks": [{"risk": "Human oversight", "why": "Live systems need a human-in-the-loop point."}],
    "serviceFit": [{"service": "AI Deployment Governance (ADGL)", "confidence": "High"}],
    "briefPath": "AOS/output/account-intelligence/account-briefs/bbva.md",
}


class NormaliseTests(unittest.TestCase):
    def test_lowercases_and_trims(self):
        self.assertEqual(engine.normalise("  BBVA  "), "bbva")
        self.assertEqual(engine.normalise("BBVA"), engine.normalise("bbva"))

    def test_none_is_honest_empty_string(self):
        self.assertEqual(engine.normalise(None), "")


class FinderTests(unittest.TestCase):
    def test_find_account_intelligence_entry_exact_match(self):
        feed = {"briefs": [AI_ENTRY]}
        self.assertEqual(engine.find_account_intelligence_entry("BBVA", feed)["organisation"], "BBVA")
        self.assertIsNone(engine.find_account_intelligence_entry("Nonexistent", feed))

    def test_find_regulatory_domain_tags_deduplicates_and_preserves_order(self):
        opportunity_schema = {"opportunities": [
            {"organisation": "BBVA", "domainTags": ["DORA", "ADGL"]},
            {"organisation": "BBVA", "domainTags": ["ADGL", "GRC"]},
            {"organisation": "Other Co", "domainTags": ["EU AI Act"]},
        ]}
        tags = engine.find_regulatory_domain_tags("BBVA", opportunity_schema)
        self.assertEqual(tags, ["DORA", "ADGL", "GRC"])

    def test_find_regulatory_domain_tags_honest_empty_when_none(self):
        self.assertEqual(engine.find_regulatory_domain_tags("BBVA", {"opportunities": []}), [])

    def test_find_registry_artifacts_matches_by_slug_in_account_brief_path(self):
        registry_index = {"artifacts": [
            {"path": "output/account-intelligence/account-briefs/bbva.md", "artifactType": "account-brief",
             "employee": "account-intelligence", "contentHash": "sha256:x", "fileModifiedAt": "2026-08-02T00:00:00+00:00"},
            {"path": "output/sales-director/2026-08-02-sales-director-report.md", "artifactType": "daily-report",
             "employee": "sales-director", "contentHash": "sha256:y", "fileModifiedAt": "2026-08-02T00:00:00+00:00"},
        ]}
        matches = engine.find_registry_artifacts("BBVA", registry_index)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["path"], "output/account-intelligence/account-briefs/bbva.md")

    def test_find_registry_artifacts_matches_delivery_kit_directory_segment(self):
        registry_index = {"artifacts": [
            {"path": "output/delivery-intelligence/delivery-kits/bbva/kickoff-agenda.md",
             "artifactType": "delivery-kit-component", "employee": "delivery-intelligence",
             "contentHash": "sha256:z", "fileModifiedAt": "2026-08-02T00:00:00+00:00"},
        ]}
        matches = engine.find_registry_artifacts("BBVA", registry_index)
        self.assertEqual(len(matches), 1)

    def test_find_registry_artifacts_honest_empty_when_nothing_indexed_or_registry_absent(self):
        self.assertEqual(engine.find_registry_artifacts("BBVA", {"artifacts": []}), [])
        self.assertEqual(engine.find_registry_artifacts("BBVA", None), [])
        self.assertEqual(engine.find_registry_artifacts("BBVA", {}), [])

    def test_find_crm_entry_matches_despite_casing_and_whitespace(self):
        crm_data = {"companies": [{"companyName": "  BBVA  ", "existingRelationship": "prior client"}]}
        found = engine.find_crm_entry("BBVA", crm_data)
        self.assertIsNotNone(found)
        self.assertEqual(found["existingRelationship"], "prior client")

    def test_find_crm_entry_honest_when_no_match(self):
        crm_data = {"companies": [{"companyName": "Other Co"}]}
        self.assertIsNone(engine.find_crm_entry("BBVA", crm_data))

    def test_find_relationship_people_matches_via_company_field(self):
        feed = {"people": [
            {"person": "Jane Doe", "company": " bbva ", "healthScore": 80, "healthBand": "Strong"},
            {"person": "Other Person", "company": "Other Co", "healthScore": 40, "healthBand": "Cooling"},
        ]}
        people = engine.find_relationship_people("BBVA", feed)
        self.assertEqual(len(people), 1)
        self.assertEqual(people[0]["person"], "Jane Doe")

    def test_find_reverse_job_hunt_entry_uses_strategies_key(self):
        feed = {"strategies": [{"organisation": "BBVA", "entryPoint": "Warm introduction"}]}
        self.assertEqual(engine.find_reverse_job_hunt_entry("BBVA", feed)["entryPoint"], "Warm introduction")
        self.assertIsNone(engine.find_reverse_job_hunt_entry("Nonexistent", feed))

    def test_find_pipeline_entries_returns_all_matches(self):
        pipeline_data = {"pipeline": [
            {"organisation": "BBVA", "id": "rev-0001"},
            {"organisation": "BBVA", "id": "rev-0002"},
            {"organisation": "Other Co", "id": "rev-0003"},
        ]}
        entries = engine.find_pipeline_entries("BBVA", pipeline_data)
        self.assertEqual(len(entries), 2)

    def test_find_service_recommendations_joins_through_opportunity_schema(self):
        opportunity_schema = {"opportunities": [{"id": "opp-1", "organisation": "BBVA"}, {"id": "opp-2", "organisation": "Other Co"}]}
        service_recommendations = {
            "opp-1": {"opportunityId": "opp-1", "primaryService": "ADGL", "notApplicable": False},
            "opp-2": {"opportunityId": "opp-2", "primaryService": "GRC", "notApplicable": False},
        }
        recs = engine.find_service_recommendations("BBVA", opportunity_schema, service_recommendations)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["opportunityId"], "opp-1")

    def test_find_service_recommendations_excludes_not_applicable(self):
        opportunity_schema = {"opportunities": [{"id": "opp-1", "organisation": "BBVA"}]}
        service_recommendations = {"opp-1": {"opportunityId": "opp-1", "notApplicable": True}}
        self.assertEqual(engine.find_service_recommendations("BBVA", opportunity_schema, service_recommendations), [])

    def test_find_delivery_engagement_honest_when_no_log_entry(self):
        result = engine.find_delivery_engagement("BBVA", {"engagements": {}}, {"engagements": []})
        self.assertEqual(result["phase"], "Not started")
        self.assertEqual(result["noteCount"], 0)
        self.assertIsNone(result["kitPath"])

    def test_find_delivery_engagement_reflects_real_log_and_feed(self):
        delivery_log = {"engagements": {"BBVA": {"phase": "Discovery", "notes": [{"date": "2026-07-01", "note": "Kickoff held."}]}}}
        delivery_feed = {"engagements": [{"organisation": "BBVA", "kitPath": "AOS/output/delivery-intelligence/delivery-kits/bbva"}]}
        result = engine.find_delivery_engagement("BBVA", delivery_log, delivery_feed)
        self.assertEqual(result["phase"], "Discovery")
        self.assertEqual(result["noteCount"], 1)
        self.assertEqual(result["kitPath"], "AOS/output/delivery-intelligence/delivery-kits/bbva")


class BuildCompany360Tests(unittest.TestCase):
    def test_assembles_every_source_when_all_exist(self):
        entry = engine.build_company_360(
            "BBVA", PROFILE, {"briefs": [AI_ENTRY]},
            {"companies": [{"companyName": "BBVA", "existingRelationship": "prior client"}]},
            {"people": [{"person": "Jane Doe", "company": "BBVA", "healthScore": 80, "healthBand": "Strong"}]},
            {"strategies": [{"organisation": "BBVA", "entryPoint": "Warm introduction", "consultingPotentialEstimate": "High"}]},
            {"pipeline": [{"organisation": "BBVA", "id": "rev-0001", "stage": "won"}]},
            {"opportunities": [{"id": "opp-1", "organisation": "BBVA"}]},
            {"opp-1": {"opportunityId": "opp-1", "primaryService": "ADGL", "notApplicable": False}},
            {"engagements": {"BBVA": {"phase": "Kickoff", "notes": []}}},
            {"engagements": [{"organisation": "BBVA", "kitPath": "some/path"}]},
        )
        self.assertEqual(entry["organisation"], "BBVA")
        self.assertIsNotNone(entry["accountIntelligence"])
        self.assertIsNotNone(entry["crm"])
        self.assertEqual(len(entry["relationshipIntelligence"]), 1)
        self.assertIsNotNone(entry["reverseJobHunt"])
        self.assertEqual(len(entry["pipeline"]), 1)
        self.assertEqual(len(entry["serviceMapping"]), 1)
        self.assertEqual(entry["deliveryIntelligence"]["phase"], "Kickoff")

    def test_honest_gaps_when_nothing_else_exists(self):
        entry = engine.build_company_360(
            "New Co", dict(PROFILE, organisation="New Co"), {"briefs": []}, {"companies": []},
            {"people": []}, {"strategies": []}, {"pipeline": []}, {"opportunities": []}, {},
            {"engagements": {}}, {"engagements": []},
        )
        self.assertIsNone(entry["accountIntelligence"])
        self.assertIsNone(entry["crm"])
        self.assertEqual(entry["relationshipIntelligence"], [])
        self.assertIsNone(entry["reverseJobHunt"])
        self.assertEqual(entry["pipeline"], [])
        self.assertEqual(entry["serviceMapping"], [])
        self.assertEqual(entry["deliveryIntelligence"]["phase"], "Not started")

    def test_registry_index_defaults_to_none_existing_callers_are_unaffected(self):
        """Every existing call site in this file omits registry_index —
        this must keep working exactly as before (AOS Architecture
        Constitution: existing employees continue to function unchanged)."""
        entry = engine.build_company_360(
            "New Co", dict(PROFILE, organisation="New Co"), {"briefs": []}, {"companies": []},
            {"people": []}, {"strategies": []}, {"pipeline": []}, {"opportunities": []}, {},
            {"engagements": {}}, {"engagements": []},
        )
        self.assertEqual(entry["artifactRegistry"], [])

    def test_registry_index_populates_artifact_registry_when_provided(self):
        registry_index = {"artifacts": [
            {"path": "output/account-intelligence/account-briefs/bbva.md", "artifactType": "account-brief",
             "employee": "account-intelligence", "contentHash": "sha256:x", "fileModifiedAt": "2026-08-02T00:00:00+00:00"},
        ]}
        entry = engine.build_company_360(
            "BBVA", PROFILE, {"briefs": []}, {"companies": []}, {"people": []}, {"strategies": []},
            {"pipeline": []}, {"opportunities": []}, {}, {"engagements": {}}, {"engagements": []},
            registry_index=registry_index,
        )
        self.assertEqual(len(entry["artifactRegistry"]), 1)


class RenderMarkdownTests(unittest.TestCase):
    def test_never_averages_the_two_deal_size_estimates(self):
        entry = engine.build_company_360(
            "BBVA", PROFILE, {"briefs": [AI_ENTRY]}, {"companies": []}, {"people": []},
            {"strategies": [{"organisation": "BBVA", "consultingPotentialEstimate": "Medium-High", "entryPoint": "Conference"}]},
            {"pipeline": []}, {"opportunities": []}, {}, {"engagements": {}}, {"engagements": []},
        )
        markdown = engine.render_company_360_markdown(entry)
        self.assertIn("62", markdown)  # Account Intelligence's overallPriority, verbatim
        self.assertIn("Medium-High", markdown)  # Reverse Job Hunt's own estimate, verbatim
        self.assertIn("not the same figure", markdown)  # explicit non-reconciliation note

    def test_honest_gap_messages_for_missing_sources(self):
        entry = engine.build_company_360(
            "New Co", dict(PROFILE, organisation="New Co"), {"briefs": []}, {"companies": []},
            {"people": []}, {"strategies": []}, {"pipeline": []}, {"opportunities": []}, {},
            {"engagements": {}}, {"engagements": []},
        )
        markdown = engine.render_company_360_markdown(entry)
        self.assertIn("No brief on record yet", markdown)
        self.assertIn("No CRM record yet", markdown)
        self.assertIn("No individual contacts tracked yet", markdown)
        self.assertIn("No BD campaign strategy on record yet", markdown)
        self.assertIn("No pipeline entries yet", markdown)
        self.assertIn("No mapped opportunities yet", markdown)
        self.assertIn("No indexed artifacts on record", markdown)

    def test_renders_indexed_artifacts_when_present(self):
        entry = engine.build_company_360(
            "BBVA", PROFILE, {"briefs": []}, {"companies": []}, {"people": []}, {"strategies": []},
            {"pipeline": []}, {"opportunities": []}, {}, {"engagements": {}}, {"engagements": []},
            registry_index={"artifacts": [
                {"path": "output/account-intelligence/account-briefs/bbva.md", "artifactType": "account-brief",
                 "employee": "account-intelligence", "contentHash": "sha256:x", "fileModifiedAt": "2026-08-02T00:00:00+00:00"},
            ]},
        )
        markdown = engine.render_company_360_markdown(entry)
        self.assertIn("## Artifact Registry", markdown)
        self.assertIn("output/account-intelligence/account-briefs/bbva.md", markdown)
        self.assertIn("account-brief", markdown)


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_default_is_deep_copied_not_shared(self):
        first = engine.load_json(Path("/nonexistent/path.json"), {"organisations": {}})
        first["organisations"]["X"] = {"industry": "Test"}
        second = engine.load_json(Path("/nonexistent/path.json"), {"organisations": {}})
        self.assertEqual(second["organisations"], {})


class GenerateEndToEndTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)

        patches = [
            patch("company_360_engine.ORGANISATION_PROFILES_PATH", self.tmp_path / "organisation-profiles.json"),
            patch("company_360_engine.OPPORTUNITY_SCHEMA_PATH", self.tmp_path / "opps.json"),
            patch("company_360_engine.ACCOUNT_INTELLIGENCE_FEED_PATH", self.tmp_path / "ai_feed.json"),
            patch("company_360_engine.CRM_PATH", self.tmp_path / "crm.json"),
            patch("company_360_engine.RELATIONSHIP_PROFILES_PATH", self.tmp_path / "rel_profiles.json"),
            patch("company_360_engine.RELATIONSHIP_FEED_PATH", self.tmp_path / "rel_feed.json"),
            patch("company_360_engine.REVERSE_JOB_HUNT_FEED_PATH", self.tmp_path / "rjh_feed.json"),
            patch("company_360_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"),
            patch("company_360_engine.SERVICE_RECOMMENDATIONS_PATH", self.tmp_path / "service_recs.json"),
            patch("company_360_engine.DELIVERY_LOG_PATH", self.tmp_path / "delivery-log.json"),
            patch("company_360_engine.DELIVERY_INTELLIGENCE_FEED_PATH", self.tmp_path / "delivery_feed.json"),
            patch("company_360_engine.ARTIFACT_REGISTRY_INDEX_PATH", self.tmp_path / "artifact-index.json"),
            patch("company_360_engine.PROFILES_DIR", self.tmp_path / "output" / "company-profiles"),
            patch("company_360_engine.FEED_PATH", self.tmp_path / "output" / "company-360-feed.json"),
            patch("company_360_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_no_organisations_writes_nothing(self):
        engine.save_json(self.tmp_path / "organisation-profiles.json", {"organisations": {}})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        self.assertFalse((self.tmp_path / "output" / "company-360-feed.json").exists())

    def test_full_run_writes_feed_and_profile(self):
        engine.save_json(self.tmp_path / "organisation-profiles.json", {"organisations": {"BBVA": PROFILE}})
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": []})
        engine.save_json(self.tmp_path / "ai_feed.json", {"briefs": [AI_ENTRY]})
        engine.save_json(self.tmp_path / "crm.json", {"companies": []})
        engine.save_json(self.tmp_path / "rel_feed.json", {"people": []})
        engine.save_json(self.tmp_path / "rjh_feed.json", {"strategies": []})
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": []})
        engine.save_json(self.tmp_path / "service_recs.json", {"recommendations": {}})
        engine.save_json(self.tmp_path / "delivery-log.json", {"engagements": {}})
        engine.save_json(self.tmp_path / "delivery_feed.json", {"engagements": []})

        exit_code = generate.main()
        self.assertEqual(exit_code, 0)

        feed = engine.load_json(self.tmp_path / "output" / "company-360-feed.json")
        self.assertEqual(len(feed["companies"]), 1)
        entry = feed["companies"][0]
        self.assertEqual(entry["organisation"], "BBVA")

        profile_path = self.tmp_path / entry["profilePath"]
        self.assertTrue(profile_path.exists())
        self.assertIn("BBVA", profile_path.read_text(encoding="utf-8"))

    def test_rerun_regenerates_the_profile_no_processed_index_needed(self):
        """Unlike Sales Director/Delivery Intelligence, nothing here is
        founder-edited, so a re-run should simply overwrite with the
        latest joined data every time."""
        engine.save_json(self.tmp_path / "organisation-profiles.json", {"organisations": {"BBVA": PROFILE}})
        for path, default in [
            ("opps.json", {"opportunities": []}), ("ai_feed.json", {"briefs": []}),
            ("crm.json", {"companies": []}), ("rel_feed.json", {"people": []}),
            ("rjh_feed.json", {"strategies": []}), ("pipeline.json", {"pipeline": []}),
            ("service_recs.json", {"recommendations": {}}), ("delivery-log.json", {"engagements": {}}),
            ("delivery_feed.json", {"engagements": []}),
        ]:
            engine.save_json(self.tmp_path / path, default)

        generate.main()
        first_profile = (self.tmp_path / "output" / "company-profiles" / "bbva.md").read_text(encoding="utf-8")
        self.assertIn("No brief on record yet", first_profile)

        engine.save_json(self.tmp_path / "ai_feed.json", {"briefs": [AI_ENTRY]})
        generate.main()
        second_profile = (self.tmp_path / "output" / "company-profiles" / "bbva.md").read_text(encoding="utf-8")
        self.assertNotIn("No brief on record yet", second_profile)
        self.assertIn("BBVA is scaling AI adoption", second_profile)


if __name__ == "__main__":
    unittest.main()
