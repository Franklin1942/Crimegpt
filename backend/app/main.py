import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .core.config import settings
from .db.session import init_db

app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    description="AI-powered crime documentation and legal intelligence platform",
    version="1.0.0",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def on_startup() -> None:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_db()


@app.get("/health", tags=["health"])
@app.get(f"{settings.API_PREFIX}/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "environment": settings.ENVIRONMENT}
