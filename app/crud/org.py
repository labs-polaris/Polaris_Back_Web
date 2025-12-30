from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.enums import OrgRole


def list_orgs_for_user(db: Session, user_id: str) -> list[Organization]:
    query = (
        select(Organization)
        .join(OrganizationMember, OrganizationMember.org_id == Organization.id)
        .where(OrganizationMember.user_id == user_id)
        .order_by(Organization.created_at.desc())
    )
    return db.execute(query).scalars().all()


def get_org(db: Session, org_id: str) -> Organization | None:
    return db.execute(select(Organization).where(Organization.id == org_id)).scalar_one_or_none()


def create_org(db: Session, name: str, owner_user_id: str) -> Organization:
    org = Organization(name=name, owner_user_id=owner_user_id)
    db.add(org)
    db.flush()
    member = OrganizationMember(org_id=org.id, user_id=owner_user_id, role=OrgRole.owner)
    db.add(member)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppException(409, ErrorCode.CONFLICT, "Organization already exists") from exc
    db.refresh(org)
    return org


def update_org(db: Session, org: Organization, name: str | None) -> Organization:
    if name is not None:
        org.name = name
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def delete_org(db: Session, org: Organization) -> None:
    db.delete(org)
    db.commit()
