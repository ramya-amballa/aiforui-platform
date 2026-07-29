#!/usr/bin/env python3
"""
Unit and integration tests for Delivery Intelligence (AOS Sprint 17).

Every test uses hand-built fixtures for pipeline/opportunity/Account
Intelligence/service-mapping data; the real templates/delivery/ files
and the real practitioner-bank.json (for ADGL/OPERA phase names) are
used as-is, the same "reuse the real shared resource" pattern every
other AOS test suite already uses for rate-card.json/practitioner-bank.json.

Run with:
    python3 -m unittest tests.test_delivery_intelligence_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import delivery_intelligence_engine as engine  # noqa: E402
import generate  # noqa: E402

WON_ENTRY = {
    "id": "rev-0001", "type": "Consulting Project", "title": "AI Governance Advisory",
    "organisation": "BBVA", "sourceRef": "opp-0001", "expectedRevenue": "USD 45,000",
    "probabilityOfSuccess": 8, "effortRequired": 5, "strategicValue": 8, "score": 78,
    "band": "Priority", "stage": "won", "owner": "Ramya", "lastTouch": "2026-07-01",
    "nextAction": "Kickoff", "nextActionDue": "2026-08-01", "expectedCloseDate": "2026-07",
}

OPPORTUNITY = {
    "id": "opp-0001", "title": "AI Governance Advisory", "organisation": "BBVA",
    "domainTags": ["ADGL", "AI Governance"],
}

AI_ENTRY = {
    "organisation": "BBVA",
    "companyProfile": {"industry": "Banking", "regulatoryEnvironment": "EU AI Act, GDPR"},
    "decisionMakerTitles": ["Chief Risk Officer"],
    "governanceRisks": [{"risk": "Human oversight", "why": "Live systems need a human-in-the-loop point."}],
    "serviceFit": [{"service": "AI Deployment Governance (ADGL)", "confidence": "High"}],
}

SERVICE_RECOMMENDATION = {
    "notApplicable": False, "primaryService": "AI Deployment Governance (ADGL)",
    "recommendedEngagementType": "Consulting Project", "estimatedProjectSize": "Medium",
}

DORA_OPPORTUNITY = dict(OPPORTUNITY, id="opp-0002", domainTags=["DORA", "Third-Party Risk"])

FRAMEWORK_CONFIG = {
    "frameworkPriority": ["DORA", "EU AI Act", "Third-Party Risk", "AI Deployment Governance (ADGL)"],
    "frameworks": {
        "DORA": {
            "frameworkLabel": "DORA (Digital Operational Resilience Act)",
            "discoveryQuestions": ["Which ICT third parties are in scope for DORA resilience testing?"],
            "riskSeedRisks": [{"risk": "ICT third-party concentration risk", "why": "DORA holds the entity accountable regardless of vendor status."}],
            "reportingNote": "Reporting should track ongoing ICT third-party monitoring status.",
        },
        "Third-Party Risk": {
            "frameworkLabel": "Third-Party Risk",
            "discoveryQuestions": ["How are vendors segmented by criticality today?"],
            "riskSeedRisks": [{"risk": "Post-onboarding ownership gap", "why": "Risk materialises after signature, not at onboarding."}],
            "reportingNote": "Reporting should track vendor monitoring cadence.",
        },
        "AI Deployment Governance (ADGL)": {
            "frameworkLabel": "AI Deployment Governance (ADGL) — general",
            "discoveryQuestions": ["Is there a named owner for AI governance decisions today?"],
            "riskSeedRisks": [{"risk": "No consistent risk evaluation across AI use cases", "why": "Inconsistent scrutiny without one risk model."}],
            "reportingNote": "Reporting should track named ownership and approval gates.",
        },
    },
}


class WonEngagementsTests(unittest.TestCase):
    def test_filters_to_won_stage_only(self):
        pipeline = {"pipeline": [WON_ENTRY, dict(WON_ENTRY, organisation="Other Co", stage="identified")]}
        result = engine.won_engagements(pipeline)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["organisation"], "BBVA")

    def test_empty_pipeline_is_honest(self):
        self.assertEqual(engine.won_engagements({"pipeline": []}), [])


class FinderTests(unittest.TestCase):
    def test_find_opportunity_matches_by_id(self):
        schema = {"opportunities": [OPPORTUNITY]}
        self.assertEqual(engine.find_opportunity("opp-0001", schema)["organisation"], "BBVA")
        self.assertIsNone(engine.find_opportunity(None, schema))
        self.assertIsNone(engine.find_opportunity("nonexistent", schema))

    def test_find_account_intelligence_entry(self):
        feed = {"briefs": [AI_ENTRY]}
        self.assertEqual(engine.find_account_intelligence_entry("BBVA", feed)["organisation"], "BBVA")
        self.assertIsNone(engine.find_account_intelligence_entry("Nonexistent", feed))

    def test_find_service_recommendation(self):
        recs = {"opp-0001": SERVICE_RECOMMENDATION}
        self.assertEqual(engine.find_service_recommendation("opp-0001", recs), SERVICE_RECOMMENDATION)
        self.assertIsNone(engine.find_service_recommendation(None, recs))
        self.assertIsNone(engine.find_service_recommendation("opp-9999", recs))


class EngagementPhaseTests(unittest.TestCase):
    def test_not_started_when_no_log_entry(self):
        phase, notes = engine.engagement_phase("BBVA", {"engagements": {}})
        self.assertEqual(phase, "Not started")
        self.assertEqual(notes, [])

    def test_reflects_real_founder_maintained_phase(self):
        log = {"engagements": {"BBVA": {"phase": "Discovery", "notes": [{"date": "2026-07-01", "note": "Kickoff held."}]}}}
        phase, notes = engine.engagement_phase("BBVA", log)
        self.assertEqual(phase, "Discovery")
        self.assertEqual(len(notes), 1)


class PlaceholderAssemblyTests(unittest.TestCase):
    def test_governance_risks_list_real_and_honest(self):
        self.assertIn("Human oversight", engine.governance_risks_list(AI_ENTRY))
        self.assertIn("Not enough signal yet", engine.governance_risks_list(None))
        self.assertIn("Not enough signal yet", engine.governance_risks_list({"governanceRisks": []}))

    def test_risk_register_rows_pre_populates_real_risks(self):
        rows = engine.risk_register_rows(AI_ENTRY)
        self.assertIn("Human oversight", rows)
        self.assertIn("Open", rows)
        empty_rows = engine.risk_register_rows(None)
        self.assertIn("Not enough signal yet", empty_rows)

    def test_primary_service_prefers_service_mapping_over_account_intelligence(self):
        self.assertEqual(engine.primary_service(SERVICE_RECOMMENDATION, AI_ENTRY), "AI Deployment Governance (ADGL)")

    def test_primary_service_falls_back_to_account_intelligence(self):
        self.assertEqual(engine.primary_service(None, AI_ENTRY), "AI Deployment Governance (ADGL)")

    def test_primary_service_honest_when_neither_available(self):
        self.assertEqual(engine.primary_service(None, None), "Not specified")

    def test_decision_maker_titles_never_invents_a_name(self):
        text = engine.decision_maker_titles_text(AI_ENTRY)
        self.assertEqual(text, "Chief Risk Officer")
        self.assertNotIn("Jane", text)
        self.assertEqual(engine.decision_maker_titles_text(None), "Not specified")

    def test_build_placeholders_assembles_real_data(self):
        bank = {"adglPhases": ["Discover", "Assess", "Govern", "Deploy", "Operate"],
                "operaPhases": ["Opportunity", "People", "Evaluation", "Response", "Assurance"]}
        placeholders = engine.build_placeholders(WON_ENTRY, OPPORTUNITY, AI_ENTRY, SERVICE_RECOMMENDATION, bank, FRAMEWORK_CONFIG)
        self.assertEqual(placeholders["{{CLIENT_NAME}}"], "BBVA")
        self.assertEqual(placeholders["{{INDUSTRY}}"], "Banking")
        self.assertIn("Discover", placeholders["{{ADGL_PHASES_LIST}}"])
        self.assertIn("Opportunity", placeholders["{{OPERA_PHASES_LIST}}"])
        # OPPORTUNITY has no DORA/EU AI Act/Third-Party Risk tag -> ADGL default
        self.assertEqual(placeholders["{{REGULATORY_FRAMEWORK_LABEL}}"], "AI Deployment Governance (ADGL) — general")

    def test_build_placeholders_honest_defaults_without_framework_config(self):
        bank = {"adglPhases": [], "operaPhases": []}
        placeholders = engine.build_placeholders(WON_ENTRY, OPPORTUNITY, AI_ENTRY, SERVICE_RECOMMENDATION, bank)
        self.assertIn("Not enough signal yet", placeholders["{{REGULATORY_FRAMEWORK_DISCOVERY_QUESTIONS}}"])
        self.assertIn("Not enough signal yet", placeholders["{{REGULATORY_FRAMEWORK_SEED_RISKS}}"])


class RegulatoryFrameworkTests(unittest.TestCase):
    """AOS Sprint 23 — Engagement Templates. select_regulatory_framework()
    reuses the opportunity's own real domainTags — the identical field
    service-mapping's determine_proposal_template() already selects a
    proposal template from — never a second, independent detection."""

    def test_selects_the_higher_priority_tag_when_two_match(self):
        # DORA_OPPORTUNITY carries both DORA and Third-Party Risk tags;
        # frameworkPriority lists DORA first.
        self.assertEqual(engine.select_regulatory_framework(DORA_OPPORTUNITY, FRAMEWORK_CONFIG), "DORA")

    def test_falls_through_priority_order_to_the_next_match(self):
        opp = dict(OPPORTUNITY, domainTags=["Third-Party Risk"])
        self.assertEqual(engine.select_regulatory_framework(opp, FRAMEWORK_CONFIG), "Third-Party Risk")

    def test_none_when_no_recognised_tag(self):
        opp = dict(OPPORTUNITY, domainTags=["GRC"])
        self.assertIsNone(engine.select_regulatory_framework(opp, FRAMEWORK_CONFIG))

    def test_label_falls_back_to_general_adgl_when_no_match(self):
        self.assertEqual(engine.regulatory_framework_label(None, FRAMEWORK_CONFIG), "AI Deployment Governance (ADGL) — general")

    def test_discovery_questions_are_real_and_framework_specific(self):
        questions = engine.regulatory_framework_discovery_questions("DORA", FRAMEWORK_CONFIG)
        self.assertIn("ICT third parties", questions)

    def test_seed_risks_are_real_and_framework_specific(self):
        risks = engine.regulatory_framework_seed_risks("DORA", FRAMEWORK_CONFIG)
        self.assertIn("ICT third-party concentration risk", risks)

    def test_reporting_note_is_real_and_framework_specific(self):
        note = engine.regulatory_framework_reporting_note("DORA", FRAMEWORK_CONFIG)
        self.assertIn("ICT third-party monitoring", note)

    def test_iso_42001_is_a_real_entry_in_the_live_annex_file(self):
        """AOS Sprint 24 — Quality Elevation added ISO 42001 as the
        fourth core framework; confirms it's wired the same way the
        other six frameworks already are, using the real, live
        annexes file (not a test fixture)."""
        framework_config = engine.load_json(engine.REGULATORY_FRAMEWORK_ANNEXES_PATH, {})
        iso_opportunity = dict(OPPORTUNITY, domainTags=["ISO 42001"])
        selected = engine.select_regulatory_framework(iso_opportunity, framework_config)
        self.assertEqual(selected, "ISO 42001")
        questions = engine.regulatory_framework_discovery_questions(selected, framework_config)
        self.assertIn("Annex A", questions)


class RenderArtifactTests(unittest.TestCase):
    """Uses the real templates/delivery/ files — the shared, static IP
    asset every engagement's kit is built from."""

    def setUp(self):
        self.bank = engine.load_json(engine.PRACTITIONER_BANK_PATH, {})
        self.placeholders = engine.build_placeholders(WON_ENTRY, OPPORTUNITY, AI_ENTRY, SERVICE_RECOMMENDATION, self.bank, FRAMEWORK_CONFIG)
        self.dora_placeholders = engine.build_placeholders(WON_ENTRY, DORA_OPPORTUNITY, AI_ENTRY, SERVICE_RECOMMENDATION, self.bank, FRAMEWORK_CONFIG)

    def test_kickoff_agenda_fills_real_placeholders(self):
        text = engine.render_artifact("kickoff-agenda-template.md", self.placeholders)
        self.assertIn("BBVA", text)
        self.assertIn("Chief Risk Officer", text)
        self.assertIn("Human oversight", text)
        self.assertNotIn("{{CLIENT_NAME}}", text)

    def test_unfilled_placeholders_remain_as_founder_prompts(self):
        text = engine.render_artifact("kickoff-agenda-template.md", self.placeholders)
        self.assertIn("{{ATTENDEES", text)  # never invented — left for the founder

    def test_all_ten_artifact_templates_render_without_error(self):
        for template_filename, suffix, _label in engine.ARTIFACT_SPECS:
            text = engine.render_artifact(template_filename, self.placeholders)
            self.assertIn("BBVA", text, f"{suffix} did not fill in the client name")

    def test_discovery_questionnaire_carries_the_dora_annex_for_a_dora_opportunity(self):
        text = engine.render_artifact("discovery-questionnaire-template.md", self.dora_placeholders)
        self.assertIn("DORA (Digital Operational Resilience Act)", text)
        self.assertIn("ICT third parties", text)
        self.assertNotIn("{{REGULATORY_FRAMEWORK", text)

    def test_discovery_questionnaire_carries_the_general_annex_for_a_generic_opportunity(self):
        text = engine.render_artifact("discovery-questionnaire-template.md", self.placeholders)
        self.assertIn("AI Deployment Governance (ADGL) — general", text)
        self.assertNotIn("DORA", text)

    def test_risk_register_carries_the_framework_seed_risks(self):
        text = engine.render_artifact("risk-register-template.md", self.dora_placeholders)
        self.assertIn("ICT third-party concentration risk", text)

    def test_steering_committee_pack_carries_the_reporting_note(self):
        text = engine.render_artifact("steering-committee-pack-template.md", self.dora_placeholders)
        self.assertIn("ICT third-party monitoring status", text)


class BuildDeliveryKitTests(unittest.TestCase):
    def test_builds_all_ten_artifacts_and_a_feed_entry(self):
        bank = engine.load_json(engine.PRACTITIONER_BANK_PATH, {})
        artifacts, feed_entry = engine.build_delivery_kit(
            WON_ENTRY, OPPORTUNITY, AI_ENTRY, SERVICE_RECOMMENDATION, bank, {"engagements": {}}, FRAMEWORK_CONFIG)
        self.assertEqual(len(artifacts), 10)
        self.assertEqual(feed_entry["organisation"], "BBVA")
        self.assertEqual(feed_entry["phase"], "Not started")
        self.assertEqual(feed_entry["regulatoryFramework"], "AI Deployment Governance (ADGL) — general")
        self.assertIsNone(feed_entry["kitPath"])  # generate.py fills this in


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_default_is_deep_copied_not_shared(self):
        first = engine.load_json(Path("/nonexistent/path.json"), {"engagements": {}})
        first["engagements"]["X"] = {"phase": "Kickoff"}
        second = engine.load_json(Path("/nonexistent/path.json"), {"engagements": {}})
        self.assertEqual(second["engagements"], {})


class GenerateEndToEndTests(unittest.TestCase):
    """Runs the real generate.main() over a mocked won engagement,
    confirming a real kit is written once, never overwritten on a
    re-run — the founder is expected to edit these files by hand."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)

        patches = [
            patch("delivery_intelligence_engine.PIPELINE_PATH", self.tmp_path / "pipeline.json"),
            patch("delivery_intelligence_engine.OPPORTUNITY_SCHEMA_PATH", self.tmp_path / "opps.json"),
            patch("delivery_intelligence_engine.ACCOUNT_INTELLIGENCE_FEED_PATH", self.tmp_path / "ai_feed.json"),
            patch("delivery_intelligence_engine.SERVICE_RECOMMENDATIONS_PATH", self.tmp_path / "service_recs.json"),
            patch("delivery_intelligence_engine.DELIVERY_LOG_PATH", self.tmp_path / "delivery-log.json"),
            patch("delivery_intelligence_engine.KITS_DIR", self.tmp_path / "output" / "delivery-kits"),
            patch("delivery_intelligence_engine.FEED_PATH", self.tmp_path / "output" / "delivery-intelligence-feed.json"),
            patch("delivery_intelligence_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def _seed(self, pipeline_entries):
        engine.save_json(self.tmp_path / "pipeline.json", {"pipeline": pipeline_entries})
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": [OPPORTUNITY]})
        engine.save_json(self.tmp_path / "ai_feed.json", {"briefs": [AI_ENTRY]})
        engine.save_json(self.tmp_path / "service_recs.json", {"recommendations": {"opp-0001": SERVICE_RECOMMENDATION}})

    def test_no_won_engagements_writes_nothing(self):
        self._seed([dict(WON_ENTRY, stage="identified")])
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        self.assertFalse((self.tmp_path / "output" / "delivery-intelligence-feed.json").exists())

    def test_won_engagement_generates_a_full_kit(self):
        self._seed([WON_ENTRY])
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)

        feed = engine.load_json(self.tmp_path / "output" / "delivery-intelligence-feed.json")
        self.assertEqual(len(feed["engagements"]), 1)
        entry = feed["engagements"][0]
        self.assertEqual(entry["organisation"], "BBVA")
        self.assertEqual(len(entry["artifacts"]), 10)
        for suffix, path in entry["artifacts"].items():
            full_path = self.tmp_path / path
            self.assertTrue(full_path.exists(), f"{suffix} was not written to disk")
            self.assertIn("BBVA", full_path.read_text(encoding="utf-8"))

    def test_rerun_never_overwrites_a_founder_edited_artifact(self):
        self._seed([WON_ENTRY])
        generate.main()

        processed = engine.load_json(self.tmp_path / "processed-index.json")
        kickoff_path = self.tmp_path / processed["processed"]["BBVA"]["artifacts"]["kickoff-agenda"]
        kickoff_path.write_text("MANUALLY EDITED BY THE FOUNDER — REAL ATTENDEES LOGGED HERE", encoding="utf-8")

        generate.main()  # re-run

        self.assertEqual(kickoff_path.read_text(encoding="utf-8"), "MANUALLY EDITED BY THE FOUNDER — REAL ATTENDEES LOGGED HERE")

    def test_backfill_only_adds_missing_artifact_never_touches_existing_ones(self):
        self._seed([WON_ENTRY])
        generate.main()

        processed = engine.load_json(self.tmp_path / "processed-index.json")
        record = processed["processed"]["BBVA"]
        edited_path = self.tmp_path / record["artifacts"]["kickoff-agenda"]
        edited_path.write_text("REAL FOUNDER EDITS", encoding="utf-8")

        # Simulate a processed engagement missing one artifact (as if a
        # new ARTIFACT_SPECS entry were added after this kit was
        # generated) by deleting one file on disk without updating the
        # index — missing_artifacts() must detect this via the real
        # file's absence, not just the index's own bookkeeping.
        missing_path = self.tmp_path / record["artifacts"]["risk-register"]
        missing_path.unlink()

        generate.main()

        self.assertEqual(edited_path.read_text(encoding="utf-8"), "REAL FOUNDER EDITS")
        self.assertTrue(missing_path.exists())

    def test_engagement_phase_refreshes_from_delivery_log_every_run(self):
        self._seed([WON_ENTRY])
        generate.main()
        engine.save_json(self.tmp_path / "delivery-log.json", {"engagements": {"BBVA": {"phase": "Discovery", "notes": []}}})
        generate.main()

        feed = engine.load_json(self.tmp_path / "output" / "delivery-intelligence-feed.json")
        self.assertEqual(feed["engagements"][0]["phase"], "Discovery")


if __name__ == "__main__":
    unittest.main()
