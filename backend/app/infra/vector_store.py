"""Index en mémoire : matrice numpy normalisée + métadonnées des morceaux.

Avec des vecteurs normalisés, la similarité cosinus est un simple produit scalaire.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

VECTORS_FILE = "embeddings.npy"
CHUNKS_FILE = "chunks.json"


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    doc_title: str
    page: int
    text: str


class VectorStore:
    def __init__(self, chunks: list[Chunk], vectors: np.ndarray):
        if len(chunks) != len(vectors):
            raise ValueError("Autant de vecteurs que de morceaux attendus")
        self.chunks = chunks
        self._vectors = _normalize(vectors.astype(np.float32))

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[Chunk, float]]:
        if not self.chunks:
            return []
        scores = self._vectors @ _normalize(query_vector.astype(np.float32).reshape(1, -1))[0]
        best = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in best]

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        np.save(directory / VECTORS_FILE, self._vectors)
        (directory / CHUNKS_FILE).write_text(
            json.dumps([asdict(c) for c in self.chunks], ensure_ascii=False, indent=1),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, directory: Path) -> "VectorStore":
        vectors = np.load(directory / VECTORS_FILE)
        raw = json.loads((directory / CHUNKS_FILE).read_text(encoding="utf-8"))
        return cls([Chunk(**item) for item in raw], vectors)


def _normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.where(norms == 0, 1, norms)
