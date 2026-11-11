# JobRadar backend

FastAPI service for company tracking, ATS scraping, resume keywords, and job matching.

For the full product guide, see [`../README.md`](../README.md).

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Windows entry points from `jobradar/`: `scripts/setup.ps1`, `scripts/start.ps1`.

## Common calls

Detect ATS from a career URL:

```bash
curl -X POST http://127.0.0.1:8000/api/companies/detect \
  -H 'Content-Type: application/json' \
  -d '{"career_url":"https://boards.greenhouse.io/stripe"}'
```

Create a company (auto-detect):

```bash
curl -X POST http://127.0.0.1:8000/api/companies \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Stripe",
    "career_url": "https://boards.greenhouse.io/stripe",
    "ats_type": "auto"
  }'
```

Scrape all active companies:

```bash
curl -X POST http://127.0.0.1:8000/api/scrape/run
```

Matched jobs (uses saved resume keywords):

```bash
curl 'http://127.0.0.1:8000/api/jobs?match=true&limit=20'
```

## Supported scrapers

`greenhouse`, `lever`, `ashby`, `smartrecruiters`, `workable`, `workday`, `generic` (also aliased as `custom`).
