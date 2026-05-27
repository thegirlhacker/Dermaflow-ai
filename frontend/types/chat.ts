export interface SourceChunk {
  source: string;
  condition: string;
  score: number;
  preview: string;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  agent_used: string;
  sources: SourceChunk[];
  confident: boolean;
  latency_ms: number;
}

export interface ChatRequest {
  session_id: string;
  query: string;
  condition_hint: string | null;
  image_base64?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  image_base64?: string;
}

export interface ChatSession {
  session_id: string;
  title: string;
  updated_at?: string;
}
