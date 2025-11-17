"""Database model for companies."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class Company(Base):
    """Represents a company tracked by the risk engine."""

    __tablename__ = "companies"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(255), unique=True, nullable=False)
    industry: str = Column(String(255), nullable=True)
    liquidity_ratio: float = Column(Numeric(10, 4), nullable=True)
    burn_rate: float = Column(Numeric(12, 2), nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="company", cascade="all, delete-orphan")
    risk_reports = relationship("RiskReport", back_populates="company", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="company", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="company", cascade="all, delete-orphan")
