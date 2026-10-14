"""PDF -> morceaux de texte -> embeddings -> index."""

import re

from app.infra.embeddings_client import EmbeddingsClient
from app.infra.pdf_reader import PdfDocument
from app.infra.vector_store import Chunk, VectorStore

MAX_CHARS = 800
HEADING_MAX_LEN = 90


def split_page(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Découpe une page en suivant sa structure.

    Les blocs sont séparés par des lignes vides. Un bloc qui ressemble à un titre
    est collé au bloc suivant : un bien du catalogue reste ainsi dans un seul morceau.
    """
    blocks = [_clean(block) for block in re.split(r"\n\s*\n", text)]
    sections: list[str] = []
    heading = ""
    for block in filter(None, blocks):
        if _is_heading(block):
            heading = f"{heading}\n{block}".strip()
            continue
        sections.append(f"{heading}\n{block}".strip())
        heading = ""
    if heading:
        sections.append(heading)

    pieces: list[str] = []
    for section in sections:
        pieces.extend(_split_long(section, max_chars))
    return pieces


def build_index(documents: list[PdfDocument], embedder: EmbeddingsClient) -> VectorStore:
    chunks = [
        Chunk(id=f"{doc.id}-p{page_no}-{i}", doc_id=doc.id, doc_title=doc.title, page=page_no, text=piece)
        for doc in documents
        for page_no, page_text in enumerate(doc.pages, start=1)
        for i, piece in enumerate(split_page(page_text))
    ]
    vectors = embedder.embed([embedding_text(chunk) for chunk in chunks])
    return VectorStore(chunks, vectors)


def embedding_text(chunk: Chunk) -> str:
    # Le titre du document aide la recherche ("honoraires", "catalogue"...).
    return f"{chunk.doc_title}\n{chunk.text}"


def _clean(block: str) -> str:
    lines = (re.sub(r"[ \t]{2,}", " ", line).strip() for line in block.splitlines())
    return "\n".join(line for line in lines if line)


def _is_heading(block: str) -> bool:
    lines = block.splitlines()
    return len(lines) <= 3 and all(
        len(line) <= HEADING_MAX_LEN and not line.endswith((".", ":", ";")) for line in lines
    )


def _split_long(section: str, max_chars: int) -> list[str]:
    """Coupe une section trop longue ligne par ligne, en répétant son titre."""
    if len(section) <= max_chars:
        return [section]
    title, *lines = section.splitlines()
    pieces, current = [], [title]
    for line in lines:
        if len("\n".join(current + [line])) > max_chars and len(current) > 1:
            pieces.append("\n".join(current))
            current = [title, current[-1]]  # 1 ligne de chevauchement
        current.append(line)
    pieces.append("\n".join(current))
    return pieces
