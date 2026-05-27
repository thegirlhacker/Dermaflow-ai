import { ChatRequest, ChatResponse, ChatSession, Message } from "@/types/chat";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function createNewSession(): Promise<string> {
  const res = await fetch(`${API_BASE_URL}/new-chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Failed to create new session");
  const data = await res.json();
  return data.session_id;
}

export async function getSessions(): Promise<ChatSession[]> {
  const res = await fetch(`${API_BASE_URL}/sessions`);
  if (!res.ok) throw new Error("Failed to fetch sessions");
  const data = await res.json();
  return data.sessions;
}

export async function getSessionHistory(sessionId: string): Promise<Message[]> {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}`);
  if (!res.ok) throw new Error("Failed to fetch session history");
  const data = await res.json();
  
  return data.session.history.map((msg: { role: "user" | "assistant"; content: string }, i: number) => ({
    id: `msg-${i}`,
    role: msg.role,
    content: msg.content
  }));
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: request.session_id,
      query: request.query,
      condition_hint: request.condition_hint === "none" ? null : request.condition_hint,
      image_base64: request.image_base64,
    }),
  });
  if (!res.ok) throw new Error("Failed to send chat message");
  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
