def build_document_storage_key(
    document_id: int,
    version_number: int,
    filename: str,
) -> str:
    return f"documents/{document_id}/{version_number}/{filename}"
