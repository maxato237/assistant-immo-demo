from typing import Protocol

from app.infra.mistral_http import ProviderError, post_json


class LLMClient(Protocol):
    def complete(self, messages: list[dict], max_tokens: int) -> str: ...


class MistralLLMClient:
    def __init__(self, api_key: str, model: str, timeout: float = 30):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def complete(self, messages: list[dict], max_tokens: int) -> str:
        data = post_json(
            "/chat/completions",
            {
                "model": self._model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0,  # réponses régulières : une démo doit être fiable
            },
            self._api_key,
            self._timeout,
        )
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as exc:
            raise ProviderError("Réponse Mistral inattendue") from exc
