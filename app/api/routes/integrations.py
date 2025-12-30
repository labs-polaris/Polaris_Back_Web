from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_org_role
from app.api.response import success_response
from app.core.errors import AppException, ErrorCode
from app.crud import member as member_crud
from app.crud import integration as integration_crud
from app.models.enums import OrgRole
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.integration import IntegrationCreate, IntegrationOut, IntegrationUpdate

router = APIRouter(prefix="/api", tags=["Integrations"])


@router.get(
    "/orgs/{org_id}/integrations",
    summary="List integrations",
    description="List integrations configured for an organization.",
    response_model=SuccessResponse[list[IntegrationOut]],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_integrations(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.member)),
):
    integrations = integration_crud.list_integrations(db, org_id)
    return success_response(request, [IntegrationOut.model_validate(i) for i in integrations])


@router.post(
    "/orgs/{org_id}/integrations",
    summary="Create integration",
    description="Create an integration (admin or owner).",
    response_model=SuccessResponse[IntegrationOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def create_integration(
    org_id: str,
    payload: IntegrationCreate,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.admin)),
):
    integration = integration_crud.create_integration(
        db, org_id, payload.provider, payload.config_json, payload.is_enabled
    )
    return success_response(request, IntegrationOut.model_validate(integration))


@router.get(
    "/integrations/{integration_id}",
    summary="Get integration",
    description="Fetch an integration by ID.",
    response_model=SuccessResponse[IntegrationOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_integration(
    integration_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    integration = integration_crud.get_integration(db, integration_id)
    if not integration:
        raise AppException(404, ErrorCode.NOT_FOUND, "Integration not found")
    member = member_crud.get_member_by_user(db, integration.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    return success_response(request, IntegrationOut.model_validate(integration))


@router.patch(
    "/integrations/{integration_id}",
    summary="Update integration",
    description="Update an integration (admin or owner).",
    response_model=SuccessResponse[IntegrationOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
@router.put(
    "/integrations/{integration_id}",
    summary="Replace integration",
    description="Replace an integration (admin or owner).",
    response_model=SuccessResponse[IntegrationOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def update_integration(
    integration_id: str,
    payload: IntegrationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    integration = integration_crud.get_integration(db, integration_id)
    if not integration:
        raise AppException(404, ErrorCode.NOT_FOUND, "Integration not found")
    member = member_crud.get_member_by_user(db, integration.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    if member.role not in (OrgRole.admin, OrgRole.owner):
        raise AppException(403, ErrorCode.FORBIDDEN, "Insufficient role")
    updated = integration_crud.update_integration(
        db, integration, payload.provider, payload.config_json, payload.is_enabled
    )
    return success_response(request, IntegrationOut.model_validate(updated))


@router.delete(
    "/integrations/{integration_id}",
    summary="Delete integration",
    description="Delete an integration (admin or owner).",
    response_model=SuccessResponse[dict],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_integration(
    integration_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    integration = integration_crud.get_integration(db, integration_id)
    if not integration:
        raise AppException(404, ErrorCode.NOT_FOUND, "Integration not found")
    member = member_crud.get_member_by_user(db, integration.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    if member.role not in (OrgRole.admin, OrgRole.owner):
        raise AppException(403, ErrorCode.FORBIDDEN, "Insufficient role")
    integration_crud.delete_integration(db, integration)
    return success_response(request, {"deleted": True})
