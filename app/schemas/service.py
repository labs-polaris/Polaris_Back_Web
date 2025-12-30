from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EnvironmentType, ServiceType


class ServiceCreate(BaseModel):
    name: str = Field(..., examples=["Console API"])
    type: ServiceType = Field(..., examples=["API"])
    environment: EnvironmentType = Field(..., examples=["PROD"])

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "Console API", "type": "API", "environment": "PROD"}}
    )


class ServiceUpdate(BaseModel):
    name: str | None = Field(None, examples=["Console API Updated"])
    type: ServiceType | None = Field(None, examples=["WEB"])
    environment: EnvironmentType | None = Field(None, examples=["STAGE"])


class ServiceOut(BaseModel):
    id: str
    project_id: str
    name: str
    type: ServiceType
    environment: EnvironmentType

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "service-uuid",
                "project_id": "project-uuid",
                "name": "Console API",
                "type": "API",
                "environment": "PROD",
            }
        },
    )
