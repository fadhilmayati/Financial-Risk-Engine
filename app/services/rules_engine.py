"""Rules engine evaluations."""
from __future__ import annotations

from typing import List

import pandas as pd
from pydantic import BaseModel


class RuleEvaluation(BaseModel):
    name: str
    triggered: bool
    description: str


def evaluate_rules(frame: pd.DataFrame) -> List[RuleEvaluation]:
    """Run deterministic rule checks and return their evaluations."""

    if frame.empty:
        return []
    total_revenue = frame[frame["amount"] > 0]["amount"].sum()
    total_expense = frame[frame["amount"] < 0]["amount"].abs().sum()
    liquidity_ratio = float(total_revenue / (total_expense + 1e-9)) if total_expense else 2.0
    rent_utilities = frame[frame["category"].isin(["rent", "utilities"])]
    rent_ratio = float(rent_utilities["amount"].abs().sum() / (total_expense + 1e-9)) if total_expense else 0.0
    subscription_creep = frame[frame["category"] == "subscriptions"]["amount"].abs().rolling(window=3, min_periods=1).mean()
    margin = float((total_revenue - total_expense) / (total_revenue + 1e-9)) if total_revenue else -1.0
    debtor_overdue = frame[(frame["category"] == "accounts_receivable") & (frame["transaction_date"] < pd.Timestamp.utcnow() - pd.Timedelta(days=60))]
    return [
        RuleEvaluation(name="liquidity_ratio", triggered=liquidity_ratio < 1.2, description="Liquidity ratio below safe threshold"),
        RuleEvaluation(name="rent_utilities", triggered=rent_ratio > 0.3, description="Rent/utility spend too high"),
        RuleEvaluation(name="subscription_creep", triggered=bool((subscription_creep.diff() > 1000).any()), description="Subscriptions growing rapidly"),
        RuleEvaluation(name="margin_compression", triggered=margin < 0.2, description="Gross margin compression"),
        RuleEvaluation(name="debtor_overdue", triggered=not debtor_overdue.empty, description="Overdue debtor pattern"),
    ]
