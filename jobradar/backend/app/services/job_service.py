from datetime import datetime, timezone
from sqlalchemy import select
from app.database.models import Job

def upsert_jobs(db, company, scraped_jobs: list[dict]) -> tuple[int, int]:
    inserted = 0
    updated = 0
    now = datetime.now(timezone.utc)

    for item in scraped_jobs:
        external_id = item.get("external_job_id")
        if not external_id:
            continue

        job = db.scalar(select(Job).where(
            Job.company_id == company.id,
            Job.external_job_id == str(external_id),
        ))

        if job is None:
            job = Job(
                company_id=company.id,
                external_job_id=str(external_id),
                title=item.get("title") or "Untitled",
                location=item.get("location"),
                description=item.get("description"),
                apply_url=item.get("apply_url") or "",
                posted_at=str(item.get("posted_at")) if item.get("posted_at") else None,
                first_seen_at=now,
                last_seen_at=now,
                active=True,
            )
            db.add(job)
            inserted += 1
        else:
            job.title = item.get("title") or job.title
            job.location = item.get("location")
            job.description = item.get("description")
            job.apply_url = item.get("apply_url") or job.apply_url
            job.posted_at = str(item.get("posted_at")) if item.get("posted_at") else job.posted_at
            job.last_seen_at = now
            job.active = True
            updated += 1

    db.commit()
    return inserted, updated
