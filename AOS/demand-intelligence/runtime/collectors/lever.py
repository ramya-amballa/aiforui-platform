"""
Lever Postings API connector — real, public, no authentication.

https://api.lever.co/v0/postings/{company}?mode=json

Per-company, same shape as Greenhouse. Add each company's Lever slug
(from https://jobs.lever.co/{slug}) to runtime/config/sources.json's
lever.companies to activate this for real companies.
"""

from . import common

SOURCE_NAME = "Lever"


def collect(keywords, config):
    companies = config.get("companies", [])
    if not companies:
        print("  Lever: no companies configured, skipping (add company slugs to sources.json)")
        return []

    results = []
    for company in companies:
        url = f"https://api.lever.co/v0/postings/{company}?mode=json"
        data = common.http_get_json(url)
        if not data:
            continue
        for job in data:
            title = job.get("text", "")
            description = job.get("descriptionPlain", "") or job.get("description", "")
            matched = common.match_keywords(f"{title} {description}", keywords)
            if not matched:
                continue
            categories = job.get("categories", {}) or {}
            location = categories.get("location", "Not specified")
            results.append(common.build_opportunity(
                source=SOURCE_NAME,
                title=title,
                organisation=company,
                description=description,
                url=job.get("hostedUrl"),
                location=location,
                remote="remote" in (location or "").lower(),
                matched_keywords=matched,
            ))
    return results
