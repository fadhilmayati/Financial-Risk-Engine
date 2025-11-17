"""Transaction model definition."""
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class Transaction(Base):
    """Represents a financial transaction."""

    __tablename__ = "transactions"

    id: int = Column(Integer, primary_key=True, index=True)
    company_id: int = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    unique_id: str = Column(String(255), unique=True, nullable=False)
    amount: float = Column(Numeric(14, 2), nullable=False)
    category: str = Column(String(255), nullable=False)
    description: str = Column(String(1024), nullable=True)
    currency: str = Column(String(10), default="USD")
    transaction_date: datetime = Column(Date, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="transactions")
