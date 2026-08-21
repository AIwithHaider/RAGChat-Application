# from pathlib import Path

# import pymupdf
# import pytest

# from app.services.pdf_extraction_service import extract_text


# def create_test_pdf(path: Path, pages: list[str]) -> None:
#     """Create a simple PDF containing the supplied text."""
#     document = pymupdf.open()

#     for text in pages:
#         page = document.new_page()
#         page.insert_text((72, 72), text)

#     document.save(path)
#     document.close()


# def test_extract_text_from_single_page_pdf(tmp_path: Path) -> None:
#     pdf_path = tmp_path / "single-page.pdf"

#     create_test_pdf(
#         pdf_path,
#         ["RAGChat PDF extraction test."],
#     )

#     text = extract_text(pdf_path)

#     assert "RAGChat PDF extraction test." in text


# def test_extract_text_from_multiple_page_pdf(tmp_path: Path) -> None:
#     pdf_path = tmp_path / "multi-page.pdf"

#     create_test_pdf(
#         pdf_path,
#         [
#             "This is page one.",
#             "This is page two.",
#             "This is page three.",
#         ],
#     )

#     text = extract_text(pdf_path)

#     assert "This is page one." in text
#     assert "This is page two." in text
#     assert "This is page three." in text


# def test_extract_text_from_missing_file(tmp_path: Path) -> None:
#     pdf_path = tmp_path / "does-not-exist.pdf"

#     with pytest.raises(pymupdf.FileNotFoundError):
#         extract_text(pdf_path)


from pathlib import Path

import pymupdf

from app.services.pdf_extraction_service import extract_text


def create_test_pdf(path: Path, pages: list[str]) -> None:
    """Create a simple PDF containing the supplied text."""
    document = pymupdf.open()

    for text in pages:
        page = document.new_page()
        page.insert_text((72, 72), text)

    document.save(path)
    document.close()


def test_extract_text_from_single_page_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "single-page.pdf"

    create_test_pdf(
        pdf_path,
        ["RAGChat PDF extraction test."],
    )

    text = extract_text(pdf_path)

    assert "RAGChat PDF extraction test." in text


def test_extract_text_from_multiple_page_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "multi-page.pdf"

    create_test_pdf(
        pdf_path,
        [
            "This is page one.",
            "This is page two.",
            "This is page three.",
        ],
    )

    text = extract_text(pdf_path)

    assert "This is page one." in text
    assert "This is page two." in text
    assert "This is page three." in text


def test_extract_text_from_missing_file(tmp_path: Path) -> None:
    pdf_path = tmp_path / "does-not-exist.pdf"

    try:
        extract_text(pdf_path)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")
