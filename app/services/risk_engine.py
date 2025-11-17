"""Core financial risk engine logic."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from app.services.rules_engine import RuleEvaluation, evaluate_rules
from app.services.llm_explainer import LLMProvider, explain_risk


@dataclass
class RiskComponent:
    """Represents a component risk score."""

    name: str
    score: float
    description: str


def _normalize_score(raw_score: float) -> float:
    return float(np.clip(raw_score, 0, 100))


def _cashflow_volatility(frame: pd.DataFrame) -> float:
    return frame["amount"].std() * 0.1 if not frame.empty else 10.0


def _burn_rate_detection(frame: pd.DataFrame) -> float:
    expenses = frame[frame["amount"] < 0]["amount"].abs().sum()
    revenue = frame[frame["amount"] > 0]["amount"].sum()
    burn_rate = expenses - revenue
    return float(max(0.0, min(100.0, burn_rate / 1000)))


def _debtor_aging_risk(frame: pd.DataFrame) -> float:
    receivables = frame[frame["category"] == "accounts_receivable"]
    if receivables.empty:
        return 15.0
    overdue = receivables[receivables["transaction_date"] < receivables["transaction_date"].max() - pd.Timedelta(days=45)]
    ratio = len(overdue) / len(receivables)
    return float(ratio * 100)


def _vendor_concentration(frame: pd.DataFrame) -> float:
    vendor_counts = frame[frame["amount"] < 0]["category"].value_counts(normalize=True)
    if vendor_counts.empty:
        return 5.0
    concentration = vendor_counts.max()
    return float(concentration * 100)


def _seasonality_adjustment(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 10.0
    monthly = frame.groupby(frame["transaction_date"].dt.to_period("M"))["amount"].sum()
    return float(np.std(monthly) / (np.mean(monthly) + 1e-9) * 100)


def _survival_probability(scores: List[RiskComponent], rules: List[RuleEvaluation]) -> float:
    penalty = np.mean([component.score for component in scores]) if scores else 10.0
    rule_penalty = sum(10 for rule in rules if rule.triggered)
    survival = 100 - penalty - rule_penalty
    return float(np.clip(survival, 0, 100))


def generate_risk_report(
    frame: pd.DataFrame,
    metadata: Dict[str, str] | None = None,
    explainer: LLMProvider | None = None,
) -> Dict[str, object]:
    """Return the computed risk report payload."""

    metadata = metadata or {}
    components = [
        RiskComponent("cashflow_volatility", _normalize_score(_cashflow_volatility(frame)), "Std-dev of daily net cash."),
        RiskComponent("burn_rate", _normalize_score(_burn_rate_detection(frame)), "Difference between expenses and revenue."),
        RiskComponent("debtor_aging", _normalize_score(_debtor_aging_risk(frame)), "Receivables overdue risk."),
        RiskComponent("vendor_concentration", _normalize_score(_vendor_concentration(frame)), "Dependence on a single vendor."),
        RiskComponent("seasonality", _normalize_score(_seasonality_adjustment(frame)), "Variability of monthly cashflows."),
    ]
    rules = evaluate_rules(frame)
    survival_probability = _survival_probability(components, rules)
    heatmap = {component.name: component.score for component in components}
    report_payload = {
        "metadata": metadata,
        "rules": [rule.model_dump() for rule in rules],
        "survival_probability": survival_probability,
    }
    summary_payload = {
        "metadata": metadata,
        "components": [component.__dict__ for component in components],
        "rules": [rule.model_dump() for rule in rules],
        "survival_probability": survival_probability,
    }
    summary = explain_risk(summary_payload, provider=explainer)
    return {
        "components": components,
        "rules": rules,
        "survival_probability": survival_probability,
        "heatmap": heatmap,
        "summary": summary,
        "report_payload": report_payload,
    }
