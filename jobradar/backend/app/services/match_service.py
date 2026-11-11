from __future__ import annotations

import html
import re
from typing import Any


def _plain(text: str | None) -> str:
    if not text:
        return ""
    unescaped = html.unescape(text)
    unescaped = re.sub(r"<[^>]+>", " ", unescaped)
    return re.sub(r"\s+", " ", unescaped).strip().lower()


def score_job(job: Any, keywords: list[str]) -> tuple[float, list[str]]:
    """Return (score, matched_keywords). Title hits weigh more than description."""
    if not keywords:
        return 0.0, []

    title = _plain(getattr(job, "title", None))
    location = _plain(getattr(job, "location", None))
    description = _plain(getattr(job, "description", None))

    matched: list[str] = []
    score = 0.0

    for keyword in keywords:
        needle = keyword.lower().strip()
        if not needle:
            continue
        hit = False
        if needle in title:
            score += 3.0
            hit = True
        if needle in location:
            score += 0.5
            hit = True
        if needle in description:
            score += 1.0
            hit = True
        if hit:
            matched.append(keyword)

    return score, matched


def rank_jobs(jobs: list[Any], keywords: list[str], *, limit: int = 100) -> list[dict]:
    ranked: list[tuple[float, list[str], Any]] = []
    for job in jobs:
        score, matched = score_job(job, keywords)
        if score <= 0:
            continue
        ranked.append((score, matched, job))

    ranked.sort(
        key=lambda item: (
            -item[0],
            -(item[2].first_seen_at.timestamp() if item[2].first_seen_at else 0.0),
        )
    )

    results: list[dict] = []
    for score, matched, job in ranked[:limit]:
        results.append(
            {
                "id": job.id,
                "company": job.company.name,
                "title": job.title,
                "location": job.location,
                "description": job.description,
                "apply_url": job.apply_url,
                "posted_at": job.posted_at,
                "first_seen_at": job.first_seen_at,
                "active": job.active,
                "match_score": round(score, 2),
                "matched_keywords": matched,
            }
        )
    return results
