# Critique: Gemini's Enterprise Evolution Roadmap for AOS

**Status: design-only critique, no employee/code added.** The founder
asked Gemini to review AOS and propose an enterprise evolution roadmap,
then asked for a critical evaluation of that roadmap — not agreement,
not a rubber stamp. This document is that evaluation, written the same
way `aos-v2-architecture.md` was: every claim about AOS traced to real
code, and every recommendation judged against what AOS's operator
actually needs today, not against what would look impressive on a
generic enterprise-architecture slide.

The short version, stated up front so it isn't buried: **Gemini's
review contains a genuinely useful core (schema contracts, an artifact
registry, confidence scoring, an ADR library) surrounded by a second
cluster of recommendations — JSON-LD, OpenTelemetry, Kafka/NATS,
Postgres, event-driven execution, worker pools, and replacing the 22
employees with "Domain Engines" — that solve problems AOS does not
have, at a cost AOS's one-founder operating model cannot absorb, and
in at least one case (Domain Engines) actively regress the property
that makes AOS auditable in the first place.** The rest of this
document earns that verdict item by item.

## Per-Recommendation Evaluation

Each item is scored against the same six questions the founder asked.
Verdicts: **NOW** / **NEXT** / **LATER** / **NEVER (at current
scale/model)**.

### Typed Artifact Registry — NOW (as a read-only shadow index)

1. **Architecturally correct?** Yes. The underlying problem is real: no
   lineage, no versioning, hardcoded path-as-API. Already established
   in `aos-v2-architecture.md` with a concrete example — this week's
   output-path consolidation touched ~40 files because every
   cross-employee reference was an independent hardcoded string.
2. **Appropriate today?** Only in its *shadow-index* form: a registry
   built by scanning `output/` after each run, read-only, additive,
   deletable and rebuildable at any time. A registry that becomes the
   *only* way employees read each other's data is a large rewrite that
   should wait.
3. **Business problem solved:** Traceability and lineage — a genuinely
   strong sell for a *governance and audit* consultancy specifically,
   not a generic engineering nicety.
4. **Complexity introduced:** Low, as a shadow index. High, as a
   replacement access layer.
5. **When:** NOW, shadow-index form only.
6. **Smallest step:** A script the orchestrator runs after each pass
   that emits one `artifact-index.json` per run (artifact ID, producer,
   path, content hash, timestamp). No employee changes its own code.

### Verification Layer — NOW (structural checks, advisory only)

1. **Correct?** Yes — this is the mechanism that makes "never
   fabricate" a property of the system instead of a property of one
   person's code review.
2. **Appropriate today?** The *structural* version (schema conformance,
   required fields present, a confidence value populated) is cheap and
   appropriate now. A semantic version that reads generated prose and
   judges whether a claim is fabricated is a different, much harder
   problem — see Claim Extraction below.
3. **Business problem:** Prevents silent shape drift and enforces the
   one convention that differentiates AOS from a template mill.
4. **Complexity:** Low for structural checks; high if scoped to
   include semantic verification.
5. **When:** NOW for structural checks, in log-only/advisory mode.
   Enforcing (blocking) mode should wait until advisory mode has run
   long enough to know its false-positive rate — a verification layer
   that silently drops real output because of its own bug is a worse
   failure mode than the fabrication it's meant to catch.
6. **Smallest step:** A post-run validation pass against the Schema
   Registry (below), logged to the Observability Layer, blocking
   nothing yet.

### Candidate Artifacts — NEXT (only once there's a gate to graduate past)

1. **Correct?** Yes, as the natural lifecycle state a Verification
   Layer needs (`draft → published`).
2. **Appropriate today?** Not standalone — a "candidate" vs.
   "published" distinction is meaningless without a gate that actually
   promotes one to the other. Building this before the Verification
   Layer exists is building a label with nothing to attach it to.
3. **Business problem:** Prevents an unverified draft from being read
   as fact by a downstream employee — real, but conditional on #2
   above existing.
4. **Complexity:** Trivial once the registry exists (one status field).
5. **When:** NEXT, bundled with Verification Layer rollout, not a
   separate initiative.
6. **Smallest step:** Add the field to the shadow index now, default
   every artifact to `published` until the gate exists, so the schema
   doesn't need a second migration later.

### JSON-LD sidecar / dual-write migration — **NEVER**, at current scale

1. **Correct?** Wrong tool for the actual problem. JSON-LD/RDF exists
   to disambiguate vocabulary *across organizations* on the open
   semantic web. AOS is a single-practice tool with one internal
   consumer of its own data. A versioned JSON Schema (below) already
   gives typed, structured artifact metadata without the `@context`/
   `@id`/namespace machinery JSON-LD requires — machinery that solves
   a cross-organization interoperability problem AOS does not have,
   even under a future multi-firm licensing model (a shared *version*
   of a plain JSON schema between AOS instances is sufficient; those
   instances do not need to interoperate with unrelated third-party
   semantic-web graphs).
2. **Appropriate today?** No.
3. **Business problem solved:** None identifiable, today or in any
   currently-foreseeable AOS deployment.
4. **Complexity introduced:** Real, and doubled by "dual-write" —
   keeping two representations of the same artifact in sync is itself
   a new, durable bug class ("the sidecar and the primary drifted"),
   the exact kind of unforced structural fragility this whole review
   series has been trying to eliminate, not add.
5. **When:** Never, unless a specific, real external consumer that
   genuinely requires linked-data interoperability materializes —
   currently hypothetical, and the plain Schema Registry covers every
   real need in front of AOS today.
6. **Smallest step if ever warranted:** Don't build a sidecar. Extend
   the JSON Schema with a namespace field if and when a real external
   consumer asks for one.

### SQLite/Postgres metadata index — split verdict

1. **Correct?** SQLite: yes, once the shadow JSON index is large
   enough that file-scanning is measurably slow — likely years away for
   a single-founder practice. Postgres: only under a genuinely
   different business model (see Multi-Tenant, below).
2. **Appropriate today?** No to both, at current scale. Postgres in
   particular breaks a property AOS has had since day one: the git
   repository *is* the audit record, because the daily GitHub Action's
   entire durability mechanism is a git commit. A database sitting
   outside git has no equivalent auditability unless it is *also*
   exported back into git — which just reintroduces the file-based
   approach anyway, with an extra moving part in between.
3. **Business problem solved:** Query performance at a scale AOS
   doesn't have.
4. **Complexity introduced:** SQLite — low, still a single embeddable
   file. Postgres — real operational burden (hosting, backup,
   credentials, a new "is the database up" failure mode) for a system
   whose current failure model is "did the git commit succeed."
5. **When:** SQLite — LATER, and only measured, not assumed. Postgres
   — NEVER for the current single-tenant model; reconsider only
   alongside a genuine hosted multi-tenant SaaS decision.
6. **Smallest step:** Keep the JSON shadow index until it's provably
   too slow to scan, then move to SQLite as a local, still-zero-ops
   upgrade. Skip Postgres entirely until there's a real hosted-product
   decision to justify it.

### Confidence scoring — NOW

1. **Correct?** Yes, and cheap. Several employees already compute
   something confidence-like ad hoc — Sales Director's own
   `confidence 73/100` pattern, its Opportunity Qualification verdict.
   The gap isn't the concept, it's that it's not a shared convention.
2. **Appropriate today?** Yes.
3. **Business problem:** Directly actionable for a founder triaging
   daily output — "trust this less" is useful information.
4. **Complexity:** Low, provided it stays deterministic and
   explainable (a number plus a one-line stated basis) rather than
   becoming a learned/statistical model, which would contradict AOS's
   whole "never fabricate, always traceable" ethos by adding a
   confidence score that is itself a black box.
5. **When:** NOW.
6. **Smallest step:** Document the convention once, apply it to the
   employees that already compute something like it, extend
   opportunistically as other employees touch their own output.

### Claim extraction — mostly NEVER, narrowly LATER

1. **Correct in principle, disproportionate in practice.** The goal —
   catch a fabricated-sounding claim before a client sees it — is
   right. Automated NLP-based claim extraction across free-form
   generated prose is a genuinely hard, research-grade problem, and
   most of AOS's output isn't actually free-form prose making
   unverified claims — it's deterministic joins, scores, and template
   placeholders, which is exactly why "never fabricate" has held for 22
   employees without this layer.
2. **Appropriate today?** Only at the narrow surface where it's
   actually relevant: the one or two employees with an optional
   LLM-backed extraction path (Demand Signals' pluggable `deterministic`
   vs. `claude` backend). Applying a claim-extraction engine to all 22
   employees' mostly-deterministic output is solving a problem that,
   for 20 of them, doesn't exist.
3. **Business problem:** Narrow, not system-wide.
4. **Complexity:** High for a general system; the false-positive/
   negative tuning alone is an ongoing maintenance burden, not a
   one-time build.
5. **When:** NEVER as a blanket system-wide layer. LATER, narrowly
   scoped to genuine LLM-generated-prose surfaces, only if that share
   of total output grows materially from today's small footprint.
6. **Smallest step, if ever warranted:** A cheap heuristic check — does
   every named number/entity in a given paragraph also appear in the
   structured source data it was generated from — rather than a full
   claim-extraction NLP subsystem. Matches the actual risk surface at
   a fraction of the cost.

### Schema contracts — NOW

1. **Correct?** Yes, and the most clearly justified item in the entire
   review. This was already Phase 0 in `aos-v2-architecture.md`.
2. **Appropriate today?** Yes, unreservedly.
3. **Business problem:** Directly prevents the exact bug class already
   demonstrated live — silent shape drift, the 40-file path refactor.
4. **Complexity:** Low. Generated from documentation that already
   exists as comment blocks in every JSON store today; checked, not
   yet runtime-enforced.
5. **When:** NOW.
6. **Smallest step:** Exactly as scoped previously — no change here.

### OpenTelemetry — **NEVER**, at current scale

1. **Correct?** Wrong tool. OpenTelemetry is built for distributed
   tracing across many services with real network calls, usually
   paired with a hosted collector (Jaeger, Tempo, etc.). AOS is 22
   subprocesses run on a single machine, finishing in **under five
   seconds total**. There is no distributed call graph to trace.
2. **Appropriate today?** No.
3. **Business problem solved:** None — the actual observability gap
   (structured, queryable run history over time) is already solved
   more cheaply by a plain appended JSONL event log, already proposed
   as the Observability Layer.
4. **Complexity introduced:** Real instrumentation work in every
   employee script, plus a collector to run and maintain, for a batch
   job that already fully explains its own timing in one Markdown
   report per run.
5. **When:** Never at current scale. Reconsider only if execution
   genuinely becomes distributed across machines/containers with real
   network calls between employees — not before.
6. **Smallest step:** None needed; the JSONL Observability Layer
   already covers the real requirement.

### Cryptographic audit ledger — LATER, genuinely interesting

1. **Correct?** Partially — this is the one "enterprise" item that
   connects to something real about AOS's specific business (audit and
   governance consulting, tamper-evidence as a client-facing property),
   unlike JSON-LD or OpenTelemetry. But git commit history already
   provides a strong version of this today: every day's output is
   committed with an immutable hash chain. A bespoke ledger only adds
   value beyond that if the requirement is something git doesn't give
   for free — e.g., third-party-verifiable notarization independent of
   trusting the hosted repo, or protection against a compromised
   maintainer rewriting history.
2. **Appropriate today?** Not urgently — no client has asked for this
   yet, and it should be *designed* alongside Evidence Intelligence
   (already an approved future horizon) rather than built speculatively
   ahead of it.
3. **Business problem:** Could become real and compelling — "we can
   cryptographically prove this Risk Register wasn't altered after
   delivery" is a genuine CISO-facing differentiator.
4. **Complexity:** Real — key management is a hard, easy-to-get-wrong
   problem in its own right, and a lost or compromised signing key
   becomes a liability, not just an engineering cost.
5. **When:** LATER — worth designing once Evidence Intelligence ships
   and a concrete "prove this wasn't altered" need appears.
6. **Smallest step short of a full ledger:** GPG-signed git commits —
   already a native git feature, near-zero new infrastructure, and may
   already answer most real audit conversations without inventing a
   new cryptographic system.

### Multi-tenant architecture — **NEVER**, until there's a second client

1. **Correct in the abstract, wrong sequencing.** This is a
   business-model decision wearing an architecture costume. AOS has
   exactly one client today: its own founder's practice.
2. **Appropriate today?** No — building tenant isolation for a
   hypothetical second customer is the clearest instance of solving a
   problem AOS does not yet have.
3. **Business problem:** None today; real the day AOS is actually
   licensed to a second firm.
4. **Complexity:** The single largest, most invasive item on this
   entire list — every persistent store gains a new dimension.
5. **When:** Never until a real second client/licensee exists; then it
   becomes urgent, not optional.
6. **Smallest step, today:** Fork-per-client — a new repository per
   licensed practice. Zero new architecture, and *safer* than a shared
   multi-tenant registry would be this early (perfect isolation by
   construction, not by policy enforcement that hasn't been proven).

### Tenant boundary manager — **NEVER**, same gate as above

Entirely downstream of the multi-tenant decision; evaluating it
independently doesn't make sense. Same verdict, same trigger.

### Event-driven execution — **NEVER**, at current operating cadence

1. **Correct as a paradigm, wrong for this business.** A real
   alternative execution model exists here, but AOS's entire value
   proposition is "one deterministic, auditable, end-to-end run, once a
   day" — `daily-operating-workflow.md` explicitly documents a 06:00
   daily cycle as the intended cadence, not a real-time one.
2. **Appropriate today?** No — nothing in this business needs sub-daily
   reaction latency; a lead doesn't need scoring within milliseconds of
   being scraped.
3. **Business problem solved:** Faster reaction time — not a problem
   this business has.
4. **Complexity:** Very high — a message broker, ordering/idempotency
   concerns, and a materially harder-to-audit story (a batch run's
   Daily Execution Report is trivially auditable end to end; an
   asynchronous event stream is not, without significant extra
   tooling that itself needs building and trusting).
5. **When:** Never at the current cadence. Only reconsider if the
   business itself changes shape — a business decision, not an
   engineering one.
6. **Smallest step if ever warranted:** The DAG Scheduler v2's
   wave-based parallelism (below) already captures most of the real
   speed benefit without sacrificing batch determinism — the correct
   middle ground, not full event-driven architecture.

### Worker pools — **NEVER** as persistent infrastructure; the underlying need is NEXT

1. **Correct?** The underlying need (run independent employees
   concurrently) is real and already scoped as DAG Scheduler v2.
   "Worker pools" implies a persistent pool of long-running processes
   or containers queuing work — heavier machinery than a job that runs
   once a day and finishes in seconds needs.
2. **Appropriate today?** Not in the persistent-service form.
3. **Business problem:** Execution speed at 50+ employees — real, but
   solvable without standing up a service.
4. **Complexity:** A persistent worker-pool service is real ongoing
   infrastructure (health checks, scaling, a new failure mode) for
   marginal benefit over a simple concurrent subprocess pool.
5. **When:** The real need — NEXT, via DAG Scheduler v2. Worker pools
   as persistent infrastructure — never in that heavier form.
6. **Smallest step:** `concurrent.futures`/a subprocess pool inside the
   existing orchestrator script. No new service, no persistent
   workers, no queue.

### Kafka/NATS — **NEVER**

1. **Correct?** The clearest "solving a distributed-systems problem AOS
   does not have" item on the whole list, alongside JSON-LD and
   OpenTelemetry. Message brokers exist to decouple producers and
   consumers across process/network boundaries at high throughput with
   delivery guarantees. AOS has 22 subprocesses on one machine
   finishing in seconds — no queue depth, no cross-service decoupling
   need.
2. **Appropriate today?** No.
3. **Business problem solved:** None.
4. **Complexity introduced:** Running and operating a message broker —
   real ops burden for a workload with none of the properties that
   justify one.
5. **When:** Never, unless the business becomes a structurally
   different, genuinely real-time multi-tenant SaaS platform — and
   even then, evaluated against measured need, not adopted by default.
6. **Smallest step:** None; not applicable at any foreseeable near-term
   scale.

### Domain Engines replacing the 22 employees — **reject, permanently, absent a demonstrated problem**

This is the recommendation most worth arguing against directly,
because it attacks the actual unit that makes AOS's current
architecture sound.

1. **Architecturally correct?** No. The 22-employee structure is not
   incidental — it is the reason each one is independently testable
   (17 suites, 528 tests, each scoped to one employee), independently
   auditable (a reviewer can read one employee's entire logic without
   holding 21 others in their head), and fails in isolation (one
   employee's bug does not corrupt another's output, and the
   orchestrator's own retry/skip semantics depend on that isolation).
   Consolidating into fewer, broader "Domain Engines" reintroduces
   coupling and makes "which specific responsibility broke" a harder
   question to answer, not an easier one.
2. **Appropriate today?** No. It directly contradicts the founder's own
   stated design philosophy for this review — "22 independent AI
   employees... each employee has a clearly defined business
   responsibility" — and nothing in this review identifies an actual
   cost the current structure imposes that consolidation would remove.
   Employee count is not a cost driver here; each one is already small,
   focused, and cheap to run (the entire 22-employee daily run finishes
   in under five seconds).
3. **Business problem it claims to solve:** Presumably fewer moving
   parts to reason about at 50+ employees — but the actual coordination
   cost at scale is the dependency *graph* (already addressed via DAG
   Scheduler v2 and Schema Registry), not the employee *count*. Merging
   employees to reduce a number on a diagram does not reduce the real
   complexity; it just hides the same logic inside fewer, larger files
   with less test isolation.
4. **Complexity introduced:** A regression, not a reduction — larger
   services are harder to test in isolation, harder to review, and
   harder to safely modify without affecting an unrelated
   responsibility bundled into the same "engine."
5. **When:** Never, absent a concrete, demonstrated maintainability
   problem with the current per-employee structure — none exists
   today.
6. **The one legitimate kernel worth keeping, separated from the bad
   idea:** A *documentation and navigation* grouping — clustering
   related employees under a shared heading (Demand & Pipeline;
   Relationship & Account Intelligence; Delivery & Practice Operations;
   Content, Product & Market Signal; Executive Synthesis) already
   exists informally (used in the external-facing brief this session
   produced) and is worth making a first-class navigational aid in the
   README and the dashboard sidebar. That is a presentation change with
   zero architectural cost — not a reason to merge any employee's
   actual code with another's.

### GitHub output strategy — NOW (a real, scoped, low-risk fix, unprompted but worth naming)

1. **Correct?** The current approach — every day's output commits
   straight to `main` — has real virtues worth defending: git *is* the
   audit ledger, trivially inspectable via `git log`/`git blame`, zero
   additional infrastructure, and matches a human-in-the-loop review
   model where the founder can see every day's diff directly. The
   review correctly identifies one real cost, though: this couples
   fast-churning *operational data* (a fresh dated report, every day,
   for 22 employees) with slow-churning *code* history on the same
   branch — directly observed this session, where reconciling a merge
   against several days of automated "AOS Orchestrator: daily run"
   commits added real friction to an otherwise simple code change.
2. **Appropriate today?** Yes, worth fixing now, and cheaply.
3. **Business problem:** A noisier, harder-to-scan code history as the
   practice runs for months/years — a real, if not urgent, cost.
4. **Complexity:** Low.
5. **When:** NOW.
6. **Smallest step:** Point the daily GitHub Action's commit step at a
   dedicated branch (e.g. `data/daily-runs`) instead of `main`, and
   keep `main` reserved for human/PR-reviewed code and template
   changes. Preserves 100% of "git is the audit trail" while
   separating the two kinds of history. **This is a recommendation for
   the founder's consideration, not something implemented in this
   pass** — it changes the daily-operations workflow and deserves an
   explicit decision, not a silent change bundled into a review
   document.

### ADR library — NOW

1. **Correct?** Yes, close to pure upside. This is documentation, not
   architecture — zero runtime risk, and directly useful: institutional
   memory for exactly the kind of decision that gets silently
   relitigated by a future contributor without a written record (why
   *is* CEO Advisor always last? why filesystem persistence over a
   database? why subprocess isolation over in-process calls?).
2. **Appropriate today?** Yes, unreservedly.
3. **Business problem:** Prevents future re-litigation of settled
   decisions, and demonstrates real architectural maturity to any
   future contributor, licensee, or acquirer performing diligence.
4. **Complexity:** Minimal — writing, not building.
5. **When:** NOW.
6. **Smallest step:** This was already item 6 of the original
   seven-part review and remains queued, unstarted, pending the
   founder's go-ahead to proceed past item 1.

## The Higher-Level Questions

### 1. Does Gemini preserve the spirit of AOS, or slowly redesign it into a generic enterprise workflow engine?

Both, in distinct halves. One half of the review (schema contracts, an
artifact registry as a shadow index, confidence scoring, an ADR
library, a cryptographic ledger tied to a real future need) is genuine,
additive architectural evolution that preserves everything that makes
AOS distinctive. The other half (JSON-LD, OpenTelemetry, Kafka/NATS,
Postgres at current scale, event-driven execution, worker pools as
persistent infrastructure, and especially Domain Engines replacing the
22 employees) reads like a generic "how would you architect an
enterprise SaaS platform" checklist applied without enough weight
given to what AOS specifically is. Implemented wholesale, that second
half **would** slowly redesign AOS into a generic enterprise workflow
engine — trading away determinism, git-native auditability, and
zero-ops single-founder operability, which are not incidental
properties of AOS but its actual competitive shape.

### 2. Genuine architectural evolution vs. premature optimization

**Genuine evolution:** Schema Registry/contracts, Artifact Registry
(shadow-index form), confidence scoring, ADR library, DAG Scheduler v2
with wave-based parallelism, Verification Layer (structural checks,
advisory first), the GitHub output branch split.

**Premature or wrong-fit:** JSON-LD/dual-write, Postgres at current
scale, OpenTelemetry, Kafka/NATS, event-driven execution, worker pools
as persistent services, multi-tenant architecture and its tenant
boundary manager (absent a second client), a system-wide claim-
extraction engine, and Domain Engines replacing the 22 employees
(which is not premature so much as simply wrong for this system's
actual shape).

### 3. Which recommendations would actually make AOS more valuable to consulting clients?

Confidence scoring (the founder can triage trust at a glance),
Schema/Artifact Registry (lineage is directly sellable to a governance
buyer as audit-readiness — this *is* the product), a cryptographic
ledger if a real client ever asks for tamper-evidence (connects
directly to Evidence Intelligence's whole thesis), and an ADR library
(demonstrates real maturity to an enterprise buyer's due-diligence
process, which for a platform being *licensed* to other consultancies
is a genuine sales artifact, not just internal hygiene).

### 4. Which would impress senior architects but add little real value here?

OpenTelemetry, Kafka/NATS, Postgres, event-driven execution, JSON-LD,
persistent worker pools, and a tenant boundary manager built ahead of
any actual tenant. Every one of these reads well on an architecture
diagram and would be a reasonable default for a venture-funded,
multi-tenant, real-time SaaS company with an ops team. None of them
solve a problem AOS's actual one-founder operator has today, and
several actively increase the operational burden a single founder has
to carry alone.

### 5. A three-year maintenance roadmap

Answered directly below.

## Prioritized Roadmap

### NOW (next 3 months)

- Fix the concrete, already-identified ordering bug
  (`reverse-job-hunt` depends on `relationship-intelligence`, which
  runs later in the fixed array) — a one-line reorder, unrelated to
  any of the rest of this roadmap, and shouldn't wait for it.
- **Schema Registry** — formalize existing comment-block documentation
  into real, versioned JSON Schemas. Checked, not yet runtime-enforced.
- **Artifact Registry**, shadow-index form only — a read-only index
  built from what's already on disk after each run.
- **Confidence scoring**, standardized as one shared convention across
  the artifacts that already compute something like it.
- **Verification Layer**, structural checks only, advisory/log-only —
  no blocking, no claim extraction.
- **ADR library** — pure documentation, zero runtime risk, real value.
- Recommend (decision for the founder, not auto-implemented): split
  the daily automated-run commits onto a dedicated branch, separate
  from `main`'s code/template history.

### NEXT (6–12 months)

- **DAG Scheduler v2** — computed topological sort, cycle validation at
  config-load time, wave-based concurrent subprocess execution. Not a
  worker-pool service, not event-driven.
- **Verification Layer**, move toward enforcing mode once advisory
  mode's false-positive rate is known and acceptable — with an
  explicit manual-override path from day one.
- **Candidate Artifacts** (draft/published lifecycle state), bundled
  with enforcing-mode verification, not built earlier as an orphaned
  label.
- **SQLite**, only if the JSON shadow index is measurably slow to scan
  by then — measured, not assumed.
- A narrowly-scoped claim-consistency check limited to the one or two
  genuinely LLM-backed extraction surfaces (not a system-wide NLP
  claim-extraction engine).
- Employee clustering made a first-class navigational aid in the
  README and dashboard sidebar — the one legitimate idea inside
  "Domain Engines," applied as presentation, not code consolidation.

### LATER (only after proven need)

- **Cryptographic audit ledger** (or, first, the much cheaper GPG-signed
  commits) — once Evidence Intelligence ships and a real client asks
  for independent tamper-evidence.
- **Multi-tenant architecture and a tenant boundary manager** — only
  once a real second client/licensee exists. Fork-per-client remains
  the correct default until then.
- **Postgres** — only alongside a genuine, separately-decided hosted
  multi-tenant SaaS business model, never as a default upgrade from
  SQLite.
- **A general, system-wide claim-extraction layer** — only if
  LLM-generated, non-deterministic content grows into a much larger
  share of total AOS output than it is today.
- **OpenTelemetry, Kafka/NATS, event-driven execution, persistent
  worker-pool services** — not on a timeline at all under the current
  business model; revisit only if AOS's business itself becomes a
  genuinely distributed, real-time, multi-tenant SaaS platform, which
  is a decision the founder makes, not one architecture backs into.
- **Domain Engines as actual code consolidation replacing the 22
  employees** — rejected outright, permanently, unless a specific,
  concrete maintainability problem with the current structure is
  demonstrated in practice. None exists today, and the current
  structure's independence is a strength this roadmap protects, not a
  cost it should spend effort removing.
