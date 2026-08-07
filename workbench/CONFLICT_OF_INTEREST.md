# Conflict of Interest Policy

The AI Governance Workbench's value depends on a reader being able to trust that no entry exists, is worded a particular way, or is excluded because of who benefits. This policy defines what counts as a conflict of interest for anyone contributing to or maintaining the dataset, and how it's managed when one exists. It is the operational counterpart to the independence statement in `EDITORIAL_POLICY.md`.

## Scope

Applies to maintainers (anyone with merge authority, per `GOVERNANCE_CHARTER.md`) and to any contributor whose submission concerns an organization, product, vendor, or matter they have a relevant relationship with. A conflict of interest is not a disqualification from contributing — it's a disclosure obligation and, where the conflict is direct, a recusal obligation.

## Commercial relationships

A maintainer or contributor with a commercial relationship to an organization named in a canonical object — as a current or recent employee, contractor, investor, board member, or paid consultant — discloses that relationship before authoring, reviewing, or approving content about that organization. Disclosure is recorded in the relevant pull request; it does not need to be published inside the canonical object itself (the dataset documents incidents and decisions, not contributors' biographies), but the record must exist and be checkable.

## Vendor neutrality

The Workbench does not accept payment, in-kind benefit, early access, or preferential treatment from any vendor in exchange for inclusion, exclusion, favorable framing, or expedited review of content concerning that vendor. Framework Controls, Patterns, and Decisions are included because they are genuinely applicable to documented incidents (see `EDITORIAL_POLICY.md`'s neutrality policy and `CITATION_POLICY.md`), never because a vendor whose product implements them requested inclusion. This holds regardless of whether the vendor is a subject of an incident, a provider of a control framework, or a company otherwise mentioned in the dataset.

## Personal affiliations

A maintainer's personal affiliations — board memberships, advisory roles, close family relationships with an organization's leadership, active litigation involving a named party — are disclosed under the same standard as commercial relationships above. The test is not whether the affiliation would actually bias the content, but whether a reasonable reader, knowing about it, would want to know before trusting the maintainer's judgment on that specific object.

## Employment disclosures

Maintainers disclose their current employer, and any past employer directly relevant to content they're reviewing, in the project's public maintainer record (see `GOVERNANCE_CHARTER.md`'s maintainers section). This is a standing disclosure, updated when employment changes, not a one-time statement — an undisclosed change in employment that creates a new conflict is treated the same as never having disclosed it.

## Consulting relationships

A maintainer or contributor who has provided or is providing paid consulting, advisory, or expert-witness services to an organization named in a canonical object does not review, approve, or promote content about that organization's incidents, decisions, or controls — this is a recusal, not merely a disclosure, because the financial relationship is direct and specific to the subject matter. They may still author a draft (clearly attributed and disclosed), which another, unconflicted maintainer then reviews.

## Sponsored research

The Workbench does not currently accept sponsored or commissioned research, and this policy does not contemplate a process for it. If that ever changes, any sponsored contribution must be labeled as such in the object's `history` and `created_by`/`contributors` fields, must meet the same evidentiary bar as any other contribution under `EDITORIAL_POLICY.md`, and the sponsorship relationship itself must be disclosed in the same public record `GOVERNANCE_CHARTER.md` maintains for maintainers — never accepted silently.

## Editorial independence

No commercial entity, regulator, or government body has editorial authority over this dataset's content, and none is entitled to pre-publication review or veto — including organizations named in incidents the dataset documents. A named organization may submit a correction through the same public process anyone else uses (`EDITORIAL_POLICY.md`'s correction policy), evaluated on the evidence it provides like any other submission, not granted special weight because of who submitted it. This project accepts no funding, sponsorship, or in-kind support conditioned on any control over editorial content, and would decline funding offered on those terms.

## Enforcement

A maintainer who fails to disclose a material conflict, or who reviews/approves content they should have recused from, has that content's promotion reviewed and, if warranted, reversed under `REVIEW_PROCESS.md`'s appeal process — reversal is a correction to the record, not a punitive act, and is handled with the same transparency `EDITORIAL_POLICY.md` requires of any other correction. Repeated or willful failure to disclose is a matter for `GOVERNANCE_CHARTER.md`'s maintainer stewardship provisions.
