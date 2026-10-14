import { Component, inject, input } from '@angular/core';

import { AgencyDocument } from '../../core/api/api.models';
import { AssistantApi } from '../../core/api/assistant-api';

/** Les PDF de l'agence : panneau latéral sur ordinateur, tiroir sur mobile. */
@Component({
  selector: 'app-documents-list',
  template: `
    <ul class="list">
      @for (document of documents(); track document.id) {
        <li>
          <a class="item" [href]="api.fileUrl(document)" target="_blank" rel="noopener">
            <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
              <path d="M14 3v6h6" />
            </svg>
            <span class="text">
              <span class="title">{{ document.title }}</span>
              <span class="meta">{{ document.pages }} {{ document.pages > 1 ? 'pages' : 'page' }}, PDF</span>
            </span>
          </a>
        </li>
      } @empty {
        <li class="meta">Chargement des documents...</li>
      }
    </ul>
  `,
  styles: `
    .list {
      display: flex;
      flex-direction: column;
      gap: var(--space-1);
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .item {
      display: flex;
      align-items: center;
      gap: 12px;
      min-height: 52px;
      padding: var(--space-2) 12px;
      border-radius: var(--radius-sm);
      color: var(--ink);
      text-decoration: none;
    }
    .item svg {
      flex-shrink: 0;
      color: var(--saone);
    }
    .item:hover {
      background: var(--saone-soft);
    }
    .text {
      display: flex;
      flex-direction: column;
    }
    .title {
      font: 600 14px/20px var(--font-body);
    }
    .meta {
      font-size: 12px;
      line-height: 16px;
      color: var(--ink-muted);
    }
  `,
})
export class DocumentsList {
  protected readonly api = inject(AssistantApi);
  readonly documents = input.required<AgencyDocument[]>();
}
