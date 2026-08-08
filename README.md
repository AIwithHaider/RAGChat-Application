# RAGChat-Application

Production-oriented RAG application built with FastAPI.

## Backend

FastAPI backend.

## Running locally

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload


Running with Docker

docker compose up
Health check
GET /health

Response:

{
  "status": "ok"
}
Tests
cd backend
uv run pytest
Lint
uv run ruff check .
Format
uv run ruff format .


