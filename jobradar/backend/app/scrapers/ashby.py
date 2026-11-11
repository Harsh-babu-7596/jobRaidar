from app.config import REQUEST_TIMEOUT_SECONDS
from app.scrapers.base import BaseScraper
from app.services.http_client import get


class AshbyScraper(BaseScraper):
    def fetch_jobs(self, company) -> list[dict]:
        board = company.ats_identifier
        if not board:
            raise ValueError(f"{company.name}: missing Ashby board name")

        url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
        response = get(url, timeout=REQUEST_TIMEOUT_SECONDS, params={"includeCompensation": "true"})
        response.raise_for_status()
        payload = response.json()

        results = []
        for item in payload.get("jobs", []):
            location = item.get("location")
            if not location:
                locs = item.get("locations") or []
                if locs and isinstance(locs[0], dict):
                    location = locs[0].get("name") or locs[0].get("location")
                elif locs:
                    location = str(locs[0])
            results.append(
                {
                    "external_job_id": str(item.get("id") or item.get("jobUrl") or item.get("title")),
                    "title": item.get("title") or "Untitled",
                    "location": location,
                    "description": item.get("descriptionPlain") or item.get("descriptionHtml"),
                    "apply_url": item.get("jobUrl") or item.get("applyUrl") or "",
                    "posted_at": item.get("publishedAt") or item.get("updatedAt"),
                }
            )
        return results
