# Proposal Library

Nine reusable proposal templates, one per practice area. Every
template shares the same structure so a proposal always reads the
same way regardless of domain, and every `{{PLACEHOLDER}}` is meant to
be filled automatically from `demand-intelligence/opportunity-schema.json`
and `06-CRM/company-intelligence.json` plus whatever is specific to
the conversation.

## Templates

- `ai-governance-proposal-template.md`
- `technology-risk-proposal-template.md`
- `grc-proposal-template.md`
- `third-party-risk-proposal-template.md`
- `security-governance-proposal-template.md`
- `dora-proposal-template.md`
- `eu-ai-act-proposal-template.md`
- `fractional-advisory-proposal-template.md`
- `enterprise-consulting-proposal-template.md`

## Shared Structure

Every template has the same sections: Understanding the Challenge,
Proposed Approach (via OPERA), Scope of Work, Deliverables, Timeline,
Fees, Why AI for U&I, Next Steps. Only the challenge framing, the
approach detail and the deliverable subset change per domain.

## Deliverable Vocabulary

Deliverables are drawn from the same canonical artefact vocabulary
used across the practice, not invented per proposal: Governance
Charter, Operating Model, RACI Matrix, Risk Register, Evidence
Register, Decision Framework, Implementation Roadmap, Board Reporting
Pack. Each template lists the subset most relevant to that domain;
adjust for the actual scope agreed with the client.

## Programmatic Reuse (Sprint 23 — Engagement Templates)

`proposal-content-library.json` is a faithful, structured extraction
of each template's `challengeFraming` and `keyDeliverables` — never a
new, independently-invented deliverable — keyed by the identical
filename `service-mapping/runtime/generate.py`'s own
`determine_proposal_template()` already selects.
`sales-director/runtime/prepare.py`'s `regulatory_deliverables()` looks
that up and, when service-mapping has matched a template for an
opportunity, replaces the Executive Proposal's generic Deliverables
boilerplate with this real, framework-specific list. These `.md` files
remain the master reference copies the founder can still open
directly; edit those first if the underlying pitch changes, and keep
`proposal-content-library.json` in sync by hand.
