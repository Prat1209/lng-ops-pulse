# LNG Ops Pulse

An operations intelligence backend for LNG production monitoring —
built as a focused demo of full-stack + automation + AI engineering
for energy-sector operations.

## What it does

- **ETL pipeline** (`app/data.py`, `app/analytics.py`) ingests and
  cleans production, shipment, and incident data (synthetic here;
  designed to be swapped for a real historian/SCADA/OSI PI feed).
- **REST API** (`app/main.py`, FastAPI) exposes KPIs, anomaly
  detection, shipment schedules, and incident logs.
- **Anomaly detection** flags production drops/spikes via trailing
  z-score analysis — explainable and fast, no black-box model needed
  for this scale of signal.
- **AI briefing layer** (`app/ai_summary.py`) turns structured KPIs
  into a plain-English daily summary a shift lead can read in
  seconds. Uses Gemini if `GEMINI_API_KEY` is set, otherwise falls
  back to a deterministic rule-based summary — so the demo runs with
  zero external dependencies.
- **Scheduled automation** (`app/automation.py`) re-runs the pipeline
  on an interval and "delivers" the briefing — a code-owned stand-in
  for a Power Automate / RPA-style workflow.

## Why this shape

This mirrors the core asks in the Venture Global Software Engineer
JD: translating business needs into working software, building data
models and automated pipelines, exposing APIs for downstream
consumption, and doing it end-to-end rather than in a single layer.

## Run it

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API docs, or hit
the endpoints directly:

- `GET /kpis` — latest production per facility + week-over-week change
- `GET /anomalies` — flagged production anomalies
- `GET /shipments` — upcoming carrier shipments
- `GET /incidents` — recent safety/ops incident log
- `GET /summary` — AI-generated daily briefing

## Next steps (not built yet, worth mentioning in an interview)

- Swap synthetic data for a real source (OSI PI export, CSV feed, etc.)
- Frontend dashboard (React) consuming these endpoints
- Deploy on AWS (EC2 + RDS, reusing the HA pattern from a prior project)
- Real delivery channel for the automation job (Slack/Teams webhook)
