from fastapi import FastAPI

from app.api.documents import router as documents_router

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(documents_router)
