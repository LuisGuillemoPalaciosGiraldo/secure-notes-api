import os
from dotenv import load_dotenv
load_dotenv()
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_expire_minutes: int
    cors_allow_origins: list[str]
    docs_enabled: bool


def _parse_cors_origins(raw_value: str) -> list[str]:
    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
    if not origins:
        raise ValueError("CORS_ALLOW_ORIGINS must include at least one origin.")
    if "*" in origins and os.getenv("ENVIRONMENT", "development") != "development":
        raise ValueError('allow_origins=["*"] is forbidden outside development.')
    return origins


def get_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "development").strip().lower()
    database_url = os.getenv("DATABASE_URL", "sqlite:///./secure_notes.db").strip()
    jwt_secret = os.getenv("JWT_SECRET", "").strip()
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256").strip()
    jwt_expire_minutes_str = os.getenv("JWT_EXPIRE_MINUTES", "30").strip()
    cors_raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").strip()

    if not jwt_secret:
        raise ValueError("JWT_SECRET is required.")

    try:
        jwt_expire_minutes = int(jwt_expire_minutes_str)
    except ValueError as exc:
        raise ValueError("JWT_EXPIRE_MINUTES must be an integer.") from exc

    if jwt_expire_minutes <= 0:
        raise ValueError("JWT_EXPIRE_MINUTES must be greater than 0.")

    cors_allow_origins = _parse_cors_origins(cors_raw)
    docs_enabled = environment == "development"

    return Settings(
        environment=environment,
        database_url=database_url,
        jwt_secret=jwt_secret,
        jwt_algorithm=jwt_algorithm,
        jwt_expire_minutes=jwt_expire_minutes,
        cors_allow_origins=cors_allow_origins,
        docs_enabled=docs_enabled,
    )
