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
    date: "2026-01-01",
    readTime: "6 min read",
    excerpt:
      "A framework tells you what questions to ask. It does not make the decision for you. Most governance failures happen after the framework has already been applied correctly.",
    body: [
      "Every governance framework eventually produces the same artefact: a matrix, a checklist, a maturity model. These are useful for structuring a conversation. They are not a substitute for the conversation itself, and treating them as one is where most governance programmes quietly fail.",
      "A risk matrix tells you that a given AI use case scores high on impact and medium on reversibility. It does not tell you whether the organisation should proceed, pause, or redesign the use case entirely. That decision requires someone with the authority and the context to make a judgment call, and to be accountable for it afterward. Frameworks distribute analysis. They do not distribute accountability, and if the operating model does not name who holds that accountability, the framework becomes a paper trail rather than a governance mechanism.",
      "This is why the OPERA methodology puts People before Evaluation. Before you build the risk model, you need to know who owns the decision it feeds. Get that sequence backwards and you end up with beautifully documented risk assessments that nobody acted on, which is a more expensive failure than having no framework at all, because it looks like governance was done.",
      "None of this is an argument against frameworks. It is an argument for treating them as decision support, not decision replacement, and for building the ownership structure first so the judgment has somewhere to land.",
    ],
    featured: true,
  },
  {
    slug: "governance-debt",
    title: "Governance Debt",
    format: "Point of View",
    category: "Risk Governance",
    domainSlugs: ["technology-risk", "enterprise-risk-governance"],
    date: "2026-01-01",
    readTime: "5 min read",
    excerpt:
      "Technical debt has a name and a budget line. Governance debt accumulates just as fast, usually with neither, until an audit or an incident forces the reckoning.",
    body: [
      "Technical debt is a familiar concept: shortcuts taken under deadline pressure, paid back later with interest in the form of rework. Governance debt behaves the same way, but it rarely gets named, budgeted, or tracked, which makes it more dangerous, not less.",
      "It accumulates in specific, recognisable forms. A committee is created to own a decision, then the people on it rotate out and no one updates the terms of reference. A control is documented as owned by a team that was reorganised eighteen months ago. A risk register lists an item as 'monitored' with no record of who last reviewed it. Individually, each of these looks minor. Collectively, they mean that when an auditor, a regulator, or an incident asks 'who owns this,' the honest answer is often nobody, even though the paperwork suggests otherwise.",
      "Governance debt is expensive to discover under pressure and comparatively cheap to address on a schedule. A governance debt diagnostic, run before an audit rather than in response to one, finds these gaps while there is still time to close them without an external forcing function.",
      "The organisations that manage this well treat governance the way they treat any other operating system: something that requires deliberate maintenance, not something that was set up once and is assumed to still be running correctly.",
    ],
    featured: true,
  },
  {
    slug: "third-party-accountability-gap",
    title: "The Third-Party Accountability Gap",
    format: "Point of View",
    category: "Third Party Governance",
    domainSlugs: ["third-party-governance", "privacy-data-governance"],
    date: "2026-01-01",
    readTime: "5 min read",
    excerpt:
      "Most third-party risk programmes are strongest at onboarding and weakest at everything after. That gap is where the actual risk lives.",
    body: [
      "Vendor onboarding tends to get disproportionate attention: a security questionnaire, a data processing agreement, a risk score. It is the most visible part of third-party governance, and often the least consequential, because a vendor's risk profile at the point of onboarding is rarely its risk profile eighteen months later.",
      "The accountability gap opens after signature. Ownership of the ongoing relationship is frequently unclear: procurement owns the contract, security owns the initial assessment, and the business unit owns the actual usage, with no single function responsible for noticing when the vendor's practice drifts from what was contracted. A subprocessor changes. A data flow expands. A control that was in place at assessment quietly lapses. None of this triggers a review unless someone is explicitly assigned to look for it.",
      "Closing this gap does not require a heavier onboarding process. It requires a monitoring cadence proportional to vendor criticality, and a named owner for each vendor relationship who is accountable for more than the initial paperwork.",
    ],
    featured: true,
  },
  {
    slug: "ai-governance-board-oversight",
    title: "What Boards Actually Need to Ask About AI",
    format: "Governance Note",
    category: "AI Governance",
    domainSlugs: ["ai-governance"],
    date: "2026-01-01",
    readTime: "4 min read",
    excerpt: "Board oversight of AI usually stops at 'do we have a policy.' The more useful question is who owns each decision the policy describes.",
    body: [
      "A board that asks whether the organisation has an AI policy will almost always get a satisfying answer, because most organisations now have one. It is a weaker question than it appears, because a policy document confirms intent, not execution.",
      "A more useful line of questioning starts with ownership: for the AI use cases currently in production, who is accountable for the risk decision on each one, and can that person be named? Boards that ask this find, more often than expected, that accountability was assumed to sit somewhere without ever being formally assigned there.",
      "The second useful question is about evidence: when was the risk assessment for a given use case last reviewed, and by whom? A risk assessment performed once, at launch, and never revisited is a snapshot, not governance. Asking for the review cadence, not just the existence of the assessment, surfaces whether oversight is a live practice or a historical artefact.",
    ],
    featured: true,
  },
  {
    slug: "third-party-risk-in-regulated-sectors",
    title: "Third-Party Risk in Regulated Sectors",
    format: "Briefing",
    category: "Third Party Governance",
    domainSlugs: ["third-party-governance"],
    date: "2026-01-01",
    readTime: "4 min read",
    excerpt: "Regulated organisations carry vendor risk differently: the obligation does not transfer with the contract.",
    body: [
      "In regulated sectors, a compliance obligation does not transfer to a vendor simply because the vendor performs the underlying activity. The regulated organisation typically remains accountable for the outcome, which means third-party governance has to be built around that reality rather than around standard commercial risk allocation.",
      "This has practical implications for assessment criteria. A vendor risk questionnaire designed for general commercial risk will miss the specific obligations that apply because of the sector, whether that is data residency, audit rights, or incident notification timelines tied to regulatory reporting deadlines. Assessment criteria need to be built from the regulatory obligation backward, not from a generic template forward.",
      "It also changes what 'monitoring' needs to mean. A vendor that was compliant at onboarding can drift out of alignment with a sector-specific obligation without any commercial breach occurring, simply because the regulatory requirement itself has evolved. Monitoring in regulated sectors has to track the obligation, not just the contract.",
    ],
    featured: false,
  },
  {
    slug: "dpdp-readiness-priorities",
    title: "DPDP Readiness: Where to Start",
    format: "Briefing",
    category: "DPDP Governance & Readiness",
    domainSlugs: ["dpdp-governance-readiness"],
    date: "2026-01-01",
    readTime: "4 min read",
    excerpt: "Most organisations approaching DPDP readiness start with policy. The more urgent starting point is the data inventory.",
    body: [
      "A consent notice or a privacy policy can be drafted in a day. It means very little if the organisation cannot answer a more basic question first: what personal data is actually being processed, for what purpose, and by which systems and vendors.",
      "This is why DPDP readiness work should begin with a data processing and consent inventory, not a policy rewrite. Without that inventory, consent mechanisms are built against an assumed data flow rather than the actual one, and gaps only surface later, usually in response to a data principal request or a regulatory inquiry that the organisation is unprepared to answer.",
      "Once the inventory exists, readiness becomes a gap assessment against specific DPDP obligations: consent, purpose limitation, data principal rights, and breach notification. That assessment, ranked by exposure rather than addressed alphabetically, is what turns readiness from a document exercise into a prioritised programme of work.",
    ],
    featured: true,
  },
  {
    slug: "technology-risk-appetite",
    title: "Risk Appetite Statements That Engineers Can Actually Use",
    format: "Governance Note",
    category: "Technology Risk",
    domainSlugs: ["technology-risk"],
    date: "2026-01-01",
    readTime: "4 min read",
    excerpt: "A risk appetite statement written for a board deck rarely survives contact with an engineering decision.",
    body: [
      "Risk appetite statements are typically written in the register of a board paper: qualitative, high-level, and calibrated for an audience making strategic decisions. That register does not translate well to an engineer deciding whether a specific system change falls within acceptable risk.",
      "A risk appetite statement becomes operationally useful when it can answer a concrete question, such as what level of unplanned downtime is acceptable for a given system tier, or what data classification requires which control before an integration can proceed. That level of specificity is what lets a risk appetite statement function as a decision rule at the point where decisions are actually made, rather than as a document referenced only during quarterly risk reporting.",
      "Getting there requires translating the board-level statement into tiered, system-specific thresholds, developed jointly with the engineering and architecture teams who will apply them. The board-level statement still exists and still matters. It simply is not the artefact that should be sitting on an engineer's desk.",
    ],
    featured: false,
  },
  {
    slug: "government-digital-governance-maturity",
    title: "Maturity in Government Digital Governance",
    format: "Field Note",
    category: "Government Digital Governance",
    domainSlugs: ["government-digital-governance"],
    date: "2026-01-01",
    readTime: "3 min read",
    excerpt: "Digital governance maturity in government looks different from the private-sector version of the same model.",
    body: [
      "Private-sector digital governance maturity models tend to measure speed of delivery and consistency of standards. Applied directly to a government or public-sector context, they miss the dimension that matters most there: whether the governance model can withstand legislative, audit, and public scrutiny at any point in the programme, not just at delivery.",
      "A more useful maturity marker for public-sector digital governance is whether decision rights are documented in a form that would make sense to an external auditor or a legislative committee with no prior context on the programme, not just to the internal team that built it. That is a different bar than the one private-sector models are typically calibrated against.",
      "Programmes that meet this bar tend to share one trait: governance was designed alongside the statutory and procurement framework from the outset, rather than layered on afterward once delivery was already underway.",
    ],
    featured: false,
  },
  {
    slug: "governance-transformation-operating-models",
    title: "Redesigning a Governance Operating Model Without Stalling the Organisation",
    format: "Governance Note",
    category: "Governance Transformation",
    domainSlugs: ["governance-transformation"],
    date: "2026-01-01",
    readTime: "5 min read",
    excerpt: "A governance transformation that tries to fix everything at once usually fixes nothing before the appetite for change runs out.",
    body: [
      "Governance transformation programmes have a common failure mode: they attempt to redesign every committee, every reporting line and every control at the same time, in the name of doing it properly. The result is usually a long, disruptive programme that loses executive sponsorship before it reaches the changes that actually mattered.",
      "A more durable approach sequences the redesign by risk exposure. Decision rights for the highest-risk categories are clarified first, even if that means leaving lower-priority structural inefficiencies in place for a later phase. This gets the organisation to a materially safer position quickly, and it demonstrates value early enough to sustain support for the phases that follow.",
      "The operating model itself should be judged on one practical test: can a new employee, six months in, find out who owns a given governance decision without asking three people first? If the answer is no, the redesign has produced a better diagram, not a better operating model.",
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
