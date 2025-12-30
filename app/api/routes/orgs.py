from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_org_role
from app.api.response import success_response
from app.core.errors import AppException, ErrorCode
from app.crud import member as member_crud
from app.crud import org as org_crud
from app.crud import user as user_crud
from app.models.enums import OrgRole
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.org import MemberCreate, MemberOut, MemberUpdate, OrganizationCreate, OrganizationOut, OrganizationUpdate

router = APIRouter(prefix="/api/orgs", tags=["Orgs"])


@router.get(
    "",
    summary="List organizations",
    description="List organizations the current user belongs to.",
    response_model=SuccessResponse[list[OrganizationOut]],
    responses={401: {"model": ErrorResponse}},
)
def list_orgs(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    orgs = org_crud.list_orgs_for_user(db, user.id)
    return success_response(request, [OrganizationOut.model_validate(org) for org in orgs])


@router.post(
    "",
    summary="Create organization",
    description="Create a new organization and assign the creator as owner.",
    response_model=SuccessResponse[OrganizationOut],
    responses={401: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def create_org(payload: OrganizationCreate, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    org = org_crud.create_org(db, payload.name, user.id)
    return success_response(request, OrganizationOut.model_validate(org))


@router.get(
    "/{org_id}",
    summary="Get organization",
    description="Fetch a specific organization by ID.",
    response_model=SuccessResponse[OrganizationOut],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_org(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.member)),
):
    org = org_crud.get_org(db, org_id)
    if not org:
        raise AppException(404, ErrorCode.NOT_FOUND, "Organization not found")
    return success_response(request, OrganizationOut.model_validate(org))


@router.patch(
    "/{org_id}",
    summary="Update organization",
    description="Update organization details (admin or owner).",
    response_model=SuccessResponse[OrganizationOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
@router.put(
    "/{org_id}",
    summary="Replace organization",
    description="Replace organization details (admin or owner).",
    response_model=SuccessResponse[OrganizationOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_org(
    org_id: str,
    payload: OrganizationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.admin)),
):
    org = org_crud.get_org(db, org_id)
    if not org:
        raise AppException(404, ErrorCode.NOT_FOUND, "Organization not found")
    updated = org_crud.update_org(db, org, payload.name)
    return success_response(request, OrganizationOut.model_validate(updated))


@router.delete(
    "/{org_id}",
    summary="Delete organization",
    description="Delete an organization (admin or owner).",
    response_model=SuccessResponse[dict],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_org(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.admin)),
):
    org = org_crud.get_org(db, org_id)
    if not org:
        raise AppException(404, ErrorCode.NOT_FOUND, "Organization not found")
    org_crud.delete_org(db, org)
    return success_response(request, {"deleted": True})


@router.get(
    "/{org_id}/members",
    summary="List organization members",
    description="List members in an organization.",
    response_model=SuccessResponse[list[MemberOut]],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_members(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.member)),
):
    members = member_crud.list_members(db, org_id)
    return success_response(request, [MemberOut.model_validate(member) for member in members])


@router.post(
    "/{org_id}/members",
    summary="Add organization member",
    description="Add an existing user to the organization by email (owner only).",
    response_model=SuccessResponse[MemberOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def add_member(
    org_id: str,
    payload: MemberCreate,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.owner)),
):
    user = user_crud.get_by_email(db, payload.email)
    if not user:
        raise AppException(404, ErrorCode.NOT_FOUND, "User not found")
    member = member_crud.add_member(db, org_id, user.id, payload.role)
    return success_response(request, MemberOut.model_validate(member))


@router.patch(
    "/{org_id}/members/{member_id}",
    summary="Update member role",
    description="Update a member's role (owner only).",
    response_model=SuccessResponse[MemberOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_member(
    org_id: str,
    member_id: str,
    payload: MemberUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.owner)),
):
    member = member_crud.get_member(db, member_id)
    if not member or member.org_id != org_id:
        raise AppException(404, ErrorCode.NOT_FOUND, "Member not found")
    updated = member_crud.update_member(db, member, payload.role)
    return success_response(request, MemberOut.model_validate(updated))


@router.delete(
    "/{org_id}/members/{member_id}",
    summary="Remove organization member",
    description="Remove a member from the organization (owner only).",
    response_model=SuccessResponse[dict],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_member(
    org_id: str,
    member_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _member=Depends(require_org_role(OrgRole.owner)),
):
    member = member_crud.get_member(db, member_id)
    if not member or member.org_id != org_id:
        raise AppException(404, ErrorCode.NOT_FOUND, "Member not found")
    member_crud.delete_member(db, member)
    return success_response(request, {"deleted": True})
