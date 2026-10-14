import { Component, input, output } from '@angular/core';

import { Source } from '../../core/api/api.models';
import { AssistantMessage } from '../../core/chat/chat-store';

/** Bulle de l'assistant : texte avec renvois numérotés, puis une puce par source citée. */
@Component({
  selector: 'app-assistant-reply',
  template: `
    <div class="bubble">
      <!-- Sur une seule ligne : aucun espace parasite entre le texte et les renvois. -->
      <p class="answer">@for (segment of message().segments; track $index) {@if (segment.kind === 'text') {<span>{{ segment.text }}</span>}@if (segment.kind === 'cite') {<span class="cite"><span class="sr-only">source </span>{{ segment.n }}</span>}}</p>
    </div>
    @if (message().sources.length) {
      <ul class="sources" aria-label="Sources de la réponse">
        @for (source of message().sources; track source.n) {
          <li>
            <button type="button" class="chip" (click)="sourceSelected.emit(source)">
              <span class="n">{{ source.n }}</span>{{ source.title }}, p. {{ source.page }}
            </button>
          </li>
        }
      </ul>
    }
  `,
  styles: `
    :host {
      display: flex;
      flex-direction: column;
      gap: var(--space-2);
      max-width: 88%;
    }
    .bubble {
      padding: var(--space-4);
      border: 1px solid var(--line);
      border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm);
      background: var(--surface-raised);
    }
    .answer {
      white-space: pre-line;
      overflow-wrap: anywhere;
    }
    .sources {
      display: flex;
      flex-wrap: wrap;
      gap: var(--space-1);
      margin: 0;
      padding: 0 0 0 var(--space-1);
      list-style: none;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      gap: var(--space-2);
      min-height: 32px;
      padding: 0 10px;
      border: none;
      border-radius: var(--radius-sm);
      background: var(--saone-soft);
      color: var(--ink);
      font: 600 13px/16px var(--font-body);
      cursor: pointer;
    }
    .n {
      font: 500 12px/1 var(--font-mono);
      color: var(--saone);
    }
    @media (max-width: 600px) {
      :host {
        max-width: 100%;
      }
    }
  `,
})
export class AssistantReply {
  readonly message = input.required<AssistantMessage>();
  readonly sourceSelected = output<Source>();
}
