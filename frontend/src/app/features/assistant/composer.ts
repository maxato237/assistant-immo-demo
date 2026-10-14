import { Component, input, output, signal } from '@angular/core';

import { MAX_QUESTION_CHARS } from '../../core/api/api.models';

/** Champ de question. Entrée envoie, Maj+Entrée va à la ligne. */
@Component({
  selector: 'app-composer',
  template: `
    <form class="form" (submit)="submit($event)">
      <label class="sr-only" for="question">Votre question</label>
      <div class="field">
        <textarea
          id="question"
          rows="1"
          [attr.maxlength]="maxChars"
          [value]="text()"
          (input)="text.set($any($event.target).value)"
          (keydown.enter)="onEnter($any($event))"
          placeholder="Posez votre question sur nos biens, honoraires ou visites"
        ></textarea>
        <button type="submit" class="send" aria-label="Envoyer la question" [disabled]="busy() || !text().trim()">
          <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 19V5" />
            <path d="M5 12l7-7 7 7" />
          </svg>
        </button>
      </div>
      <p class="hint">Réponses générées par IA à partir des documents de l'agence. Vérifiez les points importants auprès de l'agence.</p>
    </form>
  `,
  styles: `
    .form {
      display: flex;
      flex-direction: column;
      gap: var(--space-2);
    }
    .field {
      display: flex;
      align-items: flex-end;
      gap: var(--space-2);
      padding: 6px 6px 6px var(--space-4);
      border: 1px solid var(--ink-muted);
      border-radius: var(--radius-lg);
      background: var(--surface-raised);
    }
    .field:focus-within {
      outline: 2px solid var(--saone);
      outline-offset: 2px;
    }
    textarea {
      flex: 1 1 auto;
      min-height: 32px;
      max-height: 160px;
      padding: 8px 0;
      border: none;
      outline: none;
      resize: none;
      field-sizing: content;
      background: transparent;
    }
    .send {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 44px;
      height: 44px;
      flex-shrink: 0;
      border: none;
      border-radius: var(--radius-full);
      background: var(--saone);
      color: var(--on-saone);
      cursor: pointer;
    }
    .send:disabled {
      opacity: 0.45;
      cursor: default;
    }
    .hint {
      text-align: center;
      font-size: 12px;
      line-height: 16px;
      color: var(--ink-muted);
    }
  `,
})
export class Composer {
  readonly busy = input(false);
  readonly submitted = output<string>();

  protected readonly maxChars = MAX_QUESTION_CHARS;
  protected readonly text = signal('');

  protected onEnter(event: KeyboardEvent): void {
    if (event.shiftKey || event.isComposing) {
      return;
    }
    event.preventDefault();
    this.send();
  }

  protected submit(event: Event): void {
    event.preventDefault();
    this.send();
  }

  private send(): void {
    const question = this.text().trim();
    if (!question || this.busy()) {
      return;
    }
    this.submitted.emit(question);
    this.text.set('');
  }
}
