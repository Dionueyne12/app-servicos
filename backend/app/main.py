from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors import register_error_handlers
from app.logging_config import configure_logging
from app.middleware import RequestLoggingMiddleware
from database.session import SessionLocal
from routes import api_router
from services.seed_service import ensure_default_admin


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    register_error_handlers(app)
    app.include_router(api_router)

    @app.on_event("startup")
    def seed_default_admin() -> None:
        with SessionLocal() as db:
            ensure_default_admin(db)

    return app


app = create_app()
