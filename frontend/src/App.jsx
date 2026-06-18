import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const welcomeMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Hello. Ask me about admissions, fees, departments, placements, committees, research centers, or student life at JUIT.",
  sources: [],
};

function sourceKey(source, index) {
  return `${source?.url || source?.canonical_url || source?.title || "source"}-${index}`;
}

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([welcomeMessage]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const askQuestion = async () => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery || isLoading) {
      return;
    }

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmedQuery,
      sources: [],
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setQuery("");
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: trimmedQuery,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content:
          data.answer ||
          "I could not find that information in the JUIT knowledge base.",
        sources: Array.isArray(data.sources) ? data.sources : [],
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);
    } catch (requestError) {
      const errorMessage =
        "I could not reach the JUIT AI service. Please check that the backend is running and try again.";

      setError(errorMessage);
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: errorMessage,
          sources: [],
          isError: true,
        },
      ]);
      console.error(requestError);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Jaypee University of Information Technology</p>
          <h1>JUIT AI Assistant</h1>
        </div>
        <p className="status-pill">Knowledge base ready</p>
      </header>

      <main className="chat-panel" aria-label="Chat with JUIT AI Assistant">
        <section className="message-list" aria-live="polite">
          {messages.map((message) => (
            <article
              className={`message-row ${message.role}`}
              key={message.id}
            >
              <div
                className={`message-bubble ${message.role} ${
                  message.isError ? "error" : ""
                }`}
              >
                <p>{message.content}</p>

                {message.sources.length > 0 && (
                  <div className="sources">
                    <p className="sources-title">Sources</p>
                    <ul>
                      {message.sources.map((source, index) => {
                        const url = source.url || source.canonical_url;
                        const title = source.title || "JUIT source";

                        return (
                          <li key={sourceKey(source, index)}>
                            {url ? (
                              <a href={url} target="_blank" rel="noreferrer">
                                <span>{title}</span>
                                <small>{url}</small>
                              </a>
                            ) : (
                              <span>
                                <span>{title}</span>
                              </span>
                            )}
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </div>
            </article>
          ))}

          {isLoading && (
            <article className="message-row assistant">
              <div className="message-bubble assistant loading">
                <span className="spinner" aria-hidden="true" />
                <span>Searching the JUIT knowledge base...</span>
              </div>
            </article>
          )}

          <div ref={messagesEndRef} />
        </section>

        <form
          className="composer"
          onSubmit={(event) => {
            event.preventDefault();
            askQuestion();
          }}
        >
          <label className="sr-only" htmlFor="chat-input">
            Ask a question
          </label>
          <textarea
            id="chat-input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about fees, placements, departments, committees..."
            disabled={isLoading}
            rows={1}
          />
          <button type="submit" disabled={isLoading || !query.trim()}>
            Send
          </button>
        </form>

        {error && <p className="form-error">{error}</p>}
      </main>
    </div>
  );
}

export default App;
