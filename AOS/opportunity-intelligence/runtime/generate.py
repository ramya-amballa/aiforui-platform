"""
Opportunity Intelligence — entry point

Manually invoked only — NOT in orchestrator-config.json, NOT part of
the daily run, per the approved design (see the model doc's own
Status line). Two modes:

  python3 generate.py
      Reads every file in config/research-inbox/, scores and drafts
      any opportunity not already in the output feed, and writes the
      feed plus a human-readable report. Never touches an existing
      record's drafts or approval state — re-running this is always
      safe (Test 8's duplicate-opportunity property).

  python3 generate.py --approve opp-xxxx connection_request --by "Ramya" [--note "..."]
      The only way anything's approval_status changes. Also
      --reject, --request-edit, --mark-executed, --cancel. Operates
      on the existing feed only; never rescoring, never re-drafting.

Nothing in this file, or anything it imports, sends a message, submits
an application, or contacts anyone. mark_executed only records that
the human already did that themselves, outside this system.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
AOS_DIR = RUNTIME_DIR.parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import approval_queue  # noqa: E402
import opportunity_model as model  # noqa: E402
import opportunity_scoring as scoring  # noqa: E402

INBOX_DIR = RUNTIME_DIR / "config" / "research-inbox"
OUTPUT_DIR = AOS_DIR / "output" / "opportunity-intelligence"
FEED_PATH = OUTPUT_DIR / "opportunity-intelligence-feed.json"


def _now():
    return datetime.now(timezone.utc).isoformat()


def load_feed():
    if FEED_PATH.exists():
        with open(FEED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"schema": "opportunity-intelligence-feed.v1", "generatedAt": None, "opportunities": []}


def save_feed(feed):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    feed["generatedAt"] = _now()
    with open(FEED_PATH, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=2)
        f.write("\n")


def load_research_inbox():
    """Every *.json file in config/research-inbox/ is one candidate
    opportunity. A malformed file is skipped with a warning, never
    crashes the whole run — matches every other AOS employee's
    advisory-not-blocking discipline."""
    entries = []
    if not INBOX_DIR.exists():
        return entries
    for path in sorted(INBOX_DIR.glob("*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                entries.append((path.name, json.load(f)))
        except json.JSONDecodeError as e:
            print(f"WARNING: skipping unreadable research-inbox file {path.name}: {e}", file=sys.stderr)
    return entries


def run_discovery():
    feed = load_feed()
    existing_by_id = {o["opportunity_id"]: o for o in feed["opportunities"]}

    profile = scoring.load_profile()
    config = scoring.load_config()
    existing_employee_feeds = scoring.load_existing_employee_feeds()

    created, skipped_invalid, skipped_duplicate = [], [], []

    for filename, entry in load_research_inbox():
        problems = model.validate_inbox_entry(entry)
        if problems:
            skipped_invalid.append((filename, problems))
            continue

        opportunity_id = model.make_opportunity_id(entry)
        if opportunity_id in existing_by_id:
            skipped_duplicate.append(opportunity_id)
            continue

        opportunity = model.build_opportunity(entry, profile, config, existing_employee_feeds)
        feed["opportunities"].append(opportunity)
        existing_by_id[opportunity_id] = opportunity
        created.append(opportunity)

    save_feed(feed)
    write_report(feed, created, skipped_invalid, skipped_duplicate)
    return feed, created, skipped_invalid, skipped_duplicate


def write_report(feed, created, skipped_invalid, skipped_duplicate):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# Opportunity Intelligence — {date_str}", ""]
    lines.append(f"**{len(created)} new opportunit{'y' if len(created) == 1 else 'ies'}** this run. "
                 f"{len(feed['opportunities'])} total in the feed.")
    lines.append("")

    pending = [o for o in feed["opportunities"]
               for draft_key, draft in o["drafts"].items()
               if draft.get("approval_status") == "PENDING_APPROVAL" and draft.get("content")]
    lines.append(f"**{len(pending)} draft(s) awaiting approval.**")
    lines.append("")

    if created:
        lines.append("## New this run")
        for o in sorted(created, key=lambda x: {"High": 0, "Medium": 1, "Low": 2}.get(x["priority"], 3)):
            lines.append(f"- **{o['opportunity_type']}** — {o['company']} — {o['role_or_signal'] or ''} "
                         f"— priority {o['priority']} — `{o['opportunity_id']}`")
        lines.append("")

    if skipped_invalid:
        lines.append("## Skipped — invalid research-inbox entries")
        for filename, problems in skipped_invalid:
            lines.append(f"- `{filename}`: {'; '.join(problems)}")
        lines.append("")

    if skipped_duplicate:
        lines.append(f"## Skipped — already processed ({len(skipped_duplicate)})")
        lines.append("")

    report_path = OUTPUT_DIR / f"{date_str}-opportunity-intelligence-report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")


_TRANSITIONS = {
    "approve": approval_queue.approve,
    "reject": approval_queue.reject,
    "request-edit": approval_queue.request_edit,
    "mark-executed": approval_queue.mark_executed,
    "cancel": approval_queue.cancel,
}


def apply_approval_action(action, opportunity_id, draft_key, actor, note):
    feed = load_feed()
    opportunity = next((o for o in feed["opportunities"] if o["opportunity_id"] == opportunity_id), None)
    if opportunity is None:
        print(f"ERROR: no opportunity with id {opportunity_id}", file=sys.stderr)
        return 1
    draft = opportunity["drafts"].get(draft_key)
    if draft is None:
        print(f"ERROR: opportunity {opportunity_id} has no draft named {draft_key!r}. "
              f"Valid: {list(opportunity['drafts'].keys())}", file=sys.stderr)
        return 1

    try:
        _TRANSITIONS[action](draft, actor, note)
    except approval_queue.InvalidTransitionError as e:
        print(f"REFUSED: {opportunity_id}/{draft_key}: {e}", file=sys.stderr)
        return 1

    opportunity["last_updated"] = _now()
    save_feed(feed)
    print(f"{opportunity_id}/{draft_key}: {action} by {actor} -> {draft['approval_status']}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action_group = parser.add_mutually_exclusive_group()
    for action in _TRANSITIONS:
        action_group.add_argument(f"--{action}", nargs=2, metavar=("OPPORTUNITY_ID", "DRAFT_KEY"))
    parser.add_argument("--by", help="Required with any approval action — the human actor's name.")
    parser.add_argument("--note", default=None)
    args = parser.parse_args()

    for action in _TRANSITIONS:
        value = getattr(args, action.replace("-", "_"))
        if value:
            if not args.by:
                parser.error(f"--{action} requires --by")
            opportunity_id, draft_key = value
            sys.exit(apply_approval_action(action, opportunity_id, draft_key, args.by, args.note))

    feed, created, skipped_invalid, skipped_duplicate = run_discovery()
    print(f"Opportunity Intelligence: {len(created)} new, {len(skipped_duplicate)} already processed, "
          f"{len(skipped_invalid)} invalid, {len(feed['opportunities'])} total.")
    print(f"Feed: {FEED_PATH}")


if __name__ == "__main__":
    main()
