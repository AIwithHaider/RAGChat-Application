from sqlalchemy.orm import Session

from app.models.document import Document


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


def get_document(
    db: Session,
    document_id: int,
) -> Document | None:
    return db.get(Document, document_id)
