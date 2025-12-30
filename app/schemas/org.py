from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import OrgRole


class OrganizationCreate(BaseModel):
    name: str = Field(..., examples=["Polaris Lab Org"])

    model_config = ConfigDict(json_schema_extra={"example": {"name": "Polaris Lab Org"}})


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, examples=["Polaris Lab Org Updated"])


class OrganizationOut(BaseModel):
    id: str
    name: str
    owner_user_id: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "org-uuid",
                "name": "Polaris Lab Org",
                "owner_user_id": "user-uuid",
            }
        },
    )


class MemberOut(BaseModel):
    id: str
    org_id: str
    user_id: str
    role: OrgRole

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "member-uuid",
                "org_id": "org-uuid",
                "user_id": "user-uuid",
                "role": "admin",
            }
        },
    )


class MemberCreate(BaseModel):
    email: EmailStr = Field(..., examples=["admin@example.com"])
    role: OrgRole = Field(..., examples=["admin"])

    model_config = ConfigDict(json_schema_extra={"example": {"email": "admin@example.com", "role": "admin"}})


class MemberUpdate(BaseModel):
    role: OrgRole = Field(..., examples=["member"])
