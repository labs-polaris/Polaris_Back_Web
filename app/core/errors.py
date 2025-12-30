from enum import Enum
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_INVALID = "AUTH_INVALID"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BAD_REQUEST = "BAD_REQUEST"


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        code: ErrorCode,
        message: str,
        detail: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.detail = detail


def _error_payload(request: Request, code: ErrorCode, message: str, detail: Any | None = None) -> dict:
    request_id = getattr(request.state, "request_id", "")
    return {
        "ok": False,
        "error": {"code": code.value, "message": message, "detail": detail},
        "meta": {"request_id": request_id},
    }


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    payload = _error_payload(request, exc.code, exc.message, exc.detail)
    return JSONResponse(status_code=exc.status_code, content=payload)


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    payload = _error_payload(
        request,
        ErrorCode.VALIDATION_ERROR,
        "Validation failed",
        detail=exc.errors(),
    )
    return JSONResponse(status_code=422, content=payload)


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    payload = _error_payload(request, ErrorCode.BAD_REQUEST, exc.detail)
    return JSONResponse(status_code=exc.status_code, content=payload)
