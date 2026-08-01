# CEO Advisor — Decision Model

**Executed as code since Sprint 5** — `ceo-advisor/runtime/generate.py`
implements every value in this file's normalisation table via
`runtime/config/ceo-advisor-config.json`, and extends Step 4 from a
single winner to a ranked top 3 with explicit outranking reasons. See
`ceo-advisor/ceo-advisor-runtime-notes.md` for exactly what's reused
here versus genuinely new, and a real ranking bug that runtime's own
tests caught and fixed.

CEO Advisor does not re-score opportunities from scratch. Each
employee already scores its own domain (`demand-intelligence`,
`08-Revenue-Hunter`, `03-Product-Manager`, `04-Sales-Director`'s
follow-up priority). CEO Advisor's job is to compare across those
different scales and pick one winner, using urgency as the deciding
layer none of the individual models weigh on their own.

## Step 1: Normalise

Convert each candidate's native score to a 0-10 value score:

| Source | Native scale | Normalisation |
|---|---|---|
| `08-Revenue-Hunter/pipeline.json` | 0-100 | divide by 10 |
| `demand-intelligence/opportunity-schema.json` (`priorityScore`) | 0-100 | divide by 10 |
| `03-Product-Manager/product-backlog.json` | 0-40 | divide by 4 |
| `04-Sales-Director` follow-up queue | Hot/Warm/Cooling + overdue | Hot+overdue = 9, Hot = 7, Warm+overdue = 6, Warm = 4 |
| `output/sales-director/ceo-advisor-feed.json` (prepared-proposal status) | Ready To Send / Proposal Ready / Needs Review | Ready To Send = 9, Proposal Ready = 6, Needs Review = 3 |
| `orchestrator/status.json` (`failures`) | present / absent | any entry present = 9, regardless of which employee failed |
| `output/05-Market-Intelligence/ceo-advisor-feed.json` (six checks) | boolean combination | `consultingOpportunity` true = 7, else `newProduct` true = 5, else `linkedinContent`/`websiteUpdate` only = 3 |
| `output/content-director/ceo-advisor-feed.json` (draft status) | Ready to Publish / Needs Review / Low Value | Ready to Publish = 6, Needs Review = 3, Low Value = 1 |
| `output/website-intake/ceo-advisor-feed.json` (lead urgency) | High / Medium / Low | High = 8, Medium = 6, Low = 4 |

CEO Advisor reads only the `status` field from the prepared-proposal
feed — never the drafts themselves. A `Needs Review` item still
normalises to a value (3, not 0): a package that needs a human look
before it's send-ready is still worth surfacing, just not as
send-ready. A pipeline failure in `orchestrator/status.json` always
normalises to 9 — a broken daily run is itself an urgency signal,
independent of any single opportunity's value; see
`orchestrator/execution-plan.md`'s "Notify CEO Advisor" section. Market
Intelligence's feed is read for its six booleans only — the underlying
regulatory-log.json entry is never opened here, same as every other
feed above. Website Intake Runtime's feed is read for `urgency` only —
even its lowest band (Low = 4) still surfaces, since every entry is a
real, self-initiated enquiry from AI for U&I's own site, not a
speculative lead; the full lead record (`website-intake/leads.json`)
is never opened here either.

## Step 2: Apply the Urgency Overlay

Value alone doesn't decide the day. A large opportunity with no
deadline can wait a day; a smaller one that closes in 48 hours can't.
Multiply the normalised value by an urgency factor:

| Time-to-close or deadline | Urgency factor |
|---|---|
| Closes or expires within 48 hours | 1.5x |
| Due this week | 1.2x |
| Due this month | 1.0x |
| No deadline / evergreen | 0.8x |

## Step 3: Effort as Tie-Breaker

If two candidates land within 10% of each other after the urgency
overlay, the lower-effort one wins — CEO Advisor optimises for what
Ramya can actually finish today, not just what's biggest.

## Step 4: Select

- **Highest-value action**: the single top result
- **Runners-up**: the next 2-3, shown but explicitly not co-priorities
- Anything escalated by `04-Sales-Director` as at-risk (see
  `04-Sales-Director/follow-up-priority-model.md`) is always at least a
  runner-up, regardless of its raw value score — a relationship going
  cold is itself an urgency signal.

## Worked Example

A recruiter re-opens a conversation about a role that would convert to
a ₹18L contract. `08-Revenue-Hunter/lead-scoring.md` already scored
this item at 83/100 (Priority band) using its own worked example.
Normalised: 83 / 10 = 8.3. The recruiter has said the client wants to
close within 48 hours, so the urgency factor is 1.5x: 8.3 x 1.5 =
12.45. Even capped for comparison, this outranks same-day candidates
with no deadline, because effort is minutes and the window is nearly
closed.

**Today's highest-value action**
Reply to IBM recruiter.
**Estimated value:** ₹18L contract.
**Estimated effort:** 15 minutes.
**Reason:** Highest probability and closes in 48 hours.

This is the exact form `daily-recommendation-template.md` produces
every morning.
