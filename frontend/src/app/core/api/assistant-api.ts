import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { AgencyDocument, ApiErrorCode, AskRequest, AskResponse, Health } from './api.models';

const KNOWN_CODES: ApiErrorCode[] = [
  'invalid_question',
  'rate_limited',
  'demo_paused',
  'index_missing',
  'llm_unavailable',
  'internal_error',
];

@Injectable({ providedIn: 'root' })
export class AssistantApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  health(): Observable<Health> {
    return this.http.get<Health>(`${this.baseUrl}/api/health`);
  }

  documents(): Observable<AgencyDocument[]> {
    return this.http.get<AgencyDocument[]>(`${this.baseUrl}/api/documents`);
  }

  ask(request: AskRequest): Observable<AskResponse> {
    return this.http.post<AskResponse>(`${this.baseUrl}/api/ask`, request);
  }

  /** URL absolue d'un PDF : l'API renvoie un chemin relatif à son propre domaine. */
  fileUrl(document: AgencyDocument): string {
    return `${this.baseUrl}${document.url}`;
  }
}

/**
 * Statuts dont le corps peut être remplacé en route : Cloudflare, devant
 * Sevalla, sert sa propre page HTML à la place des 502 et 504 de l'origine.
 * Le code métier est alors perdu, le statut suffit à le retrouver.
 */
const STATUS_FALLBACK: Partial<Record<number, ApiErrorCode>> = {
  502: 'llm_unavailable',
  504: 'llm_unavailable',
};

/** Traduit une erreur HTTP en code métier de l'API (format {"error": {"code"}}). */
export function toApiErrorCode(error: unknown): ApiErrorCode {
  if (!(error instanceof HttpErrorResponse) || error.status === 0) {
    return 'network';
  }
  const code = error.error?.error?.code;
  if (KNOWN_CODES.includes(code)) {
    return code;
  }
  return STATUS_FALLBACK[error.status] ?? 'internal_error';
}
