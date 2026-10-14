import { Injectable, computed, inject, signal } from '@angular/core';
import { Subscription } from 'rxjs';

import {
  ApiErrorCode,
  HistoryMessage,
  MAX_HISTORY_CONTENT_CHARS,
  MAX_HISTORY_MESSAGES,
  Source,
} from '../api/api.models';
import { AssistantApi, toApiErrorCode } from '../api/assistant-api';
import { AnswerSegment, parseCitations } from './citations';

export interface UserMessage {
  id: number;
  role: 'user';
  text: string;
}

export interface AssistantMessage {
  id: number;
  role: 'assistant';
  text: string;
  segments: AnswerSegment[];
  sources: Source[];
}

export type ChatMessage = UserMessage | AssistantMessage;

export interface ChatFailure {
  code: ApiErrorCode;
  question: string;
}

/** Conversation en cours. Au niveau de l'application : elle survit à un passage sur une autre page. */
@Injectable({ providedIn: 'root' })
export class ChatStore {
  private readonly api = inject(AssistantApi);
  private nextId = 1;
  private request?: Subscription;

  readonly messages = signal<ChatMessage[]>([]);
  readonly pending = signal(false);
  readonly failure = signal<ChatFailure | null>(null);
  readonly hasStarted = computed(() => this.messages().length > 0);

  ask(question: string): void {
    const text = question.trim();
    if (!text || this.pending()) {
      return;
    }
    const history = buildHistory(this.messages());
    this.messages.update((messages) => [...messages, { id: this.nextId++, role: 'user', text }]);
    this.send(text, history);
  }

  /** Renvoie la question qui a échoué, sans la dupliquer dans la conversation. */
  retry(): void {
    const failure = this.failure();
    if (!failure || this.pending()) {
      return;
    }
    this.send(failure.question, buildHistory(this.messages().slice(0, -1)));
  }

  reset(): void {
    this.request?.unsubscribe();
    this.messages.set([]);
    this.pending.set(false);
    this.failure.set(null);
  }

  private send(question: string, history: HistoryMessage[]): void {
    this.pending.set(true);
    this.failure.set(null);
    this.request = this.api.ask({ question, history }).subscribe({
      next: (response) => {
        const known = new Set(response.sources.map((source) => source.n));
        this.messages.update((messages) => [
          ...messages,
          {
            id: this.nextId++,
            role: 'assistant',
            text: response.answer,
            segments: parseCitations(response.answer, known),
            sources: response.sources,
          },
        ]);
        this.pending.set(false);
      },
      error: (error: unknown) => {
        this.failure.set({ code: toApiErrorCode(error), question });
        this.pending.set(false);
      },
    });
  }
}

/**
 * Derniers échanges complets envoyés au serveur pour les questions de suivi
 * ("et celui-là ?"). Une question restée sans réponse (erreur) n'en fait pas partie.
 */
export function buildHistory(messages: readonly ChatMessage[]): HistoryMessage[] {
  const pairs: HistoryMessage[] = [];
  messages.forEach((message, i) => {
    const next = messages[i + 1];
    if (message.role === 'user' && next?.role === 'assistant') {
      pairs.push(toHistory(message), toHistory(next));
    }
  });
  return pairs.slice(-(MAX_HISTORY_MESSAGES - 2));
}

function toHistory(message: ChatMessage): HistoryMessage {
  return { role: message.role, content: message.text.slice(0, MAX_HISTORY_CONTENT_CHARS) };
}
