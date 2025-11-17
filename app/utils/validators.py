"""Validation helpers."""
from typing import Iterable


def ensure_positive_amounts(records: Iterable[dict]) -> None:
    """Ensure no transaction contains a zero or missing amount."""

    for record in records:
        amount = record.get("amount")
        if amount is None or float(amount) == 0:
            msg = f"Invalid transaction amount for record {record.get('unique_id')}"
            raise ValueError(msg)
