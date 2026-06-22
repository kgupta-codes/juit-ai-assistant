import {
  appVersion,
  formatConversationTime,
  summarizeConversationTitle,
} from "../lib/conversations";
import { CloseIcon, LogoMark, MoonIcon, PlusIcon, SunIcon } from "./icons";

export default function Sidebar({
  activeConversationId,
  conversations,
  isDarkMode,
  isOpen,
  onClose,
  onNewChat,
  onOpenConversation,
  onToggleTheme,
}) {
  return (
    <>
      <button
        className={`sidebar-backdrop${isOpen ? " open" : ""}`}
        type="button"
        aria-label="Close sidebar"
        onClick={onClose}
      />

      <aside
        className={`sidebar${isOpen ? " open" : ""}`}
        aria-label="JUIT AI Assistant navigation"
      >
        <div className="sidebar-brand">
          <LogoMark compact />
          <div className="sidebar-copy">
            <h1>JUIT AI</h1>
            <p>University assistant</p>
          </div>
          <button
            className="sidebar-close"
            type="button"
            aria-label="Close sidebar"
            onClick={onClose}
          >
            <CloseIcon />
          </button>
        </div>

        <button className="sidebar-new-chat" type="button" onClick={onNewChat}>
          <PlusIcon />
          <span>New Chat</span>
        </button>

        <section className="recent-section" aria-label="Recent conversations">
          <div className="recent-heading">Recent</div>

          <div className="recent-list">
            {conversations.length === 0 ? (
              <div className="recent-empty">No conversations yet.</div>
            ) : (
              conversations.map((conversation) => {
                const isActive = conversation.id === activeConversationId;
                const preview =
                  conversation.title !== "New chat"
                    ? conversation.title
                    : summarizeConversationTitle(
                        conversation.messages.find((message) => message.role === "user")
                          ?.content || "New chat",
                      );

                return (
                  <button
                    key={conversation.id}
                    type="button"
                    className={`recent-item${isActive ? " active" : ""}`}
                    onClick={() => onOpenConversation(conversation.id)}
                    aria-current={isActive ? "true" : undefined}
                  >
                    <span className="recent-item-main">
                      <span className="recent-item-title">{preview}</span>
                      <span className="recent-item-time">
                        {formatConversationTime(conversation.updatedAt)}
                      </span>
                    </span>
                  </button>
                );
              })
            )}
          </div>

          <div className="sidebar-footer" aria-label="Sidebar utilities">
            <div className="sidebar-footer-item">
              <span className="sidebar-footer-label">Status</span>
              <span className="status-pill status-pill-dark">Online</span>
            </div>

            <div className="sidebar-footer-item">
              <span className="sidebar-footer-label">Version</span>
              <span className="sidebar-version">{appVersion}</span>
            </div>

            <button
              className="sidebar-theme-toggle"
              type="button"
              onClick={onToggleTheme}
              aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              <span>
                {isDarkMode ? <SunIcon /> : <MoonIcon />}
                {isDarkMode ? "Light mode" : "Dark mode"}
              </span>
            </button>
          </div>
        </section>
      </aside>
    </>
  );
}
