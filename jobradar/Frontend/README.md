# JobRadar Frontend

React + TypeScript **Radar Console** for resume matching and ATS monitoring.

## Run

```bash
cp .env.example .env
npm install
npm run dev
```

Open http://127.0.0.1:5173

Requires the backend at `VITE_API_BASE_URL` (default `http://127.0.0.1:8000`).

Full usage guide: [`../README.md`](../README.md)

## Console flow

1. Upload resume → edit/save keywords  
2. Add companies (URL auto-detect) or import Excel  
3. Scrape now  
4. Browse ranked matches (title/location filters optional)

## Layout

- `src/api` — HTTP client and endpoint modules
- `src/types` — shared TypeScript contracts
- `src/hooks` — data loading / scrape / profile state
- `src/components` — layout, resume, companies, jobs, scrape, common UI
- `src/styles` — design tokens and console styles
- `src/utils` — date / ATS helpers
