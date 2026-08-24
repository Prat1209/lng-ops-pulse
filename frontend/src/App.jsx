import React, { useEffect, useState } from "react";
import FacilityGauge from "./FacilityGauge.jsx";
import Teletype from "./Teletype.jsx";
import OpsChat from "./OpsChat.jsx";
import ProductionChart from "./ProductionChart.jsx";
import "./App.css";

const API_BASE = "https://lng-ops-pulse.onrender.com";

function useClock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

export default function App() {
  const [kpis, setKpis] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const clock = useClock();

  useEffect(() => {
    async function loadAll() {
      try {
        const [kpisRes, anomaliesRes, shipmentsRes, summaryRes, historyRes] = await Promise.all([
          fetch(`${API_BASE}/kpis`),
          fetch(`${API_BASE}/anomalies`),
          fetch(`${API_BASE}/shipments`),
          fetch(`${API_BASE}/summary`),
          fetch(`${API_BASE}/production-history`),
        ]);

        if (!kpisRes.ok || !anomaliesRes.ok || !shipmentsRes.ok || !summaryRes.ok || !historyRes.ok) {
          throw new Error("One or more endpoints returned an error.");
        }

        setKpis(await kpisRes.json());
        setAnomalies(await anomaliesRes.json());
        setShipments(await shipmentsRes.json());
        setSummary(await summaryRes.json());
        setHistory(await historyRes.json());
        setError(null);
      } catch (e) {
        setError(
          "Can't reach the backend. Make sure the FastAPI server is running at " +
            API_BASE +
            " (uvicorn app.main:app --reload --port 8000)."
        );
      } finally {
        setLoading(false);
      }
    }
    loadAll();
  }, []);

  const anomalyFacilities = new Set(anomalies.map((a) => a.facility));
  const overallStatus = anomalies.length > 0 ? "critical" : "nominal";

  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar-title">
          <span className="topbar-mark" />
          <span className="topbar-name">LNG OPS PULSE</span>
        </div>
        <div className={`status-pill status-pill--${overallStatus}`}>
          {overallStatus === "nominal" ? "SYSTEM NOMINAL" : `${anomalies.length} ANOMALIES FLAGGED`}
        </div>
        <div className="topbar-clock">
          {clock.toISOString().slice(11, 19)} UTC
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {!error && (
        <>
          <section className="gauges-row">
            {kpis.map((k) => (
              <FacilityGauge
                key={k.facility}
                facility={k.facility}
                production={k.production_mmbtu_k}
                wowChange={k.wow_change_pct}
                hasAnomaly={anomalyFacilities.has(k.facility)}
              />
            ))}
            {loading && kpis.length === 0 && (
              <div className="gauge-placeholder">Loading facility data…</div>
            )}
          </section>

          {history.length > 0 && <ProductionChart data={history} />}

          <section className="mid-row">
            <div className="panel anomaly-panel">
              <div className="panel-header">ANOMALY LOG</div>
              <div className="panel-body">
                {anomalies.length === 0 && !loading && (
                  <div className="empty-state">No anomalies in the trailing window.</div>
                )}
                <ul className="anomaly-list">
                  {anomalies.slice(0, 8).map((a, i) => (
                    <li key={i} className="anomaly-item">
                      <span className={`anomaly-marker anomaly-marker--${a.direction}`} />
                      <div className="anomaly-text">
                        <span className="anomaly-facility">{a.facility}</span>
                        <span className="anomaly-detail">
                          {a.date} · {a.production_mmbtu_k.toLocaleString()} MMBtu-k · z{a.z_score}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <Teletype text={summary?.summary} sourceLabel={summary?.source} />
          </section>

          <OpsChat />

          <section className="panel manifest-panel">
            <div className="panel-header">SHIPMENT MANIFEST</div>
            <table className="manifest-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Facility</th>
                  <th>Carrier</th>
                  <th>Date</th>
                  <th>Volume</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {shipments.slice(0, 8).map((s) => (
                  <tr key={s.shipment_id}>
                    <td className="mono">{s.shipment_id}</td>
                    <td>{s.facility}</td>
                    <td>{s.carrier}</td>
                    <td className="mono">{s.scheduled_date}</td>
                    <td className="mono">{s.volume_mmbtu_k.toLocaleString()}</td>
                    <td>
                      <span className={`chip chip--${s.status}`}>{s.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  );
}
