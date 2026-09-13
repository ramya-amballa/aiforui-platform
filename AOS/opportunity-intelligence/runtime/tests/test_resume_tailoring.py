import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import resume_tailoring  # noqa: E402
from status_vocabulary import GapMarker  # noqa: E402

PROFILE = {
    "verified_experience": [
        {"id": "v1", "claim": "Led AI governance framework rollout", "tags": ["ai governance"]},
        {"id": "v2", "claim": "Ran quarterly board risk reporting", "tags": ["board reporting"]},
    ],
    "transferable_experience": [
        {"id": "t1", "claim": "Managed vendor risk assessments", "tags": ["tprm"]},
    ],
    "knowledge_training": [
        {"id": "k1", "claim": "Completed ISO 42001 lead implementer course", "tags": ["ai governance", "iso 42001"]},
    ],
    "claims_requiring_verification": [
        {"id": "c1", "claim": "Possibly led an ISO 42001 certification effort"},
    ],
}
EMPTY_PROFILE = {"verified_experience": [], "transferable_experience": [], "knowledge_training": [], "claims_requiring_verification": []}


class TailoringAnalysisTests(unittest.TestCase):
    def test_emphasizes_matching_verified_experience(self):
        job = {"required_skills": ["ai governance"]}
        analysis = resume_tailoring.analyze_resume_tailoring(job, PROFILE)
        self.assertIn("v1", [i["id"] for i in analysis["emphasize"]])

    def test_keeps_non_matching_verified_experience_without_dropping_it(self):
        job = {"required_skills": ["ai governance"]}
        analysis = resume_tailoring.analyze_resume_tailoring(job, PROFILE)
        self.assertIn("v2", [i["id"] for i in analysis["keep"]])

    def test_de_emphasizes_irrelevant_transferable_and_knowledge_entries(self):
        job = {"required_skills": ["ai governance"]}
        analysis = resume_tailoring.analyze_resume_tailoring(job, PROFILE)
        self.assertIn("t1", [i["id"] for i in analysis["de_emphasize"]])

    def test_do_not_claim_flags_knowledge_training_that_overlaps_the_job(self):
        job = {"required_skills": ["ai governance"]}
        analysis = resume_tailoring.analyze_resume_tailoring(job, PROFILE)
        self.assertIn("k1", [i["id"] for i in analysis["do_not_claim"]])

    def test_claims_requiring_verification_are_always_flagged_do_not_claim(self):
        job = {"required_skills": ["anything"]}
        analysis = resume_tailoring.analyze_resume_tailoring(job, PROFILE)
        self.assertIn("c1", [i["id"] for i in analysis["do_not_claim"]])


class ResumeDraftingTests(unittest.TestCase):
    def test_never_fabricates_a_resume_when_profile_is_empty(self):
        job = {"required_skills": ["ai governance"], "role_or_signal": "Head of AI Governance", "company": "Acme"}
        analysis = resume_tailoring.analyze_resume_tailoring(job, EMPTY_PROFILE)
        resume = resume_tailoring.draft_resume(job, EMPTY_PROFILE, analysis)
        self.assertEqual(resume, GapMarker.NOT_ESTABLISHED.value)

    def test_drafts_a_resume_only_from_verified_experience(self):
        job = {"required_skills": ["ai governance"], "role_or_signal": "Head of AI Governance", "company": "Acme"}
        analysis = resume_tailoring.analyze_resume_tailoring(job, PROFILE)
        resume = resume_tailoring.draft_resume(job, PROFILE, analysis)
        self.assertIn("Led AI governance framework rollout", resume)
        # Knowledge/training claim must never appear as a fact in the draft.
        self.assertNotIn("ISO 42001 lead implementer", resume)

    def test_cover_letter_never_fabricated_when_no_relevant_verified_experience(self):
        job = {"required_skills": ["quantum computing"], "role_or_signal": "Quantum Lead", "company": "Acme"}
        analysis = resume_tailoring.analyze_resume_tailoring(job, PROFILE)
        letter = resume_tailoring.draft_cover_letter(job, PROFILE, analysis)
        self.assertEqual(letter, GapMarker.NOT_ESTABLISHED.value)


if __name__ == "__main__":
    unittest.main()
