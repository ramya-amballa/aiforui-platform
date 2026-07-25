# Market Intelligence — Classification Model

What `runtime/monitor.py` executes. Every substantive development
(new since `runtime/seen-index.json` last saw it — see "Substantive"
below) is run through six deterministic checks, each producing a
boolean and a short factual reason — never drafted copy. This is the
structured-output boundary the founder set: Market Intelligence decides
*whether* something matters and *to whom*; it never writes the
LinkedIn post, the website copy, or the product brief itself.

## Sources

Thirteen tracked sources, each configured in `runtime/config/sources.json`
with zero or more feed URLs:

| Source | Nature | `domainTags` it carries downstream |
|---|---|---|
| EU AI Act | Regulation | `EU AI Act`, `AI Governance` |
| ISO 42001 | Standard | `AI Governance`, `GRC` |
| NIST AI RMF | Framework | `AI Governance`, `GRC` |
| DORA | Regulation | `DORA`, `Third-Party Risk` |
| GDPR | Regulation | `GRC` |
| CBUAE | Regulator guidance | `AI Governance`, `GRC` |
| RBI | Regulator guidance | `AI Governance`, `GRC` |
| Microsoft AI | Vendor | `ADGL`, `AI Deployment Governance` |
| OpenAI Enterprise | Vendor | `ADGL`, `AI Deployment Governance` |
| Anthropic | Vendor | `ADGL`, `AI Deployment Governance` |
| AI Security | Theme | `Security Governance` |
| AI Governance | Theme | `AI Governance` |
| Responsible AI | Theme | `AI Governance` |

Each source is checked the same way every other AOS collector checks
its sources (`opportunity-hunter/runtime/collectors/`): a real,
working, dependency-free RSS/Atom fetch (`runtime/feeds.py`) against
whatever feed URLs are configured. A source with no feed URL yet prints
"no feed URLs configured, skipping" and returns nothing — connector-
ready, not a placeholder, exactly like `uae_recruiters.py` or
`consulting_firms.py`. No feed URL in this file is guessed; each is
left for the founder to supply and verify, since a wrong guessed URL
that silently 404s is worse than an honest gap.

## Substantive

A development is substantive if its dedup key (`sha256(link, or
source|title when there's no link)`) is not already in
`runtime/seen-index.json`. This is a real, working duplicate check, not
a judgement about editorial significance — Market Intelligence cannot
tell a minor corrigendum from a landmark ruling by title text alone,
and says so rather than pretending otherwise. Everything new is
treated as substantive and run through all six checks below.

## The Six Checks

Each check is a deterministic keyword/source rule against the entry's
title + summary (whole-word matching, the same convention as
`opportunity-hunter/opportunity-relevance-engine.md`, for the same
reason — a 3-letter keyword substring match is a false positive
waiting to happen — with a trailing optional "s" tolerated, e.g. "ai
deployment" also matches "ai deployments", since regulatory text is
plural-heavy and the relevance engine's stricter singular-only matching
would otherwise miss most of it).

| # | Check | Owner it routes to | Default | Overridden true by |
|---|---|---|---|---|
| 1 | Consulting opportunity | `opportunity-hunter` | false | Terms: enforcement action, penalty, fine, compliance deadline, mandatory, must comply, audit requirement, certification required |
| 2 | LinkedIn content | `02-Content-Director` | true | — (default true for every substantive item, per `operating-manual.md`'s trigger rule); flipped false by: corrigendum, typographical, housekeeping, minor amendment |
| 3 | Website update | `02-Content-Director` | false | Terms: supersedes, replaces, new version, revises, updated requirements |
| 4 | New product | `03-Product-Manager` | false | Two or more of: framework, toolkit, assessment, certification, mandatory, requirement (a single generic hit isn't enough — same "isolated buzzword" reasoning as the relevance engine) |
| 5 | Affects ADGL | (recorded, not separately routed) | false | Source is one of Microsoft AI, OpenAI Enterprise, Anthropic (inherently AI-deployment vendors), **or** terms: ai deployment, ai system, ai lifecycle, production ai |
| 6 | Affects OPERA | (recorded, not separately routed) | true | Always true for a substantive entry from any of the thirteen tracked sources — every one of them is, by definition, a governance-relevant development, and OPERA is the umbrella methodology governance work runs through. Recorded for completeness, not treated as a meaningful discriminator on its own. |

Checks 5 and 6 are answered and stored on every `regulatory-log.json`
entry (the founder asked "does this affect ADGL / OPERA" as a
determination to make, not a fifth and sixth routing destination — the
routing list has four members, not six) and carried as context into
whichever of the four routes actually fire, so Product Manager or
Content Director sees *why* something might touch ADGL without Market
Intelligence drafting anything about it.

## Routing (Structured Records Only)

- **`02-Content-Director`**: if check 2 or 3 is true, append a
  structured entry to `02-Content-Director/content-brief-queue.json` —
  which trigger, which check(s) fired, the source link, `affectsADGL`/
  `affectsOPERA` context. No Key Point, no Supporting Detail, no Call
  to Action — those are `content-brief-template.md` fields Content
  Director (a human today, `Content Director Runtime` once built)
  fills in from judgement, not from a template Market Intelligence
  pre-writes.
- **`03-Product-Manager`**: if check 4 is true, append an entry to
  `03-Product-Manager/product-backlog.json` using its own existing
  schema, `signalSource: "Market Intelligence"`, `proposedFormat: null`
  and `score: null` — matching a format and a score is
  `product-evaluation-framework.md`'s job, not Market Intelligence's.
  The entry is a real, valid backlog row per the schema that already
  names "Market Intelligence" as a valid `signalSource`; it just
  arrives unscored, exactly as any other newly-flagged candidate would
  before evaluation.
- **`opportunity-hunter`**: if check 1 is true, write a normal
  opportunity record to `opportunity-hunter/runtime/inbox/`, in the
  exact JSON shape `ingest.py`'s own docstring already documents
  (`sourceCategory: "Compliance Programme"`, `domainTags` from the
  table above, `scopedEngagement: false` — this is a general
  market-wide signal, not a named scoped ask). The next Orchestrator
  run's Opportunity Hunter step scores, classifies and routes it
  through the exact same relevance engine and scoring model every
  other opportunity goes through. Market Intelligence does not score
  or classify this itself.
- **`09-CEO-Advisor`**: every substantive entry, regardless of which
  checks fired, gets one compact row in
  `runtime/output/ceo-advisor-feed.json` — id, source, summary link,
  and the six check results. CEO Advisor reads the six booleans, never
  a draft.

## Opportunity Handoff Scores

`opportunity-scoring-engine.md`'s eleven dimensions need a 0-10 value
each before Opportunity Hunter's existing, unmodified scoring can run.
A market-wide regulatory signal has no specific company or contact yet,
so these are conservative heuristics — the same honesty convention as
the Collection Engine's `heuristic_scores()`
(`opportunity-hunter/runtime/collectors/common.py`): `expectedRevenue`
5, `probabilityOfWinning` 3 (lower than a named lead — nobody specific
has been contacted yet), `strategicValue` 7 if check 1 fired else 5,
`relationshipValue` 2, `timeRequired` 6, `geography` 6,
`remoteCompatibility` 8, `alignmentAIforUIServices` 8,
`alignmentADGL` 8 if check 5 (ADGL) is true else 4, `alignmentOPERA` 8,
`longTermRelationshipPotential` 5. The record is written with
`autoScored: true`, so a human — or Opportunity Hunter's own downstream
consumers — knows these are estimates to verify, not a finished
judgement.

## Worked Example

A tracked NIST AI RMF feed entry: title "NIST publishes mandatory AI
Risk Management Framework certification requirement for federal AI
deployments", summary mentions "enforcement" and "audit requirement".

- Check 1 (consulting): "audit requirement" matches → **true** → an
  opportunity record is written to `opportunity-hunter/runtime/inbox/`.
- Check 2 (LinkedIn): substantive, no minor-update override → **true**
  → queued to Content Director.
- Check 3 (website): no supersedes/replaces/revises term → **false**.
- Check 4 (new product): "mandatory", "certification", "requirement" —
  three hits, ≥ 2 → **true** → queued to Product Manager, unscored.
- Check 5 (ADGL): source is NIST AI RMF, not an inherent AI-deployment
  vendor, but "ai deployment" appears in the title → **true**.
- Check 6 (OPERA): **true**, always, per the rule above.

This entry is logged once in `regulatory-log.json` with all six
results, and produces three routed records (Opportunity Hunter, Content
Director, Product Manager) plus one CEO Advisor feed row — four
structured hand-offs from one development, none of them drafted
content.

## What This Runtime Does Not Do

- Does not draft a LinkedIn post, a newsletter issue, website copy, or
  a product brief. It flags that one is warranted and why.
- Does not score or format a Product Manager candidate — that's
  `product-evaluation-framework.md`'s job, not built yet as runtime
  (see the founder's own sequencing: Content Director Runtime, Product
  Manager Runtime, Revenue Hunter Runtime and CRM Runtime come after
  this one).
- Does not score or classify the opportunity it hands to Opportunity
  Hunter — `opportunity-scoring-engine.md`'s existing, unmodified
  engine does that on the next run.
- Does not guess a feed URL for any source. Every one is left empty
  until the founder supplies and verifies it.
