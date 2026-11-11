from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services.profile_store import load_profile, save_profile
from app.services.resume_service import extract_keywords, extract_text_from_bytes, normalize_text

router = APIRouter(prefix="/api/resume", tags=["resume"])


class ProfileOut(BaseModel):
    keywords: list[str]
    resume_filename: str | None = None
    updated_at: str | None = None


class KeywordsUpdate(BaseModel):
    keywords: list[str] = Field(default_factory=list)


@router.get("/profile", response_model=ProfileOut)
def get_profile():
    return load_profile()


@router.put("/keywords", response_model=ProfileOut)
def update_keywords(payload: KeywordsUpdate):
    return save_profile(keywords=payload.keywords)


@router.post("/upload", response_model=ProfileOut)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Filename is required")

    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty")
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(400, "Resume must be 8MB or smaller")

    try:
        text = extract_text_from_bytes(file.filename, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - surface parse failures cleanly
        raise HTTPException(400, f"Could not read resume: {exc}") from exc

    text = normalize_text(text)
    if len(text) < 40:
        raise HTTPException(400, "Could not extract enough text from the resume")

    keywords = extract_keywords(text)
    if not keywords:
        raise HTTPException(
            400,
            "No keywords detected. Try a text-heavy resume or set keywords manually.",
        )

    return save_profile(keywords=keywords, resume_filename=file.filename)
