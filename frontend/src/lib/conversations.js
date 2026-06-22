export const themeStorageKey = "juit-ai-theme";
export const conversationStorageKey = "juit-ai-conversations";
export const activeConversationStorageKey = "juit-ai-active-conversation";
export const appVersion = "v1.0";
export const maxStoredConversations = 8;

let uniqueCounter = 0;

export function nextId(prefix) {
  uniqueCounter += 1;
  return `${prefix}-${Date.now()}-${uniqueCounter}`;
}

export function timestamp() {
  return Date.now();
}

export function formatConversationTime(value) {
  if (!value) {
    return "Just now";
  }

  const date = new Date(value);
  const now = new Date();
  const isSameDay = date.toDateString() === now.toDateString();

  if (isSameDay) {
    return date.toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  return date.toLocaleDateString([], {
    month: "short",
    day: "numeric",
  });
}

export function readJSON(key, fallback) {
  if (typeof window === "undefined") {
    return fallback;
  }

  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function createConversation() {
  const now = timestamp();
  return {
    id: nextId("conv"),
    title: "New chat",
    messages: [],
    updatedAt: now,
  };
}

export function summarizeConversationTitle(text) {
  const cleaned = text.replace(/\s+/g, " ").trim();
  return cleaned.length <= 44 ? cleaned : `${cleaned.slice(0, 43)}...`;
}

export function loadAppState() {
  const storedConversations = readJSON(conversationStorageKey, []);
  const conversations = Array.isArray(storedConversations)
    ? storedConversations.filter(
        (conversation) =>
          conversation &&
          typeof conversation.id === "string" &&
          Array.isArray(conversation.messages),
      )
    : [];

  const activeConversationId =
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem(activeConversationStorageKey);

  if (conversations.length === 0) {
    const draftConversation = createConversation();
    return {
      conversations: [draftConversation],
      activeConversationId: draftConversation.id,
    };
  }

  return {
    conversations,
    activeConversationId:
      conversations.find((conversation) => conversation.id === activeConversationId)
        ?.id || conversations[0].id,
  };
}

export function sourceKey(source, index) {
  return `${source?.url || source?.canonical_url || source?.title || "source"}-${index}`;
}

export function getDomain(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "juit.ac.in";
  }
}
