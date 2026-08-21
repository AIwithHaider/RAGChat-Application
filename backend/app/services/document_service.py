from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_version import DocumentVersion


# I will remove it later
def create_document(
    db: Session,
    tenant_id: int,
    filename: str,
) -> Document:
    document = Document(
        tenant_id=tenant_id,
        filename=filename,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def create_document_with_version(
    db: Session,
    tenant_id: int,
    filename: str,
    content_hash: str,
    storage_key: str,
) -> tuple[Document, DocumentVersion]:
    document = Document(
        tenant_id=tenant_id,
        filename=filename,
    )

    db.add(document)

    # Flush so PostgreSQL assigns the document ID
    # without committing the transaction yet.
    db.flush()

    document_version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        content_hash=content_hash,
        storage_key=storage_key,
    )

    db.add(document_version)

    # Commit both records as one transaction.
    db.commit()

    # Refresh both objects so their database-generated
    # values are available to the caller.
    db.refresh(document)
    db.refresh(document_version)

    return document, document_version


def create_document_record(
    db: Session,
    tenant_id: int,
    filename: str,
) -> Document:
    document = Document(
        tenant_id=tenant_id,
        filename=filename,
    )

    db.add(document)
    db.flush()

    return document


def get_document(
    db: Session,
    document_id: int,
) -> Document | None:
    return db.get(Document, document_id)


def list_documents(
    db: Session,
) -> list[Document]:
    return db.query(Document).all()


def delete_document(
    db: Session,
    document_id: int,
) -> list[str] | None:
    document = db.get(Document, document_id)

    if document is None:
        return None

    versions = (
        db.query(DocumentVersion)
        .filter(
            DocumentVersion.document_id == document_id,
        )
        .all()
    )

    storage_keys = [version.storage_key for version in versions]

    db.delete(document)

    return storage_keys
