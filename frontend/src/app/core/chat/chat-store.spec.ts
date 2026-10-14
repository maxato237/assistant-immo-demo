import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { AskResponse } from '../api/api.models';
import { ChatMessage, ChatStore, buildHistory } from './chat-store';

const ANSWER: AskResponse = {
  answer: 'Le L-104 fait 48 m² [1].',
  sources: [{ n: 1, doc_id: 'catalogue-biens', title: 'Catalogue des biens', page: 1, excerpt: 'L-104' }],
  latency_ms: 900,
};

describe('ChatStore', () => {
  let store: ChatStore;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    store = TestBed.inject(ChatStore);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('ajoute la question, puis la réponse découpée en renvois', () => {
    store.ask('  Surface du L-104 ?  ');
    expect(store.pending()).toBe(true);

    const request = http.expectOne('/api/ask');
    expect(request.request.body).toEqual({ question: 'Surface du L-104 ?', history: [] });
    request.flush(ANSWER);

    const [question, answer] = store.messages();
    expect(question).toMatchObject({ role: 'user', text: 'Surface du L-104 ?' });
    expect(answer).toMatchObject({ role: 'assistant', sources: ANSWER.sources });
    expect(answer.role === 'assistant' && answer.segments).toContainEqual({ kind: 'cite', n: 1 });
    expect(store.pending()).toBe(false);
  });

  it('envoie l’échange précédent pour une question de suivi', () => {
    store.ask('Surface du L-104 ?');
    http.expectOne('/api/ask').flush(ANSWER);

    store.ask('Il a un balcon ?');
    expect(http.expectOne('/api/ask').request.body.history).toEqual([
      { role: 'user', content: 'Surface du L-104 ?' },
      { role: 'assistant', content: ANSWER.answer },
    ]);
  });

  it('ignore une nouvelle question tant que la précédente attend', () => {
    store.ask('Q1');
    store.ask('Q2');
    http.expectOne('/api/ask');
    expect(store.messages().length).toBe(1);
  });

  it('traduit le code d’erreur de l’API, puis réessaie sans dupliquer la question', () => {
    store.ask('Q1');
    http
      .expectOne('/api/ask')
      .flush({ error: { code: 'llm_unavailable', message: 'x' } }, { status: 502, statusText: 'Bad Gateway' });
    expect(store.failure()).toEqual({ code: 'llm_unavailable', question: 'Q1' });

    store.retry();
    const retry = http.expectOne('/api/ask');
    expect(retry.request.body.question).toBe('Q1');
    retry.flush(ANSWER);

    expect(store.failure()).toBeNull();
    expect(store.messages().map((m) => m.role)).toEqual(['user', 'assistant']);
  });

  it('signale une coupure réseau', () => {
    store.ask('Q1');
    http.expectOne('/api/ask').error(new ProgressEvent('error'));
    expect(store.failure()?.code).toBe('network');
  });

  it('repart de zéro avec reset', () => {
    store.ask('Q1');
    http.expectOne('/api/ask').flush(ANSWER);
    store.reset();
    expect(store.messages()).toEqual([]);
    expect(store.hasStarted()).toBe(false);
  });
});

describe('buildHistory', () => {
  const user = (text: string): ChatMessage => ({ id: 0, role: 'user', text });
  const bot = (text: string): ChatMessage => ({ id: 0, role: 'assistant', text, segments: [], sources: [] });

  it('ne garde que les échanges complets', () => {
    expect(buildHistory([user('a'), bot('b'), user('sans réponse')])).toEqual([
      { role: 'user', content: 'a' },
      { role: 'assistant', content: 'b' },
    ]);
  });

  it('se limite aux 4 derniers messages', () => {
    const history = buildHistory([user('1'), bot('2'), user('3'), bot('4'), user('5'), bot('6')]);
    expect(history.map((m) => m.content)).toEqual(['3', '4', '5', '6']);
  });
});
