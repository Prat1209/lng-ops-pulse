"""
Simulated operational data for LNG Ops Pulse.

In a real deployment this module would be replaced by connectors to
actual plant historian / SCADA / ERP data sources (e.g. OSI PI, which
Venture Global's own job board lists as a system they run — see
`Administrator, OSI PI` req). For this demo we generate realistic
synthetic data so the pipeline, API, and AI layer can be fully
exercised end to end.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

FACILITIES = ["Calcasieu Pass", "Plaquemines", "Cameron"]

random.seed(42)
np.random.seed(42)


def _generate_production(days: int = 90) -> pd.DataFrame:
    """Daily LNG production volume (in MMBtu, thousands) per facility."""
    end = datetime.utcnow().date()
    dates = [end - timedelta(days=i) for i in range(days)][::-1]

    rows = []
    for facility in FACILITIES:
        base = {"Calcasieu Pass": 850, "Plaquemines": 1200, "Cameron": 950}[facility]
        volume = base
        for d in dates:
            # slow drift + daily noise
            volume += np.random.normal(0, 15)
            volume = max(volume, base * 0.5)

            # inject a couple of deliberate anomalies so /anomalies has
            # something real to find
            if facility == "Plaquemines" and d == dates[-4]:
                volume *= 0.72  # sudden 28% drop -> compressor issue
            if facility == "Cameron" and d == dates[-9]:
                volume *= 0.80  # 20% drop -> feed gas curtailment

            rows.append(
                {
                    "date": d.isoformat(),
                    "facility": facility,
                    "production_mmbtu_k": round(volume, 1),
                }
            )
    return pd.DataFrame(rows)


def _generate_shipments(count: int = 12) -> pd.DataFrame:
    """Upcoming LNG carrier shipments."""
    today = datetime.utcnow().date()
    carriers = [
        "LNG Endeavour", "Venture Bayou", "Gulf Voyager", "Delta Pioneer",
        "Marsh Runner", "Bayou Explorer",
    ]
    rows = []
    for i in range(count):
        ship_date = today + timedelta(days=random.randint(1, 30))
        rows.append(
            {
                "shipment_id": f"SHP-{1000 + i}",
                "facility": random.choice(FACILITIES),
                "carrier": random.choice(carriers),
                "scheduled_date": ship_date.isoformat(),
                "volume_mmbtu_k": random.randint(280, 420),
                "status": random.choice(["confirmed", "pending", "confirmed", "confirmed"]),
            }
        )
    return pd.DataFrame(rows).sort_values("scheduled_date").reset_index(drop=True)


def _generate_incidents(count: int = 5) -> pd.DataFrame:
    """Recent safety / operations incident log entries."""
    today = datetime.utcnow().date()
    categories = ["Near miss", "Equipment fault", "Minor spill", "Process upset", "Safety observation"]
    severities = ["Low", "Low", "Medium", "Medium", "High"]
    rows = []
    for i in range(count):
        idx = random.randrange(len(categories))
        rows.append(
            {
                "incident_id": f"INC-{500 + i}",
                "facility": random.choice(FACILITIES),
                "date": (today - timedelta(days=random.randint(0, 30))).isoformat(),
                "category": categories[idx],
                "severity": severities[idx],
            }
        )
    return pd.DataFrame(rows).sort_values("date", ascending=False).reset_index(drop=True)


# Materialize once at import time; a real system would refresh this on
# a schedule (see automation.py) rather than regenerate per-request.
PRODUCTION_DF = _generate_production()
SHIPMENTS_DF = _generate_shipments()
INCIDENTS_DF = _generate_incidents()
