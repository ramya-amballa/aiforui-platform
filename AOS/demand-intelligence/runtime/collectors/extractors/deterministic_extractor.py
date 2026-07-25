"""
Deterministic, fully offline extraction backend — the default. No paid
API, no network call beyond the RSS fetch collectors/demand_signals.py
already makes. Confirms whether an article names a real organisation
and extracts it using:

  1. A headline-pattern check for the common vendor-blog convention
     "Vendor: Customer did X" (base.split_vendor_headline).
  2. spaCy Named Entity Recognition (ORG entities) over the article's
     own title+summary — the one place this backend uses a pre-trained
     model rather than a hand-written rule, exactly as asked
     ("Named Entity Recognition (spaCy)"). Candidates matching
     base.VENDOR_BLOCKLIST (the AI vendor the feed is published by, or
     the tool named) are discarded — never mistaken for the
     organisation *adopting* something — and base.is_generic_only()
     discards non-company entities spaCy sometimes still tags as ORG
     (a bare "AI", "US", a role title). If nothing clean survives
     (a real, common gap for less-well-known company names on the
     small English model), base.capitalized_phrase_candidates()'s
     coarser regex heuristic is used as a fallback, never to override
     a real NER match.
  3. Deterministic confidence: "high" only when exactly one clean
     candidate organisation survives filtering, "medium" for two,
     "low" (rejected — never turned into a lead) for three or more —
     real short news text rarely names more than one or two
     organisations cleanly, so ambiguity itself is the signal that
     this extraction isn't trustworthy, never overridden into "high"
     just because *something* was found. demand_signals.py only turns
     "high" confidence into a lead, same threshold the Claude backend
     always used.

Requires the `spacy` package and an English model (default
en_core_web_sm) — see requirements.txt and README.md for installation.
If either is missing, extract() returns None and the caller treats
this exactly like any other missing-dependency connector: a clean
skip, never a crash, never a fabricated result.
"""

from . import base

_NLP_CACHE = {}


def _load_model(model_name):
    if model_name in _NLP_CACHE:
        return _NLP_CACHE[model_name]
    try:
        import spacy
        nlp = spacy.load(model_name)
    except (ImportError, OSError):
        nlp = None
    _NLP_CACHE[model_name] = nlp
    return nlp


def model_available(model_name="en_core_web_sm"):
    return _load_model(model_name) is not None


def _dedupe_preserving_order(items):
    seen = set()
    result = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _vendor_mentioned(text):
    lowered = (text or "").lower()
    for vendor in base.VENDOR_BLOCKLIST:
        if vendor in lowered:
            return vendor
    return None


def extract(title, summary, model=None):
    """Same return shape as claude_extractor.extract() / the original
    Claude-based extraction — isDemandSignal, organisation,
    eventSummary, aiTool, scale, industry, confidence — so
    collectors/demand_signals.py doesn't need to know which backend
    produced it. Returns None only if spaCy/the model isn't installed
    (a missing-dependency skip, not "no signal found")."""
    model_name = model or "en_core_web_sm"
    nlp = _load_model(model_name)
    if nlp is None:
        return None

    title = title or ""
    summary = summary or ""
    full_text = f"{title}. {summary}".strip()

    vendor_label, remainder = base.split_vendor_headline(title)

    doc = nlp(full_text)
    ner_candidates = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]
    clean_ner_candidates = _dedupe_preserving_order([
        c for c in ner_candidates if not base.is_vendor_name(c) and not base.is_generic_only(c)
    ])

    if clean_ner_candidates:
        # spaCy found something — trust it alone; adding the noisier
        # regex fallback here would only dilute a real NER match with
        # false positives, never improve it.
        clean_candidates = clean_ner_candidates
    else:
        # spaCy found nothing at all (a real, common failure mode for
        # less-well-known company names on the small English model) —
        # fall back to the coarser capitalized-phrase heuristic rather
        # than reject the article outright.
        regex_candidates = base.capitalized_phrase_candidates(full_text)
        clean_candidates = _dedupe_preserving_order([c for c in regex_candidates if not base.is_vendor_name(c)])

    if not clean_candidates:
        return {
            "isDemandSignal": False, "organisation": "", "eventSummary": "",
            "aiTool": "", "scale": "", "industry": "", "confidence": "low",
        }

    organisation = clean_candidates[0]
    scale = base.extract_scale_number_text(full_text) or ""
    industry = base.infer_industry(full_text)
    ai_tool = _vendor_mentioned(full_text) or ""

    if len(clean_candidates) == 1:
        confidence = "high"
    elif len(clean_candidates) == 2:
        confidence = "medium"
    else:
        confidence = "low"

    event_summary = summary.strip() or title.strip()

    return {
        "isDemandSignal": True,
        "organisation": organisation,
        "eventSummary": event_summary,
        "aiTool": ai_tool,
        "scale": scale,
        "industry": industry,
        "confidence": confidence,
    }
