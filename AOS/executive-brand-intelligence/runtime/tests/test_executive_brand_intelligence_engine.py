#!/usr/bin/env python3
"""
Unit and integration tests for Executive Brand Intelligence (AOS Sprint 15).

Every test uses hand-built fixtures for the four real data sources this
engine reads (organisation-profiles.json, account-intelligence-feed.json,
relationship-profiles.json, supporting-assets.json) plus an explicit
`today` date, and patches every path generate.py touches so nothing
here reads or writes real AOS data.

Run with:
    python3 -m unittest tests.test_executive_brand_intelligence_engine -v   (from runtime/)
"""

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import executive_brand_intelligence_engine as engine  # noqa: E402
import generate  # noqa: E402

TODAY = date(2026, 7, 27)

CONFIG = {
    "windowDays": 7,
    "monthlyWindowDays": 30,
    "companiesToEngageCount": 5,
    "topicsToWriteCount": 3,
    "assetsToUpdateCount": 4,
    "visibilityImpactThresholds": {"high": 3, "medium": 1},
    "leadGenerationThresholds": {"high": 2, "medium": 1},
    "consultingInfluenceThresholds": {"high": 2, "medium": 1},
}

DEMAND_CATEGORIES_CONFIG = {
    "categories": {
        "ai_adoption": {"label": "AI Adoption", "baseScore": 70},
        "governance_trigger": {"label": "Governance Trigger", "baseScore": 85},
    }
}

ACCOUNT_INTELLIGENCE_CONFIG = {
    "categoryToDomainTags": {
        "ai_adoption": ["ADGL", "AI Deployment Governance", "AI Governance"],
        "governance_trigger": ["AI Governance", "GRC"],
    }
}

ASSETS = {
    "products": [
        {"title": "ADGL Methodology", "type": "Methodology", "url": "/resources/adgl", "domainTags": ["ADGL"]},
        {"title": "AI Governance Whitepaper", "type": "Whitepaper", "url": "/resources/whitepaper", "domainTags": ["AI Governance"]},
    ],
    "websitePages": [],
    "channels": [{"title": "General Newsletter", "type": "Channel", "url": "/newsletter", "isGeneral": True}],
}


def make_org(name, **overrides):
    base = {
        "organisation": name, "industry": "Financial Services",
        "matchedCategories": ["ai_adoption"], "buyingReadinessBand": "Medium", "buyingReadinessScore": 55,
        "lastSeen": "2026-07-25",
    }
    base.update(overrides)
    return base


class OrganisationsThisWeekTests(unittest.TestCase):
    def test_filters_by_window(self):
        profiles = {"organisations": {
            "Recent Co": make_org("Recent Co", lastSeen="2026-07-25"),
            "Stale Co": make_org("Stale Co", lastSeen="2026-01-01"),
        }}
        result = engine.organisations_this_week(profiles, CONFIG, today=TODAY)
        names = [o["organisation"] for o in result]
        self.assertIn("Recent Co", names)
        self.assertNotIn("Stale Co", names)


class CompaniesToEngageTests(unittest.TestCase):
    def test_ranked_by_buying_readiness_score(self):
        orgs = [make_org("Low", buyingReadinessScore=20), make_org("High", buyingReadinessScore=90)]
        result = engine.companies_to_engage(orgs, CONFIG)
        self.assertEqual(result[0]["organisation"], "High")


class ExecutivesToFollowTests(unittest.TestCase):
    def test_returns_real_tracked_people_only(self):
        profiles = {"people": {"Jane Doe": {"person": "Jane Doe", "company": "BBVA", "role": "CRO"}}}
        result = engine.executives_to_follow(profiles)
        self.assertEqual(result, [{"person": "Jane Doe", "company": "BBVA", "role": "CRO"}])

    def test_empty_when_nothing_tracked(self):
        self.assertEqual(engine.executives_to_follow({"people": {}}), [])


class TrendingDomainTests(unittest.TestCase):
    def test_finds_most_common_category(self):
        orgs = [make_org("A", matchedCategories=["ai_adoption"]), make_org("B", matchedCategories=["ai_adoption"]),
                make_org("C", matchedCategories=["governance_trigger"])]
        label, key, count = engine.trending_domain(orgs, DEMAND_CATEGORIES_CONFIG)
        self.assertEqual(label, "AI Adoption")
        self.assertEqual(key, "ai_adoption")
        self.assertEqual(count, 2)

    def test_no_organisations_is_honest(self):
        label, key, count = engine.trending_domain([], DEMAND_CATEGORIES_CONFIG)
        self.assertIsNone(label)
        self.assertIsNone(key)
        self.assertEqual(count, 0)


class TrendingGovernanceRiskTests(unittest.TestCase):
    def test_finds_most_common_risk(self):
        briefs = [
            {"governanceRisks": [{"risk": "Human oversight", "why": "x"}]},
            {"governanceRisks": [{"risk": "Human oversight", "why": "x"}, {"risk": "Monitoring", "why": "y"}]},
        ]
        risk, count = engine.trending_governance_risk(briefs)
        self.assertEqual(risk, "Human oversight")
        self.assertEqual(count, 2)

    def test_no_briefs_is_honest(self):
        risk, count = engine.trending_governance_risk([])
        self.assertIsNone(risk)
        self.assertEqual(count, 0)


class TopicsToWriteTests(unittest.TestCase):
    def test_empty_when_no_trend_at_all(self):
        self.assertEqual(engine.topics_to_write(None, 0, None, 0, [], CONFIG), [])

    def test_cites_real_counts(self):
        orgs = [make_org("A", industry="Banking")]
        topics = engine.topics_to_write("AI Adoption", 3, "Human oversight", 2, orgs, CONFIG)
        self.assertTrue(any("2 qualified account" in t for t in topics))


class AssetsToUpdateTests(unittest.TestCase):
    def test_ranks_by_domain_tag_overlap(self):
        result = engine.assets_to_update(ASSETS, "ai_adoption", ACCOUNT_INTELLIGENCE_CONFIG, CONFIG)
        self.assertEqual(result[0]["title"], "ADGL Methodology")

    def test_no_trending_domain_still_returns_assets(self):
        result = engine.assets_to_update(ASSETS, None, ACCOUNT_INTELLIGENCE_CONFIG, CONFIG)
        self.assertTrue(len(result) > 0)


class WhitepapersToPublishTests(unittest.TestCase):
    def test_filters_to_whitepaper_type_only(self):
        result = engine.whitepapers_to_publish(ASSETS)
        self.assertEqual([a["title"] for a in result], ["AI Governance Whitepaper"])


class ConferencesToMonitorTests(unittest.TestCase):
    def test_dedupes_by_conference_name(self):
        profiles = {"people": {
            "A": {"upcomingConference": {"name": "AI Summit", "date": "2026-08-01"}},
            "B": {"upcomingConference": {"name": "AI Summit", "date": "2026-08-01"}},
            "C": {"upcomingConference": None},
        }}
        result = engine.conferences_to_monitor(profiles)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "AI Summit")

    def test_empty_when_none_tracked(self):
        self.assertEqual(engine.conferences_to_monitor({"people": {}}), [])


class GithubImprovementTests(unittest.TestCase):
    def test_honest_when_no_signal(self):
        result = engine.github_improvement_suggestion(None, None)
        self.assertIn("Not enough signal", result)

    def test_cites_real_subject(self):
        result = engine.github_improvement_suggestion("AI Adoption", "Human oversight")
        self.assertIn("Human oversight", result)


class LinkedinStrategyTests(unittest.TestCase):
    def test_honest_when_no_briefs(self):
        result = engine.linkedin_strategy([], None)
        self.assertIn("Not enough", result)

    def test_cites_real_counts(self):
        briefs = [{"outreachStrategy": "Thought Leadership"}, {"outreachStrategy": "Thought Leadership"}, {"outreachStrategy": "Direct Proposal"}]
        result = engine.linkedin_strategy(briefs, "Human oversight")
        self.assertIn("2 of 3", result)
        self.assertIn("Human oversight", result)


class EstimateTierTests(unittest.TestCase):
    """Design-smell guard: every tier in each vocabulary must be reachable."""

    def test_visibility_impact_all_tiers_reachable(self):
        self.assertEqual(engine.visibility_impact([make_org(str(i)) for i in range(5)], CONFIG), "High")
        self.assertEqual(engine.visibility_impact([make_org("A")], CONFIG), "Medium")
        self.assertEqual(engine.visibility_impact([], CONFIG), "Low")

    def test_lead_generation_all_tiers_reachable(self):
        high = [make_org("A", buyingReadinessBand="High"), make_org("B", buyingReadinessBand="Very High")]
        self.assertEqual(engine.lead_generation_potential(high, CONFIG), "High")
        medium = [make_org("A", buyingReadinessBand="High")]
        self.assertEqual(engine.lead_generation_potential(medium, CONFIG), "Medium")
        low = [make_org("A", buyingReadinessBand="Low")]
        self.assertEqual(engine.lead_generation_potential(low, CONFIG), "Low")

    def test_consulting_influence_all_tiers_reachable(self):
        briefs_high = [{"serviceFit": [{"confidence": "High"}, {"confidence": "High"}]}]
        self.assertEqual(engine.expected_consulting_influence(briefs_high, CONFIG), "High")
        briefs_medium = [{"serviceFit": [{"confidence": "High"}]}]
        self.assertEqual(engine.expected_consulting_influence(briefs_medium, CONFIG), "Medium")
        briefs_low = [{"serviceFit": [{"confidence": "Low"}]}]
        self.assertEqual(engine.expected_consulting_influence(briefs_low, CONFIG), "Low")


class LoadJsonMutableDefaultTests(unittest.TestCase):
    def test_default_is_deep_copied_not_shared(self):
        first = engine.load_json(Path("/nonexistent/path.json"), {"weeks": []})
        first["weeks"].append({"weekOf": "2026-01-01"})
        second = engine.load_json(Path("/nonexistent/path.json"), {"weeks": []})
        self.assertEqual(second["weeks"], [])


class BuildMonthlyAuthorityReportTests(unittest.TestCase):
    def test_no_history_is_honest(self):
        result = engine.build_monthly_authority_report({"weeks": []}, CONFIG, today=TODAY)
        self.assertEqual(result["weeksIncluded"], 0)

    def test_rolls_up_trailing_weeks(self):
        history = {"weeks": [
            {"weekOf": "2026-07-20", "trendingDomain": "AI Adoption", "trendingGovernanceRisk": "Human oversight",
             "companiesToEngage": [{"organisation": "A"}]},
            {"weekOf": "2026-07-13", "trendingDomain": "AI Adoption", "trendingGovernanceRisk": "Monitoring",
             "companiesToEngage": [{"organisation": "B"}]},
            {"weekOf": "2025-01-01", "trendingDomain": "Old Domain", "trendingGovernanceRisk": "Old Risk",
             "companiesToEngage": [{"organisation": "C"}]},
        ]}
        result = engine.build_monthly_authority_report(history, CONFIG, today=TODAY)
        self.assertEqual(result["weeksIncluded"], 2)
        self.assertEqual(result["topDomain"], "AI Adoption")
        self.assertEqual(result["totalCompaniesEngaged"], 2)


class BuildWeeklyPlanTests(unittest.TestCase):
    def test_full_plan_assembly(self):
        org_profiles = {"organisations": {"BBVA": make_org("BBVA", buyingReadinessBand="High", buyingReadinessScore=80)}}
        account_feed = {"briefs": [{"organisation": "BBVA", "outreachStrategy": "Thought Leadership",
                                     "governanceRisks": [{"risk": "Human oversight", "why": "x"}],
                                     "serviceFit": [{"confidence": "High"}]}]}
        relationship_profiles = {"people": {"Jane Doe": {"person": "Jane Doe", "company": "BBVA", "role": "CRO",
                                                           "upcomingConference": {"name": "AI Summit", "date": "2026-08-01"}}}}
        plan = engine.build_weekly_plan(org_profiles, account_feed, relationship_profiles, ASSETS,
                                         DEMAND_CATEGORIES_CONFIG, ACCOUNT_INTELLIGENCE_CONFIG, CONFIG, today=TODAY)
        self.assertEqual(plan["companiesThisWeek"], 1)
        self.assertEqual(plan["trendingDomain"], "AI Adoption")
        self.assertEqual(plan["trendingGovernanceRisk"], "Human oversight")
        self.assertEqual(len(plan["executivesToFollow"]), 1)
        self.assertEqual(len(plan["conferencesToMonitor"]), 1)


class GenerateEndToEndTests(unittest.TestCase):
    """Runs the real generate.main() over mocked data sources, confirming
    a genuinely populated plan is written, and an empty organisation-
    profiles.json produces an honest no-op."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_path = Path(self._tmpdir.name)

        patches = [
            patch("executive_brand_intelligence_engine.ORGANISATION_PROFILES_PATH", self.tmp_path / "organisation-profiles.json"),
            patch("executive_brand_intelligence_engine.ACCOUNT_INTELLIGENCE_FEED_PATH", self.tmp_path / "account-intelligence-feed.json"),
            patch("executive_brand_intelligence_engine.RELATIONSHIP_PROFILES_PATH", self.tmp_path / "relationship-profiles.json"),
            patch("executive_brand_intelligence_engine.SUPPORTING_ASSETS_PATH", self.tmp_path / "supporting-assets.json"),
            patch("executive_brand_intelligence_engine.DEMAND_CATEGORIES_PATH", self.tmp_path / "demand-categories.json"),
            patch("executive_brand_intelligence_engine.ACCOUNT_INTELLIGENCE_CONFIG_PATH", self.tmp_path / "account-intelligence-config.json"),
            patch("executive_brand_intelligence_engine.HISTORY_PATH", self.tmp_path / "brand-plan-history.json"),
            patch("executive_brand_intelligence_engine.FEED_PATH", self.tmp_path / "output" / "executive-brand-intelligence-feed.json"),
            patch("executive_brand_intelligence_engine.REPO_ROOT", self.tmp_path),
            patch("generate.RUNTIME_DIR", self.tmp_path),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

        engine.save_json(self.tmp_path / "supporting-assets.json", ASSETS)
        engine.save_json(self.tmp_path / "demand-categories.json", DEMAND_CATEGORIES_CONFIG)
        engine.save_json(self.tmp_path / "account-intelligence-config.json", ACCOUNT_INTELLIGENCE_CONFIG)

    def test_no_organisations_writes_nothing(self):
        engine.save_json(self.tmp_path / "organisation-profiles.json", {"organisations": {}})
        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        self.assertFalse((self.tmp_path / "output" / "executive-brand-intelligence-feed.json").exists())

    def test_real_data_produces_real_feed_and_history(self):
        engine.save_json(self.tmp_path / "organisation-profiles.json",
                          {"organisations": {"BBVA": make_org("BBVA", lastSeen=date.today().isoformat())}})
        engine.save_json(self.tmp_path / "account-intelligence-feed.json", {"briefs": []})
        engine.save_json(self.tmp_path / "relationship-profiles.json", {"people": {}})

        exit_code = generate.main()
        self.assertEqual(exit_code, 0)
        feed_path = self.tmp_path / "output" / "executive-brand-intelligence-feed.json"
        self.assertTrue(feed_path.exists())
        feed = engine.load_json(feed_path)
        self.assertEqual(feed["weeklyPlan"]["companiesThisWeek"], 1)

        history = engine.load_json(self.tmp_path / "brand-plan-history.json")
        self.assertEqual(len(history["weeks"]), 1)

    def test_rerun_same_week_does_not_duplicate_history_entry(self):
        engine.save_json(self.tmp_path / "organisation-profiles.json",
                          {"organisations": {"BBVA": make_org("BBVA", lastSeen=date.today().isoformat())}})
        engine.save_json(self.tmp_path / "account-intelligence-feed.json", {"briefs": []})
        engine.save_json(self.tmp_path / "relationship-profiles.json", {"people": {}})

        generate.main()
        generate.main()
        history = engine.load_json(self.tmp_path / "brand-plan-history.json")
        self.assertEqual(len(history["weeks"]), 1)


if __name__ == "__main__":
    unittest.main()
