from pathlib import Path

import pymupdf


def extract_text(file_path: str | Path) -> str:
    """Extract text from a PDF file."""
    pdf_path = Path(file_path)

    try:
        with pymupdf.open(pdf_path) as document:
            pages = [page.get_text() for page in document]
    except pymupdf.FileNotFoundError as exc:
        raise FileNotFoundError(pdf_path) from exc

    return "\n".join(pages)
