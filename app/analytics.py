"""
ETL / analytics layer.

Turns raw production records into the KPIs and anomaly flags the API
serves. Kept as plain pandas so it's easy to swap the data source
(data.py) for a real one later without touching this logic.
"""
from __future__ import annotations

import pandas as pd

from .data import PRODUCTION_DF


def get_kpis() -> list[dict]:
    """Latest-day production per facility plus week-over-week change."""
    df = PRODUCTION_DF.copy()
    df["date"] = pd.to_datetime(df["date"])

    results = []
    for facility, group in df.groupby("facility"):
        group = group.sort_values("date")
        latest = group.iloc[-1]
        week_ago_cutoff = latest["date"] - pd.Timedelta(days=7)
        week_ago_rows = group[group["date"] <= week_ago_cutoff]
        week_ago_value = week_ago_rows.iloc[-1]["production_mmbtu_k"] if not week_ago_rows.empty else latest["production_mmbtu_k"]

        pct_change = ((latest["production_mmbtu_k"] - week_ago_value) / week_ago_value) * 100

        results.append(
            {
                "facility": facility,
                "date": latest["date"].date().isoformat(),
                "production_mmbtu_k": latest["production_mmbtu_k"],
                "wow_change_pct": round(pct_change, 1),
            }
        )
    return results


def get_production_history() -> list[dict]:
    """
    Full daily production series per facility, shaped for charting:
    one row per date with each facility as a column, plus per-facility
    anomaly flags so the frontend can mark them directly on the line.
    """
    df = PRODUCTION_DF.copy()
    df["date"] = pd.to_datetime(df["date"])

    anomaly_dates = {}
    for a in detect_anomalies(lookback_days=len(df["date"].unique())):
        anomaly_dates.setdefault(a["facility"], set()).add(a["date"])

    pivot = df.pivot(index="date", columns="facility", values="production_mmbtu_k").sort_index()

    rows = []
    for date, row in pivot.iterrows():
        date_str = date.date().isoformat()
        entry = {"date": date_str}
        for facility in pivot.columns:
            value = row[facility]
            entry[facility] = None if pd.isna(value) else round(float(value), 1)
            entry[f"{facility}_anomaly"] = date_str in anomaly_dates.get(facility, set())
        rows.append(entry)

    return rows


def detect_anomalies(z_threshold: float = 1.8, lookback_days: int = 30) -> list[dict]:
    """
    Flag days where a facility's production deviates more than
    `z_threshold` standard deviations from its own trailing mean.
    Simple, explainable, and good enough to surface the two injected
    events in the synthetic data — swap for a more sophisticated
    detector (e.g. seasonal decomposition) against real data.
    """
    df = PRODUCTION_DF.copy()
    df["date"] = pd.to_datetime(df["date"])

    anomalies = []
    for facility, group in df.groupby("facility"):
        group = group.sort_values("date").tail(lookback_days).reset_index(drop=True)
        mean = group["production_mmbtu_k"].mean()
        std = group["production_mmbtu_k"].std()
        if std == 0:
            continue

        group["z_score"] = (group["production_mmbtu_k"] - mean) / std
        flagged = group[group["z_score"].abs() >= z_threshold]

        for _, row in flagged.iterrows():
            direction = "drop" if row["z_score"] < 0 else "spike"
            anomalies.append(
                {
                    "facility": facility,
                    "date": row["date"].date().isoformat(),
                    "production_mmbtu_k": row["production_mmbtu_k"],
                    "z_score": round(row["z_score"], 2),
                    "direction": direction,
                }
            )
    return sorted(anomalies, key=lambda a: a["date"], reverse=True)
