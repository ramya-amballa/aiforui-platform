"""
Upwork connector — connector-ready, real OAuth2 + GraphQL plumbing,
awaiting credentials.

Upwork has no unauthenticated public job-search endpoint and no
current public RSS feed for search results (its legacy RSS feature
required an authenticated session even when it existed) — an
authenticated developer application is the only compliant path. This
module implements the real mechanics of that path:

  1. Exchange a stored OAuth2 refresh token for a short-lived access
     token (RFC 6749 refresh_token grant, POSTed to Upwork's OAuth2
     token endpoint) — Upwork requires 3-legged OAuth tied to an
     authorized Upwork account for marketplace data; there is no
     server-to-server client-credentials grant for job search.
  2. Query Upwork's GraphQL API with that access token.

WHAT TO VERIFY BEFORE FIRST USE

The OAuth2 endpoint and flow below (https://www.upwork.com/api/v3/oauth2/token,
refresh_token grant) and the GraphQL endpoint (https://api.upwork.com/graphql)
are Upwork's documented, stable infrastructure URLs. The GraphQL query
body in DEFAULT_JOB_SEARCH_QUERY is a best-effort template — Upwork's
exact schema field names for job-posting search can change between API
versions, and this was written without live access to confirm the
current schema. Before activating this connector for real, open
Upwork's GraphQL schema explorer (available from the Upwork Developer
Portal once your app is approved) and confirm the query below still
matches; adjust `graphqlQuery` in runtime/config/sources.json if not —
no code change needed, the query text is read from config.

CONFIGURATION (runtime/config/sources.json's "upwork" entry)

    apiKey        -> OAuth2 client ID (from your Upwork developer app)
    apiSecret     -> OAuth2 client secret
    refreshToken  -> a refresh token obtained once via Upwork's
                     authorization-code flow (a real Upwork user must
                     authorize your app; this cannot be automated —
                     see the Configuration Guide)
    graphqlQuery  -> optional override for DEFAULT_JOB_SEARCH_QUERY

See ../../CONNECTOR-CONFIGURATION-GUIDE.md for the full activation
walkthrough, and ../config/credentials.template.env for exactly which
environment variables to set instead of committing real values here.
"""

import json
import urllib.parse
import urllib.request

from . import common

SOURCE_NAME = "Upwork"

TOKEN_URL = "https://www.upwork.com/api/v3/oauth2/token"
GRAPHQL_URL = "https://api.upwork.com/graphql"

# Best-effort — verify against Upwork's current GraphQL schema before
# relying on this (see module docstring). Deliberately requests only
# fields build_opportunity() actually uses.
DEFAULT_JOB_SEARCH_QUERY = """
query SearchJobs($query: String!) {
  marketplaceJobPostingsSearch(marketPlaceJobFilter: { titleExpression_eq: $query }) {
    edges {
      node {
        title
        description
        client { companyName }
        ciphertext
        job { publicUrl }
        engagementType
        durationLabel
      }
    }
  }
}
"""


def _refresh_access_token(client_id, client_secret, refresh_token):
    """RFC 6749 refresh_token grant. Returns an access token string, or
    None on any failure — a bad/expired refresh token must skip this
    source cleanly, never crash the run."""
    payload = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")
    request = urllib.request.Request(
        TOKEN_URL, data=payload, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": "AOS-OpportunityHunter/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            token_data = json.loads(response.read().decode("utf-8"))
            return token_data.get("access_token")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        # OSError covers urllib.error.URLError/HTTPError and every
        # lower-level socket/connection failure in one place — a
        # network hiccup here must skip this source, never crash it.
        print(f"  {SOURCE_NAME}: token refresh failed: {exc}")
        return None


def _graphql_query(access_token, query, variables):
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_URL, data=payload, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {access_token}",
                 "User-Agent": "AOS-OpportunityHunter/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"  {SOURCE_NAME}: GraphQL query failed: {exc}")
        return None


def collect(keywords, config):
    client_id = config.get("apiKey")
    client_secret = config.get("apiSecret")
    refresh_token = config.get("refreshToken")
    if not (client_id and client_secret and refresh_token):
        print(f"  {SOURCE_NAME}: connector-ready, no credentials configured — skipping")
        return []

    access_token = _refresh_access_token(client_id, client_secret, refresh_token)
    if not access_token:
        print(f"  {SOURCE_NAME}: could not obtain an access token this run — skipping")
        return []

    query = config.get("graphqlQuery") or DEFAULT_JOB_SEARCH_QUERY
    results = []
    for keyword in keywords:
        data = _graphql_query(access_token, query, {"query": keyword})
        if not data:
            continue
        if data.get("errors"):
            print(f"  {SOURCE_NAME}: GraphQL returned errors for '{keyword}' — "
                  f"the query in sources.json's graphqlQuery may not match Upwork's "
                  f"current schema: {data['errors']}")
            continue
        edges = (((data.get("data") or {}).get("marketplaceJobPostingsSearch") or {}).get("edges") or [])
        for edge in edges:
            node = edge.get("node", {}) or {}
            title = node.get("title", "")
            description = node.get("description", "")
            matched = common.match_keywords(f"{title} {description}", keywords)
            if not matched:
                continue
            job_url = ((node.get("job") or {}).get("publicUrl")) or None
            organisation = ((node.get("client") or {}).get("companyName")) or "Not disclosed"
            results.append(common.build_opportunity(
                source=SOURCE_NAME,
                title=title,
                organisation=organisation,
                description=description,
                url=job_url,
                location="Remote",
                remote=True,
                matched_keywords=matched,
            ))
    return results
