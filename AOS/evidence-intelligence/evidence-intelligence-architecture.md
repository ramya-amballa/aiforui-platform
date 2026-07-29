# Evidence Intelligence — Architecture Investigation (AOS Sprint 24)

**Status: design only. Nothing in this document is built.** Per
explicit instruction, this phase paused horizontal expansion to focus
on Artifact Depth (see the six templates elevated alongside this
document: Risk Register, Discovery Questionnaire, Governance Roadmap,
Steering Committee Pack, RACI, and four core proposal templates).
Evidence Intelligence is investigated here as the next horizon, not
implemented — the recommendation at the end is where to start *if* the
founder greenlights it.

## The Gap This Closes

Every AOS deliverable today stops at the theoretical: a Risk Register
row says a risk exists; a RACI row says who is accountable; a
Governance Roadmap phase says an exit criterion must be met. None of
them say *what specific piece of operational proof demonstrates the
gap is actually closed.* That is the difference between a document a
CISO reads once and nods at, and a document an auditor can actually
work from six months later. Most GRC tooling — and most mid-tier
advisory delivery — stops at the document. Top-tier advisory delivery
defines, for every control, the exact evidence an auditor would ask
to see, and tracks whether that evidence exists yet.

Evidence Intelligence is the bridge: for every risk/control AOS's
existing Risk Register already tracks, define what evidence would
close it, and track — honestly, founder-confirmed, never assumed —
whether that evidence has actually been collected.

## What This Is Not

- **Not a document generator for policies, screenshots or
  configurations.** AOS cannot write a client's firewall configuration
  or take a screenshot of their production console. It can say *which*
  screenshot or config extract would satisfy a specific control — the
  requirement, never the artifact itself.
- **Not a file store.** Evidence Intelligence would never hold the
  actual policy PDF, screenshot, or config export inside AOS's own
  repository. Those are often confidential, sometimes regulated data
  (PII, security-sensitive configuration) that has no business sitting
  in a git-tracked template output. Every evidence record is a
  *reference* (a location string — a SharePoint link, a ticket number,
  a file path in the client's own system) never the content.
- **Not an assertion that evidence exists.** Exactly like
  `delivery-log.json`'s phase field or `decision-log.json`'s entries,
  evidence status is founder-confirmed, read-only from any engine's
  perspective. AOS can say "ISO 42001 Clause 6 requires a dated AI risk
  assessment, approved by the AIMS owner" — a real, citable requirement
  — but it can never say "this exists" unless the founder has recorded
  that it does. The same discipline that runs through every employee
  built this session applies here without exception.

## Core Data Model

Four concepts, three of them extending real data AOS already has:

### 1. Control (already real — no new concept)

Every row in the Risk Register (Account Intelligence's own governance
risks, or `regulatory-framework-annexes.json`'s framework-standard
seed risks) is already a control in substance. Evidence Intelligence
adds nothing here — it reads what's already there.

### 2. Evidence Requirement (new — a real, citable definition, per control)

The one new field this whole system rests on: for a given control,
what specific evidence would an auditor or CISO expect to see. This is
exactly as real and exactly as bounded as `regulatory-framework-
annexes.json`'s existing `riskSeedRisks` — a faithful, professionally-
grounded statement, not a fabricated legal claim.

```json
{
  "control": "AI risk assessment not distinct from general IT risk assessment",
  "evidenceType": "Policy | Standard | Configuration | Screenshot | Ticket | Architecture Diagram | Approval Record | Training Record",
  "evidenceRequirement": "A dated AI System Risk Assessment document, distinct from the general IT risk register, approved by the named AIMS owner within the last 12 months.",
  "refreshCycle": "Annual | Per material change | One-time"
}
```

Extending the six evidence types the founder named with two natural
siblings already implied by the frameworks already built:
**Approval/Sign-off Records** (RACI sign-off, a board approval minute
— ISO 42001 Clause 5 and DORA both hinge on named accountability, not
just a policy existing) and **Training/Awareness Records** (ISO 42001
Clause 7 competence requirement specifically asks for these — a policy
with no evidence anyone was trained on it is a common, real audit
finding).

### 3. Evidence Item (new, founder-maintained — never engine-written)

The founder's own record that a specific piece of evidence has
actually been obtained, for a specific organisation and control. Same
precedent as `delivery-log.json`/`decision-log.json`: a JSON file that
starts empty, the founder edits directly, every engine reads it
read-only.

```json
{
  "organisation": "string — key, matches Company 360's own organisation string",
  "control": "string — matches the Risk Register row's own risk text",
  "evidenceType": "string — one of the taxonomy above",
  "status": "Not Started | Requested | Collected | Verified | Expired",
  "location": "string — a reference only: a SharePoint/Drive link, a ticket ID, a file path in the client's own system. Never the file content itself.",
  "collectedDate": "string or null — ISO 8601 date",
  "expiryDate": "string or null — derived from refreshCycle, when applicable",
  "notes": "string — founder's own note, e.g. who provided it"
}
```

### 4. Evidence Readiness (computed, read-only, the one new metric)

Per organisation: `(# controls with status == Verified) / (# controls
with a defined Evidence Requirement)`. Grounded entirely in real,
founder-confirmed status — never a proxy, never inferred from anything
else. This is the number a CISO or steering committee actually wants:
"we are 60% audit-ready," not "we have a Risk Register."

## How It Hooks Into What Already Exists

- **Risk Register** (`templates/delivery/risk-register-template.md`)
  gains one more column per row: **Evidence Required** — a one-line
  reference to the matching Evidence Requirement, not the full
  definition (which lives in the config, referenced by control name).
  This is the only change to an existing template this architecture
  implies; everything else is new, additive infrastructure.
- **`regulatory-framework-annexes.json`**'s existing `riskSeedRisks`
  entries are the natural home for each framework-standard control's
  Evidence Requirement — extending a structure that already exists
  rather than inventing a parallel one.
- **Company 360** would gain one more real, read-only field per
  organisation: `evidenceReadiness` (the computed percentage above) —
  the same "join what already exists, compute nothing fabricated"
  discipline every Company 360 field already follows.
- **Steering Committee Pack** would gain an "Evidence Readiness"
  section alongside Risk Summary — the single most likely place a real
  CISO would look for this first.
- **Delivery Intelligence**'s `select_regulatory_framework()` is the
  same real signal (the opportunity's own `domainTags`) that would
  determine which framework's Evidence Requirements apply to a given
  engagement — no second detection mechanism.

## Workflow

1. Delivery Intelligence generates the Risk Register as it does today,
   now with an Evidence Required column populated from the matching
   framework's real, config-defined requirements.
2. During delivery, the founder collects evidence with the client (or
   the client collects it and hands it over) and records it in
   `evidence-intelligence/evidence-log.json` by hand — a reference and
   a status, never the file itself.
3. Evidence Intelligence (if built) reads that log read-only every
   run, computes Evidence Readiness per organisation, and surfaces it
   in Company 360 and the Steering Committee Pack.
4. At Project Closure, Evidence Readiness at close becomes a real,
   citable outcome metric — "92% of controls had verified evidence at
   engagement close" is a genuinely differentiated closing statement
   most GRC engagements never produce.

## What Would Have To Be True Before This Ships

- Every Evidence Requirement definition must be reviewed by the
  founder before being trusted client-facing, exactly like the
  regulatory framework annexes already built — these are professional
  judgements, not legal advice, and carry the same "confirm with
  qualified legal counsel" disclaimer the DORA/EU AI Act templates
  already use.
- A location field is a reference, and references can go stale
  (a SharePoint link changes, a ticket gets renumbered) — this needs
  the same "freshness, not expiry" discipline `memory-system.md`
  already documents for other stores, not a new mechanism.
- Confidentiality: even a *reference* to a security-sensitive
  location (e.g. "prod firewall config, ticket SEC-4471") is more
  sensitive than most of what AOS tracks today. If this ships, the
  evidence log should be treated at the same sensitivity level as
  client credentials, not committed to a shared or public repository
  alongside the rest of AOS's own operational data.

## Recommended Starting Increment, If Greenlit

Not all four data-model pieces need to ship together. The lowest-risk,
highest-leverage first step is **Evidence Requirement only** — no new
employee, no new log file, no new orchestrator step:

1. Add a real `evidenceRequirement` string to each existing
   `riskSeedRisks` entry in `regulatory-framework-annexes.json` (seven
   frameworks, 2-3 risks each — roughly 18 definitions to author, the
   same scale of work as this sprint's framework annexes).
2. Add one column, **Evidence Required**, to the Risk Register
   template, populated the same way `{{REGULATORY_FRAMEWORK_SEED_RISKS}}`
   already is.

That alone gives every Risk Register a real answer to "what would
close this" — the single highest-value piece of Evidence Intelligence
— without a new employee, a new founder-maintained log, or any change
to the orchestrator. Evidence Item tracking (the founder-maintained
log, the computed Evidence Readiness percentage, the Company 360 and
Steering Committee integration) is the natural Phase 2, once the
founder has lived with Evidence Requirements in real engagements and
confirmed the definitions hold up.
