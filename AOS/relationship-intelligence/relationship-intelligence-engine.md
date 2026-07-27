# Relationship Intelligence Engine (AOS Sprint 13)

## Objective

Remember every relationship the founder has, the same way `06-CRM/company-intelligence.json`
already remembers every company relationship — a founder-maintained
persistent record, never an auto-scraped or invented one, that AOS then
turns into daily, deterministic intelligence: who to reconnect with,
whose birthday or work anniversary is coming up, which conference
follow-ups are due, and how healthy each relationship actually is.

This is **not** a CRM replacement and does not touch
`06-CRM/company-intelligence.json` — that file remains the
company-level relationship record 04-Sales-Director and CRM own.
Relationship Intelligence is a new, **person-level** record, additive
and downstream, that happens to cross-reference CRM and Demand
Intelligence read-only for one section (Relationship Opportunity).

## The Record — `relationship-profiles.json`

A sibling of `demand-intelligence/organisation-profiles.json` and
`recruiter-intelligence/recruiter-profiles.json`: one JSON file,
persistent across runs, keyed by person name. Unlike those two files,
nothing here is auto-collected — there is no LinkedIn, email or
calendar integration in AOS, so exactly like `company-intelligence.json`,
every field is founder-entered and this engine only ever reads it,
never invents an entry for a person AOS has no real record of.

Per person:

| Field | Meaning |
|---|---|
| `person` | Name (the key) |
| `company` | Current company |
| `role` | Title/role |
| `linkedIn` | Profile URL, or `null` |
| `email` | Email address, or `null` |
| `meetings` | `[{date, summary}]` |
| `calls` | `[{date, summary}]` |
| `messages` | `[{date, channel, summary, responded}]` — `responded` (bool) is what response rate is computed from |
| `conferenceInteractions` | `[{date, conference, summary}]` |
| `sharedInterests` | `[string]` |
| `productsDiscussed` | `[string]` |
| `resourcesShared` | `[{date, resource}]` |
| `birthday` | `"MM-DD"` or `null` — day only, no year needed for a yearly reminder |
| `workAnniversary` | `"MM-DD"` or `null` |
| `upcomingConference` | `{name, date}` or `null` — a conference this person is confirmed to attend, if known |

## What Is Computed (never stored back into the record — always derived fresh)

**Last interaction** — the most recent date across meetings, calls,
messages and conference interactions. `null` if none recorded.

**Relationship Health Score** (0-100, same weighted-and-summed pattern
every other AOS score uses):

```
health = round(
    recencyScore(0-10)     * 0.40
  + responseRateScore(0-10) * 0.30
  + channelDiversity(0-10)  * 0.30
) * 10
```

- `recencyScore`: 10 if last interaction is within `staleThresholdDays`
  (config, default 45), 6 within 2x that, 3 within 4x, 0 beyond or if
  there has never been an interaction.
- `responseRateScore`: `responded` messages ÷ total messages, scaled to
  0-10. Neutral (5) when there are no messages logged yet — silence
  isn't evidence of a bad relationship, just no signal.
- `channelDiversity`: how many of the four channel types (meetings,
  calls, messages, conference interactions) have at least one entry,
  out of 4, scaled to 0-10.

**Relationship Health Band**: `Strong` (75+), `Healthy` (50-74),
`Cooling` (25-49), `At Risk` (below 25) — except a person with zero
interactions ever recorded is `New`, never `At Risk` (no evidence of
decline, just no history yet).

**Relationship Risk**: `High` if band is `At Risk` or the relationship
is dormant (see below); `Medium` if `Cooling`; `Low` otherwise; `Not
enough data yet` for `New`.

**Relationship Opportunity** — the one section that reads outside this
engine's own record, read-only:
1. If this person's `company` has a Demand Intelligence organisation
   profile with `buyingReadinessBand` of `High` or `Very High`, flag a
   high-confidence opportunity naming that band.
2. Else if the company has a CRM record with `existingRelationship`
   beyond `none`, flag a medium-confidence opportunity.
3. Otherwise: "Not enough signal yet to flag a specific opportunity."

**Reconnect Recommendation** — true when at least one interaction has
ever been logged (this is about reconnecting, not a cold-open) and the
last interaction is `reconnectThresholdDays` (config, default 30) or
older.

**Birthday / Work Anniversary / Conference reminders** — true when the
relevant date (`birthday`/`workAnniversary`, compared by month-day
only; `upcomingConference.date`, compared as a full date) falls within
`reminderWindowDays` (config, default 14) of today. Never guessed —
absent fields never produce a reminder.

## Dashboard

**Relationship Intelligence** page: searchable by person or company; a
per-person detail view showing every tracked field, the computed
health score/band/risk/opportunity, and the full interaction timeline;
a **Follow-up Calendar** tab (every reconnect/birthday/anniversary/
conference reminder, sorted by date); and a **Network** view — a
simple, dependency-free Plotly bipartite chart (company nodes on one
side, person nodes on the other, an edge per person → their company),
not a claim of a full relationship-mapping graph tool.

## CEO Advisor

Reads `relationship-intelligence-feed.json` read-only (genuinely read,
not just an ordering dependency — same pattern as Sprint 10's Recruiter
Follow-ups) and recommends **one** relationship action per day: the
single highest-priority item across reconnect recommendations, birthday/
anniversary reminders and conference reminders due today or already
overdue, picked by nearest/most-overdue date. Honestly reports "nothing
due" when the record is empty or nothing is due.

## What This Engine Does Not Do

- Does not modify `company-intelligence.json`, `organisation-profiles.json`,
  or any other employee's output — read-only cross-references only.
- Does not auto-collect meetings, calls, messages or conference
  interactions from any external system — there is no such integration
  in AOS. Every interaction is founder-entered in
  `relationship-profiles.json`, exactly like CRM's `outreachHistory`.
- Does not invent a person, an interaction, a birthday or a conference
  AOS has no real record of. An empty `relationship-profiles.json`
  produces an honest "no relationships tracked yet" report, never a
  fabricated one.
