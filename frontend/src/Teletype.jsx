import React, { useEffect, useState, useRef } from "react";

export default function Teletype({ text, sourceLabel }) {
  const [visibleChars, setVisibleChars] = useState(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    setVisibleChars(0);
    if (!text) return;

    intervalRef.current = setInterval(() => {
      setVisibleChars((prev) => {
        if (prev >= text.length) {
          clearInterval(intervalRef.current);
          return prev;
        }
        return prev + 1;
      });
    }, 12);

    return () => clearInterval(intervalRef.current);
  }, [text]);

  const done = visibleChars >= (text?.length || 0);

  return (
    <div className="teletype">
      <div className="teletype-header">
        <span className="teletype-dot" />
        DAILY BRIEFING — {sourceLabel || "PENDING"}
      </div>
      <div className="teletype-paper">
        <pre className="teletype-text">
          {text ? text.slice(0, visibleChars) : "Awaiting transmission..."}
          {!done && text && <span className="teletype-cursor">▋</span>}
        </pre>
      </div>
    </div>
  );
}
