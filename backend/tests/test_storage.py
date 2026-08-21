from pathlib import Path

from app.storage.local import LocalStorage


def test_local_storage_saves_file(tmp_path: Path) -> None:
    storage = LocalStorage(base_path=tmp_path)

    file_content = b"test file content"
    storage_key = "documents/1/1/test.pdf"

    returned_key = storage.save(
        file_content=file_content,
        storage_key=storage_key,
    )

    expected_path = tmp_path / storage_key

    assert returned_key == storage_key
    assert expected_path.exists()
    assert expected_path.read_bytes() == file_content


def test_delete_removes_file(tmp_path):
    storage = LocalStorage(base_path=tmp_path)

    storage_key = "documents/1/1/test.pdf"
    content = b"%PDF-1.4 test"

    storage.save(
        file_content=content,
        storage_key=storage_key,
    )

    path = tmp_path / storage_key

    assert path.exists()

    storage.delete(storage_key)

    assert not path.exists()


def test_get_path(tmp_path: Path) -> None:
    storage = LocalStorage(base_path=tmp_path)

    storage_key = "documents/1/v1/test.pdf"

    path = storage.get_path(storage_key)

    assert path == tmp_path / storage_key
