from dataclasses import dataclass
import os
from pathlib import Path


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue
        key, value = clean_line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL nao configurada. Configure a URL do Neon PostgreSQL no ambiente."
        )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    print("DATABASE_URL carregada com sucesso")
    return database_url


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "sim", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "App de Prestacao de Servicos API")
    environment: str = os.getenv("APP_ENV", "development")
    database_url: str = get_database_url()
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            (
                "http://localhost:5173,"
                "http://127.0.0.1:5173,"
                "http://localhost:3000,"
                "http://127.0.0.1:3000,"
                "http://localhost:4173,"
                "http://127.0.0.1:4173"
            ),
        ).split(",")
        if origin.strip()
    )
    cors_origin_regex: str | None = os.getenv(
        "CORS_ORIGIN_REGEX",
        r"https://.*\.vercel\.app",
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", Path(__file__).resolve().parents[1] / "uploads"))
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
    demo_seed_enabled: bool = _bool_env(
        "DEMO_SEED_ENABLED",
        os.getenv("APP_ENV", "development") != "production",
    )


settings = Settings()
