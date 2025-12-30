from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import IntegrationProvider


class IntegrationCreate(BaseModel):
    provider: IntegrationProvider = Field(..., examples=["GITHUB"])
    config_json: dict[str, Any] = Field(..., examples=[{"token": "ghp_xxx"}])
    is_enabled: bool = Field(True, examples=[True])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"provider": "GITHUB", "config_json": {"token": "ghp_xxx"}, "is_enabled": True}
        }
    )


class IntegrationUpdate(BaseModel):
    provider: IntegrationProvider | None = Field(None, examples=["JIRA"])
    config_json: dict[str, Any] | None = Field(None, examples=[{"webhook": "https://..."}])
    is_enabled: bool | None = Field(None, examples=[False])


class IntegrationOut(BaseModel):
    id: str
    org_id: str
    provider: IntegrationProvider
    config_json: dict[str, Any]
    is_enabled: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "integration-uuid",
                "org_id": "org-uuid",
                "provider": "GITHUB",
                "config_json": {"token": "ghp_xxx"},
                "is_enabled": True,
            }
        },
    )
