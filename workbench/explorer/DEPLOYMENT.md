# Deployment

The Explorer is a fully static site (`output: "export"` in `next.config.mjs`) — no backend, no database, no server runtime, no environment variables. Once built, `out/` is plain HTML/CSS/JS that can be served from any static host or CDN. This document covers deploying it to **Vercel**, at the target domain `workbench.aiforui.com`.

## Why this needs one manual setting

This repository is a monorepo: `workbench/explorer` is one of several unrelated projects at the repo root (AOS, ai-governance, and others). Vercel's project import can't infer which subdirectory to build, so the single required manual step is setting the project's **Root Directory** to `workbench/explorer`. Everything else — framework detection, build command, output directory, headers — is picked up automatically from this directory once that's set.

## One-click import

1. In Vercel, **Add New → Project**, and import `ramya-amballa/aiforui-platform` (or whichever remote hosts this repo).
2. In the import screen's **Root Directory** setting, choose **Edit** and select `workbench/explorer`.
3. Framework Preset should auto-detect as **Next.js**. Leave Build Command / Output Directory as detected — they're pinned explicitly in `vercel.json` (`npm run vercel-build`, output `out`) so there's nothing to fill in by hand.
4. No environment variables are required. Click **Deploy**.

Every subsequent push to the connected branch redeploys automatically; pull requests get their own preview deployment.

## What `vercel.json` and `package.json` do

- **`package.json`'s `vercel-build` script** (`npm run build`) is what Vercel's zero-config Next.js detection runs instead of guessing a build command.
- **`predev`/`prebuild`** run `npm --prefix .. install --no-audit --no-fund` before `build-data`. This exists because `scripts/quality.ts` (which powers the live Quality Dashboard on `/standards`) imports the real validator and editorial tooling from `/workbench/validators` and `/workbench/editorial`, which depend on packages declared in `/workbench/package.json`, not `explorer/package.json`. Vercel only installs the Root Directory's own dependencies by default; this hook installs the sibling workbench-root dependencies too, so the build has everything it needs from a clean checkout. See `README.md`'s "Quality dashboard architecture" section for why those checks reuse the real tooling instead of re-implementing it.
- **`vercel.json`** pins `framework`, `buildCommand`, `installCommand`, and `outputDirectory` explicitly (belt-and-suspenders alongside auto-detection), and declares response headers — see below.

## Security headers

Static export means `next.config.mjs`'s `headers()` API isn't available (Next doesn't support it under `output: "export"`), so headers are declared in `vercel.json` instead, which Vercel's static hosting layer applies to every response:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` — camera, microphone, and geolocation denied
- `Strict-Transport-Security` with `includeSubDomains`
- A `Content-Security-Policy` scoped to `'self'` for scripts, styles, fonts, and connections (plus `data:` for images). This is safe to keep strict because the Explorer loads nothing from a third party — no analytics, no web fonts, no embeds. **If that ever changes, the CSP in `vercel.json` needs a matching update, or pages using the new resource will silently fail to load it.**
- Long-lived immutable caching for hashed `_next/static/*` build assets; a short, revalidated cache for the unhashed public icons/OG image so a future asset update isn't stuck behind a stale cache.

Verified locally before deploy by serving `out/` with these exact headers via Playwright and confirming zero console/CSP errors across the homepage, a node detail page, `/graph` (canvas + d3-force), `/standards` (client components), a framework page, and the `⌘K` search flow.

## Custom domain: `workbench.aiforui.com`

Not connected yet — for when it is:

1. In the Vercel project, **Settings → Domains → Add**, enter `workbench.aiforui.com`.
2. Vercel will show a DNS record to add at whatever registrar/DNS provider manages `aiforui.com` — typically a `CNAME` record: `workbench` → `cname.vercel-dns.com`.
3. Vercel provisions and renews the TLS certificate automatically once the record resolves; no manual certificate handling needed.
4. `app/layout.tsx`'s `metadataBase`, `app/sitemap.ts`, and `app/robots.ts` already point at `https://workbench.aiforui.com` (set ahead of the domain going live, which is standard practice — canonical/OG tags express intent, they don't redirect). If the final domain ever differs, that's the one string (`SITE_URL`) to update in each of those three files.

## Reproducing a production build locally

```sh
cd workbench/explorer
rm -rf .next out data/generated
npm run build      # runs prebuild (installs ../, regenerates data), then next build + export
npx serve out -l 3000
```

This is exactly what Vercel runs (`vercel-build` calls the same `next build`), so a clean local build is a reliable predictor of what will ship. The build was additionally verified from a genuine cold start — `workbench/node_modules` removed entirely before running — to confirm the `prebuild` hook alone is sufficient on a fresh Vercel checkout.

## Post-deploy checklist

- [ ] Homepage and a handful of node/detail pages (one per entity type) load and render correctly
- [ ] `/sitemap.xml` returns all routes (13 static + one entry per canonical object + one per framework)
- [ ] `/robots.txt` references the sitemap and allows all crawling
- [ ] `/manifest.webmanifest` loads and references the correct icons
- [ ] Favicon and Open Graph image appear correctly when the URL is shared (check via a social-preview debugger once the custom domain is live)
- [ ] Response headers include the security headers listed above (`curl -I` against the deployed URL)
- [ ] `⌘K` search, the Graph view, and Executive Export (Markdown + Print) still work in production, not just locally

## Rollback

Vercel keeps every deployment; if a deploy regresses something, use **Instant Rollback** in the project's Deployments tab to repoint production traffic at the previous deployment immediately, no rebuild required.
