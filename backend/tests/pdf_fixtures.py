from pathlib import Path

import pymupdf


def create_test_pdf(path: Path, text: str = "Test PDF document.") -> None:
    """Create a minimal text-based PDF for tests."""
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text((72, 72), text)

    document.save(path)
    document.close()
