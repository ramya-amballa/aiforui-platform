"""
UAE recruiter career pages — real, functional generic page scan, no
API key needed. Add real career-page URLs to
runtime/config/sources.json's uaeRecruiters.careerPageUrls to activate.
"""

from . import generic_page_scan

SOURCE_NAME = "UAE Recruiters"


def collect(keywords, config):
    return generic_page_scan.scan_urls(
        config.get("careerPageUrls", []), keywords, SOURCE_NAME, source_category="Recruiter Channel"
    )
