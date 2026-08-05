# Vision

If you're reading this in five years and nothing else in this repository, read this page first. Everything else — `ONTOLOGY.md`, `/schemas`, `/validators`, `/editorial`, `/explorer` — is downstream of the decisions on this page. If a future change ever seems to require breaking with something written here, that's a signal to stop and think, not a reason to quietly route around it.

## Why this project exists

AI governance advice today is scattered across regulator PDFs, consultancy decks, vendor whitepapers, and news coverage of the incident that prompted each one — none of it linked together, none of it citable at the level of a specific claim, most of it optimized to sell something. There is no equivalent, for AI governance, of what MDN Web Docs is for the web platform or what MITRE ATT&CK is for adversary tactics: a public, structured, continuously-maintained reference that practitioners actually trust and cite.

The AI Governance Workbench exists to become that reference. Not by writing new opinions about how AI should be governed, but by doing the unglamorous work of taking what has *actually happened* — real incidents, real regulatory actions, real court rulings — and connecting each one to the governance decision it implies, the pattern that would have prevented it, the control it maps to, the evidence an auditor would ask for, and the question a board should be asking. Done enough times, done rigorously, that structure becomes more valuable than any single article summarizing it.

## What problem it solves

A practitioner today cannot quickly answer questions like "what has actually gone wrong with automated hiring tools, and what would have prevented it," or "which NIST AI RMF controls are genuinely relevant to a customer-facing chatbot, not just plausibly related," or "what should our board be asking about this system." Answering these well requires connecting facts that live in different documents, different institutions, different countries, written by people who never intended their work to be cross-referenced with each other. The Workbench's job is to do that connecting once, carefully, so nobody else has to redo it from scratch — and to show the reasoning, not just the conclusion, so the connection itself can be checked.

## Who it serves

Built for practitioners, not casual readers: CISOs, enterprise architects, AI governance leads, internal auditors, risk managers, compliance officers, AI product owners, and board advisors. Every page should shorten the distance between "I have a governance question" and "I have a defensible answer with sources," for someone whose job depends on getting that answer right. If a design choice makes the site more pleasant for a casual visitor at the cost of making it slower for one of these people to find what they need, the practitioner wins.

## Editorial philosophy

Precision over completeness. Evidence over opinion. Curation over aggregation. Semantic clarity over volume. A smaller graph where every edge is defensible beats a larger one padded with plausible-sounding connections.

Concretely: no relationship exists because two concepts merely seemed related — every edge states, in plain language, why it exists. No incident enters the canonical dataset without answering what governance decision it actually involved (not just what happened), what *observable* evidence would demonstrate that decision, which single primary pattern would most directly have prevented the outcome (not every pattern that's vaguely relevant), which framework controls are genuinely and directly applicable (quality over quantity — mapping every incident to every framework inflates the graph without informing anyone), what one board-level question follows, and what confidence should be assigned, with a stated reason. An incident that can't answer these isn't ready, no matter how newsworthy it was.

## Design philosophy

Data-first, git-native, static-site-friendly. The dataset is the asset; every interface onto it is a view that could be deleted and rebuilt from `/data` alone without losing anything — see the Canonical Principle in `ONTOLOGY.md`. No database, because a database hides its write history behind an opaque path and this dataset's credibility depends on every change being a reviewable diff. No backend, because the moment a server exists, so does a second place facts could originate from, and that is precisely the failure mode this project is built to avoid.

Visually and editorially: professional, quiet, restrained. The bar is Microsoft Learn, Stripe's documentation, IBM's Carbon design system, MDN, Linear — density and clarity over decoration, in prose and in interface alike. Nothing here should read like a hobby project or a hackathon demo, because the moment it does, a CISO stops trusting it.

## Why Decisions are the center

Every other entity type is organized in relation to Governance Decisions, not the reverse. An Incident matters because of the decision it provokes. A Pattern matters because it implements a decision. A Control matters because a decision needs to satisfy it. Evidence matters because a decision requires it to be demonstrated. A Board Question matters because a decision implies it. This is deliberate: "what happened" is a news question, and news is not this project's product. "What should we decide, and why" is a governance question, and answering it — durably, with sources — is the product. A graph organized around abstractions like "risks" or "requirements" doesn't by itself imply an action; one organized around Decisions always does.

## What "canonical knowledge" means here

A fact is canonical the moment it lives in `/data`, has passed `/validators`, and — for anything beyond a first draft — has been reviewed by a named human. Confidence (`Verified` / `Reviewed` / `Draft` / `Community` / `Archived`) is stated explicitly on every object precisely so "canonical" never has to mean "certain." An LLM, including the one that built much of this dataset, may draft and propose; it may never cause content to become canonical unsupervised — see "No AI writes canonical data" in `ONTOLOGY.md`. Canonical does not mean permanent, either: `status` tracks whether a record is still current, independent of how much it should be trusted, and a retracted record stays in the dataset as a matter of record rather than disappearing.

## What this project is NOT

- **Not a new governance framework.** It doesn't compete with NIST AI RMF, the EU AI Act, ISO/IEC 42001, or anyone else's framework — it maps *to* them. If the Workbench ever starts inventing its own compliance requirements instead of citing external ones, it has drifted from its purpose.
- **Not a compliance or GRC product.** No audit workflows, no attestation tracking, no vendor risk management. It's a reference you consult, not a system you operate inside.
- **Not a media outlet or blog.** No hot takes, no opinion pieces, no incident coverage optimized for pageviews. Every incident is chosen for the governance lesson it teaches, not its newsworthiness.
- **Not a SaaS product, and not for sale.** Open, public, and free to use is the point — that's what makes citing it credible.
- **Not an AI chatbot answering governance questions from a model's memory.** Every claim traces to a citation a reader can check themselves. If it can't be sourced, it doesn't belong here.
- **Not optimized for casual browsing.** Practitioners under time pressure, not visitors killing five minutes, are who every page is built for.

## Long-term roadmap

Five workstreams, defined deliberately rather than discovered by accident. Status as of this writing:

**1. Editorial Excellence.** The dataset's real KPI is not incident count — it's citation quality. The path is 61 → 80 → 90 → 95: every citation carrying a real locator and excerpt, every relationship edge traceable to the specific source that supports it, until every page is something a regulator could confidently read and verify line by line. Tooling to measure this (`editorial:audit`, `editorial:citations`) exists and the current baseline is documented in `docs/quality-audit-2026-08.md`. Closing the gap itself is research work — re-reading real sources — not something a script can do, and is Edition 1.2's central task.

**2. Executive Language.** Every page should read like something Gartner, Microsoft, or AWS would publish — not like a GitHub repository. This is deliberately left to human editorial judgment rather than automated rewriting: tone is a matter of taste and authority that a deterministic tool shouldn't be trusted to get right at scale, and getting it wrong at scale would be worse than not touching it.

**3. Visual Identity.** Not prettier — more authoritative. The reference points (Microsoft Learn, Stripe Docs, IBM Carbon, MDN, Linear) share a restraint this project should match: no gradients, no marketing illustration, no decorative animation. The Explorer's current design direction points this way; a dedicated pass to hold every page to that bar is still ahead.

**4. Practitioner Assets.** The graph shouldn't only be something you read — it should be something you leave with. Every Decision becoming a jumping-off point for a downloadable AI risk-assessment checklist, an architecture-review worksheet, an evidence-collection template, a board slide, a ready-made set of audit questions — generated deterministically from the same canonical fields, never freehand — is the next concrete step past the Explorer, and likely the point where people start bookmarking the Workbench rather than just visiting it once.

**5. Community Trust.** Before this project opens itself to outside contributors, it needs the policy scaffolding that makes contribution safe to accept: an explicit Editorial Policy, a Contribution Guide (`docs/contributing.md` exists; needs to grow with this), a Version Policy, a Citation Policy (`docs/citation-model.md` covers the schema; a policy document covers the judgment calls around it), a documented Review Process, a Conflict of Interest Policy, a stated Methodology, and Release Notes (`docs/releases/` already does this per edition). Trust has to be built before scale is invited in, not the other way around — a rule this project intends to actually follow when the day comes to open the gate.
