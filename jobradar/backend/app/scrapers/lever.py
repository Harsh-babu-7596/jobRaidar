import requests
from app.config import REQUEST_TIMEOUT_SECONDS
from app.scrapers.base import BaseScraper

class LeverScraper(BaseScraper):
    def fetch_jobs(self, company) -> list[dict]:
        site = company.ats_identifier
        if not site:
            raise ValueError(f"{company.name}: missing Lever site identifier")

        url = f"https://api.lever.co/v0/postings/{site}"
        response = requests.get(
            url, params={"mode": "json"}, timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": "JobRadar/0.1 (personal job discovery tool)"},
        )
        response.raise_for_status()

        results = []
        for item in response.json():
            categories = item.get("categories") or {}
            lists = item.get("lists") or []
            description = item.get("descriptionPlain") or ""
            if lists:
                description += "\n" + "\n".join(
                    f"{section.get('text', '')}: {section.get('content', '')}"
                    for section in lists
                )
            results.append({
                "external_job_id": str(item.get("id")),
                "title": item.get("text") or "Untitled",
                "location": categories.get("location"),
                "description": description,
                "apply_url": item.get("hostedUrl") or item.get("applyUrl") or "",
                "posted_at": item.get("createdAt"),
            })
        return results
