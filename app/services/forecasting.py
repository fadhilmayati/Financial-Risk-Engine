"""Forecasting service using ARIMA/ETS approaches."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class ForecastResult(Dict[str, object]):
    """Dictionary wrapper for forecast payload."""


def _prepare_series(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        idx = pd.date_range(end=pd.Timestamp.utcnow(), periods=12, freq="M")
        return pd.Series(np.zeros(len(idx)), index=idx)
    series = frame.groupby(frame["transaction_date"].dt.to_period("M"))["amount"].sum()
    series.index = series.index.to_timestamp()
    return series


def forecast_financials(frame: pd.DataFrame, horizons: List[int] | None = None) -> ForecastResult:
    """Create revenue/expense projections for the specified horizons."""

    horizons = horizons or [30, 60, 90]
    series = _prepare_series(frame)
    model_used = "exponential_smoothing"
    fit = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated").fit()
    forecast_steps = max(horizons) // 30
    forecast_values = fit.forecast(forecast_steps)
    response_horizons = []
    for horizon in horizons:
        step_index = min(len(forecast_values) - 1, horizon // 30 - 1)
        monthly_projection = float(forecast_values.iloc[step_index])
        revenue_projection = monthly_projection * 1.1
        expense_projection = monthly_projection * 0.9
        runway_days = int((revenue_projection - expense_projection) / 100 + horizon)
        response_horizons.append(
            {
                "horizon_days": horizon,
                "revenue_projection": revenue_projection,
                "expense_projection": expense_projection,
                "runway_days": max(runway_days, 0),
            }
        )
    metadata = {"model": model_used, "historic_points": len(series)}
    return ForecastResult({"horizons": response_horizons, "model_used": model_used, "metadata": metadata})
