#backend/api/v1/records_api.py
# UTF-8
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models.records import (
    PendingRecord,
    PendingRecordSchema,
    ArchiveRecord,
    ArchiveRecordSchema,
    ApproveRecordRequest,
)


router = APIRouter(prefix="/api/v1/records", tags=["records"])


# ---------- Pydantic Schemas ----------

class RecordBase(BaseModel):
    id: int
    status: str
    file_path: str

    artist: Optional[str] = None
    album: Optional[str] = None
    label: Optional[str] = None
    catalog_number: Optional[str] = None
    year: Optional[str] = None
    format: Optional[str] = None
    country: Optional[str] = None
    genre: Optional[str] = None
    style: Optional[str] = None

    media_condition: Optional[str] = None
    sleeve_condition: Optional[str] = None
    sale_price: Optional[float] = None
    currency: Optional[str] = None
    for_sale: Optional[int] = None

    ocr_text: Optional[str] = None
    fingerprint_json: Optional[str] = None
    metadata_json: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class RecordUpdate(BaseModel):
    artist: Optional[str] = None
    album: Optional[str] = None
    label: Optional[str] = None
    catalog_number: Optional[str] = None
    year: Optional[str] = None
    format: Optional[str] = None
    country: Optional[str] = None
    genre: Optional[str] = None
    style: Optional[str] = None

    media_condition: Optional[str] = None
    sleeve_condition: Optional[str] = None
    sale_price: Optional[float] = None
    currency: Optional[str] = None
    for_sale: Optional[int] = Field(default=None)

    notes: Optional[str] = None
    status: Optional[str] = Field(default=None, description="PENDING / APPROVED / REJECTED")


# ---------- Endpoints ----------

@router.get("/", response_model=List[RecordBase])
def list_records(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Record)

    if user_id is not None:
        query = query.filter(Record.user_id == user_id)

    if status is not None:
        query = query.filter(Record.status == status)

    return query.order_by(Record.created_at.desc()).all()


@router.get("/pending", response_model=List[RecordBase])
def list_pending_records(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Record).filter(Record.status == "PENDING")
    if user_id is not None:
        query = query.filter(Record.user_id == user_id)
    return query.order_by(Record.created_at.desc()).all()


@router.get("/{record_id}", response_model=RecordBase)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.put("/{record_id}", response_model=RecordBase)
def update_record(record_id: int, payload: RecordUpdate, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/{record_id}/approve", response_model=RecordBase)
def approve_record(record_id: int, payload: RecordUpdate, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)

    record.status = "APPROVED"

    db.add(record)
    db.commit()
    db.refresh(record)
    return record
