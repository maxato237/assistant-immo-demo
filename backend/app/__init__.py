import json
import logging
from dataclasses import dataclass

from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from app.api.errors import register_error_handlers
from app.api.routes import api
from app.config import Config
from app.extensions import limiter
from app.infra.embeddings_client import MistralEmbeddingsClient
from app.infra.llm_client import MistralLLMClient
from app.infra.quota import DailyQuota
from app.infra.vector_store import CHUNKS_FILE, VectorStore
from app.services.chat_service import ChatService
from app.services.retrieval_service import RetrievalService

DOCUMENTS_MANIFEST = "documents.json"


@dataclass
class AssistantServices:
    chat: ChatService | None
    documents: list[dict]
    chunk_count: int
    quota: DailyQuota


def create_app(overrides: dict | None = None, services: AssistantServices | None = None) -> Flask:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update(overrides or {})

    # Render est derrière un proxy : lire la vraie IP du visiteur pour le rate limit.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})
    limiter.init_app(app)

    app.extensions["assistant"] = services or build_services(app.config)
    app.register_blueprint(api)
    register_error_handlers(app)
    return app


def build_services(config) -> AssistantServices:
    quota = DailyQuota(config["DAILY_QUOTA"])
    index_dir = config["INDEX_DIR"]
    if not (index_dir / CHUNKS_FILE).exists():
        logging.getLogger(__name__).warning(
            "Index absent dans %s : lancer scripts/build_index.py", index_dir
        )
        return AssistantServices(chat=None, documents=[], chunk_count=0, quota=quota)

    store = VectorStore.load(index_dir)
    documents = json.loads((index_dir / DOCUMENTS_MANIFEST).read_text(encoding="utf-8"))
    embedder = MistralEmbeddingsClient(config["MISTRAL_API_KEY"], config["EMBED_MODEL"])
    llm = MistralLLMClient(config["MISTRAL_API_KEY"], config["LLM_MODEL"])
    chat = ChatService(
        RetrievalService(store, embedder, config["TOP_K"]),
        llm,
        config["SYSTEM_PROMPT_FILE"].read_text(encoding="utf-8"),
        config["MAX_ANSWER_TOKENS"],
    )
    return AssistantServices(
        chat=chat, documents=documents, chunk_count=len(store.chunks), quota=quota
    )
