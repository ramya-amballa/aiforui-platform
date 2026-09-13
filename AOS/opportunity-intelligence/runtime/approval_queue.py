"""
Opportunity Intelligence — Approval Queue (the authorization gate)

This is the one genuinely new safety mechanism in AOS: nothing else in
the platform has ever needed to gate "may this be sent to the outside
world," because nothing in AOS has ever sent anything itself. Sales
Director's own three-word readiness signal (Proposal Ready / Needs
Review / Ready To Send) is a *quality* judgement, untouched by this
module and never conflated with it — READY_TO_SEND != APPROVED. This
module is a plain, generic state machine over one status field, usable
by any draft this component produces.

The rule that makes external action safe: every transition requires an
explicit, human-supplied actor, and the only way into EXECUTED is from
APPROVED. There is no function anywhere in this codebase that sends,
posts, applies, or submits anything — mark_executed() only *records*
that the human did that themselves, outside this system. Attempting to
skip a state (most importantly, marking anything EXECUTED while it is
still PENDING_APPROVAL) raises InvalidTransitionError and changes
nothing.
"""

from datetime import datetime, timezone
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDIT_REQUIRED = "EDIT_REQUIRED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"


class InvalidTransitionError(Exception):
    """Raised when a requested state transition isn't allowed. The
    caller's draft is returned unmodified — this is the failure-safe
    path Test 12 exercises."""


# Every allowed transition, explicitly. Anything not listed here is
# refused — this is an allowlist, not a denylist, deliberately: a new
# status added later must be reasoned about here before it can do
# anything, rather than being permitted by omission.
_ALLOWED_TRANSITIONS = {
    ApprovalStatus.PENDING_APPROVAL: {
        ApprovalStatus.APPROVED,
        ApprovalStatus.REJECTED,
        ApprovalStatus.EDIT_REQUIRED,
        ApprovalStatus.CANCELLED,
    },
    ApprovalStatus.EDIT_REQUIRED: {
        ApprovalStatus.APPROVED,
        ApprovalStatus.REJECTED,
        ApprovalStatus.CANCELLED,
    },
    ApprovalStatus.APPROVED: {
        ApprovalStatus.EXECUTED,
        ApprovalStatus.CANCELLED,
    },
    ApprovalStatus.REJECTED: set(),
    ApprovalStatus.EXECUTED: set(),
    ApprovalStatus.CANCELLED: set(),
}


def _now():
    return datetime.now(timezone.utc).isoformat()


def transition(draft, to_status, actor, note=None):
    """draft is a dict with at least {"approval_status": ...,
    "audit": [...]}. Mutates and returns draft on success. Raises
    InvalidTransitionError and leaves draft untouched on failure.
    actor is required and non-empty on every call — there is no
    transition this function will perform without a named human."""
    if not actor or not actor.strip():
        raise InvalidTransitionError("a named actor is required for every approval-state transition")

    current = ApprovalStatus(draft["approval_status"])
    target = ApprovalStatus(to_status)

    if target not in _ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidTransitionError(
            f"cannot transition from {current.value} to {target.value}"
        )

    if target == ApprovalStatus.EXECUTED and current != ApprovalStatus.APPROVED:
        # Redundant with the table above, kept as an explicit second
        # check because this is the one transition a bug here would
        # be most dangerous to get wrong.
        raise InvalidTransitionError("EXECUTED may only be reached from APPROVED")

    draft["approval_status"] = target.value
    draft.setdefault("audit", []).append({
        "timestamp": _now(),
        "event": f"{current.value} -> {target.value}",
        "actor": actor,
        "note": note,
    })
    if target == ApprovalStatus.APPROVED:
        draft["approved_by"] = actor
        draft["approved_at"] = _now()
        draft["decision_note"] = note
    return draft


def approve(draft, actor, note=None):
    return transition(draft, ApprovalStatus.APPROVED, actor, note)


def reject(draft, actor, note=None):
    return transition(draft, ApprovalStatus.REJECTED, actor, note)


def request_edit(draft, actor, note=None):
    return transition(draft, ApprovalStatus.EDIT_REQUIRED, actor, note)


def cancel(draft, actor, note=None):
    return transition(draft, ApprovalStatus.CANCELLED, actor, note)


def mark_executed(draft, actor, note=None):
    """Records that the human performed this action themselves,
    outside this system. This function has no side effect on the
    outside world — it cannot, since nothing in this codebase talks to
    LinkedIn, email, or any other external service. It only updates
    this record to reflect a fact the human is reporting."""
    return transition(draft, ApprovalStatus.EXECUTED, actor, note)


def new_draft(content):
    """Every draft starts here, at PENDING_APPROVAL, with an empty
    audit trail — never any other starting state."""
    return {
        "content": content,
        "approval_status": ApprovalStatus.PENDING_APPROVAL.value,
        "approved_by": None,
        "approved_at": None,
        "decision_note": None,
        "audit": [{
            "timestamp": _now(),
            "event": "drafted",
            "actor": "opportunity-intelligence/runtime/generate.py",
            "note": None,
        }],
    }
