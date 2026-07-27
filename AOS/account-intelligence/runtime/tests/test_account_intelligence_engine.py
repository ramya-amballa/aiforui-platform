#!/usr/bin/env python3
"""
Unit and integration tests for Account Intelligence (AOS Sprint 8):
each of the ten section builders in account_intelligence_engine.py,
plus generate.py's end-to-end run over a sample organisation profile.

Every test uses a hand-built fixture profile/config, never real
demand-intelligence data, and patches every path account_intelligence_engine.py
or generate.py touches so nothing here reads or writes real AOS files.

Run with:
    python3 -m unittest tests.test_account_intelligence_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import account_intelligence_engine as engine  # noqa: E402
import generate  # noqa: E402

DEMAND_CATEGORIES_CONFIG = {
    "categories": {
        "ai_adoption": {"label": "AI Adoption", "baseScore": 70},
        "governance_trigger": {"label": "Governance Trigger", "baseScore": 85},
        "funding_trigger": {"label": "Funding Trigger", "baseScore": 75},
        "regulatory_trigger": {"label": "Regulatory Trigger", "baseScore": 95},
        "failure_trigger": {"label": "Failure Trigger", "baseScore": 100},
    }
}

CONFIG = engine.load_json(engine.CONFIG_PATH, {})
ASSETS = engine.load_json(engine.ASSETS_PATH, {"products": [], "websitePages": [], "channels": []})


def make_profile(**overrides):
    base = {
        "organisation": "BBVA",
        "signals": [
            {"date": "2026-07-20", "category": "ai_adoption", "categoryLabel": "AI Adoption", "baseScore": 70,
             "confidence": "high", "eventSummary": "BBVA rolled out Microsoft Copilot to 40,000 employees.",
             "sourceUrl": "https://example.com/1"},
        ],
        "overallDemandScore": 70, "matchedCategories": ["ai_adoption"],
        "buyingReadinessScore": 58, "buyingReadinessBand": "Medium",
        "recommendedServices": ["AI Deployment Governance (ADGL)", "AI Risk Assessment", "AI Governance Advisory"],
        "recommendedAction": "Prepare Insight Article", "recommendedActionReason": "test",
        "opportunityNarrative": "test narrative",
        "industry": "Financial Services", "scale": "40,000 employees", "region": "Europe",
        "firstSeen": "2026-07-20", "lastSeen": "2026-07-20",
        "outreachHappened": False, "proposalCreated": False, "converted": False, "revenueGenerated": None,
    }
    base.update(overrides)
    return base


class CompanyProfileTests(unittest.TestCase):
    def test_extracts_known_fields_honestly(self):
        profile = make_profile()
        result = engine.company_profile(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(result["industry"], "Financial Services")
        self.assertEqual(result["geographicFootprint"], "Europe")
        self.assertEqual(result["approximateSize"], "40,000 employees")
        self.assertIn("Not specified", result["headquarters"])

    def test_regulatory_environment_by_region(self):
        profile = make_profile(region="UAE")
        result = engine.company_profile(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertIn("CBUAE", result["regulatoryEnvironment"])

    def test_unspecified_region_is_honest_not_guessed(self):
        profile = make_profile(region="Not specified")
        result = engine.company_profile(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertIn("Not specified", result["regulatoryEnvironment"])

    def test_ai_maturity_uses_strongest_matched_category(self):
        profile = make_profile(matchedCategories=["ai_adoption", "governance_trigger"])
        result = engine.company_profile(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(result["aiMaturityLevel"], "Governance-formalising")

    def test_no_matched_categories_is_honest(self):
        profile = make_profile(matchedCategories=[])
        result = engine.company_profile(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(result["aiMaturityLevel"], "Not enough signal to assess")
        self.assertIn("Not enough public signal", result["businessPriorities"])


class AiDeploymentIntelligenceTests(unittest.TestCase):
    def test_detects_named_vendor_from_signal_text(self):
        profile = make_profile()
        result = engine.ai_deployment_intelligence(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertIn("Microsoft", result["vendorsInvolved"])
        self.assertIn("Copilot", result["vendorsInvolved"])

    def test_no_vendor_mentioned_is_honest_not_invented(self):
        profile = make_profile(signals=[
            {"date": "2026-07-20", "category": "governance_trigger", "categoryLabel": "Governance Trigger",
             "baseScore": 85, "confidence": "high",
             "eventSummary": "Acme Corp appointed a Chief AI Officer.", "sourceUrl": None},
        ], matchedCategories=["governance_trigger"])
        result = engine.ai_deployment_intelligence(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(result["vendorsInvolved"], ["Not specified — no named AI vendor detected in public signal text"])

    def test_public_announcements_reflect_real_signals(self):
        profile = make_profile()
        result = engine.ai_deployment_intelligence(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(len(result["publicAnnouncements"]), 1)
        self.assertEqual(result["publicAnnouncements"][0]["url"], "https://example.com/1")


class GovernanceRiskAssessmentTests(unittest.TestCase):
    def test_returns_risks_for_matched_category(self):
        profile = make_profile()
        risks = engine.governance_risk_assessment(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        risk_names = [r["risk"] for r in risks]
        self.assertIn("Human oversight", risk_names)
        self.assertIn("BBVA", risks[0]["why"])

    def test_deduplicates_across_multiple_matched_categories(self):
        profile = make_profile(matchedCategories=["ai_adoption", "funding_trigger"])
        risks = engine.governance_risk_assessment(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        risk_names = [r["risk"] for r in risks]
        self.assertEqual(len(risk_names), len(set(risk_names)))

    def test_no_matched_categories_returns_empty(self):
        profile = make_profile(matchedCategories=[])
        risks = engine.governance_risk_assessment(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(risks, [])


class ServiceFitTests(unittest.TestCase):
    def test_confidence_tiers_match_rank_position(self):
        profile = make_profile()
        services = engine.service_fit(profile)
        self.assertEqual(services[0]["confidence"], "High")
        self.assertEqual(services[1]["confidence"], "Medium")
        self.assertEqual(services[2]["confidence"], "Low")

    def test_empty_services_returns_empty(self):
        profile = make_profile(recommendedServices=[])
        self.assertEqual(engine.service_fit(profile), [])


class DecisionMakersTests(unittest.TestCase):
    def test_returns_titles_only_never_names(self):
        profile = make_profile(matchedCategories=["governance_trigger"])
        titles = engine.decision_makers(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertIn("Chief AI Officer", titles)
        for title in titles:
            self.assertNotIn("Ramya", title)

    def test_no_signal_gives_honest_fallback(self):
        profile = make_profile(matchedCategories=[])
        titles = engine.decision_makers(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(len(titles), 1)
        self.assertIn("Not enough signal", titles[0])


class OutreachStrategyTests(unittest.TestCase):
    """All six buckets must be genuinely reachable — a design smell this
    suite specifically guards against is a vocabulary option that can
    never actually be produced by the deterministic rules."""

    def test_low_confidence_always_waits(self):
        profile = make_profile(buyingReadinessBand="Very High",
                                signals=[dict(make_profile()["signals"][0], confidence="low")])
        strategy, _ = engine.outreach_strategy(profile, CONFIG)
        self.assertEqual(strategy, "Wait")

    def test_failure_trigger_is_direct_proposal_regardless_of_band(self):
        profile = make_profile(matchedCategories=["failure_trigger"], buyingReadinessBand="Medium")
        strategy, _ = engine.outreach_strategy(profile, CONFIG)
        self.assertEqual(strategy, "Direct proposal")

    def test_very_high_band_is_direct_proposal(self):
        profile = make_profile(buyingReadinessBand="Very High")
        strategy, _ = engine.outreach_strategy(profile, CONFIG)
        self.assertEqual(strategy, "Direct proposal")

    def test_high_band_is_discovery_workshop(self):
        profile = make_profile(buyingReadinessBand="High")
        strategy, _ = engine.outreach_strategy(profile, CONFIG)
        self.assertEqual(strategy, "Discovery workshop")

    def test_medium_band_high_confidence_is_thought_leadership(self):
        profile = make_profile(buyingReadinessBand="Medium",
                                signals=[dict(make_profile()["signals"][0], confidence="high")])
        strategy, _ = engine.outreach_strategy(profile, CONFIG)
        self.assertEqual(strategy, "Thought leadership")

    def test_medium_band_medium_confidence_is_connection_first(self):
        profile = make_profile(buyingReadinessBand="Medium",
                                signals=[dict(make_profile()["signals"][0], confidence="medium")])
        strategy, _ = engine.outreach_strategy(profile, CONFIG)
        self.assertEqual(strategy, "Connection first")

    def test_low_band_is_monitor(self):
        profile = make_profile(buyingReadinessBand="Low",
                                signals=[dict(make_profile()["signals"][0], confidence="medium")])
        strategy, _ = engine.outreach_strategy(profile, CONFIG)
        self.assertEqual(strategy, "Monitor")


class ConversationStartersTests(unittest.TestCase):
    def test_always_returns_exactly_three(self):
        profile = make_profile(matchedCategories=[])
        starters = engine.conversation_starters(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(len(starters), 3)

    def test_no_starter_is_a_sales_pitch(self):
        profile = make_profile()
        starters = engine.conversation_starters(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        for starter in starters:
            lowered = starter.lower()
            self.assertNotIn("buy", lowered)
            self.assertNotIn("purchase", lowered)
            self.assertNotIn("sign up", lowered)

    def test_starters_never_duplicate(self):
        profile = make_profile(matchedCategories=[])
        starters = engine.conversation_starters(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        self.assertEqual(len(starters), len(set(starters)))


class SupportingAssetsTests(unittest.TestCase):
    def test_ranks_domain_matched_assets_first(self):
        profile = make_profile(matchedCategories=["ai_adoption"])
        assets = engine.supporting_assets(profile, DEMAND_CATEGORIES_CONFIG, CONFIG, ASSETS)
        self.assertTrue(any(a["id"] == "adgl-methodology" for a in assets))

    def test_falls_back_to_general_assets_when_nothing_matches(self):
        profile = make_profile(matchedCategories=[])
        assets = engine.supporting_assets(profile, DEMAND_CATEGORIES_CONFIG, CONFIG, ASSETS)
        self.assertTrue(assets)
        self.assertTrue(all(a.get("isGeneral") for a in assets))

    def test_never_invents_an_asset_not_in_the_catalogue(self):
        profile = make_profile()
        assets = engine.supporting_assets(profile, DEMAND_CATEGORIES_CONFIG, CONFIG, ASSETS)
        catalogue_ids = {a["id"] for a in ASSETS["products"] + ASSETS["websitePages"] + ASSETS["channels"]}
        for a in assets:
            self.assertIn(a["id"], catalogue_ids)


class OpportunityScorecardTests(unittest.TestCase):
    def test_uses_real_opportunity_record_when_present(self):
        profile = make_profile()
        opportunity_schema = {"opportunities": [{
            "organisation": "BBVA", "priorityScore": 82,
            "scores": {"strategicValue": 8, "expectedRevenue": 7, "relationshipValue": 7},
        }]}
        scorecard = engine.opportunity_scorecard(profile, opportunity_schema, CONFIG)
        self.assertEqual(scorecard["overallPriority"], 82)
        self.assertEqual(scorecard["strategicValue"], 8)
        self.assertIn("Real opportunity record", scorecard["source"])

    def test_falls_back_to_estimate_when_no_opportunity_record(self):
        profile = make_profile()
        scorecard = engine.opportunity_scorecard(profile, {"opportunities": []}, CONFIG)
        self.assertIn("Estimated", scorecard["source"])
        self.assertEqual(scorecard["overallPriority"], profile["buyingReadinessScore"])

    def test_sales_cycle_and_competition_risk_are_deterministic(self):
        profile = make_profile(buyingReadinessBand="Very High", signals=[
            make_profile()["signals"][0], make_profile()["signals"][0], make_profile()["signals"][0],
        ])
        scorecard = engine.opportunity_scorecard(profile, {"opportunities": []}, CONFIG)
        self.assertIn("2-6 weeks", scorecard["estimatedSalesCycle"])
        self.assertIn("Elevated", scorecard["competitionRisk"])


class ExecutiveSummaryTests(unittest.TestCase):
    def test_never_exceeds_300_words(self):
        profile = make_profile()
        company = engine.company_profile(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        deployment = engine.ai_deployment_intelligence(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        risks = engine.governance_risk_assessment(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        # Pathologically long why-text, to prove the cap is enforced, not
        # just usually satisfied by short templates.
        long_risk = {"risk": "Human oversight", "why": "word " * 500}
        services = engine.service_fit(profile)
        strategy = engine.outreach_strategy(profile, CONFIG)
        scorecard = engine.opportunity_scorecard(profile, {"opportunities": []}, CONFIG)
        summary = engine.executive_summary(profile, company, deployment, long_risk, services[0], strategy, scorecard)
        self.assertLessEqual(len(summary.split()), 300)

    def test_never_lowercases_ai_acronym(self):
        profile = make_profile()
        company = engine.company_profile(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        deployment = engine.ai_deployment_intelligence(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        risks = engine.governance_risk_assessment(profile, DEMAND_CATEGORIES_CONFIG, CONFIG)
        services = engine.service_fit(profile)
        strategy = engine.outreach_strategy(profile, CONFIG)
        scorecard = engine.opportunity_scorecard(profile, {"opportunities": []}, CONFIG)
        summary = engine.executive_summary(profile, company, deployment, risks[0], services[0], strategy, scorecard)
        self.assertNotIn("planned ai use", summary)
        self.assertIn("AI", summary)


class BuildBriefIntegrationTests(unittest.TestCase):
    def test_produces_all_ten_sections(self):
        profile = make_profile()
        markdown, feed_entry = engine.build_brief(
            profile, {"opportunities": []}, DEMAND_CATEGORIES_CONFIG, CONFIG, ASSETS)
        for i in range(1, 11):
            self.assertIn(f"Section {i}", markdown)
        self.assertEqual(feed_entry["organisation"], "BBVA")
        self.assertIsNone(feed_entry["briefPath"])  # generate.py fills this in, not the engine

    def test_feed_entry_exposes_structured_fields_for_downstream_consumers(self):
        """AOS Sprint 12 — Sales Director's Executive Proposal Generator
        traces every proposal section back to this brief's own data via
        these structured feed fields, not by parsing rendered markdown."""
        profile = make_profile()
        _, feed_entry = engine.build_brief(profile, {"opportunities": []}, DEMAND_CATEGORIES_CONFIG, CONFIG, ASSETS)
        for key in ("companyProfile", "deploymentStage", "aiInitiatives", "governanceRisks",
                    "serviceFit", "decisionMakerTitles", "supportingAssets"):
            self.assertIn(key, feed_entry)

    def test_brief_never_mentions_a_sales_pitch_verb_in_conversation_starters_section(self):
        profile = make_profile()
        markdown, _ = engine.build_brief(profile, {"opportunities": []}, DEMAND_CATEGORIES_CONFIG, CONFIG, ASSETS)
        starters_section = markdown.split("Section 7")[1].split("Section 8")[0]
        self.assertNotIn("Buy now", starters_section)


class GenerateMainTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)
        (self.tmp_path / "output").mkdir(parents=True, exist_ok=True)

    def _patches(self):
        return [
            patch("account_intelligence_engine.PROFILES_PATH", self.tmp_path / "profiles.json"),
            patch("account_intelligence_engine.OPPORTUNITY_SCHEMA_PATH", self.tmp_path / "opps.json"),
            patch("account_intelligence_engine.BRIEFS_DIR", self.tmp_path / "briefs"),
            patch("account_intelligence_engine.FEED_PATH", self.tmp_path / "feed.json"),
            patch("account_intelligence_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]

    def test_no_qualified_organisations_writes_nothing(self):
        engine.save_json(self.tmp_path / "profiles.json", {"organisations": {}})
        patches = self._patches()
        for p in patches:
            p.start()
        try:
            exit_code = generate.main()
        finally:
            for p in patches:
                p.stop()
        self.assertEqual(exit_code, 0)
        self.assertFalse((self.tmp_path / "feed.json").exists())

    def test_generates_a_brief_file_and_feed_entry_for_every_qualified_organisation(self):
        engine.save_json(self.tmp_path / "profiles.json", {"organisations": {"BBVA": make_profile()}})
        engine.save_json(self.tmp_path / "opps.json", {"opportunities": []})
        patches = self._patches()
        for p in patches:
            p.start()
        try:
            exit_code = generate.main()
        finally:
            for p in patches:
                p.stop()

        self.assertEqual(exit_code, 0)
        feed = engine.load_json(self.tmp_path / "feed.json", {})
        self.assertEqual(len(feed["briefs"]), 1)
        entry = feed["briefs"][0]
        self.assertEqual(entry["organisation"], "BBVA")
        brief_path = self.tmp_path / entry["briefPath"]
        self.assertTrue(brief_path.exists())
        self.assertIn("Account Intelligence Brief — BBVA", brief_path.read_text(encoding="utf-8"))


class SlugifyTests(unittest.TestCase):
    def test_basic_slug(self):
        self.assertEqual(engine.slugify("BBVA S.A."), "bbva-s-a")


class LoadJsonMutableDefaultTests(unittest.TestCase):
    """Regression test mirroring the real bug found in sales-director's
    prepare.py: a shared mutable default dict returned by reference lets
    one call's in-place mutation leak into the next call in the same
    process. account_intelligence_engine.load_json() must deep-copy."""

    def test_repeated_calls_never_share_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.json"
            default = {"organisations": {}}
            first = engine.load_json(missing_path, default)
            first["organisations"]["polluted"] = {"organisation": "polluted"}
            second = engine.load_json(missing_path, default)
            self.assertEqual(second["organisations"], {})


if __name__ == "__main__":
    unittest.main()
