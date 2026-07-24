# Opportunity Sources

The 19 sources Opportunity Hunter monitors, grouped by channel. Each
source produces entries in `opportunity-schema.json` tagged with its
`source` and `sourceCategory`, so downstream filtering (by channel, by
domain) never requires re-reading raw listings.

## Marketplace

| Source | What it is | Signal produced | Cadence |
|---|---|---|---|
| Upwork | Freelance/consulting contract postings | Direct-hire and project-based opportunities, usually well-scoped and time-bound | Daily |

## Professional Network

| Source | What it is | Signal produced | Cadence |
|---|---|---|---|
| LinkedIn Jobs | Formal job/contract postings | Fractional, contract and full-time roles in AI governance, GRC, technology risk | Daily |
| LinkedIn Posts | Organic posts from target companies, recruiters and practitioners | Early signals before a formal posting exists: a company mentioning an AI governance gap, a recruiter mentioning a search | Daily |

## Recruiter Channel

| Source | What it is | Signal produced | Cadence |
|---|---|---|---|
| UAE Recruiters | Recruiting agencies and independent recruiters active in the UAE market | Fractional CISO, GRC and AI governance roles, usually warm/relationship-based | 2-3x per week |

## Consulting Channel

| Source | What it is | Signal produced | Cadence |
|---|---|---|---|
| Consulting firms | Larger advisory/consulting firms subcontracting specialist AI governance capacity | Partnership and whitelabel delivery opportunities, not direct-to-client | Weekly |

## Role-Based Searches

| Source | What it is | Signal produced | Cadence |
|---|---|---|---|
| Remote AI Governance jobs | Targeted search across job boards and LinkedIn for remote-eligible AI governance roles | Direct-hire and contract roles filtered for remote compatibility | Daily |
| Fractional CISO / GRC roles | Targeted search for fractional/part-time security and GRC leadership roles | Ongoing advisory relationships, often long-term | 2-3x per week |
| AI Governance consulting projects | Targeted search for named consulting engagements (RFPs, scoped projects) | Direct engagement opportunities, usually well-defined scope | Daily |

## Compliance Programme Searches

| Source | What it is | Signal produced | Cadence |
|---|---|---|---|
| FedRAMP | US federal cloud authorization programme | Consulting and advisory demand tied to FedRAMP authorization work | Weekly |
| GovRAMP | US state/local government cloud authorization programme (formerly StateRAMP) | Consulting and advisory demand tied to GovRAMP authorization work | Weekly |
| CMMC | US Cybersecurity Maturity Model Certification | Consulting and advisory demand tied to CMMC assessment/readiness work | Weekly |

## Technology Practice Searches

| Source | What it is | Signal produced | Cadence |
|---|---|---|---|
| Microsoft Copilot governance | Targeted search for Copilot Enterprise governance demand | Direct alignment with ADGL's named deployment types | Daily |
| ChatGPT Enterprise governance | Targeted search for ChatGPT Enterprise governance demand | Direct alignment with ADGL's named deployment types | Daily |
| AI Deployment Governance | Targeted search for the general deployment-governance problem, independent of vendor | Highest-alignment ADGL signal; often an organisation searching for exactly what ADGL solves | Daily |
| RAG implementation | Targeted search for retrieval-augmented-generation build and governance work | Direct alignment with ADGL's named deployment types | Daily |
| AI Agent governance | Targeted search for agentic AI governance demand | Direct alignment with ADGL's named deployment types, and the newest/highest-growth category | Daily |

## Risk and Assurance Keyword Searches

| Source | What it is | Signal produced | Cadence |
|---|---|---|---|
| AI Risk | Broad keyword search for AI risk assessment and management demand | GRC and technology-risk engagement signals | Daily |
| AI Compliance | Broad keyword search for AI regulatory compliance demand | GRC and regulatory-alignment engagement signals | Daily |
| AI Audit | Broad keyword search for AI audit and assurance demand | Audit-readiness and evidence-based engagement signals | Daily |
| AI Security | Broad keyword search for AI security demand | Security-governance engagement signals, often adjacent to AI Deployment Governance | Daily |

## Source-to-Domain-Tag Defaults

A starting point for `domainTags` at intake, refined during scoring
rather than treated as final:

| Source | Default `domainTags` |
|---|---|
| Microsoft Copilot governance, ChatGPT Enterprise governance, AI Deployment Governance, RAG implementation, AI Agent governance | `ADGL`, `AI Deployment Governance` |
| AI Governance consulting projects, AI Risk, AI Compliance | `AI Governance`, `GRC` |
| AI Audit | `AI Governance`, `Third-Party Risk` |
| AI Security | `Security Governance` |
| FedRAMP, GovRAMP, CMMC | `Government/FedRAMP-GovRAMP-CMMC` |
| Fractional CISO / GRC roles | `Fractional Advisory`, `Security Governance` |
| Consulting firms | `Fractional Advisory` |

## Automation Readiness

Each source above is scoped for a specific future connector type, so
wiring live data in later doesn't require re-architecting this file:

| Source type | Future connector |
|---|---|
| Upwork, LinkedIn Jobs | API or feed connector, scheduled GitHub Actions job |
| LinkedIn Posts | API/feed connector where available; manual review queue otherwise, since organic posts are harder to query reliably |
| UAE Recruiters, Consulting firms | Manual review queue (relationship-based, low volume, high judgement) |
| Remote AI Governance jobs, Fractional CISO / GRC roles, AI Governance consulting projects | Job-board API/feed connector with saved search queries |
| FedRAMP, GovRAMP, CMMC | Programme marketplace/directory feed connector |
| Microsoft Copilot governance, ChatGPT Enterprise governance, AI Deployment Governance, AI Risk, AI Compliance, AI Audit, AI Security, RAG implementation, AI Agent governance | Keyword-based search connector (job boards, LinkedIn, procurement portals) run per keyword set |

This build defines the source taxonomy, cadence and default tagging
each connector must produce against; it does not itself implement a
scraper or API client.
