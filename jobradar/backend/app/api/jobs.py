from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.database.connection import get_db
from app.database.models import Job
from app.services.match_service import rank_jobs
from app.services.profile_store import load_profile

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _serialize_job(job: Job) -> dict:
    return {
        "id": job.id,
        "company": job.company.name,
        "title": job.title,
        "location": job.location,
        "description": job.description,
        "apply_url": job.apply_url,
        "posted_at": job.posted_at,
        "first_seen_at": job.first_seen_at,
        "active": job.active,
        "match_score": None,
        "matched_keywords": [],
    }


@router.get("")
def list_jobs(
    search: str | None = None,
    location: str | None = None,
    active: bool = True,
    match: bool = Query(
        default=False,
        description="When true, rank/filter jobs using saved resume keywords",
    ),
    keywords: str | None = Query(
        default=None,
        description="Optional comma-separated keywords override for this request",
    ),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Job).options(joinedload(Job.company)).where(Job.active == active)
    if search:
        stmt = stmt.where(Job.title.ilike(f"%{search}%"))
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))

    # Pull a wider candidate set when matching so ranking has room to work.
    fetch_limit = 2000 if match else limit
    jobs = db.scalars(stmt.order_by(Job.first_seen_at.desc()).limit(fetch_limit)).unique().all()

    if not match:
        return [_serialize_job(job) for job in jobs[:limit]]

    if keywords is not None:
        keyword_list = [part.strip() for part in keywords.split(",") if part.strip()]
    else:
        keyword_list = list(load_profile().get("keywords") or [])

    if not keyword_list:
        return {
            "jobs": [],
            "keywords_used": [],
            "message": "No keywords set. Upload a resume or add keywords first.",
        }

    ranked = rank_jobs(jobs, keyword_list, limit=limit)
    return {
        "jobs": ranked,
        "keywords_used": keyword_list,
        "matched": len(ranked),
        "scanned": len(jobs),
    }
