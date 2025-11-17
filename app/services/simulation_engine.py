"""Monte Carlo style simulation engine."""
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


class SimulationResult(Dict[str, object]):
    """Dictionary payload for simulation results."""


def run_simulation(frame: pd.DataFrame, iterations: int = 1000) -> SimulationResult:
    """Execute scenario stress tests for a company."""

    if frame.empty:
        base_cash = 0.0
    else:
        base_cash = float(frame["amount"].sum())
    rng = np.random.default_rng(seed=42)
    insolvency_hits = 0
    scenario_aggregates = {"sales_drop": 0.0, "expense_spike": 0.0, "debtor_delay": 0.0, "supplier_disruption": 0.0, "payroll_increase": 0.0}
    for _ in range(iterations):
        sales_drop = rng.normal(0.85, 0.05)
        expense_spike = rng.normal(1.2, 0.1)
        debtor_delay = rng.uniform(0.8, 1.0)
        supplier_disruption = rng.uniform(0.9, 1.05)
        payroll_increase = rng.normal(1.1, 0.02)
        cash_flow = base_cash * sales_drop - base_cash * (expense_spike - 1) - (1 - debtor_delay) * 5000
        cash_flow -= (supplier_disruption - 1) * 3000
        cash_flow -= (payroll_increase - 1) * 4000
        if cash_flow < 0:
            insolvency_hits += 1
        scenario_aggregates["sales_drop"] += sales_drop
        scenario_aggregates["expense_spike"] += expense_spike
        scenario_aggregates["debtor_delay"] += debtor_delay
        scenario_aggregates["supplier_disruption"] += supplier_disruption
        scenario_aggregates["payroll_increase"] += payroll_increase
    insolvency_probability = insolvency_hits / iterations
    avg_scenarios = {key: value / iterations for key, value in scenario_aggregates.items()}
    summary = {
        "insolvency_probability": insolvency_probability,
        "stress_test": "Significant" if insolvency_probability > 0.3 else "Moderate",
    }
    return SimulationResult({"insolvency_probability": insolvency_probability, "scenarios": avg_scenarios, "summary": summary})
