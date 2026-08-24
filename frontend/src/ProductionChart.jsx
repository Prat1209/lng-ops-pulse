import React, { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Dot,
} from "recharts";

const FACILITY_COLORS = {
  "Calcasieu Pass": "#3ec4ff",
  Cameron: "#b26bff",
  Plaquemines: "#ff9d1f",
};

const RANGE_OPTIONS = [
  { label: "30D", days: 30 },
  { label: "60D", days: 60 },
  { label: "90D", days: 90 },
];

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-date">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className="chart-tooltip-row">
          <span className="chart-tooltip-swatch" style={{ background: p.color }} />
          <span className="chart-tooltip-name">{p.dataKey}</span>
          <span className="chart-tooltip-value">{p.value?.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}

function AnomalyDot(facility) {
  return (props) => {
    const { cx, cy, payload } = props;
    if (!payload[`${facility}_anomaly`]) return null;
    return (
      <Dot
        cx={cx}
        cy={cy}
        r={4}
        fill="#ff5a5a"
        stroke="#0e1319"
        strokeWidth={1.5}
      />
    );
  };
}

export default function ProductionChart({ data }) {
  const [rangeDays, setRangeDays] = useState(90);
  const [hidden, setHidden] = useState(new Set());

  const facilities = Object.keys(FACILITY_COLORS);
  const chartData = data.slice(-rangeDays);

  function toggleFacility(facility) {
    setHidden((prev) => {
      const next = new Set(prev);
      if (next.has(facility)) next.delete(facility);
      else next.add(facility);
      return next;
    });
  }

  return (
    <div className="panel chart-panel">
      <div className="panel-header chart-header-row">
        <span>PRODUCTION TREND</span>
        <div className="chart-range-toggle">
          {RANGE_OPTIONS.map((opt) => (
            <button
              key={opt.label}
              className={`chart-range-btn ${rangeDays === opt.days ? "chart-range-btn--active" : ""}`}
              onClick={() => setRangeDays(opt.days)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="chart-body">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#2f3a45" strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fill: "#8a96a3", fontSize: 11, fontFamily: "IBM Plex Mono" }}
              tickLine={false}
              axisLine={{ stroke: "#2f3a45" }}
              minTickGap={30}
            />
            <YAxis
              tick={{ fill: "#8a96a3", fontSize: 11, fontFamily: "IBM Plex Mono" }}
              tickLine={false}
              axisLine={{ stroke: "#2f3a45" }}
              width={50}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              onClick={(e) => toggleFacility(e.dataKey)}
              wrapperStyle={{ cursor: "pointer", fontFamily: "IBM Plex Mono", fontSize: 12 }}
              formatter={(value) => (
                <span style={{ color: hidden.has(value) ? "#55606c" : "#e8edf2" }}>{value}</span>
              )}
            />
            {facilities.map((facility) => (
              <Line
                key={facility}
                type="monotone"
                dataKey={facility}
                stroke={FACILITY_COLORS[facility]}
                strokeWidth={2}
                dot={AnomalyDot(facility)}
                activeDot={{ r: 5 }}
                hide={hidden.has(facility)}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="chart-hint">Click a legend item to toggle a facility · red dots mark flagged anomalies</div>
    </div>
  );
}
