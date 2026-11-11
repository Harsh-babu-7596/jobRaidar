# JobRadar

Local job-discovery console. Upload your resume, add company career pages (or import them from Excel), scrape openings, and rank jobs against keywords extracted from your resume.

```
Resume keywords  +  Company career URLs  →  Scrape  →  Matched job feed
```

## What you get

- **Radar Console** (React + TypeScript) at http://127.0.0.1:5173
- **API** (FastAPI) at http://127.0.0.1:8000 — docs at `/docs`
- **ATS auto-detect** from career URLs (Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Workday)
- **Generic fallback** for other career pages (JSON-LD / job-link heuristics)
- **Resume → keywords → ranked matches**
- **Excel import** for company lists
- **15-minute scheduler** while the backend is running

## Requirements

- Python 3.11+
- Node.js 20+ and npm
- Git (optional)

On some Linux distros, `python3 -m venv` needs `python3-venv`. If that fails, use [uv](https://github.com/astral-sh/uv): `uv venv .venv`.

---

## Quick start (Linux / macOS)

### 1. Backend

```bash
cd jobradar/backend
python3 -m venv .venv          # or: uv venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # or: uv pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Or from `jobradar/`:

```bash
./scripts/start-backend.sh
```

Check:

- Health: http://127.0.0.1:8000/health
- Swagger: http://127.0.0.1:8000/docs

### 2. Frontend

In a second terminal:

```bash
cd jobradar/frontend
cp .env.example .env
npm install
npm run dev
```

Or:

```bash
./scripts/start-frontend.sh
```

Open **http://127.0.0.1:5173**

`frontend/.env` should point at the API:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## Quick start (Windows)

From the `jobradar` folder in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
.\scripts\start.ps1
```

Then start the UI:

```powershell
cd frontend
npm install
npm run dev
```

---

## How to use the Radar Console

### Step 1 — Upload your resume

1. In the left rail, click **Upload resume** (PDF, DOCX, or TXT).
2. Keywords are extracted automatically.
3. Add/remove chips as needed, then **Save keywords**.

Keywords are stored locally in `backend/data/profile.json`.

### Step 2 — Add companies

**Option A — one by one**

1. Enter **Company name** and **Career URL** (e.g. `https://boards.greenhouse.io/stripe` or `https://company.com/careers`).
2. Leave ATS on auto (default). Optionally click **Detect ATS**.
3. Click **Add company**.

**Option B — Excel bulk import**

1. Click **Download template** (or open http://127.0.0.1:8000/api/companies/template.xlsx).
2. Fill rows and **Upload Excel**.

| Column | Required | Notes |
|---|---|---|
| `name` | yes | Unique company name |
| `career_url` | yes | Careers / board URL |
| `ats_type` | no | Use `auto` (recommended), or a specific ATS |
| `ats_identifier` | no | Usually filled by auto-detect |
| `active` | no | `true` / `false` (default true) |

### Step 3 — Scrape

Click **Scrape now** in the header. You’ll see per-company fetched / inserted / updated counts.

The backend also re-scrapes active companies about every **15 minutes** while it stays running (`SCRAPE_INTERVAL_MINUTES` in `backend/.env`).

### Step 4 — Browse matches

1. Keep **Match resume keywords** checked.
2. Optionally filter by title or location.
3. Open **Details** for a description snippet, or **Apply** for the posting.

Turn matching off to see the unfiltered scraped feed.

---

## Career URLs that work best

Prefer the company’s **public job-board URL** when you know the ATS:

| ATS | Example URL | Identifier (auto-filled) |
|---|---|---|
| Greenhouse | `https://boards.greenhouse.io/stripe` | `stripe` |
| Lever | `https://jobs.lever.co/example` | `example` |
| Ashby | `https://jobs.ashbyhq.com/notion` | `notion` |
| SmartRecruiters | `https://jobs.smartrecruiters.com/Company` | company slug |
| Workable | `https://apply.workable.com/account` | account shortcode |
| Workday | `https://company.wd5.myworkdayjobs.com/en-US/SiteName` | host\|tenant\|site |

A general `https://company.com/careers` page often works if:

- it embeds one of the ATS above, or
- it exposes JSON-LD `JobPosting` data / clear job links

**Harder cases:** heavy JavaScript portals (e.g. Google Careers) may return few or no jobs via the generic parser. Use a Greenhouse/Lever/Ashby/Workday board URL for that company when available.

---

## Useful API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness |
| `POST` | `/api/resume/upload` | Upload resume → extract keywords |
| `GET` | `/api/resume/profile` | Saved keywords / resume name |
| `PUT` | `/api/resume/keywords` | Replace keyword list |
| `POST` | `/api/companies/detect` | Detect ATS from a career URL |
| `POST` | `/api/companies` | Create company (`ats_type: "auto"` ok) |
| `GET` | `/api/companies` | List companies |
| `GET` | `/api/companies/template.xlsx` | Excel template |
| `POST` | `/api/companies/import` | Import companies from Excel |
| `POST` | `/api/scrape/run` | Scrape all active companies now |
| `GET` | `/api/jobs?match=true` | Ranked jobs for saved keywords |
| `GET` | `/api/jobs` | Plain job list (filters: `search`, `location`, `limit`) |

### Create company (auto-detect)

```bash
curl -X POST http://127.0.0.1:8000/api/companies \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Stripe",
    "career_url": "https://boards.greenhouse.io/stripe",
    "ats_type": "auto"
  }'
```

### Scrape now

```bash
curl -X POST http://127.0.0.1:8000/api/scrape/run
```

### Matched jobs

```bash
curl 'http://127.0.0.1:8000/api/jobs?match=true&limit=20'
```

---

## Project layout

```
jobradar/
  backend/                 FastAPI app, scrapers, SQLite
    app/
      api/                 companies, jobs, resume routes
      scrapers/            greenhouse, lever, ashby, …
      services/            detect, match, resume, scheduler
    data/                  jobradar.db, profile.json (runtime)
    logs/                  jobradar.log
  frontend/                React + TypeScript Radar Console
  scripts/                 start-backend.sh, start-frontend.sh, Windows .ps1
```

## Configuration

`backend/.env` (from `.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | SQLite under `backend/data/` | DB connection |
| `SCRAPE_INTERVAL_MINUTES` | `15` | Scheduler interval |
| `REQUEST_TIMEOUT_SECONDS` | `20` | HTTP timeout for scrapers |

## Data & logs

- Database: `backend/data/jobradar.db`
- Resume profile: `backend/data/profile.json`
- Logs: `backend/logs/jobradar.log`
- Sample Excel: `backend/data/samples/companies_template.xlsx`

---

## Limitations

- Generic / unknown career sites are best-effort; JS-only boards may not scrape cleanly.
- Keyword extraction uses a curated skills lexicon (not an LLM) — edit chips after upload.
- Stale jobs are not auto-deactivated when they disappear from a board.
- Google Sheets sync is not implemented.
- The scheduler only runs while the backend process is alive.
- Start with a few companies, confirm results, then scale.
- Respect site terms, robots rules, rate limits, and API policies.

## Troubleshooting

| Symptom | What to try |
|---|---|
| UI shows API offline | Start backend; confirm http://127.0.0.1:8000/health |
| CORS / network errors in browser | Ensure `VITE_API_BASE_URL` matches the API; backend allows `localhost:5173` / `127.0.0.1:5173` |
| Scrape fetched 0 / failed | Prefer a known ATS board URL; check `backend/logs/jobradar.log` |
| No matched jobs | Upload resume / save keywords; confirm scrape inserted jobs; toggle match filter |
| `python3 -m venv` fails on Linux | Install `python3-venv` or use `uv venv .venv` |
