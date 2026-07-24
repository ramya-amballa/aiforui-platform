"""
Wellfound (AngelList Talent) connector — connector-ready, not yet live.

Wellfound has no public API; access requires whatever official or
partner integration Wellfound offers once identified. This module is
fully wired into the collection pipeline (same collect(keywords,
config) signature as every working connector) so activating it later
is a config change, not a rewrite: once apiKey is supplied in
runtime/config/sources.json, replace the body below with a real call
and normalise each result with collectors.common.build_opportunity(...),
exactly like greenhouse.py.
"""

SOURCE_NAME = "Wellfound"


def collect(keywords, config):
    if not config.get("apiKey"):
        print(f"  {SOURCE_NAME}: connector-ready, no API credentials configured — skipping")
        return []
    # Not implemented: requires an identified Wellfound access method.
    print(f"  {SOURCE_NAME}: credentials present but the API call is not yet implemented")
    return []
