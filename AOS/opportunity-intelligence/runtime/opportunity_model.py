"""
Opportunity Intelligence — Opportunity record builder

Assembles one full Opportunity record (the nested shape documented in
opportunity-intelligence-model.md) from a single research-inbox entry,
calling into opportunity_scoring/resume_tailoring/outreach_drafting for
each piece. This module does no scoring or drafting itself — it only
wires the pieces together and is the one place the record's shape is
defined, so every field name is decided here once.
"""

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import approval_queue  # noqa: E402
import opportunity_scoring as scoring  # noqa: E402
import outreach_drafting as drafting  # noqa: E402
import resume_tailoring  # noqa: E402

VALID_OPPORTUNITY_TYPES = {"EMPLOYMENT", "CONSULTING", "RELATIONSHIP", "PARTNERSHIP", "REFERRAL"}


def _now():
    return datetime.now(timezone.utc).isoformat()


def make_opportunity_id(inbox_entry):
    """Deterministic — the same research-inbox entry always yields the
    same id, so re-running generate.py on unchanged input never creates
    a duplicate record (this is the Test 8 property)."""
    basis = f"{inbox_entry.get('company', '')}|{inbox_entry.get('role_or_signal', '')}|{inbox_entry.get('discovered_at', '')}"
    return "opp-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]


def validate_inbox_entry(inbox_entry):
    """Required-field check. Returns a list of problems; empty means
    valid. This is deliberately separate from schema_validator.py's
    own structural check (that validates the written feed's shape;
    this validates a single inbox entry before it becomes a record)."""
    problems = []
    if inbox_entry.get("opportunity_type") not in VALID_OPPORTUNITY_TYPES:
        problems.append(f"invalid or missing opportunity_type: {inbox_entry.get('opportunity_type')!r}")
    if not inbox_entry.get("company"):
        problems.append("missing required field: company")
    if not inbox_entry.get("source"):
        problems.append("missing required field: source")
    return problems


def build_opportunity(inbox_entry, profile, config, existing_feeds):
    """inbox_entry has already passed validate_inbox_entry(). Returns
    a full Opportunity record, brand new (all drafts at
    PENDING_APPROVAL) — merging with any existing record for the same
    id is the caller's (generate.py's) job, not this function's."""
    opportunity_type = inbox_entry["opportunity_type"]
    opportunity_id = make_opportunity_id(inbox_entry)

    decision_makers = scoring.derive_decision_makers(inbox_entry, config)

    ramya_fit = {"score": None, "verified_matches": [], "transferable_matches": [], "knowledge_matches": [], "claim_requires_verification": [], "gaps": []}
    consulting_assessment = {"score": None, "why_now": None, "who_to_contact": None, "why_this_person": None,
                              "problem_to_lead_with": None, "what_not_to_sell_yet": None, "recommended_first_step": None}
    resume_draft_content, cover_letter_content = None, None

    if opportunity_type == "EMPLOYMENT":
        fit = scoring.score_employment_fit(inbox_entry, profile, config)
        ramya_fit = {k: v for k, v in fit.items() if not k.startswith("_")}
        tailoring = resume_tailoring.analyze_resume_tailoring(inbox_entry, profile)
        resume_draft_content = resume_tailoring.draft_resume(inbox_entry, profile, tailoring)
        cover_letter_content = resume_tailoring.draft_cover_letter(inbox_entry, profile, tailoring)
        score = fit["score"]
    elif opportunity_type in ("CONSULTING", "PARTNERSHIP"):
        consulting_assessment = scoring.assess_consulting_opportunity(inbox_entry, config, existing_feeds)
        score = consulting_assessment.get("score") or 0
    else:  # RELATIONSHIP, REFERRAL
        score = inbox_entry.get("relationship_health_score", 0)

    priority = scoring.derive_priority(score or 0, config)
    recommended_action = (
        scoring.derive_employment_recommendation(score, config) if opportunity_type == "EMPLOYMENT"
        else "RELATIONSHIP_FIRST" if opportunity_type in ("CONSULTING", "RELATIONSHIP", "PARTNERSHIP", "REFERRAL")
        else "REVIEW"
    )

    evidence_summary = "; ".join(inbox_entry.get("evidence_notes", [])) or "Not established"

    drafts = {
        "resume": approval_queue.new_draft(resume_draft_content) if opportunity_type == "EMPLOYMENT" else approval_queue.new_draft(None),
        "cover_letter": approval_queue.new_draft(cover_letter_content) if opportunity_type == "EMPLOYMENT" else approval_queue.new_draft(None),
        "connection_request": drafting.draft_connection_request(inbox_entry, decision_makers, evidence_summary),
        "dm": (
            drafting.draft_consulting_conversation_opener(inbox_entry, decision_makers, consulting_assessment)
            if opportunity_type in ("CONSULTING", "PARTNERSHIP")
            else drafting.draft_initial_relationship_message(inbox_entry, decision_makers, evidence_summary)
        ),
        "follow_up": drafting.draft_follow_up(inbox_entry, decision_makers),
    }
    if opportunity_type == "EMPLOYMENT":
        drafts["job_outreach"] = drafting.draft_job_related_outreach(inbox_entry, decision_makers, evidence_summary)
    if opportunity_type == "REFERRAL":
        drafts["referral_request"] = drafting.draft_referral_request(inbox_entry, decision_makers)

    return {
        "opportunity_id": opportunity_id,
        "opportunity_type": opportunity_type,
        "source": inbox_entry.get("source"),
        "source_url": inbox_entry.get("source_url"),
        "company": inbox_entry.get("company"),
        "company_url": inbox_entry.get("company_url"),
        "role_or_signal": inbox_entry.get("role_or_signal"),
        "discovered_at": inbox_entry.get("discovered_at", _now()),
        "location": inbox_entry.get("location"),
        "remote_status": inbox_entry.get("remote_status"),
        "industry": inbox_entry.get("industry"),
        "evidence": inbox_entry.get("evidence_notes", []),
        "company_intelligence": {
            "matched_existing_record": consulting_assessment.get("_source") is not None,
            "source_employee": consulting_assessment.get("_source"),
        },
        "decision_makers": decision_makers,
        "ramya_fit": ramya_fit,
        "consulting_assessment": {k: v for k, v in consulting_assessment.items() if not k.startswith("_")},
        "priority": priority,
        "recommended_action": recommended_action,
        "outreach_strategy": "Relationship-first" if recommended_action != "APPLY" else "Direct application",
        "drafts": drafts,
        "approval": {"status": "PENDING_APPROVAL", "approved_by": None, "approved_at": None, "decision_note": None},
        "outcome": "Not established",
        "next_action": recommended_action,
        "last_updated": _now(),
        "audit": [{"timestamp": _now(), "event": "opportunity created", "actor": "opportunity-intelligence/runtime/generate.py", "note": None}],
    }
