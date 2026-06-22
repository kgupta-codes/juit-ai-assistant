import { renderMarkdownBlocks } from "../lib/markdown";
import { SparkIcon } from "./icons";
import SourceList from "./SourceList";

function AssistantAvatar() {
  return (
    <div className="assistant-avatar" aria-hidden="true">
      <SparkIcon />
    </div>
  );
}

export default function MessageBubble({ message }) {
  const isAssistant = message.role === "assistant";

  return (
    <article className={`message-row ${message.role}`}>
      {isAssistant ? <AssistantAvatar /> : <div className="message-spacer" aria-hidden="true" />}

      <div className={`message-bubble ${message.role} ${message.isError ? "error" : ""}`}>
        {message.isStreaming && (
          <div className="typing-status" aria-live="polite">
            <span className="typing-dot" aria-hidden="true" />
            <span>JUIT AI Assistant is writing...</span>
          </div>
        )}

        <div className="message-text">{renderMarkdownBlocks(message.content)}</div>
        <SourceList sources={message.sources} />
      </div>
    </article>
  );
}
