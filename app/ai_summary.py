"""
AI summary layer.

Turns the structured KPI + anomaly output into a short, plain-English
ops briefing — the kind of thing a shift lead could read in 10 seconds
instead of scanning a dashboard. Calls Gemini if GEMINI_API_KEY is set
in the environment; otherwise falls back to a deterministic
rule-based summary so the demo runs with zero external dependencies.
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root if present; no-op if missing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lng-ops-pulse.ai_summary")


def _rule_based_summary(kpis: list[dict], anomalies: list[dict]) -> str:
    lines = []

    worst = min(kpis, key=lambda k: k["wow_change_pct"]) if kpis else None
    best = max(kpis, key=lambda k: k["wow_change_pct"]) if kpis else None

    if worst and worst["wow_change_pct"] < 0:
        lines.append(
            f"{worst['facility']} production is down {abs(worst['wow_change_pct'])}% "
            f"week-over-week — worth a look before end of shift."
        )
    if best and best is not worst and best["wow_change_pct"] > 0:
        lines.append(
            f"{best['facility']} is up {best['wow_change_pct']}% week-over-week, "
            f"currently the strongest performer."
        )

    if anomalies:
        latest = anomalies[0]
        lines.append(
            f"Flagged: {latest['facility']} had a production {latest['direction']} "
            f"on {latest['date']} ({latest['production_mmbtu_k']:,} MMBtu-k, "
            f"z-score {latest['z_score']}) — check compressor / feed-gas logs for that date."
        )
        if len(anomalies) > 1:
            lines.append(f"{len(anomalies) - 1} additional anomaly event(s) in the trailing window.")
    else:
        lines.append("No significant anomalies detected in the trailing window.")

    return " ".join(lines)


def _gemini_summary(kpis: list[dict], anomalies: list[dict]) -> str | None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set — using rule-based fallback.")
        return None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = (
            "You are an LNG plant operations analyst. Write a 3-4 sentence "
            "daily briefing for a shift lead based on this data. Be direct, "
            "flag anything that needs attention, and skip generic filler.\n\n"
            f"KPIs: {kpis}\n\nAnomalies: {anomalies}"
        )
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        # Log the real reason instead of failing silently
        logger.error("Gemini call failed, falling back to rule-based summary: %s", e)
        return None


def generate_daily_summary(kpis: list[dict], anomalies: list[dict]) -> dict:
    ai_text = _gemini_summary(kpis, anomalies)
    if ai_text:
        return {"summary": ai_text, "source": "gemini-3.6-flash"}

    return {"summary": _rule_based_summary(kpis, anomalies), "source": "rule-based-fallback"}