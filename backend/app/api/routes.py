import logging
import time

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from pydantic import ValidationError

from app.api.errors import ApiError
from app.api.schemas import MAX_QUESTION_CHARS, AskRequest
from app.extensions import limiter
from app.infra.mistral_http import ProviderError

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__, url_prefix="/api")


def _services():
    return current_app.extensions["assistant"]


@api.get("/health")
def health():
    services = _services()
    ready = services.chat is not None
    return jsonify({
        "status": "ok" if ready else "index_missing",
        "documents": len(services.documents),
        "chunks": services.chunk_count,
    })


@api.get("/documents")
def list_documents():
    return jsonify([
        {**doc, "url": f"/api/documents/{doc['id']}/file"} for doc in _services().documents
    ])


@api.get("/documents/<doc_id>/file")
def document_file(doc_id: str):
    # Seuls les identifiants connus sont servis : pas de chemin construit depuis l'URL.
    if doc_id not in {doc["id"] for doc in _services().documents}:
        raise ApiError(404, "document_not_found", "Document introuvable.")
    return send_from_directory(current_app.config["DOCUMENTS_DIR"], f"{doc_id}.pdf")


@api.post("/ask")
@limiter.limit(lambda: current_app.config["RATE_LIMIT_ASK"])
def ask():
    try:
        payload = AskRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError:
        raise ApiError(
            400, "invalid_question",
            f"La question doit faire entre 1 et {MAX_QUESTION_CHARS} caractères.",
        )

    services = _services()
    if services.chat is None:
        raise ApiError(503, "index_missing", "L'assistant n'est pas encore prêt.")
    if not services.quota.try_consume():
        raise ApiError(
            503, "demo_paused",
            "La démo a atteint son nombre de questions pour aujourd'hui. Revenez demain !",
        )

    started = time.perf_counter()
    try:
        answer = services.chat.answer(
            payload.question, [m.model_dump() for m in payload.history]
        )
    except ProviderError:
        logger.exception("Fournisseur IA en erreur")
        raise ApiError(
            502, "llm_unavailable", "L'assistant est momentanément indisponible. Réessayez dans un instant."
        )
    latency_ms = round((time.perf_counter() - started) * 1000)

    logger.info(
        "ask question=%r latency_ms=%d best_score=%.3f sources=%d",
        payload.question[:200], latency_ms, answer.best_score, len(answer.sources),
    )
    return jsonify({
        "answer": answer.text,
        "sources": [vars(source) for source in answer.sources],
        "latency_ms": latency_ms,
    })
