from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors import register_error_handlers
from app.logging_config import configure_logging
from app.middleware import RequestLoggingMiddleware
from database.session import SessionLocal, engine
from models import Base
from routes import api_router
from services.seed_service import ensure_default_admin


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    register_error_handlers(app)
    app.include_router(api_router)

    @app.on_event("startup")
    def initialize_database() -> None:
        print("[DB] criando tabelas se não existirem")
        Base.metadata.create_all(bind=engine)
        print("[DB] tabelas verificadas/criadas")
        print("[DB] seed admin iniciado")
        with SessionLocal() as db:
            ensure_default_admin(db)

    return app


app = create_app()
