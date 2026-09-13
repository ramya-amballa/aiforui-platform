# AOS — Handoff / Current State

Written 2026-09-13, after syncing this session to the actual latest
`main` (it had moved 38 commits since this session's own last save —
this document reflects what's really there now, not what an earlier
turn in this conversation last saw).

## Where things are

- **Repo:** `https://github.com/ramya-amballa/aiforui-platform`, branch `main`.
- **Clone it:** `git clone https://github.com/ramya-amballa/aiforui-platform.git && cd aiforui-platform/AOS`
- **Run it:** `python3 orchestrator/orchestrator.py` from inside `AOS/`. No install step for most of it.
- **Read the output:** `AOS/output/ceo-advisor/ceo-daily-report.md` first, `AOS/output/executive-dashboard/executive-dashboard.md` second.

## The single most important fact right now

**AOS has been running automatically in production for 40+ days**
(`.github/workflows/aos-daily-operations.yml`, one commit per day from
2026-08-03 through today, e.g. `AOS Orchestrator: daily run
(2026-09-13)`). The platform side is proven — it hasn't needed a human
to remember to run it.

**Real business usage hasn't started yet.** As of today's run:
- `06-CRM/company-intelligence.json` — **0 companies.** Nothing real has been entered.
- Website Intake — **0 enquiries in the last 7 days.**
- `delivery-log.json` — **doesn't exist yet.** No engagement has ever reached "won."
- Today's CEO Advisor report's own Strategic Alert: *"No website enquiries received — 0 website leads in the last 7 days"* and its own recommendation: *"Review whether the website's calls to action... are converting."*

In plain terms: **the operating system works; the business hasn't been fed into it yet.** That gap, not anything technical, is the actual bottleneck.

## Key documents, in the order to read them

1. `AOS/ARCHITECTURE-CONSTITUTION.md` — what AOS fundamentally is, and what may never be traded away. Treat as fixed.
2. `AOS/adr/` — specific past decisions (0001 Artifact Registry, 0002 stdlib over Pydantic, 0003 wiring the registry into the daily run). Historical record, not a to-do list.
3. `AOS/AOS-PRACTICE-VALIDATION-ROADMAP.md` — **the current operating guide.** KPIs, the first-20-engagements plan, and — importantly — the rule that architecture stays frozen unless repeated real evidence justifies a change.
4. `AOS/AOS-BUSINESS-SCORECARD.md` — the day-zero KPI tracker (still day zero, per the numbers above). [Visual version](https://claude.ai/code/artifact/35995fbb-3bb2-425c-b4fb-0767f65df45f).
5. `AOS/README.md` — the employee-by-employee index, for looking up what a specific one of the 24 employees does.

## What's likely still blocking real leads

Two contact paths exist on the live site, both privacy-safe (nothing rendered in the HTML), both gated by a Vercel environment variable:
- **Email** via Resend — needs `RESEND_API_KEY` and `CONTACT_TO_EMAIL` set in Vercel. This was still unconfigured as of our last check.
- **WhatsApp** via `/api/whatsapp` — needs `WHATSAPP_NUMBER` set in Vercel (digits only, e.g. `919392696371`). Falls back to the contact form if unset, silently.

Given zero enquiries in 7 real days of live traffic, it's worth confirming both are actually set in Vercel — not just that the code is right.

## Immediate next steps

1. Confirm `RESEND_API_KEY` / `CONTACT_TO_EMAIL` / `WHATSAPP_NUMBER` are actually set in Vercel.
2. Put real prospects into `06-CRM/company-intelligence.json` — AOS has nothing to work with until this file has real companies in it.
3. Start Engagement 1 (Roadmap §2, Cohort A) the moment a real prospect exists.
4. Start the two founder habits from day one of Engagement 1: a satisfaction note and a referral source, in `delivery-log.json`'s `clientSatisfactionNote` and `company-intelligence.json`'s `referredBy` — both fields exist now; neither can be filled in retroactively.

## Two things in this repo outside AOS's scope — flagging, not assuming

This repo now also contains `workbench/` (an "AI Governance Workbench" — ontology, an Explorer UI, incident editions, its own `workbench-validate.yml` CI) and `youtube-question-bank-factory/` (a video-production tool, unrelated to consulting). Neither was built in this session and neither is referenced by AOS or the Roadmap. Worth confirming whether these are active parallel work you want kept, or something to leave alone/archive — this handoff doesn't assume either way.
