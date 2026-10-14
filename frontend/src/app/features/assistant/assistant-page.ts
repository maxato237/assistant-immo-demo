import {
  Component,
  ElementRef,
  OnInit,
  afterRenderEffect,
  computed,
  inject,
  signal,
  viewChild,
} from '@angular/core';

import { Source } from '../../core/api/api.models';
import { AssistantApi } from '../../core/api/assistant-api';
import { ChatStore } from '../../core/chat/chat-store';
import { ServerStatus } from '../../core/chat/server-status';
import { DemoBanner } from '../../shared/demo-banner/demo-banner';
import { AssistantReply } from './assistant-reply';
import { ChatError } from './chat-error';
import { Composer } from './composer';
import { DocumentsList } from './documents-list';

export const SUGGESTED_QUESTIONS = [
  'Quels T2 sont disponibles à moins de 800 € ?',
  'Combien coûtent les honoraires pour louer le L-104 ?',
  'Quels documents dois-je fournir pour mon dossier ?',
  'Acceptez-vous les animaux dans le L-102 ?',
];

@Component({
  selector: 'app-assistant-page',
  imports: [DemoBanner, DocumentsList, AssistantReply, ChatError, Composer],
  templateUrl: './assistant-page.html',
  styleUrl: './assistant-page.css',
})
export class AssistantPage implements OnInit {
  protected readonly chat = inject(ChatStore);
  protected readonly server = inject(ServerStatus);
  private readonly api = inject(AssistantApi);

  protected readonly suggestions = SUGGESTED_QUESTIONS;
  protected readonly selectedSource = signal<Source | null>(null);
  protected readonly selectedSourceUrl = computed(() => {
    const source = this.selectedSource();
    const document = this.server.documents().find((doc) => doc.id === source?.doc_id);
    return source && document ? `${this.api.fileUrl(document)}#page=${source.page}` : null;
  });

  private readonly scroller = viewChild.required<ElementRef<HTMLElement>>('scroller');
  private readonly documentsDialog = viewChild.required<ElementRef<HTMLDialogElement>>('documentsDialog');
  private readonly sourceDialog = viewChild.required<ElementRef<HTMLDialogElement>>('sourceDialog');

  constructor() {
    // Garde le dernier message visible quand la conversation avance.
    afterRenderEffect(() => {
      this.chat.messages();
      this.chat.pending();
      this.chat.failure();
      const element = this.scroller().nativeElement;
      element.scrollTo({ top: element.scrollHeight, behavior: 'smooth' });
    });
  }

  ngOnInit(): void {
    this.server.start();
  }

  protected openDocuments(): void {
    this.documentsDialog().nativeElement.showModal();
  }

  protected closeDocuments(): void {
    this.documentsDialog().nativeElement.close();
  }

  protected openSource(source: Source): void {
    this.selectedSource.set(source);
    this.sourceDialog().nativeElement.showModal();
  }

  protected closeSource(): void {
    this.sourceDialog().nativeElement.close();
  }
}
