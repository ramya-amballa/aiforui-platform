# KPI Dashboard — Opportunity Hunter

## Inputs

The nineteen sources in `opportunity-hunter/opportunity-sources.md`:
Upwork, LinkedIn Jobs, LinkedIn Posts, UAE Recruiters, consulting
firms, remote AI governance/fractional CISO/GRC role searches,
FedRAMP/GovRAMP/CMMC, Microsoft Copilot and ChatGPT Enterprise
governance searches, AI Deployment Governance, RAG implementation and
AI Agent governance searches, and AI Risk/Compliance/Audit/Security
keyword searches — plus consulting-opportunity flags from Market
Intelligence.

## Outputs

`opportunity-schema.json` entries, `companies.md` updates, new/updated
CRM records, `daily-opportunity-report-template.md`,
`opportunity-backlog.md`.

## Success Metrics

- Opportunities logged per week, by source
- Time from an opportunity appearing publicly to being logged and
  scored
- Classification accuracy: opportunities re-classified after the fact
  because the automatic call was wrong
- Percentage of `Priority`-band opportunities routed downstream the
  same day
- Zero missed `Priority`-would-have-scored opportunities, checked
  retrospectively against source archives

## Weekly Targets

| Metric | Target |
|---|---|
| Opportunities logged | 15+ (across all nineteen sources) |
| Priority or Active scored | 4+ |
| Time-to-log (publication to logged) | Under 24 hours |
| Priority-band items routed downstream same day | 100% |

## Monthly Targets

| Metric | Target |
|---|---|
| Opportunities logged | 60+ |
| Classification accuracy | 90%+ (no more than 1 in 10 re-classified) |
| Immediate Proposal → conversation conversion | 20%+ |
| Convert into Content / Convert into Product Idea handed off | 100% within 48 hours |

## Business Impact

This is the top of the funnel, and the first employee whose output
reaches five other employees directly (Revenue Hunter, CRM, Sales
Director, Product Manager, Content Director) rather than one or two.
If this number is low or misrouted, every one of those five is working
with a smaller or wrong set of choices, not because of a lack of
effort further down the chain but because the funnel itself is thin
or misclassifying.
