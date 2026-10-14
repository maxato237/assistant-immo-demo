export type AnswerSegment = { kind: 'text'; text: string } | { kind: 'cite'; n: number };

/**
 * Découpe une réponse en texte et en renvois de source : "650 € [1][2]." donne
 * texte, renvoi 1, renvoi 2, texte. Seuls les numéros des sources reçues deviennent
 * des renvois ; un [7] inventé par le modèle reste du texte.
 */
export function parseCitations(answer: string, knownSources: ReadonlySet<number>): AnswerSegment[] {
  const segments: AnswerSegment[] = [];
  let buffer = '';
  let last = 0;

  for (const match of answer.matchAll(/\[(\d+)\]/g)) {
    const n = Number(match[1]);
    buffer += answer.slice(last, match.index);
    last = match.index + match[0].length;
    if (!knownSources.has(n)) {
      buffer += match[0];
      continue;
    }
    if (buffer) {
      segments.push({ kind: 'text', text: buffer });
      buffer = '';
    }
    segments.push({ kind: 'cite', n });
  }
  buffer += answer.slice(last);
  if (buffer) {
    segments.push({ kind: 'text', text: buffer });
  }
  return segments;
}
