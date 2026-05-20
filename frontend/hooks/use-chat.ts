import { useState, useCallback, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { Message, ChatSession } from "@/types/chat";
import { createNewSession, sendChatMessage } from "@/lib/api";

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Record<string, Message[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize a new session if none exists
  useEffect(() => {
    if (!currentSessionId && sessions.length === 0) {
      handleNewChat();
    }
  }, [currentSessionId, sessions.length]);

  const handleNewChat = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const sessionId = await createNewSession();
      setCurrentSessionId(sessionId);
      setSessions((prev) => [{ id: sessionId, preview: "New Chat" }, ...prev]);
      setMessages((prev) => ({ ...prev, [sessionId]: [] }));
    } catch (err) {
      setError("Failed to create a new session.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendMessage = useCallback(
    async (query: string, condition_hint: string) => {
      if (!currentSessionId || !query.trim()) return;

      const userMessageId = uuidv4();
      const userMessage: Message = { id: userMessageId, role: "user", content: query };

      setMessages((prev) => ({
        ...prev,
        [currentSessionId]: [...(prev[currentSessionId] || []), userMessage],
      }));

      // Update session preview if it's the first message
      setSessions((prev) =>
        prev.map((s) => {
          if (s.id === currentSessionId && s.preview === "New Chat") {
            const preview = query.split(" ").slice(0, 3).join(" ") + "...";
            return { ...s, preview };
          }
          return s;
        })
      );

      setIsLoading(true);
      setError(null);

      try {
        const response = await sendChatMessage({
          session_id: currentSessionId,
          query,
          condition_hint,
        });

        const assistantMessage: Message = {
          id: uuidv4(),
          role: "assistant",
          content: response.response,
          sources: response.sources,
        };

        setMessages((prev) => ({
          ...prev,
          [currentSessionId]: [...(prev[currentSessionId] || []), assistantMessage],
        }));
      } catch (err) {
        setError("Failed to fetch response. Please try again.");
      } finally {
        setIsLoading(false);
      }
    },
    [currentSessionId]
  );

  return {
    sessions,
    currentSessionId,
    setCurrentSessionId,
    messages: currentSessionId ? messages[currentSessionId] || [] : [],
    isLoading,
    error,
    handleNewChat,
    sendMessage,
  };
}
