import type { Insight } from "@/types";

/**
 * Insights: the perspective library. `format` distinguishes original
 * Point of View pieces (frameworks, decision models, governance
 * perspectives, the site's signature content) from shorter Governance
 * Notes, Briefings and Field Notes, without splitting them into
 * separate collections or routes. The homepage's Point of View section
 * is simply insights.filter(i => i.format === "Point of View").
 */
export const insights: Insight[] = [
  {
    slug: "judgment-over-frameworks",
    title: "Judgment Over Frameworks",
    format: "Point of View",
    category: "Governance Philosophy",
    domainSlugs: ["ai-governance", "governance-transformation"],
    readTime: "6 min read",
    excerpt:
      "A framework tells you what questions to ask. It does not make the decision for you. Most governance failures happen after the framework has already been applied correctly.",
    body: [
      "Every governance framework produces the same artefact: a matrix, a checklist, a maturity model. These structure a conversation. They are not a substitute for it, and treating them as one is where most governance programmes quietly fail.",
      "A risk matrix tells you a use case scores high on impact and medium on reversibility. It does not tell you whether to proceed, pause, or redesign it. That call requires someone with authority and context, accountable for it afterward. Frameworks distribute analysis, not accountability; without a named owner, the framework becomes a paper trail, not a governance mechanism.",
      "This is why OPERA puts People before Evaluation: before building the risk model, you need to know who owns the decision it feeds. Get that sequence backwards and you end up with well-documented risk assessments nobody acted on, a more expensive failure than having no framework at all, because it looks like governance was done.",
      "None of this argues against frameworks. It argues for treating them as decision support, not decision replacement, and building the ownership structure first so judgment has somewhere to land.",
    ],
    featured: true,
  },
  {
    slug: "governance-debt",
    title: "Governance Debt",
    format: "Point of View",
    category: "Risk Governance",
    domainSlugs: ["technology-risk", "enterprise-risk-governance"],
    readTime: "5 min read",
    excerpt:
      "Technical debt has a name and a budget line. Governance debt accumulates just as fast, usually with neither, until an audit or an incident forces the reckoning.",
    body: [
      "Technical debt is shortcuts taken under deadline pressure, repaid later with interest. Governance debt behaves the same way, but rarely gets named, budgeted, or tracked, which makes it more dangerous, not less.",
      "It accumulates in recognisable forms: a committee whose terms of reference were never updated after its members rotated out, a control still documented as owned by a team that was reorganised, a risk register item marked 'monitored' with no record of a last review. Individually minor. Collectively, when an auditor asks 'who owns this,' the honest answer is often nobody.",
      "It is expensive to discover under pressure and comparatively cheap to address on a schedule. A governance debt diagnostic, run before an audit rather than in response to one, finds these gaps while there is still time to close them.",
      "Organisations that manage this well treat governance as an operating system requiring deliberate maintenance, not something set up once and assumed to still be running.",
    ],
    featured: true,
  },
  {
    slug: "third-party-accountability-gap",
    title: "The Third-Party Accountability Gap",
    format: "Point of View",
    category: "Third Party Governance",
    domainSlugs: ["third-party-governance", "privacy-data-governance"],
    readTime: "5 min read",
    excerpt:
      "Most third-party risk programmes are strongest at onboarding and weakest at everything after. That gap is where the actual risk lives.",
    body: [
      "Vendor onboarding gets disproportionate attention: a security questionnaire, a data processing agreement, a risk score. It is the most visible part of third-party governance, and often the least consequential, since a vendor's risk profile at onboarding is rarely its risk profile eighteen months later.",
      "The gap opens after signature. Ownership of the ongoing relationship is often unclear: procurement owns the contract, security owns the initial assessment, the business unit owns actual usage, and no one owns noticing drift. A subprocessor changes, a data flow expands, a control quietly lapses; none of it triggers review unless someone is assigned to look for it.",
      "Closing the gap does not require a heavier onboarding process. It requires monitoring proportional to vendor criticality, and a named owner accountable for more than the initial paperwork.",
    ],
    featured: true,
  },
  {
    slug: "ai-governance-board-oversight",
    title: "What Boards Actually Need to Ask About AI",
    format: "Governance Note",
    category: "AI Governance",
    domainSlugs: ["ai-governance"],
    readTime: "4 min read",
    excerpt: "Board oversight of AI usually stops at 'do we have a policy.' The more useful question is who owns each decision the policy describes.",
    body: [
      "A board that asks whether the organisation has an AI policy will almost always get a satisfying answer, since most now have one. It is a weaker question than it appears: a policy document confirms intent, not execution.",
      "A more useful question starts with ownership: for AI use cases in production, who is accountable for the risk decision on each, and can that person be named? Boards that ask this often find accountability was assumed to sit somewhere without ever being formally assigned.",
      "The second question is about evidence: when was the risk assessment last reviewed, and by whom? One performed once, at launch, and never revisited is a snapshot, not governance. Asking for the review cadence, beyond the assessment's existence, surfaces whether oversight is live or historical.",
    ],
    featured: true,
  },
  {
    slug: "third-party-risk-in-regulated-sectors",
    title: "Third-Party Risk in Regulated Sectors",
    format: "Briefing",
    category: "Third Party Governance",
    domainSlugs: ["third-party-governance"],
    readTime: "4 min read",
    excerpt: "Regulated organisations carry vendor risk differently: the obligation does not transfer with the contract.",
    body: [
      "In regulated sectors, a compliance obligation does not transfer to a vendor simply because the vendor performs the activity. The regulated organisation typically remains accountable for the outcome, so third-party governance has to be built around that, not standard commercial risk allocation.",
      "A vendor questionnaire built for general commercial risk will miss sector-specific obligations, data residency, audit rights, incident notification timelines. Assessment criteria need to be built from the regulatory obligation backward, not a generic template forward.",
      "It also changes what monitoring needs to mean. A vendor compliant at onboarding can drift out of alignment as the regulatory requirement itself evolves, with no commercial breach involved. Monitoring in regulated sectors has to track the obligation itself, beyond the contract.",
    ],
    featured: false,
  },
  {
    slug: "dpdp-readiness-priorities",
    title: "DPDP Readiness: Where to Start",
    format: "Briefing",
    category: "DPDP Governance & Readiness",
    domainSlugs: ["dpdp-governance-readiness"],
    readTime: "4 min read",
    excerpt: "Most organisations approaching DPDP readiness start with policy. The more urgent starting point is the data inventory.",
    body: [
      "A consent notice or privacy policy can be drafted in a day. It means little if the organisation cannot first answer what personal data is actually processed, for what purpose, and by which systems and vendors.",
      "This is why DPDP readiness should begin with a data processing and consent inventory, not a policy rewrite. Without it, consent mechanisms are built against an assumed data flow, and gaps surface later, usually via a data principal request the organisation is unprepared to answer.",
      "Once the inventory exists, readiness becomes a gap assessment against specific obligations: consent, purpose limitation, data principal rights, breach notification, ranked by exposure rather than addressed alphabetically.",
    ],
    featured: true,
  },
  {
    slug: "technology-risk-appetite",
    title: "Risk Appetite Statements That Engineers Can Actually Use",
    format: "Governance Note",
    category: "Technology Risk",
    domainSlugs: ["technology-risk"],
    readTime: "4 min read",
    excerpt: "A risk appetite statement written for a board deck rarely survives contact with an engineering decision.",
    body: [
      "Risk appetite statements are typically written in the register of a board paper: qualitative, high-level, calibrated for strategic decisions. That register does not translate to an engineer deciding whether a specific change falls within acceptable risk.",
      "A statement becomes operationally useful when it answers a concrete question: what downtime is acceptable for a given system tier, what data classification requires which control before an integration proceeds. That specificity lets it function as a decision rule where decisions are actually made, not just in quarterly risk reporting.",
      "Getting there means translating the board-level statement into tiered, system-specific thresholds, built jointly with engineering. The board-level statement still matters; it simply is not the artefact that belongs on an engineer's desk.",
    ],
    featured: false,
  },
  {
    slug: "government-digital-governance-maturity",
    title: "Maturity in Government Digital Governance",
    format: "Field Note",
    category: "Government Digital Governance",
    domainSlugs: ["government-digital-governance"],
    readTime: "3 min read",
    excerpt: "Digital governance maturity in government looks different from the private-sector version of the same model.",
    body: [
      "Private-sector maturity models measure speed of delivery and consistency of standards. Applied directly to government, they miss what matters most there: whether the governance model withstands legislative, audit and public scrutiny at any point, not just at delivery.",
      "A more useful marker is whether decision rights are documented in a form that makes sense to an external auditor or legislative committee with no prior context, not just to the team that built it. That is a higher bar than most private-sector models are calibrated against.",
      "Programmes that meet it share one trait: governance was designed alongside the statutory and procurement framework from the outset, not layered on after delivery was already underway.",
    ],
    featured: false,
  },
  {
    slug: "governance-transformation-operating-models",
    title: "Redesigning a Governance Operating Model Without Stalling the Organisation",
    format: "Governance Note",
    category: "Governance Transformation",
    domainSlugs: ["governance-transformation"],
    readTime: "5 min read",
    excerpt: "A governance transformation that tries to fix everything at once usually fixes nothing before the appetite for change runs out.",
    body: [
      "Governance transformation has a common failure mode: redesigning every committee, reporting line and control at once, in the name of doing it properly. The result is usually a long, disruptive programme that loses executive sponsorship before reaching the changes that actually mattered.",
      "A more durable approach sequences by risk exposure. Decision rights for the highest-risk categories are clarified first, even if lower-priority inefficiencies wait for a later phase. This reaches a materially safer position quickly, and demonstrates value early enough to sustain support for what follows.",
      "Judge the operating model on one test: can a new employee, six months in, find who owns a given decision without asking three people first? If not, the redesign produced a better diagram, not a better operating model.",
    ],
    featured: true,
  },
];

export function getInsightBySlug(slug: string) {
  return insights.find((insight) => insight.slug === slug);
}

export function getPointOfViewInsights() {
  return insights.filter((insight) => insight.format === "Point of View");
}
