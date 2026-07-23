# Revenue Hunter — Daily Workflow

1. Pull anything new since yesterday from `01-Opportunity-Hunter/opportunities.json`
   scored Active or Priority.
2. Pull `06-CRM/company-intelligence.json` for any existing
   relationship where `relationshipTemperature` is hot or warm and no
   open pipeline item exists yet, upsell and renewal potential that
   would otherwise get missed.
3. Pull any product or licensing idea flagged as revenue-worthy from
   `03-Product-Manager/product-backlog.json`.
4. Pull any partnership signal from `05-Market-Intelligence`.
5. For every new item, add it to `pipeline.json` and score it using
   `lead-scoring.md`.
6. Re-score anything already in the pipeline where circumstances
   changed (a deadline moved, a contact went cold, new information
   arrived).
7. Run every open item through `decision-tree.md` to confirm it's in
   the right stage and assigned the right next action.
8. Update `revenue-dashboard-template.md` for the day.
9. Hand the top 1-3 items to `04-Sales-Director` for outreach, and the
   single highest-value action to `09-CEO-Advisor`.
10. Hand the full pipeline summary to `07-Daily-Brief`.
