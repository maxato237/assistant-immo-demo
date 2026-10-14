"""Question -> extraits pertinents -> prompt -> réponse + sources citées."""

import re
from dataclasses import dataclass

from app.infra.llm_client import LLMClient
from app.services.retrieval_service import RetrievalService

EXCERPT_CHARS = 300
CONTEXT_PLACEHOLDER = "{EXTRAITS}"


@dataclass(frozen=True)
class Source:
    n: int
    doc_id: str
    title: str
    page: int
    excerpt: str


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[Source]
    best_score: float


class ChatService:
    def __init__(self, retriever: RetrievalService, llm: LLMClient, system_prompt: str, max_tokens: int):
        self._retriever = retriever
        self._llm = llm
        self._system_prompt = system_prompt
        self._max_tokens = max_tokens

    def answer(self, question: str, history: list[dict]) -> Answer:
        hits = self._retriever.retrieve(_retrieval_query(question, history))
        context = "\n\n".join(
            f"[{n}] ({chunk.doc_title}, p.{chunk.page})\n{chunk.text}"
            for n, (chunk, _) in enumerate(hits, start=1)
        )
        messages = [
            {"role": "system", "content": self._system_prompt.replace(CONTEXT_PLACEHOLDER, context)},
            *history,
            {"role": "user", "content": question},
        ]
        # Le front affiche du texte simple : on retire le gras markdown que le modèle ajoute parfois.
        text = self._llm.complete(messages, self._max_tokens).replace("**", "")

        cited = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
        sources = [
            Source(n=n, doc_id=chunk.doc_id, title=chunk.doc_title, page=chunk.page,
                   excerpt=chunk.text[:EXCERPT_CHARS])
            for n, (chunk, _) in enumerate(hits, start=1)
            if n in cited
        ]
        best_score = hits[0][1] if hits else 0.0
        return Answer(text=text, sources=sources, best_score=best_score)


def _retrieval_query(question: str, history: list[dict]) -> str:
    """Ajoute la dernière question du visiteur : "et celui-là ?" garde son contexte."""
    previous = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
    return f"{previous}\n{question}".strip()
