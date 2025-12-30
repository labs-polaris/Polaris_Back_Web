from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.models.organization_member import OrganizationMember
from app.models.enums import OrgRole


def list_members(db: Session, org_id: str) -> list[OrganizationMember]:
    return db.execute(
        select(OrganizationMember).where(OrganizationMember.org_id == org_id).order_by(
            OrganizationMember.created_at.desc()
        )
    ).scalars().all()


def get_member(db: Session, member_id: str) -> OrganizationMember | None:
    return db.execute(select(OrganizationMember).where(OrganizationMember.id == member_id)).scalar_one_or_none()


def get_member_by_user(db: Session, org_id: str, user_id: str) -> OrganizationMember | None:
    return db.execute(
        select(OrganizationMember).where(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user_id,
        )
    ).scalar_one_or_none()


def add_member(db: Session, org_id: str, user_id: str, role: OrgRole) -> OrganizationMember:
    member = OrganizationMember(org_id=org_id, user_id=user_id, role=role)
    db.add(member)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppException(409, ErrorCode.CONFLICT, "User already in organization") from exc
    db.refresh(member)
    return member


def update_member(db: Session, member: OrganizationMember, role: OrgRole) -> OrganizationMember:
    member.role = role
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member: OrganizationMember) -> None:
    db.delete(member)
    db.commit()
