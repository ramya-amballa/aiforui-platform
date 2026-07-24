"""
Upwork connector — connector-ready, not yet live.

Upwork's job-search endpoints require an authenticated developer
application (OAuth2 client id/secret via Upwork's API); there is no
public, unauthenticated way to search open job postings. This module
is fully wired into the collection pipeline (same collect(keywords,
config) signature as every working connector) so activating it later
is a config change, not a rewrite: once apiKey/apiSecret are supplied
in runtime/config/sources.json, replace the body below with a real
call to Upwork's job-search API and normalise each result with
collectors.common.build_opportunity(...), exactly like greenhouse.py.
"""

SOURCE_NAME = "Upwork"


def collect(keywords, config):
    if not config.get("apiKey") or not config.get("apiSecret"):
        print(f"  {SOURCE_NAME}: connector-ready, no API credentials configured — skipping")
        return []
    # Not implemented: requires an authenticated Upwork API session.
    print(f"  {SOURCE_NAME}: credentials present but the API call is not yet implemented")
    return []
