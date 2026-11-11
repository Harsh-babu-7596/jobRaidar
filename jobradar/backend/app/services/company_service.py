from datetime import datetime, timezone

from app.scrapers.ashby import AshbyScraper
from app.scrapers.custom import CustomScraper
from app.scrapers.generic import GenericCareerScraper
from app.scrapers.greenhouse import GreenhouseScraper
from app.scrapers.lever import LeverScraper
from app.scrapers.smartrecruiters import SmartRecruitersScraper
from app.scrapers.workable import WorkableScraper
from app.scrapers.workday import WorkdayScraper
from app.services.ats_detect import detect_from_url
from app.services.job_service import upsert_jobs

SCRAPERS = {
    "greenhouse": GreenhouseScraper(),
    "lever": LeverScraper(),
    "ashby": AshbyScraper(),
    "smartrecruiters": SmartRecruitersScraper(),
    "workable": WorkableScraper(),
    "workday": WorkdayScraper(),
    "generic": GenericCareerScraper(),
    "custom": CustomScraper(),  # alias of generic
}


def scrape_company(db, company) -> dict:
    ats_type = (company.ats_type or "").lower()
    upgraded = None

    # If company was saved as generic/custom, try to discover a better ATS at scrape time.
    if ats_type in {"generic", "custom", ""}:
        detected = detect_from_url(company.career_url, fetch_page=True)
        if detected.ats_type in SCRAPERS and detected.ats_type not in {"generic", "custom"}:
            company.ats_type = detected.ats_type
            if detected.ats_identifier:
                company.ats_identifier = detected.ats_identifier
            ats_type = detected.ats_type
            upgraded = detected

    scraper = SCRAPERS.get(ats_type)
    if scraper is None:
        raise ValueError(f"Unsupported ATS type: {company.ats_type}")

    jobs = scraper.fetch_jobs(company)
    inserted, updated = upsert_jobs(db, company, jobs)
    company.last_scraped_at = datetime.now(timezone.utc)
    db.commit()

    result = {
        "company": company.name,
        "fetched": len(jobs),
        "inserted": inserted,
        "updated": updated,
        "status": "success",
        "ats_type": company.ats_type,
        "ats_identifier": company.ats_identifier,
    }
    if upgraded:
        result["detected_ats"] = upgraded.ats_type
        result["detection_source"] = upgraded.source
    return result
