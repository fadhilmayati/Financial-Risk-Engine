"""Simulation schemas."""
from datetime import datetime
from typing import Dict

from pydantic import BaseModel


class SimulationResponse(BaseModel):
    company_id: int
    created_at: datetime
    insolvency_probability: float
    scenarios: Dict[str, float]
    summary: Dict[str, str]
