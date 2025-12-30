from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.crud.utils import apply_sort, paginate
from app.models.project import Project


def list_projects(
    db: Session,
    org_id: str,
    page: int,
    page_size: int,
    sort: str | None,
    q: str | None,
) -> tuple[list[Project], int]:
    query = select(Project).where(Project.org_id == org_id)
    if q:
        query = query.where(or_(Project.name.ilike(f"%{q}%"), Project.key.ilike(f"%{q}%")))
    query = apply_sort(query, Project, sort) if sort else query.order_by(Project.created_at.desc())
    return paginate(db, query, page, page_size)


def get_project(db: Session, project_id: str) -> Project | None:
    return db.execute(select(Project).where(Project.id == project_id)).scalar_one_or_none()


def create_project(db: Session, org_id: str, name: str, key: str) -> Project:
    project = Project(org_id=org_id, name=name, key=key)
    db.add(project)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppException(409, ErrorCode.CONFLICT, "Project key already exists in org") from exc
    db.refresh(project)
    return project


def update_project(db: Session, project: Project, name: str | None, key: str | None) -> Project:
    if name is not None:
        project.name = name
    if key is not None:
        project.key = key
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
