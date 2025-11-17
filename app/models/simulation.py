"""Simulation ORM model."""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class Simulation(Base):
    """Stores simulation results for a company."""

    __tablename__ = "simulations"

    id: int = Column(Integer, primary_key=True, index=True)
    company_id: int = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    insolvency_probability: float = Column(Float, nullable=False)
    summary: str = Column(JSON, nullable=False)
    simulation_payload: dict = Column(JSON, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="simulations")
