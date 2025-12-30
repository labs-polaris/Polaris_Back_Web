from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.utils import apply_sort, paginate
from app.models.service import Service


def list_services(
    db: Session,
    project_id: str,
    page: int,
    page_size: int,
    sort: str | None,
    q: str | None,
) -> tuple[list[Service], int]:
    query = select(Service).where(Service.project_id == project_id)
    if q:
        query = query.where(Service.name.ilike(f"%{q}%"))
    query = apply_sort(query, Service, sort) if sort else query.order_by(Service.created_at.desc())
    return paginate(db, query, page, page_size)


def get_service(db: Session, service_id: str) -> Service | None:
    return db.execute(select(Service).where(Service.id == service_id)).scalar_one_or_none()


def create_service(
    db: Session, project_id: str, name: str, service_type: str, environment: str
) -> Service:
    service = Service(project_id=project_id, name=name, type=service_type, environment=environment)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def update_service(
    db: Session,
    service: Service,
    name: str | None,
    service_type: str | None,
    environment: str | None,
) -> Service:
    if name is not None:
        service.name = name
    if service_type is not None:
        service.type = service_type
    if environment is not None:
        service.environment = environment
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, service: Service) -> None:
    db.delete(service)
    db.commit()
