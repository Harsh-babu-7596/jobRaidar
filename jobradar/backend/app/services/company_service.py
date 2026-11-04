from app.scrapers.greenhouse import GreenhouseScraper
from app.scrapers.lever import LeverScraper
from app.scrapers.custom import CustomScraper
from app.services.job_service import upsert_jobs

SCRAPERS = {
    "greenhouse": GreenhouseScraper(),
    "lever": LeverScraper(),
    "custom": CustomScraper(),
}

def scrape_company(db, company) -> dict:
    scraper = SCRAPERS.get(company.ats_type.lower())
    if scraper is None:
        raise ValueError(f"Unsupported ATS type: {company.ats_type}")

    jobs = scraper.fetch_jobs(company)
    inserted, updated = upsert_jobs(db, company, jobs)
    from datetime import datetime, timezone
    company.last_scraped_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "company": company.name,
        "fetched": len(jobs),
        "inserted": inserted,
        "updated": updated,
        "status": "success",
    }
