from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.document_version import DocumentVersion
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    create_document_record,
    delete_document,
    get_document,
    list_documents,
)
from app.services.pdf_extraction_service import extract_text
from app.storage.hashing import calculate_sha256
from app.storage.keys import build_document_storage_key
from app.storage.local import LocalStorage

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


storage = LocalStorage()


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document_endpoint(
    tenant_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    file_content = file.file.read()

    content_hash = calculate_sha256(file_content)

    document = create_document_record(
        db=db,
        tenant_id=tenant_id,
        filename=filename,
    )

    storage_key = build_document_storage_key(
        document_id=document.id,
        version_number=1,
        filename=filename,
    )

    try:
        storage.save(
            file_content=file_content,
            storage_key=storage_key,
        )

        pdf_path = storage.get_path(storage_key)
        extracted_text = extract_text(pdf_path)

        document_version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content_hash=content_hash,
            storage_key=storage_key,
            extracted_text=extracted_text,
        )

        db.add(document_version)
        db.commit()

        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        storage.delete(storage_key)
        raise


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents_endpoint(
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:
    return list_documents(db=db)


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


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
) -> None:
    storage_keys = delete_document(
        db=db,
        document_id=document_id,
    )

    if storage_keys is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        for storage_key in storage_keys:
            storage.delete(storage_key)

        db.commit()

    except Exception:
        db.rollback()
        raise
