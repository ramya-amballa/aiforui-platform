# Revenue Hunter Runtime — Sources, Reuse, and Honesty Rules

`runtime/generate.py` executes three documents that already exist and
had never run as code: `08-Revenue-Hunter/lead-scoring.md`,
`decision-tree.md`, and `revenue-forecasting-engine.md`. It also
reuses, verbatim, `executive-dashboard/runtime/generate.py`'s currency
parser rather than writing a second one. Nothing here is a new
financial model — see below for exactly what's reused from where.

## The One Rule Everything Else Follows

**No financial assumption may be fabricated.** Where a real
`expectedRevenue` figure exists (founder-entered, or already estimated
by another employee), it's used. Where none exists, the field is set
to the literal string `"Not yet estimated"` — exactly the convention
`demand-intelligence/runtime/ingest.py` already uses — and excluded from
every dollar sum. It is still counted and surfaced ("N items pending a
revenue estimate") so nothing silently disappears from view. This
runtime never guesses a number to fill the gap, not even a labelled
estimate — Sales Director's rate-card estimates exist for outbound
pricing conversations; a financial forecast is a different context,
and averaging in unlabelled guesses would quietly distort every
downstream sum.

## Sources Consumed

| Source | What's read | Why this isn't duplicated logic |
|---|---|---|
| `demand-intelligence/opportunity-schema.json` | Every `Active`/`Priority`-band opportunity with no existing `pipeline.json` entry (`sourceRef`) | `Immediate Proposal`/`Partnership` opportunities already got a pipeline entry from `ingest.py`'s own `route_to_revenue_hunter` — this runtime only adds the ones that classification never routes there (`Apply`, `Follow Recruiter`, `Relationship Building`), exactly as `daily-workflow.md` step 1 already specifies |
| `06-CRM/company-intelligence.json` | Every `hot`/`warm` relationship with no open pipeline item | `daily-workflow.md` step 2, never run as code before |
| `sales-director/runtime/processed-index.json` | Every opportunity Sales Director has prepared a package for | Advances that pipeline item's `stage` to `in-progress` — Sales Director's own status is never re-read or re-interpreted, only its existence |
| `03-Product-Manager/product-backlog.json`, `shipped-products-log.json` | `in-development` candidates and shipped products' own `revenueOrLeadResult` | Surfaced as-is in the Product Revenue Potential section — a real, already-measured result, never a projection this runtime invents |

## Reused, Not Reinvented

- **Scoring** — new pipeline entries this runtime adds use the exact
  same weights `ingest.py`'s `route_to_revenue_hunter` already applies
  (0.35 expected-revenue-clarity, 0.30 probability, 0.20 effort
  inverted, 0.15 strategic value — identical to `lead-scoring.md`'s own
  table), against the same opportunity `scores` fields Demand
  Intelligence already computed. This runtime does not introduce a second
  scoring formula; it applies the one that already exists to the
  entries it doesn't yet cover.
- **Decision tree** — `decision-tree.md`'s stage/action rules are
  applied to every open item exactly as written.
- **Forecasting** — `revenue-forecasting-engine.md`'s EV formula
  (`expectedRevenue × probability ÷ 10`), three-scenario monthly
  bucketing, and leverage ranking (`expectedRevenue × 2 ÷ 10`) are
  implemented exactly as documented, including its own worked example,
  reproduced as a test before this runtime shipped.
- **Currency parsing** — `parse_currency`/`format_amount` are the same
  functions `executive-dashboard/runtime/generate.py` already ships,
  copied verbatim rather than re-derived, so a number parses the same
  way wherever AOS reads `pipeline.json`.

## Defaults Used When No Real Per-Item Judgement Exists Yet

Two fixed, documented defaults for CRM-sourced entries only (no
backing opportunity to reuse real scores from) — the same kind of
labelled, adjustable default every other runtime in AOS already uses
(Sales Director's rate card, Market Intelligence's source-strength
table, Content Director's hero-image rules):

- `probabilityOfSuccess`: `hot` → 7, `warm` → 4 — the same numbers
  `09-CEO-Advisor/decision-model.md` already uses for this exact
  temperature mapping, reused for consistency rather than invented
  fresh.
- `effortRequired`: 6, `strategicValue`: 6 — a renewal/upsell
  conversation with an existing relationship is documented here as
  moderately low-effort and inherently strategic; adjust in
  `generate.py` if real experience says otherwise.

## A Known Limitation From the Fixed Execution Order

The Orchestrator runs Revenue Hunter (step 3) before Sales Director
(step 5). So a stage advance driven by "Sales Director has now
prepared a package" always reflects Sales Director's state as of the
*previous* run, not the one happening later the same day — the same
one-cycle-behind reality Product Manager's and Content Director's own
notes describe for their own upstream reads. It self-corrects the
following run.

## What This Runtime Does Not Do

- Does not invent a dollar figure for any item. "Not yet estimated"
  is a real, counted state, not a gap to be papered over.
- Does not re-score a pipeline entry `ingest.py` already scored.
- Does not decide Sales Director's or Product Manager's status —
  their fields are read, never re-interpreted.
- Does not close, win, or lose a deal. Every stage change reflects
  something that already happened elsewhere in AOS (a proposal
  prepared); nothing here simulates an outcome.
