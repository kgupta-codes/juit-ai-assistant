import { SendIcon, StopIcon } from "./icons";

export default function Composer({
  disabled,
  error,
  onChange,
  onKeyDown,
  onStop,
  onSubmit,
  query,
  textareaRef,
}) {
  return (
    <div className="composer-wrap">
      <form
        className="composer"
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
      >
        <label className="sr-only" htmlFor="chat-input">
          Ask a question
        </label>
        <textarea
          id="chat-input"
          ref={textareaRef}
          value={query}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask anything about JUIT..."
          disabled={disabled}
          rows={1}
          aria-describedby={error ? "composer-error" : "composer-hint"}
        />
        {disabled ? (
          <button type="button" onClick={onStop} aria-label="Stop generating">
            <StopIcon />
          </button>
        ) : (
          <button type="submit" disabled={!query.trim()} aria-label="Send message">
            <SendIcon />
          </button>
        )}
      </form>
      <p id="composer-hint" className="composer-hint">
        Press Enter to send. Use Shift+Enter for a new line.
      </p>
      {error && (
        <p id="composer-error" className="form-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
