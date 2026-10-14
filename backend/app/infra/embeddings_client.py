from typing import Protocol

import numpy as np

from app.infra.mistral_http import ProviderError, post_json


class EmbeddingsClient(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray:
        """Renvoie une matrice (len(texts), dimension) en float32."""
        ...


class MistralEmbeddingsClient:
    BATCH_SIZE = 32

    def __init__(self, api_key: str, model: str, timeout: float = 30):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[start:start + self.BATCH_SIZE]
            data = post_json(
                "/embeddings",
                {"model": self._model, "input": batch},
                self._api_key,
                self._timeout,
            )
            try:
                items = sorted(data["data"], key=lambda item: item["index"])
                vectors.extend(item["embedding"] for item in items)
            except (KeyError, TypeError) as exc:
                raise ProviderError("Réponse embeddings Mistral inattendue") from exc
        return np.asarray(vectors, dtype=np.float32)
