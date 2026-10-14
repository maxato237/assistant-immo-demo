// Contrat de l'API Flask (backend/app/api). Garder synchronisé avec routes.py.

export interface HistoryMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AskRequest {
  question: string;
  history: HistoryMessage[];
}

export interface Source {
  n: number;
  doc_id: string;
  title: string;
  page: number;
  excerpt: string;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
  latency_ms: number;
}

export interface AgencyDocument {
  id: string;
  title: string;
  pages: number;
  url: string;
}

export interface Health {
  status: 'ok' | 'index_missing';
  documents: number;
  chunks: number;
}

export type ApiErrorCode =
  | 'invalid_question'
  | 'rate_limited'
  | 'demo_paused'
  | 'index_missing'
  | 'llm_unavailable'
  | 'internal_error'
  | 'network';

export const MAX_QUESTION_CHARS = 500;
export const MAX_HISTORY_MESSAGES = 6;
export const MAX_HISTORY_CONTENT_CHARS = 2000;
