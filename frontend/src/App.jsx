import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([
    {
      text: "Hello! How can I help you today?",
      sender: "bot",
    },
  ]);

  const sendMessage = async () => {
    if (!message.trim()) return;
  
    const userMessage = message;
  
    setMessages([
      ...messages,
      {
        text: userMessage,
        sender: "user",
      },
    ]);
  
    setMessage("");
  
    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: userMessage,
          top_k: 5,
        }),
      });
  
      const data = await response.json();
  
      setMessages((prev) => [
        ...prev,
        {
          text: data.answer,
          sender: "bot",
        },
      ]);
  
    } catch (error) {
      console.error(error);
  
      setMessages((prev) => [
        ...prev,
        {
          text: "Sorry, something went wrong.",
          sender: "bot",
        },
      ]);
    }
  };

  return (
    <div className="chat-container">

      <header className="chat-header">
        <div>
          <h2>AI Assistant</h2>
          <span>Online</span>
        </div>
      </header>

      <main className="chat-messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender}`}
          >
            {msg.text}
          </div>
        ))}
      </main>

      <div className="chat-input">

        <input
          type="text"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendMessage();
            }
          }}
        />

        <button onClick={sendMessage}>
          Send
        </button>

      </div>

    </div>
  );
}

export default App;