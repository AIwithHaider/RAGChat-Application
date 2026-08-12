from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services.document_service import create_document, get_document

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document_endpoint(
    data: DocumentCreate,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = create_document(
        db=db,
        tenant_id=data.tenant_id,
        filename=data.filename,
    )

    return document


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = get_document(
        db=db,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document
