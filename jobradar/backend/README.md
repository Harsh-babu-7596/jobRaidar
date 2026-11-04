# JobRadar backend

The root-level `scripts/setup.ps1` and `scripts/start.ps1` are the recommended Windows entry points.

For manual startup from this directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

## API examples

Create a Greenhouse company with `POST /api/companies`:

```json
{
  "name": "Example Company",
  "career_url": "https://boards.greenhouse.io/example",
  "ats_type": "greenhouse",
  "ats_identifier": "example",
  "active": true
}
```

Run a scrape manually with `POST /api/scrape/run`.
