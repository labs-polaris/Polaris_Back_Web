from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_org_role
from app.api.response import success_response
from app.core.errors import AppException, ErrorCode
from app.crud import member as member_crud
from app.crud import policy as policy_crud
from app.models.enums import OrgRole
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.policy import PolicyCreate, PolicyOut, PolicyUpdate

router = APIRouter(prefix="/api", tags=["Policies"])


@router.get(
    "/orgs/{org_id}/policies",
    summary="List policies",
    description="List policies configured for an organization.",
    response_model=SuccessResponse[list[PolicyOut]],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_policies(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.member)),
):
    policies = policy_crud.list_policies(db, org_id)
    return success_response(request, [PolicyOut.model_validate(p) for p in policies])


@router.post(
    "/orgs/{org_id}/policies",
    summary="Create policy",
    description="Create a policy for an organization (admin or owner).",
    response_model=SuccessResponse[PolicyOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def create_policy(
    org_id: str,
    payload: PolicyCreate,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.admin)),
):
    policy = policy_crud.create_policy(db, org_id, payload.type, payload.config_json, payload.is_enabled)
    return success_response(request, PolicyOut.model_validate(policy))


@router.get(
    "/policies/{policy_id}",
    summary="Get policy",
    description="Fetch a policy by ID.",
    response_model=SuccessResponse[PolicyOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_policy(
    policy_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    policy = policy_crud.get_policy(db, policy_id)
    if not policy:
        raise AppException(404, ErrorCode.NOT_FOUND, "Policy not found")
    member = member_crud.get_member_by_user(db, policy.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    return success_response(request, PolicyOut.model_validate(policy))


@router.patch(
    "/policies/{policy_id}",
    summary="Update policy",
    description="Update a policy (admin or owner).",
    response_model=SuccessResponse[PolicyOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
@router.put(
    "/policies/{policy_id}",
    summary="Replace policy",
    description="Replace a policy (admin or owner).",
    response_model=SuccessResponse[PolicyOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def update_policy(
    policy_id: str,
    payload: PolicyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    policy = policy_crud.get_policy(db, policy_id)
    if not policy:
        raise AppException(404, ErrorCode.NOT_FOUND, "Policy not found")
    member = member_crud.get_member_by_user(db, policy.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    if member.role not in (OrgRole.admin, OrgRole.owner):
        raise AppException(403, ErrorCode.FORBIDDEN, "Insufficient role")
    updated = policy_crud.update_policy(db, policy, payload.type, payload.config_json, payload.is_enabled)
    return success_response(request, PolicyOut.model_validate(updated))


@router.delete(
    "/policies/{policy_id}",
    summary="Delete policy",
    description="Delete a policy (admin or owner).",
    response_model=SuccessResponse[dict],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_policy(
    policy_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    policy = policy_crud.get_policy(db, policy_id)
    if not policy:
        raise AppException(404, ErrorCode.NOT_FOUND, "Policy not found")
    member = member_crud.get_member_by_user(db, policy.org_id, user.id)
    if not member:
        raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
    if member.role not in (OrgRole.admin, OrgRole.owner):
        raise AppException(403, ErrorCode.FORBIDDEN, "Insufficient role")
    policy_crud.delete_policy(db, policy)
    return success_response(request, {"deleted": True})
