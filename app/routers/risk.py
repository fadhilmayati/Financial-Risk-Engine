"""Risk engine endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.models.risk_report import RiskReport
from app.models.transaction import Transaction
from app.schemas.risk_schema import RiskReportResponse
from app.services.risk_engine import generate_risk_report
from app.utils.preprocess import to_dataframe, transactions_to_records

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/report/{company_id}", response_model=RiskReportResponse)
def create_risk_report(company_id: int, db: Session = Depends(get_db)) -> RiskReportResponse:
    """Compute risk scores for a company and persist the report."""

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    transactions = db.query(Transaction).filter(Transaction.company_id == company_id).all()
    frame = to_dataframe(transactions_to_records(transactions))
    report = generate_risk_report(frame, metadata={"company": company.name})
    db_report = RiskReport(
        company_id=company_id,
        survival_probability=report["survival_probability"],
        heatmap=report["heatmap"],
        summary=report["summary"],
        report_payload=report["report_payload"],
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return RiskReportResponse(
        id=db_report.id,
        company_id=company_id,
        survival_probability=db_report.survival_probability,
        heatmap=db_report.heatmap,
        summary=db_report.summary,
        report_payload=db_report.report_payload,
        created_at=db_report.created_at,
        scores=[{"metric": component.name, "score": component.score, "description": component.description} for component in report["components"]],
    )
