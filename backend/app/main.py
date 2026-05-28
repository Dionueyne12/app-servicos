import re

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors import register_error_handlers
from app.logging_config import configure_logging
from app.middleware import RequestLoggingMiddleware
from database.schema_updates import ensure_schema_updates
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
    async def ensure_cors_headers(request, call_next):
        origin = request.headers.get("origin")
        allowed = False
        if origin:
            allowed = _is_cors_origin_allowed(origin)
            print(f"[CORS] origem recebida: {origin}")
            print(f"[CORS] origem permitida: {allowed}")

        if request.method == "OPTIONS" and origin and allowed:
            response = Response(status_code=200)
        else:
            response = await call_next(request)

        if origin and allowed:
            _apply_cors_headers(response, origin)

        return response

    register_error_handlers(app)
    app.include_router(api_router)

    @app.on_event("startup")
    def initialize_database() -> None:
        print("[DB] criando tabelas se não existirem")
        Base.metadata.create_all(bind=engine)
        ensure_schema_updates(engine)
        print("[DB] tabelas verificadas/criadas")
        print("[DB] seed admin iniciado")
        with SessionLocal() as db:
            ensure_default_admin(db)
        if settings.demo_seed_enabled:
            print("[DB] seed demo operacional iniciado")
            from scripts.seed_operational_demo import main as seed_operational_demo

            seed_operational_demo()

    return app


def _is_cors_origin_allowed(origin: str) -> bool:
    if origin in settings.cors_origins:
        return True
    if settings.cors_origin_regex and re.fullmatch(settings.cors_origin_regex, origin):
        return True
    return False


def _apply_cors_headers(response: Response, origin: str) -> None:
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
    response.headers["Vary"] = "Origin"


app = create_app()
