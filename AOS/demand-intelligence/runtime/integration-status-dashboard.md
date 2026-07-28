# Demand Intelligence — Integration Status Dashboard

**Generated:** 2026-07-28

*Regenerated automatically at the end of every collection run (`collect.py` calls `integration_status.py`). Reflects `config/sources.json`'s current configuration and the most recent collection snapshot; regenerate by re-running collection, do not hand-edit.*

## Sources

**Demand Signals is the primary discovery mode** — it answers "which named organisation is most likely to need our services this week" directly, from real evidence of AI adoption at scale, rather than waiting for a vacancy to be advertised. Everything below it is a secondary, employment-intelligence channel.

| Source | Status | Requires | Last Run |
|---|---|---|---|
| Demand Signals | Awaiting credentials | spacy + en_core_web_sm (pip install spacy && python3 -m spacy download en_core_web_sm) | (0 found in last run) |
| Upwork | Awaiting credentials | real OAuth2 secrets (client ID, client secret, refresh token) | (0 found in last run) |
| LinkedIn Jobs | Deprioritized (by choice) | a Talent Solutions/Jobs API partner access token | (0 found in last run) |
| Wellfound | Deprioritized (by choice) | no known public/partner API exists yet to authenticate against | (0 found in last run) |
| RemoteOK | Connected | already configured | (10 found in last run) |
| Greenhouse | Awaiting credentials | public company board tokens (not secret) — one per company to monitor | (0 found in last run) |
| Lever | Awaiting credentials | public company slugs (not secret) — one per company to monitor | (0 found in last run) |
| Ashby | Awaiting credentials | public job board names (not secret) — one per organisation to monitor | (0 found in last run) |

**Summary:** 1 of 8 sources Connected, 5 Awaiting credentials, 0 Awaiting API access, 2 Deprioritized by choice.

## Deprioritized by Choice

Per explicit founder instruction (2026-07-25): stop investing effort chasing platforms that either prohibit automation outright or are low-value for this consulting model. These are real, working connectors — left wired, not deleted — but not being actively pursued:

- **LinkedIn Jobs** — Terms of Service explicitly prohibit scraping job listings; the only compliant path (Talent Solutions/Jobs API partner access) is not self-serve and not worth continued pursuit for an employment-intelligence use case Demand Signals has superseded anyway.
- **Google Jobs, Wellfound, FlexJobs** — generic job-board aggregators with the same low-signal problem RemoteOK demonstrated on a real run (13 postings discovered, 0 above the relevance threshold — see `runtime/logs`). Not worth further integration effort for an AI governance consulting model.

## Configuration

See `../CONNECTOR-CONFIGURATION-GUIDE.md` for exactly how to activate each connector above, and `config/credentials.template.env` for the environment variable names real secrets should be set as — never commit a real secret into `config/sources.json`.
