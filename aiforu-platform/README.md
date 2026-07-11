# AIforU&I — Advisory Platform (Phase 1: Architecture & Codebase)

Independent advisory platform for Ramya Amballa. This is the **architecture and
component system**, not final content. Every page renders with clearly
labelled `[Placeholder]` copy pending Phase 2 authoring.

Positioning: independent executive advisor — not a consulting firm, not an
agency. The visual language (serif display type, restrained ink/paper
palette, generous whitespace, no stock photography) is built to read as the
digital home of a senior independent practitioner.

---

## Stack

- **Next.js 15** (App Router) + **React 19** + **TypeScript** (strict)
- **Tailwind CSS** — design tokens sourced from CSS custom properties
- No UI/animation/icon libraries — deliberately minimal dependency surface
- Static generation throughout (`generateStaticParams` for all `[slug]` routes)

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
│   ├── app/                          # Routes (App Router)
│   │   ├── layout.tsx                 # Root layout: fonts, ThemeProvider, SiteShell
│   │   ├── page.tsx                   # Home
│   │   ├── globals.css                # Design tokens + base styles
│   │   ├── sitemap.ts / robots.ts     # SEO infrastructure
│   │   ├── not-found.tsx
│   │   ├── selected-advisory-engagements/
│   │   │   ├── page.tsx               # Listing
│   │   │   └── [slug]/page.tsx        # Reusable engagement template
│   │   ├── advisory-services/page.tsx
│   │   ├── governance-domains/
│   │   │   ├── page.tsx               # Listing (9 domains)
│   │   │   └── [slug]/page.tsx        # Reusable domain template
│   │   ├── insights/
│   │   │   ├── page.tsx
│   │   │   └── [slug]/page.tsx
│   │   ├── resources/
│   │   │   ├── page.tsx
│   │   │   └── [slug]/page.tsx
│   │   ├── about/page.tsx
│   │   └── contact/page.tsx
│   │
│   ├── components/
│   │   ├── ui/                        # Design-system primitives
│   │   │   ├── button.tsx             # primary / secondary / ghost, sm/md/lg, polymorphic (Link or <button>)
│   │   │   ├── card.tsx               # Card + CardEyebrow/Title/Description/Footer
│   │   │   ├── badge.tsx
│   │   │   ├── container.tsx          # default / narrow / wide max-widths
│   │   │   ├── section-heading.tsx
│   │   │   ├── eyebrow.tsx
│   │   │   ├── divider.tsx
│   │   │   └── placeholder.tsx        # Image/diagram stand-ins + inline text placeholder
│   │   ├── layout/
│   │   │   ├── header.tsx             # Sticky nav, mobile menu, theme toggle
│   │   │   ├── footer.tsx
│   │   │   ├── site-shell.tsx         # Header + skip link + Footer wrapper
│   │   │   └── breadcrumbs.tsx
│   │   ├── theme/
│   │   │   ├── theme-provider.tsx     # Custom light/dark/system context (no dependency)
│   │   │   └── theme-toggle.tsx
│   │   ├── sections/
│   │   │   ├── page-hero.tsx          # Standard top-of-page hero
│   │   │   └── cta-band.tsx           # Primary + secondary CTA closing band
│   │   ├── advisory/                  # Selected Advisory Engagement components
│   │   ├── governance/                # Governance Domain components
│   │   ├── article/                   # Insights components
│   │   ├── resource/                  # Resources components
│   │   ├── contact/contact-form.tsx
│   │   └── seo/
│   │       ├── json-ld.tsx
│   │       └── schema.ts              # Person / Organization / Article / Breadcrumb schema.org builders
│   │
│   ├── content/                       # Placeholder data (swap for CMS/MDX in Phase 2)
│   │   ├── governance-domains.ts      # 9 domains
│   │   ├── advisory-engagements.ts    # 7 example engagements
│   │   ├── insights.ts
│   │   ├── resources.ts
│   │   └── advisory-services.ts
│   │
│   ├── lib/
│   │   ├── constants.ts               # site config, nav, primary/secondary CTA
│   │   ├── metadata.ts                # buildMetadata() — canonical/OG/Twitter helper
│   │   └── utils.ts                   # cn(), formatDate()
│   │
│   └── types/index.ts                 # GovernanceDomain, AdvisoryEngagement, Insight, Resource, NavItem
│
├── public/                            # Static assets (empty — no imagery per Phase 1 scope)
├── tailwind.config.ts                 # Color/type/spacing token mapping
└── next.config.ts
```

---

## 2. Architecture Explanation

**Content/presentation split.** Every listing and detail page is a thin
route file that pulls typed data from `src/content/*.ts` and hands it to a
template component. Adding a new advisory engagement, governance domain,
insight or resource is a data-only change — no new template code, no new
route file (the `[slug]` dynamic route + `generateStaticParams` already
covers it).

**Design tokens over hard-coded values.** Colour is defined once as HSL
triplets in CSS custom properties (`globals.css`) and consumed through
Tailwind's `hsl(var(--x) / <alpha-value>)` pattern. Light/dark are two sets
of the same variable names, switched by a `data-theme` attribute — nothing
in component code branches on theme.

**Three-tier component model.**
1. `components/ui` — dumb, domain-agnostic primitives (Button, Card, Badge…).
2. `components/{advisory,governance,article,resource}` — compose `ui`
   primitives into cards, grids and detail templates for one content type.
3. `app/**/page.tsx` — compose section components + content data. Pages
   contain no styling decisions of their own beyond layout order.

**Theme system has no dependency.** Rather than pull in `next-themes`, dark
mode is ~60 lines of context + a render-blocking inline script (in `<head>`)
that reads `localStorage` before hydration to avoid a flash of incorrect
theme.

**SEO is centralized.** `lib/metadata.ts#buildMetadata()` is the single
place that produces `<title>`, canonical URL, Open Graph and Twitter tags;
every route calls it with just a title/description/path. `components/seo`
adds schema.org JSON-LD (Person, ProfessionalService, Article,
BreadcrumbList) and `app/sitemap.ts` / `app/robots.ts` generate the crawl
surface from the same content files the pages render from — engagements,
domains, insights and resources can never drift out of the sitemap.

**Accessibility defaults.** Skip-to-content link, visible focus rings via
`:focus-visible`, semantic landmark elements (`header`/`main`/`footer`/`nav`
with `aria-label`), `aria-current="page"` in breadcrumbs, and form labels
tied to inputs in the contact form.

---

## 3. Components Created

| Category | Components |
|---|---|
| UI primitives | `Button`, `Card` (+ `CardEyebrow`/`CardTitle`/`CardDescription`/`CardFooter`), `Badge`, `Container`, `SectionHeading`, `Eyebrow`, `Divider`, `Placeholder`/`TextPlaceholder` |
| Layout | `Header`, `Footer`, `SiteShell`, `Breadcrumbs` |
| Theme | `ThemeProvider`, `ThemeToggle` |
| Sections | `PageHero`, `CtaBand` |
| Advisory | `AdvisoryEngagementCard`, `AdvisoryEngagementGrid`, `AdvisoryEngagementDetail` (reusable engagement template) |
| Governance | `GovernanceDomainCard`, `GovernanceDomainGrid`, `GovernanceDomainDetail` (reusable domain template) |
| Article (Insights) | `ArticleCard`, `ArticleGrid`, `ArticleDetail` |
| Resource | `ResourceCard`, `ResourceGrid`, `ResourceDetail` |
| Contact | `ContactForm` (presentational; no submit handler wired) |
| SEO | `JsonLd`, `schema.ts` (person/organization/article/breadcrumb builders), `buildMetadata()` |

## 4. Pages Created

`/`, `/selected-advisory-engagements`, `/selected-advisory-engagements/[slug]`
(7 example engagements), `/advisory-services`, `/governance-domains`,
`/governance-domains/[slug]` (all 9 domains), `/insights`,
`/insights/[slug]` (6 example insights), `/resources`,
`/resources/[slug]` (5 example resources), `/about`, `/contact`,
`/sitemap.xml`, `/robots.txt`, `not-found`.

Verified: `npm run typecheck`, `npm run build` (26 routes, 40 static pages
incl. dynamic slugs, zero errors/warnings) and a manual pass in-browser
(light + dark) confirming layout, theming and the reusable detail templates
render correctly.

## 5. Remaining Work for Phase 2

- Replace all `[Placeholder]` copy with real content (positioning, bio,
  engagement narratives, insight articles, resource descriptions).
- Source/commission real imagery (executive portrait, engagement visuals)
  to replace `Placeholder` components; remove the dashed placeholder style.
- Decide on content source of truth: keep `src/content/*.ts` hand-authored,
  or migrate to MDX / a headless CMS — the template components are
  data-shape agnostic either way.
- Wire the contact form to a real submission path (API route + email
  provider, or a form service) and add spam protection.
- Resource downloads: attach real files/gated-download flow behind
  `ResourceDetail`'s CTA.
- Analytics/consent (if required), plus final favicon/social preview image.
- Content review for DPDP/privacy-domain pages against current regulatory
  text before publishing.
- Deployment to Vercel (env vars, domain, preview workflow) — intentionally
  not done in Phase 1.
