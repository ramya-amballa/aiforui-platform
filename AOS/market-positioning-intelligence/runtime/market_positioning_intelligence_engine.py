"""
Market Positioning Intelligence Engine (AOS Sprint 21)

There is no real competitor, market-share, win/loss, or competitive-
pricing data anywhere in AOS — confirmed by a full-codebase search
before this employee was designed. Sales Director's own
`competition_level()` already says so honestly ("Not tracked — AOS has
no data source for competitor activity"). Fabricating competitor names
or market-share numbers to make this employee look more impressive
would violate the one rule every other employee in AOS already follows.

So Market Positioning Intelligence answers a narrower, fully honest
question instead: **where does AI for U&I's own service catalogue
stand relative to the real demand and regulatory signal AOS already
tracks?** Three read-only sections, each grounded in data another
employee already computed:

1. Service Demand Coverage — service-mapping's own already-computed
   `primaryService` recommendations, counted per service in
   `service-catalogue.json`'s fixed 10-service list. A service with
   zero real recommendations isn't a failure to detect — it's an
   honest flag that the catalogue offers something real demand hasn't
   yet validated.
2. Regulatory Tailwinds — market-intelligence's own
   `regulatory-log.json`, counted per source (EU AI Act, DORA, etc.),
   substantive entries only.
3. Competitive Signal — the same honest "Not tracked" Sales Director
   already states, plus the one real, non-fabricated data point AOS
   does have: a count of pipeline.json's own `stage == "lost"` entries
   (organisation and title only — never a guessed reason or a
   fabricated competitor name).
"""

import copy
import json
from collections import Counter
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
MPI_DIR = RUNTIME_DIR.parent
AOS_DIR = MPI_DIR.parent
REPO_ROOT = AOS_DIR.parent

SERVICE_CATALOGUE_PATH = AOS_DIR / "service-mapping" / "runtime" / "config" / "service-catalogue.json"
SERVICE_RECOMMENDATIONS_PATH = AOS_DIR / "service-mapping" / "service-recommendations.json"
REGULATORY_LOG_PATH = AOS_DIR / "05-Market-Intelligence" / "regulatory-log.json"
PIPELINE_PATH = AOS_DIR / "08-Revenue-Hunter" / "pipeline.json"

FEED_PATH = RUNTIME_DIR / "output" / "market-positioning-feed.json"

TODAY = date.today().isoformat()

COMPETITION_NOT_TRACKED = "Not tracked — AOS has no data source for competitor activity, market share or competitive pricing."


def load_json(path, default=None):
    if not path.exists():
        if default is not None:
            return copy.deepcopy(default)
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# --------------------------------------------------------------------------
# Service Demand Coverage
# --------------------------------------------------------------------------

def service_demand_coverage(service_catalogue, service_recommendations):
    """Every count here is a real service-mapping recommendation,
    reused verbatim — never a second, independently-derived demand
    estimate. A service with 0 recommendations is reported as
    genuinely unvalidated by real demand, not omitted."""
    primary_services = service_catalogue.get("primaryServices", [])
    counts = Counter(
        rec["primaryService"] for rec in service_recommendations.values()
        if not rec.get("notApplicable") and rec.get("primaryService") in primary_services
    )
    coverage = [{"service": s, "recommendationCount": counts.get(s, 0)} for s in primary_services]
    coverage.sort(key=lambda c: -c["recommendationCount"])
    return coverage


# --------------------------------------------------------------------------
# Regulatory Tailwinds
# --------------------------------------------------------------------------

def regulatory_tailwinds(regulatory_log):
    """Counts market-intelligence's own already-logged substantive
    developments per source — never a new regulatory signal."""
    substantive = [e for e in regulatory_log.get("log", []) if e.get("substantive")]
    counts = Counter(e["source"] for e in substantive)
    tailwinds = [{"source": s, "developmentCount": c} for s, c in counts.items()]
    tailwinds.sort(key=lambda t: -t["developmentCount"])
    return tailwinds, len(substantive)


# --------------------------------------------------------------------------
# Competitive Signal
# --------------------------------------------------------------------------

def lost_opportunities(pipeline_data):
    return [
        {"organisation": e.get("organisation"), "title": e.get("title")}
        for e in pipeline_data.get("pipeline", []) if e.get("stage") == "lost"
    ]


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_market_positioning_markdown(coverage, tailwinds, substantive_count, lost):
    lines = [
        "# Market Positioning Intelligence",
        "",
        f"**Generated:** {TODAY}",
        "",
        "*A read-only view of where AI for U&I's own service catalogue stands relative to real demand and "
        "regulatory signal AOS already tracks. There is no competitor, market-share or win/loss data source "
        "anywhere in AOS — see Competitive Signal below for that honest gap, stated plainly rather than "
        "filled in with an invented number.*",
        "",
        "---",
        "",
        "## Service Demand Coverage",
        "",
        "How many real, already-mapped opportunities recommended each of AI for U&I's 10 catalogue services:",
        "",
    ]
    for c in coverage:
        flag = "" if c["recommendationCount"] > 0 else "  — *not yet validated by any real opportunity*"
        lines.append(f"- **{c['service']}** — {c['recommendationCount']} recommendation(s){flag}")

    lines += ["", "---", "", "## Regulatory Tailwinds", "",
               f"Substantive regulatory/standards developments logged: {substantive_count}", ""]
    if tailwinds:
        lines += [f"- **{t['source']}** — {t['developmentCount']} development(s)" for t in tailwinds]
    else:
        lines.append("_No substantive regulatory development logged yet._")

    lines += ["", "---", "", "## Competitive Signal", "", f"**Status:** {COMPETITION_NOT_TRACKED}", ""]
    if lost:
        lines.append(f"**Lost opportunities on record:** {len(lost)} (organisation and title only — "
                      "no competitor name or reason is tracked anywhere in AOS)")
        lines += [f"- {o['organisation']} — {o['title']}" for o in lost]
    else:
        lines.append("**Lost opportunities on record:** 0")

    return "\n".join(lines)
