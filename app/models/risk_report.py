"""Risk report ORM model."""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class RiskReport(Base):
    """Stores computed risk metrics for a company."""

    __tablename__ = "risk_reports"

    id: int = Column(Integer, primary_key=True, index=True)
    company_id: int = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    survival_probability: float = Column(Float, nullable=False)
    heatmap: dict = Column(JSON, nullable=False)
    summary: str = Column(String(2048), nullable=False)
    report_payload: dict = Column(JSON, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="risk_reports")
