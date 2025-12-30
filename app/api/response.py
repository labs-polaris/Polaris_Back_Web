from typing import Any

from fastapi import Request

from app.schemas.common import Paging


def success_response(request: Request, data: Any, paging: Paging | None = None) -> dict:
    meta = {"request_id": getattr(request.state, "request_id", "")}
    if paging is not None:
        meta["paging"] = paging.model_dump()
    return {"ok": True, "data": data, "meta": meta}
