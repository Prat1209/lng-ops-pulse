"""
LNG Ops Pulse — FastAPI backend.

A lightweight operations intelligence API: exposes production KPIs,
anomaly detection, shipment schedules, and an AI-generated daily
briefing, backed by a scheduled automation job.

Run locally:
    uvicorn app.main:app --reload --port 8000

Then visit http://localhost:8000/docs for interactive API docs.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .analytics import detect_anomalies, get_kpis
from .ai_summary import generate_daily_summary
from .automation import start_scheduler
from .data import INCIDENTS_DF, SHIPMENTS_DF


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield


app = FastAPI(
    title="LNG Ops Pulse",
    description="Operations intelligence API for LNG production, shipments, and safety monitoring.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only — lock this down for real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"service": "LNG Ops Pulse API", "docs": "/docs"}


@app.get("/kpis")
def kpis():
    """Latest production KPIs per facility, with week-over-week change."""
    return get_kpis()


@app.get("/anomalies")
def anomalies():
    """Production anomalies flagged via trailing z-score detection."""
    return detect_anomalies()


@app.get("/shipments")
def shipments():
    """Upcoming LNG carrier shipment schedule."""
    return SHIPMENTS_DF.to_dict(orient="records")


@app.get("/incidents")
def incidents():
    """Recent safety / operations incident log."""
    return INCIDENTS_DF.to_dict(orient="records")


@app.get("/summary")
def summary():
    """AI-generated plain-English daily ops briefing."""
    return generate_daily_summary(get_kpis(), detect_anomalies())
