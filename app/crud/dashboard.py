from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.integration import Integration
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.policy import Policy
from app.models.project import Project
from app.models.service import Service


def get_summary(db: Session, user_id: str) -> dict:
    org_ids = db.execute(
        select(OrganizationMember.org_id).where(OrganizationMember.user_id == user_id)
    ).scalars().all()

    if not org_ids:
        return {
            "org_count": 0,
            "project_count": 0,
            "service_count": 0,
            "policy_count": 0,
            "integration_count": 0,
            "latest_projects": [],
            "latest_services": [],
            "setup_progress": {
                "has_org": False,
                "has_project": False,
                "has_service": False,
                "has_policy": False,
                "has_integration": False,
            },
        }

    org_count = db.execute(select(func.count(Organization.id)).where(Organization.id.in_(org_ids))).scalar_one()
    project_count = db.execute(select(func.count(Project.id)).where(Project.org_id.in_(org_ids))).scalar_one()
    policy_count = db.execute(select(func.count(Policy.id)).where(Policy.org_id.in_(org_ids))).scalar_one()
    integration_count = db.execute(select(func.count(Integration.id)).where(Integration.org_id.in_(org_ids))).scalar_one()

    project_ids = db.execute(select(Project.id).where(Project.org_id.in_(org_ids))).scalars().all()
    if project_ids:
        service_count = db.execute(select(func.count(Service.id)).where(Service.project_id.in_(project_ids))).scalar_one()
    else:
        service_count = 0

    latest_projects = (
        db.execute(select(Project).where(Project.org_id.in_(org_ids)).order_by(Project.created_at.desc()).limit(5))
        .scalars()
        .all()
    )
    latest_services = []
    if project_ids:
        latest_services = (
            db.execute(select(Service).where(Service.project_id.in_(project_ids)).order_by(Service.created_at.desc()).limit(5))
            .scalars()
            .all()
        )

    return {
        "org_count": org_count,
        "project_count": project_count,
        "service_count": service_count,
        "policy_count": policy_count,
        "integration_count": integration_count,
        "latest_projects": latest_projects,
        "latest_services": latest_services,
        "setup_progress": {
            "has_org": org_count > 0,
            "has_project": project_count > 0,
            "has_service": service_count > 0,
            "has_policy": policy_count > 0,
            "has_integration": integration_count > 0,
        },
    }
