# Opportunity Relevance Engine v1

Runs inside `runtime/ingest.py`, immediately after an inbox record is
read and before `opportunity-scoring-engine.md`'s scoring runs. It
answers a narrower question than the scoring engine does: not "how
good is this opportunity" but "is this actually about AI governance,
AI risk, AI deployment, or AI security consulting at all, or did it
only surface because a short keyword string happened to appear
somewhere in the text." Opportunities that fail this check never reach
`opportunity-schema.json`, never get a priority score, and never reach
Revenue Hunter.

## Why This Exists

The first live run of the Collection Engine surfaced fourteen postings
— a paralegal role, an animal-cruelty case specialist, a Taco Bell crew
posting, a handyperson-driver role — every one of them carrying a
matched keyword of `RAG`. The postings don't mention AI at all; the
word "RAG" matched as a bare substring inside ordinary words like
"sto**rag**e", "prog**ra**m" and "D**rag** to change". `RAG` is a real,
necessary keyword (retrieval-augmented generation is core to AI for
U&I's work) but a 3-letter keyword will always do this on naive
substring matching. This engine is the fix: it re-examines each
posting's actual text for real AI-governance content using
whole-word matching, rather than trusting that the upstream keyword
hit meant anything on its own.

## Relevance Score (0-100)

Fifteen signal categories, each with a fixed point value, matched by
whole-word (not substring) search across the posting's title and
description combined — deliberately **not** its `domainTags`.
`domainTags` is set by the Collection Engine's own heuristic, derived
from the very upstream keyword match this engine exists to
double-check; scoring against it would let a false-positive keyword
match validate itself through its own downstream tag. A category
contributes its full points if any of its terms appear anywhere in the
title/description text — there is no partial credit within a category,
only across categories.

| Category | Points | Example terms |
|---|---|---|
| AI Governance | 15 | ai governance, ai oversight |
| AI Risk | 12 | ai risk, model risk, algorithmic risk |
| Responsible AI | 10 | responsible ai, ethical ai, trustworthy ai |
| Governance context | 10 | governance, oversight, accountability, raci |
| Compliance context | 10 | compliance, regulatory, audit, risk management |
| Role responsibilities | 10 | governance framework, policy development, control design, risk appetite, model validation, use case review |
| Cybersecurity context | 8 | cybersecurity, information security, security operations |
| Deployment context | 8 | ai deployment, model deployment, mlops, production rollout |
| Consulting context | 8 | advisory, consulting, client engagement |
| Microsoft Copilot | 8 | microsoft copilot, copilot studio |
| Required skills | 8 | nist ai rmf, iso 42001, gdpr, dora, eu ai act, grc |
| LLM | 6 | llm, large language model, foundation model, gpt |
| RAG | 6 | rag, retrieval augmented generation, rag pipeline |
| AI context (general) | 6 | artificial intelligence, machine learning, generative ai |
| Company industry | 5 | financial services, government, critical infrastructure, enterprise saas |

Points sum to a maximum of 130 (capped at 100) so that a genuine
opportunity — which typically hits several categories at once — clears
100 comfortably, while a posting that only hits the weakest categories
(AI context, LLM, RAG — the three easiest to false-positive) stays well
below any reasonable threshold on its own.

## Penalties

Two independent penalty rules, both designed so a real specialised role
(an AI governance counsel, an AI-policy HR lead) isn't punished for
also matching a role-family term, while a genuinely unrelated posting
is:

**1. Role-family penalty.** If the text matches a penalised role
family's terms:

| Family | Penalty | Example terms |
|---|---|---|
| Legal | -40 | paralegal, attorney, legal counsel, litigation |
| Healthcare (unrelated to AI) | -40 | nurse, clinical, patient care, physician, caregiver |
| HR | -40 | human resources, recruiter, talent acquisition, people ops |
| Administrative | -35 | data entry, file clerk, administrative assistant |
| Generic analyst | -25 | business analyst, data analyst, financial analyst |

The full penalty applies only if **zero** of the fourteen AI-related
categories above (everything except Company industry) matched — i.e.
the posting is purely a legal/healthcare/HR/admin/analyst role with no
AI content whatsoever. If exactly one AI-related category matched, the
penalty is halved (still probably a false positive, but not
certainly). If two or more AI-related categories matched, no penalty
applies at all — a role like "AI Governance Counsel" or "HR Lead, AI
Policy Adoption" is allowed to stand on its real signal.

**2. Isolated-buzzword penalty.** If exactly one category matched in
total, and that category is AI context, LLM, or RAG — the three
easiest for a single common word to trigger by accident — an
additional flat -15 applies. A posting needs more than one weak,
generic hit to be taken seriously.

## Relevance Threshold

**Threshold: 50.** Below 50, the opportunity is rejected before
scoring. This is set deliberately high relative to any single
category's points (the two strongest categories, AI Governance and AI
Risk, sum to only 27) specifically so that no single strong-sounding
keyword match is ever enough on its own — real opportunities clear it
by combining several categories, the way an actual job posting or
brief actually reads.

## Worked Examples

**Passes (score 93).** A posting reads: "We are looking for an AI
Governance consultant to lead deployment governance for our Microsoft
Copilot and RAG-based LLM applications, ensuring AI risk assessment,
responsible AI principles and regulatory compliance across our AI
systems in production." Matches: AI Governance (15), AI Risk (12),
Responsible AI (10), Governance context (10), Compliance context (10),
Deployment context (8), Consulting context (8), Microsoft Copilot (8),
LLM (6), RAG (6) = 93. No role-family match, no penalty. **93 ≥ 50 →
passes, proceeds to scoring.**

**Rejected (score 0).** The real "Animal Cruelty Case Specialist"
posting from the first live run: the text describes investigating
animal-welfare complaints, with no AI, governance, risk, deployment or
compliance content anywhere. Zero categories match (the upstream `RAG`
keyword hit was `sto**rag**e`/similar, not a real occurrence of the
word "RAG" — this engine's whole-word matching correctly finds
nothing). **0 < 50 → rejected.** Reason recorded: "No relevance signals
matched in posting text; upstream keyword match (`RAG`) did not
correspond to a real occurrence of any tracked term — likely a
substring false positive, not a real opportunity."

**Rejected despite a real category (score 0).** A posting for a
"Data Entry File Clerk" mentions in passing that "the company uses
artificial intelligence tools internally to manage records." Matches:
AI context only (6). Administrative role-family matches, and since
exactly one AI-related category matched (not zero), the administrative
penalty is halved: -35 / 2 = -17.5, rounded to -18. Isolated-buzzword
penalty also applies, since the one category matched (AI context) is
one of the three weak ones: -15. 6 - 18 - 15 = -27, floored at 0.
**0 < 50 → rejected.**

**Passes despite a role-family match (score 55).** A posting titled
"HR Business Partner — AI Governance & Policy Adoption" describes
owning the AI governance framework and policy development for the AI
deployment programme, coordinating with the governance committee, and
assessing AI risk across HR systems. Five categories match: AI
Governance (15), AI Risk (12), Deployment context (8), Governance
context (10), Role responsibilities (10) = 55. The HR role-family terms
also match ("HR Business Partner"), but since five AI-related
categories matched — well above the two-or-more threshold — **no
penalty applies**. **55 ≥ 50 → passes.**

## What Happens Below Threshold

The opportunity is never written to `opportunity-schema.json`, never
scored, never routed to `08-Revenue-Hunter/pipeline.json` or
`06-CRM/company-intelligence.json`, and Sales Director never sees it.
It is written instead to `runtime/rejected/rejected-log.json` (a
cumulative record, same id-and-append convention as every other AOS
log) with its relevance score, which categories (if any) matched, and
the exact reason above, plus a same-day
`runtime/rejected/{date}-rejected-report.md` for a quick daily scan.
Nothing about a rejected posting is deleted — it's kept, with its
reasoning, in case the threshold or category list ever needs
retuning against real evidence.

## What This Engine Does Not Do

- Does not replace `opportunity-scoring-engine.md`. An opportunity that
  clears the relevance threshold is scored exactly as before, with no
  change to `compute_priority_score`, `classify`, or routing.
- Does not change how the Collection Engine or manual entry match
  keywords upstream (`demand-intelligence/runtime/collectors/common.py`'s
  `match_keywords` still does the original substring match to decide
  whether to collect a posting at all). This engine is the downstream
  check that catches what that upstream match gets wrong, not a fix to
  the upstream match itself.
- Does not reject based on `source` or `sourceCategory` alone — a
  Recruiter Channel or Marketplace posting is judged on the same
  category/penalty rules as everything else.
