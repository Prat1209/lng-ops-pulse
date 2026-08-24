import React, { useState, useRef, useEffect } from "react";

const API_BASE = "https://lng-ops-pulse.onrender.com";

const SUGGESTED_QUESTIONS = [
  "Which facility needs attention today?",
  "Are any shipments at risk?",
  "Summarize the safety incidents this month",
];

export default function OpsChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  async function sendQuestion(question) {
    if (!question.trim() || loading) return;

    const userMsg = { role: "user", content: question };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          history: messages.slice(-6),
        }),
      });
      const data = await res.json();
      setMessages([...nextMessages, { role: "assistant", content: data.answer, source: data.source }]);
    } catch (e) {
      setMessages([
        ...nextMessages,
        { role: "assistant", content: "Comms link down — couldn't reach the server.", source: "error" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ops-chat">
      <div className="ops-chat-header">
        <span className="ops-chat-dot" />
        OPS COMMS — ASK A QUESTION
      </div>

      <div className="ops-chat-body" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="ops-chat-empty">
            <div className="ops-chat-empty-text">No transmissions yet. Try:</div>
            <div className="ops-chat-suggestions">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button key={q} className="ops-chat-suggestion" onClick={() => sendQuestion(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`ops-chat-msg ops-chat-msg--${m.role}`}>
            <span className="ops-chat-msg-tag">{m.role === "user" ? "YOU" : "OPS AI"}</span>
            <span className="ops-chat-msg-text">{m.content}</span>
          </div>
        ))}

        {loading && (
          <div className="ops-chat-msg ops-chat-msg--assistant">
            <span className="ops-chat-msg-tag">OPS AI</span>
            <span className="ops-chat-msg-text ops-chat-typing">receiving…</span>
          </div>
        )}
      </div>

      <form
        className="ops-chat-input-row"
        onSubmit={(e) => {
          e.preventDefault();
          sendQuestion(input);
        }}
      >
        <span className="ops-chat-prompt">&gt;</span>
        <input
          className="ops-chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about production, anomalies, shipments..."
          disabled={loading}
        />
        <button className="ops-chat-send" type="submit" disabled={loading || !input.trim()}>
          SEND
        </button>
      </form>
    </div>
  );
}
