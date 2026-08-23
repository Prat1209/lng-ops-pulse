import React from "react";

// Facility baselines used to normalize the gauge arc (rough operating midpoints)
const BASELINES = {
  "Calcasieu Pass": 850,
  Plaquemines: 1200,
  Cameron: 950,
};

function arcPath(cx, cy, r, startAngle, endAngle) {
  const toXY = (angle) => {
    const rad = (angle - 90) * (Math.PI / 180);
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  };
  const [x1, y1] = toXY(startAngle);
  const [x2, y2] = toXY(endAngle);
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`;
}

export default function FacilityGauge({ facility, production, wowChange, hasAnomaly }) {
  const baseline = BASELINES[facility] || 1000;
  const ratio = Math.min(Math.max(production / baseline, 0), 1.4);
  const sweep = Math.min(ratio / 1.4, 1) * 270;

  const status = hasAnomaly ? "critical" : wowChange < -8 ? "warning" : "nominal";
  const statusColor = `var(--${status})`;

  return (
    <div className="gauge-card">
      <svg viewBox="0 0 200 160" className="gauge-svg">
        <path
          d={arcPath(100, 100, 78, -135, 135)}
          fill="none"
          stroke="var(--grid-line)"
          strokeWidth="10"
          strokeLinecap="round"
        />
        <path
          d={arcPath(100, 100, 78, -135, -135 + sweep)}
          fill="none"
          stroke={statusColor}
          strokeWidth="10"
          strokeLinecap="round"
          className="gauge-fill"
        />
        <text x="100" y="95" textAnchor="middle" className="gauge-value">
          {production.toLocaleString()}
        </text>
        <text x="100" y="115" textAnchor="middle" className="gauge-unit">
          MMBtu-k
        </text>
      </svg>

      <div className="gauge-label">
        <span className="gauge-facility">{facility}</span>
        <span className={`gauge-change gauge-change--${wowChange < 0 ? "down" : "up"}`}>
          {wowChange > 0 ? "▲" : "▼"} {Math.abs(wowChange)}% WoW
        </span>
      </div>
    </div>
  );
}
