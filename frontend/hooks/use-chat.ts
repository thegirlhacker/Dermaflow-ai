import { useState, useCallback, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { Message, ChatSession } from "@/types/chat";
import { sendChatMessage, getSessions, getSessionHistory, generateSessionTitle } from "@/lib/api";

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Record<string, Message[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fetchedRef = useRef(false);

  const handleNewChat = useCallback(() => {
    const sessionId = uuidv4();
    setCurrentSessionId(sessionId);
    setSessions((prev) => {
      if (prev.length > 0 && prev[0].title === "New Chat") {
        return prev;
      }
      return [{ session_id: sessionId, title: "New Chat" }, ...prev];
    });
    setMessages((prev) => ({ ...prev, [sessionId]: [] }));
  }, []);

  // Fetch sessions on mount
  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    
    async function loadSessions() {
      try {
        const loadedSessions = await getSessions();
        if (loadedSessions.length > 0) {
          setSessions(loadedSessions);
          setCurrentSessionId(loadedSessions[0].session_id);
        } else {
          handleNewChat();
        }
      } catch (err) {
        console.error("Failed to load sessions", err);
      }
    }
    loadSessions();
  }, [handleNewChat]);

  // Fetch history when currentSessionId changes
  useEffect(() => {
    if (currentSessionId && !messages[currentSessionId]) {
      let mounted = true;
      async function loadHistory() {
        try {
          setIsLoading(true);
          const history = await getSessionHistory(currentSessionId as string);
          if (mounted) {
            setMessages((prev) => ({ ...prev, [currentSessionId as string]: history }));
          }
        } catch (err) {
          console.error("Failed to load history", err);
        } finally {
          if (mounted) setIsLoading(false);
        }
      }
      loadHistory();
      return () => { mounted = false; };
    }
  }, [currentSessionId, messages]);

  const switchSession = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId);
  }, []);

  const sendMessage = useCallback(
    async (query: string, condition_hint: string, image_base64?: string) => {
      if (!currentSessionId || (!query.trim() && !image_base64)) return;

      const userMessageId = uuidv4();
      const userMessage: Message = { id: userMessageId, role: "user", content: query, image_base64 };

      setMessages((prev) => ({
        ...prev,
        [currentSessionId]: [...(prev[currentSessionId] || []), userMessage],
      }));

      setIsLoading(true);
      setError(null);

      // Trigger parallel title generation if this is a new chat
      const activeSession = sessions.find((s) => s.session_id === currentSessionId);
      const isNewSession = activeSession && activeSession.title === "New Chat";
      if (isNewSession) {
        generateSessionTitle(currentSessionId, query || "Analyze image")
          .then((title) => {
            setSessions((prev) =>
              prev.map((s) =>
                s.session_id === currentSessionId ? { ...s, title } : s
              )
            );
          })
          .catch((err) => {
            console.error("Parallel title generation error:", err);
          });
      }

      try {
        const response = await sendChatMessage({
          session_id: currentSessionId,
          query: query || "Analyze this image.",
          condition_hint,
          image_base64,
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
        
        // Refresh sessions to get the updated title
        const updatedSessions = await getSessions();
        setSessions((prev) => {
          // keep the new chat if it's currently active and not in DB yet
          const activeSession = prev.find(s => s.session_id === currentSessionId);
          if (activeSession && activeSession.title === "New Chat" && !updatedSessions.find((s: ChatSession) => s.session_id === currentSessionId)) {
             return [activeSession, ...updatedSessions];
          }
          return updatedSessions;
        });
      } catch (err) {
        console.error(err);
        setError("Failed to fetch response. Please try again.");
      } finally {
        setIsLoading(false);
      }
    },
    [currentSessionId, sessions]
  );

  return {
    sessions,
    currentSessionId,
    setCurrentSessionId: switchSession,
    messages: currentSessionId ? messages[currentSessionId] || [] : [],
    isLoading,
    error,
    handleNewChat,
    sendMessage,
  };
}
