import re

from app.infra.embeddings_client import EmbeddingsClient
from app.infra.vector_store import Chunk, VectorStore

# Références exactes du type "L-104" ou "V-202" : les embeddings les captent mal.
REFERENCE_PATTERN = re.compile(r"\b[A-Z]{1,3}-\d{2,5}\b")
MAX_EXACT_MATCHES = 3
EXACT_MATCH_SCORE = 1.0


class RetrievalService:
    """Recherche hybride : sens (embeddings) + références exactes citées dans la question."""

    def __init__(self, store: VectorStore, embedder: EmbeddingsClient, top_k: int = 6):
        self._store = store
        self._embedder = embedder
        self._top_k = top_k

    def retrieve(self, query: str) -> list[tuple[Chunk, float]]:
        exact = self._exact_matches(query)
        vector = self._embedder.embed([query])[0]
        semantic = self._store.search(vector, self._top_k)

        seen = {chunk.id for chunk, _ in exact}
        others = [(chunk, score) for chunk, score in semantic if chunk.id not in seen]
        return (exact + others)[:max(self._top_k, len(exact))]

    def _exact_matches(self, query: str) -> list[tuple[Chunk, float]]:
        references = set(REFERENCE_PATTERN.findall(query.upper()))
        if not references:
            return []
        matches = [
            (chunk, EXACT_MATCH_SCORE)
            for chunk in self._store.chunks
            if any(ref in chunk.text.upper() for ref in references)
        ]
        return matches[:MAX_EXACT_MATCHES]
