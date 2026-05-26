from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

from app.responses import error_response
from utils.exceptions import AppError


def _registrar_alerta(request: Request, tipo: str, nivel: str, mensagem: str) -> None:
    try:
        from database.session import SessionLocal
        from services.monitoring_service import registrar_alerta_monitoramento

        with SessionLocal() as db:
            registrar_alerta_monitoramento(db, tipo, nivel, mensagem, request.url.path)
    except Exception:
        pass


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.message, request, exc.__class__.__name__),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, __: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content=error_response(
                "Registro duplicado ou dados relacionados invalidos.",
                request,
                "IntegrityError",
            ),
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, __: OperationalError) -> JSONResponse:
        _registrar_alerta(request, "falha_postgresql", "critico", "Falha de conexao com PostgreSQL.")
        return JSONResponse(
            status_code=503,
            content=error_response(
                "Banco de dados indisponivel. Verifique o PostgreSQL.",
                request,
                "OperationalError",
            ),
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, __: Exception) -> JSONResponse:
        _registrar_alerta(request, "erro_interno", "critico", "Erro interno inesperado.")
        return JSONResponse(
            status_code=500,
            content=error_response("Erro interno inesperado.", request, "InternalServerError"),
        )
