from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from app.database.connection import Base, engine
from app.api.companies import router as companies_router
from app.api.jobs import router as jobs_router
from app.services.scheduler import start_scheduler, scheduler, scrape_all_companies
from app.config import LOG_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "jobradar.log", encoding="utf-8"), logging.StreamHandler()],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)

app = FastAPI(
    title="JobRadar API",
    description="Local job discovery and career-page monitoring service",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(companies_router)
app.include_router(jobs_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/scrape/run")
def run_scrape_now():
    # Intended for local/manual use; scheduled runs happen every 15 minutes.
    scrape_all_companies()
    return {"message": "Scrape cycle completed. Check backend logs for per-company results."}
