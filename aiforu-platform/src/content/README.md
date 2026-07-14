# Content: extension contract

Everything in this directory is the site's data layer. Pages never
hard-code copy or lists; they import from here. This is what makes the
platform additive: new work gets published by editing data, not by
touching `app/` or `components/`.

## Adding new content

| To add a… | Do this | Do NOT |
|---|---|---|
| Advisory engagement (government, enterprise or strategic) | Append an entry to `advisory-engagements.ts` with a unique `slug` and a `track` | Create a new route or template |
| Governance domain | Append an entry to `governance-domains.ts` with an existing `cluster` id | Add a nav item; the domain shows up on `/governance-domains` automatically |
| Governance cluster (rare) | Add one entry to `governance-clusters.ts` | n/a |
| Insight (Point of View, Governance Note, Briefing, Field Note) | Append an entry to `insights.ts` with a `format` | Create a separate "Point of View" page; the homepage section is a filtered view of this same collection |
| Resource (any type/tier) | Append an entry to `resources.ts` | n/a |
| Current priority | Edit `items` in `current-priorities.ts` **and** bump `updatedAt` | Leave `updatedAt` stale; it is the freshness signal |

Cross-links (`relatedEngagementSlugs`, `relatedInsightSlugs`,
`relatedResourceSlugs`, `domainSlugs`) are plain slug arrays checked at
build time by `generateStaticParams`; a typo produces a broken link
during `next build`, not a silent 404 in production.

## Scale path

Listing pages (`/insights`, `/resources`, `/selected-advisory-engagements`)
already paginate and filter via `lib/pagination.ts` and
`lib/query.ts` against the in-memory arrays here. When the collection
sizes here outgrow hand-maintained `.ts` files (the stated target is
several hundred pieces of content), the migration is: replace the
arrays and `getXBySlug`/`getAllX` functions in this directory with
calls to MDX frontmatter or a headless CMS. Every `page.tsx` and
component downstream only calls those functions, so nothing outside
`src/content/` needs to change.
