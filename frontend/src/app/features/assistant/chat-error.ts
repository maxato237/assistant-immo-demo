import { Component, computed, input, output } from '@angular/core';

import { ApiErrorCode } from '../../core/api/api.models';
import { environment } from '../../../environments/environment';

interface ErrorCopy {
  message: string;
  detail?: string;
  canRetry: boolean;
}

const COPY: Record<ApiErrorCode, ErrorCopy> = {
  llm_unavailable: {
    message: "L'assistant est momentanément indisponible. Votre question n'a pas été perdue.",
    canRetry: true,
  },
  network: {
    message: "Impossible de joindre l'assistant. Vérifiez votre connexion, votre question n'a pas été perdue.",
    canRetry: true,
  },
  internal_error: {
    message: 'Une erreur est survenue de notre côté. Votre question n\'a pas été perdue.',
    canRetry: true,
  },
  index_missing: {
    message: "L'assistant n'est pas encore prêt. Réessayez dans un instant.",
    canRetry: true,
  },
  rate_limited: {
    message: "Vous avez posé beaucoup de questions d'affilée. Réessayez dans quelques minutes.",
    detail: 'Limite de la démo : 20 questions par heure.',
    canRetry: false,
  },
  invalid_question: {
    message: 'La question doit faire entre 1 et 500 caractères.',
    canRetry: false,
  },
  demo_paused: {
    message: "La démo a atteint son nombre de questions pour aujourd'hui. Elle revient demain matin.",
    canRetry: false,
  },
};

/** Erreur affichée dans la conversation, à la place de la réponse, avec une action. */
@Component({
  selector: 'app-chat-error',
  template: `
    <div class="bubble" role="alert">
      <p class="message">{{ copy().message }}</p>
      @if (copy().detail) {
        <p class="detail">{{ copy().detail }}</p>
      }
      @if (copy().canRetry) {
        <button type="button" class="button-primary" (click)="retry.emit()">Réessayer</button>
      } @else if (code() === 'demo_paused') {
        <a class="button-primary" [href]="contactUrl" target="_blank" rel="noopener">Demander une démonstration en direct</a>
      }
    </div>
  `,
  styles: `
    :host {
      display: block;
      max-width: 88%;
    }
    .bubble {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
      padding: var(--space-4);
      border: 1px solid var(--line);
      border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm);
      background: var(--surface-raised);
    }
    .message {
      color: var(--danger);
    }
    .detail {
      font-size: 14px;
      line-height: 20px;
      color: var(--ink-muted);
    }
  `,
})
export class ChatError {
  readonly code = input.required<ApiErrorCode>();
  readonly retry = output<void>();
  protected readonly copy = computed(() => COPY[this.code()]);
  protected readonly contactUrl = environment.contactUrl;
}
