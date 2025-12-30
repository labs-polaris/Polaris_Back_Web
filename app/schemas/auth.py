from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "user-uuid",
                "email": "owner@example.com",
                "name": "Owner",
                "is_active": True,
            }
        },
    )


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., examples=["owner@example.com"])
    password: str = Field(..., min_length=8, max_length=72, examples=["PolarisPass1!"])
    name: str = Field(..., examples=["Owner"])

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "owner@example.com", "password": "PolarisPass1!", "name": "Owner"}}
    )


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["owner@example.com"])
    password: str = Field(..., max_length=72, examples=["PolarisPass1!"])

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "owner@example.com", "password": "PolarisPass1!"}}
    )


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., examples=["<refresh_token>"])

    model_config = ConfigDict(json_schema_extra={"example": {"refresh_token": "<refresh_token>"}})


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "<access_token>",
                "refresh_token": "<refresh_token>",
                "token_type": "bearer",
            }
        }
    )
