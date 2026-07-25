"""
Ashby Job Board API connector — real, public, no authentication.

https://api.ashbyhq.com/posting-api/job-board/{jobBoardName}

Per-organisation, same shape as Greenhouse/Lever. Add each org's job
board name (from https://jobs.ashbyhq.com/{name}) to
runtime/config/sources.json's ashby.jobBoardNames to activate this for
real organisations.
"""

from . import common

SOURCE_NAME = "Ashby"


def collect(keywords, config):
    job_boards = config.get("jobBoardNames", [])
    if not job_boards:
        print("  Ashby: no jobBoardNames configured, skipping (add org names to sources.json)")
        return []

    results = []
    for board_name in job_boards:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{board_name}"
        data = common.http_get_json(url)
        if not data:
            continue
        for job in data.get("jobs", []):
            title = job.get("title", "")
            description = job.get("descriptionPlain", "") or job.get("description", "")
            matched = common.match_keywords(f"{title} {description}", keywords)
            if not matched:
                continue
            location = job.get("location", "Not specified")
            results.append(common.build_opportunity(
                source=SOURCE_NAME,
                title=title,
                organisation=board_name,
                description=description,
                url=job.get("jobUrl"),
                location=location,
                remote=bool(job.get("isRemote")),
                matched_keywords=matched,
            ))
    return results
