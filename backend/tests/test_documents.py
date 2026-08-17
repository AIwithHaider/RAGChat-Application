import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.dependencies import get_db
from app.main import app
from app.models.tenant import Tenant

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


def test_create_document():
    with TestSessionLocal() as db:
        tenant = Tenant(name="Test Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        tenant_id = tenant.id

    response = client.post(
        "/documents",
        json={
            "tenant_id": tenant_id,
            "filename": "test-api.pdf",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["tenant_id"] == tenant_id
    assert data["filename"] == "test-api.pdf"
    assert data["status"] == "pending"


def test_get_document():
    with TestSessionLocal() as db:
        tenant = Tenant(name="Get Document Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        response = client.post(
            "/documents",
            json={
                "tenant_id": tenant.id,
                "filename": "get-test.pdf",
            },
        )

        document_id = response.json()["id"]

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document_id
    assert data["filename"] == "get-test.pdf"
    assert data["status"] == "pending"


def test_list_documents():
    with TestSessionLocal() as db:
        tenant = Tenant(name="List Documents Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        tenant_id = tenant.id

    first_response = client.post(
        "/documents",
        json={
            "tenant_id": tenant_id,
            "filename": "first.pdf",
        },
    )

    second_response = client.post(
        "/documents",
        json={
            "tenant_id": tenant_id,
            "filename": "second.pdf",
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
