# Homepage Copy — Production Draft

Final copy for the Explorer homepage, written to the standard `EDITORIAL_POLICY.md` and `VISION.md` set: institutional, restrained, no marketing language. This document is a **content deliverable, not a code change** — Phase 4's constraints explicitly exclude modifying `/explorer`, so this copy is provided ready to drop into `explorer/app/page.tsx` (and the components it references) in a future, separate pass, rather than implemented now. Everything below maps directly onto the homepage's existing structure so that mapping is mechanical when it's implemented.

## What changed and why

The current homepage copy (in production as of Edition 1.1) is already close to this standard — it was written under the same restraint this document continues. This draft tightens it further and makes sure all four questions the brief asks for are answered explicitly and in order, rather than implied.

## Hero

**Eyebrow / kicker** *(new — small label above the H1, establishing category before the name)*

> An Open Practitioner Reference by AI for U&I

**H1**

> AI Governance Workbench

**Subhead**

> The open knowledge graph connecting real AI governance incidents to the decisions, patterns, controls, evidence, and board-level questions they imply.

*(Why this eyebrow, not "AI Governance Reference": the Workbench is a recognizable project in its own right — not a rebrand, not a separate mission — and this line does the identity work without a wordmark or a design system: it names the project, credits AI for U&I as steward without implying the Workbench is merely a feature of the consulting business, and gives every future consulting, research, or training reference a natural, honest way to point back to it. See `VISION.md`'s independence framing for why this stays a credit line, not a promotional one.)*

**Lede paragraph** *(answers "what is this" and "why does it exist")*

> Every entry here traces to a documented incident, regulatory action, or published framework — never speculation. Each one is mapped through a fixed set of typed relationships to the governance decision it implies, the pattern that would mitigate it, the framework controls it satisfies, the evidence an auditor would ask for, and the question a board should be asking. Nothing is generated; everything is cited, reviewed, and versioned like the reference work it's meant to be.

**Secondary line** *(answers "who is it for" and "how should practitioners use it")*

> Built for the people accountable for AI governance decisions — CISOs, enterprise architects, governance leads, internal auditors, risk and compliance officers, AI product owners, and board advisors — to answer a specific governance question with sources in minutes, not to be read end to end.

## Stats strip

Labels stay factual and undecorated — numbers speaking for themselves is the point:

- **Canonical objects** — *(unchanged)*
- **Incidents** — *(unchanged)*
- **Relationships** — *(unchanged)*

*(Optional fourth stat, if a fourth column is added later: **Average citation score**, sourced live from `editorial:citations` — makes the Editorial Excellence commitment in `VISION.md` visible on the homepage itself, not just in `/docs`. Not required for this draft; noted for a future pass.)*

## "Try asking" chips

Keep the existing mechanism (pre-filled search queries); tighten the example set to lead with governance questions rather than topics, matching the brief's own examples:

> human oversight failures · customer-facing AI · hiring · GDPR · facial recognition · board questions

## Section: entity cards ("Browse the graph")

**Section heading**

> Browse by entity type

**Section subhead** *(new — one line orienting a first-time visitor before six cards)*

> Six connected object types. Every one links back to the Governance Decision it informs or implements.

Per-card descriptions — tightened from current copy, each stating what the type *is for*, not just what it *is*:

- **Governance Decisions** — "The organizing unit of the graph: a concrete, testable governance commitment, and the reason every other object type exists."
- **Incidents** — "Real, independently-verified events, included for the governance lesson each one demonstrates — not for how widely it was reported."
- **Design Patterns** — "The concrete way a decision gets implemented in practice, one primary pattern per decision by design."
- **Framework Controls** — "Provisions drawn from real regulatory and standards frameworks, mapped only where genuinely and directly applicable."
- **Evidence Types** — "What an auditor or regulator would actually ask to see to confirm a decision was followed, not just declared."
- **Board Questions** — "One concise, executive-actionable question per governance concept, ready for the boardroom."

## Footer line

> AI Governance Workbench is a public, independently-maintained reference. It accepts no vendor sponsorship and holds no editorial position beyond what its cited evidence supports. See `GOVERNANCE_CHARTER.md` and `EDITORIAL_POLICY.md`.

*(Current footer line is close to this already; this version makes the independence statement explicit on the page itself, not just in the governance documents, per the "How practitioners should use it" trust signal a first-time visitor needs before they'll cite anything from the site.)*

## What this draft deliberately avoids

No superlatives ("the definitive," "the world's most comprehensive"), no calls to action beyond the search/browse affordances already in the interface, no customer logos or testimonials (there are none, and inventing the impression of them would violate `EDITORIAL_POLICY.md`'s neutrality policy), and no copy implying the dataset is larger or more complete than the live stats already show — the numbers are the credibility signal; the prose should not compete with them.
