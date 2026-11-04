import requests
from app.config import REQUEST_TIMEOUT_SECONDS
from app.scrapers.base import BaseScraper

class GreenhouseScraper(BaseScraper):
    def fetch_jobs(self, company) -> list[dict]:
        token = company.ats_identifier
        if not token:
            raise ValueError(f"{company.name}: missing Greenhouse board token")

        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
        response = requests.get(
            url, params={"content": "true"}, timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": "JobRadar/0.1 (personal job discovery tool)"},
        )
        response.raise_for_status()

        results = []
        for item in response.json().get("jobs", []):
            location = (item.get("location") or {}).get("name")
            results.append({
                "external_job_id": str(item["id"]),
                "title": item.get("title") or "Untitled",
                "location": location,
                "description": item.get("content"),
                "apply_url": item.get("absolute_url") or "",
                "posted_at": item.get("updated_at"),
            })
        return results
