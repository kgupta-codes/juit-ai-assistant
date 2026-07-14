import { renderMarkdownBlocks } from "../lib/markdown";
import { formatMessageTime } from "../lib/conversations";
import { CopyIcon, RefreshIcon, SparkIcon, StopIcon } from "./icons";
import SourceList from "./SourceList";

function AssistantAvatar() {
  return (
    <div className="assistant-avatar" aria-hidden="true">
      <SparkIcon />
    </div>
  );
}

export default function MessageBubble({
  isLoading,
  message,
  onCopy,
  onRegenerate,
  onStop,
}) {
  const isAssistant = message.role === "assistant";
  const showActions = isAssistant && message.content;

  return (
    <article className={`message-row ${message.role}`}>
      {isAssistant ? <AssistantAvatar /> : <div className="message-spacer" aria-hidden="true" />}

      <div className={`message-bubble ${message.role} ${message.isError ? "error" : ""}`}>
        <div className="message-meta">
          <span>{isAssistant ? "JUIT AI" : "You"}</span>
          {message.createdAt ? (
            <time dateTime={new Date(message.createdAt).toISOString()}>
              {formatMessageTime(message.createdAt)}
            </time>
          ) : null}
        </div>

        {message.isStreaming && (
          <div className="typing-status" aria-live="polite">
            <span className="typing-dot" aria-hidden="true" />
            <span>JUIT AI Assistant is writing...</span>
          </div>
        )}

        <div className="message-text">{renderMarkdownBlocks(message.content)}</div>
        <SourceList sources={message.sources} />

        {showActions ? (
          <div className="message-actions" aria-label="Message actions">
            <button type="button" onClick={() => onCopy(message)} aria-label="Copy response">
              <CopyIcon />
              <span>Copy</span>
            </button>
            <button
              type="button"
              onClick={() => onRegenerate(message.id)}
              disabled={isLoading}
              aria-label="Regenerate response"
            >
              <RefreshIcon />
              <span>Regenerate</span>
            </button>
            {message.isStreaming ? (
              <button type="button" onClick={onStop} aria-label="Stop generating">
                <StopIcon />
                <span>Stop</span>
              </button>
            ) : null}
          </div>
        ) : null}
      </div>
    </article>
  );
}
