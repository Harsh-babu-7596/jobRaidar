# JobRadar

Local resume-aware job discovery: scrape company career boards, match openings to keywords from your resume, and browse results in a Radar Console UI.

**Full setup and usage guide:** [`jobradar/README.md`](jobradar/README.md)

## Start here

```bash
# Terminal 1 — API
cd jobradar
./scripts/start-backend.sh

# Terminal 2 — UI
./scripts/start-frontend.sh
```

Then open:

- Console: http://127.0.0.1:5173
- API docs: http://127.0.0.1:8000/docs

**Typical flow:** upload resume → add companies (career URL or Excel) → Scrape now → browse matched jobs.
