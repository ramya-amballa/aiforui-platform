# AIforU&I — Advisory Platform (Phase 2: Living-Platform Architecture)

Independent advisory platform for Ramya Amballa. This is the **architecture and
component system**, not final content. Every page renders with clearly
labelled `[Placeholder]` copy pending content authoring.

Positioning: independent executive advisor — not a consulting firm, not an
agency. The visual language (serif display type, restrained ink/paper
palette, generous whitespace, no stock photography) is built to read as the
digital home of a senior independent practitioner whose reputation compounds
over years, not a campaign site.

Phase 2 rebuilt the information architecture around one constraint: **the
site must get more valuable with every engagement, framework and article
published — not depend on a backlog of finished projects to look
substantial.** See `src/content/README.md` for the content extension
contract this enables.

---

## Stack

- **Next.js 15** (App Router) + **React 19** + **TypeScript** (strict)
- **Tailwind CSS** — design tokens sourced from CSS custom properties
- No UI/animation/icon libraries — deliberately minimal dependency surface
- Static generation for all detail pages (`generateStaticParams`); listing
  pages with filters/pagination are server-rendered on demand

## Getting Started

```bash
npm install
npm run dev        # http://localhost:3000
npm run build       # production build
npm run typecheck   # tsc --noEmit
npm run lint         # eslint
```

---

## 1. Folder Structure

```
aiforu-platform/
├── src/
│   ├── app/
│   │   ├── layout.tsx                     # Root layout: fonts, ThemeProvider, SiteShell
│   │   ├── page.tsx                       # Home — see §3 for section order
│   │   ├── globals.css
│   │   ├── sitemap.ts / robots.ts
│   │   ├── not-found.tsx
│   │   ├── selected-advisory-engagements/
│   │   │   ├── page.tsx                   # Listing — track filter + pagination
│   │   │   └── [slug]/page.tsx            # Reusable engagement template
│   │   ├── governance-domains/
│   │   │   ├── page.tsx                   # Full capability map, grouped by cluster
│   │   │   └── [slug]/page.tsx            # Reusable domain template (all 13 domains)
│   │   ├── insights/
│   │   │   ├── page.tsx                   # Listing — format filter + pagination
│   │   │   └── [slug]/page.tsx
│   │   ├── resources/
│   │   │   ├── page.tsx                   # Listing — type + tier filters + pagination
│   │   │   └── [slug]/page.tsx
│   │   ├── about/page.tsx                 # Executive biography, not a résumé
│   │   └── contact/page.tsx
│   │
│   ├── components/
│   │   ├── ui/                            # Button, Card, Badge, Container, SectionHeading,
│   │   │                                    Eyebrow, Divider, Placeholder, BackLink,
│   │   │                                    FilterPills, Pagination
│   │   ├── layout/                        # Header, Footer, SiteShell, Breadcrumbs
│   │   ├── theme/                         # ThemeProvider, ThemeToggle (no dependency)
│   │   ├── sections/                      # PageHero, CtaBand, PointOfViewSection,
│   │   │                                    CurrentPrioritiesSection
│   │   ├── advisory/                      # Engagement card/grid/detail
│   │   ├── governance/                    # Domain card/grid/detail + GovernanceCapabilityMap
│   │   ├── article/                       # Insight card/grid/detail
│   │   ├── resource/                      # Resource card/grid/detail
│   │   ├── contact/contact-form.tsx
│   │   └── seo/                           # JsonLd, schema.ts
│   │
│   ├── content/                           # Data layer — see content/README.md
│   │   ├── README.md                      # Extension contract: how to add content
│   │   ├── governance-clusters.ts         # 4 clusters
│   │   ├── governance-domains.ts          # 13 domains
│   │   ├── advisory-engagements.ts        # 8 engagements (Government / Enterprise / Strategic)
│   │   ├── insights.ts                    # 9 insights (incl. 3 signature Point of View pieces)
│   │   ├── resources.ts                   # 10 resources (Free + Premium)
│   │   └── current-priorities.ts          # Dated "now page" snapshot
│   │
│   ├── lib/
│   │   ├── constants.ts                   # site config, 6-item primary nav, CTAs
│   │   ├── metadata.ts                    # buildMetadata()
│   │   ├── pagination.ts                  # paginate(), parsePage(), parseFilter()
│   │   ├── query.ts                       # buildQueryString() — searchParams-driven filter links
│   │   └── utils.ts
│   │
│   └── types/index.ts
│
├── public/
├── tailwind.config.ts
└── next.config.ts
```

---

## 2. What changed in Phase 2

Following the positioning review, three structural shifts:

**Governance Domains grew from 9 to 13, grouped into 4 clusters, all live as
full pages from day one** (`Emerging Technology Governance`,
`Risk, Cyber & Assurance`, `Regulatory, Privacy & Third-Party`,
`Public Sector & Transformation`). `GovernanceCapabilityMap` renders this
same taxonomy two ways — a compact text index on the homepage, a full
cluster-grouped card grid on `/governance-domains` — so the map reads as a
structured index rather than a wall of tiles.

**Point of View is now a first-class content format, not a homepage
one-liner.** `Insight.format` distinguishes `"Point of View"` (original
frameworks, decision models) from `"Governance Note"`, `"Briefing"` and
`"Field Note"` within one collection. `PointOfViewSection` — deliberately
not built from the standard Card primitive — is the homepage's signature
section, and `/insights` filters by format.

**Every content type now supports several-hundred-item scale without a
redesign.** `lib/pagination.ts` and `lib/query.ts` back a searchParams-driven
filter + pagination pattern (`FilterPills`, `Pagination` — both plain
server-rendered links, no client JS) used identically across
`/selected-advisory-engagements`, `/insights` and `/resources`. Growing a
collection is a data-only change; see `src/content/README.md`.

Other changes: the flat homepage keyword strip is gone; the hero now carries
one primary CTA plus a quiet secondary link instead of two stacked buttons;
the closing CTA band appears only on hub/listing pages, replaced by a quiet
`BackLink` on every detail page (an insight, engagement, domain or resource
page is meant to be read and left, not funneled); the standalone "Advisory
Services" page is retired and folded into About as "How I Work"; About is
restructured around *why/how/experience*, not a chronology.

---

## 3. Homepage section order

1. Hero (single primary CTA + secondary text link)
2. Current Advisory Priorities (dated "now page" snapshot)
3. Point of View (signature section)
4. Why organisations engage her (About teaser)
5. Governance Domains (capability map, compact)
6. Selected Advisory Engagements (featured)
7. Insights (featured, excluding Point of View to avoid duplicating §3)
8. Closing CTA band

---

## 4. Components created (Phase 2 additions)

| Component | Purpose |
|---|---|
| `PointOfViewSection` | Signature homepage section — numbered list over hairline rules, not cards |
| `CurrentPrioritiesSection` | "Now page" style block; self-dates via `updatedAt` |
| `GovernanceCapabilityMap` | Cluster-grouped domain taxonomy — `compact` and `full` variants |
| `FilterPills` | Server-rendered filter links (track / format / type / tier) |
| `Pagination` | Server-rendered pager, `?page=` param |
| `BackLink` | Quiet end-of-detail-page wayfinding, replaces `CtaBand` on `[slug]` pages |

## 5. Pages

`/`, `/selected-advisory-engagements` (+ 8 engagements), `/governance-domains`
(+ 13 domains across 4 clusters), `/insights` (+ 9 insights, 3 of them Point
of View), `/resources` (+ 10 resources across 8 types and 2 access tiers),
`/about`, `/contact`, `/sitemap.xml`, `/robots.txt`, `not-found`.

Verified: `npm run typecheck`, `npm run build` (52 pages, zero
errors/warnings — detail pages statically generated, filtered listing pages
server-rendered on demand) and a manual light/dark browser pass across the
homepage, capability map, filtered Insights view and About.

## 6. Remaining work

- Replace all `[Placeholder]` copy with real content — positioning,
  biography, engagement narratives, Point of View pieces, resource
  descriptions.
- Source real imagery (executive portrait) to replace `Placeholder`
  components.
- Content migration path: `src/content/*.ts` arrays are hand-authored by
  design; when volume outgrows that, swap the `getXBySlug`/array exports for
  MDX frontmatter or a headless CMS query — nothing outside `src/content/`
  needs to change (see `content/README.md`).
- Wire the contact form to a real submission path; add spam protection.
- Resource downloads: real gating/delivery behind `ResourceDetail`'s CTA for
  `Premium` items (currently a label only, no paywall).
- Analytics/consent, final favicon/social preview image.
- Content review for DPDP/privacy-domain pages against current regulatory
  text before publishing.
- Phase 3 candidate (per the roadmap in the positioning review): promote
  Resources toward a "Governance Lab" framing once it carries enough
  original frameworks to earn the name; add a Speaking & Writing section
  once external citations exist.
- Deployment to Vercel — intentionally not done yet.

## 7. AOS Website Intake

The contact form (`src/components/contact/contact-form.tsx` →
`src/app/api/contact/route.ts`) is also this site's connection to AOS,
the operating system behind AI for U&I
(`AOS/website-intake/website-intake-model.md` in this same monorepo).
Every submission still sends its existing Resend notification email,
unchanged; in addition, the API route makes a best-effort call to
commit the submission as a JSON file into `AOS/website-intake/runtime/
inbox/` via the GitHub Contents API, so AOS can turn it into a Lead ID,
an opportunity record, a CRM record, a Revenue Hunter pipeline entry
and a Service Mapping recommendation automatically.

This is connector-ready, not required: without `AOS_INTAKE_GITHUB_TOKEN`
and `AOS_INTAKE_REPO` set (see `.env.example`), the contact form works
exactly as it always has — the AOS call cleanly no-ops, logged
server-side only, and never affects the response a visitor sees.

**`sourcePage`**: `CtaBand` (`src/components/sections/cta-band.tsx`)
accepts an optional `sourcePage` prop, appended to its link to `/contact`
as `?source=...` — set on the ADGL, Methodology (OPERA) and Selected
Advisory Engagements pages, and on both global "Start a Conversation"
buttons (header nav, homepage hero). The Contact page reads that query
param server-side and passes it to `ContactForm` as a hidden field, so
AOS can tell which page (or which global CTA) an enquiry started from.
A direct visit to `/contact` with no query param defaults to `"contact"`.
