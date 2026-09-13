import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import opportunity_model as model  # noqa: E402

CONFIG = {
    "employmentFitWeights": {"roleRelevance": 20, "seniorityAlignment": 12, "grcTechnologyRiskAlignment": 18,
                              "aiGovernanceAlignment": 18, "tprmAlignment": 12, "regulatedIndustryAlignment": 8,
                              "geographicSuitability": 6, "evidenceStrength": 6},
    "priorityThresholds": {"High": 75, "Medium": 45},
    "recommendationThresholds": {"APPLY": 70, "STRENGTHEN_PROFILE_FIRST": 45},
    "consultingHeuristicWeights": {"painEvidence": 25, "urgency": 20, "regulatoryPressure": 20,
                                    "decisionMakerAccessibility": 15, "companyMaturitySignal": 10, "relationshipPotential": 10},
}
EMPTY_PROFILE = {"verified_experience": [], "transferable_experience": [], "knowledge_training": [], "claims_requiring_verification": []}
EMPTY_FEEDS = {"account_intelligence": {}, "fractional_advisory_radar": {}, "relationship_intelligence": {}}


class RelationshipContactTests(unittest.TestCase):
    """TEST 6 — Potential relationship contact."""

    def test_relationship_opportunity_builds_with_relationship_first_strategy(self):
        entry = {
            "opportunity_type": "RELATIONSHIP", "company": "Familiar Bank", "source": "public LinkedIn post",
            "role_or_signal": "New CISO announcement", "relationship_health_score": 60,
        }
        opp = model.build_opportunity(entry, EMPTY_PROFILE, CONFIG, EMPTY_FEEDS)
        self.assertEqual(opp["opportunity_type"], "RELATIONSHIP")
        self.assertEqual(opp["recommended_action"], "RELATIONSHIP_FIRST")
        self.assertEqual(opp["drafts"]["dm"]["approval_status"], "PENDING_APPROVAL")
        # No resume/cover-letter drafting for a non-employment type.
        self.assertIsNone(opp["drafts"]["resume"]["content"])


class MissingDataTests(unittest.TestCase):
    """TEST 7 — Opportunity with missing data."""

    def test_validate_rejects_missing_required_fields(self):
        problems = model.validate_inbox_entry({"opportunity_type": "CONSULTING"})  # no company, no source
        self.assertTrue(any("company" in p for p in problems))
        self.assertTrue(any("source" in p for p in problems))

    def test_build_handles_a_minimally_valid_entry_without_crashing(self):
        """Only the required fields present — everything else absent.
        Must produce honest gap markers, never crash, never fabricate."""
        minimal = {"opportunity_type": "CONSULTING", "company": "Sparse Co", "source": "manual note"}
        opp = model.build_opportunity(minimal, EMPTY_PROFILE, CONFIG, EMPTY_FEEDS)
        self.assertEqual(opp["company"], "Sparse Co")
        self.assertIsNone(opp["role_or_signal"])
        self.assertEqual(opp["decision_makers"], [])
        self.assertEqual(opp["evidence"], [])


class DuplicateOpportunityTests(unittest.TestCase):
    """TEST 8 — Duplicate opportunity."""

    def test_same_entry_always_produces_the_same_id(self):
        entry = {"opportunity_type": "EMPLOYMENT", "company": "Acme Corp", "role_or_signal": "Head of AI Governance",
                  "source": "careers page", "discovered_at": "2026-09-13"}
        id1 = model.make_opportunity_id(entry)
        id2 = model.make_opportunity_id(dict(entry))  # a fresh dict, same values
        self.assertEqual(id1, id2)

    def test_a_different_entry_produces_a_different_id(self):
        entry_a = {"company": "Acme Corp", "role_or_signal": "Role A", "discovered_at": "2026-09-13"}
        entry_b = {"company": "Acme Corp", "role_or_signal": "Role B", "discovered_at": "2026-09-13"}
        self.assertNotEqual(model.make_opportunity_id(entry_a), model.make_opportunity_id(entry_b))


class OpportunityTypeValidationTests(unittest.TestCase):
    def test_rejects_an_invalid_opportunity_type(self):
        problems = model.validate_inbox_entry({"opportunity_type": "NOT_A_REAL_TYPE", "company": "X", "source": "Y"})
        self.assertTrue(any("opportunity_type" in p for p in problems))

    def test_accepts_every_declared_valid_type(self):
        for t in model.VALID_OPPORTUNITY_TYPES:
            problems = model.validate_inbox_entry({"opportunity_type": t, "company": "X", "source": "Y"})
            self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
