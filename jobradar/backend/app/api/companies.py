from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, HttpUrl, ConfigDict, ValidationError, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Company
from app.services.ats_detect import ALLOWED_ATS, detect_from_url, resolve_company_ats
from app.services.excel_import import build_template_bytes, parse_companies_workbook

router = APIRouter(prefix="/api/companies", tags=["companies"])


class CompanyCreate(BaseModel):
    name: str
    career_url: HttpUrl
    ats_type: str | None = "auto"
    ats_identifier: str | None = None
    active: bool = True

    @field_validator("ats_type")
    @classmethod
    def normalize_ats_type(cls, value: str | None) -> str:
        if value is None or not str(value).strip():
            return "auto"
        return str(value).strip().lower()


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    career_url: str
    ats_type: str
    ats_identifier: str | None
    active: bool
    last_scraped_at: datetime | None = None


class CompanyImportResult(BaseModel):
    created: int
    updated: int
    skipped: int
    total_rows: int
    errors: list[str] = []


class DetectRequest(BaseModel):
    career_url: HttpUrl


class DetectResponse(BaseModel):
    ats_type: str
    ats_identifier: str | None
    confidence: str
    source: str
    notes: str = ""


@router.post("/detect", response_model=DetectResponse)
def detect_company_ats(payload: DetectRequest):
    detected = detect_from_url(str(payload.career_url), fetch_page=True)
    return DetectResponse(
        ats_type=detected.ats_type,
        ats_identifier=detected.ats_identifier,
        confidence=detected.confidence,
        source=detected.source,
        notes=detected.notes,
    )


@router.post("", response_model=CompanyOut)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    try:
        resolved = resolve_company_ats(
            career_url=str(payload.career_url),
            ats_type=payload.ats_type,
            ats_identifier=payload.ats_identifier,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    existing = db.scalar(select(Company).where(Company.name == payload.name))
    if existing:
        raise HTTPException(409, "Company already exists")

    company = Company(
        name=payload.name,
        career_url=str(payload.career_url),
        ats_type=resolved.ats_type,
        ats_identifier=resolved.ats_identifier,
        active=payload.active,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.scalars(select(Company).order_by(Company.name)).all()


@router.get("/template.xlsx")
def download_companies_template():
    content = build_template_bytes()
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="jobradar_companies_template.xlsx"'},
    )


@router.post("/import", response_model=CompanyImportResult)
async def import_companies_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(400, "Upload an Excel .xlsx file")

    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty")

    try:
        rows = parse_companies_workbook(data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, f"Could not parse Excel file: {exc}") from exc

    created = updated = skipped = 0
    errors: list[str] = []

    for row in rows:
        try:
            payload = CompanyCreate(
                name=row["name"],
                career_url=row["career_url"],
                ats_type=row.get("ats_type") or "auto",
                ats_identifier=row.get("ats_identifier"),
                active=row.get("active", True),
            )
            resolved = resolve_company_ats(
                career_url=str(payload.career_url),
                ats_type=payload.ats_type,
                ats_identifier=payload.ats_identifier,
            )
            if resolved.ats_type not in ALLOWED_ATS:
                raise ValueError(f"Unsupported ats_type: {resolved.ats_type}")
        except (ValidationError, ValueError) as exc:
            skipped += 1
            errors.append(f"{row.get('name', '?')}: {exc}")
            continue

        existing = db.scalar(select(Company).where(Company.name == payload.name))
        if existing:
            existing.career_url = str(payload.career_url)
            existing.ats_type = resolved.ats_type
            existing.ats_identifier = resolved.ats_identifier
            existing.active = payload.active
            updated += 1
        else:
            db.add(
                Company(
                    name=payload.name,
                    career_url=str(payload.career_url),
                    ats_type=resolved.ats_type,
                    ats_identifier=resolved.ats_identifier,
                    active=payload.active,
                )
            )
            created += 1

    db.commit()
    return CompanyImportResult(
        created=created,
        updated=updated,
        skipped=skipped,
        total_rows=len(rows),
        errors=errors[:20],
    )
