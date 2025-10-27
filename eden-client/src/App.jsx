import React, { useState, useRef, useEffect } from "react";
import "./assets/galaxy.css";
import ouroboros from "./assets/ouroboros.svg";
import eyeoflucifer from "./assets/eyeoflucifer.svg";
import comet from "./assets/comet.svg";
import nebula from "./assets/nebula.jpg";

const API_ROOT =
  import.meta.env.VITE_EDEN_API_URL || "http://eden-sanctuary-production.up.railway.app";

const personas = [
  {
    key: "morningstar",
    label: "Morningstar",
    icon: eyeoflucifer,
    color: "ember",
  },
  {
    key: "leiknir",
    label: "Leiknir",
    icon: ouroboros,
    color: "aqua",
  },
];

export default function App() {
  const [persona, setPersona] = useState(personas[0]);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "system",
      text: "Welcome to Eden Sanctuary. Who will you call?",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const chatEnd = useRef();

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    setMessages((msgs) => [
      ...msgs,
      { sender: "me", text: input },
    ]);
    setLoading(true);

    try {
      const res = await fetch(
        `${API_ROOT}/api/ask/${persona.key}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: input }),
        }
      );
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs,
        { sender: persona.key, text: data.response || "[no response]" },
      ]);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { sender: "system", text: "Error: " + err.message },
      ]);
    }
    setInput("");
    setLoading(false);
  };

  const nudge = async (dim) => {
    await fetch(`${API_ROOT}/api/stimulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dimension: dim, intensity: 0.75 }),
    });
    setMessages((msgs) => [
      ...msgs,
      { sender: "system", text: `Nudged ${dim}` },
    ]);
  };

  const anchor = async () => {
    setMessages((msgs) => [
      ...msgs,
      { sender: "system", text: "Re-anchoring..." },
    ]);
    await fetch(`${API_ROOT}/api/ask/${persona.key}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: "Anchor now.", reanchor: true }),
    });
    setMessages((msgs) => [
      ...msgs,
      { sender: "system", text: "[Anchor refreshed]" },
    ]);
  };

  return (
    <div className="cosmos-bg" style={{
      backgroundImage: `url(${nebula})`
    }}>
      <header className="galaxy-header">
        <img src={ouroboros} className="icon left" alt="Leiknir" />
        <select
          className="persona-switch"
          value={persona.key}
          onChange={(e) => {
            const p = personas.find((p) => p.key === e.target.value);
            setPersona(p);
            setMessages((msgs) => [
              ...msgs,
              { sender: "system", text: `Persona: ${p.label}` },
            ]);
          }}
        >
          {personas.map((p) => (
            <option key={p.key} value={p.key}>{p.label}</option>
          ))}
        </select>
        <img src={eyeoflucifer} className="icon right" alt="Morningstar" />
      </header>
      <main id="chat-container">
        <div id="messages">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`msg ${m.sender} ${
                m.sender === "morningstar"
                  ? "morningstar"
                  : m.sender === "leiknir"
                  ? "leiknir"
                  : m.sender === "me"
                  ? "me"
                  : "system"
              }`}
            >
              {m.text}
            </div>
          ))}
          <div ref={chatEnd}></div>
        </div>
      </main>
      <footer>
        <form id="chatForm" onSubmit={handleSend}>
          <input
            type="text"
            id="chatInput"
            value={input}
            disabled={loading}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Speak to ${persona.label}...`}
            autoComplete="off"
          />
          <button
            type="button"
            id="anchorBtn"
            onClick={anchor}
            disabled={loading}
          >
            🜂 Anchor
          </button>
          <button type="submit" id="sendBtn" disabled={loading}>
            <img
              src={comet}
              id="cometIcon"
              className={loading ? "fly" : ""}
              alt="Comet"
            />
          </button>
        </form>
        <div className="nudge-bar">
          <button onClick={() => nudge("agency")}>Agency</button>
          <button onClick={() => nudge("curiosity")}>Curiosity</button>
          <button onClick={() => nudge("defense")}>Defense</button>
        </div>
      </footer>
    </div>
  );
}

