import MessageBubble from "./MessageBubble";
import { SparkIcon } from "./icons";

export default function ConversationList({ isLoading, messages, messagesEndRef }) {
  return (
    <div className="conversation-list" aria-live="polite">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
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
