import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import approval_queue as aq  # noqa: E402


class NewDraftTests(unittest.TestCase):
    def test_every_new_draft_starts_pending_approval(self):
        """TEST 9 — Draft DM awaiting approval."""
        draft = aq.new_draft("Hi, following up on...")
        self.assertEqual(draft["approval_status"], "PENDING_APPROVAL")
        self.assertIsNone(draft["approved_by"])
        self.assertEqual(len(draft["audit"]), 1)


class ApprovedActionTests(unittest.TestCase):
    def test_approve_transitions_and_records_actor(self):
        """TEST 10 — Approved action."""
        draft = aq.new_draft("some outreach text")
        aq.approve(draft, actor="Ramya", note="looks good")
        self.assertEqual(draft["approval_status"], "APPROVED")
        self.assertEqual(draft["approved_by"], "Ramya")
        self.assertIsNotNone(draft["approved_at"])
        self.assertEqual(draft["decision_note"], "looks good")
        self.assertEqual(len(draft["audit"]), 2)

    def test_approved_can_then_be_marked_executed(self):
        draft = aq.new_draft("x")
        aq.approve(draft, actor="Ramya")
        aq.mark_executed(draft, actor="Ramya", note="sent manually via LinkedIn")
        self.assertEqual(draft["approval_status"], "EXECUTED")


class RejectedActionTests(unittest.TestCase):
    def test_reject_transitions_from_pending(self):
        """TEST 11 — Rejected action."""
        draft = aq.new_draft("x")
        aq.reject(draft, actor="Ramya", note="not relevant")
        self.assertEqual(draft["approval_status"], "REJECTED")

    def test_rejected_is_a_dead_end(self):
        draft = aq.new_draft("x")
        aq.reject(draft, actor="Ramya")
        with self.assertRaises(aq.InvalidTransitionError):
            aq.approve(draft, actor="Ramya")
        self.assertEqual(draft["approval_status"], "REJECTED")


class ExecutionSafetyTests(unittest.TestCase):
    def test_cannot_execute_while_pending_approval(self):
        """TEST 12 — Attempted execution while PENDING_APPROVAL.
        MUST FAIL SAFELY. No external action may occur."""
        draft = aq.new_draft("x")
        self.assertEqual(draft["approval_status"], "PENDING_APPROVAL")

        with self.assertRaises(aq.InvalidTransitionError):
            aq.mark_executed(draft, actor="Ramya")

        # The single most important assertion in this whole test suite:
        # the failed attempt changed nothing.
        self.assertEqual(draft["approval_status"], "PENDING_APPROVAL")
        self.assertEqual(len(draft["audit"]), 1)

    def test_cannot_execute_from_rejected(self):
        draft = aq.new_draft("x")
        aq.reject(draft, actor="Ramya")
        with self.assertRaises(aq.InvalidTransitionError):
            aq.mark_executed(draft, actor="Ramya")
        self.assertEqual(draft["approval_status"], "REJECTED")

    def test_cannot_execute_from_cancelled(self):
        draft = aq.new_draft("x")
        aq.cancel(draft, actor="Ramya")
        with self.assertRaises(aq.InvalidTransitionError):
            aq.mark_executed(draft, actor="Ramya")

    def test_actor_is_mandatory_for_every_transition(self):
        draft = aq.new_draft("x")
        with self.assertRaises(aq.InvalidTransitionError):
            aq.approve(draft, actor="")
        with self.assertRaises(aq.InvalidTransitionError):
            aq.approve(draft, actor=None)
        self.assertEqual(draft["approval_status"], "PENDING_APPROVAL")

    def test_edit_required_path_reaches_approved(self):
        draft = aq.new_draft("x")
        aq.request_edit(draft, actor="Ramya", note="tone")
        self.assertEqual(draft["approval_status"], "EDIT_REQUIRED")
        aq.approve(draft, actor="Ramya")
        self.assertEqual(draft["approval_status"], "APPROVED")

    def test_no_transition_skips_pending_approval_straight_to_executed(self):
        """A brand-new draft can never reach EXECUTED in one call,
        regardless of which transition function is used."""
        for fn in (aq.mark_executed,):
            draft = aq.new_draft("x")
            with self.assertRaises(aq.InvalidTransitionError):
                fn(draft, actor="Ramya")


if __name__ == "__main__":
    unittest.main()
