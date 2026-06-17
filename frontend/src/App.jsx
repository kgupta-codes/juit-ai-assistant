import { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");

  const askQuestion = async () => {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: query,
      }),
    });

    const data = await response.json();
    setAnswer(data.answer);
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>JUIT AI Assistant</h1>

      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
        style={{
          width: "400px",
          padding: "10px",
        }}
      />

      <button
        onClick={askQuestion}
        style={{
          marginLeft: "10px",
          padding: "10px",
        }}
      >
        Ask
      </button>

      <div style={{ marginTop: "20px" }}>
        <h3>Answer</h3>
        <p>{answer}</p>
      </div>
    </div>
  );
}

export default App;
