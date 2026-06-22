import { SendIcon } from "./icons";

export default function Composer({
  disabled,
  error,
  onChange,
  onKeyDown,
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
        />
        <button type="submit" disabled={disabled || !query.trim()} aria-label="Send message">
          <SendIcon />
        </button>
      </form>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}
