"""Forecast ORM model."""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class Forecast(Base):
    """Stores forecasting outputs for a company."""

    __tablename__ = "forecasts"

    id: int = Column(Integer, primary_key=True, index=True)
    company_id: int = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    horizon_days: int = Column(Integer, nullable=False)
    revenue_projection: float = Column(Float, nullable=False)
    expense_projection: float = Column(Float, nullable=False)
    runway_days: int = Column(Integer, nullable=False)
    forecast_payload: dict = Column(JSON, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="forecasts")
