# LNG Ops Pulse — Frontend

A control-room style dashboard for the LNG Ops Pulse API: facility
production gauges, an anomaly log, a teletype-style AI briefing
readout, and a shipment manifest.

## Run it

Make sure the backend is running first (from the project root, in a
separate terminal):

```bash
uvicorn app.main:app --reload --port 8000
```

Then, in this `frontend/` folder:

```bash
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`).

## Design notes

Built as an industrial control-room panel rather than a generic
SaaS dashboard — gunmetal background, instrument-panel gauge colors
(muted green/amber/red), and monospace data typography throughout.
The AI daily briefing renders as a teletype printout (typewriter
animation, blinking cursor) to visually tie the feature to what it
actually does: producing a shift report a human would read.

## Files

- `src/App.jsx` — layout and data fetching
- `src/FacilityGauge.jsx` — custom SVG radial gauge (no chart library)
- `src/Teletype.jsx` — the typewriter-effect AI briefing component
- `src/App.css` — all component styling and design tokens
