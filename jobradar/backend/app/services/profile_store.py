from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import DATA_DIR

PROFILE_PATH = DATA_DIR / "profile.json"


def _empty_profile() -> dict[str, Any]:
    return {
        "keywords": [],
        "resume_filename": None,
        "updated_at": None,
    }


def load_profile() -> dict[str, Any]:
    if not PROFILE_PATH.exists():
        return _empty_profile()
    try:
        data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _empty_profile()
    if not isinstance(data, dict):
        return _empty_profile()
    data.setdefault("keywords", [])
    data.setdefault("resume_filename", None)
    data.setdefault("updated_at", None)
    return data


def save_profile(
    *,
    keywords: list[str],
    resume_filename: str | None = None,
) -> dict[str, Any]:
    current = load_profile()
    cleaned = _clean_keywords(keywords)
    profile = {
        "keywords": cleaned,
        "resume_filename": resume_filename
        if resume_filename is not None
        else current.get("resume_filename"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    PROFILE_PATH.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    return profile


def _clean_keywords(keywords: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in keywords:
        item = " ".join(str(raw).split()).strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out
