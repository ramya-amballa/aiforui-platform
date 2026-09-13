"""
Opportunity Intelligence — Resume Tailoring (Phase 8 of the approved spec)

The founder's own rule, enforced here in code, not just documented:
only verified_experience may be rendered as fact in a drafted resume
or cover letter. transferable_experience and knowledge_training may
only ever appear as an honest characterization ("training in X",
"transferable experience in Y") — this module has no code path that
promotes either into an implementation claim. claims_requiring_
verification entries never appear in a draft at all.

If ramya-professional-profile.json is still empty (Day Zero — nothing
has been entered yet), every draft function here returns
GapMarker.NOT_ESTABLISHED rather than fabricating placeholder resume
content. This is deliberate: Phase 8 explicitly says not to invent a
master resume if one isn't available yet.
"""

import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
AOS_DIR = RUNTIME_DIR.parent.parent
_SCHEMA_CONTRACTS_RUNTIME = AOS_DIR / "schema-contracts" / "runtime"
if str(_SCHEMA_CONTRACTS_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_SCHEMA_CONTRACTS_RUNTIME))

from status_vocabulary import GapMarker  # noqa: E402


def analyze_resume_tailoring(inbox_entry, profile):
    """Returns {keep, emphasize, de_emphasize, add_from_verified,
    do_not_claim}, each a list of {id, claim, reason}. Every id is
    traceable back to a real ramya-professional-profile.json entry —
    nothing here is invented."""
    required_tags = {t.strip().lower() for t in inbox_entry.get("required_skills", []) + inbox_entry.get("domains", [])}

    keep, emphasize, add_from_verified = [], [], []
    for entry in profile.get("verified_experience", []):
        entry_tags = {t.strip().lower() for t in entry.get("tags", [])}
        overlap = entry_tags & required_tags
        if overlap:
            emphasize.append({"id": entry["id"], "claim": entry["claim"], "reason": f"Matches required: {', '.join(sorted(overlap))}"})
            if len(overlap) == len(required_tags) and required_tags:
                add_from_verified.append({"id": entry["id"], "claim": entry["claim"], "reason": "Directly closes a required-skill gap — make sure this is explicit, not implied"})
        else:
            keep.append({"id": entry["id"], "claim": entry["claim"], "reason": "Verified and true, not specifically relevant to this role"})

    de_emphasize = []
    for entry in profile.get("transferable_experience", []) + profile.get("knowledge_training", []):
        entry_tags = {t.strip().lower() for t in entry.get("tags", [])}
        if not (entry_tags & required_tags):
            de_emphasize.append({"id": entry["id"], "claim": entry["claim"], "reason": "Not relevant to this specific role"})

    do_not_claim = []
    for entry in profile.get("knowledge_training", []):
        entry_tags = {t.strip().lower() for t in entry.get("tags", [])}
        if entry_tags & required_tags:
            do_not_claim.append({"id": entry["id"], "claim": entry["claim"], "reason": "Training/knowledge only — do not present as implementation experience"})
    for entry in profile.get("claims_requiring_verification", []):
        do_not_claim.append({"id": entry["id"], "claim": entry["claim"], "reason": "Requires verification before it can appear in any draft at all"})

    return {
        "keep": keep,
        "emphasize": emphasize,
        "de_emphasize": de_emphasize,
        "add_from_verified": add_from_verified,
        "do_not_claim": do_not_claim,
    }


def draft_resume(inbox_entry, profile, tailoring):
    """Plain-text resume section, built only from verified_experience
    entries the tailoring analysis marked keep/emphasize. Returns
    GapMarker.NOT_ESTABLISHED if there is no verified experience to
    draft from at all — never a fabricated resume."""
    if not profile.get("verified_experience"):
        return GapMarker.NOT_ESTABLISHED.value

    lines = [f"Tailored for: {inbox_entry.get('role_or_signal', 'this role')} at {inbox_entry.get('company', 'this company')}", ""]
    lines.append("Relevant experience (emphasized):")
    for item in tailoring["emphasize"]:
        lines.append(f"- {item['claim']}")
    if tailoring["keep"]:
        lines.append("")
        lines.append("Additional verified experience:")
        for item in tailoring["keep"]:
            lines.append(f"- {item['claim']}")
    return "\n".join(lines)


def draft_cover_letter(inbox_entry, profile, tailoring):
    """Same factual-faithfulness constraint as draft_resume(). Cites
    only emphasize/add_from_verified entries as direct claims;
    de_emphasized transferable/knowledge entries, if mentioned at all,
    are phrased as framing, never fact."""
    if not tailoring["emphasize"] and not tailoring["add_from_verified"]:
        return GapMarker.NOT_ESTABLISHED.value

    company = inbox_entry.get("company", "your organisation")
    role = inbox_entry.get("role_or_signal", "this role")
    claims = "; ".join(item["claim"] for item in tailoring["emphasize"][:3])

    return (
        f"Regarding {role} at {company}: my directly relevant, verified experience includes "
        f"{claims}. [DRAFT — founder review required before any claim here is sent anywhere.]"
    )
