from pathlib import Path


class LocalStorage:
    """Store uploaded files on the local filesystem."""

    def __init__(self, base_path: str | Path = "storage") -> None:
        self.base_path = Path(base_path)

    def save(
        self,
        file_content: bytes,
        storage_key: str,
    ) -> str:
        """Save file content and return its storage key."""

        file_path = self.base_path / storage_key

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path.write_bytes(file_content)

        return storage_key

    def delete(self, storage_key: str) -> None:
        file_path = self.base_path / storage_key

        if file_path.exists():
            file_path.unlink()
