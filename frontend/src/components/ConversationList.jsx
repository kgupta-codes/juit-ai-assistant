import MessageBubble from "./MessageBubble";
import { SparkIcon } from "./icons";

export default function ConversationList({
  isLoading,
  messages,
  messagesEndRef,
  onCopyMessage,
  onRegenerateMessage,
  onStopGenerating,
}) {
  return (
    <div className="conversation-list" aria-live="polite" aria-busy={isLoading}>
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          isLoading={isLoading}
          message={message}
          onCopy={onCopyMessage}
          onRegenerate={onRegenerateMessage}
          onStop={onStopGenerating}
        />
      ))}

      {isLoading && (
        <article className="message-row assistant">
          <div className="assistant-avatar" aria-hidden="true">
            <SparkIcon />
          </div>
          <div className="message-bubble assistant loading">
            <span className="typing-dots" aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
            <span>Searching JUIT sources...</span>
          </div>
        </article>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
