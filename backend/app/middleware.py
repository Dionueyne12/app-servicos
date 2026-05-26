import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("api.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        started_at = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            extra={
                "extra": {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            },
        )
        if duration_ms >= 1500 or response.status_code >= 500:
            try:
                from database.session import SessionLocal
                from services.monitoring_service import registrar_alerta_monitoramento

                with SessionLocal() as db:
                    registrar_alerta_monitoramento(
                        db,
                        "rota_lenta" if duration_ms >= 1500 else "erro_rota",
                        "alerta" if response.status_code < 500 else "critico",
                        f"{request.method} {request.url.path} respondeu {response.status_code} em {duration_ms}ms.",
                        "middleware_request",
                    )
            except Exception:
                logger.exception("monitoring_alert_failed")
        return response
