# The AOS Architecture Constitution

*Ratified after three independent architectural reviews — Claude,
Gemini, and ChatGPT — converged on the same conclusion: the
22-employee architecture is sound, and its remaining risks are
evolutionary, not foundational. This document freezes that
conclusion. It is not a specification of how AOS is built. It is a
statement of what AOS is, and is not allowed to become.*

---

## Preamble

AOS exists so that one person can operate an AI governance consulting
practice with the leverage of a firm, without ever pretending to be
something it is not.

Every clause below exists to protect that sentence. Where a future
change would make AOS faster, larger, or more impressive at the cost
of that sentence, this Constitution is the standing objection.

---

## 1. Purpose

**Why AOS exists.** A solo AI-governance consulting practice needs, in
effect, a research desk, a proposal desk, a delivery desk, and a chief
of staff — four functions a firm would staff with four different
people. AOS exists to give one founder that leverage: 22 independent,
narrowly-scoped employees that find demand, qualify it, propose
against it, deliver against it, and resolve the entire day's signal
into one ranked action — without a second hire, and without a single
invented fact anywhere in the chain.

**What problem it solves.** The bottleneck a solo practitioner faces is
not expertise — it is throughput. There is real signal every day
(a company adopting AI at scale, a regulation shifting, a proposal
worth revisiting, a relationship going cold) and one person cannot
watch all of it, score all of it, and act on the highest-value item
without something doing the watching and the scoring on their behalf.
AOS is that something. It does not replace judgment. It clears
everything away from judgment except the one decision that actually
requires it.

**What AOS deliberately does not try to become.** AOS is not a
generic workflow engine, and does not try to become one by
accumulating enterprise infrastructure it hasn't earned. It is not a
distributed system — it has no distributed problem. It is not
multi-tenant — it has one client today, and will not pretend otherwise
until it has a second. It is not a platform whose value is its own
sophistication. If a future version of AOS is ever more architecturally
impressive and less trustworthy, less auditable, or harder for one
person to run alone, it has failed at the one thing it exists to do,
regardless of what else it has gained.

---

## 2. Core Architectural Principles

Each principle below is stated with the reasoning behind it, because a
rule without a reason is the first thing a future contributor discards
under pressure.

**Never fabricate.** AOS's clients are organizations that audit other
organizations for a living. A tool that invents a number to fill a gap
would be a walking contradiction of the exact discipline it sells. A
stated gap — `Not tracked`, `Not enough signal yet` — is not a failure
of the system; it is the system working correctly.

**The founder remains the record of truth.** Some facts cannot be
safely inferred — whether a relationship is actually warm, what phase
an engagement is really in, whether a standing decision still holds.
AOS reads these from the founder and never writes them. This is not a
limitation to be engineered away. Judgment that matters stays with the
person accountable for it.

**Additive, never destructive.** Nothing is ever deleted. A losing
opportunity is archived, not removed; a parked product idea stays on
record. A solo founder has no second copy of the practice's
institutional memory — losing it once is losing it permanently. The
system's default is to keep restating history, never to erase it.

**One business capability per employee.** Each of the 22 employees
does exactly one thing a real person in a real firm would be
responsible for, and nothing else. This is what lets a reviewer hold
one employee's entire logic in their head, what let 22 of them ship
independently tested (528 tests across 17 suites), and what makes a
single employee's failure a contained, diagnosable event instead of a
mystery inside a larger system.

**Human-readable persistence.** Every artifact AOS produces can be
opened and understood by a person, with no query language, no
dashboard, and no intermediary between the founder and the fact. The
moment a report requires special tooling to verify, it has stopped
being trustworthy on its own terms.

**Revenue over engineering novelty.** This is a standing, explicit
directive, not a preference: twenty rigorous templates beat two
hundred average ones, and a boring solution that sells is worth more
than an elegant one that doesn't. AOS is judged by what it produces
for the practice, never by how it looks on an architecture diagram.

**One action per day.** Twenty-one employees' worth of signal is
useless without synthesis — it is just more noise, better formatted.
The terminal step of every run exists specifically to resolve
everything upstream of it into one ranked priority. More information
is not the goal. One correct decision is.

**Simplicity before infrastructure.** Every piece of infrastructure
AOS adopts is a cost the founder personally carries, every single day
it exists, with no ops team to absorb it. Infrastructure is earned by a
demonstrated problem, never adopted in anticipation of one.

---

## 3. Architectural Invariants

An invariant is a property whose loss would make AOS a *different
system*, not an evolved version of this one. An implementation detail
is a choice that can change freely as long as the invariant it serves
survives. Confusing the two — defending a detail as if it were sacred,
or discarding an invariant because its current implementation looks
outdated — is the most common way architectures drift without anyone
deciding they should.

### Invariant

- The final step of every run is always the terminal synthesis step
  (today, CEO Advisor). Nothing may be added downstream of it. If this
  ever changes, AOS no longer resolves its own day into one decision —
  it becomes a report generator again.
- No employee ever overwrites another employee's output. Cross-employee
  reads are read-only, always.
- Founder-owned data is read-only to every employee, without
  exception, forever.
- Every output remains inspectable by a human without specialized
  tooling.
- Business-capability boundaries are preserved — no employee's
  responsibility silently grows to absorb another's.
- Nothing is destructively deleted. State changes; the record persists.
- What happened in any given run, and why, must be reconstructable
  after the fact from what is committed. Auditability is the default
  state of the system, not an optional feature bolted on.
- No artifact is trusted downstream without a traceable source.

### Implementation detail (may change; the invariant above is what must survive the change)

- **Python**, as the implementation language — the invariant is
  auditable, reviewable code; not this specific language.
- **Subprocess-per-employee** — the invariant is *isolation*, so one
  employee's failure cannot corrupt another's state; not literally
  "subprocess." Any mechanism that preserves that isolation guarantee
  satisfies the invariant.
- **Flat JSON and Markdown files on disk** — the invariant is
  human-readable, directly-inspectable persistence; not the specific
  file format. An embeddable, single-file store could satisfy the same
  invariant if it preserved that property; a networked database, on
  its own, generally would not.
- **A fixed, hand-maintained execution array** — the invariant is a
  *validated, cycle-free* execution order; not this specific
  mechanism. A computed topological sort satisfies the same invariant
  more reliably than the array does today.
- **Git as the audit ledger** — the invariant is tamper-evident,
  inspectable history; not specifically Git. Anything that preserves
  that property (and today, nothing does it more cheaply) satisfies
  the invariant.

Distinguishing these two columns is itself a discipline this
Constitution requires of every future contributor: before defending or
attacking any specific technology, name which invariant it is actually
serving, and ask whether a different implementation could serve that
same invariant better.

---

## 4. Evolution Rules

- **Prefer extending an existing employee over creating a new one.** A
  new capability that genuinely belongs to an existing employee's
  responsibility should be added there, not spun out as a 23rd
  employee whose real job overlaps an existing one.
- **Prefer a new template over new orchestration.** If the actual gap
  is a missing deliverable, a missing framework annex, or a missing
  proposal variant — solve it in `templates/`, not by adding a new
  moving part to the execution graph.
- **Infrastructure must solve a demonstrated business problem, never a
  speculative one.** "This is how a system at scale would be built" is
  not a justification. "This is the problem we are actually having
  today" is the only one that counts.
- **Every new employee must represent a genuine, real consulting
  capability** — something a real person in a real firm would own —
  never a technical convenience dressed up as a capability.
- **Every architectural change must preserve every invariant in
  Section 3, with no exceptions traded for convenience.** A change
  that improves performance, reduces cost, or adds a capability at the
  price of auditability, human-readability, or founder-owned truth is
  not a trade this Constitution allows a future contributor to make
  unilaterally.
- **Any proposal to add infrastructure must show who pays its ongoing
  cost.** If the answer is "the founder, alone, forever," that cost
  must be weighed explicitly against the problem it solves — not
  assumed away because the technology itself is well-regarded.
- **This Constitution is amended deliberately, or not at all.** No
  single sprint, pull request, or convenient shortcut erodes a
  principle or invariant by precedent. A genuine case for change is
  written down, argued, and ratified as an explicit amendment to this
  document — never inferred later from what the codebase happened to
  drift into.

---

## 5. Decision Framework

Before any architectural change is accepted, its proposer answers
these questions in writing, and a "no" or "it makes it worse" to more
than one should stop the proposal absent an explicit, argued exception:

1. Does this increase consulting value — or only the appearance of
   sophistication?
2. Does it reduce auditability, in any way, for any artifact?
3. Does it increase the operational burden the founder personally
   carries, with no ops team to share it?
4. Does it introduce infrastructure that requires ongoing maintenance
   AOS's current operating model cannot absorb?
5. Does it preserve deterministic execution — the same inputs
   producing the same outputs, reconstructable after the fact?
6. Does it preserve human readability, without requiring specialized
   tooling to verify?
7. Would rejecting this proposal cost AOS a real, demonstrated
   capability today — or only a hypothetical one it might need later?
8. Could the same real need be met by extending something that already
   exists, before anything new is built?

This is not a formality. It is the same test that separated the parts
of two prior enterprise-architecture reviews worth adopting now from
the parts that were solving problems AOS does not have. It is meant to
be run again, honestly, every time — not answered once and assumed
forever.

---

## 6. Technology Philosophy

AOS chooses **subprocess orchestration** because process isolation is
the simplest failure boundary available: one employee crashing cannot
corrupt another's state, and there is no shared-memory failure mode to
reason about, debug, or explain to an auditor.

AOS chooses **filesystem persistence** because a file the founder can
open and read *is* the audit trail — no export step, no query
language, no trust placed in an intermediary system between the fact
and the person who needs it.

AOS chooses **Markdown artifacts** because its primary audience is a
human making a judgment call, not a machine consuming an API.
Legibility is the feature. It is never a limitation waiting to be
optimized away.

AOS chooses **additive execution** because a solo practice's
institutional memory is its single most valuable and least
reconstructable asset. Nothing produced by AOS is disposable, and
nothing is designed as if it were.

AOS chooses a **deterministic DAG** because auditability requires that
what ran, in what order, reading what data, is always reconstructable
— a property a validated, fixed dependency order gives for free, and
that a queue, an event stream, or an asynchronous system has to work
hard, and add real machinery, to approximate.

AOS explicitly rejects — not as inferior technology, but as
**unjustified by any real problem AOS currently has** — a networked
database, a message broker, distributed tracing, event-driven
execution, and multi-tenant isolation. Each of these is a reasonable
default for a venture-funded, real-time, multi-tenant platform with an
operations team. None of them is a reasonable default for a
22-employee system that finishes its entire day's work in under five
seconds, run by one person. Adopting any of them ahead of a
demonstrated need would spend that one person's limited time
maintaining infrastructure instead of running the practice — the exact
trade this Constitution exists to prevent.

---

## 7. Long-Term Vision

AOS can grow for a decade without losing its identity, as long as
growth stays evolutionary — extending what exists without violating
Section 3.

**Evolutionary — consistent with this Constitution:**
- Growing past 22 employees, as long as each new one is a genuine
  capability and no invariant is compromised to add it.
- A Schema Registry, an Artifact Registry (as an additive index, not a
  replacement for the filesystem), structural verification, confidence
  scoring, and an ADR library — already reviewed, already judged sound,
  already the immediate next work.
- Moving from flat-file scanning to an embeddable index (such as
  SQLite) once file-scanning is *measurably*, not speculatively, too
  slow — as long as the underlying files remain the record of truth and
  the index stays disposable and rebuildable.
- Licensing AOS to a second consulting practice by forking the
  repository — perfect isolation, zero new architecture.
- Building genuine multi-client support through a client-scoped
  registry, *if and only if* a real second client exists and every
  invariant in Section 3 holds for both.
- A cryptographic audit ledger, or the much smaller step of signed
  commits, once Evidence Intelligence ships and a real client asks for
  independently verifiable tamper-evidence.

**Identity-violating — would make AOS a different system, not an
evolution of this one:**
- Consolidating the 22 employees into fewer, broader "engines" that
  blur business-capability boundaries in the name of a smaller
  employee count.
- Making any founder-owned data writable by any employee, for any
  reason.
- Any change that trades auditability for throughput, scale, or speed.
- Adopting a message broker or event-driven execution as the *default*
  execution model, abandoning deterministic batch runs as the norm.
- Adopting enterprise infrastructure — a networked database, a
  distributed tracing system, a message queue — before a demonstrated
  need, on the reasoning that a larger system would eventually want it.
- Removing the terminal synthesis step, or splitting the day's final
  decision across multiple competing outputs.
- Any artifact a person cannot open and understand without
  specialized tooling standing between them and the fact.

A decade from now, AOS should be recognizably the same kind of system
it is today — larger, more capable, more automated in places that have
earned it — never a different kind of system wearing the same name.

---

## 8. Relationship to the ADR Library

This Constitution states what must remain true regardless of when it
is read. The ADR library records why one specific decision was made,
at one specific point, including the alternatives considered and the
consequences accepted — a growing, evolving history of *decisions*,
sitting beneath a fixed statement of *identity*.

An ADR can extend, implement, or refine anything in this Constitution.
An ADR can never contradict it. If a genuinely good reason ever
emerges to change something this document declares invariant, that is
not a decision an ADR is allowed to make quietly — it requires an
explicit, visible amendment to this Constitution itself, argued in the
open, not a precedent that erodes the principle one accepted exception
at a time.

---

## Ratification

This Constitution was written at the close of three independent
architectural reviews — this document's own predecessor
(`architecture-v2/aos-v2-architecture.md`), a critique of a second
model's enterprise roadmap
(`architecture-v2/gemini-enterprise-roadmap-critique.md`), and the
founder's own judgment across both. All three converged: the
22-employee architecture is sound, its real risks are evolutionary,
and further architectural redesign has reached its end for now.

From here, the work is not architecture. It is building the four
things already judged worth building — the Shadow Artifact Registry,
schema contracts, structural verification, confidence scoring — writing
the ADRs that explain the decisions already made, and then using AOS,
on real engagements, for the practice it was built to run.
