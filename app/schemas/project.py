from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., examples=["Web Console"])
    key: str = Field(..., examples=["WEB"])

    model_config = ConfigDict(json_schema_extra={"example": {"name": "Web Console", "key": "WEB"}})


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, examples=["Web Console Updated"])
    key: str | None = Field(None, examples=["WEB2"])


class ProjectOut(BaseModel):
    id: str
    org_id: str
    name: str
    key: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "project-uuid",
                "org_id": "org-uuid",
                "name": "Web Console",
                "key": "WEB",
            }
        },
    )
