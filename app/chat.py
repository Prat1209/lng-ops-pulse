"""
Ops chat layer.

Lets someone ask free-form operational questions ("why did Plaquemines
drop?", "which facility needs attention today?", "any shipments at
risk?") and get an answer grounded in the current live data — not a
generic chatbot, an operator assistant that only knows what's actually
in the system right now.
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("lng-ops-pulse.chat")

SYSTEM_CONTEXT_TEMPLATE = """You are an operations assistant for an LNG plant monitoring system. \
You answer questions from shift leads and engineers using ONLY the data provided below — \
never invent facilities, numbers, or events that aren't in this data.

Be direct and concise (2-4 sentences unless the question needs more). If the data doesn't \
contain what's needed to answer, say so plainly rather than guessing.

CURRENT KPIs:
{kpis}

CURRENT ANOMALIES:
{anomalies}

UPCOMING SHIPMENTS:
{shipments}

RECENT INCIDENTS:
{incidents}
"""


def _format_context(kpis, anomalies, shipments, incidents) -> str:
    return SYSTEM_CONTEXT_TEMPLATE.format(
        kpis=kpis, anomalies=anomalies, shipments=shipments, incidents=incidents
    )


def answer_question(question: str, history: list[dict], kpis, anomalies, shipments, incidents) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "answer": "Chat isn't available right now — no AI key configured on the server.",
            "source": "unavailable",
        }

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        context = _format_context(kpis, anomalies, shipments, incidents)

        # Build conversation: system context first, then prior turns, then the new question
        contents = []
        for turn in history[-6:]:  # keep last few turns to bound context size
            role = "user" if turn.get("role") == "user" else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part(text=turn.get("content", ""))])
            )
        contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=context),
        )
        return {"answer": response.text.strip(), "source": "gemini-3.6-flash"}
    except Exception as e:
        logger.error("Chat call failed: %s", e)
        return {
            "answer": "Something went wrong answering that — try rephrasing or ask again in a moment.",
            "source": "error",
        }
