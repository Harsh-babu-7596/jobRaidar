from urllib.parse import urlparse

from app.config import REQUEST_TIMEOUT_SECONDS
from app.scrapers.base import BaseScraper
from app.services.http_client import post


class WorkdayScraper(BaseScraper):
    def fetch_jobs(self, company) -> list[dict]:
        host, tenant, site = self._parse_identity(company)
        url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
        results: list[dict] = []
        offset = 0
        limit = 20

        while True:
            response = post(
                url,
                timeout=REQUEST_TIMEOUT_SECONDS,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                json={
                    "appliedFacets": {},
                    "limit": limit,
                    "offset": offset,
                    "searchText": "",
                },
            )
            response.raise_for_status()
            payload = response.json()
            postings = payload.get("jobPostings") or []
            for item in postings:
                external_path = item.get("externalPath") or ""
                apply_url = (
                    f"https://{host}{external_path}"
                    if external_path.startswith("/")
                    else external_path
                )
                results.append(
                    {
                        "external_job_id": str(
                            item.get("bulletFields", [None])[0]
                            if item.get("bulletFields")
                            else item.get("externalPath") or item.get("title")
                        ),
                        "title": item.get("title") or "Untitled",
                        "location": item.get("locationsText"),
                        "description": item.get("jobPostingInfo", {}).get("jobDescription")
                        if isinstance(item.get("jobPostingInfo"), dict)
                        else None,
                        "apply_url": apply_url,
                        "posted_at": item.get("postedOn"),
                    }
                )

            total = int(payload.get("total") or 0)
            offset += limit
            if offset >= total or not postings:
                break
            if offset > 500:  # safety cap
                break
        return results

    def _parse_identity(self, company) -> tuple[str, str, str]:
        raw = (company.ats_identifier or "").strip()
        if raw and "|" in raw:
            host, tenant, site = raw.split("|", 2)
            return host, tenant, site

        career = company.career_url or ""
        parsed = urlparse(career)
        host = parsed.netloc
        parts = [p for p in parsed.path.split("/") if p]
        # drop locale segment if present
        if parts and ("-" in parts[0] and len(parts[0]) <= 6):
            site = parts[1] if len(parts) > 1 else ""
        else:
            site = parts[0] if parts else ""
        tenant = host.split(".")[0] if host else ""
        if not (host and tenant and site):
            raise ValueError(
                f"{company.name}: Workday identity missing. "
                "Use career URL like https://company.wd5.myworkdayjobs.com/en-US/SiteName "
                "or identifier host|tenant|site"
            )
        return host, tenant, site
