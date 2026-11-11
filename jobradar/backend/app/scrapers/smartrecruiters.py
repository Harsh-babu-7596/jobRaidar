from app.config import REQUEST_TIMEOUT_SECONDS
from app.scrapers.base import BaseScraper
from app.services.http_client import get


class SmartRecruitersScraper(BaseScraper):
    def fetch_jobs(self, company) -> list[dict]:
        company_id = company.ats_identifier
        if not company_id:
            raise ValueError(f"{company.name}: missing SmartRecruiters company id")

        results: list[dict] = []
        offset = 0
        limit = 100
        while True:
            url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
            response = get(
                url,
                timeout=REQUEST_TIMEOUT_SECONDS,
                params={"limit": limit, "offset": offset},
            )
            response.raise_for_status()
            payload = response.json()
            content = payload.get("content") or []
            for item in content:
                location = None
                loc = item.get("location") or {}
                if isinstance(loc, dict):
                    parts = [loc.get("city"), loc.get("region"), loc.get("country")]
                    location = ", ".join(p for p in parts if p) or None
                ref = item.get("ref") or item.get("id")
                apply_url = ""
                if isinstance(ref, str) and ref.startswith("http"):
                    apply_url = ref
                elif item.get("id"):
                    apply_url = f"https://jobs.smartrecruiters.com/{company_id}/{item['id']}"

                results.append(
                    {
                        "external_job_id": str(item.get("id") or apply_url),
                        "title": item.get("name") or "Untitled",
                        "location": location,
                        "description": None,
                        "apply_url": apply_url,
                        "posted_at": item.get("releasedDate") or item.get("createdOn"),
                    }
                )

            total = int(payload.get("totalFound") or 0)
            offset += limit
            if offset >= total or not content:
                break
            if offset > 1000:  # safety cap
                break
        return results
