from typing import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt

from app.core.database import SessionLocal
from app.core.errors import AppException, ErrorCode
from app.core.security import decode_token
from app.crud import member as member_crud
from app.crud import org as org_crud
from app.crud import project as project_crud
from app.crud import user as user_crud
from app.models.enums import OrgRole

security = HTTPBearer(auto_error=False, scheme_name="BearerAuth")

ROLE_PRIORITY = {
    OrgRole.member: 1,
    OrgRole.admin: 2,
    OrgRole.owner: 3,
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    if credentials is None or not credentials.credentials:
        raise AppException(401, ErrorCode.AUTH_REQUIRED, "Authentication required")
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as exc:
        raise AppException(401, ErrorCode.AUTH_INVALID, "Invalid token") from exc
    if payload.get("type") != "access":
        raise AppException(401, ErrorCode.AUTH_INVALID, "Invalid access token")
    user = user_crud.get_by_id(db, payload.get("sub"))
    if not user:
        raise AppException(401, ErrorCode.AUTH_INVALID, "User not found")
    return user


def require_org_role(min_role: OrgRole) -> Callable:
    def _checker(
        org_id: str,
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
    ):
        org = org_crud.get_org(db, org_id)
        if not org:
            raise AppException(404, ErrorCode.NOT_FOUND, "Organization not found")
        member = member_crud.get_member_by_user(db, org_id, user.id)
        if not member:
            raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
        if ROLE_PRIORITY[member.role] < ROLE_PRIORITY[min_role]:
            raise AppException(403, ErrorCode.FORBIDDEN, "Insufficient role")
        return member

    return _checker


def require_project_access(min_role: OrgRole) -> Callable:
    def _checker(
        project_id: str,
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
    ):
        project = project_crud.get_project(db, project_id)
        if not project:
            raise AppException(404, ErrorCode.NOT_FOUND, "Project not found")
        member = member_crud.get_member_by_user(db, project.org_id, user.id)
        if not member:
            raise AppException(403, ErrorCode.FORBIDDEN, "Not a member of this organization")
        if ROLE_PRIORITY[member.role] < ROLE_PRIORITY[min_role]:
            raise AppException(403, ErrorCode.FORBIDDEN, "Insufficient role")
        return member

    return _checker
