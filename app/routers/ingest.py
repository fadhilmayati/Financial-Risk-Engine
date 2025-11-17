"""Transaction ingestion endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.models.transaction import Transaction
from app.schemas.transaction_schema import TransactionIngestRequest, TransactionResponse
from app.utils.preprocess import remove_duplicates, to_dataframe
from app.utils.validators import ensure_positive_amounts

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/transactions", response_model=list[TransactionResponse])
def ingest_transactions(payload: TransactionIngestRequest, db: Session = Depends(get_db)) -> list[TransactionResponse]:
    """Clean, validate, deduplicate, and persist transactions."""

    company = db.query(Company).filter(Company.id == payload.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    ensure_positive_amounts(record.model_dump() for record in payload.records)
    frame = to_dataframe([record.model_dump() for record in payload.records])
    frame = remove_duplicates(frame)
    responses: list[TransactionResponse] = []
    for record in frame.to_dict(orient="records"):
        existing = db.query(Transaction).filter(Transaction.unique_id == record["unique_id"]).first()
        if existing:
            continue
        transaction = Transaction(
            company_id=payload.company_id,
            unique_id=record["unique_id"],
            amount=record["amount"],
            category=record["category"],
            description=record.get("description"),
            currency=record.get("currency", "USD"),
            transaction_date=record["transaction_date"],
        )
        db.add(transaction)
        db.flush()
        responses.append(TransactionResponse.model_validate(transaction))
    db.commit()
    return responses
