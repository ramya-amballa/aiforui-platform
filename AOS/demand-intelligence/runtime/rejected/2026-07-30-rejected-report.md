# Opportunity Relevance Engine — Daily Rejections

**Date:** 2026-07-30
**Rejected today:** 7

| Title | Organisation | Relevance | Reason |
|---|---|---|---|
| Hospice | Hometown Deli &amp; Grocery | 0 | Weak/insufficient relevance signal (matched: companyIndustry; Healthcare role penalty (-40)). |
| Acoustical Management | Hometown Deli &amp; Grocery | 0 | Weak/insufficient relevance signal (matched: companyIndustry; Healthcare role penalty (-40)). |
| Video Editor Reacts | MrBeast | 0 | No relevance signals matched in posting text (upstream keyword match: RAG) — likely a substring false positive upstream, not a real opportunity. |
| Area Sales Manager | ROAR Organic | 10 | Weak/insufficient relevance signal (matched: governanceContext; no penalties). |
| Sales &amp; Marketing Director | Hustler Marketing | 20 | Weak/insufficient relevance signal (matched: complianceContext, governanceContext; no penalties). |
| LLM Engineer Freelancer | Monterail | 12 | Weak/insufficient relevance signal (matched: llm, rag; no penalties). |
| AI Intern | CertifyOS | 26 | Weak/insufficient relevance signal (matched: aiContext, complianceContext, governanceContext; no penalties). |

---

*Rejected before scoring — see opportunity-relevance-engine.md for the model.
Nothing here was written to opportunity-schema.json, pipeline.json or
company-intelligence.json. Full history: rejected/rejected-log.json.*
