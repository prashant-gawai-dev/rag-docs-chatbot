import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const suggestedPrompts = [
  "What does Cashfree decline code 3044 mean?",
  "How long should a failed payment refund take?",
  "Help me draft an escalation to Razorpay",
  "What details should I collect for a payment issue?",
];

function App() {
  const [message, setMessage] = useState("");
  const [promptsOpen, setPromptsOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isTypingResponse, setIsTypingResponse] = useState(false);
  const [typingText, setTypingText] = useState("");
  const messagesEndRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      text: "Hello! How can I help you today?",
      sender: "bot",
    },
  ]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = async () => {
    if (!message.trim() || isLoading) return;

    const userMessage = message;

    setMessages((previous) => [
      ...previous,
      { text: userMessage, sender: "user" },
    ]);
    setMessage("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: userMessage,
          top_k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed with status ${response.status}`);
      }

      const data = await response.json();
      const answer = data.answer;
      setIsTypingResponse(true);

      for (const character of answer) {
        setTypingText((currentText) => currentText + character);
        await new Promise((resolve) => setTimeout(resolve, 16));
      }

      setMessages((prev) => [
        ...prev,
        { text: answer, sender: "bot" },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { text: "Sorry, something went wrong.", sender: "bot" },
      ]);
    } finally {
      setIsTypingResponse(false);
      setTypingText("");
      setIsLoading(false);
    }
  };

  const choosePrompt = (prompt) => {
    setMessage(prompt);
    setPromptsOpen(false);
  };

  return (
    <div className="chat-widget">
      {chatOpen && <div className="chat-shell">
      <header className="chat-header">
        <div className="brand-mark" aria-hidden="true">G</div>
        <div className="header-copy">
          <p className="eyebrow">GOLDENPI SUPPORT</p>
          <h1>Payment assistant</h1>
        </div>
        <div className="connection-status"><span /> Knowledge base online</div>
      </header>

      <main className="chat-main">
        <section className="chat-messages" aria-live="polite" aria-label="Conversation">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.sender}`}>
              {msg.sender === "bot" && <div className="assistant-mark" aria-hidden="true">G</div>}
              <div className={`message ${msg.sender}`}>{msg.text}</div>
            </div>
          ))}
          {isLoading && !isTypingResponse && (
            <div className="message-row bot" role="status" aria-label="Assistant is thinking">
              <div className="assistant-mark" aria-hidden="true">G</div>
              <div className="message bot typing-indicator">
                <span />
                <span />
                <span />
                <span className="visually-hidden">Thinking...</span>
              </div>
            </div>
          )}
          {isTypingResponse && (
            <div className="message-row bot" role="status" aria-label="Assistant is typing">
              <div className="assistant-mark" aria-hidden="true">G</div>
              <div className="message bot response-typing">{typingText}</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </section>
      </main>

      <footer className="composer-area">
        <div className="composer-wrap">
          {promptsOpen && (
            <div className="prompt-panel" id="prompt-panel" role="group" aria-label="Suggested prompts">
              <div className="prompt-panel-heading">
                <span>Try asking</span>
                <span className="prompt-count">{suggestedPrompts.length} suggestions</span>
              </div>
              {suggestedPrompts.map((prompt) => (
                <button className="prompt-option" key={prompt} onClick={() => choosePrompt(prompt)}>
                  <span className="prompt-arrow" aria-hidden="true">↗</span>
                  {prompt}
                </button>
              ))}
            </div>
          )}
          <div className="chat-input">
            <button
              className={`prompts-toggle${promptsOpen ? " is-open" : ""}`}
              type="button"
              aria-expanded={promptsOpen}
              aria-controls="prompt-panel"
              onClick={() => setPromptsOpen((open) => !open)}
            >
              <span className="prompt-toggle-icon" aria-hidden="true">✦</span>
              <span>Prompts</span>
            </button>
            <input
              type="text"
              aria-label="Message"
              placeholder="Ask about a payment, refund, or escalation..."
              value={message}
              disabled={isLoading}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") sendMessage();
              }}
            />
            <button className="send-button" type="button" onClick={sendMessage} aria-label="Send message" disabled={!message.trim() || isLoading}>
              <span>Send</span><span aria-hidden="true">↑</span>
            </button>
          </div>
          <p className="composer-note">Responses are grounded in the payment support knowledge base.</p>
        </div>
      </footer>
      </div>}
      <button
        className={`chat-launcher${chatOpen ? " is-open" : ""}`}
        type="button"
        aria-label={chatOpen ? "Close payment assistant" : "Open payment assistant"}
        aria-expanded={chatOpen}
        onClick={() => {
          setChatOpen((open) => !open);
          setPromptsOpen(false);
        }}
      >
        <span className="launcher-symbol" aria-hidden="true">{chatOpen ? "×" : ""}</span>
        <span>{chatOpen ? "Close" : "Chat with us"}</span>
      </button>
    </div>
  );
}

export default App;