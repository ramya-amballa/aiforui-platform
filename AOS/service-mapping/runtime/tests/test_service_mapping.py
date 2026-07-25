#!/usr/bin/env python3
"""
Unit tests for the Service Mapping Engine's decision logic — every
Primary Service rule branch, the engagement-type overrides, project
size (both the real-revenue path and the heuristic fallback), template
mapping, and the three excluded classifications. Calls generate.py's
pure functions directly with fixture opportunities; never touches a
real AOS data file.

Run with:
    python3 -m unittest tests.test_service_mapping -v   (from runtime/)
"""

import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import generate  # noqa: E402

CATALOGUE = generate.load_json(RUNTIME_DIR / "config" / "service-catalogue.json")


def opp(**kwargs):
    base = {
        "id": "opp-test", "title": "Test Opportunity", "organisation": "Test Org",
        "description": "", "domainTags": [], "scores": {"expectedRevenue": 5, "probabilityOfWinning": 5},
        "scopedEngagement": False, "classification": "Apply", "sourceCategory": "Marketplace",
    }
    base.update(kwargs)
    return base


class PrimaryServiceTests(unittest.TestCase):
    def test_fractional_keyword(self):
        service, reason = generate.determine_primary_service(
            opp(title="Fractional AI Governance Advisor"), CATALOGUE)
        self.assertEqual(service, "Fractional AI Governance Lead")

    def test_fractional_domain_tag(self):
        service, _ = generate.determine_primary_service(
            opp(domainTags=["Fractional Advisory"]), CATALOGUE)
        self.assertEqual(service, "Fractional AI Governance Lead")

    def test_adgl_domain_tag(self):
        service, _ = generate.determine_primary_service(opp(domainTags=["ADGL"]), CATALOGUE)
        self.assertEqual(service, "AI Deployment Governance (ADGL)")

    def test_third_party_risk(self):
        service, _ = generate.determine_primary_service(opp(domainTags=["Third-Party Risk"]), CATALOGUE)
        self.assertEqual(service, "AI Third-Party Risk Review")

    def test_regulatory_scoped_gives_control_framework(self):
        service, _ = generate.determine_primary_service(
            opp(domainTags=["DORA"], scopedEngagement=True), CATALOGUE)
        self.assertEqual(service, "AI Policy & Control Framework")

    def test_regulatory_unscoped_gives_readiness_assessment(self):
        service, _ = generate.determine_primary_service(
            opp(domainTags=["EU AI Act"], scopedEngagement=False), CATALOGUE)
        self.assertEqual(service, "AI Readiness Assessment")

    def test_grc_gives_operating_model(self):
        service, _ = generate.determine_primary_service(opp(domainTags=["GRC"]), CATALOGUE)
        self.assertEqual(service, "AI Governance Operating Model")

    def test_security_governance_gives_risk_assessment(self):
        service, _ = generate.determine_primary_service(opp(domainTags=["Security Governance"]), CATALOGUE)
        self.assertEqual(service, "AI Risk Assessment")

    def test_ai_governance_scoped_gives_responsible_ai(self):
        service, _ = generate.determine_primary_service(
            opp(domainTags=["AI Governance"], scopedEngagement=True), CATALOGUE)
        self.assertEqual(service, "Responsible AI Implementation")

    def test_ai_governance_unscoped_gives_advisory(self):
        service, _ = generate.determine_primary_service(
            opp(domainTags=["AI Governance"], scopedEngagement=False), CATALOGUE)
        self.assertEqual(service, "AI Governance Advisory")

    def test_consulting_channel_gives_advisory(self):
        service, _ = generate.determine_primary_service(
            opp(domainTags=[], sourceCategory="Consulting Channel"), CATALOGUE)
        self.assertEqual(service, "AI Governance Advisory")

    def test_workshop_keyword_gives_executive_workshop(self):
        service, _ = generate.determine_primary_service(
            opp(domainTags=[], title="Board Workshop Request"), CATALOGUE)
        self.assertEqual(service, "Executive Workshop")

    def test_no_signal_falls_back_to_readiness_assessment(self):
        service, _ = generate.determine_primary_service(opp(domainTags=[]), CATALOGUE)
        self.assertEqual(service, "AI Readiness Assessment")

    def test_fractional_checked_before_adgl(self):
        # Fractional Advisory tag alongside ADGL — fractional wins,
        # since engagement shape is checked before domain specificity.
        service, _ = generate.determine_primary_service(
            opp(domainTags=["ADGL", "Fractional Advisory"]), CATALOGUE)
        self.assertEqual(service, "Fractional AI Governance Lead")


class EngagementTypeTests(unittest.TestCase):
    def test_active_client_overrides_everything(self):
        crm_entry = {"existingRelationship": "active client"}
        etype, _ = generate.determine_engagement_type(
            opp(scopedEngagement=True), "AI Deployment Governance (ADGL)", crm_entry, CATALOGUE)
        self.assertEqual(etype, "Retainer")

    def test_fractional_primary_gives_fractional_consulting(self):
        etype, _ = generate.determine_engagement_type(opp(), "Fractional AI Governance Lead", None, CATALOGUE)
        self.assertEqual(etype, "Fractional consulting")

    def test_executive_workshop_training_keyword_gives_training(self):
        etype, _ = generate.determine_engagement_type(
            opp(title="Staff training enablement session"), "Executive Workshop", None, CATALOGUE)
        self.assertEqual(etype, "Training")

    def test_executive_workshop_no_training_keyword_gives_discovery_workshop(self):
        etype, _ = generate.determine_engagement_type(
            opp(title="Board Workshop"), "Executive Workshop", None, CATALOGUE)
        self.assertEqual(etype, "Discovery workshop")

    def test_readiness_assessment_gives_discovery_workshop(self):
        etype, _ = generate.determine_engagement_type(opp(), "AI Readiness Assessment", None, CATALOGUE)
        self.assertEqual(etype, "Discovery workshop")

    def test_scoped_gives_fixed_price(self):
        etype, _ = generate.determine_engagement_type(
            opp(scopedEngagement=True), "AI Governance Operating Model", None, CATALOGUE)
        self.assertEqual(etype, "Fixed-price project")

    def test_relationship_building_gives_advisory(self):
        etype, _ = generate.determine_engagement_type(
            opp(classification="Relationship Building"), "AI Governance Advisory", None, CATALOGUE)
        self.assertEqual(etype, "Advisory engagement")

    def test_default_gives_advisory(self):
        etype, _ = generate.determine_engagement_type(opp(), "AI Governance Advisory", None, CATALOGUE)
        self.assertEqual(etype, "Advisory engagement")


class ProjectSizeTests(unittest.TestCase):
    def test_real_pipeline_revenue_small(self):
        pipeline_entry = {"expectedRevenue": "USD 3,000"}
        size, basis = generate.determine_project_size(
            opp(), "AI Deployment Governance (ADGL)", pipeline_entry, CATALOGUE)
        self.assertEqual(size, "Small")
        self.assertEqual(basis, "pipeline-revenue")

    def test_real_pipeline_revenue_enterprise(self):
        pipeline_entry = {"expectedRevenue": "USD 150,000"}
        size, basis = generate.determine_project_size(
            opp(), "Executive Workshop", pipeline_entry, CATALOGUE)
        self.assertEqual(size, "Enterprise")
        self.assertEqual(basis, "pipeline-revenue")

    def test_heuristic_default_no_adjustment(self):
        size, basis = generate.determine_project_size(
            opp(scores={"expectedRevenue": 5}), "AI Risk Assessment", None, CATALOGUE)
        self.assertEqual(size, "Medium")
        self.assertEqual(basis, "heuristic-estimate")

    def test_heuristic_bumped_up_by_high_revenue_score(self):
        size, basis = generate.determine_project_size(
            opp(scores={"expectedRevenue": 9}), "AI Risk Assessment", None, CATALOGUE)
        self.assertEqual(size, "Large")

    def test_heuristic_bumped_down_by_low_revenue_score(self):
        size, basis = generate.determine_project_size(
            opp(scores={"expectedRevenue": 1}), "AI Risk Assessment", None, CATALOGUE)
        self.assertEqual(size, "Small")

    def test_heuristic_capped_at_enterprise(self):
        size, _ = generate.determine_project_size(
            opp(scores={"expectedRevenue": 10}), "Fractional AI Governance Lead", None, CATALOGUE)
        self.assertEqual(size, "Enterprise")

    def test_heuristic_capped_at_small(self):
        size, _ = generate.determine_project_size(
            opp(scores={"expectedRevenue": 0}), "Executive Workshop", None, CATALOGUE)
        self.assertEqual(size, "Small")

    def test_unparseable_pipeline_revenue_falls_back_to_heuristic(self):
        pipeline_entry = {"expectedRevenue": "Not yet estimated"}
        size, basis = generate.determine_project_size(
            opp(scores={"expectedRevenue": 5}), "AI Risk Assessment", pipeline_entry, CATALOGUE)
        self.assertEqual(basis, "heuristic-estimate")
        self.assertEqual(size, "Medium")


class ProposalTemplateTests(unittest.TestCase):
    def test_dora_domain_tag_overrides_primary_service(self):
        template = generate.determine_proposal_template(
            opp(domainTags=["DORA"]), "AI Policy & Control Framework", CATALOGUE)
        self.assertEqual(template, "dora-proposal-template.md")

    def test_eu_ai_act_domain_tag_overrides(self):
        template = generate.determine_proposal_template(
            opp(domainTags=["EU AI Act"]), "AI Readiness Assessment", CATALOGUE)
        self.assertEqual(template, "eu-ai-act-proposal-template.md")

    def test_primary_service_default_when_no_domain_override(self):
        template = generate.determine_proposal_template(
            opp(domainTags=["ADGL"]), "AI Deployment Governance (ADGL)", CATALOGUE)
        self.assertEqual(template, "ai-governance-proposal-template.md")

    def test_fractional_primary_service_template(self):
        template = generate.determine_proposal_template(
            opp(domainTags=[]), "Fractional AI Governance Lead", CATALOGUE)
        self.assertEqual(template, "fractional-advisory-proposal-template.md")


class SecondaryAndCrossSellTests(unittest.TestCase):
    def test_adgl_secondary_chain_matches_founders_example(self):
        chain = generate.determine_secondary_services("AI Deployment Governance (ADGL)", CATALOGUE)
        self.assertEqual(chain, ["AI Governance Operating Model", "AI Control Library", "Fractional Governance Support"])

    def test_cross_sell_includes_complement_and_real_products(self):
        bank_products = [
            {"title": "The ADGL Methodology", "domainTags": ["ADGL", "AI Deployment Governance"]},
            {"title": "Unrelated Product", "domainTags": ["GRC"]},
        ]
        cross_sell = generate.determine_cross_sell(
            opp(domainTags=["ADGL"]), "AI Deployment Governance (ADGL)", bank_products, CATALOGUE)
        self.assertIn("Executive Workshop", cross_sell)  # the configured complement
        self.assertIn("The ADGL Methodology", cross_sell)
        self.assertNotIn("Unrelated Product", cross_sell)


class ExcludedClassificationTests(unittest.TestCase):
    def test_ignore_is_not_applicable(self):
        entry = generate.not_applicable_entry(opp(classification="Ignore"), "reason")
        self.assertTrue(entry["notApplicable"])
        self.assertIsNone(entry["primaryService"])

    def test_map_opportunity_full_pipeline_matches_worked_example(self):
        # The exact worked example from service-mapping-model.md.
        opportunity = opp(
            id="opp-worked-example", domainTags=["ADGL", "AI Deployment Governance"],
            scopedEngagement=True, classification="Immediate Proposal",
            scores={"expectedRevenue": 9, "probabilityOfWinning": 7},
        )
        entry = generate.map_opportunity(opportunity, None, None, [], CATALOGUE)
        self.assertEqual(entry["primaryService"], "AI Deployment Governance (ADGL)")
        self.assertEqual(entry["secondaryServices"],
                          ["AI Governance Operating Model", "AI Control Library", "Fractional Governance Support"])
        self.assertEqual(entry["recommendedEngagementType"], "Fixed-price project")
        self.assertEqual(entry["estimatedProjectSize"], "Enterprise")
        self.assertEqual(entry["projectSizeBasis"], "heuristic-estimate")
        self.assertEqual(entry["recommendedProposalTemplate"], "ai-governance-proposal-template.md")


if __name__ == "__main__":
    unittest.main()
