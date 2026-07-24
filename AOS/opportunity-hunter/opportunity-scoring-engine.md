# Opportunity Scoring Engine

Every opportunity in `opportunity-schema.json` is scored 0-10 across
eleven weighted dimensions, producing a single 0-100 Priority Score,
then classified into one of eight actions. This is v1's core logic:
score, band, classify, route — the same four steps regardless of
which source the opportunity came from.

## Step 1: Score Eleven Dimensions

| Dimension | Weight | 0 | 10 (max) |
|---|---|---|---|
| Expected revenue | 20% | Negligible or unclear | Large, well-defined engagement or day-rate |
| Probability of winning | 15% | Long shot, no signal | High confidence: warm referral, active RFP, verbal interest |
| Strategic value | 10% | No spillover benefit | Opens a market, produces a case study, deepens a key relationship |
| Relationship value | 10% | Cold, transactional, one-off | Existing or high-potential long-term relationship |
| Time required | 10% (inverted: lower effort scores higher) | Large, multi-week pursuit before any decision | Minutes to hours to respond |
| Geography | 5% | Jurisdiction with no practical reach or high friction to serve | Core served geography (UAE, US, India, UK, EU remote-eligible) |
| Remote compatibility | 5% | Requires full-time on-site presence | Fully remote-deliverable |
| Alignment with AI for U&I services | 10% | Outside AI governance, technology risk, GRC or TPRM | Squarely in-practice |
| Alignment with ADGL | 5% | Not an AI deployment governance need | Direct AI deployment governance engagement (Copilot, ChatGPT Enterprise, RAG, agentic AI) |
| Alignment with OPERA | 5% | Not a governance advisory engagement | Fits the OPERA advisory delivery model directly |
| Long-term relationship potential | 5% | One-off, unlikely to recur | Clear path to a retained, fractional or recurring relationship |

Score each dimension 0-10. Time required is scored inverted at
intake (10 = least time), so it can be multiplied by its weight the
same way as every other dimension.

```
Priority Score =
    (Expected revenue × 0.20)
  + (Probability of winning × 0.15)
  + (Strategic value × 0.10)
  + (Relationship value × 0.10)
  + (Time required, inverted × 0.10)
  + (Geography × 0.05)
  + (Remote compatibility × 0.05)
  + (Alignment with AI for U&I services × 0.10)
  + (Alignment with ADGL × 0.05)
  + (Alignment with OPERA × 0.05)
  + (Long-term relationship potential × 0.05)
```

Each dimension is 0-10; the weighted sum lands on 0-100 directly. All
eleven weights sum to 100%.

## Step 2: Band

- **80-100 — Priority**: respond same day
- **50-79 — Active**: respond within 48 hours
- **Below 50 — Archived**: logged for the record, no action unless
  new information arrives

## Step 3: Classify

Band alone doesn't decide the action — a Priority-band recruiter lead
is handled differently from a Priority-band direct RFP. Classification
runs as a decision tree, evaluated in order:

```
Priority Score < 30
  -> IGNORE

Priority Score >= 30, source is a recruiter or agency
  (UAE Recruiters, or any source where sourceCategory = "Recruiter Channel")
  -> FOLLOW RECRUITER

Priority Score >= 80, opportunity is a named, scoped engagement
  (a specific RFP, project brief or consulting mandate)
  -> IMMEDIATE PROPOSAL

Priority Score 50-79, relationship value >= 7, no scoped engagement yet
  -> RELATIONSHIP BUILDING

sourceCategory = "Consulting Channel" (a firm subcontracting capacity),
strategic value >= 6
  -> PARTNERSHIP

Opportunity is a recurring theme or pattern, not a single named
engagement (the same question/gap appearing across multiple listings
or conversations)
  -> CONVERT INTO CONTENT

Opportunity reveals unmet demand better served by a reusable asset
than a one-to-one engagement (the same narrow need recurring, suited
to a Toolkit, Checklist, Assessment or similar)
  -> CONVERT INTO PRODUCT IDEA

Priority Score 30-49 and none of the above apply
  -> RELATIONSHIP BUILDING (nurture; re-score if new information arrives)

Priority Score 50-79 and none of the above apply
  -> APPLY
```

`Convert into Content` and `Convert into Product Idea` can apply
alongside any other classification when the recurrence condition is
independently true, the same additive-trigger logic
`business-decision-engine.md` already uses for the wider business.

## Step 4: Route

Classification decides where the entry gets written, with no manual
reformatting required — every field below already exists on the
opportunity's own record in `opportunity-schema.json`.

| Classification | Writes to | Field mapping |
|---|---|---|
| Apply | Founder action only, surfaced in the daily report | — |
| Immediate Proposal | `08-Revenue-Hunter/pipeline.json` (new entry), `opportunity-hunter/proposal-template.md` (drafted) | `id`→`sourceRef`, `title`→`title`, `organisation`→`organisation`, `scores.expectedRevenue`→`expectedRevenue`, `scores.probabilityOfWinning`→`probabilityOfSuccess`, `scores.timeRequired`→`effortRequired`, `scores.strategicValue`→`strategicValue` |
| Follow Recruiter | `06-CRM/company-intelligence.json` (new/updated record) | `organisation`→`companyName`, `source`→`recruiter`, `relationshipTemperature`: `warm` |
| Relationship Building | `06-CRM/company-intelligence.json`, `04-Sales-Director` follow-up queue | `organisation`→`companyName`, `relationshipTemperature`: `warm`, `nextFollowUpDue` set |
| Partnership | `06-CRM/company-intelligence.json`, `08-Revenue-Hunter/pipeline.json` (`type`: Partnership) | `organisation`→`companyName`; `id`→`sourceRef`, `type`: `Partnership` |
| Ignore | `opportunity-schema.json` only | `status`: `archived`, `band`: `Archived` |
| Convert into Content | `02-Content-Director/content-brief-template.md` (new brief) | `description`→Key Point, `domainTags`→objective mapping via `content-conversion-map.md` |
| Convert into Product Idea | `03-Product-Manager/product-backlog.json` (new candidate) | `id`→`signalSource`, `description`→`signalDescription` |

## Notes

- Re-score an archived opportunity if new information arrives; don't
  leave the original score standing.
- A high-probability, high-alignment opportunity with modest expected
  revenue can still land in Priority — expected revenue is 20% of the
  score, not the whole of it.
- `Convert into Content` and `Convert into Product Idea` are pattern
  triggers, not score triggers: a single Archived-band posting can
  still be worth converting into content if it's the third instance of
  the same question this month.
