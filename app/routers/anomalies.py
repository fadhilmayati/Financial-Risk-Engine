"""Anomaly detection endpoints."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.models.transaction import Transaction
from app.services.anomaly_detector import detect_anomalies
from app.utils.preprocess import to_dataframe, transactions_to_records

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.post("/{company_id}")
def detect_company_anomalies(company_id: int, db: Session = Depends(get_db)) -> dict:
    """Detect unusual activities for a company."""

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    transactions = db.query(Transaction).filter(Transaction.company_id == company_id).all()
    frame = to_dataframe(transactions_to_records(transactions))
    result = detect_anomalies(frame)
    result["company_id"] = company_id
    result["generated_at"] = datetime.utcnow().isoformat()
    return result
