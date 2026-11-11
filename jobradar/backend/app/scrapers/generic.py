from __future__ import annotations

import json
import re
from html import unescape
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.config import REQUEST_TIMEOUT_SECONDS
from app.scrapers.base import BaseScraper
from app.services.http_client import get

JOB_HREF_RE = re.compile(
    r"(careers?|jobs?|positions?|openings?|vacanc|opportunit)",
    re.IGNORECASE,
)


class GenericCareerScraper(BaseScraper):
    """Best-effort parser for arbitrary career pages.

    Strategy:
    1) JSON-LD JobPosting on the page
    2) Discover job-like links and read JobPosting from those pages
    3) Fall back to link title heuristics
    """

    def fetch_jobs(self, company) -> list[dict]:
        career_url = company.career_url
        if not career_url:
            raise ValueError(f"{company.name}: career_url is required for generic scraping")

        html = self._fetch_html(career_url)
        jobs = self._jobs_from_json_ld(html, base_url=career_url)

        if len(jobs) < 3:
            link_jobs = self._jobs_from_links(html, base_url=career_url, limit=40)
            jobs = self._merge(jobs, link_jobs)

        if not jobs:
            raise ValueError(
                f"{company.name}: no jobs found on career page. "
                "If this company uses Greenhouse/Lever/Ashby/Workday, paste that board URL instead."
            )
        return jobs

    def _fetch_html(self, url: str) -> str:
        response = get(url, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True)
        response.raise_for_status()
        return response.text

    def _jobs_from_json_ld(self, html: str, *, base_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[dict] = []
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            raw = script.string or script.get_text() or ""
            raw = raw.strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            for node in self._walk(data):
                if not isinstance(node, dict):
                    continue
                types = node.get("@type")
                type_list = types if isinstance(types, list) else [types]
                if "JobPosting" not in {str(t) for t in type_list if t}:
                    continue
                jobs.append(self._job_from_posting(node, base_url=base_url))
        return [j for j in jobs if j.get("external_job_id") and j.get("title")]

    def _jobs_from_links(self, html: str, *, base_url: str, limit: int) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        base_host = urlparse(base_url).netloc
        candidates: list[tuple[str, str]] = []
        seen: set[str] = set()

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            text = " ".join(anchor.get_text(" ", strip=True).split())
            absolute = urljoin(base_url, href)
            parsed = urlparse(absolute)
            if parsed.scheme not in {"http", "https"}:
                continue
            if parsed.netloc and base_host and parsed.netloc != base_host:
                # Allow common job hosts
                if not any(
                    key in parsed.netloc
                    for key in (
                        "greenhouse",
                        "lever",
                        "ashby",
                        "workday",
                        "smartrecruiters",
                        "workable",
                    )
                ):
                    continue
            path = parsed.path or ""
            if not (JOB_HREF_RE.search(path) or JOB_HREF_RE.search(text)):
                continue
            # Skip pure listing roots
            if path.rstrip("/").lower() in {"/jobs", "/careers", "/career", "/job"}:
                continue
            if absolute in seen:
                continue
            seen.add(absolute)
            candidates.append((absolute, text or "Untitled"))
            if len(candidates) >= limit:
                break

        jobs: list[dict] = []
        for url, text in candidates[:25]:
            try:
                page = self._fetch_html(url)
                detailed = self._jobs_from_json_ld(page, base_url=url)
                if detailed:
                    jobs.extend(detailed)
                    continue
            except Exception:
                pass
            jobs.append(
                {
                    "external_job_id": url,
                    "title": text[:500] or "Untitled",
                    "location": None,
                    "description": None,
                    "apply_url": url,
                    "posted_at": None,
                }
            )
        return jobs

    def _job_from_posting(self, node: dict, *, base_url: str) -> dict:
        title = node.get("title") or "Untitled"
        apply_url = (
            node.get("url")
            or node.get("applicationUrl")
            or node.get("sameAs")
            or base_url
        )
        if isinstance(apply_url, list):
            apply_url = apply_url[0] if apply_url else base_url
        location = None
        loc = node.get("jobLocation")
        if isinstance(loc, dict):
            address = loc.get("address")
            if isinstance(address, dict):
                parts = [
                    address.get("addressLocality"),
                    address.get("addressRegion"),
                    address.get("addressCountry"),
                ]
                location = ", ".join(str(p) for p in parts if p) or None
            else:
                location = loc.get("name")
        elif isinstance(loc, list) and loc:
            location = self._job_from_posting({"jobLocation": loc[0]}, base_url=base_url).get(
                "location"
            )

        description = node.get("description")
        if isinstance(description, str):
            description = unescape(re.sub(r"<[^>]+>", " ", description))
            description = re.sub(r"\s+", " ", description).strip()

        external_id = str(node.get("identifier") or apply_url or title)
        if isinstance(node.get("identifier"), dict):
            external_id = str(
                node["identifier"].get("value")
                or node["identifier"].get("name")
                or external_id
            )

        return {
            "external_job_id": external_id,
            "title": str(title)[:500],
            "location": location,
            "description": description,
            "apply_url": str(apply_url),
            "posted_at": node.get("datePosted"),
        }

    def _walk(self, node):
        if isinstance(node, list):
            for item in node:
                yield from self._walk(item)
        elif isinstance(node, dict):
            yield node
            if "@graph" in node:
                yield from self._walk(node["@graph"])
            for value in node.values():
                if isinstance(value, (dict, list)):
                    yield from self._walk(value)

    def _merge(self, primary: list[dict], secondary: list[dict]) -> list[dict]:
        seen = {j["external_job_id"] for j in primary}
        merged = list(primary)
        for job in secondary:
            if job["external_job_id"] in seen:
                continue
            seen.add(job["external_job_id"])
            merged.append(job)
        return merged
