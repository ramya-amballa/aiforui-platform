# Opportunity Intelligence — Design Model

**Status: experimental, manually invoked, not wired into the daily
Orchestrator run.** Not an AOS employee in the `orchestrator-config.json`
sense — no `dependsOn`, no daily execution, no CEO Advisor section yet.
Evaluated against the first 20 real opportunities before any further
integration is even considered, per `AOS-PRACTICE-VALIDATION-ROADMAP.md`'s
own Platform Governance bar for a new employee (2+ real engagements'
worth of demonstrated need, approved at a Quarterly Review — not met
yet, because zero real opportunities have been processed).

This document is also the record of the approval conditions this
component was built under. Every one of the twelve numbered conditions
below is a real constraint on the code, not aspirational text:

1. Public-web research stays in v1.
2. No LinkedIn login/API dependency.
3. No scraping private/authenticated information.
4. No sending/applying externally.
5. Human approval remains mandatory.
6. Master professional profile is authoritative.
7. Evidence must support scoring and recommendations.
8. Existing AOS employees remain untouched.
9. No orchestrator/CEO integration yet.
10. No Architecture Constitution or ADR changes.
11. The 12 required tests exist before this is declared complete.
12. Stop after implementation and show files, test results, sample
    output, and the safety/approval test before any further
    architectural change.

## Why this doesn't scrape anything

Every existing AOS employee that touches external data reads from a
sanctioned, structured source — Demand Intelligence's RSS/Atom Demand
Signals connector, Tender Intelligence's procurement feeds — never live
scraping of an authenticated or ToS-restricted site. This component
follows the same pattern. It does not fetch LinkedIn, a careers page,
or anything else itself.

**The research inbox is the boundary.** `runtime/config/research-inbox/`
holds one plain JSON file per candidate opportunity, written by a human
or by a Claude session with web-research tools *sitting outside this
runtime component* — the research inbox schema (below) is exactly what
that person or session should fill in after finding something on a
public job posting, a company's careers page, a public LinkedIn search
result, a press release, or similar. This component's own code never
logs in, never authenticates, never automates a browser, and never
writes to any external service. It only reads inbox files, scores them,
drafts from them, and queues drafts for human approval.

This means DISCOVER (Phase in the original spec) happens outside this
codebase. NORMALIZE onward — everything from here to APPROVAL — is
this component.

## Data model

One record per opportunity, written to
`output/opportunity-intelligence/opportunity-intelligence-feed.json`.
Nested, per the approved data model, not flat:

```json
{
  "opportunity_id": "string — stable, derived from company+role+discovered_at",
  "opportunity_type": "EMPLOYMENT | CONSULTING | RELATIONSHIP | PARTNERSHIP | REFERRAL",
  "source": "string — e.g. 'company careers page', 'public LinkedIn search'",
  "source_url": "string or null",
  "company": "string",
  "company_url": "string or null",
  "role_or_signal": "string — job title, or the signal itself for non-employment types",
  "discovered_at": "ISO 8601 date",
  "location": "string or null",
  "remote_status": "string or null",
  "industry": "string or null",
  "evidence": ["array of strings — every fact the scoring below cites, so a score is always traceable"],
  "company_intelligence": {
    "matched_existing_record": "boolean — true if this company already exists in account-intelligence-feed.json, fractional-advisory-radar-feed.json, relationship-profiles.json, or 06-CRM/company-intelligence.json",
    "source_employee": "string or null — which existing AOS employee's record this was read from, never recomputed"
  },
  "decision_makers": [
    {
      "name": "string or GapMarker.NOT_ESTABLISHED — never invented",
      "role": "string",
      "why_relevant": "string",
      "relationship_strength": "string or GapMarker.NOT_TRACKED",
      "likely_influence": "string",
      "recommended_approach": "string"
    }
  ],
  "ramya_fit": {
    "score": "number 0-100, employment opportunities only; null otherwise",
    "verified_matches": ["profile entry ids from ramya-professional-profile.json's verified_experience"],
    "transferable_matches": ["profile entry ids from transferable_experience"],
    "knowledge_matches": ["profile entry ids from knowledge_training"],
    "claim_requires_verification": ["profile entry ids from claims_requiring_verification"],
    "gaps": ["string — named, specific gaps, never glossed over"]
  },
  "consulting_assessment": {
    "score": "number 0-100, consulting opportunities only; null otherwise",
    "why_now": "string or GapMarker.NOT_ESTABLISHED",
    "who_to_contact": "string or GapMarker.NOT_ESTABLISHED",
    "why_this_person": "string or GapMarker.NOT_ESTABLISHED",
    "problem_to_lead_with": "string or GapMarker.NOT_ESTABLISHED",
    "what_not_to_sell_yet": "string or GapMarker.NOT_ESTABLISHED",
    "recommended_first_step": "string — defaults to relationship-first per the approved strategy"
  },
  "priority": "string — High, Medium, Low, derived deterministically from score + evidence strength",
  "recommended_action": "string",
  "outreach_strategy": "string",
  "drafts": {
    "resume": {"content": "string or null", "approval_status": "PENDING_APPROVAL"},
    "cover_letter": {"content": "string or null", "approval_status": "PENDING_APPROVAL"},
    "connection_request": {"content": "string or null", "approval_status": "PENDING_APPROVAL"},
    "dm": {"content": "string or null", "approval_status": "PENDING_APPROVAL"},
    "follow_up": {"content": "string or null", "approval_status": "PENDING_APPROVAL"}
  },
  "approval": {
    "status": "PENDING_APPROVAL | APPROVED | REJECTED | EDIT_REQUIRED | EXECUTED | CANCELLED — this is per-draft in practice (see below), this top-level field reflects the opportunity's own overall state",
    "approved_by": "string or null",
    "approved_at": "ISO 8601 timestamp or null",
    "decision_note": "string or null"
  },
  "outcome": "string or GapMarker.NOT_ESTABLISHED",
  "next_action": "string",
  "last_updated": "ISO 8601 timestamp",
  "audit": ["array of {timestamp, event, actor} — every state transition, append-only"]
}
```

Each of the five `drafts` entries carries its **own** `approval_status`
— approving a connection request never implies the resume is approved.
The top-level `approval.status` is a convenience rollup only.

## READY_TO_SEND ≠ APPROVED

Sales Director's existing three-word readiness signal (`Proposal
Ready`, `Needs Review`, `Ready To Send`) is untouched and means exactly
what it always has — a *quality* judgement about whether a package is
well-formed. It is not, and has never been, an authorization to send
anything; the founder already sends everything by hand today. This
component's `approval_status` is a different, new concept: an
authorization gate for the one thing that doesn't exist anywhere in
AOS yet — actually acting on the outside world. A draft can be
`Ready To Send` (Sales Director's judgement) and still sit at
`PENDING_APPROVAL` (this component's judgement) until Ramya explicitly
approves it. The two are never conflated in the code.

## The state machine

```
PENDING_APPROVAL --approve--> APPROVED --mark_executed--> EXECUTED
PENDING_APPROVAL --reject--> REJECTED
PENDING_APPROVAL --request_edit--> EDIT_REQUIRED --approve--> APPROVED
PENDING_APPROVAL --cancel--> CANCELLED
APPROVED --cancel--> CANCELLED
```

Every transition requires an explicit, human-supplied `actor` and is
invoked only via `generate.py`'s CLI flags (`--approve`, `--reject`,
`--request-edit`, `--mark-executed`, `--cancel`) — never as a side
effect of the normal read/score/draft run. `mark_executed` additionally
requires the actor to affirmatively state the action was already taken
*by them, outside this system* — this codebase contains no function
that sends, posts, or submits anything, so there is no code path
`mark_executed` could be triggering other than recording a fact.
Attempting any transition into `EXECUTED` from a state other than
`APPROVED` raises `InvalidTransitionError` and changes nothing — this
is Test 12.

## Ramya's professional profile — the authoritative source

`runtime/config/ramya-professional-profile.json` ships empty (four
empty arrays, fully documented schema) — exactly the same "founder-
maintained, empty until populated" pattern as `relationship-
profiles.json` and `delivery-log.json` elsewhere in AOS. Never
fabricated, never seeded with placeholder achievements.

Four categories, and the rule the founder set is enforced in code, not
just in the doc: **only `verified_experience` entries may be cited as
fact in a resume or outreach draft.** `transferable_experience` and
`knowledge_training` may inform `ramya_fit.gaps` and framing language,
but `resume_tailoring.py` refuses to draft a factual claim from either
— it can say "relevant training in X" (an honest characterization) and
must never render it as "implemented X." `claims_requiring_verification`
entries are never used in any draft at all until moved to
`verified_experience` by the founder.

**The profile is read-only to this entire component, with no
exception, today or in any future extension.** `load_profile()` in
`opportunity_scoring.py` is the only function anywhere in this
codebase that references the profile's path, and it only opens the
file for reading — verified by `tests/test_profile_is_read_only.py`,
which hashes the real shipped profile file before and after a full
discovery run and fails if a single byte or the mtime changed, greps
every module's own source for a write pattern near the filename, and
fails if any function named anything like `save_profile`/
`write_profile`/`update_profile` is ever defined. This is enforced as
a real regression test, not only documented as an intention.

**If a future capability is ever built that would suggest a profile
change** — for example, noticing after a real, closed engagement that
a `claims_requiring_verification` entry should be promoted to
`verified_experience`, or that a verified entry is missing a tag that
would have mattered for a real opportunity — that suggestion must be
written to a separate artifact (e.g. `output/opportunity-intelligence/
profile-change-proposals.json`), never to the profile file itself, and
must use the exact same `approval_queue.py` state machine already
built for outreach drafts: it starts at `PENDING_APPROVAL`, and only
an explicit, human-invoked acceptance (mirroring `generate.py`'s
`--approve` pattern) may ever cause the profile file to be edited —
and even then, by the founder's own hand or an explicitly separate,
clearly-logged write step, never as a side effect of a normal
discovery run. No such capability exists today; this paragraph is the
contract it must satisfy if one is ever proposed, not a roadmap item.

## Consulting / relationship / partnership / referral scoring

Never recomputed if a real answer already exists. Before scoring a
company itself, this component checks — read-only — whether it already
has a record in `account-intelligence-feed.json`,
`fractional-advisory-radar-feed.json`, or `relationship-profiles.json`,
and if so, uses that real, already-computed value
(`company_intelligence.source_employee` records which one). Only when
no existing record exists does it compute a bounded heuristic
directly from the research-inbox entry's own stated evidence — and that
heuristic is always visibly weaker-labelled than a real cross-referenced
score, never presented as equally confident.

## One company, several opportunity types

A single research-inbox entry can — and should — be capable of
producing more than one `Opportunity` record: a senior employment
opportunity, a consulting angle, a relationship with a named decision
maker, all from the same company, each scored on its own terms. This
is deliberate, per the founder's own framing: the goal is *Opportunity
Intelligence*, not a job-application machine.
