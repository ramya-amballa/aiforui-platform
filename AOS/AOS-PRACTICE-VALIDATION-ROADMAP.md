# AOS Practice Validation Roadmap

## Preamble

The architecture is frozen. `ARCHITECTURE-CONSTITUTION.md`, the ADR
library (0001-0003), the Shadow Artifact Registry, Schema Contracts,
the advisory validation layer, and 19 green test suites are the
platform as it stands — not a foundation still being poured. This
document does not propose a single line of code. It asks a different
question: now that the operating system exists, how does a boutique
AI Governance consulting firm actually run on it, and what evidence
would ever justify touching it again?

Every prior document in this repository was written by an architect
deciding what AOS should be. This one is written by the person who has
to hit a revenue number, keep clients happy, and go home at a
reasonable hour using what already exists. Where a KPI's data source
doesn't exist in AOS today, that is stated plainly — as an honest gap,
not a reason to go build one. The Constitution already has a phrase
for that: `"Not tracked"`. This roadmap uses it the same way.

The rule that governs everything below: **only repeated operational
evidence from real client engagements justifies architectural change.**
A founder's Tuesday-afternoon idea is not evidence. A pattern that
shows up identically across three engagements is.

---

## 1. Success Metrics

Seven categories. Each KPI names its real AOS data source — or names
the honest gap if no source exists yet.

### Business Development

| KPI | Definition | Source |
|---|---|---|
| Pipeline coverage ratio | Weighted pipeline value ÷ quarterly revenue target | `revenue-hunter/pipeline.json` |
| Qualified opportunity velocity | New `Immediate Proposal` / `Apply` classifications per week | `demand-intelligence/opportunity-schema.json` |
| Source diversification | % of qualified opportunities *not* from the single largest channel | `demand-intelligence` + `recruiter-intelligence` + `tender-intelligence` + `reverse-job-hunt` combined |
| Channel conversion rate | Contacted → responded → signed, per channel | `recruiter-intelligence-feed.json`, `reverse-job-hunt-feed.json`, `tender-intelligence` feed, cross-referenced against `crm/company-intelligence.json` |

### Proposal Quality

| KPI | Definition | Source |
|---|---|---|
| Confidence-to-outcome accuracy | Did Sales Director's one-word confidence status (derived from its 0-100 score) predict whether the proposal needed a structural rewrite? | `sales-director` proposal package + founder edit log (see §5) |
| Template hit rate | % of proposals citing one of the real, founder-authored `templates/proposals/` practice-area templates vs. a generic fallback | `proposal-content-library.json` citations |
| Time-to-first-draft | Opportunity reaches `Immediate Proposal` → first proposal draft ready | timestamps in `pipeline.json` vs. proposal package generation time |
| Edit depth | Structural rewrite vs. word-level polish vs. sent as-generated (three-way tag, not a number) | founder-logged per proposal, see §5 |

### Client Delivery

| KPI | Definition | Source |
|---|---|---|
| Delivery kit as-generated rate | Of the 10 ADGL/OPERA-aligned artifacts (Kickoff Agenda through Project Closure Report), how many were used with no founder rework | `delivery-intelligence` output vs. founder edit log |
| OPERA checkpoint completeness | At each Steering Committee checkpoint: is the Use Case Record, RACI, Risk Assessment, Decision Log, and KRI Dashboard all present and current | manual checkpoint review against the delivery kit |
| On-time milestone rate | Actual vs. planned date for each of the 10 kit artifacts | `delivery-log.json` |
| **Zero-fabrication rate** | Any AOS-sourced fact in a client-facing deliverable later found inaccurate | founder-caught or client-caught; target is exactly zero, always — this is the one KPI on this list with no acceptable non-zero baseline, given the firm's own subject matter |

### Knowledge Reuse

| KPI | Definition | Source |
|---|---|---|
| Template reuse rate | % of engagements pulling an existing proposal/delivery/annex template vs. writing new content | `templates/proposals/`, `templates/delivery/`, `regulatory-framework-annexes.json` citation counts |
| Executive Memory action rate | How often a founder's actual decision matches a recurring pattern or Lessons Learned entry Executive Memory surfaced, rather than being decided fresh | `executive-memory/decision-log.json` cross-referenced against founder's actual choice |
| Artifact Registry query use | How often the founder or CEO Advisor actually resolves a "what did we do last time" question via `registry_query.py` rather than re-deriving it by hand | manual count until real usage patterns justify anything more automated |

### Founder Productivity

| KPI | Definition | Source |
|---|---|---|
| CEO Advisor Top 3 acceptance rate | % of days the founder's actual work matches CEO Advisor's Top 3 recommended priorities without override | `ceo-advisor/ceo-daily-report.md` vs. founder's own end-of-day note |
| Time-to-first-draft (productivity view) | Same metric as Proposal Quality, read as founder-hours saved, not proposal accuracy | same source, different lens |
| Manual upkeep burden | Minutes/week spent maintaining founder-authored files (`relationship-profiles.json`, `decision-log.json`, `capacity-config.json`, rate cards) | self-reported, weekly |
| AOS-derived vs. judgment-only time split | Rough weekly split between time spent reading/adapting AOS output and time spent on things only a human can do (client conversation, negotiation, judgment calls) | self-reported |

### Revenue

| KPI | Definition | Source |
|---|---|---|
| Forecast accuracy | Realized revenue vs. `pipeline.json`'s weighted forecast, per quarter | `pipeline.json` + actual invoicing |
| Average deal size trend | Across the 20 engagements and beyond | `pipeline.json` |
| Revenue per employee-touch | Whether engagements that used more of the 24 employees correlate with larger or faster deals — tracked honestly as an open question, not an assumption | cross-reference `artifact-index.json` per engagement against deal outcome |
| Capacity realization | Actual utilization vs. `capacity-management`'s predicted Available/Near/Over Capacity band | `capacity-management` feed vs. `delivery-log.json` |

### Client Satisfaction

| KPI | Definition | Source |
|---|---|---|
| Direct satisfaction score | Post-engagement client feedback | `delivery-log.json`'s `clientSatisfactionNote` (no employee computes this — it's a founder-written field, populated starting with Engagement 1, see Technical Debt Register) |
| Referral rate | % of new engagements originating from a prior client | `06-CRM/company-intelligence.json`'s `referredBy` field, cross-referenced against `existingRelationship == "warm referral"` |
| Scope stability | Change requests / scope creep per engagement | `delivery-intelligence` Project Closure Report, once real closures exist |
| Renewal / extension rate | % of closed engagements leading to a second SOW | `delivery-log.json` completion status, cross-referenced against `crm` |

---

## 2. First 20 Engagements

Twenty individually bespoke playbooks would misrepresent how a boutique
practice actually works: the same handful of engagement *archetypes*
recur, and what matters operationally is how AOS is used within each
archetype, not the sequence number. The 20 are grouped into four
cohorts of five. Within a cohort, the employees used are the same by
design — the archetype, not the engagement count, drives employee
selection.

### Cohort A — Engagements 1-5: "Prove the Pipeline"

Smaller, faster engagements (a single AI Readiness Assessment, a
scoped advisory sprint) — the first real test of whether AOS-assisted
proposals and delivery hold up against a paying client, not a
hypothesis.

- **Employees used:** `demand-intelligence`, `account-intelligence`,
  `crm`, `sales-director`, `revenue-hunter`, `delivery-intelligence`
  (Kickoff Agenda, Discovery Questionnaire, AI Readiness Assessment
  Workbook only), `ceo-advisor`.
- **Outputs that matter:** the proposal package and its confidence
  score/one-word status; the three early-stage delivery artifacts;
  `company-360`'s rollup, used to sanity-check the account picture
  before the first client call.
- **Founder feedback to capture:** did the proposal need a structural
  rewrite or only word-level polish; was the one-word confidence
  status right in hindsight; which OPERA artefact was hardest to
  populate from AOS-derived facts vs. required pure founder judgment.
- **Improvements measured:** time-to-first-draft, edit depth, whether
  the Discovery Questionnaire actually anticipated the client's real
  questions.

### Cohort B — Engagements 6-10: "Full OPERA Governance Program"

Larger, multi-month governance engagements — the firm's core service
line — the first real end-to-end run of all 10 delivery-kit artifacts
from Kickoff through Closure.

- **Employees used:** everything in Cohort A, plus the full
  `delivery-intelligence` kit (RACI, Risk Register, Workshop
  Materials, Executive Status Report, Steering Committee Pack, Project
  Closure Report), `executive-brand-intelligence` (thought leadership
  running alongside the engagement), `executive-memory` (first real
  Lessons Learned entries once a Closure Report exists),
  `capacity-management` (does the firm have room for Engagement 7
  while 6 is still active?).
- **Outputs that matter:** RACI and Risk Register at each governance
  checkpoint; the Steering Committee Pack (the client-facing proof
  point); the Project Closure Report (the first real input to
  Executive Memory's Lessons Learned Library — it has zero entries
  until this cohort closes its first engagement).
- **Founder feedback to capture:** which of the 10 artifacts were used
  as-generated vs. needed rework; did the regulatory annex selected
  from `regulatory-framework-annexes.json` (DORA / EU AI Act /
  Security Governance) actually match the client's real regime; did
  `capacity-management`'s predicted band match what running two
  engagements at once actually felt like.
- **Improvements measured:** OPERA checkpoint completeness, on-time
  milestone rate, and — the first real test of Knowledge Reuse —
  whether Executive Memory's first Lessons Learned entry gets surfaced
  usefully on Cohort C's engagements or sits unused.

### Cohort C — Engagements 11-15: "Diversify Channels"

The first real test of whether the five non-Demand-Intelligence lead
channels — Recruiter Intelligence, Reverse Job Hunt, Tender
Intelligence, Fractional Advisory Radar, Relationship Intelligence —
convert to *signed* engagements, not just qualified leads.

- **Employees used:** `recruiter-intelligence`, `reverse-job-hunt`,
  `tender-intelligence`, `fractional-advisory-radar`,
  `relationship-intelligence`, plus the full Cohort B stack for
  whichever engagements actually close.
- **Outputs that matter:** `recruiter-intelligence-feed.json`'s
  weekly follow-up list, `reverse-job-hunt-feed.json`'s ROI-sorted
  strategies, the tender feed, `relationship-profiles.json`'s
  reconnect recommendations.
- **Founder feedback to capture:** which channel actually produced a
  signed engagement, not just an interesting lead; whether any of
  these five employees produced zero real conversions across all five
  engagements — a direct, honest input to the Quarterly Review's
  "which employees were rarely used" question, and potentially to
  Platform Governance's judgment on whether an employee earns its
  keep.
- **Improvements measured:** the Business Development source-
  diversification KPI gets its first real denominator; this cohort is
  where "we have five lead-generation employees" first gets tested
  against "which of them actually generate revenue."

### Cohort D — Engagements 16-20: "Full-Loop Operation"

Steady state. All 24 employees run daily; CEO Advisor's Top 3 is the
actual daily driver of the founder's time; the Artifact Registry and
Schema Contracts are tested at real, accumulated volume for the first
time (roughly 15-20 engagements' worth of real artifacts, not the
handful used to verify the mechanism during the build).

- **Employees used:** the complete daily Orchestrator cycle, all 24
  entries, run to completion every day.
- **Outputs that matter:** `ceo-daily-report.md`,
  `executive-dashboard.md`, and — the first genuine test of Knowledge
  Reuse rather than a mechanism demo — whether `artifact-index.json`
  actually gets *queried* to answer a real "what did we do for a
  similar client before" question, or whether the founder still
  reaches for memory and grep instead.
- **Founder feedback to capture:** CEO Advisor Top 3 acceptance rate
  over a real multi-week stretch; whether `decision-log.json` actually
  prevented a repeated mistake or merely recorded one after the fact;
  whether any employee's daily output was ignored for the entire
  cohort (a stronger and more concerning signal than Cohort C's
  channel-specific version of the same question).
- **Improvements measured:** this cohort is where a full-year KPI
  baseline first exists across all seven categories in §1 — the point
  at which the Quarterly Review process (§5) has real data to run
  against for the first time, rather than a hypothesis about what it
  will find.

---

## 3. Learning Loop

Something goes wrong, or feels missing, during a real engagement. Four
categories, four different fixes, four different evidence bars. The
bar rises sharply as the fix gets more structural — correctness is
fixed on sight; architecture is fixed only under repeated, demonstrated
pressure.

| Category | What it looks like | Evidence bar | Fix |
|---|---|---|---|
| **Bug** | An employee's own documented behavior didn't happen — e.g. Sales Director's confidence score computed wrong, or Delivery Intelligence overwrote an already-generated artifact when its own spec says it never does | None required — a bug is a bug the first time it's seen | Fixed immediately, inside the existing employee, no new capability |
| **Missing template** | The employee ran correctly, but a genuinely needed proposal template, delivery template, or regulatory annex doesn't exist yet | Confirmed the gap will recur — a second real or clearly imminent prospect in the same vertical/jurisdiction, not a one-off | Add the template in the exact existing founder-authored format; no code change |
| **Missing employee capability** | An *existing* employee's real scope should stretch to cover something adjacent it doesn't today | **2+ real engagements** show the identical need | Extend the existing employee's runtime; does not create a new employee (that bar is separately, and more strictly, set in §4) |
| **Architectural issue** | The platform's structure itself — execution model, storage, cross-employee contracts — is the actual blocker, not any one employee's logic | **3+ real engagements** with the same-shaped problem, **and** a written note of what was tried at the lower tiers first and why it didn't hold | Only then does it become an ADR candidate |

The two prior fixes made during the architecture-review cycle are the
worked example of this discipline: the `reverse-job-hunt` /
`relationship-intelligence` ordering bug was a **bug** (one employee's
own dependency wasn't honored) and was fixed immediately, in place,
with no scheduler redesign. Wiring the Artifact Registry into the
daily run was **not** a bug or a capability gap — it was accepted
because ADR 0001 had already named the exact evidence ("proven out by
its own test suite and a live run") that would justify it, and that
evidence existed before the change was made.

---

## 4. Platform Governance

Every addition needs demonstrated consulting value, not anticipated
value. "This would be useful" is not a criterion; "this already
would have helped, more than once, in a real engagement" is.

**New employee** — all of the following, together:
- A repeated (2+) real client need, per §3's own capability-gap bar,
  that no existing employee can absorb even after extension.
- A named, real class of client work it serves — not a speculative
  future client.
- An honest net-time estimate: founder-hours saved per week *after*
  subtracting the time cost of keeping the new employee's data current
  — a new employee that saves 20 minutes but costs an hour a week in
  upkeep fails this test.
- Approved at a Quarterly Review (§5), never as an ad hoc mid-quarter
  decision. This is the single rule most responsible for keeping 24
  employees from becoming 40.

**New template** (proposal, delivery, or vertical-specific):
- At least one real artifact where an existing template genuinely
  didn't fit — not "could be nicer."
- Confirmed the gap will recur.
- Authored in the same plain-file convention as the existing nine
  practice templates — no new mechanism, no new tooling.

**New annex** (regulatory framework, e.g. a jurisdiction beyond
DORA/EU AI Act/Security Governance):
- A real client, in a real regime, where the annex is needed for a
  live proposal or delivery kit — never speculative coverage.
- Personally verified by the founder against the actual regulation
  text before first use. This is the one governance-governance
  intersection on this list: a firm selling AI governance advice
  cannot afford a fabricated regulatory annex, and no structural
  validation layer in AOS checks regulatory accuracy — only a human
  can.

**New framework** (adopting something beyond OPERA, or a variant for a
new service line):
- OPERA's five phases demonstrably fail to fit a real, recurring class
  of engagement — not "a different framework is trendier."
- Before adoption, retroactively applied to at least one already-
  closed engagement to confirm it would genuinely have helped.

**New infrastructure** (anything like the Artifact Registry or Schema
Contracts):
- The exact bar ADR 0001-0003 already set: demonstrated, not
  anticipated, necessity. spaCy for offline NER, stdlib over Pydantic
  for Schema Contracts — both were adopted (or rejected) against real,
  demonstrated need, never against a hypothetical future one. Any new
  infrastructure proposal is judged against that same precedent, and
  restated in COO terms: what client-facing capability or founder-hour
  saving does this create, quantified, this quarter — not eventually.

---

## 5. Quarterly Review Process

Half a day of founder time, not a PMO ritual. Run after each quarter
of real engagements, using data AOS already produces plus two habits
the founder keeps by hand (below).

**Inputs:**
- `registry_query.py` — real per-employee and per-organisation lookups
  across the quarter's daily indices.
- `artifact-index.json`'s `employeeCounts`, across every daily build
  in the quarter — a literal count of which employees produced
  artifacts and how often.
- `ceo-advisor`'s `daily-priorities-log.json` — what needed repeated
  founder attention.
- `executive-memory`'s `decision-log.json` and Lessons Learned Library.
- Actual invoiced revenue vs. `pipeline.json`'s quarter-start forecast.
- Two founder-kept habits, both a single line each, no new tooling:
  a one-line satisfaction/referral note per closed engagement (feeds
  Client Satisfaction, §1), and a one-line edit-reason tag per proposal
  or delivery artifact that needed rework (`polish` / `structural` /
  `sent-as-generated` — feeds Proposal Quality and Client Delivery,
  §1, and the "which founder edits were repeatedly required"
  question below).

**Five standing questions, each answered from a named source:**

1. **What generated the most client value?** Cross-reference realized
   revenue and the satisfaction note per engagement against which
   employees' outputs were used un-edited in the actual deliverable —
   an imperfect but evidence-based attribution, not a guess.
2. **Which employees were rarely used?** Read directly off
   `artifact-index.json`'s `employeeCounts` across the quarter's
   builds, or the Orchestrator's own `status.json` history for
   employees that ran but produced nothing.
3. **Which templates were most reused?** Count citations of
   `templates/proposals/` and `templates/delivery/` files across the
   quarter's real proposals and delivery kits.
4. **Which verification warnings mattered?** Cross-reference
   `registry_validation.py`'s `validationFlags` raised during the
   quarter against which ones led to a real founder catch vs. which
   were ignored every single time. A flag type never acted on in a
   full quarter is itself a finding — either fix the false positive or
   retire the check.
5. **Which founder edits were repeatedly required?** Read the
   one-line edit-reason tags kept above; a pattern appearing 3+ times
   is exactly the kind of repeated operational evidence §3 requires
   before anything gets escalated toward a capability or architecture
   change.

**Output:** a half-page memo. It feeds two things directly — the
Technical Debt Register's re-ranking (§6) and any Platform Governance
decision (§4) that was waiting on evidence rather than opinion.

---

## 6. Technical Debt Register

Ranked by business impact only. Kept deliberately short — an inflated
backlog at the start of real client work would misrepresent how much
is actually broken, which is very little.

### Immediate

- ~~Client satisfaction has no data source.~~ **Addressed:**
  `delivery-log.json`'s documented shape now includes
  `clientSatisfactionNote` (`delivery-intelligence/
  delivery-intelligence-engine.md`) — a place for the founder's own
  one-line note at Closed phase, read-only to every employee, never
  computed. The founder habit itself — actually writing it every time
  — still has to start with Engagement 1, or Cohort D's KPI baseline
  (§2) is built on retrofitted memory instead of real data.
- ~~Referral source isn't captured anywhere.~~ **Addressed:**
  `06-CRM/company-intelligence.json`'s schema now includes
  `referredBy` alongside the existing `existingRelationship` field —
  `existingRelationship` could already say a company arrived via
  referral, not who sent them. Same caveat as above: the field exists,
  the founder still has to fill it in.
- **Regulatory annex verification is not yet a habit.** Before the
  first real annex ships in a client deliverable, confirm the founder
  has personally checked it against source text at least once. This
  is a zero-tolerance area, not a nice-to-have.

### Next

- **Template and annex reuse isn't currently countable without manual
  review.** Worth a query addition to `registry_query.py` — but only
  once a real Quarterly Review (§5) needs the number and manual
  counting has actually proven too slow. Not before; this is the
  Learning Loop's own "missing capability" bar applied to the
  Registry's own query surface.
- **Executive Memory's Lessons Learned Library has zero real entries.**
  Nothing to fix — it needs its first real Project Closure Report,
  which Cohort B (§2) produces. Listed here only so it isn't mistaken
  for a bug when it's still empty in Engagement 6.

### Someday

- **A registry view surfacing artifact types never referenced in a
  founder edit-log** — i.e., genuinely dead output. Only worth
  building if the Quarterly Review process itself becomes too slow to
  spot this by hand across a full year of accumulated data.
- **Multi-consultant support.** Someday, and only triggered by an
  actual second consultant joining the firm — a headcount event, not
  a technical readiness milestone. See §7.

---

## 7. Exit Criteria

Each of these is frozen until the stated evidence exists. Not a
timeline — a bar.

**Introducing SQLite as more than a shadow index.** Only when
file-scanning the Artifact Registry is *measurably* slow in real,
founder-experienced use at real accumulated volume — the same
threshold ADR 0001 already set ("stays JSON until file-scanning is
measurably, not speculatively, too slow"), now applied against real
engagement data instead of a hypothesis about future scale.

**Introducing semantic verification** (a fact-checking layer beyond
today's structural checks). Only if a real fabricated or inaccurate
claim actually reaches a client-facing deliverable, is caught, and the
structural validation layer demonstrably could not have caught it.
One real incident, precisely diagnosed, outweighs any amount of
anticipated risk — and even then the bar stays high, given this path
was already explicitly rejected as a general-purpose mechanism in the
Gemini roadmap critique.

**Adding another AI employee.** Exactly §4's own bar: 2+ real
engagements demonstrating a need no existing employee, even extended,
can absorb — approved at a Quarterly Review, never mid-quarter.

**Introducing multi-tenancy.** Only when a real second consultant
starts using AOS. This is a hiring event, not a technical milestone —
no architectural preparation for it is warranted before the hire
exists.

**Redesigning orchestration** (replacing the fixed execution array
with something more dynamic, e.g. a computed DAG). Only if the fixed
array's own limits cause a real operational problem more than once —
and the standing counter-evidence is already on record: the one real
ordering bug found during the last review cycle was fixed with a
one-line reorder inside the existing array, not a scheduler rewrite.
Until the array itself, not any one entry in it, is the actual
blocker, it is not touched.
