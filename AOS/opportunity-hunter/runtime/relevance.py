"""
Opportunity Relevance Engine v1 — see ../opportunity-relevance-engine.md
for the full model and worked examples. Imported by ingest.py and run
on every inbox record before opportunity-scoring-engine.md's scoring,
so a keyword match that turns out to be a substring false positive
(the "RAG" in "storage" problem the first live collection run
surfaced) never reaches Revenue Hunter.

Matching here is deliberately whole-word (\\bterm\\b), not substring —
the opposite of collectors/common.py's match_keywords, which stays a
simple substring match because it only decides whether to collect a
posting at all, not whether to trust it.
"""

import re

RELEVANCE_THRESHOLD = 50

# category_key -> (points, terms). Order matches the table in
# opportunity-relevance-engine.md.
TERM_CATEGORIES = {
    "aiGovernance": (15, ["ai governance", "ai oversight"]),
    "aiRisk": (12, ["ai risk", "model risk", "algorithmic risk"]),
    "responsibleAi": (10, ["responsible ai", "ethical ai", "trustworthy ai"]),
    "governanceContext": (10, ["governance", "oversight", "accountability", "raci"]),
    "complianceContext": (10, ["compliance", "regulatory", "audit", "risk management"]),
    "roleResponsibilities": (10, [
        "governance framework", "policy development", "control design", "risk appetite",
        "model validation", "use case review", "third-party risk", "vendor risk", "assurance",
    ]),
    "cybersecurityContext": (8, ["cybersecurity", "cyber security", "information security", "security operations"]),
    "deploymentContext": (8, ["ai deployment", "model deployment", "mlops", "production rollout", "deployment governance"]),
    "consultingContext": (8, ["advisory", "consulting", "consultant", "client engagement"]),
    "microsoftCopilot": (8, ["microsoft copilot", "copilot studio"]),
    "requiredSkills": (8, ["nist ai rmf", "iso 42001", "gdpr", "dora", "eu ai act", "grc"]),
    "llm": (6, ["llm", "large language model", "foundation model", "gpt"]),
    "rag": (6, ["rag", "retrieval augmented generation", "rag pipeline"]),
    "aiContext": (6, ["artificial intelligence", "machine learning", "generative ai"]),
    "companyIndustry": (5, ["financial services", "government", "critical infrastructure", "enterprise saas"]),
}

# Every category counts toward "is this actually about AI" except
# companyIndustry, which is only ever corroborating, never sufficient.
STRONG_AI_CATEGORIES = {k for k in TERM_CATEGORIES if k != "companyIndustry"}

# The three categories a single common word can trigger by accident.
WEAK_CATEGORIES = {"aiContext", "llm", "rag"}

# family_key -> (penalty, display name, terms)
ROLE_FAMILY_PENALTIES = {
    "legal": (40, "Legal", ["paralegal", "attorney", "legal counsel", "lawyer", "legal assistant", "litigation", "law clerk"]),
    "healthcare": (40, "Healthcare", ["nurse", "nursing", "clinical", "patient care", "physician", "medical assistant", "caregiver", "therapist", "pharmacy", "dental", "veterinary"]),
    "hr": (40, "HR", ["human resources", "hr business partner", "recruiter", "talent acquisition", "people operations", "people ops"]),
    "administrative": (35, "Administrative", ["data entry", "file clerk", "administrative assistant", "office administrator", "receptionist"]),
    "genericAnalyst": (25, "Generic analyst", ["business analyst", "data analyst", "financial analyst"]),
}


def _matches(text, term):
    return re.search(r"\b" + re.escape(term) + r"\b", text) is not None


def _category_hits(text):
    hits = {}
    for category, (points, terms) in TERM_CATEGORIES.items():
        if any(_matches(text, term) for term in terms):
            hits[category] = points
    return hits


def _role_family_hits(text):
    return [key for key, (_, _, terms) in ROLE_FAMILY_PENALTIES.items() if any(_matches(text, term) for term in terms)]


def compute_relevance(record):
    """Returns {"score", "categoriesMatched", "penalties", "reason"}.
    `reason` is populated only when the score falls below
    RELEVANCE_THRESHOLD — the text explaining why, for rejected-log.json."""
    # domainTags is deliberately excluded: it's set by the Collection
    # Engine's own domain_tags_for() heuristic, derived from the very
    # upstream keyword match this engine exists to double-check —
    # including it here would let a false-positive keyword match
    # validate itself through its own downstream tag.
    text = " ".join([
        str(record.get("title", "")),
        str(record.get("description", "")),
    ]).lower()

    category_hits = _category_hits(text)
    strong_hit_count = sum(1 for c in category_hits if c in STRONG_AI_CATEGORIES)
    score = sum(category_hits.values())

    penalties = []
    for family in _role_family_hits(text):
        base_penalty, display_name, _ = ROLE_FAMILY_PENALTIES[family]
        if strong_hit_count == 0:
            penalty = base_penalty
        elif strong_hit_count == 1:
            penalty = round(base_penalty / 2)
        else:
            continue  # two or more real AI-related categories: no penalty
        score -= penalty
        penalties.append(f"{display_name} role penalty (-{penalty})")

    if strong_hit_count == 1 and set(category_hits) & WEAK_CATEGORIES:
        score -= 15
        penalties.append("Isolated weak-keyword penalty (-15)")

    score = max(0, min(100, round(score)))

    reason = None
    if score < RELEVANCE_THRESHOLD:
        if not category_hits:
            matched_keywords = record.get("matchedKeywords") or []
            upstream = f" (upstream keyword match: {', '.join(matched_keywords)})" if matched_keywords else ""
            reason = (
                "No relevance signals matched in posting text" + upstream +
                " — likely a substring false positive upstream, not a real opportunity."
            )
        else:
            matched_list = ", ".join(sorted(category_hits))
            penalty_list = "; ".join(penalties) if penalties else "no penalties"
            reason = f"Weak/insufficient relevance signal (matched: {matched_list}; {penalty_list})."

    return {
        "score": score,
        "categoriesMatched": sorted(category_hits.keys()),
        "penalties": penalties,
        "reason": reason,
    }
