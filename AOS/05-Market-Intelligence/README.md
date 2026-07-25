# Market Intelligence

AI employee #5. Tracks regulatory, standards and market developments
relevant to AI and technology governance, and turns every real change
into a concrete action for another AI employee to pick up, rather than
just a note that sits unread.

## Files

- `operating-manual.md` — mission, what's tracked, and the trigger rule
- `regulatory-log.json` — the log of tracked developments and the
  actions each one triggered
- `market-intelligence-classification-model.md` — the six deterministic
  checks run against every substantive development, and exactly what
  each one routes to

Start with `operating-manual.md`.

## Execution

`runtime/` is this specification running as code: `python3
runtime/monitor.py` checks every configured source, classifies every
new development, and routes structured records to Content Director,
Product Manager, Opportunity Hunter and CEO Advisor. See
`market-intelligence-classification-model.md`, then `runtime/monitor.py`'s
own docstring.
