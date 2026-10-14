import { Injectable, inject, signal } from '@angular/core';
import { retry, switchMap, tap } from 'rxjs';

import { AgencyDocument } from '../api/api.models';
import { AssistantApi } from '../api/assistant-api';

/** Au-delà de ce délai sans réponse, on prévient que le serveur gratuit se réveille. */
export const WAKE_NOTICE_DELAY_MS = 2000;
const HEALTH_RETRIES = 20;
const HEALTH_RETRY_DELAY_MS = 3000;

export type ServerState = 'checking' | 'waking' | 'ready' | 'unavailable';

/**
 * Réveille le serveur dès l'ouverture de la page (Render gratuit s'endort après
 * 15 min) et charge la liste des documents de l'agence.
 */
@Injectable({ providedIn: 'root' })
export class ServerStatus {
  private readonly api = inject(AssistantApi);
  private started = false;

  readonly state = signal<ServerState>('checking');
  readonly documents = signal<AgencyDocument[]>([]);

  start(): void {
    if (this.started) {
      return;
    }
    this.started = true;
    const wakeNotice = setTimeout(() => {
      if (this.state() === 'checking') {
        this.state.set('waking');
      }
    }, WAKE_NOTICE_DELAY_MS);

    this.api
      .health()
      .pipe(
        retry({ count: HEALTH_RETRIES, delay: HEALTH_RETRY_DELAY_MS }),
        tap((health) => {
          clearTimeout(wakeNotice);
          this.state.set(health.status === 'ok' ? 'ready' : 'unavailable');
        }),
        switchMap(() => this.api.documents()),
      )
      .subscribe({
        next: (documents) => this.documents.set(documents),
        error: () => {
          clearTimeout(wakeNotice);
          if (this.state() !== 'ready') {
            this.state.set('unavailable');
          }
        },
      });
  }
}
