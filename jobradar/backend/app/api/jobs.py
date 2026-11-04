from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.database.connection import get_db
from app.database.models import Job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("")
def list_jobs(
    search: str | None = None,
    location: str | None = None,
    active: bool = True,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Job).options(joinedload(Job.company)).where(Job.active == active)
    if search:
        stmt = stmt.where(Job.title.ilike(f"%{search}%"))
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    jobs = db.scalars(stmt.order_by(Job.first_seen_at.desc()).limit(limit)).unique().all()
    return [{
        "id": job.id,
        "company": job.company.name,
        "title": job.title,
        "location": job.location,
        "apply_url": job.apply_url,
        "posted_at": job.posted_at,
        "first_seen_at": job.first_seen_at,
        "active": job.active,
    } for job in jobs]
