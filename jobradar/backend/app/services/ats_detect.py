from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from app.config import REQUEST_TIMEOUT_SECONDS
from app.services.http_client import get

ALLOWED_ATS = {
    "greenhouse",
    "lever",
    "ashby",
    "smartrecruiters",
    "workable",
    "workday",
    "generic",
}


@dataclass
class AtsDetection:
    ats_type: str
    ats_identifier: str | None
    confidence: str  # high | medium | low
    source: str
    notes: str = ""


def detect_from_url(url: str, *, fetch_page: bool = True) -> AtsDetection:
    """Infer ATS type + identifier from a careers URL (and optionally page HTML)."""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    path = parsed.path or ""
    path_parts = [p for p in path.split("/") if p]

    # --- Direct ATS hosts ---
    if "greenhouse.io" in host:
        token = _greenhouse_token(host, path_parts, parsed.query)
        if token:
            return AtsDetection("greenhouse", token, "high", "url")

    if "lever.co" in host:
        site = path_parts[0] if path_parts else None
        if site and site not in {"api", "v0", "postings"}:
            return AtsDetection("lever", site, "high", "url")

    if "ashbyhq.com" in host:
        board = path_parts[0] if path_parts else None
        if board and board not in {"api", "posting-api", "job-board"}:
            return AtsDetection("ashby", board, "high", "url")

    if "smartrecruiters.com" in host:
        company = path_parts[0] if path_parts else None
        if company and company.lower() not in {"v1", "companies", "api"}:
            return AtsDetection("smartrecruiters", company, "high", "url")

    if "workable.com" in host:
        account = path_parts[0] if path_parts else None
        if account and account not in {"api", "widget", "accounts"}:
            return AtsDetection("workable", account, "high", "url")

    if "myworkdayjobs.com" in host:
        site = _workday_site(path_parts)
        tenant = host.split(".")[0]
        if site:
            identifier = f"{host}|{tenant}|{site}"
            return AtsDetection("workday", identifier, "high", "url")

    # Query-string embeds (common on company career pages)
    qs = parse_qs(parsed.query)
    for key in ("for", "gh_src", "board"):
        if key in qs and qs[key][0]:
            # greenhouse embed style ?for=token
            if "greenhouse" in host or key == "for":
                return AtsDetection("greenhouse", qs[key][0], "medium", "query")

    if not fetch_page:
        return AtsDetection("generic", None, "low", "fallback", "No known ATS pattern in URL")

    # --- Fetch page and sniff embeds / structured data ---
    try:
        response = get(url, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True)
        response.raise_for_status()
        html = response.text
        final_url = response.url
    except Exception as exc:  # noqa: BLE001
        return AtsDetection(
            "generic",
            None,
            "low",
            "fallback",
            f"Could not fetch page for detection: {exc}",
        )

    # Re-run URL detection against redirect target
    redirected = detect_from_url(final_url, fetch_page=False)
    if redirected.ats_type != "generic":
        redirected.source = "redirect"
        return redirected

    sniffed = _detect_from_html(html, base_url=final_url)
    if sniffed:
        return sniffed

    return AtsDetection(
        "generic",
        None,
        "low",
        "fallback",
        "No known ATS detected; will use generic career-page parser",
    )


def resolve_company_ats(
    *,
    career_url: str,
    ats_type: str | None,
    ats_identifier: str | None,
) -> AtsDetection:
    """Fill ATS fields. Explicit values win; otherwise auto-detect from URL/page."""
    explicit_type = (ats_type or "").strip().lower()
    explicit_id = (ats_identifier or "").strip() or None

    if explicit_type in {"", "auto", "detect"}:
        detected = detect_from_url(career_url, fetch_page=True)
        if explicit_id and not detected.ats_identifier:
            detected.ats_identifier = explicit_id
        return detected

    if explicit_type not in ALLOWED_ATS:
        raise ValueError(
            f"ats_type must be one of: {', '.join(sorted(ALLOWED_ATS))} or auto"
        )

    if explicit_id:
        return AtsDetection(explicit_type, explicit_id, "high", "explicit")

    # Type given but no identifier — try to recover identifier from URL/page.
    detected = detect_from_url(career_url, fetch_page=True)
    if detected.ats_type == explicit_type and detected.ats_identifier:
        return AtsDetection(explicit_type, detected.ats_identifier, detected.confidence, "hybrid")

    if explicit_type == "generic":
        return AtsDetection("generic", explicit_id, "medium", "explicit")

    return AtsDetection(explicit_type, explicit_id, "medium", "explicit")


def _greenhouse_token(host: str, path_parts: list[str], query: str) -> str | None:
    qs = parse_qs(query)
    if "for" in qs and qs["for"]:
        return qs["for"][0]
    # boards.greenhouse.io/{token} or job-boards.greenhouse.io/{token}
    if path_parts:
        candidate = path_parts[0]
        if candidate not in {"embed", "jobs", "v1", "boards"}:
            return candidate
    # subdomain style token.greenhouse.io
    sub = host.split(".")[0]
    if sub not in {"boards", "job-boards", "api", "www"}:
        return sub
    return None


def _workday_site(path_parts: list[str]) -> str | None:
    # /en-US/SiteName/... or /SiteName
    parts = [p for p in path_parts if p.lower() not in {"wday", "cxs", "jobs"}]
    if not parts:
        return None
    if re.fullmatch(r"[a-z]{2}-[A-Z]{2}", parts[0]) or parts[0].lower() in {"en-us", "en-gb"}:
        return parts[1] if len(parts) > 1 else None
    return parts[0]


def _detect_from_html(html: str, *, base_url: str) -> AtsDetection | None:
    patterns = [
        (
            "greenhouse",
            r"boards(?:-api)?\.greenhouse\.io/(?:embed/job_board\?for=|v1/boards/)?([a-zA-Z0-9_-]+)",
            "high",
        ),
        (
            "greenhouse",
            r"job-boards\.greenhouse\.io/([a-zA-Z0-9_-]+)",
            "high",
        ),
        (
            "lever",
            r"(?:api|jobs)\.lever\.co/(?:v0/postings/)?([a-zA-Z0-9_-]+)",
            "high",
        ),
        (
            "ashby",
            r"(?:jobs\.ashbyhq\.com|api\.ashbyhq\.com/posting-api/job-board)/([a-zA-Z0-9_-]+)",
            "high",
        ),
        (
            "smartrecruiters",
            r"(?:jobs|api)\.smartrecruiters\.com/(?:v1/companies/)?([a-zA-Z0-9_-]+)",
            "medium",
        ),
        (
            "workable",
            r"apply\.workable\.com/(?:api/v\d+/accounts/)?([a-zA-Z0-9_-]+)",
            "medium",
        ),
        (
            "workday",
            r"(https?://[a-z0-9.-]+\.myworkdayjobs\.com)/[^\s\"']*",
            "medium",
        ),
    ]

    for ats_type, pattern, confidence in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if not match:
            continue
        if ats_type == "workday":
            detected = detect_from_url(match.group(0), fetch_page=False)
            if detected.ats_type == "workday":
                detected.confidence = confidence
                detected.source = "html"
                return detected
            continue
        token = match.group(1)
        if token.lower() in {"embed", "api", "v0", "v1", "postings", "companies", "jobs"}:
            continue
        return AtsDetection(ats_type, token, confidence, "html")

    # JSON-LD presence suggests generic parser can work
    if "JobPosting" in html:
        return AtsDetection(
            "generic",
            None,
            "medium",
            "html",
            f"JobPosting markup found on {base_url}",
        )
    return None
