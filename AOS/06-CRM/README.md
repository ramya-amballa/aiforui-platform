# CRM

AI employee #6. Maintains the single record of contacts, companies and
relationship status across the pipeline, so no other AI employee, or
the founder, ever starts from scratch on a company already
encountered.

## Files

- `company-intelligence.json` — the company knowledge base: one entry
  per organisation, enriched every time it's touched again

## Who Writes to This

Any AI employee that encounters a company (most often
`opportunity-hunter`, but also `04-Sales-Director` and
`05-Market-Intelligence`) adds or updates its entry here rather than
keeping its own separate copy. `opportunity-hunter/companies.md`
stays a lightweight log that links back to the full record here.

`04-Sales-Director` owns `relationshipTemperature`, `nextFollowUpDue`
and `outreachHistory` specifically: it is the only employee that
updates these fields, since keeping a warm relationship warm is its
job.
