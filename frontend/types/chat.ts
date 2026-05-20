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
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
}

export interface ChatSession {
  id: string;
  preview: string; // first 2-3 words of first user query
}
