"""Simulation endpoints."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.api.dependencies import DBSession
from app.models.company import Company
from app.models.simulation import Simulation
from app.models.transaction import Transaction
from app.schemas.simulation_schema import SimulationResponse
from app.services.simulation_engine import run_simulation
from app.utils.preprocess import to_dataframe, transactions_to_records

router = APIRouter(prefix="/simulate", tags=["simulation"])


@router.post("/{company_id}", response_model=SimulationResponse)
def simulate_company(company_id: int, db: DBSession) -> SimulationResponse:
    """Run scenario stress tests."""

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    transactions = db.query(Transaction).filter(Transaction.company_id == company_id).all()
    frame = to_dataframe(transactions_to_records(transactions))
    result = run_simulation(frame)
    db_simulation = Simulation(
        company_id=company_id,
        insolvency_probability=result["insolvency_probability"],
        summary=result["summary"],
        simulation_payload=result["scenarios"],
    )
    db.add(db_simulation)
    db.commit()
    created_at = datetime.utcnow()
    return SimulationResponse(
        company_id=company_id,
        created_at=created_at,
        insolvency_probability=result["insolvency_probability"],
        scenarios=result["scenarios"],
        summary=result["summary"],
    )
