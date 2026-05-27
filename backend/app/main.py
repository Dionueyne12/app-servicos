import re

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
    print("[CORS] carregado")
    print(f"[CORS] origins permitidas: {list(settings.cors_origins)}")
    print(f"[CORS] regex permitida: {settings.cors_origin_regex}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    @app.middleware("http")
    async def log_cors_origin(request, call_next):
        origin = request.headers.get("origin")
        if origin:
            allowed = _is_cors_origin_allowed(origin)
            print(f"[CORS] origem recebida: {origin}")
            print(f"[CORS] origem permitida: {allowed}")
        return await call_next(request)

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


def _is_cors_origin_allowed(origin: str) -> bool:
    if origin in settings.cors_origins:
        return True
    if settings.cors_origin_regex and re.fullmatch(settings.cors_origin_regex, origin):
        return True
    return False


app = create_app()
