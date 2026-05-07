import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import auth, notes

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="Secure Notes API",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.on_event("startup")
def on_startup() -> None:
    try:
        _ = get_settings()
        Base.metadata.create_all(bind=engine)
        logger.info("Startup checks passed and database initialized.")
    except Exception as exc:
        logger.error("Startup validation failed: %s", exc)
        raise RuntimeError("Startup validation failed.") from exc


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(notes.router)
