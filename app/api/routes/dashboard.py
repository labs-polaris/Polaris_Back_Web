from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.response import success_response
from app.crud import dashboard as dashboard_crud
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    summary="Get dashboard summary",
    description="Return counts, latest items, and setup progress for the current user.",
    response_model=SuccessResponse[DashboardSummary],
    responses={401: {"model": ErrorResponse}},
)
def get_summary(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    summary = dashboard_crud.get_summary(db, user.id)
    return success_response(request, DashboardSummary.model_validate(summary))
