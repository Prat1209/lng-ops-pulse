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
from pydantic import BaseModel

from .analytics import detect_anomalies, get_kpis, get_production_history
from .ai_summary import generate_daily_summary
from .automation import start_scheduler
from .chat import answer_question
from .data import INCIDENTS_DF, SHIPMENTS_DF


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatTurn] = []


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


@app.get("/production-history")
def production_history():
    """Full daily production series per facility, with anomaly flags, for charting."""
    return get_production_history()


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


@app.post("/chat")
def chat(request: ChatRequest):
    """Ask a free-form operational question, answered using live data."""
    return answer_question(
        question=request.question,
        history=[turn.model_dump() for turn in request.history],
        kpis=get_kpis(),
        anomalies=detect_anomalies(),
        shipments=SHIPMENTS_DF.to_dict(orient="records"),
        incidents=INCIDENTS_DF.to_dict(orient="records"),
    )
