# Fractional Advisory Radar (AOS Sprint 11)

Detects organisations likely to need fractional AI Governance support
— purely additive, downstream of Demand Intelligence, read-only.

## Reuse, Not a Second Scan

The public signals this sprint asks to monitor (Enterprise AI rollout,
Microsoft Copilot deployment, ISO 42001, NIST AI RMF, AI Governance
Committee, Responsible AI initiatives, Chief AI Officer appointments)
are already exactly what `demand-signal-categories.json`'s five
categories detect. This engine reads
`demand-intelligence/organisation-profiles.json` (the same qualified
population Account Intelligence and Reverse Job Hunt already use)
rather than re-scanning the same RSS feeds with a second, parallel
taxonomy.

## What's New

- **Stage classification** (Emerging / Growing / Enterprise / Urgent) —
  a different question from Buying Readiness Band (how ready to buy).
  `failure_trigger` always means Urgent; `regulatory_trigger`/
  `governance_trigger` mean Enterprise; `funding_trigger` means
  Growing; `ai_adoption` alone means Emerging, upgraded to Growing at
  large scale (10,000+ employees, same threshold `demand_engine.py`'s
  own size heuristic uses).
- **Fractional Advisory Potential** (0-100) — a stage-based value
  nudged by the organisation's own Buying Readiness Score.
- **Recommended Engagement Model** — Discovery workshop / Retainer /
  Advisory / Implementation, one per stage, all four genuinely
  reachable.
- **Expected Consulting Revenue** — prefers a real
  `pipeline.json`/`opportunity-schema.json` figure over a heuristic,
  same "prefer the real record" pattern as Reverse Job Hunt (Sprint 9)
  and Recruiter Intelligence (Sprint 10).

## What This Sprint Deliberately Does Not Do

- Does not add a new RSS/signal collector — reuses Demand
  Intelligence's own already-collected signals entirely.
- Does not modify `organisation-profiles.json` or any scoring formula
  elsewhere in AOS.
- Does not invent a revenue figure when a real one exists — the
  heuristic is a documented, honestly-labelled fallback only.

## Dashboard

The Command Center's new **Fractional Advisory Radar** page: a refresh
button, a stage filter, and a table ranked by expected consulting
revenue.
