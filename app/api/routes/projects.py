from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_org_role, require_project_access
from app.api.response import success_response
from app.core.errors import AppException, ErrorCode
from app.crud import project as project_crud
from app.models.enums import OrgRole
from app.schemas.common import ErrorResponse, Paging, SuccessResponse
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/api", tags=["Projects"])


@router.get(
    "/orgs/{org_id}/projects",
    summary="List projects",
    description="List projects in an organization with paging and search.",
    response_model=SuccessResponse[list[ProjectOut]],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_projects(
    org_id: str,
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str | None = Query(None, examples=["created_at:desc"]),
    q: str | None = Query(None, examples=["console"]),
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.member)),
):
    projects, total = project_crud.list_projects(db, org_id, page, page_size, sort, q)
    paging = Paging(total=total, page=page, page_size=page_size, has_next=(page * page_size) < total)
    return success_response(request, [ProjectOut.model_validate(p) for p in projects], paging)


@router.post(
    "/orgs/{org_id}/projects",
    summary="Create project",
    description="Create a project under an organization.",
    response_model=SuccessResponse[ProjectOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def create_project(
    org_id: str,
    payload: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.admin)),
):
    project = project_crud.create_project(db, org_id, payload.name, payload.key)
    return success_response(request, ProjectOut.model_validate(project))


@router.get(
    "/projects/{project_id}",
    summary="Get project",
    description="Get a project by ID.",
    response_model=SuccessResponse[ProjectOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_project(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_project_access(OrgRole.member)),
):
    project = project_crud.get_project(db, project_id)
    if not project:
        raise AppException(404, ErrorCode.NOT_FOUND, "Project not found")
    return success_response(request, ProjectOut.model_validate(project))


@router.patch(
    "/projects/{project_id}",
    summary="Update project",
    description="Update a project (admin or owner).",
    response_model=SuccessResponse[ProjectOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
@router.put(
    "/projects/{project_id}",
    summary="Replace project",
    description="Replace a project (admin or owner).",
    response_model=SuccessResponse[ProjectOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_project_access(OrgRole.admin)),
):
    project = project_crud.get_project(db, project_id)
    if not project:
        raise AppException(404, ErrorCode.NOT_FOUND, "Project not found")
    updated = project_crud.update_project(db, project, payload.name, payload.key)
    return success_response(request, ProjectOut.model_validate(updated))


@router.delete(
    "/projects/{project_id}",
    summary="Delete project",
    description="Delete a project (admin or owner).",
    response_model=SuccessResponse[dict],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_project(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_project_access(OrgRole.admin)),
):
    project = project_crud.get_project(db, project_id)
    if not project:
        raise AppException(404, ErrorCode.NOT_FOUND, "Project not found")
    project_crud.delete_project(db, project)
    return success_response(request, {"deleted": True})
