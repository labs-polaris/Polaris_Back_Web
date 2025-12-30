from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import jwt

from app.api.deps import get_current_user, get_db
from app.api.response import success_response
from app.core.errors import AppException, ErrorCode
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.crud import user as user_crud
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair, UserOut
from app.schemas.common import ErrorResponse, SuccessResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post(
    "/register",
    summary="Register a new user",
    description="Create a new user account for the Polaris Lab console.",
    response_model=SuccessResponse[UserOut],
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    existing = user_crud.get_by_email(db, payload.email)
    if existing:
        raise AppException(409, ErrorCode.CONFLICT, "Email already exists")
    user = user_crud.create_user(db, payload.email, payload.password, payload.name)
    return success_response(request, UserOut.model_validate(user))


@router.post(
    "/login",
    summary="Login and receive tokens",
    description="Authenticate with email and password to receive JWT access and refresh tokens.",
    response_model=SuccessResponse[TokenPair],
    responses={401: {"model": ErrorResponse}},
)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = user_crud.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppException(401, ErrorCode.AUTH_INVALID, "Invalid credentials")
    tokens = TokenPair(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))
    return success_response(request, tokens)


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="Use a refresh token to issue a new access token.",
    response_model=SuccessResponse[TokenPair],
    responses={401: {"model": ErrorResponse}},
)
def refresh(payload: RefreshRequest, request: Request):
    try:
        decoded = decode_token(payload.refresh_token)
    except jwt.PyJWTError as exc:
        raise AppException(401, ErrorCode.AUTH_INVALID, "Invalid token") from exc
    if decoded.get("type") != "refresh":
        raise AppException(401, ErrorCode.AUTH_INVALID, "Invalid refresh token")
    tokens = TokenPair(access_token=create_access_token(decoded["sub"]), refresh_token=payload.refresh_token)
    return success_response(request, tokens)


@router.get(
    "/me",
    summary="Get current user",
    description="Return the currently authenticated user profile.",
    response_model=SuccessResponse[UserOut],
    responses={401: {"model": ErrorResponse}},
)
def me(request: Request, user=Depends(get_current_user)):
    return success_response(request, UserOut.model_validate(user))
