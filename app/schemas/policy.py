from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PolicyType


class PolicyCreate(BaseModel):
    type: PolicyType = Field(..., examples=["SLA"])
    config_json: dict[str, Any] = Field(..., examples=[{"critical_days": 7, "high_days": 30}])
    is_enabled: bool = Field(True, examples=[True])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "SLA",
                "config_json": {"critical_days": 7, "high_days": 30},
                "is_enabled": True,
            }
        }
    )


class PolicyUpdate(BaseModel):
    type: PolicyType | None = Field(None, examples=["PR_GATE"])
    config_json: dict[str, Any] | None = Field(None, examples=[{"block_on": ["CRITICAL"]}])
    is_enabled: bool | None = Field(None, examples=[False])


class PolicyOut(BaseModel):
    id: str
    org_id: str
    type: PolicyType
    config_json: dict[str, Any]
    is_enabled: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "policy-uuid",
                "org_id": "org-uuid",
                "type": "SLA",
                "config_json": {"critical_days": 7, "high_days": 30},
                "is_enabled": True,
            }
        },
    )
