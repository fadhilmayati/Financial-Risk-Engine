"""Pydantic schemas for transactions."""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    unique_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., description="Transaction amount")
    category: str = Field(..., description="Transaction category")
    description: Optional[str] = Field(default=None)
    currency: str = Field(default="USD")
    transaction_date: date


class TransactionCreate(TransactionBase):
    company_id: int


class TransactionResponse(TransactionBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True


class TransactionIngestRequest(BaseModel):
    company_id: int
    records: List[TransactionBase]
