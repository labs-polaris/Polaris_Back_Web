from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Paging(BaseModel):
    total: int
    page: int
    page_size: int
    has_next: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"total": 42, "page": 1, "page_size": 20, "has_next": True}
        }
    )


class ResponseMeta(BaseModel):
    request_id: str
    paging: Optional[Paging] = None

    model_config = ConfigDict(
        json_schema_extra={"example": {"request_id": "req-123", "paging": None}}
    )


class SuccessResponse(BaseModel, Generic[T]):
    ok: bool = True
    data: T
    meta: ResponseMeta

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ok": True,
                "data": {},
                "meta": {"request_id": "req-123", "paging": None},
            }
        }
    )


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: Any | None = None


class ErrorResponse(BaseModel):
    ok: bool = False
    error: ErrorDetail
    meta: ResponseMeta

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ok": False,
                "error": {"code": "NOT_FOUND", "message": "Resource not found", "detail": None},
                "meta": {"request_id": "req-123"},
            }
        }
    )
