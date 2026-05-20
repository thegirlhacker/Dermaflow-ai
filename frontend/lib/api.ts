import { ChatRequest, ChatResponse } from "@/types/chat";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createNewSession(): Promise<string> {
  const res = await fetch(`${API_BASE_URL}/new-chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Failed to create new session");
  const data = await res.json();
  return data.session_id;
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: request.session_id,
      query: request.query,
      condition_hint: request.condition_hint === "none" ? null : request.condition_hint,
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
