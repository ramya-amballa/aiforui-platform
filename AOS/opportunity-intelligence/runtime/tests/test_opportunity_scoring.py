import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import opportunity_scoring as scoring  # noqa: E402

CONFIG = {
    "employmentFitWeights": {
        "roleRelevance": 20, "seniorityAlignment": 12, "grcTechnologyRiskAlignment": 18,
        "aiGovernanceAlignment": 18, "tprmAlignment": 12, "regulatedIndustryAlignment": 8,
        "geographicSuitability": 6, "evidenceStrength": 6,
    },
    "priorityThresholds": {"High": 75, "Medium": 45},
    "recommendationThresholds": {"APPLY": 70, "STRENGTHEN_PROFILE_FIRST": 45},
    "consultingHeuristicWeights": {
        "painEvidence": 25, "urgency": 20, "regulatoryPressure": 20,
        "decisionMakerAccessibility": 15, "companyMaturitySignal": 10, "relationshipPotential": 10,
    },
}


def strong_profile():
    """Fixture only — never the real, shipped ramya-professional-profile.json,
    which stays empty. Clearly fictional entries."""
    return {
        "verified_experience": [
            {"id": "v1", "category": "role", "claim": "Led AI governance framework rollout across three business units",
             "tags": ["ai governance", "grc", "technology risk"]},
            {"id": "v2", "category": "certification", "claim": "Certified in third-party risk management",
             "tags": ["tprm"]},
        ],
        "transferable_experience": [
            {"id": "t1", "category": "role", "claim": "Managed vendor risk assessments", "tags": ["tprm", "regulated"]},
        ],
        "knowledge_training": [
            {"id": "k1", "category": "training", "claim": "Completed ISO 42001 lead implementer course", "tags": ["ai governance", "iso 42001"]},
        ],
        "claims_requiring_verification": [],
    }


def empty_profile():
    return {"verified_experience": [], "transferable_experience": [], "knowledge_training": [], "claims_requiring_verification": []}


class StrongAiGovernanceJobTests(unittest.TestCase):
    """TEST 1 — Strong AI Governance job."""

    def test_high_score_and_apply_recommendation(self):
        job = {"required_skills": ["ai governance", "grc"], "regulated_industry": True, "seniority_level": "Director"}
        fit = scoring.score_employment_fit(job, strong_profile(), CONFIG)
        self.assertGreaterEqual(fit["score"], 70)
        self.assertIn("v1", fit["verified_matches"])
        self.assertEqual(scoring.derive_employment_recommendation(fit["score"], CONFIG), "APPLY")

    def test_evidence_is_traceable_to_real_profile_entries(self):
        job = {"required_skills": ["ai governance"]}
        fit = scoring.score_employment_fit(job, strong_profile(), CONFIG)
        self.assertIn("v1", fit["verified_matches"])
        # Never cites an id that doesn't exist in the profile.
        profile_ids = {e["id"] for e in strong_profile()["verified_experience"]}
        self.assertTrue(set(fit["verified_matches"]).issubset(profile_ids))


class StrongGrcTechRiskJobTests(unittest.TestCase):
    """TEST 2 — Strong GRC/Technology Risk job."""

    def test_high_score(self):
        job = {"required_skills": ["grc", "technology risk"], "regulated_industry": True, "seniority_level": "Head of"}
        fit = scoring.score_employment_fit(job, strong_profile(), CONFIG)
        self.assertGreaterEqual(fit["score"], 60)
        self.assertIn("v1", fit["verified_matches"])


class WeakJobTests(unittest.TestCase):
    """TEST 3 — Weak job that should be rejected."""

    def test_low_score_and_do_not_pursue(self):
        job = {"required_skills": ["marine biology", "underwater welding"]}
        fit = scoring.score_employment_fit(job, strong_profile(), CONFIG)
        self.assertLess(fit["score"], 45)
        self.assertEqual(scoring.derive_employment_recommendation(fit["score"], CONFIG), "DO_NOT_PURSUE_YET")
        self.assertIn("marine biology", fit["gaps"])

    def test_knowledge_training_alone_never_inflates_a_fit_score(self):
        """The founder's own rule: training must never be quietly
        upgraded into implementation experience."""
        job = {"required_skills": ["iso 42001"]}
        fit_with_only_knowledge = scoring.score_employment_fit(job, strong_profile(), CONFIG)
        # k1 (knowledge_training) matches "iso 42001" but no verified/transferable entry does.
        self.assertEqual(fit_with_only_knowledge["knowledge_matches"], ["k1"])
        self.assertLess(fit_with_only_knowledge["score"], 45)


class StrongConsultingOpportunityTests(unittest.TestCase):
    """TEST 4 — Strong consulting opportunity."""

    def test_high_score_when_no_existing_record(self):
        opp = {
            "company": "Brand New Bank",
            "evidence": {"pain_evidence": True, "urgency": True, "regulatory_pressure": True},
            "decision_makers": [{"name": "Not established", "role": "CISO"}],
        }
        assessment = scoring.assess_consulting_opportunity(opp, CONFIG, {"account_intelligence": {}, "fractional_advisory_radar": {}, "relationship_intelligence": {}})
        self.assertGreaterEqual(assessment["score"], 70)
        self.assertIsNone(assessment["_source"])

    def test_prefers_a_real_existing_score_over_its_own_heuristic(self):
        feeds = {
            "account_intelligence": {"briefs": [{"organisation": "Existing Corp", "overallPriority": 91}]},
            "fractional_advisory_radar": {},
            "relationship_intelligence": {},
        }
        opp = {"company": "Existing Corp", "evidence": {}}
        assessment = scoring.assess_consulting_opportunity(opp, CONFIG, feeds)
        self.assertEqual(assessment["score"], 91)
        self.assertEqual(assessment["_source"], "account-intelligence")


class WeakConsultingLeadTests(unittest.TestCase):
    """TEST 5 — Weak consulting lead."""

    def test_low_score_with_no_evidence(self):
        opp = {"company": "Vague Prospect Inc", "evidence": {}}
        assessment = scoring.assess_consulting_opportunity(opp, CONFIG, {"account_intelligence": {}, "fractional_advisory_radar": {}, "relationship_intelligence": {}})
        self.assertLess(assessment["score"], 45)


class DecisionMakerTests(unittest.TestCase):
    def test_never_invents_a_name_falls_back_to_real_title_table(self):
        opp = {"signal_categories": ["regulatory_trigger"]}
        people = scoring.derive_decision_makers(opp, CONFIG)
        for person in people:
            self.assertEqual(person["name"], "Not established")
        self.assertTrue(any("CISO" in p["role"] or "Chief Risk Officer" in p["role"] for p in people))

    def test_uses_a_real_supplied_name_when_research_provided_one(self):
        opp = {"decision_makers": [{"name": "Jane Smith", "role": "Head of AI Governance"}]}
        people = scoring.derive_decision_makers(opp, CONFIG)
        self.assertEqual(people[0]["name"], "Jane Smith")


if __name__ == "__main__":
    unittest.main()
