"""
Opportunity Intelligence — Outreach Drafting (Phase 9 of the approved spec)

Every draft: PERSON + COMPANY + REAL SIGNAL + RELEVANT RAMYA EVIDENCE +
LOW-FRICTION NEXT STEP. Default strategy is relationship-first, not an
immediate pitch — the founder's own instruction. Every draft this
module produces starts at PENDING_APPROVAL via approval_queue.new_draft()
and nothing here sends anything; these are strings, not network calls.
"""

import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import approval_queue  # noqa: E402


def _person_and_signal(inbox_entry, decision_makers):
    person = decision_makers[0] if decision_makers else None
    person_name = person["name"] if person and person["name"] != "Not established" else None
    person_role = person["role"] if person else "the relevant team"
    signal = inbox_entry.get("evidence", {}).get("headline_signal") or inbox_entry.get("role_or_signal", "")
    return person_name, person_role, signal


def draft_connection_request(inbox_entry, decision_makers, evidence_summary):
    person_name, person_role, signal = _person_and_signal(inbox_entry, decision_makers)
    greeting = f"Hi {person_name}" if person_name else f"Hi (name not yet established — {person_role})"
    content = (
        f"{greeting}, I noticed {inbox_entry.get('company', 'your team')}'s work on {signal or 'this'}. "
        f"{evidence_summary} Would welcome connecting."
    )
    return approval_queue.new_draft(content)


def draft_initial_relationship_message(inbox_entry, decision_makers, evidence_summary):
    person_name, person_role, signal = _person_and_signal(inbox_entry, decision_makers)
    greeting = f"Hi {person_name}" if person_name else f"Hi (name not yet established — {person_role})"
    content = (
        f"{greeting}, following up on the connection — {evidence_summary} "
        f"No specific ask here, just genuinely interested in how you're approaching {signal or 'this'}."
    )
    return approval_queue.new_draft(content)


def draft_consulting_conversation_opener(inbox_entry, decision_makers, consulting_assessment):
    person_name, person_role, _ = _person_and_signal(inbox_entry, decision_makers)
    greeting = f"Hi {person_name}" if person_name else f"Hi (name not yet established — {person_role})"
    problem = consulting_assessment.get("problem_to_lead_with", "the challenge you're navigating")
    content = (
        f"{greeting}, {problem} caught my attention. Not proposing anything yet — "
        f"curious how {inbox_entry.get('company', 'your team')} is thinking about it. "
        f"{consulting_assessment.get('recommended_first_step', 'Open to a short conversation if useful.')}"
    )
    return approval_queue.new_draft(content)


def draft_job_related_outreach(inbox_entry, decision_makers, verified_evidence_summary):
    person_name, person_role, _ = _person_and_signal(inbox_entry, decision_makers)
    greeting = f"Hi {person_name}" if person_name else f"Hi (name not yet established — {person_role})"
    role = inbox_entry.get("role_or_signal", "this role")
    content = (
        f"{greeting}, I'm interested in {role} at {inbox_entry.get('company', 'your organisation')}. "
        f"{verified_evidence_summary} Happy to share more if there's a fit."
    )
    return approval_queue.new_draft(content)


def draft_follow_up(inbox_entry, decision_makers, days_since_last_contact=None):
    person_name, person_role, _ = _person_and_signal(inbox_entry, decision_makers)
    greeting = f"Hi {person_name}" if person_name else f"Hi (name not yet established — {person_role})"
    timing_note = f" (it's been {days_since_last_contact} days)" if days_since_last_contact else ""
    content = f"{greeting}, following up{timing_note} — no pressure, just keeping the conversation open."
    return approval_queue.new_draft(content)


def draft_referral_request(inbox_entry, decision_makers):
    person_name, person_role, _ = _person_and_signal(inbox_entry, decision_makers)
    greeting = f"Hi {person_name}" if person_name else f"Hi (name not yet established — {person_role})"
    content = (
        f"{greeting}, if you know anyone at {inbox_entry.get('company', 'your network')} who's thinking "
        f"about this area, I'd appreciate an introduction — no obligation either way."
    )
    return approval_queue.new_draft(content)
