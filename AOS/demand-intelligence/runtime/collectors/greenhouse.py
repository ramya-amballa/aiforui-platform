"""
Greenhouse Job Board API connector — real, public, no authentication.

https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true

Greenhouse has no cross-company search; each company's board is
queried individually using its board token (the slug in that
company's careers URL, e.g. https://boards.greenhouse.io/{token}).
Add tokens to runtime/config/sources.json's greenhouse.boardTokens to
activate this for real companies.
"""

from . import common

SOURCE_NAME = "Greenhouse"


def collect(keywords, config):
    board_tokens = config.get("boardTokens", [])
    if not board_tokens:
        print("  Greenhouse: no boardTokens configured, skipping (add company tokens to sources.json)")
        return []

    results = []
    for token in board_tokens:
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
        data = common.http_get_json(url)
        if not data:
            continue
        for job in data.get("jobs", []):
            title = job.get("title", "")
            description = job.get("content", "")
            matched = common.match_keywords(f"{title} {description}", keywords)
            if not matched:
                continue
            location = (job.get("location") or {}).get("name", "Not specified")
            results.append(common.build_opportunity(
                source=SOURCE_NAME,
                title=title,
                organisation=token,
                description=description,
                url=job.get("absolute_url"),
                location=location,
                remote="remote" in location.lower(),
                matched_keywords=matched,
            ))
    return results
