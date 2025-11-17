"""Risk report schemas."""
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class RiskScore(BaseModel):
    metric: str
    score: float
    description: str


class RiskReportBase(BaseModel):
    company_id: int
    survival_probability: float
    heatmap: Dict[str, float]
    summary: str
    report_payload: Dict[str, float]


class RiskReportResponse(RiskReportBase):
    id: int
    created_at: datetime
    scores: List[RiskScore]

    class Config:
        orm_mode = True


class RiskRequest(BaseModel):
    company_id: int
