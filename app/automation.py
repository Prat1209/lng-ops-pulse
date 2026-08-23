"""
Automation layer.

Stands in for a Power Automate / UI Path style workflow: on a schedule,
re-run the ETL + anomaly detection + AI summary, and "deliver" it
(here: log it; in production this would post to Slack/Teams/email via
an API call — swapping the delivery step is a one-function change).

This is the honest equivalent to describe in an interview: "I built a
scheduled automation pipeline that does what a Power Automate flow
would do, in code I fully own."
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from .analytics import detect_anomalies, get_kpis
from .ai_summary import generate_daily_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lng-ops-pulse.automation")

scheduler = BackgroundScheduler()


def run_daily_ops_job() -> dict:
    kpis = get_kpis()
    anomalies = detect_anomalies()
    summary = generate_daily_summary(kpis, anomalies)

    logger.info("Daily ops summary generated (%s): %s", summary["source"], summary["summary"])
    # Delivery step placeholder — e.g. POST to a Slack/Teams webhook here.
    return summary


def start_scheduler() -> None:
    if not scheduler.running:
        # Runs every 24h; interval shortened here would be for demo purposes only.
        scheduler.add_job(run_daily_ops_job, "interval", hours=24, id="daily_ops_job", replace_existing=True)
        scheduler.start()
        logger.info("Automation scheduler started — daily ops job registered.")
