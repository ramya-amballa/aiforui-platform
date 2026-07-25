"""
Google Jobs connector — connector-ready, not yet live.

Google for Jobs has no direct public API of its own; access requires a
third-party search API (e.g. a jobs-focused SERP provider) that
surfaces the Google for Jobs index. This module is fully wired into
the collection pipeline (same collect(keywords, config) signature as
every working connector) so activating it later is a config change,
not a rewrite: once apiKey is supplied in runtime/config/sources.json
against a chosen provider, replace the body below with a real call and
normalise each result with collectors.common.build_opportunity(...),
exactly like greenhouse.py.
"""

SOURCE_NAME = "Google Jobs"


def collect(keywords, config):
    if not config.get("apiKey"):
        print(f"  {SOURCE_NAME}: connector-ready, no API credentials configured — skipping")
        return []
    # Not implemented: requires a third-party Google for Jobs search API provider.
    print(f"  {SOURCE_NAME}: credentials present but the API call is not yet implemented")
    return []
