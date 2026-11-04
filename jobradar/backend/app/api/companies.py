from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Company

router = APIRouter(prefix="/api/companies", tags=["companies"])

class CompanyCreate(BaseModel):
    name: str
    career_url: HttpUrl
    ats_type: str
    ats_identifier: str | None = None
    active: bool = True

class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    career_url: str
    ats_type: str
    ats_identifier: str | None
    active: bool

@router.post("", response_model=CompanyOut)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    ats = payload.ats_type.lower()
    if ats not in {"greenhouse", "lever", "custom"}:
        raise HTTPException(400, "ats_type must be greenhouse, lever, or custom")
    existing = db.scalar(select(Company).where(Company.name == payload.name))
    if existing:
        raise HTTPException(409, "Company already exists")
    company = Company(
        name=payload.name,
        career_url=str(payload.career_url),
        ats_type=ats,
        ats_identifier=payload.ats_identifier,
        active=payload.active,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.scalars(select(Company).order_by(Company.name)).all()
