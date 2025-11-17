"""Utility helpers for preprocessing financial data."""
from __future__ import annotations

from typing import Iterable, List

import pandas as pd


def to_dataframe(records: Iterable[dict]) -> pd.DataFrame:
    """Convert iterable of transaction dicts into a cleaned DataFrame."""

    frame = pd.DataFrame(list(records))
    if frame.empty:
        return frame
    frame["transaction_date"] = pd.to_datetime(frame["transaction_date"])
    frame["amount"] = pd.to_numeric(frame["amount"])
    frame.sort_values("transaction_date", inplace=True)
    frame.reset_index(drop=True, inplace=True)
    return frame


def remove_duplicates(frame: pd.DataFrame, subset: List[str] | None = None) -> pd.DataFrame:
    """Drop duplicate rows based on provided subset."""

    subset = subset or ["unique_id"]
    return frame.drop_duplicates(subset=subset)


def transactions_to_records(transactions: Iterable[object]) -> list[dict]:
    """Serialize SQLAlchemy transaction objects into plain dictionaries."""

    records: list[dict] = []
    for txn in transactions:
        records.append(
            {
                "unique_id": txn.unique_id,
                "amount": float(txn.amount),
                "category": txn.category,
                "description": txn.description,
                "currency": txn.currency,
                "transaction_date": txn.transaction_date,
            }
        )
    return records
