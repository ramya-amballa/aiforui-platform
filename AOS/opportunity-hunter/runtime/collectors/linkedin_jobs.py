"""
LinkedIn Jobs connector — connector-ready, awaiting API access.

LinkedIn has no public, unauthenticated job-search API, and its Terms
of Service prohibit scraping job listings — this connector deliberately
does not attempt either. The only compliant path is LinkedIn's Talent
Solutions / Jobs API, which is not self-serve: it requires applying for
and being approved as a LinkedIn Marketing/Talent API partner before
any client ID or API key is issued. This is an access-approval process,
not a credential you can generate yourself — see the Configuration
Guide (../../CONNECTOR-CONFIGURATION-GUIDE.md) for what that process
involves.

This module is fully wired into the collection pipeline (same
collect(keywords, config) signature as every working connector) so
activating it later is a config change plus one implementation, not a
rewrite: once partner access is approved and an apiKey/access token is
supplied in runtime/config/sources.json, implement the real call here
against LinkedIn's own current API contract (provided only after
approval, so it cannot be written blind ahead of time) and normalise
each result with collectors.common.build_opportunity(...), exactly
like greenhouse.py.
"""

SOURCE_NAME = "LinkedIn Jobs"


def collect(keywords, config):
    if not config.get("apiKey"):
        print(f"  {SOURCE_NAME}: connector-ready, awaiting Talent Solutions/Jobs API "
              f"partner access — skipping")
        return []
    # Not implemented: LinkedIn provides its exact API contract only
    # after partner approval, so there is nothing stable to code against
    # ahead of that.
    print(f"  {SOURCE_NAME}: access token present but the API call is not yet implemented "
          f"— see the module docstring")
    return []
