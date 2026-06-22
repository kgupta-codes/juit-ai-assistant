import { TopicIcon } from "./icons";

export default function WelcomeState({ prompts, isLoading, onAsk }) {
  return (
    <section className="welcome-state" aria-label="Welcome section">
      <div className="welcome-orb" aria-hidden="true">
        <img src="/juit-icon.png" alt="" />
      </div>

      <div className="welcome-copy">
        <p className="greeting">JUIT knowledge base</p>
        <h3>How can I help?</h3>
        <p>
          Ask about university information and get answers grounded in retrieved JUIT
          sources.
        </p>
      </div>

      <div className="prompt-grid" aria-label="Suggested questions">
        {prompts.map((prompt) => (
          <button
            key={prompt.question}
            className="prompt-card"
            type="button"
            onClick={() => onAsk(prompt.question)}
            disabled={isLoading}
          >
            <span className="prompt-card-icon">
              <TopicIcon label={prompt.label} />
            </span>
            <span>
              <strong>{prompt.label}</strong>
              <small>{prompt.question}</small>
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
