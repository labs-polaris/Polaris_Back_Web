from pydantic import BaseModel, ConfigDict

from app.schemas.project import ProjectOut
from app.schemas.service import ServiceOut


class SetupProgress(BaseModel):
    has_org: bool
    has_project: bool
    has_service: bool
    has_policy: bool
    has_integration: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "has_org": True,
                "has_project": True,
                "has_service": True,
                "has_policy": False,
                "has_integration": False,
            }
        }
    )


class DashboardSummary(BaseModel):
    org_count: int
    project_count: int
    service_count: int
    policy_count: int
    integration_count: int
    latest_projects: list[ProjectOut]
    latest_services: list[ServiceOut]
    setup_progress: SetupProgress

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "org_count": 1,
                "project_count": 2,
                "service_count": 3,
                "policy_count": 1,
                "integration_count": 1,
                "latest_projects": [],
                "latest_services": [],
                "setup_progress": {
                    "has_org": True,
                    "has_project": True,
                    "has_service": True,
                    "has_policy": False,
                    "has_integration": False,
                },
            }
        }
    )
