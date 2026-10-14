from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PdfDocument:
    id: str
    title: str
    pages: list[str]


def read_pdf(path: Path) -> PdfDocument:
    """Texte page par page. Le mode layout garde les lignes vides entre sections."""
    reader = PdfReader(path)
    title = (reader.metadata.title if reader.metadata else None) or path.stem
    pages = [page.extract_text(extraction_mode="layout") or "" for page in reader.pages]
    return PdfDocument(id=path.stem, title=title, pages=pages)
