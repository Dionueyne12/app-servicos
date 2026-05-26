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


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "App de Prestacao de Servicos API")
    environment: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/app_servicos",
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", Path(__file__).resolve().parents[1] / "uploads"))
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))


settings = Settings()
