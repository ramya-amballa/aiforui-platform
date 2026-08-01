"""
Executive Memory Engine (AOS Sprint 20)

AOS scattered a great deal of institutional memory across the daily
noise: CEO Advisor's Top 3 Priorities are overwritten every day
(ceo-daily-report.md is a stable filename); Delivery Intelligence's
project-closure-report.md Lessons Learned sections are real founder
prose, but nothing ever reads them back across engagements; Account
Intelligence's governance risks are already drawn from a small, fixed
vocabulary (see account_intelligence_engine.py's
categoryToGovernanceRisks config) but nothing surfaces which risks
recur across multiple companies. Executive Memory is a read-only
aggregator over all three — it recognises patterns already present in
real, already-computed data, it invents no new pattern and scores
nothing.

Sources, all read-only:
- output/ceo-advisor/daily-priorities-log.json — CEO Advisor's
  own self-log of its daily Top 3/alerts (added this sprint,
  generate.py's own update_priorities_log()). Executive Memory counts
  recurrences across it; it never re-derives a priority or a score.
- output/delivery-intelligence/delivery-intelligence-feed.json
  (for kitPath) + the real project-closure-report.md file at that
  path, if one exists and its {{LESSONS_LEARNED}} placeholder has
  actually been replaced by the founder. A closure report still
  showing the raw placeholder contributes nothing — never fabricated.
- output/account-intelligence/account-intelligence-feed.json —
  governanceRisks per brief, grouped by their own already-fixed `risk`
  label (exact match — these come from a small shared vocabulary, not
  free text, so grouping is real, not approximate).
- executive-memory/decision-log.json — founder-maintained, read-only,
  the same pattern as relationship-profiles.json/touchpoint-log.json/
  delivery-log.json: a place for the founder to record a standalone
  institutional decision or rule that isn't tied to one engagement's
  closure report. This engine never writes it.
"""

import copy
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
EXECUTIVE_MEMORY_DIR = RUNTIME_DIR.parent
AOS_DIR = EXECUTIVE_MEMORY_DIR.parent
REPO_ROOT = AOS_DIR.parent

CEO_ADVISOR_PRIORITIES_LOG_PATH = AOS_DIR / "output" / "ceo-advisor" / "daily-priorities-log.json"
DELIVERY_INTELLIGENCE_FEED_PATH = AOS_DIR / "output" / "delivery-intelligence" / "delivery-intelligence-feed.json"
ACCOUNT_INTELLIGENCE_FEED_PATH = AOS_DIR / "output" / "account-intelligence" / "account-intelligence-feed.json"
DECISION_LOG_PATH = EXECUTIVE_MEMORY_DIR / "decision-log.json"

FEED_PATH = AOS_DIR / "output" / "executive-memory" / "executive-memory-feed.json"

TODAY = date.today().isoformat()

LESSONS_LEARNED_PLACEHOLDER = "{{LESSONS_LEARNED}}"
LESSONS_LEARNED_HEADING = "## Lessons Learned"
NEXT_HEADING = "## Recommended Next Steps"


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
# Recurring priorities/alerts — CEO Advisor's own history, counted, not re-scored
# --------------------------------------------------------------------------

def recurring_priorities(priorities_log, min_occurrences=2):
    """Counts how many days each organisation appeared in CEO Advisor's
    own Top 3, and how many days each alert type fired — real counts
    over real, already-persisted history, never a new priority score."""
    org_counts = defaultdict(int)
    alert_counts = defaultdict(int)
    for entry in priorities_log.get("log", []):
        seen_orgs_today = {p.get("organisation") for p in entry.get("top3", []) if p.get("organisation")}
        for org in seen_orgs_today:
            org_counts[org] += 1
        for alert_type in set(entry.get("alertTypes", [])):
            alert_counts[alert_type] += 1

    recurring_orgs = sorted(
        [{"organisation": o, "daysInTop3": c} for o, c in org_counts.items() if c >= min_occurrences],
        key=lambda r: -r["daysInTop3"],
    )
    recurring_alerts = sorted(
        [{"alertType": a, "daysFired": c} for a, c in alert_counts.items() if c >= min_occurrences],
        key=lambda r: -r["daysFired"],
    )
    return recurring_orgs, recurring_alerts, len(priorities_log.get("log", []))


# --------------------------------------------------------------------------
# Lessons Learned Library — real founder prose, extracted, never invented
# --------------------------------------------------------------------------

def extract_lessons_learned(closure_report_text):
    """None when the founder hasn't filled this engagement's Lessons
    Learned section in yet — never a fabricated substitute."""
    if LESSONS_LEARNED_PLACEHOLDER in closure_report_text:
        return None
    if LESSONS_LEARNED_HEADING not in closure_report_text:
        return None
    after_heading = closure_report_text.split(LESSONS_LEARNED_HEADING, 1)[1]
    section = after_heading.split(NEXT_HEADING, 1)[0] if NEXT_HEADING in after_heading else after_heading
    text = section.strip()
    return text or None


def build_lessons_learned_library(delivery_feed):
    library = []
    for engagement in delivery_feed.get("engagements", []):
        closure_path = engagement.get("artifacts", {}).get("project-closure-report")
        if not closure_path:
            continue
        full_path = REPO_ROOT / closure_path
        if not full_path.exists():
            continue
        lessons = extract_lessons_learned(full_path.read_text(encoding="utf-8"))
        if lessons:
            library.append({"organisation": engagement["organisation"], "lessons": lessons, "closureReportPath": closure_path})
    return library


# --------------------------------------------------------------------------
# Recurring Governance Risk Patterns — exact match, since Account
# Intelligence's own risk labels already come from a small, fixed
# vocabulary (categoryToGovernanceRisks), never free text.
# --------------------------------------------------------------------------

def recurring_governance_risks(ai_feed, min_occurrences=2):
    risk_orgs = defaultdict(list)
    for brief in ai_feed.get("briefs", []):
        for risk_entry in brief.get("governanceRisks", []):
            risk_orgs[risk_entry["risk"]].append(brief["organisation"])

    return sorted(
        [{"risk": risk, "organisations": orgs, "occurrenceCount": len(orgs)}
         for risk, orgs in risk_orgs.items() if len(orgs) >= min_occurrences],
        key=lambda r: -r["occurrenceCount"],
    )


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_executive_memory_markdown(recurring_orgs, recurring_alerts, days_tracked, lessons_library,
                                      recurring_risks, decisions):
    lines = [
        "# Executive Memory",
        "",
        f"**Generated:** {TODAY}",
        f"**Days of CEO Advisor priority history tracked:** {days_tracked}",
        "",
        "*A read-only aggregator — every pattern below is counted from real, already-computed data. "
        "Nothing here is a new score or a fabricated pattern.*",
        "",
        "---",
        "",
        "## Recurring Priorities (CEO Advisor's own history)",
        "",
    ]
    if recurring_orgs:
        lines += [f"- **{r['organisation']}** — Top 3 on {r['daysInTop3']} day(s)" for r in recurring_orgs]
    else:
        lines.append("_No organisation has recurred in Top 3 across the tracked history yet._")
    lines += ["", "## Recurring Alert Types", ""]
    if recurring_alerts:
        lines += [f"- **{r['alertType']}** — fired on {r['daysFired']} day(s)" for r in recurring_alerts]
    else:
        lines.append("_No alert type has recurred across the tracked history yet._")

    lines += ["", "---", "", "## Lessons Learned Library", ""]
    if lessons_library:
        for entry in lessons_library:
            lines += [f"### {entry['organisation']}", "", entry["lessons"], ""]
    else:
        lines.append("_No engagement has a completed Lessons Learned section yet._")

    lines += ["---", "", "## Recurring Governance Risk Patterns", ""]
    if recurring_risks:
        for r in recurring_risks:
            lines.append(f"- **{r['risk']}** — flagged for {r['occurrenceCount']} organisation(s): {', '.join(r['organisations'])}")
    else:
        lines.append("_No governance risk has recurred across two or more organisations yet._")

    lines += ["", "---", "", "## Founder-Recorded Decisions", ""]
    if decisions:
        for d in decisions:
            lines.append(f"- **{d.get('date', 'Undated')}:** {d.get('decision', '')}"
                          + (f" — {d['context']}" if d.get("context") else ""))
    else:
        lines.append("_No decisions recorded yet in decision-log.json._")

    return "\n".join(lines)
