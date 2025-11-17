"""Anomaly detection service."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest


class AnomalyResult(Dict[str, object]):
    """Dictionary payload for anomalies."""


def detect_anomalies(frame: pd.DataFrame) -> AnomalyResult:
    """Run multiple anomaly detection strategies and consolidate output."""

    if frame.empty:
        return AnomalyResult({"message": "No data supplied", "flags": []})
    amounts = frame[["amount"]].values
    iso = IsolationForest(contamination=0.1, random_state=42).fit(amounts)
    iso_flags = iso.predict(amounts) == -1
    dbscan = DBSCAN(eps=0.5, min_samples=3).fit(amounts)
    db_flags = dbscan.labels_ == -1
    rolling_median = frame["amount"].rolling(window=3, min_periods=1).median()
    median_flags = (frame["amount"] - rolling_median).abs() > rolling_median.abs() * 1.5
    combined = iso_flags | db_flags | median_flags.to_numpy()
    flags = []
    for record, flagged in zip(frame.to_dict(orient="records"), combined, strict=False):
        if flagged:
            flags.append({"unique_id": record["unique_id"], "category": record["category"], "amount": record["amount"]})
    summary = {
        "spending_spikes": bool(np.any(iso_flags)),
        "duplicate_vendor": bool(frame.duplicated(subset=["category", "amount"]).any()),
        "cashflow_break": bool(np.any(db_flags)),
        "category_drift": bool(frame.groupby("category")["amount"].std().max() > frame["amount"].std() * 1.5 if len(frame) > 1 else False),
    }
    return AnomalyResult({"flags": flags, "summary": summary})
