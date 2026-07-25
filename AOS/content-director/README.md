# Content Director — Draft Generation Engine (Runtime v1.0)

The executable half of Content Director: turns already-classified
signals (Market Intelligence's checks, Opportunity Hunter's `Convert
into Content` opportunities, shipped products, CEO Advisor's daily
priority) into publish-ready drafts, without deciding relevance itself
and without ever publishing anything.

`02-Content-Director/` remains the specification — mission, the five
objectives, `content-conversion-map.md`, `content-brief-template.md`,
`published-content-log.json` — and keeps running exactly as documented
there. This folder is the newer, narrower half of the same employee:
the moment a signal is worth turning into content, it generates the
actual draft.

## Files

- `content-generation-model.md` — every source consumed, the seven
  determinations, the hashtag/hero-image/CTA rules, the content score,
  and the three statuses this engine reports upward
- `runtime/` — this specification, running as code

## How It Fits AOS

- **Reads from:** `02-Content-Director/content-brief-queue.json`,
  `05-Market-Intelligence/regulatory-log.json`,
  `opportunity-hunter/opportunity-schema.json`,
  `03-Product-Manager/shipped-products-log.json`,
  `executive-dashboard/executive-dashboard.md`,
  `sales-director/runtime/config/practitioner-bank.json` — all
  read-only
- **Writes to:** `runtime/queue/`, `runtime/output/`, `runtime/logs/`
  only
- **Feeds:** `09-CEO-Advisor`, one of three words per batch of drafts —
  `Ready to Publish`, `Needs Review`, or `Low Value`. CEO Advisor never
  sees the drafts themselves.

## What This Is Not

Not a publishing pipeline. Every draft is a markdown file for the
founder to read, edit, and post by hand — `Ready to Publish` is a
priority label, not a send instruction, exactly as Sales Director's
`Ready To Send` never sends a proposal on its own.

Start with `content-generation-model.md`, then `runtime/generate.py`'s
own docstring for the exact mechanics.
