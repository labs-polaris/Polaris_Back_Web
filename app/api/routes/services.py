from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_project_access
from app.api.response import success_response
from app.core.errors import AppException, ErrorCode
from app.crud import member as member_crud
from app.crud import project as project_crud
from app.crud import service as service_crud
from app.models.enums import OrgRole
from app.schemas.common import ErrorResponse, Paging, SuccessResponse
from app.schemas.service import ServiceCreate, ServiceOut, ServiceUpdate

router = APIRouter(prefix="/api", tags=["Services"])


@router.get(
    "/projects/{project_id}/services",
    summary="List services",
    description="List services for a project with paging and search.",
    response_model=SuccessResponse[list[ServiceOut]],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_services(
    project_id: str,
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str | None = Query(None, examples=["created_at:desc"]),
    q: str | None = Query(None, examples=["api"]),
    db: Session = Depends(get_db),
    _member=Depends(require_project_access(OrgRole.member)),
):
    services, total = service_crud.list_services(db, project_id, page, page_size, sort, q)
    paging = Paging(total=total, page=page, page_size=page_size, has_next=(page * page_size) < total)
    return success_response(request, [ServiceOut.model_validate(s) for s in services], paging)


@router.post(
    "/projects/{project_id}/services",
    summary="Create service",
    description="Create a service under a project.",
    response_model=SuccessResponse[ServiceOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def create_service(
    project_id: str,
    payload: ServiceCreate,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_project_access(OrgRole.admin)),
):
    service = service_crud.create_service(db, project_id, payload.name, payload.type, payload.environment)
    return success_response(request, ServiceOut.model_validate(service))


@router.get(
    "/services/{service_id}",
    summary="Get service",
    description="Get a service by ID.",
    response_model=SuccessResponse[ServiceOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_service(
    service_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    service = service_crud.get_service(db, service_id)
    if not service:
        raise AppException(404, ErrorCode.NOT_FOUND, "Service not found")
    project = project_crud.get_project(db, service.project_id)
    if not project:
        raise AppException(404, ErrorCode.NOT_FOUND, "Project not found")
    member = member_crud.get_member_by_user(db, project.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    return success_response(request, ServiceOut.model_validate(service))


@router.patch(
    "/services/{service_id}",
    summary="Update service",
    description="Update a service (admin or owner).",
    response_model=SuccessResponse[ServiceOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
@router.put(
    "/services/{service_id}",
    summary="Replace service",
    description="Replace a service (admin or owner).",
    response_model=SuccessResponse[ServiceOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def update_service(
    service_id: str,
    payload: ServiceUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    service = service_crud.get_service(db, service_id)
    if not service:
        raise AppException(404, ErrorCode.NOT_FOUND, "Service not found")
    project = project_crud.get_project(db, service.project_id)
    if not project:
        raise AppException(404, ErrorCode.NOT_FOUND, "Project not found")
    member = member_crud.get_member_by_user(db, project.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    if member.role not in (OrgRole.admin, OrgRole.owner):
        raise AppException(403, ErrorCode.FORBIDDEN, "Insufficient role")
    updated = service_crud.update_service(db, service, payload.name, payload.type, payload.environment)
    return success_response(request, ServiceOut.model_validate(updated))


@router.delete(
    "/services/{service_id}",
    summary="Delete service",
    description="Delete a service (admin or owner).",
    response_model=SuccessResponse[dict],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_service(
    service_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    service = service_crud.get_service(db, service_id)
    if not service:
        raise AppException(404, ErrorCode.NOT_FOUND, "Service not found")
    project = project_crud.get_project(db, service.project_id)
    if not project:
        raise AppException(404, ErrorCode.NOT_FOUND, "Project not found")
    member = member_crud.get_member_by_user(db, project.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    if member.role not in (OrgRole.admin, OrgRole.owner):
        raise AppException(403, ErrorCode.FORBIDDEN, "Insufficient role")
    service_crud.delete_service(db, service)
    return success_response(request, {"deleted": True})
