from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import Base, engine
from app.api.companies import router as companies_router
from app.api.jobs import router as jobs_router
from app.api.resume import router as resume_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies_router)
app.include_router(jobs_router)
app.include_router(resume_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/scrape/run")
def run_scrape_now():
    # Intended for local/manual use; scheduled runs happen every 15 minutes.
    results = scrape_all_companies()
    summary = {
        "companies": len(results),
        "fetched": sum(item.get("fetched", 0) for item in results),
        "inserted": sum(item.get("inserted", 0) for item in results),
        "updated": sum(item.get("updated", 0) for item in results),
        "failed": sum(1 for item in results if item.get("status") == "failed"),
    }
    return {"results": results, "summary": summary}
