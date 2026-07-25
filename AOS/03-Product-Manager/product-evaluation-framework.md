# Product Evaluation Framework

## Step 1: Is This Signal Reusable?

Before picking a format, confirm the signal isn't a one-off. Ask: has
this question, gap or pattern come up more than once, or is it likely
to? If it's genuinely one-off, it belongs in a proposal or engagement
deliverable, not a product.

## Step 2: Match to a Format

| Question | If yes |
|---|---|
| Is this a recurring operational task needing several bundled artefacts? | Toolkit |
| Is this a single, narrow, repeatable check? | Checklist |
| Is this a board/executive-level overview meant to be read in minutes? | Executive Guide |
| Can a prospect self-score against this without help? | Assessment |
| Does this need a structured, multi-part teaching sequence? | Course |
| Does this need live facilitation or discussion, not just reading? | Workshop |
| Is this ongoing value best delivered continuously rather than once? | Subscription |
| Does this specifically extend the ADGL Methodology's phases or controls, rather than stand alone? | ADGL Extension |
| Does this specifically extend OPERA's phases or the methodology itself, rather than stand alone? | OPERA Module |

If more than one applies, pick the format that requires the least
new material to launch, then note the others as future extensions in
`product-backlog.json`. ADGL Extension and OPERA Module are the lowest-
effort formats by construction — they extend a product/methodology
that already exists rather than building something new, and should be
preferred over a freestanding format whenever the signal is genuinely
about ADGL or OPERA specifically.

## Step 3: Score the Candidate

| Dimension | 0 | 10 (max) |
|---|---|---|
| Demand signal strength | One mention, unconfirmed | Repeated across multiple clients/channels |
| Build effort | Requires substantial new material | Mostly assembled from existing engagement artefacts |
| Differentiation | Generic, available elsewhere | Reflects real, practitioner-specific judgment |
| Revenue or lead potential | Unclear | Clear price point or clear lead-gen role |

Sum for a rough 0-40 priority score. Log in `product-backlog.json`
regardless of score; low scores are parked, not discarded.

## Step 4: Decide

- **30+**: move to `in-development`, notify Content Director to plan
  launch content
- **15-29**: keep as `candidate`, revisit if the demand signal repeats
- **Below 15**: log as `parked`

## Runtime Execution Notes (v1.0)

`product-manager/runtime/generate.py` is this framework running as
code. It does not re-decide anything another employee has already
decided — see `product-manager/product-manager-runtime-notes.md` for
the exact sources consumed and why none of them is duplicated logic.
This section documents only how the four scoring-dimension questions
above become deterministic 0-10 numbers, since the framework itself
leaves that judgement-call open for a human:

| Dimension | How the runtime answers it |
|---|---|
| Demand signal strength | `min(10, 4 + 2 * occurrenceCount)` — `occurrenceCount` is 1 for a single flagged signal, or the real count of Sales-Director-prepared opportunities sharing the same `domainTags` for a recurring-pattern signal (never invented — it's a count of real records) |
| Build effort (inverted: 10 = least effort) | 8 if the matched format is ADGL Extension or OPERA Module (extending something that already exists); 7 if the signal's own text matches 2+ of `toolkit`/`checklist`/`template`/`framework` (suggesting it assembles from existing engagement artefacts); 5 otherwise |
| Differentiation | 6 if the signal matched a real practitioner-experience bullet or product in `sales-director/runtime/config/practitioner-bank.json` (see Content Director's identical grounding gate — the same real content bank, reused, not re-collected); 3 if nothing matched, since ungrounded claims are exactly the "generic, available elsewhere" case this dimension is meant to catch |
| Revenue or lead potential | 7 if the signal originated from Opportunity Hunter's own `Convert into Product Idea` classification (a real, already-qualified opportunity, not a cold signal) or from 2+ recurring Sales Director records; 5 for everything else |

### Worked Example

A signal recurs: three separate opportunities Sales Director has
already prepared proposals for all share the `ADGL` domain tag —
`occurrenceCount = 3`. Format match: extends the ADGL Methodology
directly → **ADGL Extension**. Demand: `min(10, 4 + 6) = 10`. Build
effort: ADGL Extension → 8. Differentiation: matches the ADGL
Methodology product in the practitioner bank → 6. Revenue: 2+
recurring Sales Director records → 7.

```
10 + 8 + 6 + 7 = 31 -> 31/40 -> in-development
```
