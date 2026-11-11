from app.config import REQUEST_TIMEOUT_SECONDS
from app.scrapers.base import BaseScraper
from app.services.http_client import get


class WorkableScraper(BaseScraper):
    def fetch_jobs(self, company) -> list[dict]:
        account = company.ats_identifier
        if not account:
            raise ValueError(f"{company.name}: missing Workable account shortcode")

        # Prefer widget/account JSON endpoints used by public career widgets.
        endpoints = [
            f"https://apply.workable.com/api/v1/widget/accounts/{account}",
            f"https://apply.workable.com/api/v2/accounts/{account}/jobs",
        ]

        last_error: Exception | None = None
        payload = None
        for url in endpoints:
            try:
                response = get(url, timeout=REQUEST_TIMEOUT_SECONDS)
                response.raise_for_status()
                payload = response.json()
                break
            except Exception as exc:  # noqa: BLE001
                last_error = exc

        if payload is None:
            raise RuntimeError(f"{company.name}: Workable fetch failed ({last_error})")

        jobs = payload.get("jobs") if isinstance(payload, dict) else payload
        if not isinstance(jobs, list):
            jobs = []

        results = []
        for item in jobs:
            location = item.get("location") or item.get("city")
            if isinstance(location, dict):
                location = location.get("city") or location.get("location_str")
            apply_url = (
                item.get("url")
                or item.get("shortlink")
                or item.get("application_url")
                or ""
            )
            results.append(
                {
                    "external_job_id": str(item.get("id") or item.get("shortcode") or apply_url),
                    "title": item.get("title") or item.get("name") or "Untitled",
                    "location": location,
                    "description": item.get("description") or item.get("full_description"),
                    "apply_url": apply_url,
                    "posted_at": item.get("published_on") or item.get("created_at"),
                }
            )
        return results
