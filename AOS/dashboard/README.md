# AOS Command Center

The single operating interface for AI for U&I's AOS (AI for U&I Operating
System). This is a **presentation and orchestration layer only** — it
invokes the existing AI employees exactly as a human would run them by
hand, and displays whatever they already write to disk. It does not
contain, duplicate, or modify any scoring, classification, routing, or
business logic — every one of the eleven AI employees (Market
Intelligence, Website Intake, Opportunity Hunter, Revenue Hunter, CRM,
Service Mapping, Sales Director, Product Manager, Content Director,
Daily Brief, CEO Advisor) is treated as a black-box service.

## Installation

From the repository root:

```bash
cd AOS/dashboard
pip install -r requirements.txt
```

Requires Python 3.11+ (matching the rest of AOS). The existing AOS
runtimes remain dependency-free stdlib Python — Streamlit/pandas/plotly
are scoped entirely to this dashboard.

## Running Locally

**Windows, no terminal needed:** double-click `Start_AOS.bat` in this
folder. See `README_START_HERE.md`. It finds Python, installs any
missing packages (only the first time), starts the dashboard, and
opens your browser automatically. If the dashboard is already running,
it just opens the browser. Double-click `Stop_AOS.bat` to stop it.

**Manual / any OS:**

```bash
cd AOS/dashboard
streamlit run app.py
```

Opens at `http://localhost:8501`. The sidebar lists every page in the
order specified for AOS v1.0: Home, CEO Advisor, Opportunity Hunter,
Market Intelligence, Website Leads, CRM, Revenue Hunter, Service
Mapping, Sales Director, Content Director, Product Manager, Execution,
Reports, Charts, Settings, Logs.

No configuration is required to view the dashboard against a fresh
checkout — every page handles missing output files honestly (a clear
"no data yet" message), since AOS's own convention is to never
fabricate data. Click an employee's action button (or **Run Full AOS**
on the Execution page) to generate real output, then revisit any page
to see it.

## Architecture

```
AOS/dashboard/
  Start_AOS.bat            Windows one-click launcher — see README_START_HERE.md.
  Stop_AOS.bat             Windows one-click stop.
  README_START_HERE.md     Three-line non-technical quick start.
  app.py                  Home page: date, last execution, system status,
                           employees running, executive summary, top 3
                           priorities, and the 10 business-at-a-glance cards.
  pages/                  One file per sidebar page. Streamlit's numbered-
                           file convention (01_, 02_, ...) fixes the sidebar
                           order to exactly the order specified for AOS v1.0,
                           with Execution/Reports/Charts inserted after
                           Product Manager (not part of the original 12-item
                           sidebar list, but required by separate sections
                           of the same spec) and Settings/Logs kept last.
  components/             Shared, reusable UI and integration code:
    theme.py                 Injects assets/style.css; page config.
    cards.py                 Metric-card rendering for Home and per-runtime
                              pages.
    tables.py                Dataframe rendering with a graceful empty state.
    charts.py                Plotly chart builders, styled to the brand
                              palette (no gradients, no bright colors).
    runtime_runner.py        Subprocess wrapper — every "Run X" button goes
                              through this. Mirrors orchestrator.py's own
                              run_attempt(): `python3 <script>`, run from the
                              script's own directory, output captured, never
                              imported in-process.
    data_loader.py           Safe, read-only JSON/Markdown loaders. A missing
                              file is reported as "no data yet", never
                              fabricated and never a crash.
  assets/
    style.css                The actual theme: white background, dark blue
                              headings, grey cards, no gradients/animations.
                              Colors are the real AI for U&I brand tokens
                              (aiforu-platform/src/app/globals.css), not
                              invented ones.
  config/
    runtimes.json             The button-to-runtime manifest — see below.
    settings.json              UI-only dashboard preferences (table density).
                              Never stores secrets.
  utils/
    paths.py                  Central path resolution (AOS_ROOT env var,
                              defaulting to this checkout — see Deployment).
    formatting.py              parse_currency/format_amount, reused verbatim
                              from revenue-hunter/runtime/generate.py, so
                              currency parsing matches every runtime exactly.
    state.py                   Small Streamlit session-state helpers.
  .streamlit/config.toml       Base theme (colors match assets/style.css).
  Dockerfile                  Optional container build — see Deployment.
  requirements.txt
```

## How Every Button Maps to the Existing AOS Runtime

`config/runtimes.json` is the single source of truth: for every AI
employee it records the exact `script` to run, the `cwd` to run it
from, and the `outputs`/`outputDir`/`dataFile` the corresponding page
reads afterward. Every button in the dashboard calls
`components/runtime_runner.run_script(script, cwd)`, which shells out
to `python3 <script>` from `<cwd>` — identical to how
`AOS/orchestrator/orchestrator.py` runs the same script, and identical
to running it by hand from the terminal.

| Page | Button | Script (via `runtime_runner`) | Primary output read |
|---|---|---|---|
| CEO Advisor | Run CEO Advisor | `ceo-advisor/runtime/generate.py` | `ceo-advisor/runtime/output/ceo-daily-report.md` (+ weekly/monthly) |
| Opportunity Hunter | Scan Opportunities | `opportunity-hunter/runtime/collect.py` | `opportunity-hunter/opportunity-schema.json`, today's daily report |
| Market Intelligence | Check Market | `05-Market-Intelligence/runtime/monitor.py` | today's market intelligence report |
| Website Leads | Refresh Website Leads | `website-intake/runtime/generate.py` | `website-intake/leads.json` |
| CRM | Open CRM | `crm/runtime/generate.py` | `06-CRM/company-intelligence.json`, today's CRM reports |
| Revenue Hunter | Update Forecast | `revenue-hunter/runtime/generate.py` | `08-Revenue-Hunter/pipeline.json`, revenue dashboard/forecast |
| Service Mapping | Run Service Mapping | `service-mapping/runtime/generate.py` | `service-mapping/service-recommendations.json` |
| Sales Director | Generate Proposal | `sales-director/runtime/prepare.py` | `sales-director/runtime/output/ceo-advisor-feed.json` + per-opportunity packages in `output/packages/` |
| Content Director | Generate Content | `content-director/runtime/generate.py` | drafts in `content-director/runtime/output/drafts/` |
| Product Manager | Review Product Ideas | `product-manager/runtime/generate.py` | `03-Product-Manager/product-backlog.json` |
| Execution | Run Full AOS | `orchestrator/orchestrator.py` | `orchestrator/status.json`, the day's Daily Execution Report |

The Reports page reads `config/runtimes.json`'s `reports` section (a
label → file-path map) to offer the six requested downloads. The
Charts page reads the same underlying data files listed above — it
never calls a runtime script, since every chart is a read-only view
over data other pages already produce.

## Deployment

Designed to move from a laptop to a hosted domain (e.g.
`aos.aiforui.org`) with minimal changes:

- **No hardcoded paths.** `utils/paths.py` resolves everything relative
  to an `AOS_ROOT` environment variable, defaulting to this checkout's
  own parent directory for local use. A hosted deployment only needs
  to set `AOS_ROOT` (or place `AOS/` where the default expects it).
- **Docker.** `Dockerfile` builds an image containing the full `AOS/`
  tree (build from the repository root, not this directory — see the
  file's own header comment) so every runtime script the dashboard
  invokes is present in the image:
  ```bash
  docker build -f AOS/dashboard/Dockerfile -t aos-command-center .
  docker run -p 8501:8501 aos-command-center
  ```
- **Streamlit Community Cloud.** Point it at this repo with
  `AOS/dashboard/app.py` as the entry point; set `AOS_ROOT` if the
  checkout layout differs from local.
- **Reverse proxy / systemd.** Run `streamlit run app.py
  --server.port=8501 --server.address=127.0.0.1` under systemd, and
  reverse-proxy `aos.aiforui.org` to it (nginx/Caddy) with TLS
  terminated at the proxy. `.streamlit/config.toml` already disables
  Streamlit's own CORS handling assumptions that don't apply behind a
  proxy.
- **Secrets stay out of the dashboard.** The Settings page only ever
  reports whether an environment variable is set — never its value —
  and never persists a secret to any file the dashboard controls. Real
  credentials are environment variables / GitHub Actions repository
  secrets, exactly as every connector already expects (see
  `opportunity-hunter/runtime/config/credentials.template.env`).

## What This Dashboard Deliberately Does Not Do

- Does not reimplement any employee's scoring, classification, routing,
  or aggregation logic — every number and every report shown is read
  directly from a file that employee's own runtime wrote.
- Does not write to any business data file (`opportunity-schema.json`,
  `pipeline.json`, `company-intelligence.json`, `leads.json`,
  `service-recommendations.json`, etc.) — only the employees themselves
  do that. The dashboard's only writes are its own
  `config/settings.json` (a UI preference) and whatever a runtime
  script it invoked wrote on its own.
- Does not import any runtime module in-process — every "Run X" button
  is a subprocess call, identical to the Orchestrator's own invocation
  pattern, so a crash in one employee can never take down the
  dashboard or any other page.
- Does not fabricate placeholder data. An employee with no output yet
  shows an honest "no data yet" message and, where applicable, the
  button to generate it.
