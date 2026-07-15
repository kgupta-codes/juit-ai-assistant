import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import Composer from "./components/Composer";
import ConversationList from "./components/ConversationList";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import WelcomeState from "./components/WelcomeState";
import {
  activeConversationStorageKey,
  conversationStorageKey,
  createConversation,
  loadAppState,
  maxStoredConversations,
  nextId,
  summarizeConversationTitle,
  themeStorageKey,
  timestamp,
} from "./lib/conversations";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV
    ? "http://127.0.0.1:8000"
    : "https://juit-ai-assistant-production.up.railway.app");

const examplePrompts = [
  {
    label: "Admissions",
    question: "Tell me about admissions at JUIT.",
  },
  {
    label: "Placements",
    question: "Tell me about placements at JUIT.",
  },
  {
    label: "Hostels",
    question: "What hostel facilities are available at JUIT?",
  },
  {
    label: "Departments",
    question: "What departments does JUIT have?",
  },
  {
    label: "Scholarships",
    question: "What scholarships are available at JUIT?",
  },
  {
    label: "Research Centers",
    question: "What research centers are available at JUIT?",
  },
];

const EMPTY_MESSAGES = [];
const sidebarBreakpoint = 1120;

function App() {
  const [initialState] = useState(() => loadAppState());
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }

    return window.localStorage.getItem(themeStorageKey) === "dark";
  });
  const [conversations, setConversations] = useState(initialState.conversations);
  const [activeConversationId, setActiveConversationId] = useState(
    initialState.activeConversationId,
  );
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const activeRequestRef = useRef(0);
  const abortControllerRef = useRef(null);
  const streamTimerRef = useRef(null);

  const activeConversation = useMemo(
    () =>
      conversations.find(
        (conversation) => conversation.id === activeConversationId,
      ) || conversations[0],
    [activeConversationId, conversations],
  );

  const messages = activeConversation?.messages ?? EMPTY_MESSAGES;
  const visibleConversations = conversations
    .filter((conversation) => conversation.messages.length > 0)
    .sort((a, b) => b.updatedAt - a.updatedAt)
    .slice(0, maxStoredConversations);
  const hasMessages = messages.length > 0;

  const persistConversation = useCallback((conversationId, updater) => {
    setConversations((currentConversations) =>
      currentConversations.map((conversation) =>
        conversation.id === conversationId ? updater(conversation) : conversation,
      ),
    );
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = isDarkMode ? "dark" : "light";
    window.localStorage.setItem(themeStorageKey, isDarkMode ? "dark" : "light");
  }, [isDarkMode]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  useEffect(() => {
    window.localStorage.setItem(
      conversationStorageKey,
      JSON.stringify(conversations.slice(0, maxStoredConversations)),
    );
    window.localStorage.setItem(activeConversationStorageKey, activeConversationId);
  }, [activeConversationId, conversations]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
  }, [query]);

  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth > sidebarBreakpoint) {
        setIsSidebarOpen(false);
      }
    };

    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  useEffect(
    () => () => {
      if (streamTimerRef.current) {
        clearTimeout(streamTimerRef.current);
      }
    },
    [],
  );

  const focusComposer = () => {
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
    });
  };

  const cancelStream = useCallback(() => {
    if (streamTimerRef.current) {
      clearTimeout(streamTimerRef.current);
      streamTimerRef.current = null;
    }
  }, []);

  const stopGenerating = useCallback(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    activeRequestRef.current = 0;
    cancelStream();
    setIsLoading(false);

    if (activeConversationId) {
      persistConversation(activeConversationId, (conversation) => ({
        ...conversation,
        messages: conversation.messages.map((message) =>
          message.isStreaming ? { ...message, isStreaming: false } : message,
        ),
        updatedAt: timestamp(),
      }));
    }
  }, [activeConversationId, cancelStream, persistConversation]);

  const streamAssistantReply = useCallback((conversationId, answer, sources) => {
    cancelStream();

    const fullText = answer || "I could not find that information in the JUIT knowledge base.";
    const assistantMessageId = nextId("assistant");
    const chunkSize = Math.max(2, Math.ceil(fullText.length / 42));
    let cursor = 0;

    persistConversation(conversationId, (conversation) => ({
      ...conversation,
      messages: [
        ...conversation.messages,
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          sources,
          isStreaming: true,
          createdAt: timestamp(),
        },
      ],
      updatedAt: timestamp(),
    }));

    const tick = () => {
      const nextCursor = Math.min(fullText.length, cursor + chunkSize);
      const nextContent = fullText.slice(0, nextCursor);

      persistConversation(conversationId, (conversation) => ({
        ...conversation,
        messages: conversation.messages.map((message) =>
          message.id === assistantMessageId
            ? {
                ...message,
                content: nextContent,
                isStreaming: nextCursor < fullText.length,
              }
            : message,
        ),
        updatedAt: timestamp(),
      }));

      cursor = nextCursor;

      if (cursor < fullText.length) {
        streamTimerRef.current = window.setTimeout(tick, 16);
      } else {
        streamTimerRef.current = null;
        setIsLoading(false);
      }
    };

    streamTimerRef.current = window.setTimeout(tick, 180);
  }, [cancelStream, persistConversation]);

  const startNewChat = () => {
    if (activeConversation && activeConversation.messages.length === 0 && !query.trim()) {
      setError("");
      setIsLoading(false);
      setIsSidebarOpen(false);
      activeRequestRef.current = 0;
      focusComposer();
      return;
    }

    const draftConversation = createConversation();
    setConversations((currentConversations) => [
      draftConversation,
      ...currentConversations.filter((conversation) => conversation.id !== draftConversation.id),
    ]);
    setActiveConversationId(draftConversation.id);
    setQuery("");
    setError("");
    setIsLoading(false);
    setIsSidebarOpen(false);
    activeRequestRef.current = 0;
    focusComposer();
  };

  const askQuestion = async (overrideQuery = query, options = {}) => {
    const trimmedQuery = overrideQuery.trim();

    if (!trimmedQuery || isLoading) {
      return;
    }

    const requestId = timestamp();
    activeRequestRef.current = requestId;
    const userMessage = {
      id: nextId("user"),
      role: "user",
      content: trimmedQuery,
      sources: [],
      createdAt: timestamp(),
    };
    const conversationId = options.conversationId || activeConversation?.id || `conv-${requestId}`;
    const currentConversation =
      conversations.find((conversation) => conversation.id === conversationId) ||
      activeConversation;
    const shouldAppendUser = options.appendUser !== false;

    if (options.replaceFromIndex !== undefined) {
      persistConversation(conversationId, (conversation) => ({
        ...conversation,
        messages: conversation.messages.slice(0, options.replaceFromIndex),
        updatedAt: timestamp(),
      }));
      setActiveConversationId(conversationId);
    } else if (!currentConversation || currentConversation.messages.length === 0) {
      const nextConversation = currentConversation
        ? {
            ...currentConversation,
            title: summarizeConversationTitle(trimmedQuery),
            messages: shouldAppendUser ? [userMessage] : currentConversation.messages,
            updatedAt: timestamp(),
          }
        : {
            id: conversationId,
            title: summarizeConversationTitle(trimmedQuery),
            messages: shouldAppendUser ? [userMessage] : [],
            updatedAt: timestamp(),
          };

      setConversations((currentConversations) => [
        nextConversation,
        ...currentConversations.filter(
          (conversation) => conversation.id !== nextConversation.id,
        ),
      ]);
      setActiveConversationId(nextConversation.id);
    } else {
      persistConversation(conversationId, (conversation) => ({
        ...conversation,
        title:
          conversation.title === "New chat"
            ? summarizeConversationTitle(trimmedQuery)
            : conversation.title,
        messages: shouldAppendUser
          ? [...conversation.messages, userMessage]
          : conversation.messages,
        updatedAt: timestamp(),
      }));
    }

    setQuery("");
    setError("");
    setIsLoading(true);
    setIsSidebarOpen(false);
    abortControllerRef.current?.abort();
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: trimmedQuery, session_id: conversationId }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();

      if (activeRequestRef.current !== requestId) {
        return;
      }

      streamAssistantReply(
        conversationId,
        data.answer,
        Array.isArray(data.sources) ? data.sources : [],
      );
    } catch (requestError) {
      if (requestError.name === "AbortError") {
        return;
      }

      if (activeRequestRef.current !== requestId) {
        return;
      }

      cancelStream();
      setIsLoading(false);
      setError(
        "I could not reach the JUIT AI service. Please check that the backend is running and try again.",
      );

      persistConversation(conversationId, (conversation) => ({
        ...conversation,
        messages: [
          ...conversation.messages,
          {
            id: nextId("error"),
            role: "assistant",
            content:
              "I could not reach the JUIT AI service. Please check that the backend is running and try again.",
            sources: [],
            isError: true,
            createdAt: timestamp(),
          },
        ],
        updatedAt: timestamp(),
      }));

      console.error(requestError);
    } finally {
      if (activeRequestRef.current === requestId) {
        abortControllerRef.current = null;
      }
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const openConversation = (conversationId) => {
    setActiveConversationId(conversationId);
    setQuery("");
    setError("");
    setIsLoading(false);
    setIsSidebarOpen(false);
    activeRequestRef.current = 0;
    cancelStream();
    focusComposer();
  };

  const copyMessage = async (message) => {
    try {
      await navigator.clipboard.writeText(message.content);
    } catch {
      setError("I could not copy the response. Please select the text manually.");
    }
  };

  const regenerateMessage = (messageId) => {
    const conversation = activeConversation;
    const assistantIndex = conversation?.messages.findIndex(
      (message) => message.id === messageId,
    );

    if (!conversation || assistantIndex <= 0) {
      return;
    }

    const previousUser = [...conversation.messages]
      .slice(0, assistantIndex)
      .reverse()
      .find((message) => message.role === "user");

    if (!previousUser) {
      return;
    }

    askQuestion(previousUser.content, {
      appendUser: false,
      conversationId: conversation.id,
      replaceFromIndex: assistantIndex,
    });
  };

  const renameConversation = (conversationId, title) => {
    persistConversation(conversationId, (conversation) => ({
      ...conversation,
      title,
      updatedAt: timestamp(),
    }));
  };

  const deleteConversation = (conversationId) => {
    setConversations((currentConversations) => {
      const nextConversations = currentConversations.filter(
        (conversation) => conversation.id !== conversationId,
      );

      if (nextConversations.length > 0) {
        if (conversationId === activeConversationId) {
          setActiveConversationId(nextConversations[0].id);
        }
        return nextConversations;
      }

      const draftConversation = createConversation();
      setActiveConversationId(draftConversation.id);
      return [draftConversation];
    });
  };

  return (
    <div className="app-shell">
      <Sidebar
        activeConversationId={activeConversationId}
        conversations={visibleConversations}
        isDarkMode={isDarkMode}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onDeleteConversation={deleteConversation}
        onNewChat={startNewChat}
        onOpenConversation={openConversation}
        onRenameConversation={renameConversation}
        onToggleTheme={() => setIsDarkMode((current) => !current)}
      />

      <main className="workspace">
        <Topbar
          isDarkMode={isDarkMode}
          onToggleSidebar={() => setIsSidebarOpen((current) => !current)}
          onToggleTheme={() => setIsDarkMode((current) => !current)}
        />

        <section className="conversation-panel" aria-label="Conversation area">
          {!hasMessages ? (
            <WelcomeState
              prompts={examplePrompts}
              isLoading={isLoading}
              onAsk={askQuestion}
            />
          ) : null}

          <ConversationList
            isLoading={isLoading}
            messages={messages}
            messagesEndRef={messagesEndRef}
            onCopyMessage={copyMessage}
            onRegenerateMessage={regenerateMessage}
            onStopGenerating={stopGenerating}
          />

          <Composer
            disabled={isLoading}
            error={error}
            onChange={setQuery}
            onKeyDown={handleKeyDown}
            onStop={stopGenerating}
            onSubmit={askQuestion}
            query={query}
            textareaRef={textareaRef}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
