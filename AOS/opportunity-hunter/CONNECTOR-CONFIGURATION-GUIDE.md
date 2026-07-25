# Opportunity Hunter — Connector Configuration Guide (Phase 1)

How to activate each of the seven Phase 1 sources: Upwork, LinkedIn
Jobs, Wellfound, RemoteOK, Greenhouse, Lever, Ashby. Current status for
all seven is in `runtime/integration-status-dashboard.md`, regenerated
every collection run — this guide is what to do about whatever it
shows.

Every connector shares the same activation model: fill in the field(s)
below in `runtime/config/sources.json`, **or** set the equivalent
environment variable (see `runtime/config/credentials.template.env`)
— either way, no code change is needed, and nothing downstream
(relevance filtering, scoring, classification, routing, Revenue
Hunter, CRM, CEO Advisor) needs to know or care which sources are
active. A source with nothing configured skips itself cleanly every
run; it never blocks the other ten sources `collect.py` also runs.

**Prefer environment variables for anything secret.** `sources.json`
is a committed file — a real API key or refresh token belongs in a
GitHub Actions repository secret or a local, gitignored `.env`, never
in `sources.json` itself. Board tokens/company slugs/job-board names
for Greenhouse, Lever and Ashby are public identifiers, not secrets,
so committing them directly to `sources.json` is fine if you'd rather
manage them there.

---

## RemoteOK — already Connected, nothing to do

Public, unauthenticated global feed (`remoteok.com/api`). No
per-company configuration exists or is needed. This is the one Phase 1
source active by default in every environment.

## Greenhouse — Awaiting credentials (a target list, not a secret)

Real, working, public per-company Job Board API
(`boards-api.greenhouse.io`) — the code already calls it for real.
What's missing is which companies to watch, since Greenhouse has no
cross-company search.

**To activate:** for each company you want to monitor, find their
Greenhouse board token — it's the slug in their careers URL,
`https://boards.greenhouse.io/{token}`. Add it to
`runtime/config/sources.json`'s `greenhouse.boardTokens` array, or set
`GREENHOUSE_BOARD_TOKENS` as a comma-separated list.

## Lever — Awaiting credentials (a target list, not a secret)

Same shape as Greenhouse: real, working, public per-company Postings
API (`api.lever.co`). Find each company's Lever slug from
`https://jobs.lever.co/{slug}`. Add it to `runtime/config/sources.json`'s
`lever.companies` array, or set `LEVER_COMPANIES` (comma-separated).

## Ashby — Awaiting credentials (a target list, not a secret)

Same shape again: real, working, public per-organisation Job Board API
(`api.ashbyhq.com/posting-api`). Find each org's job board name from
`https://jobs.ashbyhq.com/{name}`. Add it to
`runtime/config/sources.json`'s `ashby.jobBoardNames` array, or set
`ASHBY_JOB_BOARD_NAMES` (comma-separated).

## Upwork — Awaiting credentials (real secrets)

Upwork requires an authenticated developer application — there is no
public, unauthenticated job-search endpoint, and its legacy public RSS
feature (if it still exists in any form) required a logged-in session
even when it did, so it isn't a compliant unauthenticated path either.
`collectors/upwork.py` implements the real OAuth2 token-refresh and
GraphQL request mechanics; it needs three real values before it runs:

1. **Register a developer application** with Upwork to get a client
   ID and client secret (`apiKey`/`apiSecret`).
2. **Authorize it as a real Upwork user**, once, via Upwork's
   authorization-code OAuth2 flow, to obtain a refresh token
   (`refreshToken`). This step cannot be automated or done on the
   founder's behalf sight-unseen — it requires a real Upwork account
   holder to grant consent.
3. Set `UPWORK_API_KEY`, `UPWORK_API_SECRET`, `UPWORK_REFRESH_TOKEN`
   (or the equivalent `sources.json` fields).

**Before relying on this for real:** Upwork's GraphQL schema for job
search may have changed since `collectors/upwork.py` was written
without live access to confirm it. Open Upwork's GraphQL schema
explorer (available from the Upwork Developer Portal once your app is
approved) and compare it against `DEFAULT_JOB_SEARCH_QUERY` in that
file. If the schema differs, set `sources.json`'s `upwork.graphqlQuery`
to the corrected query — no code change needed. If the query doesn't
match, the connector logs the GraphQL error and returns zero results;
it will never fabricate a posting from a malformed response.

## LinkedIn Jobs — Awaiting API access (not self-serve)

LinkedIn's Terms of Service explicitly prohibit scraping job listings,
so no scraping fallback exists here, by design. The only compliant
path is LinkedIn's Talent Solutions / Jobs API, which requires applying
for and being approved as a partner — this is an access-approval
process, not something you can self-serve a key for. Once approved,
LinkedIn provides its own current API contract as part of that
approval; `collectors/linkedin_jobs.py` is wired to receive an
`apiKey`/access token via `sources.json` or `LINKEDIN_JOBS_API_KEY`,
but the actual API call still needs to be written against whatever
contract LinkedIn provides at approval time — it cannot be written
blind ahead of that, since LinkedIn's partner API surface isn't
publicly documented in a stable way.

## Wellfound — Awaiting API access (no known path today)

Wellfound (formerly AngelList Talent) does not currently publish a
public, self-serve API; its earlier developer API was discontinued.
No compliant path — public or partner — is documented today, so, as
with LinkedIn, no scraping fallback was built. If Wellfound introduces
an API or partner integration in the future, `collectors/wellfound.py`
is already wired to receive an `apiKey` via `sources.json` or
`WELLFOUND_API_KEY`; the real call still needs implementing against
whatever contract becomes available.

---

## Testing a Connector Independently

`runtime/tests/test_collectors.py` unit-tests every Phase 1 connector's
parsing and skip-logic against realistic canned API responses, without
making a live network call — run it any time with:

```
python3 -m unittest AOS.opportunity-hunter.runtime.tests.test_collectors -v
```

(or `cd` into `runtime/` and `python3 -m unittest tests.test_collectors -v`).

To test a connector against the real API by hand once credentials are
set, run it directly:

```python
from collectors import greenhouse
import json
config = json.load(open("config/sources.json"))["greenhouse"]
keywords = json.load(open("config/keywords.json"))["keywords"]
print(greenhouse.collect(keywords, config))
```

## Verifying a Day's Collection

Every run of `collect.py` writes, automatically:

- `runtime/snapshots/{date}-collection-snapshot.json` — every posting
  found, per source, whether or not it was a duplicate
- `runtime/output/{date}-collection-verification-report.md` — a
  human-readable per-source table: did it run, how many postings, any
  error
- `runtime/integration-status-dashboard.md` — the current Connected /
  Awaiting credentials / Awaiting API access / Disabled status of
  every Phase 1 source (overwritten each run, always current)

None of these change what the Relevance Engine, scoring, classification,
routing, Revenue Hunter, CRM, or CEO Advisor do — they are read-only
reporting over the same `ingest.py` pipeline every opportunity, from
any source, already goes through unchanged.
