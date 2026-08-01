# Daily Collection Verification Report

**Date:** 2026-07-26

**Total postings discovered today (before dedup):** 13

| Source | Ran | Postings Found | Error |
|---|---|---|---|
| Demand Signals | Yes | 0 | - |
| Upwork | Yes | 0 | - |
| LinkedIn Jobs | Yes | 0 | - |
| Wellfound | Yes | 0 | - |
| RemoteOK | Yes | 13 | - |
| Greenhouse | Yes | 0 | - |
| Lever | Yes | 0 | - |
| Ashby | Yes | 0 | - |

A count of 0 with no error usually means the connector ran cleanly and found nothing matching this run — not a failure. It can also mean the underlying HTTP request itself failed (unreachable network, rate limit, 5xx): `common.http_get_json()` catches that internally and returns no data so one source's outage never stops the rest of the run, which means it doesn't reach this report's Error column either. Check the run's own log/console output for a `fetch failed (...)` line for the authoritative picture of *why* a count is 0. The Error column here only reflects an exception that escaped all the way to collect.py's own per-source handler (a bug in a connector, not a network condition).

See `integration-status-dashboard.md` for whether a source is Connected, still awaiting credentials/API access, or disabled.
