"""
Shared, dependency-free helpers used by every extraction backend
(deterministic_extractor.py and the optional claude_extractor.py):
a vendor blocklist so the AI vendor a news feed is published by is
never mistaken for the organisation the article is *about*, a
headline-pattern splitter for the common "Vendor: Customer did X"
convention vendor blogs actually use, and industry/region inference
reused verbatim from website-intake/runtime/generate.py so this
doesn't invent a second copy of the same keyword tables.
"""

import re

# AI vendors/products a news item is likely to be published by or
# mention as the tool being adopted — never the organisation itself.
# Deliberately conservative (real, well-known names only); an
# organisation whose own name happens to be a substring of one of
# these is a false-negative risk this list accepts, since the reverse
# (crediting a vendor as the "organisation adopting AI") is the far
# more common and more damaging failure mode this exists to prevent.
VENDOR_BLOCKLIST = [
    "microsoft", "copilot", "openai", "chatgpt", "gpt-4", "gpt-5",
    "anthropic", "claude", "google", "gemini", "bard", "amazon", "aws",
    "ibm", "watsonx", "salesforce", "einstein", "meta ai", "llama",
    "mistral", "cohere", "nvidia", "azure", "vertex ai",
]

# Reused verbatim from website-intake/runtime/config/website-intake-config.json's
# industryKeywords — same table, not a second copy invented for Demand
# Intelligence. "Not specified" when nothing matches, never guessed.
INDUSTRY_KEYWORDS = {
    "Financial Services": ["bank", "banking", "insurer", "insurance", "asset management", "financial services", "fintech"],
    "Healthcare": ["hospital", "healthcare", "health system", "pharma", "life sciences", "biotech"],
    "Government": ["government", "public sector", "ministry", "federal", "municipal", "agency"],
    "Technology": ["saas", "software company", "tech company", "startup", "platform"],
    "Energy": ["energy", "utility", "utilities", "oil and gas", "renewables"],
    "Retail": ["retail", "e-commerce", "ecommerce", "consumer goods"],
    "Manufacturing": ["manufacturing", "industrial", "supply chain"],
}

ACTION_VERBS = [
    "deployed", "adopted", "rolled out", "launched", "announced", "appointed",
    "raised", "faces", "disclosed", "implemented", "introduced", "unveiled",
]


def is_vendor_name(candidate):
    lowered = candidate.lower()
    return any(vendor in lowered for vendor in VENDOR_BLOCKLIST)


def split_vendor_headline(title):
    """Vendor blogs commonly title customer stories "Vendor: Customer did
    X" (e.g. "Microsoft: Land O'Lakes deploys Copilot to 40,000
    employees"). Returns (vendor_label_or_None, remainder) — remainder
    is the whole title unchanged if no such pattern is present."""
    match = re.match(r"^([A-Za-z][\w\s&.,'-]{1,40}):\s+(.+)$", title or "")
    if not match:
        return None, title
    label, remainder = match.group(1).strip(), match.group(2).strip()
    return label, remainder


def infer_industry(text):
    lowered = (text or "").lower()
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return industry
    return "Not specified"


_STOPWORD_START = {"The", "This", "That", "These", "Those", "It", "A", "An", "In", "On", "At",
                    "For", "With", "After", "Following", "According", "Local", "New"}

# Generic acronyms/role titles that are never, on their own, an
# organisation name — filtered so "AI", "Chief AI Officer", "US" etc.
# never get treated as a candidate. Multi-word phrases are only
# excluded if EVERY word in them is on this list (so "Acme AI" still
# passes — "Acme" isn't generic — but "Chief AI Officer" doesn't).
_GENERIC_WORDS = {
    "ai", "us", "uk", "eu", "ml", "api", "llm", "ceo", "cfo", "cto", "coo", "chief",
    "officer", "director", "president", "manager", "head", "chair", "vice",
    "series", "reuters", "bloomberg", "inc", "llc", "corp", "co",
}


def is_generic_only(phrase):
    words = re.findall(r"[A-Za-z']+", phrase)
    return bool(words) and all(w.lower() in _GENERIC_WORDS for w in words)


def capitalized_phrase_candidates(text):
    """Regex fallback for when spaCy's statistical NER finds nothing —
    real, short news text on an unfamiliar or synthetic-sounding
    company name (spaCy's small English model is trained on general
    news/web text and reliably recognises well-known companies far
    better than uncommon ones) often doesn't tag it as an entity at
    all. A run of 1-4 capitalized words is a coarser, noisier signal
    than NER, so it is only ever used to *add* candidates spaCy
    missed, never to override what spaCy already found, and is still
    filtered through the same vendor blocklist and the same
    single-clean-candidate confidence rule as everything else here —
    never treated as more trustworthy than it is. No period allowed
    inside a word deliberately — an earlier version did, and a
    sentence-ending period plus the following sentence's capitalised
    first word matched as one phrase, silently bridging two unrelated
    sentences into a single garbled candidate."""
    pattern = r"\b([A-Z][a-zA-Z&']*(?:\s+[A-Z][a-zA-Z&']*){0,3})\b"
    candidates = []
    for match in re.finditer(pattern, text or ""):
        phrase = match.group(1).strip()
        first_word = phrase.split()[0]
        if first_word in _STOPWORD_START:
            continue
        if len(phrase) < 3 or is_generic_only(phrase):
            continue
        candidates.append(phrase)
    return candidates


def strip_html(text):
    """RSS summaries routinely carry raw, unstripped HTML, including an
    auto-generated "The post <a href=...>Title</a> appeared first on
    <a href=...>Blog Name</a>." footer WordPress-style feeds add to
    every single entry regardless of its actual content. Left
    unstripped, that footer's own text (e.g. a blog named "Microsoft
    Copilot Blog") can spuriously match a keyword/vendor pattern on
    every article from that feed — discovered empirically when a real
    feed's footer text alone made every entry match ai_adoption's
    "microsoft copilot" keyword. Tags are replaced with a space (not
    dropped outright) so "</p><p>" doesn't glue two words together."""
    return re.sub(r"<[^>]+>", " ", text or "")


def extract_scale_number_text(text):
    """Returns the first "<number> employees/staff/workers/users"-shaped
    phrase verbatim, or None — the same honest, never-guessed convention
    demand_engine.py's own _extract_scale_number() uses for the number
    itself; this returns the phrase, not just the digits, since
    demand_engine stores/display it as-is."""
    match = re.search(r"([\d,]{2,})\s*(employees|staff|workers|users|people)", text or "", re.IGNORECASE)
    if not match:
        return None
    return f"{match.group(1)} {match.group(2)}"
