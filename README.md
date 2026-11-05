# JobRadar

Local job-discovery platform with a Python/FastAPI backend, scheduled ATS scrapers,
SQLite storage, and planned Google Sheets + React interfaces.

## Windows 10/11 quick start

Requirements:
- Python 3.11 or newer
- PowerShell 5.1+ or PowerShell 7
- Git (optional)

Open PowerShell in the extracted `JobRadar` folder:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
.\scripts\start.ps1
```

Then open:
- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

The backend creates its SQLite database at `backend/data/jobradar.db` and writes logs
to `backend/logs/jobradar.log`.

## Current implementation

- Greenhouse public job-board endpoint
- Lever public postings endpoint
- SQLAlchemy models and duplicate-safe job upsert
- FastAPI company and job endpoints
- 15-minute local scheduler
- Windows PowerShell setup/start scripts

## Important limitations

- React frontend and Google Sheets sync are not implemented yet.
- `custom` ATS is an adapter placeholder; individual career sites need dedicated parsers.
- The scheduler runs only while the backend process is running.
- Start with a small number of test companies, verify site-specific behavior, then scale.
- Respect website terms, robots directives, rate limits, and API usage rules.
