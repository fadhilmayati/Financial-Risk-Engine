"""Forecast response schemas."""
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class ForecastHorizon(BaseModel):
    horizon_days: int
    revenue_projection: float
    expense_projection: float
    runway_days: int


class ForecastResponse(BaseModel):
    company_id: int
    created_at: datetime
    horizons: List[ForecastHorizon]
    model_used: str
    metadata: Dict[str, float]
