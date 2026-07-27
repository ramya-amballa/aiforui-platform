"""
Generic RSS/Atom feed fetcher — reused verbatim from
demand-intelligence/runtime/collectors/feed_fetch.py, itself reused
verbatim from 05-Market-Intelligence/runtime/feeds.py's
fetch_feed_entries() (same dependency-free urllib + xml.etree.ElementTree
approach, no third-party feed parser), rather than a third,
independently-written RSS/Atom parser. Each employee stays self-
contained (no cross-employee import) — see that file for the original.
"""

import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ATOM_NS = "{http://www.w3.org/2005/Atom}"


def fetch_feed_entries(url, timeout=15):
    """Returns a list of {title, link, summary, published, guid} dicts,
    or [] on any fetch/parse failure — one bad feed must never stop the
    rest of the run."""
    request = urllib.request.Request(url, headers={"User-Agent": "AOS-TenderIntelligence/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"    fetch failed ({url}): {exc}")
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        print(f"    parse failed ({url}): {exc}")
        return []

    if root.tag == "rss" or root.find("channel") is not None:
        return _parse_rss(root)
    if root.tag == f"{ATOM_NS}feed" or root.tag == "feed":
        return _parse_atom(root)
    return []


def _text(el):
    return (el.text or "").strip() if el is not None else ""


def _parse_rss(root):
    entries = []
    channel = root.find("channel")
    if channel is None:
        return entries
    for item in channel.findall("item"):
        entries.append({
            "title": _text(item.find("title")),
            "link": _text(item.find("link")),
            "summary": _text(item.find("description")),
            "published": _text(item.find("pubDate")),
            "guid": _text(item.find("guid")) or _text(item.find("link")),
        })
    return entries


def _first(*elements):
    """Returns the first non-None element. Plain `a or b` is wrong here:
    ElementTree's Element.__bool__ is based on child count, so a real,
    populated leaf element like <title>text</title> (no child elements)
    is falsy and `or` would skip straight past it to the next
    candidate — silently dropping real content."""
    for el in elements:
        if el is not None:
            return el
    return None


def _parse_atom(root):
    entries = []
    for entry in root.findall(f"{ATOM_NS}entry") or root.findall("entry"):
        link_el = _first(entry.find(f"{ATOM_NS}link"), entry.find("link"))
        link = link_el.get("href", "") if link_el is not None else ""
        summary_el = _first(entry.find(f"{ATOM_NS}summary"), entry.find("summary"),
                             entry.find(f"{ATOM_NS}content"), entry.find("content"))
        published_el = _first(entry.find(f"{ATOM_NS}published"), entry.find("published"),
                               entry.find(f"{ATOM_NS}updated"), entry.find("updated"))
        id_el = _first(entry.find(f"{ATOM_NS}id"), entry.find("id"))
        title_el = _first(entry.find(f"{ATOM_NS}title"), entry.find("title"))
        entries.append({
            "title": _text(title_el),
            "link": link,
            "summary": _text(summary_el),
            "published": _text(published_el),
            "guid": _text(id_el) or link,
        })
    return entries
