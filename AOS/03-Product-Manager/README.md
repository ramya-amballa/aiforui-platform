# Product Manager

AI employee #3. Continuously evaluates whether a new regulation, a
client question, or a LinkedIn discussion should become a product, and
which format it should take.

## Files

- `operating-manual.md` — mission, the seven formats, and daily workflow
- `product-evaluation-framework.md` — how a signal gets matched to a
  format, or rejected
- `product-backlog.json` — the live list of candidate and in-progress
  products. `05-Market-Intelligence/runtime/monitor.py` now writes
  unscored candidates here directly (`signalSource: "Market
  Intelligence"`, `proposedFormat`/`score: null`) — matching a format
  and a score is still this employee's own evaluation, not Market
  Intelligence's
- `shipped-products-log.json` — the permanent organisational record of
  every product actually shipped, why it was built, and its result;
  part of AOS's long-term memory system

Start with `operating-manual.md`.
