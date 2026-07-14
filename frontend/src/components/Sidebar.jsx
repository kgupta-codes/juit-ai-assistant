import { useMemo, useState } from "react";
import {
  appVersion,
  formatConversationTime,
  summarizeConversationTitle,
} from "../lib/conversations";
import {
  CheckIcon,
  CloseIcon,
  EditIcon,
  LogoMark,
  MoonIcon,
  PlusIcon,
  SearchIcon,
  SunIcon,
  TrashIcon,
} from "./icons";

export default function Sidebar({
  activeConversationId,
  conversations,
  isDarkMode,
  isOpen,
  onClose,
  onDeleteConversation,
  onNewChat,
  onOpenConversation,
  onRenameConversation,
  onToggleTheme,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [draftTitle, setDraftTitle] = useState("");

  const filteredConversations = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();

    if (!normalizedQuery) {
      return conversations;
    }

    return conversations.filter((conversation) => {
      const haystack = [
        conversation.title,
        ...conversation.messages.map((message) => message.content),
      ]
        .join(" ")
        .toLowerCase();

      return haystack.includes(normalizedQuery);
    });
  }, [conversations, searchQuery]);

  const startRename = (conversation, preview) => {
    setEditingId(conversation.id);
    setDraftTitle(preview);
  };

  const submitRename = (conversationId) => {
    const nextTitle = draftTitle.trim();
    if (nextTitle) {
      onRenameConversation(conversationId, nextTitle);
    }
    setEditingId(null);
    setDraftTitle("");
  };

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

          <label className="recent-search">
            <SearchIcon />
            <span className="sr-only">Search chats</span>
            <input
              type="search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search chats"
            />
          </label>

          <div className="recent-list">
            {filteredConversations.length === 0 ? (
              <div className="recent-empty">
                {conversations.length === 0 ? "No conversations yet." : "No matching chats."}
              </div>
            ) : (
              filteredConversations.map((conversation) => {
                const isActive = conversation.id === activeConversationId;
                const preview =
                  conversation.title !== "New chat"
                    ? conversation.title
                    : summarizeConversationTitle(
                        conversation.messages.find((message) => message.role === "user")
                          ?.content || "New chat",
                      );

                return (
                  <div
                    key={conversation.id}
                    className={`recent-item${isActive ? " active" : ""}`}
                  >
                    {editingId === conversation.id ? (
                      <form
                        className="recent-edit-form"
                        onSubmit={(event) => {
                          event.preventDefault();
                          submitRename(conversation.id);
                        }}
                      >
                        <input
                          value={draftTitle}
                          onChange={(event) => setDraftTitle(event.target.value)}
                          onKeyDown={(event) => {
                            if (event.key === "Escape") {
                              setEditingId(null);
                              setDraftTitle("");
                            }
                          }}
                          aria-label="Rename chat"
                          autoFocus
                        />
                        <button type="submit" aria-label="Save chat name">
                          <CheckIcon />
                        </button>
                      </form>
                    ) : (
                      <>
                        <button
                          type="button"
                          className="recent-item-open"
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
                        <span className="recent-actions">
                          <button
                            type="button"
                            onClick={() => startRename(conversation, preview)}
                            aria-label={`Rename chat: ${preview}`}
                          >
                            <EditIcon />
                          </button>
                          <button
                            type="button"
                            onClick={() => onDeleteConversation(conversation.id)}
                            aria-label={`Delete chat: ${preview}`}
                          >
                            <TrashIcon />
                          </button>
                        </span>
                      </>
                    )}
                  </div>
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
