from typing import Any

from fastapi import Request


def error_response(message: str, request: Request | None = None, code: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "success": False,
        "detail": message,
    }
    if code:
        payload["code"] = code
    if request is not None and hasattr(request.state, "request_id"):
        payload["request_id"] = request.state.request_id
    return payload
