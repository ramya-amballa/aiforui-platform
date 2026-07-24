"""
Consulting firm career pages — real, functional generic page scan, no
API key needed. Add real career-page URLs to
runtime/config/sources.json's consultingFirms.careerPageUrls to
activate.
"""

from . import generic_page_scan

SOURCE_NAME = "Consulting Firms"


def collect(keywords, config):
    return generic_page_scan.scan_urls(
        config.get("careerPageUrls", []), keywords, SOURCE_NAME, source_category="Consulting Channel"
    )
