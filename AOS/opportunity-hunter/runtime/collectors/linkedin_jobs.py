"""
LinkedIn Jobs connector — connector-ready, not yet live.

LinkedIn has no public, unauthenticated job-search API, and its Terms
of Service prohibit scraping job listings. This module is fully wired
into the collection pipeline (same collect(keywords, config) signature
as every working connector) so activating it later is a config change,
not a rewrite: once apiKey is supplied in runtime/config/sources.json
against LinkedIn's official Jobs API/Talent Solutions, replace the body
below with a real call and normalise each result with
collectors.common.build_opportunity(...), exactly like greenhouse.py.
"""

SOURCE_NAME = "LinkedIn Jobs"


def collect(keywords, config):
    if not config.get("apiKey"):
        print(f"  {SOURCE_NAME}: connector-ready, no API credentials configured — skipping")
        return []
    # Not implemented: requires LinkedIn's official Jobs API/Talent Solutions access.
    print(f"  {SOURCE_NAME}: credentials present but the API call is not yet implemented")
    return []
