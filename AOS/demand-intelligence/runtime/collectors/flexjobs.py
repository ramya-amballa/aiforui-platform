"""
FlexJobs connector — connector-ready, as specified. Not yet live.

FlexJobs requires a paid account and has no public API. This module is
fully wired into the collection pipeline (same collect(keywords,
config) signature as every working connector) so activating it later
is a config change, not a rewrite: once apiKey is supplied in
runtime/config/sources.json against whatever access method FlexJobs
provides to paid accounts, replace the body below with a real call and
normalise each result with collectors.common.build_opportunity(...),
exactly like greenhouse.py.
"""

SOURCE_NAME = "FlexJobs"


def collect(keywords, config):
    if not config.get("apiKey"):
        print(f"  {SOURCE_NAME}: connector-ready, no API credentials configured — skipping")
        return []
    # Not implemented: requires a paid FlexJobs account access method.
    print(f"  {SOURCE_NAME}: credentials present but the API call is not yet implemented")
    return []
