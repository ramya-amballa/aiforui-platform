# Governance Charter

This charter describes how the AI Governance Workbench is governed, not what it contains. `VISION.md` says why the project exists; `ONTOLOGY.md` says what its terms mean; this document says who is responsible for it and how decisions about it get made — including after anyone reading this today has moved on.

## Mission

To be a public, citable, continuously-maintained reference connecting real AI governance incidents to the decisions, patterns, controls, evidence, and board-level questions they imply — maintained to a standard a regulator, auditor, or board could rely on, and free for anyone to use.

## Scope

In scope: the canonical dataset (`/data`), the ontology and schemas that govern it (`/schemas`, `/relationships`), the tooling that validates and audits it (`/validators`, `/editorial`), the public interface onto it (`/explorer`), and the governance documents that describe how all of the above is maintained (this document and its siblings).

Out of scope, by design, not by oversight: original policy advocacy, compliance consulting for a specific organization, vendor rankings or endorsements, and anything that would make the Workbench a party with a stake in the outcome of the governance questions it documents. See `VISION.md`'s "What this project is NOT" and `CONFLICT_OF_INTEREST.md`.

## Editorial authority

Editorial authority over the canonical dataset rests with the project's maintainers, exercised through the review process defined in `REVIEW_PROCESS.md`. No single contribution — including one authored or drafted with AI assistance — becomes canonical without a maintainer's review, per the AI-authorship rule in `ONTOLOGY.md`. Editorial authority is a responsibility exercised on the dataset's behalf, not a personal credential; it transfers with the maintainer role, not with any individual's continued involvement.

## Maintainers

A maintainer is anyone with merge authority over `/data`, `/schemas`, `/relationships`, `/validators`, `/editorial`, or `/explorer`. Maintainer responsibilities:

- Enforce the review bar in `REVIEW_PROCESS.md` and the standards in `EDITORIAL_POLICY.md` and `CITATION_POLICY.md` — consistently, not selectively.
- Disclose anything `CONFLICT_OF_INTEREST.md` requires before reviewing or merging content touching that conflict.
- Treat the ontology and schemas as stable contracts (`VERSION_POLICY.md`) — changing them is a deliberate, documented act, not a side effect of adding content.
- Leave a record. Every substantive editorial action — a promotion, a correction, a retraction — should be traceable to who did it and why, via `history` entries and PR descriptions, not memory.

The project currently operates with a small maintainer set appropriate to its size. This charter does not fix that number; it fixes the standard any maintainer, present or future, is held to.

## Decision-making principles

1. **The dataset outranks any single contributor's opinion.** A claim stands or falls on its citations, not on who wrote it. See `EDITORIAL_POLICY.md`'s neutrality policy.
2. **Structural rules are enforced by tooling, not judgment calls.** Whether an object is an orphan, whether a relationship triple is valid, whether a citation is present when required — `/validators` decides this the same way every time. Judgment is reserved for what tooling cannot decide: whether a source is credible, whether a reason is substantive, whether an edition is ready.
3. **Changes to the rules themselves require more scrutiny than changes made under them.** Adding an Incident is a normal contribution. Adding a relationship verb, changing a schema, or amending this charter is a governance change — see `VERSION_POLICY.md` for what that requires.
4. **When in doubt, favor precision over completeness.** A gap the dataset is honest about (see the "known gaps" sections in every edition's release notes) is preferable to a mapping that overstates what's actually known. This is the same principle `VISION.md` states editorially; here it's stated as how disagreements among maintainers should be resolved when they arise.
5. **Reversibility matters.** Every canonical change is a git commit. Nothing about this project's governance should ever require trusting a maintainer's memory over the repository's actual history.

## Long-term stewardship

This charter is written on the assumption that the project should be able to outlive its original maintainers without a crisis. Concretely, that means:

- **Nothing is a single point of failure by design.** The dataset is plain files in a git repository, not a database only one person can access. The Explorer is a static build derivable from `/data` alone (`ONTOLOGY.md`'s Canonical Principle). Anyone with a git clone and this documentation set has everything needed to continue the project, fork it, or audit it — including someone who was never involved in building it.
- **Institutional memory lives in documents, not people.** The reasoning behind every major decision is written down — in `VISION.md`, `METHODOLOGY.md`, and the "why" sections of `/docs` — specifically so a future maintainer doesn't have to guess or ask someone who may no longer be reachable.
- **Maintainer succession is expected, not exceptional.** A maintainer stepping back should be a routine event handled by transferring merge authority and updating this document, not a project-ending one. Any maintainer taking on the role inherits the obligations in this charter, not just the permissions.
- **The mission constrains successors, not just founders.** A future maintainer who wanted to turn this into a paid product, a vendor-sponsored ranking, or a policy-advocacy platform would be acting outside this charter's scope, regardless of who they are. Changing the mission itself is possible — projects legitimately evolve — but it should be done explicitly, by amending this document and saying so, never by drift.

## Amending this charter

This document can change. It should change rarely, deliberately, and via the same PR-and-review path as everything else in this repository — a charter that can be quietly edited is not a charter. An amendment should state what changed and why in its own commit, and — for any change to Mission or Scope — should be treated with at least the scrutiny `VERSION_POLICY.md` reserves for a major release.
