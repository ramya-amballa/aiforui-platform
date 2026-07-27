# Tender & RFP Intelligence Engine (AOS Sprint 14)

## Objective

Monitor consulting opportunities beyond recruiters: public procurement
tenders and RFPs from Government, Banking, Healthcare, UN, World Bank,
ADB, EU and UAE procurement channels, plus any dedicated Public AI
Governance tender source, for the same seven domains AI for U&I
already serves.

## How Tenders Are Found

Real RSS/Atom feeds, configured by the founder in
`runtime/config/tender-intelligence-config.json`'s `feedUrls` — a list
of `{"url", "sourceType"}` pairs, where `sourceType` is exactly what
you label it (`Government`, `Banking`, `Healthcare`, `UN`, `World
Bank`, `ADB`, `EU`, `UAE`, `Public AI Governance`, ...). Nothing is
guessed from content — the source type is only ever what the config
says it is. With no feed URLs configured, this connector does nothing,
honestly, exactly like Demand Intelligence's Demand Signals connector
with no `feedUrls`.

## Domain Detection

Every fetched entry's title+summary is checked against seven
deterministic keyword sets: **AI Governance**, **Responsible AI**,
**Technology Risk**, **GRC**, **Cyber Risk**, **Vendor Risk**,
**Compliance** (`config/tender-intelligence-config.json`'s
`domainKeywords`). An entry matching none of the seven is skipped
entirely — a generic procurement notice is never treated as
GRC-relevant on a guess.

## Per-Tender Fields

| Field | How it's produced |
|---|---|
| Tender Summary | The entry's own (HTML-stripped) title/summary |
| Estimated Value | Parsed from the entry's own text (currency symbol/code + a number, reusing the same currency-parsing pattern CRM/Revenue Hunter/Executive Dashboard already use) — `"Not specified"` when no real figure is present, never invented |
| Eligibility | An honest pointer to the source tender notice — this engine has no eligibility-rules database, so it never guesses who qualifies |
| Fit Score (0-100) | An explicit heuristic based on how many of the seven domains matched (1 match, 2, or 3+) — **not a claim of true win probability**; AOS has no historical tender win-rate data yet |
| Fit Band | High (70+) / Medium (40-69) / Low (below 40) |
| Required Partners | A deterministic flag for source types (`Government`, `UAE`, `Banking`, `Healthcare`) where a local/registered partner is typically required; otherwise an honest "not specified — review tender documents" |
| Deadline | Parsed from the entry's own text via configured date patterns ("deadline:", "closing date:", "submission date:") — `"Not specified"` when absent |
| Recommended Response | Tied directly to the Fit Band — High: prepare a full response; Medium: register interest and monitor; Low: note only |

## Persistence

Every tender ever collected accumulates in
`output/tender-intelligence-feed.json`, keyed by its source URL — a
re-run adds genuinely new tenders without duplicating ones already
tracked, the same accumulation pattern as
`organisation-profiles.json`/`recruiter-profiles.json`. A separate
`config/tender-seen.json` index (never a feed field) prevents
re-fetching the same RSS entry twice.

## Dashboard

**Tender Intelligence** page: every tracked tender, sorted by
Estimated Value (highest first; unestimated tenders sort last, never
guessed a value to rank them higher), filterable by source type and
fit band.

## What This Engine Does Not Do

- Does not fabricate an estimated value, eligibility rule, deadline or
  required partner it has no real evidence for in the tender's own
  text — every one of those fields honestly says "Not specified" when
  the source text doesn't contain it.
- Does not claim a true probability of winning — AOS has no historical
  tender outcome data. The Fit Score is explicitly labelled a
  relevance heuristic, in both the code and every rendered output.
- Does not modify any other employee's data — this is a new,
  self-contained employee with its own persistent feed.
