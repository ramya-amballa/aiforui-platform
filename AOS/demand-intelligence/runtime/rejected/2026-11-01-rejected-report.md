# Opportunity Relevance Engine — Daily Rejections

**Date:** 2026-11-01
**Rejected today:** 3

| Title | Organisation | Relevance | Reason |
|---|---|---|---|
| Scientific Account Executive | Adaptyv | 10 | Weak/insufficient relevance signal (matched: governanceContext; no penalties). |
| Contract Recruiter | CAI | 0 | Weak/insufficient relevance signal (matched: companyIndustry; HR role penalty (-40)). |
| AWS Cloud Solutions Architect | Cloudary SAS | 0 | No relevance signals matched in posting text (upstream keyword match: RAG) — likely a substring false positive upstream, not a real opportunity. |

---

*Rejected before scoring — see opportunity-relevance-engine.md for the model.
Nothing here was written to opportunity-schema.json, pipeline.json or
company-intelligence.json. Full history: rejected/rejected-log.json.*
