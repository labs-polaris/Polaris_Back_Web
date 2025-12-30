from typing import Any

from sqlalchemy import Select, func
from sqlalchemy.orm import Session


def apply_sort(query: Select, model: Any, sort: str | None) -> Select:
    if not sort:
        return query
    parts = sort.split(":")
    if len(parts) != 2:
        return query
    field, direction = parts
    column = getattr(model, field, None)
    if column is None:
        return query
    if direction.lower() == "desc":
        return query.order_by(column.desc())
    return query.order_by(column.asc())


def paginate(db: Session, query: Select, page: int, page_size: int) -> tuple[list[Any], int]:
    total = db.execute(select_count(query)).scalar_one()
    offset = (page - 1) * page_size
    items = db.execute(query.limit(page_size).offset(offset)).scalars().all()
    return items, total


def select_count(query: Select) -> Select:
    return query.with_only_columns(func.count(), maintain_column_froms=True).order_by(None)
