# Content Director — Content Generation Model

What `runtime/generate.py` executes. Content Director's job starts
where Market Intelligence's ends: Market Intelligence already decided
*whether* something matters (`05-Market-Intelligence/market-intelligence-classification-model.md`'s
six checks); Content Director never re-runs that judgement. It only
decides *which four asset types* a signal should become, assembles a
publish-ready draft for each from real AI for U&I material, and hands
the whole batch to CEO Advisor as one of three statuses. Nothing is
ever published automatically.

## Sources Consumed (Read-Only)

Content Director writes to nothing outside `content-director/`. Every
input below is read as-is, from wherever it already lives:

| Source | What's read | Why this isn't duplicated logic |
|---|---|---|
| `02-Content-Director/content-brief-queue.json` | Market Intelligence's structured triggers: `triggeredBy`, `affectsADGL`, `affectsOPERA` | These booleans are already computed by `monitor.py`'s six checks — Content Director reads them, never recomputes them |
| `05-Market-Intelligence/regulatory-log.json` | The full entry behind each queued trigger (`regulatoryLogRef`), for the real summary and link | Read-only cross-reference, same log Market Intelligence already wrote |
| `opportunity-hunter/opportunity-schema.json` | Every entry with `classification: "Convert into Content"` | This classification is `opportunity-scoring-engine.md`'s own decision tree, made when `recurrencePattern: "content"` is set at ingestion — Content Director consumes the label, it doesn't decide when a theme has recurred |
| `03-Product-Manager/shipped-products-log.json` | Every shipped product, for a product-announcement candidate | Read-only; Product Manager owns what counts as "shipped" |
| `executive-dashboard/executive-dashboard.md` | The `## Today's Priorities` section only | Same read-only text extraction the Orchestrator already does for its Business Impact section — CEO Advisor's own decision model, already executed, quoted verbatim |
| `sales-director/runtime/config/practitioner-bank.json` | Practitioner-experience bullets, the product catalogue, ADGL's five phases, OPERA's five phases | The exact real content bank Sales Director already built from the live site and AOS itself — reused, not re-collected, so there is exactly one source of truth for what AI for U&I actually knows and has done |
| `05-Market-Intelligence/runtime/config/sources.json` | Each source's own `domainTags` (data, not logic) | `content-brief-queue.json` entries don't carry `domainTags` themselves — without this lookup, every regulatory signal would have nothing to match against the content bank and would be forced `Low Value` regardless of real relevance |

## Queue

Every new signal from the five sources above is normalised into
`runtime/queue/content-queue.json`, deduplicated against
`runtime/queue/processed-index.json` (own id per source: the
`content-brief-queue.json` entry's own `id`, the opportunity's `id`,
the shipped product's `id`, or `ceo-priority-{date}` for the once-daily
priority echo — never the same signal queued twice).

## The Seven Determinations

For every queued signal, seven booleans — reusing whichever upstream
signal already answered the question, never re-deriving it:

| # | Determination | Source of the answer |
|---|---|---|
| 1 | LinkedIn post | Market Intelligence's `linkedinContent`; always true for a `Convert into Content` opportunity or a shipped product |
| 2 | Newsletter article | Paired with LinkedIn, per `editorial-operating-system.md`'s existing trigger rule (LinkedIn and newsletter ideas travel together) |
| 3 | Website insight | Market Intelligence's `websiteUpdate`; always true for a shipped product |
| 4 | GitHub update | True only for a shipped product (AI for U&I's public resources live partly on GitHub) |
| 5 | Affects ADGL | Market Intelligence's `affectsADGL` for a regulatory signal; a domain-tag match for an opportunity or product signal |
| 6 | Affects OPERA | Market Intelligence's `affectsOPERA` for a regulatory signal; true by default for everything else — all of this work runs through OPERA |
| 7 | Product announcement | True only for a shipped product |

Determinations 5 and 6 (ADGL/OPERA) are recorded on the queue entry and
carried into every draft's front matter as `also_relevant_to` context.
They do not produce their own files — ADGL and OPERA are internal
methodology, not a publish channel, and inventing a fifth and sixth
output format when only four were asked for would be scope the founder
didn't ask this build to take. Determination 4 (GitHub) is recorded the
same way for now — a real GitHub-update draft format is a one-line
addition to `templates/` and `generate.py`'s format list whenever a
concrete asset (not just a flag) is wanted.

## Draft Generation

Four output formats, one template each in `runtime/templates/`, filled
by simple `{{TOKEN}}` substitution (no template engine, no
dependencies — consistent with every other AOS runtime). Every token
resolves to something real:

- **Hook and body**: the actual title/summary from the source record
  (`regulatory-log.json`'s `summary`, the opportunity's `description`,
  or the shipped product's `title`/`originSignal`) — never invented,
  never paraphrased into vaguer language than the source itself uses.
- **Practitioner grounding**: exactly one bullet from
  `practitioner-bank.json`'s `practitionerExperience`, matched by
  `domainTags` overlap — the same real thirteen-years/PwC/Wells
  Fargo/JPMorgan Chase/Viatris facts Sales Director already quotes. If
  nothing matches, no grounding sentence is fabricated — the draft
  still generates, but the queue entry is forced to `Low Value` (see
  below), because a draft with no real practitioner substance behind
  it is exactly the "generic AI wording" the founder ruled out.
- **Product reference**: for a product-announcement draft, or where a
  `products` entry's `domainTags` overlap the signal's, one real
  product from the same bank — title and description, unedited.
- **ADGL/OPERA phase language**: only included when determination 5/6
  is true, and only ever the five real phase names each methodology
  actually has (Discover/Assess/Govern/Deploy/Operate;
  Opportunity/People/Evaluation/Response/Assurance) — never a
  paraphrase of what OPERA or ADGL "generally means."

## Recommended Hashtags, Hero Image, CTA

Deterministic, not drafted per-piece:

- **Hashtags**: `#AIforUandI` always, plus one hashtag per matched
  `domainTags` entry from a fixed map (`AI Governance` →
  `#AIGovernance`, `ADGL` → `#ADGL`, `GRC` → `#GRC`, `EU AI Act` →
  `#EUAIAct`, and so on — see `generate.py`'s `HASHTAG_MAP`).
- **Hero image type**: a fixed rule by signal type — a regulatory
  signal gets "a structured governance/framework diagram, not stock AI
  imagery"; a product announcement gets "a screenshot or diagram of
  the resource itself"; an engagement-pattern or CEO-priority signal
  gets "a founder portrait or the AI for U&I brand mark."
- **CTA**: a fixed recommendation per format (comment/DM for LinkedIn,
  subscribe/forward for newsletter, download-the-resource/book-a-call
  for a website insight, view-the-resource/book-a-call for a product
  announcement) — see `generate.py`'s `CTA_BY_FORMAT`.

## Status (What CEO Advisor Receives)

Three statuses, same three-tier discipline as Sales Director's
`Ready To Send` / `Proposal Ready` / `Needs Review`:

A content score (0-100) per queue entry:

```
score = (flagBreadth * 0.35 + grounding * 0.35 + sourceStrength * 0.30) * 10
```

- `flagBreadth` (0-10): `min(10, 2 * count of true determinations among the seven)`
- `grounding` (0-10): 10 if a real practitioner-experience bullet or
  product matched; 0 if nothing matched
- `sourceStrength` (0-10): shipped product = 9, Market-Intelligence
  substantive development = 7, `Convert into Content` opportunity = 6,
  CEO Advisor priority echo = 5

**Hard gate**: `grounding == 0` always forces **Low Value**, regardless
of score — a draft with no real AI for U&I substance behind it is not
"needs a second look," it's not worth generating further. A CEO
Advisor priority echo is capped at **Needs Review** at most — it's the
weakest, most speculative source, and content-conversion-map.md itself
warns that a piece with no distinct practitioner take isn't ready.

- **Low Value**: `grounding == 0`, or score < 40
- **Needs Review**: 40-69, or 70+ from a CEO Advisor priority echo
- **Ready to Publish**: 70+, `grounding == 10`, from any other source

"Ready to Publish" still means a human sends it — see Constraints.

## Worked Example

A queued Market Intelligence trigger: NIST AI RMF publishes a
mandatory certification requirement (the same real example from
`market-intelligence-classification-model.md`), already flagged
`linkedinContent: true`, `websiteUpdate: false`, `affectsADGL: true`,
`affectsOPERA: true`. Determinations: LinkedIn (1), Newsletter (paired,
2), Website (0, from source), GitHub (0, not a product), ADGL (1),
OPERA (1), Product announcement (0) → 4 of 7 true → `flagBreadth =
min(10, 8) = 8`. The regulatory summary mentions "AI risk management"
and "certification," matching the practitioner-experience bullet on
NIST AI RMF/CAISR/EU GDPR Practitioner certifications and the ADGL
Methodology product → `grounding = 10`. Source is a Market Intelligence
substantive development → `sourceStrength = 7`.

```
(8 * 0.35) + (10 * 0.35) + (7 * 0.30) = 2.8 + 3.5 + 2.1 = 8.4 -> 84/100
```

84 ≥ 70, grounding is 10, source isn't a priority echo → **Ready to
Publish**.

## Constraints

- **Never publishes.** Every draft is a file in `runtime/output/drafts/`
  for a human to read, edit and post by hand. "Ready to Publish" is a
  priority label for CEO Advisor, not a send instruction.
- **Never invents expertise.** Every practitioner claim, every product
  reference, every ADGL/OPERA phase name traces to
  `practitioner-bank.json` or the source record itself. Nothing here
  writes a sentence claiming experience, a credential, or a result
  that isn't already real and on file.
- **Never re-scores or re-classifies an upstream signal.** Market
  Intelligence's six checks, Opportunity Hunter's classification, and
  CEO Advisor's decision model are read as final answers, not
  candidates for a second opinion.
