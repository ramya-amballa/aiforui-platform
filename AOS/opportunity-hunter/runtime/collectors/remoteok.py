"""
RemoteOK API connector — real, public, no authentication.

https://remoteok.com/api

Unlike Greenhouse/Lever/Ashby, this is one global feed of remote
listings across all companies — no per-company configuration needed,
so this connector is active by default.
"""

from . import common

SOURCE_NAME = "RemoteOK"


def collect(keywords, config):
    url = "https://remoteok.com/api"
    data = common.http_get_json(url, headers={"User-Agent": "Mozilla/5.0 (AOS-OpportunityHunter/1.0)"})
    if not data:
        return []

    results = []
    # RemoteOK's first array element is a legend/metadata object, not a job.
    for job in data:
        if not isinstance(job, dict) or "position" not in job:
            continue
        title = job.get("position", "")
        description = job.get("description", "")
        tags = " ".join(job.get("tags", []) or [])
        matched = common.match_keywords(f"{title} {description} {tags}", keywords)
        if not matched:
            continue
        results.append(common.build_opportunity(
            source=SOURCE_NAME,
            title=title,
            organisation=job.get("company", "Unknown"),
            description=description,
            url=job.get("url"),
            location=job.get("location", "Remote"),
            remote=True,
            matched_keywords=matched,
        ))
    return results
