"""Indexe les PDF de data/documents dans data/index.

À relancer après chaque modification des PDF. Coût : quelques centimes au plus.
Usage : python scripts/build_index.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import DOCUMENTS_MANIFEST  # noqa: E402
from app.config import Config  # noqa: E402
from app.infra.embeddings_client import MistralEmbeddingsClient  # noqa: E402
from app.infra.mistral_http import ProviderError  # noqa: E402
from app.infra.pdf_reader import read_pdf  # noqa: E402
from app.services.indexing_service import build_index  # noqa: E402


def main() -> None:
    documents = [read_pdf(path) for path in sorted(Config.DOCUMENTS_DIR.glob("*.pdf"))]
    if not documents:
        sys.exit(f"Aucun PDF dans {Config.DOCUMENTS_DIR} : lancer scripts/generate_pdfs.py")

    embedder = MistralEmbeddingsClient(Config.MISTRAL_API_KEY, Config.EMBED_MODEL)
    try:
        store = build_index(documents, embedder)
    except ProviderError as exc:
        sys.exit(f"Échec de l'indexation : {exc}. Vérifier MISTRAL_API_KEY dans backend/.env")
    store.save(Config.INDEX_DIR)

    manifest = [{"id": d.id, "title": d.title, "pages": len(d.pages)} for d in documents]
    (Config.INDEX_DIR / DOCUMENTS_MANIFEST).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"{len(documents)} documents, {len(store.chunks)} morceaux indexés dans {Config.INDEX_DIR}")


if __name__ == "__main__":
    main()
