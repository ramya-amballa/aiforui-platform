"""
Shared logic for career-page sources with no API: fetch the page,
strip markup, and pull the text around every keyword hit. This is a
generic page scan, not structured extraction — it will not identify
individual job titles as cleanly as an ATS API connector does. It
exists because UAE recruiter and consulting-firm career pages have no
shared API to call, unlike Greenhouse/Lever/Ashby.
"""

import re
import urllib.error
import urllib.request

from . import common

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def fetch_page_text(url, timeout=15):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AOS-OpportunityHunter/1.0)"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"    fetch failed ({url}): {exc}")
        return None
    text = TAG_RE.sub(" ", html)
    return WHITESPACE_RE.sub(" ", text).strip()


def scan_urls(urls, keywords, source_name, source_category=None, context_chars=200):
    if not urls:
        print(f"  {source_name}: no career page URLs configured, skipping")
        return []

    results = []
    for url in urls:
        text = fetch_page_text(url)
        if not text:
            continue
        matched = common.match_keywords(text, keywords)
        if not matched:
            continue
        lowered = text.lower()
        first_hit = lowered.find(matched[0].lower())
        start = max(0, first_hit - context_chars)
        end = min(len(text), first_hit + context_chars)
        snippet = text[start:end]

        results.append(common.build_opportunity(
            source=source_name,
            title=f"Opportunity mentioned on {url}",
            organisation=source_name,
            description=snippet,
            url=url,
            location="Not specified",
            remote=False,
            matched_keywords=matched,
            source_category=source_category,
        ))
    return results
