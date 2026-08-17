# RAGChat-Application

Production-oriented Retrieval-Augmented Generation (RAG) application built with FastAPI and React.

The project is being developed incrementally, starting with the backend foundation and basic frontend before introducing document processing and RAG functionality.

## Current Status

### Sprint 1 — Backend Foundation

Completed:

- FastAPI application
- `/health` endpoint
- Python development environment
- Docker Compose development environment
- pytest
- Ruff
- Environment configuration

### Sprint 2 — Database Foundation

Completed:

- PostgreSQL
- SQLAlchemy
- Alembic migrations
- Document model
- Document service
- Document API
- Database integration tests

### Sprint 3 — Basic Frontend

Completed:

- React + Vite frontend
- Dockerized frontend development server
- Application shell
- Sidebar
- Document list
- Chat area
- Message component
- Chat input
- Upload button
- Frontend loading/error/empty states
- Frontend API client
- Fetch documents from the backend
- Display backend documents
- Fake document upload
- Frontend component testing

The upload functionality is intentionally simulated at this stage. Real document ingestion and RAG processing will be implemented in later sprints.

---

## Architecture

The current development architecture consists of three Docker Compose services:

```text
┌───────────────────────────────┐
│           Browser             │
└───────────────┬───────────────┘
                │
                │ HTTP
                ▼
┌───────────────────────────────┐
│       React + Vite            │
│       localhost:5173          │
└───────────────┬───────────────┘
                │
                │ REST API
                ▼
┌───────────────────────────────┐
│       FastAPI Backend         │
│       localhost:8000          │
└───────────────┬───────────────┘
                │
                │ SQLAlchemy
                ▼
┌───────────────────────────────┐
│          PostgreSQL           │
│       localhost:5432          │
└───────────────────────────────┘

The architecture will evolve as document processing, vector search, RAG, authentication, background processing, and observability are introduced.

Running with Docker

From the project root:

docker compose up

The development services are available at:

Frontend: http://localhost:5173
Backend API: http://localhost:8000
API documentation: http://localhost:8000/docs
PostgreSQL: localhost:5432

Check running services:

docker compose ps
Backend

The backend is built with FastAPI, SQLAlchemy, PostgreSQL, and Alembic.

Run backend tests

From the project root:

docker compose exec backend uv run pytest
Run backend linting
docker compose exec backend uv run ruff check .
Check backend formatting
docker compose exec backend uv run ruff format --check .
Frontend

The frontend is built with React and Vite.

Run frontend tests

From the project root:

docker compose exec frontend npm test
Run frontend linting
docker compose exec frontend npm run lint
Frontend development server

The frontend is available at:

http://localhost:5173

Vite hot reload is enabled for development.

Current API
Health
GET /health

Example response:

{
  "status": "ok"
}
List documents
GET /documents

Example response:

[
  {
    "id": 1,
    "tenant_id": 1,
    "filename": "report.pdf",
    "status": "pending",
    "created_at": "2026-08-17T05:51:32.616Z",
    "updated_at": "2026-08-17T05:51:32.616Z"
  }
]
Create document
POST /documents

Example request:

{
  "tenant_id": 1,
  "filename": "report.pdf"
}
Development Philosophy

The project is intentionally developed incrementally.

The development approach is:

Small working implementation
          ↓
        Test
          ↓
     Understand
          ↓
      Improve

