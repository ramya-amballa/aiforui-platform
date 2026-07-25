# Website Intake Runtime — Model

How a website enquiry becomes an AOS opportunity, a CRM record, a
Revenue Hunter pipeline entry, a Service Mapping recommendation, and a
CEO Advisor notification — automatically, deterministically, with no
email ever sent from this runtime. Every rule below is implemented, in
this order, in `runtime/generate.py`; the lookup tables live in
`runtime/config/website-intake-config.json`.

## How a Submission Reaches This Runtime

AI for U&I's website (`aiforu-platform/`) has exactly one real
enquiry form today: the Contact page's `ContactForm`, which is also
what "Start a Conversation" refers to everywhere else on the site —
there is no separate ADGL, OPERA, or Selected Engagement Areas form;
those pages' closing `CtaBand` all link through to the same Contact
form. This runtime distinguishes them by which page the visitor was on
when they clicked through, carried as a `sourcePage` value
(`adgl` / `opera` / `selected-engagement-areas` / `contact` /
`start-a-conversation`) appended to the `/contact` link and forwarded
as a hidden form field — see `aiforu-platform/src/components/
sections/cta-band.tsx`'s `sourcePage` prop and
`aiforu-platform/src/app/api/contact/route.ts`'s `sourcePage` handling.

The website's `/api/contact` route, after its existing Resend
notification email (unchanged), makes a best-effort, connector-ready
call to commit the submission as a JSON file into this runtime's
`runtime/inbox/` via the GitHub Contents API — see
`aiforu-platform/README.md`'s "AOS Website Intake" section for the
exact environment variables and what a raw submission file looks like.
This call is wrapped so its failure never affects the response the
visitor sees; the Resend email remains the guaranteed notification path
regardless of whether the GitHub commit succeeds.

**Raw submission schema** (what a file in `runtime/inbox/` contains):

```json
{
  "name": "string",
  "organization": "string, may be empty",
  "role": "string, may be empty",
  "email": "string",
  "message": "string",
  "sourcePage": "adgl | opera | selected-engagement-areas | contact | start-a-conversation",
  "submittedAt": "ISO 8601 timestamp, server-stamped"
}
```

## 1. Lead ID

`lead-{sha256(email|submittedAt|sourcePage|message)[:12]}` —
content-derived and deterministic, so the same raw submission (if it
somehow reappeared) always yields the same Lead ID, the same
convention `demand-intelligence/runtime/collect.py`'s `dedupe_key()`
already uses. This is a distinct identifier from the opportunity id
`ingest.py` separately assigns (`opp-XXXX`) — the two are
cross-referenced via `notes`, see below.

## 2. Lead Classification

`sourcePage` is checked first — the strongest available signal, since
it's a genuine action the visitor took (which page they were reading
before reaching out), not an inference from text:

- `adgl` → **ADGL enquiry**
- `opera` or `selected-engagement-areas` → **AI Governance Advisory**
- `contact` / `start-a-conversation` → no page signal, fall through

When there's no page signal (or as a secondary check), the message is
matched against keyword lists in priority order: Fractional Consulting
→ Speaking → Workshop → Training → Partnership → ADGL enquiry → AI
Risk Assessment → AI Governance Advisory. No match → **Unknown**, never
forced into a category the text doesn't support.

## 3. Qualification

- **Probability** (0-10): a documented base (5), nudged by message
  length — a substantive message (40+ words) suggests a more
  considered enquiry (+1); a very short one (under 10 words) suggests
  less (-1).
- **Strategic Value** (0-10): a documented base (5), +3 if the visitor
  came from the ADGL or OPERA/methodology page specifically (AI for
  U&I's flagship methodologies), else +2 if the Lead Classification is
  ADGL enquiry or AI Governance Advisory.
- **Revenue Potential** (0-10): a fixed table per Lead Classification
  (Fractional Consulting highest at 8, Speaking lowest at 3) — the same
  kind of documented default Service Mapping Engine's own project-size
  defaults use, never a fabricated dollar figure.
- **Urgency** (High/Medium/Low): keyword match against the message
  only ("urgent", "asap", "this week", etc. → High; "this month",
  "soon" → Medium; else Low).
- **Industry**: best-effort keyword match against the message and
  organisation name (banking, healthcare, government, technology,
  energy, retail, manufacturing) — `"Not specified"` when nothing
  matches, never guessed beyond what the text actually says.
- **Geography**: same approach, against the same served-geography
  vocabulary `demand-intelligence/runtime/collectors/common.py` already
  uses (UAE, US, UK, India, Europe) — `"Not specified"` otherwise.
- **Organisation Size**: always **"Unknown"**. The contact form
  collects nothing — no employee count, no revenue, no headcount
  signal of any kind — that could support even a heuristic guess. This
  mirrors CRM's own precedent of reporting Speaking Contact/Partner as
  an honest gap rather than guessing.

## 4-6. Building the Opportunity Record, and Why the Relevance Engine Is Bypassed

The qualification above is mapped onto `opportunity-schema.json`'s own
eleven 0-10 dimensions (documented defaults for the two dimensions a
raw enquiry gives no signal for at all: `relationshipValue` = 6,
`remoteCompatibility` = 8 — a self-initiated enquiry implies some
relationship intent already, and advisory work is generally
remote-compatible). The resulting record is written to
`demand-intelligence/runtime/inbox/` in the exact shape `ingest.py`
already accepts, and `ingest.py` is invoked as its own subprocess —
the same relevance filter, scoring, classification and routing to
Revenue Hunter/CRM every other source already goes through, completely
unduplicated.

**One deliberate, documented change was made to `ingest.py` itself**:
records with `source == "Website"` are exempted from
`opportunity-relevance-engine.md`'s scoring, rather than scored.
That engine exists to answer one specific question — "did this posting
only surface because a keyword coincidentally appeared in unrelated
text" (its own worked example: a scraped "Paralegal" posting matching
bare "RAG"). A website enquiry cannot have that problem: it is a
self-initiated, self-selected message from a real visitor to AI for
U&I's own site, not a scraped posting that might be about anything.
Testing this runtime against real enquiry phrasing (natural,
conversational prose — nothing like a job posting's keyword-dense
style) confirmed the relevance model, unmodified, would have rejected
genuine, well-qualified leads (an explicit ADGL rollout enquiry scored
18/100) purely because conversational prose doesn't repeat the exact
terms the model's fifteen categories match against. The fix is a
four-line conditional at `ingest.py`'s scoring call site, not a change
to `relevance.py`'s model, tables, or threshold — every other source
is scored exactly as before, unchanged and independently verified
still working.

Revenue Hunter's and the Service Mapping Engine's own `generate.py`
scripts are then invoked the same way (subprocess), so the opportunity
is admitted to the pipeline and mapped to a recommended service the
same day — both are already idempotent (their own processed-index
files), so an extra mid-day call changes nothing for opportunities
they've already handled and only picks up what's new.

## 5. Guaranteeing a CRM Record

`ingest.py`'s own `route_to_crm()` only creates a CRM record for four
classifications (Follow Recruiter, Relationship Building, Partnership,
Immediate Proposal) — a website lead very often classifies as `Apply`
instead (see `opportunity-scoring-engine.md`'s decision tree), which
would leave no CRM record at all under that routing alone. Since a
self-initiated website enquiry is always worth tracking — unlike an
auto-collected scraped posting, there's no risk this is noise —
`ensure_crm_record()` checks whether the organisation already has a
record (created either by `ingest.py`'s own routing or a prior lead)
and, only if genuinely missing, creates one using the *exact same
defaults* `route_to_crm()`'s own "new company" branch already
establishes (`relationshipTemperature: "warm"`, a 10-day
`nextFollowUpDue`, per `04-Sales-Director/follow-up-priority-model.md`'s
own `FOLLOW_UP_DAYS` table) — mirrored, not reinvented. This never
writes `relationshipTemperature`/`nextFollowUpDue`/`outreachHistory`
for a company that already has a record — those stay Sales Director's
exclusively, exactly as CRM's own README already documents.

## Sales Package

- **CRM record**: guaranteed to exist per the above.
- **Recommended Service / Proposal Template**: read directly from
  `service-mapping/service-recommendations.json` once the Service
  Mapping Engine has run — no second opinion computed here.
- **Suggested Discovery Call Agenda**: a fixed six-step structure per
  Lead Classification (`discoveryCallAgendaByClassification` —
  currently one shared structure for all classifications, since a
  discovery call's shape — context, current state, scope, timeline,
  approach, next steps — is the same regardless of what a client is
  asking about; only the conversation's *content* differs, which is
  what the Service Mapping recommendation and the opportunity's own
  `domainTags` inform, not this agenda's structure).
- **Follow-Up Tasks**: a fixed checklist per Urgency band
  (`followUpTasksByUrgency`) — always includes logging the CRM record;
  High urgency additionally flags same-day response and a same-day CEO
  Advisor priority.

## 7. Notifying CEO Advisor

`runtime/output/ceo-advisor-feed.json` — the same additive-feed-file
convention every previous new source has used (Market Intelligence,
Content Director, Sales Director's own feed). `09-CEO-Advisor/
decision-model.md` gained one new normalisation row:
Urgency High/Medium/Low → value 8/6/4 — a self-initiated enquiry from
the primary acquisition channel is treated as worth same-day attention
even at its lowest urgency band, since every one of them is a real,
already-interested prospect, not a speculative lead.

## What This Runtime Does Not Do

- Does not send any email, to the prospect or anyone else — every
  output is a file on disk. The one email in this entire flow (the
  founder's own internal notification) is the website's pre-existing
  Resend call, unrelated to and unchanged by this runtime.
- Does not re-implement Demand Intelligence's scoring or classification,
  Revenue Hunter's forecasting, CRM's schema, or the Service Mapping
  Engine's decision tables — every one of those is invoked as its own
  already-built script.
- Does not change any of the above for any other source — the
  relevance-filter exemption is scoped to `source == "Website"` only,
  verified by re-running the existing connector test suites unchanged
  after this runtime was added.

## Assumptions vs. Verified Behaviour

**Verified**: the full chain (Lead ID → opportunity record →
`ingest.py` → CRM guarantee → Revenue Hunter → Service Mapping → Sales
Director) was run end-to-end against two realistic fixture enquiries
(an urgent ADGL rollout enquiry from a named bank, and a low-urgency
fractional-advisory enquiry from an individual with no organisation
given) — Lead Classification, qualification, the resulting opportunity,
CRM record, pipeline entry, Service Mapping recommendation, and Sales
Director's own prepared package all matched hand-calculation. A second
run with no new inbox files changed nothing (idempotent).

**Assumptions, not verified facts**:

- The qualification heuristics (revenue-potential-by-classification,
  urgency/industry/geography keyword lists) are a first, reasonable,
  adjustable pass — not confirmed against real website traffic, since
  none exists yet.
- The website-side delivery mechanism (a GitHub Contents API commit
  from the contact form's API route) is the most conservative path
  available given the website has no database and Vercel functions
  don't persist local disk writes across invocations — it has not been
  exercised against a live Vercel deployment, since (per
  `aiforu-platform/README.md`) the site has not been deployed yet.
