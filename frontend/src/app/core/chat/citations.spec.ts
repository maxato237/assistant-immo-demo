import { parseCitations } from './citations';

describe('parseCitations', () => {
  it('sépare le texte et les renvois connus', () => {
    expect(parseCitations('Total 624 € [1][2].', new Set([1, 2]))).toEqual([
      { kind: 'text', text: 'Total 624 € ' },
      { kind: 'cite', n: 1 },
      { kind: 'cite', n: 2 },
      { kind: 'text', text: '.' },
    ]);
  });

  it('laisse en texte un numéro sans source reçue', () => {
    expect(parseCitations('Voir [7] et [1]', new Set([1]))).toEqual([
      { kind: 'text', text: 'Voir [7] et ' },
      { kind: 'cite', n: 1 },
    ]);
  });

  it('renvoie le texte seul quand il n’y a aucun renvoi', () => {
    expect(parseCitations('Je ne peux pas répondre.', new Set())).toEqual([
      { kind: 'text', text: 'Je ne peux pas répondre.' },
    ]);
  });
});
