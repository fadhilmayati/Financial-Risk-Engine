"""Forecast endpoints."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.api.dependencies import DBSession
from app.models.company import Company
from app.models.forecast import Forecast
from app.models.transaction import Transaction
from app.schemas.forecast_schema import ForecastResponse
from app.services.forecasting import forecast_financials
from app.utils.preprocess import to_dataframe, transactions_to_records

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.post("/{company_id}", response_model=ForecastResponse)
def create_forecast(company_id: int, db: DBSession) -> ForecastResponse:
    """Generate forecasts and persist summary."""

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    transactions = db.query(Transaction).filter(Transaction.company_id == company_id).all()
    frame = to_dataframe(transactions_to_records(transactions))
    result = forecast_financials(frame)
    horizons = []
    for horizon in result["horizons"]:
        db_forecast = Forecast(
            company_id=company_id,
            horizon_days=horizon["horizon_days"],
            revenue_projection=horizon["revenue_projection"],
            expense_projection=horizon["expense_projection"],
            runway_days=horizon["runway_days"],
            forecast_payload=result["metadata"],
        )
        db.add(db_forecast)
        horizons.append(horizon)
    db.commit()
    created_at = datetime.utcnow()
    return ForecastResponse(company_id=company_id, created_at=created_at, horizons=horizons, model_used=result["model_used"], metadata=result["metadata"])
