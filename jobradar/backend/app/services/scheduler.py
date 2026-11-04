import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select
from app.database.connection import SessionLocal
from app.database.models import Company
from app.services.company_service import scrape_company
from app.config import SCRAPE_INTERVAL_MINUTES

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone="UTC")

def scrape_all_companies():
    db = SessionLocal()
    try:
        companies = db.scalars(
            select(Company).where(Company.active.is_(True))
        ).all()
        for company in companies:
            try:
                result = scrape_company(db, company)
                logger.info("Scrape result: %s", result)
            except Exception:
                db.rollback()
                logger.exception("Failed scraping %s", company.name)
    finally:
        db.close()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            scrape_all_companies,
            "interval",
            minutes=SCRAPE_INTERVAL_MINUTES,
            id="company_scrape",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()
