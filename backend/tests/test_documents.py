import hashlib
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.dependencies import get_db
from app.main import app
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.tenant import Tenant
from app.services.document_service import create_document_with_version
from tests.pdf_fixtures import create_test_pdf

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    # "postgresql+psycopg://ragchat_test:3366@localhost:5432/ragchat_test",
    "postgresql+psycopg://ragchat:ragchat@postgres:5432/ragchat",
)

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    with test_engine.begin() as connection:
        connection.exec_driver_sql(
            """
            TRUNCATE TABLE
                messages,
                conversations,
                document_versions,
                documents,
                users,
                tenants
            RESTART IDENTITY CASCADE
            """
        )


def test_create_document_with_version():
    with TestSessionLocal() as db:
        tenant = Tenant(name="Version Test Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        document, version = create_document_with_version(
            db=db,
            tenant_id=tenant.id,
            filename="report.pdf",
            content_hash="a" * 64,
            storage_key="documents/1/1/report.pdf",
        )

        assert document.id is not None
        assert document.filename == "report.pdf"

        assert version.id is not None
        assert version.document_id == document.id
        assert version.version_number == 1
        assert version.content_hash == "a" * 64
        assert version.storage_key == "documents/1/1/report.pdf"


def test_upload_document_persists_complete_flow(tmp_path: Path):
    pdf_path = tmp_path / "persistence-test.pdf"

    create_test_pdf(
        pdf_path,
        "Complete persistence test.",
    )

    file_content = pdf_path.read_bytes()
    expected_hash = hashlib.sha256(file_content).hexdigest()

    with TestSessionLocal() as db:
        tenant = Tenant(name="Persistence Flow Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        tenant_id = tenant.id

    response = client.post(
        "/documents",
        data={
            "tenant_id": str(tenant_id),
        },
        files={
            "file": (
                "persistence-test.pdf",
                file_content,
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 201

    document_data = response.json()

    document_id = document_data["id"]

    assert document_data["tenant_id"] == tenant_id
    assert document_data["filename"] == "persistence-test.pdf"
    assert document_data["status"] == "pending"

    with TestSessionLocal() as db:
        document = db.get(Document, document_id)

        assert document is not None
        assert document.id == document_id
        assert document.tenant_id == tenant_id
        assert document.filename == "persistence-test.pdf"
        assert document.status == "pending"

        version = (
            db.query(DocumentVersion)
            .filter(
                DocumentVersion.document_id == document_id,
            )
            .one()
        )

        assert version.document_id == document_id
        assert version.version_number == 1
        assert version.content_hash == expected_hash
        assert version.storage_key == (
            f"documents/{document_id}/1/persistence-test.pdf"
        )
        assert version.extracted_text is not None
        assert "Complete persistence test." in version.extracted_text

        storage_path = Path("storage") / version.storage_key

        assert storage_path.exists()
        assert storage_path.is_file()
        assert storage_path.read_bytes() == file_content


def test_delete_document(tmp_path: Path):
    pdf_path = tmp_path / "delete-test.pdf"

    create_test_pdf(
        pdf_path,
        "Delete test.",
    )

    file_content = pdf_path.read_bytes()

    with TestSessionLocal() as db:
        tenant = Tenant(name="Delete Document Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        tenant_id = tenant.id

    response = client.post(
        "/documents",
        data={
            "tenant_id": str(tenant_id),
        },
        files={
            "file": (
                "delete-test.pdf",
                file_content,
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 201

    document_id = response.json()["id"]

    with TestSessionLocal() as db:
        document = db.get(Document, document_id)

        assert document is not None

        version = (
            db.query(DocumentVersion)
            .filter(
                DocumentVersion.document_id == document_id,
            )
            .one()
        )

        storage_key = version.storage_key

    storage_path = Path("storage") / storage_key

    assert storage_path.exists()

    response = client.delete(
        f"/documents/{document_id}",
    )

    assert response.status_code == 204
    assert response.content == b""

    with TestSessionLocal() as db:
        document = db.get(Document, document_id)

        assert document is None

        versions = (
            db.query(DocumentVersion)
            .filter(
                DocumentVersion.document_id == document_id,
            )
            .all()
        )

        assert versions == []

    assert not storage_path.exists()

    response = client.get(
        f"/documents/{document_id}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found",
    }


def test_delete_missing_document():
    response = client.delete(
        "/documents/999999",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found",
    }


def test_get_document(tmp_path: Path):
    pdf_path = tmp_path / "get-test.pdf"

    create_test_pdf(
        pdf_path,
        "Get document test.",
    )

    file_content = pdf_path.read_bytes()

    with TestSessionLocal() as db:
        tenant = Tenant(name="Get Document Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        response = client.post(
            "/documents",
            data={
                "tenant_id": str(tenant.id),
            },
            files={
                "file": (
                    "get-test.pdf",
                    file_content,
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 201

        document_id = response.json()["id"]

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document_id
    assert data["filename"] == "get-test.pdf"
    assert data["status"] == "pending"


def test_list_documents(tmp_path: Path):

    first_pdf = tmp_path / "first.pdf"
    second_pdf = tmp_path / "second.pdf"

    create_test_pdf(
        first_pdf,
        "First test document.",
    )

    create_test_pdf(
        second_pdf,
        "Second test document.",
    )

    first_file_content = first_pdf.read_bytes()
    second_file_content = second_pdf.read_bytes()

    with TestSessionLocal() as db:
        tenant = Tenant(name="List Documents Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        tenant_id = tenant.id

    first_response = client.post(
        "/documents",
        data={
            "tenant_id": str(tenant_id),
        },
        files={
            "file": (
                "first.pdf",
                first_file_content,
                "application/pdf",
            ),
        },
    )

    second_response = client.post(
        "/documents",
        data={
            "tenant_id": str(tenant_id),
        },
        files={
            "file": (
                "second.pdf",
                second_file_content,
                "application/pdf",
            ),
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get("/documents")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["filename"] == "first.pdf"
    assert data[1]["filename"] == "second.pdf"


def test_get_missing_document():
    response = client.get("/documents/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
