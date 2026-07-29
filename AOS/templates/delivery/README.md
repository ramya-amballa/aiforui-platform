# Delivery Template Library

Ten reusable, ADGL/OPERA-aligned delivery artifact templates, the same
`{{PLACEHOLDER}}` convention as `templates/proposals/`. These are the
durable intellectual property every engagement compounds: each real
engagement fills the same structure with its own facts, so the
structure itself gets better (not rewritten) over time.

`delivery-intelligence/runtime/delivery_intelligence_engine.py`
programmatically fills the placeholders it has real evidence for
(client name, date, reference, primary service, industry, regulatory
environment, decision-maker titles, governance risks, ADGL/OPERA phase
names) from Account Intelligence's brief, Service Mapping's
recommendation, and Revenue Hunter's own pipeline record — never a
second, independently-invented fact. Placeholders for things AOS has
no way to know (an actual meeting date, a named attendee, a real
workshop outcome) are deliberately left as `{{...}}` tokens for the
founder to fill in by hand during real delivery.

| Template | Aligned to | Filled automatically |
|---|---|---|
| `kickoff-agenda-template.md` | ADGL Discover | Client, scope, decision-makers (titles) |
| `discovery-questionnaire-template.md` | ADGL Discover | Governance risks already on record, drive the question list |
| `ai-readiness-assessment-workbook-template.md` | ADGL Discover/Assess | Scoring dimensions scaffold; scores left blank |
| `governance-roadmap-template.md` | ADGL five phases | Phase names, governance risks as roadmap items |
| `raci-template.md` | ADGL Govern | Role *titles* only — AOS never invents a named individual |
| `risk-register-template.md` | ADGL Assess/Govern | Pre-populated with real Account Intelligence governance risks |
| `workshop-materials-template.md` | OPERA five phases | Phase names, agenda skeleton |
| `executive-status-report-template.md` | OPERA Assurance | Client, reference; status/progress left blank per cycle |
| `steering-committee-pack-template.md` | OPERA Assurance | Combines roadmap + risk register summary |
| `project-closure-report-template.md` | ADGL Operate / OPERA Assurance | Client, scope, deliverables list |
